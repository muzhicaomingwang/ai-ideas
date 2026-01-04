#!/bin/bash

# ====================================
# TeamVenture 登录流程 E2E 测试脚本
# ====================================
# 版本: v1.0
# 日期: 2026-01-03
# 说明: 完整测试登录流程，包括新用户创建、现有用户更新、会话管理等
# ====================================

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试计数器
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# API 基础地址
API_BASE_URL="${API_BASE_URL:-http://localhost/api/v1}"

# 测试辅助函数
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "${YELLOW}[TEST $TOTAL_TESTS] $1${NC}"
}

print_success() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✓ PASS:${NC} $1"
}

print_failure() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}✗ FAIL:${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ INFO:${NC} $1"
}

# JSON 解析辅助函数（使用 python3）
json_get() {
    echo "$1" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data$2)" 2>/dev/null || echo ""
}

# 验证 JSON 字段存在
assert_json_field() {
    local json="$1"
    local field="$2"
    local expected="$3"

    local actual=$(json_get "$json" "$field")

    if [ -z "$actual" ]; then
        print_failure "字段 $field 不存在"
        return 1
    elif [ ! -z "$expected" ] && [ "$actual" != "$expected" ]; then
        print_failure "字段 $field 值不匹配: 期望 '$expected', 实际 '$actual'"
        return 1
    else
        print_success "字段 $field 验证通过: $actual"
        return 0
    fi
}

# 验证数据库记录
verify_db_user() {
    local user_id="$1"
    local expected_nickname="$2"
    local expected_avatar="$3"

    print_info "验证数据库中的用户记录..."

    local db_result=$(docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
        "SELECT user_id, nickname, avatar_url, role FROM users WHERE user_id='$user_id';" 2>&1 | grep -v Warning | tail -n 1)

    if echo "$db_result" | grep -q "$user_id"; then
        print_success "数据库记录存在: $user_id"

        if echo "$db_result" | grep -q "$expected_nickname"; then
            print_success "nickname 匹配: $expected_nickname"
        else
            print_failure "nickname 不匹配，数据库记录: $db_result"
            return 1
        fi

        if [ ! -z "$expected_avatar" ] && echo "$db_result" | grep -q "$expected_avatar"; then
            print_success "avatar_url 匹配: $expected_avatar"
        fi

        return 0
    else
        print_failure "数据库中未找到用户: $user_id"
        return 1
    fi
}

# 验证 Redis Session
verify_redis_session() {
    local token="$1"
    local expected_user_id="$2"

    print_info "验证 Redis Session..."

    local redis_user_id=$(docker exec teamventure-redis redis-cli -a redis123456 GET "session:$token" 2>&1 | grep -v Warning)

    if [ "$redis_user_id" == "$expected_user_id" ]; then
        print_success "Redis Session 验证通过: $redis_user_id"
        return 0
    else
        print_failure "Redis Session 不匹配: 期望 $expected_user_id, 实际 $redis_user_id"
        return 1
    fi
}

# ====================================
# 前置检查
# ====================================
print_header "前置检查"

print_test "检查后端服务健康状态"
HEALTH_RESPONSE=$(curl -s "http://localhost/actuator/health")
if echo "$HEALTH_RESPONSE" | grep -q '"status":"UP"'; then
    print_success "后端服务运行正常"
else
    print_failure "后端服务未运行或不健康"
    echo "健康检查响应: $HEALTH_RESPONSE"
    exit 1
fi

print_test "检查 MySQL 连接"
if docker exec teamventure-mysql-master mysql -u root -proot123456 -e "SELECT 1;" > /dev/null 2>&1; then
    print_success "MySQL 连接正常"
else
    print_failure "MySQL 连接失败"
    exit 1
fi

print_test "检查 Redis 连接"
if docker exec teamventure-redis redis-cli -a redis123456 PING 2>&1 | grep -q "PONG"; then
    print_success "Redis 连接正常"
else
    print_failure "Redis 连接失败"
    exit 1
fi

# ====================================
# 测试 1: 新用户登录
# ====================================
print_header "测试 1: 新用户首次登录"

TEST_CODE_1="E2E_NEW_USER_$(date +%s)"
TEST_NICKNAME_1="E2E测试用户"
TEST_AVATAR_1="https://example.com/avatar-new.jpg"

print_test "发送登录请求 (新用户)"
LOGIN_RESPONSE_1=$(curl -s -X POST "$API_BASE_URL/auth/wechat/login" \
    -H "Content-Type: application/json" \
    -d "{\"code\":\"$TEST_CODE_1\",\"nickname\":\"$TEST_NICKNAME_1\",\"avatarUrl\":\"$TEST_AVATAR_1\"}")

print_info "响应内容:"
echo "$LOGIN_RESPONSE_1" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE_1"

# 验证响应结构
print_test "验证响应结构"
assert_json_field "$LOGIN_RESPONSE_1" "['success']" "True" || true
assert_json_field "$LOGIN_RESPONSE_1" "['data']['sessionToken']" || true
assert_json_field "$LOGIN_RESPONSE_1" "['data']['userInfo']['user_id']" || true
assert_json_field "$LOGIN_RESPONSE_1" "['data']['userInfo']['nickname']" "$TEST_NICKNAME_1" || true
assert_json_field "$LOGIN_RESPONSE_1" "['data']['userInfo']['avatar']" "$TEST_AVATAR_1" || true
assert_json_field "$LOGIN_RESPONSE_1" "['data']['userInfo']['role']" "HR" || true

# 提取关键字段
USER_ID_1=$(json_get "$LOGIN_RESPONSE_1" "['data']['userInfo']['user_id']")
SESSION_TOKEN_1=$(json_get "$LOGIN_RESPONSE_1" "['data']['sessionToken']")

print_info "用户ID: $USER_ID_1"
print_info "Session Token: ${SESSION_TOKEN_1:0:50}..."

# 验证数据库
print_test "验证数据库存储"
verify_db_user "$USER_ID_1" "$TEST_NICKNAME_1" "$TEST_AVATAR_1" || true

# 验证 Redis
print_test "验证 Redis Session"
verify_redis_session "$SESSION_TOKEN_1" "$USER_ID_1" || true

# ====================================
# 测试 2: 现有用户重复登录并更新信息
# ====================================
print_header "测试 2: 现有用户重复登录并更新信息"

TEST_NICKNAME_2="E2E更新昵称"
TEST_AVATAR_2="https://example.com/avatar-updated.jpg"

print_test "发送登录请求 (相同 code，不同昵称和头像)"
LOGIN_RESPONSE_2=$(curl -s -X POST "$API_BASE_URL/auth/wechat/login" \
    -H "Content-Type: application/json" \
    -d "{\"code\":\"$TEST_CODE_1\",\"nickname\":\"$TEST_NICKNAME_2\",\"avatarUrl\":\"$TEST_AVATAR_2\"}")

print_info "响应内容:"
echo "$LOGIN_RESPONSE_2" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE_2"

# 验证用户ID相同（未创建新用户）
print_test "验证用户ID未变化"
USER_ID_2=$(json_get "$LOGIN_RESPONSE_2" "['data']['userInfo']['user_id']")
if [ "$USER_ID_2" == "$USER_ID_1" ]; then
    print_success "用户ID相同，未创建新用户: $USER_ID_2"
else
    print_failure "用户ID不同: 原 $USER_ID_1, 新 $USER_ID_2"
fi

# 验证信息已更新
print_test "验证昵称和头像已更新"
assert_json_field "$LOGIN_RESPONSE_2" "['data']['userInfo']['nickname']" "$TEST_NICKNAME_2" || true
assert_json_field "$LOGIN_RESPONSE_2" "['data']['userInfo']['avatar']" "$TEST_AVATAR_2" || true

# 验证数据库更新
print_test "验证数据库记录已更新"
verify_db_user "$USER_ID_1" "$TEST_NICKNAME_2" "$TEST_AVATAR_2" || true

# ====================================
# 测试 3: 空昵称和头像的处理
# ====================================
print_header "测试 3: 空昵称和头像的默认值处理"

TEST_CODE_3="E2E_EMPTY_$(date +%s)"

print_test "发送登录请求 (空昵称和头像)"
LOGIN_RESPONSE_3=$(curl -s -X POST "$API_BASE_URL/auth/wechat/login" \
    -H "Content-Type: application/json" \
    -d "{\"code\":\"$TEST_CODE_3\",\"nickname\":\"\",\"avatarUrl\":\"\"}")

print_info "响应内容:"
echo "$LOGIN_RESPONSE_3" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE_3"

# 验证默认昵称
print_test "验证使用默认昵称"
NICKNAME_3=$(json_get "$LOGIN_RESPONSE_3" "['data']['userInfo']['nickname']")
if [ ! -z "$NICKNAME_3" ]; then
    print_success "设置了默认昵称: $NICKNAME_3"
else
    print_failure "昵称为空，未设置默认值"
fi

# ====================================
# 测试 4: 并发登录
# ====================================
print_header "测试 4: 并发登录（10个用户）"

print_test "发起10个并发登录请求"
CONCURRENT_CODES=()
for i in {1..10}; do
    CODE="E2E_CONCURRENT_${i}_$(date +%s)"
    CONCURRENT_CODES+=("$CODE")
    curl -s -X POST "$API_BASE_URL/auth/wechat/login" \
        -H "Content-Type: application/json" \
        -d "{\"code\":\"$CODE\",\"nickname\":\"并发用户$i\",\"avatarUrl\":\"https://example.com/avatar$i.jpg\"}" \
        > /tmp/concurrent_$i.json &
done

wait  # 等待所有请求完成

print_test "验证所有并发请求成功"
SUCCESS_COUNT=0
for i in {1..10}; do
    if [ -f "/tmp/concurrent_$i.json" ]; then
        RESPONSE=$(cat /tmp/concurrent_$i.json)
        if echo "$RESPONSE" | grep -q '"success":true'; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        fi
        rm -f /tmp/concurrent_$i.json
    fi
done

if [ $SUCCESS_COUNT -eq 10 ]; then
    print_success "所有10个并发请求成功"
else
    print_failure "仅 $SUCCESS_COUNT/10 个并发请求成功"
fi

# ====================================
# 测试 5: 使用 Session Token 访问需要鉴权的接口
# ====================================
print_header "测试 5: Session Token 鉴权"

print_test "使用有效 Token 访问我的方案列表"
MY_PLANS_RESPONSE=$(curl -s -X GET "$API_BASE_URL/plans?page=1&page_size=10" \
    -H "Authorization: Bearer $SESSION_TOKEN_1")

print_info "我的方案响应:"
echo "$MY_PLANS_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$MY_PLANS_RESPONSE"

# 验证响应成功（即使列表为空）
if echo "$MY_PLANS_RESPONSE" | grep -q '"success":true'; then
    print_success "使用 Token 成功访问受保护接口"
else
    print_failure "Token 鉴权失败"
fi

print_test "使用无效 Token 访问"
INVALID_TOKEN_RESPONSE=$(curl -s -X GET "$API_BASE_URL/plans?page=1&page_size=10" \
    -H "Authorization: Bearer INVALID_TOKEN_12345")

if echo "$INVALID_TOKEN_RESPONSE" | grep -q "UNAUTHENTICATED\|Unauthorized\|401"; then
    print_success "无效 Token 正确返回未授权错误"
else
    print_failure "无效 Token 未正确处理"
fi

print_test "不提供 Token 访问"
NO_TOKEN_RESPONSE=$(curl -s -X GET "$API_BASE_URL/plans?page=1&page_size=10")

if echo "$NO_TOKEN_RESPONSE" | grep -q "UNAUTHENTICATED\|Unauthorized\|401"; then
    print_success "缺少 Token 正确返回未授权错误"
else
    print_failure "缺少 Token 未正确处理"
fi

# ====================================
# 测试 6: 特殊字符处理
# ====================================
print_header "测试 6: 特殊字符和边界情况"

TEST_CODE_6="E2E_SPECIAL_$(date +%s)"
SPECIAL_NICKNAME="测试<>\"'&用户"
SPECIAL_AVATAR="https://example.com/avatar?param=value&other=123"

print_test "发送包含特殊字符的登录请求"
LOGIN_RESPONSE_6=$(curl -s -X POST "$API_BASE_URL/auth/wechat/login" \
    -H "Content-Type: application/json" \
    -d "{\"code\":\"$TEST_CODE_6\",\"nickname\":\"$SPECIAL_NICKNAME\",\"avatarUrl\":\"$SPECIAL_AVATAR\"}")

if echo "$LOGIN_RESPONSE_6" | grep -q '"success":true'; then
    print_success "特殊字符处理成功"

    # 验证数据存储
    USER_ID_6=$(json_get "$LOGIN_RESPONSE_6" "['data']['userInfo']['user_id']")
    DB_CHECK=$(docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
        "SELECT nickname FROM users WHERE user_id='$USER_ID_6';" 2>&1 | grep -v Warning | tail -n 1)

    print_info "数据库中的昵称: $DB_CHECK"
else
    print_failure "特殊字符处理失败"
fi

# ====================================
# 测试 7: 昵称前后空格处理
# ====================================
print_header "测试 7: 昵称 trim 处理"

TEST_CODE_7="E2E_TRIM_$(date +%s)"
TRIMMED_NICKNAME="  TrimTest  "
EXPECTED_TRIMMED="TrimTest"

print_test "发送包含前后空格的昵称"
LOGIN_RESPONSE_7=$(curl -s -X POST "$API_BASE_URL/auth/wechat/login" \
    -H "Content-Type: application/json" \
    -d "{\"code\":\"$TEST_CODE_7\",\"nickname\":\"$TRIMMED_NICKNAME\",\"avatarUrl\":\"https://example.com/avatar.jpg\"}")

ACTUAL_NICKNAME=$(json_get "$LOGIN_RESPONSE_7" "['data']['userInfo']['nickname']")

if [ "$ACTUAL_NICKNAME" == "$EXPECTED_TRIMMED" ]; then
    print_success "昵称正确 trim: '$ACTUAL_NICKNAME'"
else
    print_failure "昵称 trim 失败: 期望 '$EXPECTED_TRIMMED', 实际 '$ACTUAL_NICKNAME'"
fi

# ====================================
# 清理测试数据
# ====================================
print_header "清理测试数据"

print_test "删除测试用户"
docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
    "DELETE FROM users WHERE nickname LIKE 'E2E%' OR nickname LIKE '并发用户%' OR nickname LIKE 'TrimTest%';" \
    > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "测试数据清理完成"
else
    print_failure "测试数据清理失败"
fi

print_test "清理 Redis 测试 Session"
docker exec teamventure-redis redis-cli -a redis123456 KEYS "session:*" 2>&1 | grep -v Warning | while read key; do
    docker exec teamventure-redis redis-cli -a redis123456 DEL "$key" > /dev/null 2>&1
done
print_success "Redis Session 清理完成"

# ====================================
# 测试总结
# ====================================
print_header "测试总结"

echo -e "总测试数: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "通过: ${GREEN}$TESTS_PASSED${NC}"
echo -e "失败: ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}所有测试通过！ ✓${NC}"
    echo -e "${GREEN}========================================${NC}\n"
    exit 0
else
    echo -e "\n${RED}========================================${NC}"
    echo -e "${RED}部分测试失败 ✗${NC}"
    echo -e "${RED}========================================${NC}\n"
    exit 1
fi
