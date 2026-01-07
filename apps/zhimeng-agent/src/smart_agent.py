"""智能 Agent

根据问题类型，选择合适的工具回答：
- 知识库检索：个人笔记、方法论、技术文档
- Web 搜索：实时信息（机票、天气、新闻等）
- 旅行工具：航班搜索（Kiwi MCP）、地图服务（高德）
- 对话记忆：记住与每个用户的对话历史
- 知识沉淀：将有价值的回答自动保存到 Obsidian
"""

import json
import logging
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import httpx

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config.settings import settings
from src.travel_tools import get_travel_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 需要 Web 搜索的问题关键词
REALTIME_KEYWORDS = [
    "机票", "航班", "火车票", "酒店", "价格", "多少钱",
    "天气", "温度", "下雨",
    "新闻", "最新", "今天", "明天", "本周", "下周",
    "股票", "汇率", "比特币",
    "路况", "地图", "怎么走",
    "电话", "地址", "营业时间",
]


def needs_web_search(question: str) -> bool:
    """判断问题是否需要 Web 搜索"""
    question_lower = question.lower()
    for keyword in REALTIME_KEYWORDS:
        if keyword in question_lower:
            return True
    return False


def web_search(query: str, num_results: int = 5) -> str:
    """使用搜索引擎搜索实时信息

    Args:
        query: 搜索查询
        num_results: 返回结果数量

    Returns:
        搜索结果文本或搜索建议
    """
    # 对于旅行相关查询，提供专业平台建议
    travel_keywords = ["机票", "航班", "酒店", "火车票", "高铁"]
    is_travel_query = any(kw in query for kw in travel_keywords)

    if is_travel_query:
        # 构建旅行查询的智能建议
        suggestions = generate_travel_suggestions(query)
        return suggestions

    # 其他查询尝试通用搜索
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))

        if results:
            formatted = []
            for i, r in enumerate(results, 1):
                formatted.append(f"{i}. **{r.get('title', 'N/A')}**")
                formatted.append(f"   {r.get('body', 'N/A')}")
                formatted.append(f"   来源: {r.get('href', 'N/A')}")
                formatted.append("")
            return "\n".join(formatted)

    except Exception as e:
        logger.warning(f"搜索失败: {e}")

    # 通用搜索建议
    return generate_search_suggestions(query)


def parse_flight_query(query: str) -> Optional[dict]:
    """解析航班查询，提取出发地、目的地、日期

    Returns:
        dict with keys: origin, destination, date
        None if not a flight query or cannot parse
    """
    from datetime import datetime, timedelta

    # 城市列表
    cities = ["北京", "上海", "广州", "深圳", "成都", "杭州", "西安",
              "重庆", "南京", "武汉", "青岛", "大连", "厦门", "昆明", "三亚"]

    # 检测是否是航班查询
    flight_keywords = ["机票", "航班", "飞", "坐飞机"]
    if not any(kw in query for kw in flight_keywords):
        return None

    # 提取城市
    found_cities = [c for c in cities if c in query]
    if len(found_cities) < 2:
        return None

    # 判断出发地和目的地（通过"到"、"去"、"飞"等介词）
    origin = None
    destination = None

    # 模式: "从X到Y" 或 "X到Y" 或 "X飞Y" 或 "去Y"
    patterns = [
        r"从(.+?)到(.+)",
        r"(.+?)到(.+)",
        r"(.+?)飞(.+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            for city in cities:
                if city in match.group(1):
                    origin = city
                    break
            for city in cities:
                if city in match.group(2):
                    destination = city
                    break
            if origin and destination:
                break

    if not origin or not destination:
        # 默认第一个为出发地，第二个为目的地
        origin = found_cities[0]
        destination = found_cities[1]

    # 解析日期
    date = None
    today = datetime.now()

    if "明天" in query:
        date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "后天" in query:
        date = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    elif "本周六" in query or "这周六" in query:
        days_until = (5 - today.weekday()) % 7
        if days_until == 0:
            days_until = 7
        date = (today + timedelta(days=days_until)).strftime("%Y-%m-%d")
    elif "本周日" in query or "这周日" in query:
        days_until = (6 - today.weekday()) % 7
        if days_until == 0:
            days_until = 7
        date = (today + timedelta(days=days_until)).strftime("%Y-%m-%d")
    elif "下周" in query:
        days_until = (7 - today.weekday()) % 7 + 7
        date = (today + timedelta(days=days_until)).strftime("%Y-%m-%d")
    else:
        # 尝试匹配日期格式
        date_patterns = [
            (r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", lambda m: f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"),
            (r"(\d{1,2})月(\d{1,2})日?", lambda m: f"{today.year}-{m.group(1).zfill(2)}-{m.group(2).zfill(2)}"),
        ]
        for pattern, formatter in date_patterns:
            match = re.search(pattern, query)
            if match:
                date = formatter(match)
                break

        if not date:
            # 默认 7 天后
            date = (today + timedelta(days=7)).strftime("%Y-%m-%d")

    return {
        "origin": origin,
        "destination": destination,
        "date": date,
    }


def generate_travel_suggestions(query: str) -> str:
    """为旅行查询生成专业建议，优先使用 MCP 工具获取实时数据"""
    from datetime import datetime, timedelta

    # 尝试解析航班查询
    flight_info = parse_flight_query(query)

    if flight_info:
        # 使用 Kiwi MCP 搜索真实航班
        logger.info(f"检测到航班查询: {flight_info}")
        try:
            travel_tools = get_travel_tools()
            result = travel_tools.search_flights(
                origin=flight_info["origin"],
                destination=flight_info["destination"],
                date=flight_info["date"],
                format_output=True,
            )

            if "❌" not in result and "未找到" not in result:
                # 成功获取航班数据
                header = f"## {flight_info['origin']} → {flight_info['destination']} 航班查询\n"
                header += f"**出发日期：** {flight_info['date']}\n\n"
                return header + result + "\n\n" + _get_booking_tips()
            else:
                logger.warning(f"航班搜索无结果或失败: {result}")
        except Exception as e:
            logger.error(f"航班搜索异常: {e}")

    # 回退到静态建议
    return _generate_static_travel_suggestions(query)


def _get_booking_tips() -> str:
    """获取订票小贴士"""
    return """---
**💡 订票小贴士：**
- 建议通过 [携程](https://flights.ctrip.com)、[去哪儿](https://flight.qunar.com) 比价后预订
- 早上6-8点航班通常更便宜
- 提前7-14天预订性价比最高
- 关注航空公司会员日促销"""


def _generate_static_travel_suggestions(query: str) -> str:
    """生成静态旅行建议（当 MCP 不可用时的回退方案）"""
    from datetime import datetime, timedelta

    # 解析查询中的信息
    destination = ""
    if "北京" in query:
        destination = "北京"
    elif "上海" in query:
        destination = "上海"

    time_hint = ""
    if "本周六" in query:
        today = datetime.now()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        saturday = today + timedelta(days=days_until_saturday)
        time_hint = saturday.strftime("%Y年%m月%d日（周六）")
    elif "明天" in query:
        tomorrow = datetime.now() + timedelta(days=1)
        time_hint = tomorrow.strftime("%Y年%m月%d日")

    suggestions = f"""## 实时旅行信息查询建议

**您的需求：** {query}

**推荐查询平台：**

1. **携程旅行** - https://flights.ctrip.com
   - 机票比价、航班时刻查询
   - 支持多平台比价

2. **去哪儿** - https://flight.qunar.com
   - 低价机票搜索
   - 价格日历查看最便宜日期

3. **飞猪** - https://www.fliggy.com
   - 阿里系旅行平台
   - 常有会员专享折扣

4. **航空公司官网**
   - 国航: www.airchina.com.cn
   - 东航: www.ceair.com
   - 南航: www.csair.com
   - 官网有时有独家优惠

**省钱小贴士：**
- 早上6-8点航班通常更便宜
- 提前7-14天预订性价比最高
- 关注航空公司会员日促销
- 选择经停航班可能更省钱"""

    if time_hint:
        suggestions += f"\n\n**目标日期：** {time_hint}"

    return suggestions


def generate_search_suggestions(query: str) -> str:
    """为通用查询生成搜索建议"""
    return f"""## 搜索建议

由于实时搜索暂时不可用，建议您通过以下方式获取最新信息：

1. **搜索引擎**
   - Google: https://www.google.com
   - Bing: https://www.bing.com
   - 百度: https://www.baidu.com

2. **相关查询关键词**
   - 原始查询: {query}

如果您有关于 AI 产品设计、认知科学或软件工程的问题，我可以基于知识库为您详细解答。"""


def search_with_httpx(query: str, num_results: int = 5) -> str:
    """使用 httpx 直接搜索（备用方案）"""
    try:
        # 使用 DuckDuckGo HTML API
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        with httpx.Client(timeout=10.0) as client:
            response = client.post(url, data={"q": query}, headers=headers)

        if response.status_code != 200:
            return f"搜索失败: HTTP {response.status_code}"

        # 简单解析结果
        from html.parser import HTMLParser

        class ResultParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.results = []
                self.in_result = False
                self.current = {}

            def handle_starttag(self, tag, attrs):
                attrs_dict = dict(attrs)
                if tag == "a" and "result__a" in attrs_dict.get("class", ""):
                    self.in_result = True
                    self.current["url"] = attrs_dict.get("href", "")

            def handle_data(self, data):
                if self.in_result and data.strip():
                    self.current["title"] = data.strip()
                    self.results.append(self.current)
                    self.current = {}
                    self.in_result = False

        parser = ResultParser()
        parser.feed(response.text)

        if not parser.results:
            return "未找到搜索结果"

        formatted = []
        for i, r in enumerate(parser.results[:num_results], 1):
            formatted.append(f"{i}. **{r.get('title', 'N/A')}**")
            formatted.append(f"   来源: {r.get('url', 'N/A')}")
            formatted.append("")

        return "\n".join(formatted)

    except Exception as e:
        logger.error(f"备用搜索失败: {e}")
        return f"搜索出错: {e}"


class SmartAgent:
    """智能 Agent

    支持对话记忆和知识自动沉淀功能。
    """

    # 类级别的对话历史存储（按用户ID）
    _conversation_history: Dict[str, List[dict]] = defaultdict(list)

    # 配置
    MAX_HISTORY_TURNS = 10  # 最多记住10轮对话
    AUTO_SAVE_FOLDER = "AI-Generated"  # Obsidian 自动保存目录

    def __init__(self):
        from src.retriever import get_retriever
        from src.llm_client import get_llm_client

        self.retriever = get_retriever()
        self.llm_client = get_llm_client()

    def _get_conversation_context(self, user_id: str) -> str:
        """获取用户的对话历史作为上下文

        Args:
            user_id: 用户唯一标识（如飞书 open_id）

        Returns:
            格式化的对话历史文本
        """
        history = self._conversation_history.get(user_id, [])
        if not history:
            return ""

        context_parts = ["## 之前的对话记录\n"]
        for turn in history[-self.MAX_HISTORY_TURNS:]:
            context_parts.append(f"**用户**: {turn['question']}")
            # 只取回答的前500字作为历史上下文，避免太长
            answer_preview = turn['answer'][:500]
            if len(turn['answer']) > 500:
                answer_preview += "..."
            context_parts.append(f"**助手**: {answer_preview}\n")

        return "\n".join(context_parts)

    def _update_conversation_history(
        self,
        user_id: str,
        question: str,
        answer: str
    ) -> None:
        """更新用户的对话历史

        Args:
            user_id: 用户唯一标识
            question: 用户问题
            answer: 助手回答
        """
        self._conversation_history[user_id].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat(),
        })

        # 限制历史长度
        if len(self._conversation_history[user_id]) > self.MAX_HISTORY_TURNS * 2:
            self._conversation_history[user_id] = \
                self._conversation_history[user_id][-self.MAX_HISTORY_TURNS:]

    def _save_to_obsidian(
        self,
        question: str,
        answer: str,
        category: str = "general"
    ) -> Optional[str]:
        """将生成的内容保存到 Obsidian

        Args:
            question: 用户问题（用于生成文件名）
            answer: 生成的回答
            category: 分类（用于子目录）

        Returns:
            保存的文件路径，失败返回 None
        """
        try:
            # 构建保存路径
            vault_path = settings.vault_path
            save_dir = vault_path / self.AUTO_SAVE_FOLDER / category
            save_dir.mkdir(parents=True, exist_ok=True)

            # 生成文件名（基于问题和时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # 清理问题文本作为文件名
            safe_title = re.sub(r'[\\/*?:"<>|]', '', question)[:50]
            filename = f"{timestamp}_{safe_title}.md"
            file_path = save_dir / filename

            # 构建 Markdown 内容
            content = f"""# {question}

> 🤖 由 AI 自动生成 | {datetime.now().strftime("%Y-%m-%d %H:%M")}

{answer}

---

#ai-generated #{category}
"""

            # 写入文件
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"知识自动沉淀: {file_path}")

            return str(file_path)

        except Exception as e:
            logger.error(f"保存到 Obsidian 失败: {e}")
            return None

    def answer(
        self,
        question: str,
        top_k: int = 5,
        user_id: Optional[str] = None
    ) -> dict:
        """智能回答问题

        Args:
            question: 用户问题
            top_k: 知识库检索数量
            user_id: 用户唯一标识（用于对话记忆）

        Returns:
            回答结果 {"answer": str, "sources": list, "search_used": bool, "saved_to": str|None}
        """
        search_used = False
        search_results = ""
        kb_context = ""
        sources = []
        saved_to = None

        # 1. 判断是否需要 Web 搜索
        if needs_web_search(question):
            logger.info(f"问题需要 Web 搜索: {question}")
            search_results = web_search(question)
            search_used = True

        # 2. 同时检索知识库（可能有相关的方法论或经验）
        results = self.retriever.retrieve_with_context(
            query=question,
            top_k=top_k,
        )

        has_kb_content = False
        if results:
            # 检查是否有真正相关的内容（相关度 > 0.3）
            relevant_results = [r for r in results if r.get("relevance", 0) > 0.3]
            if relevant_results:
                has_kb_content = True
                kb_context = self.retriever.format_context(relevant_results)
                sources = [
                    {
                        "file": r["source"],
                        "folder": r["folder"],
                        "relevance": r["relevance"],
                    }
                    for r in relevant_results
                ]

        # 3. 构建综合上下文
        context_parts = []

        # 3.1 添加对话历史（如果有 user_id）
        if user_id:
            conversation_context = self._get_conversation_context(user_id)
            if conversation_context:
                context_parts.append(conversation_context)
                logger.info(f"已加载用户 {user_id[:8]}... 的对话历史")

        if search_results and "未找到" not in search_results and "出错" not in search_results:
            context_parts.append("## 实时搜索结果\n\n" + search_results)

        if kb_context:
            context_parts.append("## 知识库相关内容\n\n" + kb_context)

        if not context_parts:
            context = "没有找到相关信息。"
        else:
            context = "\n\n".join(context_parts)

        # 4. 生成回答
        system_prompt = self._get_system_prompt(search_used, has_kb_context=has_kb_content)
        answer = self.llm_client.generate(
            question=question,
            context=context,
            system_prompt=system_prompt,
        )

        # 5. 更新对话历史
        if user_id:
            self._update_conversation_history(user_id, question, answer)
            logger.info(f"已更新用户 {user_id[:8]}... 的对话历史")

        # 6. 知识自动沉淀：当知识库没有相关内容时，保存生成的回答
        if not has_kb_content and not search_used:
            # 只对知识型问题进行沉淀（排除闲聊、实时查询等）
            if self._is_knowledge_question(question):
                category = self._categorize_question(question)
                saved_to = self._save_to_obsidian(question, answer, category)
                if saved_to:
                    logger.info(f"知识自动沉淀成功: {saved_to}")

        return {
            "answer": answer,
            "sources": sources,
            "search_used": search_used,
            "saved_to": saved_to,
        }

    def _is_knowledge_question(self, question: str) -> bool:
        """判断是否是值得沉淀的知识型问题"""
        # 排除简单问候和闲聊
        casual_patterns = [
            r"^(你好|hi|hello|嗨|早上好|晚上好|下午好)",
            r"^(谢谢|感谢|thanks|thx)",
            r"^(再见|拜拜|bye)",
            r"^(今天.*?(天气|怎么样))",
            r"^(.{1,5})$",  # 太短的问题
        ]
        for pattern in casual_patterns:
            if re.match(pattern, question, re.IGNORECASE):
                return False

        # 知识型问题的特征
        knowledge_patterns = [
            r"(什么是|如何|怎么|为什么|什么叫|是什么|怎样)",
            r"(方法|技巧|原理|概念|定义|区别|比较)",
            r"(教程|指南|步骤|流程|最佳实践)",
            r"(推荐|建议|选择|评价)",
        ]
        for pattern in knowledge_patterns:
            if re.search(pattern, question):
                return True

        # 问题长度超过15字，且不是实时查询，也认为是知识型
        if len(question) > 15:
            return True

        return False

    def _categorize_question(self, question: str) -> str:
        """对问题进行分类，用于保存到不同子目录"""
        categories = {
            "技术": ["代码", "编程", "开发", "API", "数据库", "python", "java", "框架"],
            "产品": ["产品", "需求", "PRD", "用户", "功能", "设计", "体验"],
            "AI": ["AI", "人工智能", "机器学习", "大模型", "GPT", "Claude", "LLM"],
            "方法论": ["方法", "流程", "框架", "原则", "思维", "认知", "心理"],
            "商业": ["商业", "运营", "增长", "营销", "市场", "竞品"],
        }

        question_lower = question.lower()
        for category, keywords in categories.items():
            for kw in keywords:
                if kw.lower() in question_lower:
                    return category

        return "general"

    def _get_system_prompt(self, search_used: bool, has_kb_context: bool = True) -> str:
        """获取系统提示词"""
        base_prompt = """你是 zhimeng 的 AI 分身，由 Claude Opus 4.5 驱动的智能助手。

**核心能力**：
1. **通用知识**：利用你强大的基础能力直接回答问题，不要拘泥于知识库
2. **知识库**：zhimeng 的 Obsidian 笔记，可作为参考但非必须
3. **实时搜索**：通过 Web 搜索获取最新信息（如机票、天气、新闻等）

**回答原则**：

1. **直接回答**：优先使用你的知识和推理能力直接回答，不要因为知识库没有相关内容就说"无法回答"
2. **结构化输出**：使用清晰的标题、列表组织回答
3. **实用导向**：提供可操作的建议
4. **坦诚相告**：对于需要实时数据的问题（如具体价格），建议用户查询专业平台

**重要**：你是一个全能的AI助手，可以回答任何问题。知识库只是补充参考，不是回答的必要条件。"""

        if search_used:
            base_prompt += """

**注意**：本次回答包含实时搜索结果，请优先使用搜索结果回答实时性问题（如价格、时间等）。"""

        if not has_kb_context:
            base_prompt += """

**注意**：本次问题在知识库中没有找到相关内容，请直接用你的知识和能力回答问题。"""

        return base_prompt


# 单例
_smart_agent: Optional[SmartAgent] = None


def get_smart_agent() -> SmartAgent:
    """获取智能 Agent 单例"""
    global _smart_agent
    if _smart_agent is None:
        _smart_agent = SmartAgent()
    return _smart_agent
