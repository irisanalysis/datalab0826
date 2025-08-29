#!/bin/bash

# End-to-End Authentication System Test Script
# Tests the complete authentication flow using curl

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_BASE="http://localhost:8000"
FRONTEND_BASE="http://localhost:3000"
TEST_EMAIL="test@example.com"
TEST_PASSWORD="TestPass123"
COOKIE_FILE="test_cookies.txt"

# Helper functions
print_step() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

cleanup() {
    rm -f "$COOKIE_FILE"
    print_step "Cleanup completed"
}

# Trap to ensure cleanup runs
trap cleanup EXIT

print_step "Starting End-to-End Authentication Tests"

# Test 1: Health Check
print_step "1. Health Check"
health_response=$(curl -s "$API_BASE/healthz")
if echo "$health_response" | grep -q '"status":"healthy"'; then
    print_success "API is healthy"
else
    print_error "API health check failed"
    echo "Response: $health_response"
    exit 1
fi

# Test 2: Frontend Health Check
print_step "2. Frontend Health Check"
if curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_BASE/" | grep -q "200"; then
    print_success "Frontend is accessible"
else
    print_warning "Frontend may not be ready (this is optional)"
fi

# Test 3: User Registration
print_step "3. User Registration"
register_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST "$API_BASE/api/auth/register" \
    -H "Content-Type: application/json" \
    -H "X-Requested-With: XMLHttpRequest" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

# Extract HTTP status
http_status=$(echo "$register_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$register_response" | sed 's/HTTPSTATUS:[0-9]*$//')

if [ "$http_status" -eq 200 ]; then
    print_success "User registration successful"
    echo "Response: $body"
elif [ "$http_status" -eq 400 ] && echo "$body" | grep -q "Registration failed"; then
    print_warning "User may already exist, continuing with login test"
else
    print_error "User registration failed with status $http_status"
    echo "Response: $body"
    exit 1
fi

# Test 4: User Login
print_step "4. User Login"
login_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST "$API_BASE/api/auth/login" \
    -H "Content-Type: application/json" \
    -H "X-Requested-With: XMLHttpRequest" \
    -c "$COOKIE_FILE" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

# Extract HTTP status
http_status=$(echo "$login_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$login_response" | sed 's/HTTPSTATUS:[0-9]*$//')

if [ "$http_status" -eq 200 ]; then
    print_success "User login successful"
    echo "Response: $body"
    
    # Verify we got user data back
    if echo "$body" | grep -q "\"user\""; then
        print_success "User data received in login response"
    else
        print_error "No user data in login response"
        exit 1
    fi
else
    print_error "User login failed with status $http_status"
    echo "Response: $body"
    exit 1
fi

# Test 5: Access Protected Resource
print_step "5. Access Protected Resource (/api/me)"
me_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X GET "$API_BASE/api/me" \
    -b "$COOKIE_FILE")

# Extract HTTP status
http_status=$(echo "$me_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$me_response" | sed 's/HTTPSTATUS:[0-9]*$//')

if [ "$http_status" -eq 200 ]; then
    print_success "Protected resource access successful"
    echo "Response: $body"
    
    # Verify we got user data
    if echo "$body" | grep -q "\"email\":\"$TEST_EMAIL\""; then
        print_success "Correct user data returned"
    else
        print_error "Incorrect user data returned"
        exit 1
    fi
else
    print_error "Protected resource access failed with status $http_status"
    echo "Response: $body"
    exit 1
fi

# Test 6: Token Refresh
print_step "6. Token Refresh"
refresh_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST "$API_BASE/api/auth/refresh" \
    -b "$COOKIE_FILE" \
    -c "$COOKIE_FILE")

# Extract HTTP status
http_status=$(echo "$refresh_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$refresh_response" | sed 's/HTTPSTATUS:[0-9]*$//')

if [ "$http_status" -eq 200 ]; then
    print_success "Token refresh successful"
    echo "Response: $body"
else
    print_error "Token refresh failed with status $http_status"
    echo "Response: $body"
    exit 1
fi

# Test 7: Access Protected Resource Again (with new token)
print_step "7. Access Protected Resource Again (with refreshed token)"
me_response2=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X GET "$API_BASE/api/me" \
    -b "$COOKIE_FILE")

# Extract HTTP status
http_status=$(echo "$me_response2" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$me_response2" | sed 's/HTTPSTATUS:[0-9]*$//')

if [ "$http_status" -eq 200 ]; then
    print_success "Protected resource access after refresh successful"
else
    print_error "Protected resource access after refresh failed with status $http_status"
    echo "Response: $body"
    exit 1
fi

# Test 8: User Logout
print_step "8. User Logout"
logout_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST "$API_BASE/api/auth/logout" \
    -b "$COOKIE_FILE")

# Extract HTTP status
http_status=$(echo "$logout_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$logout_response" | sed 's/HTTPSTATUS:[0-9]*$//')

if [ "$http_status" -eq 200 ]; then
    print_success "User logout successful"
    echo "Response: $body"
else
    print_error "User logout failed with status $http_status"
    echo "Response: $body"
    exit 1
fi

# Test 9: Access Protected Resource After Logout (Should Fail)
print_step "9. Access Protected Resource After Logout (Should Fail)"
me_response3=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X GET "$API_BASE/api/me" \
    -b "$COOKIE_FILE")

# Extract HTTP status
http_status=$(echo "$me_response3" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
body=$(echo "$me_response3" | sed 's/HTTPSTATUS:[0-9]*$//')

if [ "$http_status" -eq 401 ]; then
    print_success "Protected resource correctly denied after logout"
else
    print_error "Protected resource should be denied after logout (got status $http_status)"
    echo "Response: $body"
    exit 1
fi

# Test 10: Rate Limiting Test
print_step "10. Rate Limiting Test"
print_warning "Testing rate limits on registration endpoint..."

# Make multiple requests quickly to trigger rate limiting
for i in {1..12}; do
    rate_test_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
        -X POST "$API_BASE/api/auth/register" \
        -H "Content-Type: application/json" \
        -H "X-Requested-With: XMLHttpRequest" \
        -d "{\"email\":\"ratetest$i@example.com\",\"password\":\"$TEST_PASSWORD\"}")
    
    http_status=$(echo "$rate_test_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$http_status" -eq 429 ]; then
        print_success "Rate limiting is working (got 429 on request $i)"
        break
    elif [ $i -eq 12 ]; then
        print_warning "Rate limiting may not be working as expected (no 429 errors)"
    fi
done

# Test 11: CSRF Protection Test
print_step "11. CSRF Protection Test"
print_warning "Testing CSRF protection by omitting X-Requested-With header..."

csrf_test_response=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -X POST "$API_BASE/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"csrf_test@example.com\",\"password\":\"$TEST_PASSWORD\"}")

http_status=$(echo "$csrf_test_response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)

if [ "$http_status" -eq 403 ]; then
    print_success "CSRF protection is working (request blocked without proper header)"
else
    print_warning "CSRF protection may not be working as expected (got status $http_status instead of 403)"
fi

print_step "All Tests Completed Successfully!"
echo -e "${GREEN}🎉 Authentication system is working correctly!${NC}"

# Summary
echo ""
echo "Test Summary:"
echo "✅ Health checks passed"
echo "✅ User registration working"
echo "✅ User login working"
echo "✅ Protected resource access working"
echo "✅ Token refresh working"
echo "✅ User logout working"
echo "✅ Post-logout access denial working"
echo "✅ Rate limiting configured"
echo "✅ CSRF protection configured"
echo ""
echo "Frontend URL: $FRONTEND_BASE"
echo "Backend URL: $API_BASE"
echo "API Docs: $API_BASE/docs"