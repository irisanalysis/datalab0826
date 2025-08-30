# CI/CD Integration & Automated Deployment Strategy

## 1. GitHub Actions Pipeline (Recommended)

### Multi-Stage Pipeline Configuration
```yaml
# .github/workflows/deploy-microservices.yml
name: DataLab Platform CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: datalab-platform

jobs:
  # Stage 1: Testing and Quality Checks
  test:
    name: Test & Quality Checks
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11"]
        service: [api-gateway, data-service, ai-service, compute-service, viz-service]
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Install UV package manager
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.local/bin" >> $GITHUB_PATH

    - name: Setup Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      working-directory: ./backend
      run: |
        uv venv
        uv install
        uv add --dev pytest-cov

    - name: Code quality checks
      working-directory: ./backend
      run: |
        # Linting
        uv run black --check .
        uv run isort --check-only .
        uv run flake8 .
        
        # Type checking
        uv run mypy apps/${{ matrix.service }}

    - name: Run unit tests
      working-directory: ./backend
      run: |
        uv run pytest tests/unit/test_${{ matrix.service }}.py \
          --cov=apps/${{ matrix.service }} \
          --cov-report=xml \
          --cov-fail-under=80

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml
        flags: ${{ matrix.service }}

  # Stage 2: Integration Testing
  integration-test:
    name: Integration Tests
    runs-on: ubuntu-latest
    needs: test
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: datalab_test
          POSTGRES_USER: test_user
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Install UV
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.local/bin" >> $GITHUB_PATH

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"

    - name: Install dependencies
      working-directory: ./backend
      run: |
        uv venv
        uv install

    - name: Run database migrations
      working-directory: ./backend
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: datalab_test
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
      run: |
        uv run alembic upgrade head

    - name: Start services for testing
      working-directory: ./backend
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        POSTGRES_DB: datalab_test
        POSTGRES_USER: test_user
        POSTGRES_PASSWORD: test_password
        REDIS_URL: redis://localhost:6379
      run: |
        # Start services in background
        uv run uvicorn apps.api_gateway.main:app --host 0.0.0.0 --port 8000 &
        uv run uvicorn apps.data_service.main:app --host 0.0.0.0 --port 8001 &
        uv run uvicorn apps.ai_service.main:app --host 0.0.0.0 --port 8002 &
        uv run uvicorn apps.compute_service.main:app --host 0.0.0.0 --port 8003 &
        uv run uvicorn apps.viz_service.main:app --host 0.0.0.0 --port 8004 &
        
        # Wait for services to start
        sleep 30

    - name: Run integration tests
      working-directory: ./backend
      run: |
        uv run pytest tests/integration/ -v --tb=short

    - name: Run end-to-end tests
      working-directory: ./backend
      run: |
        uv run pytest tests/e2e/ -v --tb=short

  # Stage 3: Security Scanning
  security-scan:
    name: Security Scanning
    runs-on: ubuntu-latest
    needs: test

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Run dependency vulnerability scan
      working-directory: ./backend
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.local/bin" >> $GITHUB_PATH
        uv venv
        uv add --dev safety bandit
        
        # Check for known vulnerabilities
        uv run safety check --json
        
        # Static security analysis
        uv run bandit -r apps/ -f json

    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: './backend'
        format: 'sarif'
        output: 'trivy-results.sarif'

    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

  # Stage 4: Build Container Images
  build:
    name: Build Images
    runs-on: ubuntu-latest
    needs: [test, integration-test, security-scan]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    
    strategy:
      matrix:
        service: [api-gateway, data-service, ai-service, compute-service, viz-service]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Log in to Container Registry
      uses: docker/login-action@v3
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}

    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v5
      with:
        images: ${{ env.REGISTRY }}/${{ github.repository }}/${{ matrix.service }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}

    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        file: ./backend/infrastructure/docker/Dockerfile.${{ matrix.service }}
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        platforms: linux/amd64,linux/arm64
        cache-from: type=gha
        cache-to: type=gha,mode=max

  # Stage 5: Deploy to Staging
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/develop'
    environment: staging

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'

    - name: Configure kubeconfig for staging
      run: |
        mkdir -p ~/.kube
        echo "${{ secrets.STAGING_KUBECONFIG }}" | base64 -d > ~/.kube/config
        kubectl config use-context staging-cluster

    - name: Deploy to staging
      run: |
        # Update image tags in Kubernetes manifests
        export IMAGE_TAG="${{ github.sha }}"
        envsubst < infrastructure/kubernetes/staging/api-gateway.yaml | kubectl apply -f -
        envsubst < infrastructure/kubernetes/staging/data-service.yaml | kubectl apply -f -
        envsubst < infrastructure/kubernetes/staging/ai-service.yaml | kubectl apply -f -
        envsubst < infrastructure/kubernetes/staging/compute-service.yaml | kubectl apply -f -
        envsubst < infrastructure/kubernetes/staging/viz-service.yaml | kubectl apply -f -

    - name: Wait for deployment rollout
      run: |
        kubectl rollout status deployment/api-gateway -n datalab-staging --timeout=300s
        kubectl rollout status deployment/data-service -n datalab-staging --timeout=300s
        kubectl rollout status deployment/ai-service -n datalab-staging --timeout=300s
        kubectl rollout status deployment/compute-service -n datalab-staging --timeout=300s
        kubectl rollout status deployment/viz-service -n datalab-staging --timeout=300s

    - name: Run smoke tests
      run: |
        # Get staging URL and run basic health checks
        STAGING_URL=$(kubectl get ingress -n datalab-staging -o jsonpath='{.items[0].spec.rules[0].host}')
        
        for endpoint in /health /api/v1/health; do
          curl -f "https://${STAGING_URL}${endpoint}" || exit 1
        done

    - name: Notify deployment success
      uses: 8398a7/action-slack@v3
      with:
        status: success
        text: "🚀 Staging deployment successful for commit ${{ github.sha }}"
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  # Stage 6: Performance Testing
  performance-test:
    name: Performance Testing
    runs-on: ubuntu-latest
    needs: deploy-staging
    if: github.ref == 'refs/heads/develop'

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Node.js for k6
      uses: actions/setup-node@v4
      with:
        node-version: '18'

    - name: Install k6
      run: |
        sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
        echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
        sudo apt-get update
        sudo apt-get install k6

    - name: Run performance tests
      env:
        STAGING_URL: ${{ secrets.STAGING_URL }}
      run: |
        k6 run tests/performance/api_load_test.js \
          --env BASE_URL=$STAGING_URL \
          --out json=performance-results.json

    - name: Upload performance results
      uses: actions/upload-artifact@v3
      with:
        name: performance-results
        path: performance-results.json

  # Stage 7: Deploy to Production
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build, deploy-staging, performance-test]
    if: github.ref == 'refs/heads/main'
    environment: 
      name: production
      url: https://api.datalab.com

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup kubectl
      uses: azure/setup-kubectl@v3
      with:
        version: 'v1.28.0'

    - name: Configure kubeconfig for production
      run: |
        mkdir -p ~/.kube
        echo "${{ secrets.PRODUCTION_KUBECONFIG }}" | base64 -d > ~/.kube/config
        kubectl config use-context production-cluster

    - name: Create deployment backup
      run: |
        # Backup current deployment state
        kubectl get deployments -n datalab-production -o yaml > deployment-backup.yaml

    - name: Deploy to production (Blue-Green)
      run: |
        # Blue-Green deployment strategy
        export IMAGE_TAG="${{ github.sha }}"
        export DEPLOYMENT_COLOR="green"
        
        # Deploy green version
        envsubst < infrastructure/kubernetes/production/api-gateway.yaml | kubectl apply -f -
        envsubst < infrastructure/kubernetes/production/data-service.yaml | kubectl apply -f -
        envsubst < infrastructure/kubernetes/production/ai-service.yaml | kubectl apply -f -
        envsubst < infrastructure/kubernetes/production/compute-service.yaml | kubectl apply -f -
        envsubst < infrastructure/kubernetes/production/viz-service.yaml | kubectl apply -f -

    - name: Wait for green deployment
      run: |
        kubectl rollout status deployment/api-gateway-green -n datalab-production --timeout=600s
        kubectl rollout status deployment/data-service-green -n datalab-production --timeout=600s
        kubectl rollout status deployment/ai-service-green -n datalab-production --timeout=600s
        kubectl rollout status deployment/compute-service-green -n datalab-production --timeout=600s
        kubectl rollout status deployment/viz-service-green -n datalab-production --timeout=600s

    - name: Health check green deployment
      run: |
        # Internal health checks
        kubectl exec -n datalab-production deployment/api-gateway-green -- curl -f http://localhost:8000/health
        
        # Run comprehensive health check
        ./tests/scripts/production_health_check.sh

    - name: Switch traffic to green
      run: |
        # Update service selectors to point to green deployment
        kubectl patch service api-gateway -n datalab-production -p '{"spec":{"selector":{"version":"green"}}}'
        kubectl patch service data-service -n datalab-production -p '{"spec":{"selector":{"version":"green"}}}'
        kubectl patch service ai-service -n datalab-production -p '{"spec":{"selector":{"version":"green"}}}'
        kubectl patch service compute-service -n datalab-production -p '{"spec":{"selector":{"version":"green"}}}'
        kubectl patch service viz-service -n datalab-production -p '{"spec":{"selector":{"version":"green"}}}'

    - name: Monitor deployment for 5 minutes
      run: |
        # Monitor error rates and response times
        sleep 300
        ./tests/scripts/deployment_validation.sh

    - name: Cleanup old blue deployment
      if: success()
      run: |
        # Remove old blue deployment after successful switch
        kubectl delete deployment api-gateway-blue -n datalab-production --ignore-not-found
        kubectl delete deployment data-service-blue -n datalab-production --ignore-not-found
        kubectl delete deployment ai-service-blue -n datalab-production --ignore-not-found
        kubectl delete deployment compute-service-blue -n datalab-production --ignore-not-found
        kubectl delete deployment viz-service-blue -n datalab-production --ignore-not-found

    - name: Rollback on failure
      if: failure()
      run: |
        echo "❌ Deployment failed, rolling back..."
        kubectl apply -f deployment-backup.yaml
        kubectl rollout undo deployment/api-gateway -n datalab-production
        kubectl rollout undo deployment/data-service -n datalab-production
        kubectl rollout undo deployment/ai-service -n datalab-production
        kubectl rollout undo deployment/compute-service -n datalab-production
        kubectl rollout undo deployment/viz-service -n datalab-production

    - name: Notify deployment result
      if: always()
      uses: 8398a7/action-slack@v3
      with:
        status: ${{ job.status }}
        text: |
          🚀 Production deployment ${{ job.status }} for commit ${{ github.sha }}
          📊 View monitoring: https://grafana.datalab.com
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}

  # Stage 8: Post-Deployment Monitoring
  post-deployment-monitoring:
    name: Post-Deployment Monitoring
    runs-on: ubuntu-latest
    needs: deploy-production
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Wait and monitor for 15 minutes
      run: |
        echo "🔍 Monitoring deployment for 15 minutes..."
        sleep 900

    - name: Check error rates
      run: |
        # Query Prometheus for error rates
        ERROR_RATE=$(curl -s "https://prometheus.datalab.com/api/v1/query?query=sum(rate(http_requests_total{status=~'5..'}[5m]))/sum(rate(http_requests_total[5m]))" | jq '.data.result[0].value[1]' | tr -d '"')
        
        if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
          echo "❌ High error rate detected: $ERROR_RATE"
          exit 1
        fi

    - name: Check response times
      run: |
        # Check P95 response times
        P95_RESPONSE_TIME=$(curl -s "https://prometheus.datalab.com/api/v1/query?query=histogram_quantile(0.95,rate(http_request_duration_seconds_bucket[5m]))" | jq '.data.result[0].value[1]' | tr -d '"')
        
        if (( $(echo "$P95_RESPONSE_TIME > 2.0" | bc -l) )); then
          echo "⚠️ High response times detected: ${P95_RESPONSE_TIME}s"
          # This is a warning, not a failure
        fi

    - name: Generate deployment report
      run: |
        echo "📊 Deployment Report" > deployment_report.md
        echo "==================" >> deployment_report.md
        echo "Commit: ${{ github.sha }}" >> deployment_report.md
        echo "Deployment Time: $(date)" >> deployment_report.md
        echo "Error Rate: $ERROR_RATE" >> deployment_report.md
        echo "P95 Response Time: ${P95_RESPONSE_TIME}s" >> deployment_report.md

    - name: Upload deployment report
      uses: actions/upload-artifact@v3
      with:
        name: deployment-report
        path: deployment_report.md
```

## 2. GitLab CI Alternative
```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy-staging
  - performance
  - deploy-production
  - monitor

variables:
  DOCKER_REGISTRY: $CI_REGISTRY
  DOCKER_IMAGE: $CI_REGISTRY_IMAGE

# Shared templates
.uv_setup: &uv_setup
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.local/bin:$PATH"
    - cd backend && uv venv && uv install

.docker_setup: &docker_setup
  image: docker:latest
  services:
    - docker:dind

# Test stage
test:unit:
  stage: test
  image: python:3.11
  <<: *uv_setup
  script:
    - uv run pytest tests/unit/ --cov=apps --cov-report=xml
  coverage: '/TOTAL.+?(\d+\%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml

test:integration:
  stage: test
  image: python:3.11
  services:
    - postgres:15
    - redis:7
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_pass
    REDIS_URL: redis://redis:6379
  <<: *uv_setup
  script:
    - uv run alembic upgrade head
    - uv run pytest tests/integration/

# Build stage
.build_service:
  stage: build
  <<: *docker_setup
  script:
    - docker build -f backend/infrastructure/docker/Dockerfile.$SERVICE -t $DOCKER_REGISTRY/$SERVICE:$CI_COMMIT_SHA backend/
    - docker push $DOCKER_REGISTRY/$SERVICE:$CI_COMMIT_SHA
  only:
    - main
    - develop

build:api-gateway:
  extends: .build_service
  variables:
    SERVICE: api-gateway

build:data-service:
  extends: .build_service
  variables:
    SERVICE: data-service

# ... additional build jobs for each service

# Deploy staging
deploy:staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $STAGING_CONTEXT
    - envsubst < infrastructure/kubernetes/staging/*.yaml | kubectl apply -f -
    - kubectl rollout status deployment/api-gateway -n datalab-staging
  environment:
    name: staging
    url: https://staging.datalab.com
  only:
    - develop

# Performance testing
performance:k6:
  stage: performance
  image: grafana/k6:latest
  script:
    - k6 run tests/performance/load_test.js --env BASE_URL=https://staging.datalab.com
  artifacts:
    reports:
      performance: performance.json
  only:
    - develop

# Production deployment
deploy:production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  script:
    - kubectl config use-context $PRODUCTION_CONTEXT
    - ./scripts/blue_green_deploy.sh
  environment:
    name: production
    url: https://api.datalab.com
  when: manual
  only:
    - main
```

## 3. Deployment Scripts

### Blue-Green Deployment Script
```bash
#!/bin/bash
# scripts/blue_green_deploy.sh

set -e

NAMESPACE="datalab-production"
SERVICES=("api-gateway" "data-service" "ai-service" "compute-service" "viz-service")
IMAGE_TAG=${CI_COMMIT_SHA:-latest}

echo "🔵 Starting Blue-Green Deployment"

# Determine current color
CURRENT_COLOR=$(kubectl get service api-gateway -n $NAMESPACE -o jsonpath='{.spec.selector.version}' 2>/dev/null || echo "blue")
NEW_COLOR=$([ "$CURRENT_COLOR" = "blue" ] && echo "green" || echo "blue")

echo "📊 Current: $CURRENT_COLOR, Deploying: $NEW_COLOR"

# Deploy new version
for service in "${SERVICES[@]}"; do
    echo "🚀 Deploying $service-$NEW_COLOR"
    
    # Update deployment with new color and image
    kubectl patch deployment "$service-$NEW_COLOR" -n $NAMESPACE -p "{
        \"spec\": {
            \"selector\": {\"matchLabels\": {\"app\": \"$service\", \"version\": \"$NEW_COLOR\"}},
            \"template\": {
                \"metadata\": {\"labels\": {\"app\": \"$service\", \"version\": \"$NEW_COLOR\"}},
                \"spec\": {
                    \"containers\": [{
                        \"name\": \"$service\",
                        \"image\": \"$DOCKER_REGISTRY/$service:$IMAGE_TAG\"
                    }]
                }
            }
        }
    }"
    
    # Wait for rollout
    kubectl rollout status deployment/"$service-$NEW_COLOR" -n $NAMESPACE --timeout=300s
done

# Health check new deployment
echo "🔍 Running health checks..."
for service in "${SERVICES[@]}"; do
    for i in {1..5}; do
        if kubectl exec -n $NAMESPACE deployment/"$service-$NEW_COLOR" -- curl -s -f http://localhost:800$(echo $service | tr -d '-' | wc -c)/health; then
            echo "✅ $service health check passed"
            break
        else
            echo "⚠️ $service health check failed, attempt $i/5"
            if [ $i -eq 5 ]; then
                echo "❌ $service health check failed after 5 attempts"
                exit 1
            fi
            sleep 10
        fi
    done
done

# Switch traffic
echo "🔀 Switching traffic to $NEW_COLOR"
for service in "${SERVICES[@]}"; do
    kubectl patch service "$service" -n $NAMESPACE -p "{\"spec\":{\"selector\":{\"version\":\"$NEW_COLOR\"}}}"
done

# Monitor for 2 minutes
echo "📊 Monitoring new deployment for 2 minutes..."
sleep 120

# Final health check
echo "🔍 Final health check..."
HEALTH_CHECK_URL="https://api.datalab.com/health"
if curl -s -f "$HEALTH_CHECK_URL" > /dev/null; then
    echo "✅ Final health check passed"
    
    # Cleanup old deployment
    echo "🧹 Cleaning up $CURRENT_COLOR deployment"
    for service in "${SERVICES[@]}"; do
        kubectl scale deployment "$service-$CURRENT_COLOR" -n $NAMESPACE --replicas=0
    done
    
    echo "🎉 Blue-Green deployment completed successfully!"
else
    echo "❌ Final health check failed, rolling back..."
    
    # Rollback
    for service in "${SERVICES[@]}"; do
        kubectl patch service "$service" -n $NAMESPACE -p "{\"spec\":{\"selector\":{\"version\":\"$CURRENT_COLOR\"}}}"
    done
    
    exit 1
fi
```

### Canary Deployment Script
```bash
#!/bin/bash
# scripts/canary_deploy.sh

set -e

NAMESPACE="datalab-production" 
SERVICE="api-gateway"
IMAGE_TAG=${CI_COMMIT_SHA:-latest}
CANARY_PERCENTAGE=${1:-10}

echo "🐤 Starting Canary Deployment ($CANARY_PERCENTAGE%)"

# Deploy canary version
kubectl set image deployment/"$SERVICE-canary" -n $NAMESPACE "$SERVICE=$DOCKER_REGISTRY/$SERVICE:$IMAGE_TAG"
kubectl rollout status deployment/"$SERVICE-canary" -n $NAMESPACE

# Update Istio VirtualService for traffic splitting
kubectl patch virtualservice "$SERVICE" -n $NAMESPACE -p "{
    \"spec\": {
        \"http\": [{
            \"match\": [{\"headers\": {\"canary\": {\"exact\": \"true\"}}}],
            \"route\": [{\"destination\": {\"host\": \"$SERVICE-canary\"}}]
        }, {
            \"route\": [
                {\"destination\": {\"host\": \"$SERVICE-stable\"}, \"weight\": $((100 - CANARY_PERCENTAGE))},
                {\"destination\": {\"host\": \"$SERVICE-canary\"}, \"weight\": $CANARY_PERCENTAGE}
            ]
        }]
    }
}"

echo "📊 Canary deployment active with $CANARY_PERCENTAGE% traffic"

# Monitor canary for specified duration
MONITOR_DURATION=${2:-300}  # 5 minutes default
echo "🔍 Monitoring canary for $MONITOR_DURATION seconds..."
sleep $MONITOR_DURATION

# Check metrics and decide on promotion/rollback
ERROR_RATE=$(curl -s "http://prometheus:9090/api/v1/query?query=sum(rate(http_requests_total{service='$SERVICE-canary',status=~'5..'}[5m]))/sum(rate(http_requests_total{service='$SERVICE-canary'}[5m]))" | jq -r '.data.result[0].value[1] // "0"')

if (( $(echo "$ERROR_RATE > 0.01" | bc -l) )); then
    echo "❌ High error rate ($ERROR_RATE) detected, rolling back canary"
    kubectl patch virtualservice "$SERVICE" -n $NAMESPACE -p '{"spec":{"http":[{"route":[{"destination":{"host":"'$SERVICE'-stable"}}]}]}}'
    exit 1
else
    echo "✅ Canary deployment successful, promoting to stable"
    # Promote canary to stable
    kubectl set image deployment/"$SERVICE-stable" -n $NAMESPACE "$SERVICE=$DOCKER_REGISTRY/$SERVICE:$IMAGE_TAG"
    kubectl patch virtualservice "$SERVICE" -n $NAMESPACE -p '{"spec":{"http":[{"route":[{"destination":{"host":"'$SERVICE'-stable"}}]}]}}'
fi
```

This comprehensive CI/CD strategy provides:

1. **Multi-stage pipeline** with proper gates
2. **Automated testing** at multiple levels
3. **Security scanning** integration
4. **Multiple deployment strategies** (Blue-Green, Canary)
5. **Rollback mechanisms** on failure
6. **Performance validation** 
7. **Monitoring integration** for deployment validation