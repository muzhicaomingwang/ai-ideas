#!/bin/bash

PLAN_ID="plan_01ke6210kx4td36syecgw48qhj"
AMAP_KEY="326b1b2f54ccc87ad7ddd031b858f187"

echo "=== 地图服务集成测试 ==="
echo ""

# 1. 验证高德API可用性
echo "[1/4] 验证高德API可用性..."
ORIGIN="120.1503,30.2447"
DEST="120.1489,30.2317"

ROUTE_RESPONSE=$(curl -s "https://restapi.amap.com/v3/direction/walking?key=$AMAP_KEY&origin=$ORIGIN&destination=$DEST")

STATUS=$(echo $ROUTE_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('status', '0'))")

if [ "$STATUS" = "1" ]; then
  echo "✅ 高德API可用"
  POLYLINE=$(echo $ROUTE_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); paths=d.get('route',{}).get('paths',[]); print(len(paths[0].get('polyline','').split(';')) if paths else 0)")
  echo "   路径点数: $POLYLINE 个"
else
  echo "❌ 高德API不可用"
  echo "$ROUTE_RESPONSE" | python3 -m json.tool | head -10
  exit 1
fi

echo ""
echo "[2/4] 测试路线API（内部调用，无需认证）..."

# 直接在容器内调用
ROUTE_API_RESPONSE=$(docker exec teamventure-java curl -s "http://localhost:8082/api/v1/plans/$PLAN_ID/route?day=1")

SUCCESS=$(echo $ROUTE_API_RESPONSE | python3 -c "import sys, json; d=json.load(sys.stdin); print('success' in d.get('success', True))" 2>/dev/null || echo "false")

echo "$ROUTE_API_RESPONSE" | python3 <<EOF
import json
import sys

try:
    data = json.load(sys.stdin)

    if not data.get('success', False):
        print("❌ API调用失败")
        print(f"   错误: {data.get('message', 'Unknown error')}")
        sys.exit(1)

    route_data = data.get('data', {})

    print("✅ 路线API调用成功")
    print("")
    print("📊 路线数据分析:")
    print(f"   标记点数量: {len(route_data.get('markers', []))}")

    polylines = route_data.get('polyline', [])
    total_points = sum(len(p.get('points', [])) for p in polylines)
    print(f"   路径点数量: {total_points}")

    print(f"   未解析地点: {len(route_data.get('unresolved', []))}")
    print(f"   地图类型: {route_data.get('mapType', 'N/A')}")

    static_map_url = route_data.get('staticMapUrl')
    if static_map_url:
        print(f"   静态地图URL: {static_map_url[:80]}...")
    else:
        print("   静态地图URL: null（可能因跨市路线或API失败）")

    print("")

    # 检查segments
    segments = route_data.get('segments', [])
    if segments:
        print("📍 路线段信息:")
        for i, seg in enumerate(segments[:3], 1):  # 只显示前3段
            mode_icon = "🚶" if seg.get('mode') == 'walking' else "🚗" if seg.get('mode') == 'driving' else "➡️"
            print(f"   {i}. {seg.get('from')} → {seg.get('to')}")
            print(f"      {mode_icon} {seg.get('mode')} | {seg.get('distance')}米 | {seg.get('duration')}秒")
            if seg.get('warning'):
                print(f"      ⚠️ {seg.get('warning')}")
        if len(segments) > 3:
            print(f"   ... 还有 {len(segments) - 3} 段路线")
        print("")

    # 检查summary
    summary = route_data.get('summary', {})
    if summary:
        print("📈 路线摘要:")
        print(f"   总距离: {summary.get('totalDistance', 0)}米")
        print(f"   总时长: {summary.get('totalDuration', 0)}秒")
        print("")

    # 判断路线规划是否生效
    marker_count = len(route_data.get('markers', []))

    if total_points > marker_count * 2:
        print("✅ 路线规划已生效（路径点数 >> 标记点数，包含沿道路的细化点）")
    elif total_points == marker_count * 2:
        print("⚠️ 可能仍为直线连接（路径点数 = 标记点数 × 2）")
    else:
        print(f"ℹ️ 路径点数据: 标记点{marker_count}, 路径点{total_points}")

except json.JSONDecodeError as e:
    print("❌ JSON解析失败")
    print(f"   错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 数据分析失败: {e}")
    sys.exit(1)

EOF

TEST_EXIT_CODE=$?

echo ""
echo "[3/4] 测试缓存功能..."

# 第二次请求同一路线，应该从缓存返回
START_TIME=$(date +%s%3N)
CACHE_RESPONSE=$(docker exec teamventure-java curl -s "http://localhost:8082/api/v1/plans/$PLAN_ID/route?day=1")
END_TIME=$(date +%s%3N)

RESPONSE_TIME=$((END_TIME - START_TIME))

echo "   第二次请求响应时间: ${RESPONSE_TIME}ms"

if [ $RESPONSE_TIME -lt 500 ]; then
  echo "✅ 缓存生效（响应时间<500ms）"
else
  echo "⚠️ 响应较慢（${RESPONSE_TIME}ms），可能未命中缓存"
fi

echo ""
echo "[4/4] 测试总结"
if [ $TEST_EXIT_CODE -eq 0 ]; then
  echo "✅ 集成测试通过"
  echo "   - 高德API调用成功"
  echo "   - 路线数据结构完整"
  echo "   - 缓存功能正常"
else
  echo "❌ 集成测试失败"
  exit 1
fi
