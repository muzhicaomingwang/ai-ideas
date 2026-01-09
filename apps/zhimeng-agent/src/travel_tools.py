"""旅行工具集成模块

集成 MCP 服务实现真实的旅行数据查询：
- Kiwi: 航班搜索
- 高德地图: 路线规划、POI搜索
- Travel Planner: 行程规划 (Google Maps)
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KiwiFlightSearch:
    """Kiwi 航班搜索 MCP 客户端"""

    BASE_URL = "https://mcp.kiwi.com/mcp"

    def __init__(self):
        self.session_id: Optional[str] = None
        self.client = httpx.Client(timeout=60.0)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

    def _initialize(self) -> bool:
        """初始化 MCP 会话"""
        try:
            init_payload = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "zhimeng-agent", "version": "1.0.0"},
                },
                "id": 1,
            }

            resp = self.client.post(
                self.BASE_URL, json=init_payload, headers=self.headers
            )
            self.session_id = resp.headers.get("mcp-session-id")

            if self.session_id:
                self.headers["mcp-session-id"] = self.session_id
                # Send initialized notification
                self.client.post(
                    self.BASE_URL,
                    json={"jsonrpc": "2.0", "method": "notifications/initialized"},
                    headers=self.headers,
                )
                return True
        except Exception as e:
            logger.error(f"Kiwi MCP 初始化失败: {e}")
        return False

    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
    ) -> dict:
        """搜索航班

        Args:
            origin: 出发机场代码 (如 BJS, SHA, PEK)
            destination: 目的地机场代码
            departure_date: 出发日期 (YYYY-MM-DD 格式，会自动转换)
            return_date: 返程日期 (可选)

        Returns:
            航班搜索结果
        """
        if not self.session_id:
            if not self._initialize():
                return {"error": "无法连接 Kiwi 航班服务"}

        # 转换日期格式: YYYY-MM-DD -> DD/MM/YYYY
        try:
            dt = datetime.strptime(departure_date, "%Y-%m-%d")
            date_formatted = dt.strftime("%d/%m/%Y")
        except ValueError:
            date_formatted = departure_date

        search_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "search-flight",
                "arguments": {
                    "flyFrom": origin,
                    "flyTo": destination,
                    "departureDate": date_formatted,
                },
            },
            "id": 2,
        }

        try:
            resp = self.client.post(
                self.BASE_URL, json=search_payload, headers=self.headers
            )

            # 解析 SSE 响应
            for line in resp.text.split("\n"):
                if line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if "result" in data:
                        content = data["result"].get("content", [])
                        for item in content:
                            if item.get("type") == "text":
                                return {
                                    "success": True,
                                    "flights": json.loads(item["text"]),
                                }
                    elif "error" in data:
                        return {"error": data["error"].get("message", "搜索失败")}

        except Exception as e:
            logger.error(f"航班搜索失败: {e}")
            return {"error": str(e)}

        return {"error": "未获取到航班数据"}

    def format_flights(self, result: dict, max_results: int = 5) -> str:
        """格式化航班结果为可读文本"""
        if "error" in result:
            return f"❌ 航班搜索失败: {result['error']}"

        flights = result.get("flights", [])
        if not flights:
            return "未找到符合条件的航班"

        lines = [f"✈️ 找到 {len(flights)} 个航班选项：\n"]

        for i, f in enumerate(flights[:max_results], 1):
            # 解析时间
            dep = f.get("departure", {})
            arr = f.get("arrival", {})
            dep_local = dep.get("local", "") if isinstance(dep, dict) else ""
            arr_local = arr.get("local", "") if isinstance(arr, dict) else ""

            dep_time = dep_local[11:16] if dep_local else "N/A"
            arr_time = arr_local[11:16] if arr_local else "N/A"

            # 计算时长
            duration_str = ""
            if dep_local and arr_local:
                try:
                    dep_dt = datetime.fromisoformat(dep_local.replace(".000", ""))
                    arr_dt = datetime.fromisoformat(arr_local.replace(".000", ""))
                    delta = arr_dt - dep_dt
                    hours = delta.seconds // 3600
                    mins = (delta.seconds % 3600) // 60
                    duration_str = f"({hours}h{mins}m)"
                except Exception:
                    pass

            # 价格
            price_eur = f.get("price", 0)
            price_cny = int(price_eur * 7.8)

            lines.append(f"**航班 {i}**: {dep_time} → {arr_time} {duration_str}")
            lines.append(f"   💰 €{price_eur} (约 ¥{price_cny})")

            # 航空公司
            airlines = f.get("airlines", [])
            if airlines:
                lines.append(f"   ✈️ {', '.join(airlines)}")

            lines.append("")

        return "\n".join(lines)

    def close(self):
        """关闭客户端"""
        self.client.close()


class AmapMaps:
    """高德地图 MCP 客户端 (SSE)"""

    BASE_URL = "https://mcp.amap.com/sse"

    def __init__(self):
        self.client = httpx.Client(timeout=30.0)
        self.api_key = os.getenv("AMAP_API_KEY") or os.getenv("GAODE_API_KEY") or ""

    def search_poi(self, keywords: str, city: str = "") -> dict:
        """搜索 POI (地点)

        Args:
            keywords: 搜索关键词
            city: 城市名 (可选)

        Returns:
            POI 搜索结果
        """
        if not self.api_key:
            return {"error": "missing AMAP_API_KEY (or GAODE_API_KEY) env var"}
        try:
            params = {"key": self.api_key, "keywords": keywords}
            if city:
                params["city"] = city

            # 高德 MCP 使用 SSE，这里简化调用
            url = f"{self.BASE_URL}?key={self.api_key}"
            # 实际调用需要通过 SSE 协议
            # 这里使用 REST API 作为替代
            rest_url = "https://restapi.amap.com/v3/place/text"
            params["output"] = "json"

            resp = self.client.get(rest_url, params=params)
            return resp.json()
        except Exception as e:
            logger.error(f"POI 搜索失败: {e}")
            return {"error": str(e)}

    def route_planning(
        self, origin: str, destination: str, mode: str = "driving"
    ) -> dict:
        """路线规划

        Args:
            origin: 起点 (经纬度 "lng,lat" 或地名)
            destination: 终点
            mode: 出行方式 (driving/walking/transit)

        Returns:
            路线规划结果
        """
        try:
            # 使用高德 REST API
            if mode == "transit":
                url = "https://restapi.amap.com/v3/direction/transit/integrated"
            elif mode == "walking":
                url = "https://restapi.amap.com/v3/direction/walking"
            else:
                url = "https://restapi.amap.com/v3/direction/driving"

            params = {
                "key": self.API_KEY,
                "origin": origin,
                "destination": destination,
                "output": "json",
            }

            resp = self.client.get(url, params=params)
            return resp.json()
        except Exception as e:
            logger.error(f"路线规划失败: {e}")
            return {"error": str(e)}

    def close(self):
        self.client.close()


class TravelTools:
    """旅行工具聚合类"""

    def __init__(self):
        self._kiwi: Optional[KiwiFlightSearch] = None
        self._amap: Optional[AmapMaps] = None

    @property
    def kiwi(self) -> KiwiFlightSearch:
        if self._kiwi is None:
            self._kiwi = KiwiFlightSearch()
        return self._kiwi

    @property
    def amap(self) -> AmapMaps:
        if self._amap is None:
            self._amap = AmapMaps()
        return self._amap

    def search_flights(
        self,
        origin: str,
        destination: str,
        date: str,
        format_output: bool = True,
    ) -> str:
        """搜索航班并返回格式化结果

        Args:
            origin: 出发城市/机场 (如 "北京", "BJS", "PEK")
            destination: 目的城市/机场
            date: 日期 (支持 "明天", "本周六", "2026-01-20" 等格式)
            format_output: 是否格式化输出

        Returns:
            格式化的航班信息
        """
        # 城市名转机场代码
        city_to_code = {
            "北京": "BJS",
            "上海": "SHA",
            "广州": "CAN",
            "深圳": "SZX",
            "成都": "CTU",
            "杭州": "HGH",
            "西安": "XIY",
            "重庆": "CKG",
            "南京": "NKG",
            "武汉": "WUH",
            "青岛": "TAO",
            "大连": "DLC",
            "厦门": "XMN",
            "昆明": "KMG",
            "三亚": "SYX",
        }

        origin_code = city_to_code.get(origin, origin.upper())
        dest_code = city_to_code.get(destination, destination.upper())

        # 解析日期
        date_str = self._parse_date(date)

        result = self.kiwi.search_flights(origin_code, dest_code, date_str)

        if format_output:
            return self.kiwi.format_flights(result)
        return json.dumps(result, ensure_ascii=False)

    def _parse_date(self, date_input: str) -> str:
        """解析日期输入为 YYYY-MM-DD 格式"""
        today = datetime.now()

        if "明天" in date_input:
            target = today + timedelta(days=1)
        elif "后天" in date_input:
            target = today + timedelta(days=2)
        elif "本周六" in date_input or "这周六" in date_input:
            days_until = (5 - today.weekday()) % 7
            if days_until == 0:
                days_until = 7
            target = today + timedelta(days=days_until)
        elif "本周日" in date_input or "这周日" in date_input:
            days_until = (6 - today.weekday()) % 7
            if days_until == 0:
                days_until = 7
            target = today + timedelta(days=days_until)
        elif "下周" in date_input:
            # 下周一
            days_until = (7 - today.weekday()) % 7 + 7
            target = today + timedelta(days=days_until)
        else:
            # 尝试解析日期字符串
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%m月%d日", "%d/%m/%Y"]:
                try:
                    target = datetime.strptime(date_input, fmt)
                    if target.year < 2000:
                        target = target.replace(year=today.year)
                    break
                except ValueError:
                    continue
            else:
                # 默认返回 7 天后
                target = today + timedelta(days=7)

        return target.strftime("%Y-%m-%d")

    def close(self):
        """关闭所有客户端"""
        if self._kiwi:
            self._kiwi.close()
        if self._amap:
            self._amap.close()


# 单例
_travel_tools: Optional[TravelTools] = None


def get_travel_tools() -> TravelTools:
    """获取旅行工具单例"""
    global _travel_tools
    if _travel_tools is None:
        _travel_tools = TravelTools()
    return _travel_tools


# 便捷函数
def search_flights(origin: str, destination: str, date: str) -> str:
    """搜索航班的便捷函数"""
    tools = get_travel_tools()
    return tools.search_flights(origin, destination, date)


if __name__ == "__main__":
    # 测试
    print("=== 测试航班搜索 ===")
    result = search_flights("北京", "上海", "2026-01-20")
    print(result)
