#!/usr/bin/env python3
"""
Reddit 数据分析脚本
对收集的 Reddit 数据进行 AI 分析，生成研究报告
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 分析类型提示词模板
ANALYSIS_PROMPTS = {
    "sentiment": """分析以下 Reddit 帖子和评论的情感倾向。

请识别：
1. 整体情感倾向（正面/负面/中性的比例）
2. 主要的正面观点和原因
3. 主要的负面观点和原因
4. 值得注意的中性/客观讨论

输出格式：
## 情感分析报告

### 整体情感分布
- 正面: X%
- 负面: X%
- 中性: X%

### 正面观点
[列出主要正面观点]

### 负面观点
[列出主要负面观点]

### 关键洞察
[总结发现]
""",

    "topic": """分析以下 Reddit 帖子和评论的主题分布。

请识别：
1. 主要讨论主题及其热度
2. 主题之间的关联性
3. 新兴/热门话题
4. 被忽视但重要的话题

输出格式：
## 主题分析报告

### 热门主题
1. [主题1] - 出现频率 X%
2. [主题2] - 出现频率 X%
...

### 主题关联
[描述主题之间的关系]

### 新兴话题
[列出新出现的讨论热点]

### 关键洞察
[总结发现]
""",

    "summary": """总结以下 Reddit 帖子和评论的核心内容。

请提供：
1. 主要讨论内容概述
2. 关键观点和论据
3. 重要数据和案例
4. 社区共识和分歧点

输出格式：
## 内容摘要报告

### 核心主题
[一句话概述]

### 关键观点
1. [观点1]
2. [观点2]
...

### 重要发现
[列出重要的数据、案例或见解]

### 社区态度
[描述社区的整体态度和主要分歧]
""",

    "competitive": """分析以下 Reddit 帖子和评论中提及的产品/公司/解决方案。

请识别：
1. 提及的产品/公司列表
2. 每个产品的评价（优点/缺点）
3. 用户推荐度和使用体验
4. 竞品对比和选择建议

输出格式：
## 竞品分析报告

### 提及的产品/解决方案
| 产品名称 | 提及次数 | 整体评价 |
|---------|---------|---------|
| ... | ... | ... |

### 详细分析
#### [产品1]
- 优点: ...
- 缺点: ...
- 用户评价: ...

### 用户推荐
[列出被推荐最多的选项]

### 市场洞察
[总结市场趋势和机会]
""",

    "pain_points": """分析以下 Reddit 帖子和评论中反映的用户痛点和需求。

请识别：
1. 主要痛点和问题
2. 用户的核心需求
3. 现有解决方案的不足
4. 潜在的产品机会

输出格式：
## 痛点分析报告

### 核心痛点
1. **[痛点1]**
   - 描述: ...
   - 影响程度: 高/中/低
   - 提及频率: X次

2. **[痛点2]**
   ...

### 用户需求
[列出用户表达的核心需求]

### 现有方案不足
[描述现有解决方案的问题]

### 产品机会
[基于痛点分析提出的机会点]
""",
}


def call_anthropic_api(prompt: str, content: str, model: str) -> str:
    """调用 Anthropic Claude API 进行分析"""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("错误: 请设置 ANTHROPIC_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    # 模型映射
    model_map = {
        "opus": "claude-opus-4-5-20251101",
        "opus-4.5": "claude-opus-4-5-20251101",
        "sonnet": "claude-sonnet-4-20250514",
        "haiku": "claude-3-haiku-20240307",
    }
    model_id = model_map.get(model, model)

    client = Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model=model_id,
            max_tokens=4000,
            system="你是一个专业的数据分析师，擅长分析社交媒体数据并生成结构化报告。请使用中文回复。",
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\n---\n\n待分析数据:\n{content}",
                }
            ],
        )
        return message.content[0].text
    except Exception as e:
        print(f"API 调用失败: {e}", file=sys.stderr)
        sys.exit(1)


def prepare_content_for_analysis(data: dict) -> str:
    """准备用于分析的内容"""
    lines = []

    # 处理搜索结果格式
    if "results" in data:
        for item in data["results"][:50]:  # 限制数量避免 token 超限
            lines.append(f"### {item.get('title', 'No Title')}")
            lines.append(f"- Subreddit: r/{item.get('subreddit', 'unknown')}")
            lines.append(f"- Score: {item.get('score', 0)}, Comments: {item.get('num_comments', 0)}")
            if item.get("selftext"):
                lines.append(f"- Content: {item['selftext'][:500]}...")
            lines.append("")

    # 处理帖子格式
    if "posts" in data:
        for post in data["posts"][:30]:
            lines.append(f"### {post.get('title', 'No Title')}")
            lines.append(f"- Score: {post.get('score', 0)}, Comments: {post.get('num_comments', 0)}")
            if post.get("selftext"):
                lines.append(f"- Content: {post['selftext'][:500]}...")

            # 处理评论
            if "comments" in post:
                lines.append("- Top Comments:")
                for comment in post["comments"][:5]:
                    lines.append(f"  - [{comment.get('score', 0)} votes] {comment.get('body', '')[:200]}...")
            lines.append("")

    return "\n".join(lines)


def analyze_reddit(
    input_file: str,
    analysis_type: str,
    model: str = "opus",
    output_format: str = "markdown",
) -> dict:
    """
    分析 Reddit 数据

    Args:
        input_file: 输入数据文件路径
        analysis_type: 分析类型
        model: AI 模型
        output_format: 输出格式

    Returns:
        分析结果
    """
    # 读取输入文件
    input_path = Path(input_file)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_file}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 获取分析提示词
    prompt = ANALYSIS_PROMPTS.get(analysis_type)
    if not prompt:
        print(f"错误: 不支持的分析类型: {analysis_type}", file=sys.stderr)
        sys.exit(1)

    # 准备内容
    content = prepare_content_for_analysis(data)
    if not content.strip():
        print("错误: 输入数据为空或格式不正确", file=sys.stderr)
        sys.exit(1)

    # 调用 AI 分析
    print(f"正在使用 {model} 进行 {analysis_type} 分析...", file=sys.stderr)
    analysis_result = call_anthropic_api(prompt, content, model)

    # 构建结果
    result = {
        "analysis_type": analysis_type,
        "model": model,
        "timestamp": datetime.utcnow().isoformat(),
        "source_file": input_file,
        "source_summary": {
            "total_items": data.get("total_results", data.get("total_posts", 0)),
            "query": data.get("query"),
            "subreddit": data.get("subreddit", {}).get("name") if isinstance(data.get("subreddit"), dict) else data.get("subreddit"),
        },
    }

    if output_format == "markdown":
        result["report"] = analysis_result
    else:
        result["report_text"] = analysis_result

    return result


def main():
    parser = argparse.ArgumentParser(
        description="分析 Reddit 数据并生成报告",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
分析类型说明:
  sentiment     - 情感分析，识别正面/负面/中性观点
  topic         - 主题聚类，识别讨论热点
  summary       - 内容摘要，提取关键信息
  competitive   - 竞品分析，识别提及的竞品及评价
  pain_points   - 痛点分析，识别用户抱怨和需求

示例:
  # 情感分析
  python analyze_reddit.py --input data/search.json --analysis_type sentiment

  # 生成 Markdown 报告
  python analyze_reddit.py --input data/posts.json --analysis_type pain_points --output reports/analysis.md
        """,
    )

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入数据文件（JSON 格式）",
    )
    parser.add_argument(
        "--analysis_type", "-a",
        required=True,
        choices=["sentiment", "topic", "summary", "competitive", "pain_points"],
        help="分析类型",
    )
    parser.add_argument(
        "--model", "-m",
        default="opus",
        help="AI 模型（默认 opus，可选 opus-4.5, sonnet, haiku 或完整模型 ID）",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出报告路径",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown"],
        default="markdown",
        help="输出格式（默认 markdown）",
    )

    args = parser.parse_args()

    # 执行分析
    result = analyze_reddit(
        input_file=args.input,
        analysis_type=args.analysis_type,
        model=args.model,
        output_format=args.format,
    )

    # 输出结果
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if args.format == "markdown":
            # Markdown 格式直接输出报告内容
            content = f"""# Reddit 调研报告

**分析类型**: {result['analysis_type']}
**分析时间**: {result['timestamp']}
**数据来源**: {result['source_file']}
**数据量**: {result['source_summary']['total_items']} 条

---

{result['report']}
"""
            output_path.write_text(content, encoding="utf-8")
        else:
            output_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        print(f"报告已保存到: {args.output}", file=sys.stderr)
    else:
        if args.format == "markdown":
            print(result["report"])
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
