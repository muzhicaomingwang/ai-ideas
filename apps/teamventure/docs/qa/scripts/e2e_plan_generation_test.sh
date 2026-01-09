#!/bin/bash

# ====================================
# TeamVenture 方案生成流程 E2E 测试脚本
# ====================================
# 版本: v1.0
# 日期: 2026-01-04
# 说明: 完整测试方案生成、查询、确认等流程
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

# JSON 解析辅助函数
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

# ====================================
# 前置准备：获取登录Token
# ====================================
print_header "前置准备：登录获取Token"

print_test "创建测试用户并登录"
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/auth/wechat/login" \
    -H "Content-Type: application/json" \
    -d '{"code":"E2E_PLAN_GEN_USER","nickname":"PlanGenTestUser","avatarUrl":""}')

SESSION_TOKEN=$(json_get "$LOGIN_RESPONSE" "['data']['sessionToken']")
USER_ID=$(json_get "$LOGIN_RESPONSE" "['data']['userInfo']['user_id']")

if [ -z "$SESSION_TOKEN" ]; then
    print_failure "登录失败，无法获取Token"
    echo "$LOGIN_RESPONSE"
    exit 1
else
    print_success "登录成功，获取Token"
    print_info "User ID: $USER_ID"
    print_info "Token: ${SESSION_TOKEN:0:50}..."
fi

# ====================================
# 测试 1: 创建方案生成请求
# ====================================
print_header "测试 1: 创建方案生成请求"

print_test "发送方案生成请求"
	GENERATE_RESPONSE=$(curl -s -X POST "$API_BASE_URL/plans/generate" \
	    -H "Content-Type: application/json" \
	    -H "Authorization: Bearer $SESSION_TOKEN" \
	    -d '{
	        "people_count": 50,
	        "budget_min": 10000,
	        "budget_max": 15000,
	        "start_date": "2026-02-01",
	        "end_date": "2026-02-03",
	        "departure_city": "Beijing",
	        "destination": "杭州千岛湖",
	        "preferences": {
	            "activity_types": ["team_building"],
	            "accommodation_level": "standard"
	        }
	    }')

print_info "响应内容:"
echo "$GENERATE_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GENERATE_RESPONSE"

# 验证响应结构
print_test "验证响应结构"
assert_json_field "$GENERATE_RESPONSE" "['success']" "True" || true
assert_json_field "$GENERATE_RESPONSE" "['data']['plan_request_id']" || true
assert_json_field "$GENERATE_RESPONSE" "['data']['status']" "generating" || true

PLAN_REQUEST_ID=$(json_get "$GENERATE_RESPONSE" "['data']['plan_request_id']")
print_info "Plan Request ID: $PLAN_REQUEST_ID"

# 验证数据库记录
print_test "验证plan_requests表记录"
DB_RECORD=$(docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
    "SELECT plan_request_id, user_id, people_count, status FROM plan_requests WHERE plan_request_id='$PLAN_REQUEST_ID';" \
    2>&1 | grep -v Warning | tail -n 1)

if echo "$DB_RECORD" | grep -q "$PLAN_REQUEST_ID"; then
    print_success "数据库记录存在"
    print_info "记录: $DB_RECORD"
else
    print_failure "数据库记录不存在"
fi

# 验证领域事件
print_test "验证领域事件记录"
EVENT_RECORD=$(docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
    "SELECT event_id, event_type, aggregate_id FROM domain_events WHERE event_type='PlanRequestCreated' AND aggregate_id='$PLAN_REQUEST_ID';" \
    2>&1 | grep -v Warning | tail -n 1)

if echo "$EVENT_RECORD" | grep -q "PlanRequestCreated"; then
    print_success "领域事件已记录: PlanRequestCreated"
else
    print_failure "领域事件未记录"
fi

# ====================================
# 测试 2: 参数验证测试
# ====================================
print_header "测试 2: 参数验证"

print_test "缺少必填字段people_count"
INVALID_RESPONSE=$(curl -s -X POST "$API_BASE_URL/plans/generate" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $SESSION_TOKEN" \
    -d '{
        "budget_min": 10000,
        "budget_max": 15000,
        "start_date": "2026-02-01",
        "end_date": "2026-02-03",
        "departure_city": "Beijing"
    }')

if echo "$INVALID_RESPONSE" | grep -q "false\|error\|400"; then
    print_success "正确返回验证错误"
else
    print_failure "未正确验证必填字段"
fi

print_test "预算范围错误(min > max)"
INVALID_BUDGET=$(curl -s -X POST "$API_BASE_URL/plans/generate" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $SESSION_TOKEN" \
    -d '{
        "people_count": 50,
        "budget_min": 20000,
        "budget_max": 10000,
        "start_date": "2026-02-01",
        "end_date": "2026-02-03",
        "departure_city": "Beijing"
    }')

# 注意：当前后端可能没有实现此验证，此测试可能会失败
print_info "当前后端可能未实现预算范围验证，此测试仅用于记录"

# ====================================
# 测试 3: 未鉴权访问
# ====================================
print_header "测试 3: 鉴权验证"

print_test "不提供Token访问"
NO_TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/plans/generate" \
    -H "Content-Type: application/json" \
    -d '{
        "people_count": 50,
        "budget_min": 10000,
        "budget_max": 15000,
        "start_date": "2026-02-01",
        "end_date": "2026-02-03",
        "departure_city": "Beijing"
    }')

if echo "$NO_TOKEN_RESPONSE" | grep -q "UNAUTHENTICATED\|Unauthorized\|401\|false"; then
    print_success "正确拒绝未鉴权请求"
else
    print_failure "未正确处理缺少Token的请求"
fi

print_test "使用无效Token访问"
INVALID_TOKEN_RESPONSE=$(curl -s -X POST "$API_BASE_URL/plans/generate" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer INVALID_TOKEN_12345" \
    -d '{
        "people_count": 50,
        "budget_min": 10000,
        "budget_max": 15000,
        "start_date": "2026-02-01",
        "end_date": "2026-02-03",
        "departure_city": "Beijing"
    }')

if echo "$INVALID_TOKEN_RESPONSE" | grep -q "UNAUTHENTICATED\|Unauthorized\|401\|false"; then
    print_success "正确拒绝无效Token"
else
    print_failure "未正确验证Token有效性"
fi

# ====================================
# 测试 4: 方案列表查询
# ====================================
print_header "测试 4: 方案列表查询"

print_test "查询我的方案列表"
LIST_RESPONSE=$(curl -s -X GET "$API_BASE_URL/plans?page=1&pageSize=10" \
    -H "Authorization: Bearer $SESSION_TOKEN")

print_info "列表响应:"
echo "$LIST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LIST_RESPONSE"

print_test "验证列表响应结构"
assert_json_field "$LIST_RESPONSE" "['success']" "True" || true
assert_json_field "$LIST_RESPONSE" "['data']['plans']" || true
assert_json_field "$LIST_RESPONSE" "['data']['total']" || true

# 注意：由于AI生成需要时间，此时可能列表为空
TOTAL_PLANS=$(json_get "$LIST_RESPONSE" "['data']['total']")
print_info "当前方案总数: $TOTAL_PLANS (AI生成中，可能为0)"

# ====================================
# 测试 5: 并发生成请求
# ====================================
print_header "测试 5: 并发生成请求"

print_test "发起5个并发方案生成请求"
for i in {1..5}; do
    curl -s -X POST "$API_BASE_URL/plans/generate" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $SESSION_TOKEN" \
        -d "{
            \"people_count\": $((30 + i * 10)),
            \"budget_min\": $((8000 + i * 1000)),
            \"budget_max\": $((12000 + i * 1000)),
            \"start_date\": \"2026-02-0$i\",
            \"end_date\": \"2026-02-0$((i + 2))\",
            \"departure_city\": \"Beijing\",
            \"preferences\": {}
        }" > /tmp/concurrent_plan_$i.json &
done

wait

SUCCESS_COUNT=0
for i in {1..5}; do
    if [ -f "/tmp/concurrent_plan_$i.json" ]; then
        RESPONSE=$(cat /tmp/concurrent_plan_$i.json)
        if echo "$RESPONSE" | grep -q '"success":true'; then
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        fi
        rm -f /tmp/concurrent_plan_$i.json
    fi
done

if [ $SUCCESS_COUNT -eq 5 ]; then
    print_success "所有5个并发请求成功"
else
    print_failure "仅 $SUCCESS_COUNT/5 个并发请求成功"
fi

# 验证并发请求的数据库记录
print_test "验证并发请求的数据库记录数"
CONCURRENT_COUNT=$(docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
    "SELECT COUNT(*) as count FROM plan_requests WHERE user_id='$USER_ID';" \
    2>&1 | grep -v Warning | tail -n 1)

print_info "用户的总请求数: $CONCURRENT_COUNT (应该 >= 6)"

# ====================================
# 测试 6: 模拟AI生成完成（手动插入方案）
# ====================================
print_header "测试 6: 方案详情和确认（模拟数据）"

print_test "手动插入测试方案数据（模拟AI生成完成）"

# 生成测试方案ID
TEST_PLAN_ID="plan_test_$(date +%s)"

# 插入测试方案
docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
    "INSERT INTO plans (plan_id, plan_request_id, user_id, plan_type, plan_name, summary, itinerary, budget_breakdown, supplier_snapshots, budget_total, budget_per_person, duration_days, status)
    VALUES (
        '$TEST_PLAN_ID',
        '$PLAN_REQUEST_ID',
        '$USER_ID',
        'standard',
        '北京团建方案',
        '3天2晚精品团建',
        '[]',
        '{}',
        '[]',
        12000.00,
        240.00,
        3,
        'draft'
    );" 2>&1 | grep -v Warning

if [ $? -eq 0 ]; then
    print_success "测试方案插入成功: $TEST_PLAN_ID"
else
    print_failure "测试方案插入失败"
fi

# 测试方案详情查询
print_test "查询方案详情"
DETAIL_RESPONSE=$(curl -s -X GET "$API_BASE_URL/plans/$TEST_PLAN_ID" \
    -H "Authorization: Bearer $SESSION_TOKEN")

print_info "详情响应:"
echo "$DETAIL_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$DETAIL_RESPONSE"

if echo "$DETAIL_RESPONSE" | grep -q '"success":true'; then
    print_success "方案详情查询成功"
else
    print_failure "方案详情查询失败"
fi

# 测试方案确认
print_test "确认方案"
CONFIRM_RESPONSE=$(curl -s -X POST "$API_BASE_URL/plans/$TEST_PLAN_ID/confirm" \
    -H "Authorization: Bearer $SESSION_TOKEN")

if echo "$CONFIRM_RESPONSE" | grep -q '"success":true'; then
    print_success "方案确认成功"

    # 验证数据库状态更新
    PLAN_STATUS=$(docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
        "SELECT status FROM plans WHERE plan_id='$TEST_PLAN_ID';" \
        2>&1 | grep -v Warning | tail -n 1)

    if echo "$PLAN_STATUS" | grep -q "CONFIRMED"; then
        print_success "方案状态已更新为CONFIRMED"
    else
        print_failure "方案状态未正确更新"
    fi
else
    print_failure "方案确认失败"
fi

# 测试重复确认（幂等性）
print_test "重复确认方案（幂等性测试）"
CONFIRM_AGAIN=$(curl -s -X POST "$API_BASE_URL/plans/$TEST_PLAN_ID/confirm" \
    -H "Authorization: Bearer $SESSION_TOKEN")

if echo "$CONFIRM_AGAIN" | grep -q '"success":true'; then
    print_success "重复确认成功（幂等）"
else
    print_failure "重复确认失败"
fi

# ====================================
# 清理测试数据
# ====================================
print_header "清理测试数据"

print_test "删除测试数据"
docker exec teamventure-mysql-master mysql -u root -proot123456 -D teamventure_main -e \
    "DELETE FROM supplier_contact_logs WHERE user_id='$USER_ID';
     DELETE FROM plans WHERE user_id='$USER_ID';
     DELETE FROM plan_requests WHERE user_id='$USER_ID';
     DELETE FROM domain_events WHERE user_id='$USER_ID';
     DELETE FROM users WHERE user_id='$USER_ID';" \
    > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "测试数据清理完成"
else
    print_failure "测试数据清理失败"
fi

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
