#!/bin/bash
# 测试路线规划功能

set -e

echo "=== 地图路线规划功能测试 ==="
echo ""

# 配置
BASE_URL="http://localhost:8080"
TOKEN="${TOKEN:-eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzAxa2U3MjBjeHByeTZlZGRzbTlmcGM3c2QwIiwiaWF0IjoxNzY3NjM5NzU0LCJleHAiOjE3Njc3MjYxNTR9._UPsx35Dv47FiHf88wi5QzBXQM6fyNBZBceG6luROX8}"

# 1. 获取方案列表，找到一个已生成的方案
echo "1. 获取方案列表..."
PLANS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/plans?page=1&pageSize=10")

# 提取第一个已确认或reviewing状态的方案ID
PLAN_ID=$(echo "$PLANS_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
plans = data.get('data', {}).get('plans', [])
for plan in plans:
    status = plan.get('status', '')
    if status in ['confirmed', 'reviewing', 'draft']:
        print(plan.get('plan_id', ''))
        break
" 2>/dev/null)

if [ -z "$PLAN_ID" ]; then
  echo "❌ 未找到可用的方案，请先创建一个方案"
  exit 1
fi

echo "✓ 找到方案ID: $PLAN_ID"
echo ""

# 2. 获取方案路线（天数1）
echo "2. 获取方案路线（第1天）..."
ROUTE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/plans/$PLAN_ID/route?day=1")

echo "$ROUTE_RESPONSE" | python3 -c "
import sys, json

try:
    data = json.load(sys.stdin)

    if 'error' in data:
        print(f\"❌ 获取路线失败: {data.get('message', '未知错误')}\")
        sys.exit(1)

    route_data = data.get('data', {})

    # 检查基本字段
    markers = route_data.get('markers', [])
    polyline = route_data.get('polyline', [])
    include_points = route_data.get('include_points', [])
    segments = route_data.get('segments', [])
    summary = route_data.get('summary', {})
    unresolved = route_data.get('unresolved', [])

    print('=== 路线数据概览 ===')
    print(f'标记点数量: {len(markers)}')
    print(f'路径点数量: {len(include_points)}')
    print(f'路线段数量: {len(segments)}')
    print(f'未解析地点: {len(unresolved)}')
    print()

    # 检查summary
    if summary:
        total_distance = summary.get('totalDistance', 0)
        total_duration = summary.get('totalDuration', 0)
        print('=== 路线摘要 ===')
        print(f'总距离: {total_distance}米 ({total_distance/1000:.2f}公里)')
        print(f'总时长: {total_duration}秒 ({total_duration//60}分钟)')
        print()

    # 检查路线段详情
    if segments:
        print('=== 路线段详情 ===')
        for i, seg in enumerate(segments, 1):
            from_loc = seg.get('from', '')
            to_loc = seg.get('to', '')
            distance = seg.get('distance', 0)
            duration = seg.get('duration', 0)
            mode = seg.get('mode', '')
            warning = seg.get('warning', '')

            print(f'段{i}: {from_loc} → {to_loc}')
            print(f'  距离: {distance}米, 时长: {duration}秒, 方式: {mode}')
            if warning:
                print(f'  ⚠️  {warning}')
        print()

    # 验收标准检查
    print('=== 验收标准检查 ===')

    # 1. 路径点数量应该大于标记点数量（说明包含路径细化点）
    if len(include_points) > len(markers):
        print('✅ 路径点数量 > 标记点数量 (说明包含路径细化点)')
    else:
        print('⚠️  路径点数量 <= 标记点数量 (可能是直线连接或API失败)')

    # 2. 检查是否有segments数据
    if segments:
        print('✅ 包含路线段详情（segments字段）')
    else:
        print('❌ 缺少路线段详情（segments字段）')

    # 3. 检查是否有summary数据
    if summary and summary.get('totalDistance', 0) > 0:
        print('✅ 包含路线摘要（summary字段）')
    else:
        print('❌ 缺少路线摘要（summary字段）')

    # 4. 检查polyline格式
    if polyline and len(polyline) > 0:
        first_line = polyline[0]
        if 'points' in first_line and 'color' in first_line:
            print('✅ polyline格式正确')
        else:
            print('❌ polyline格式错误')
    else:
        print('❌ 缺少polyline数据')

    print()
    print('=== 测试结果 ===')

    # 判断测试是否通过
    passed = (
        len(include_points) >= len(markers) and
        len(segments) > 0 and
        summary.get('totalDistance', 0) > 0 and
        len(polyline) > 0
    )

    if passed:
        print('✅ 路线规划功能测试通过')
        sys.exit(0)
    else:
        print('⚠️  路线规划功能部分失败或降级为直线连接')
        sys.exit(2)

except json.JSONDecodeError:
    print('❌ 响应不是有效的JSON')
    sys.exit(1)
except Exception as e:
    print(f'❌ 测试失败: {e}')
    sys.exit(1)
"

echo ""
echo "=== 测试完成 ==="
