#!/bin/bash

echo "=== 用户认证系统API测试 User Authentication System API Test ==="
echo ""

# Test variables
BASE_URL="http://localhost"
if [ ! -z "$1" ]; then
    BASE_URL="$1"
fi

TEST_EMAIL="test@example.com"
TEST_PASSWORD="TestPassword123"

echo "Testing against: $BASE_URL"
echo ""

# Test 1: Health Check
echo "1. 健康检查 Health Check"
curl -s -X GET "$BASE_URL/api/healthz" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/healthz"
echo -e "\n"

# Test 2: Register
echo "2. 用户注册 User Registration"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")
echo "$REGISTER_RESPONSE" | jq . 2>/dev/null || echo "$REGISTER_RESPONSE"
echo -e "\n"

# Test 3: Login
echo "3. 用户登录 User Login"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")
echo "$LOGIN_RESPONSE" | jq . 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract tokens
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r .access_token 2>/dev/null)
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r .refresh_token 2>/dev/null)

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "Login failed - no access token received"
    exit 1
fi

echo -e "\n"

# Test 4: Get User Info
echo "4. 获取用户信息 Get User Info"
curl -s -X GET "$BASE_URL/api/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/me" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

# Test 5: Refresh Token
echo "5. 刷新令牌 Refresh Token"
REFRESH_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/refresh" \
  -H "Authorization: Bearer $REFRESH_TOKEN")
echo "$REFRESH_RESPONSE" | jq . 2>/dev/null || echo "$REFRESH_RESPONSE"

# Update tokens
NEW_ACCESS_TOKEN=$(echo "$REFRESH_RESPONSE" | jq -r .access_token 2>/dev/null)
if [ "$NEW_ACCESS_TOKEN" != "null" ] && [ ! -z "$NEW_ACCESS_TOKEN" ]; then
    ACCESS_TOKEN="$NEW_ACCESS_TOKEN"
fi

echo -e "\n"

# Test 6: Get User Info with New Token
echo "6. 使用新令牌获取用户信息 Get User Info with New Token"
curl -s -X GET "$BASE_URL/api/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/me" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

# Test 7: Logout
echo "7. 用户登出 User Logout"
curl -s -X POST "$BASE_URL/api/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq . 2>/dev/null || curl -s -X POST "$BASE_URL/api/auth/logout" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

# Test 8: Try to access protected resource after logout
echo "8. 登出后访问保护资源测试 Access Protected Resource After Logout"
curl -s -X GET "$BASE_URL/api/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq . 2>/dev/null || curl -s -X GET "$BASE_URL/api/me" -H "Authorization: Bearer $ACCESS_TOKEN"
echo -e "\n"

echo "=== 测试完成 Tests Completed ==="