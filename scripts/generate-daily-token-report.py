#!/usr/bin/env python3
"""
CFO Daily Token Consumption Report Generator

用途：自动生成每日 Claude Code 和 CodeX 的 Token 消耗报告
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Token 定价表（USD per 1M tokens）
PRICING = {
    "claude_code": {
        "sonnet_4_5": {"input": 3.0, "output": 15.0},
        "opus_4_5": {"input": 15.0, "output": 75.0},
        "haiku": {"input": 0.25, "output": 1.25},
    },
    "codex": {
        "cursor_pro": {"monthly": 20.0},
        "github_copilot": {"monthly": 10.0},
        "openai_api": {"gpt4_input": 30.0, "gpt4_output": 60.0},
    }
}

def calculate_cost(tokens_input: int, tokens_output: int, model_pricing: Dict[str, float]) -> float:
    """计算 token 成本"""
    cost_input = (tokens_input / 1_000_000) * model_pricing["input"]
    cost_output = (tokens_output / 1_000_000) * model_pricing["output"]
    return round(cost_input + cost_output, 4)

def parse_claude_code_logs(log_file: Path) -> Dict[str, Any]:
    """
    解析 Claude Code 日志文件

    格式示例：
    Token usage: 71727/200000; 128273 remaining
    """
    # TODO: 实现日志解析逻辑
    # 这里返回示例数据
    return {
        "sonnet_4_5": {
            "input_tokens": 71727,
            "output_tokens": 15000,
            "sessions": 3
        },
        "haiku": {
            "input_tokens": 5000,
            "output_tokens": 1000,
            "sessions": 2
        }
    }

def parse_codex_usage(service: str = "cursor_pro") -> Dict[str, Any]:
    """
    解析 CodeX 使用数据

    TODO: 实现 Cursor API 或本地配置文件解析
    """
    return {
        "service": service,
        "fast_requests_used": 45,
        "slow_requests_used": 120,
        "monthly_cost_usd": PRICING["codex"][service]["monthly"]
    }

def generate_daily_report(date: str, output_dir: Path, notes: str = "") -> Path:
    """
    生成每日 Token 消耗报告

    Args:
        date: YYYY-MM-DD 格式的日期
        output_dir: 报告输出目录
        notes: 当日主要工作内容备注

    Returns:
        生成的报告文件路径
    """
    # 解析 Claude Code 消耗
    claude_data = parse_claude_code_logs(Path("~/.claude/logs"))

    # 计算 Claude Code 成本
    claude_cost = {}
    claude_total = 0
    for model, data in claude_data.items():
        cost = calculate_cost(
            data["input_tokens"],
            data["output_tokens"],
            PRICING["claude_code"][model]
        )
        claude_cost[model] = {**data, "cost_usd": cost}
        claude_total += cost

    # 解析 CodeX 消耗
    codex_data = parse_codex_usage()
    codex_daily_cost = codex_data["monthly_cost_usd"] / 30

    # 总成本
    total_cost = claude_total + codex_daily_cost

    # 生成数据结构
    report_data = {
        "date": date,
        "claude_code": {
            **claude_cost,
            "total_cost_usd": round(claude_total, 2)
        },
        "codex": {
            **codex_data,
            "daily_amortized_cost_usd": round(codex_daily_cost, 2)
        },
        "total_daily_cost_usd": round(total_cost, 2),
        "notes": notes
    }

    # 保存 JSON
    json_file = output_dir / "token-logs" / f"{date[:7]}.json"
    json_file.parent.mkdir(parents=True, exist_ok=True)

    # 读取或创建月度日志文件
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            monthly_data = json.load(f)
    else:
        monthly_data = {}

    monthly_data[date] = report_data

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(monthly_data, f, indent=2, ensure_ascii=False)

    # 生成 Markdown 报告
    md_file = output_dir / "reports" / "daily" / f"{date}.md"
    md_file.parent.mkdir(parents=True, exist_ok=True)

    markdown = generate_markdown_report(report_data)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✅ 报告已生成:")
    print(f"   JSON: {json_file}")
    print(f"   Markdown: {md_file}")
    print(f"   今日总成本: ${total_cost:.2f}")

    return md_file

def generate_markdown_report(data: Dict[str, Any]) -> str:
    """生成 Markdown 格式的报告"""

    # Claude Code 表格
    claude_rows = []
    for model in ["sonnet_4_5", "opus_4_5", "haiku"]:
        if model in data["claude_code"]:
            d = data["claude_code"][model]
            model_name = model.replace("_", " ").title()
            claude_rows.append(
                f"| {model_name} | {d['input_tokens']:,} | {d['output_tokens']:,} | "
                f"{d['sessions']} | ${d['cost_usd']:.2f} |"
            )

    # 总计行
    total_input = sum(
        data["claude_code"][m]["input_tokens"]
        for m in data["claude_code"] if m != "total_cost_usd"
    )
    total_output = sum(
        data["claude_code"][m]["output_tokens"]
        for m in data["claude_code"] if m != "total_cost_usd"
    )
    total_sessions = sum(
        data["claude_code"][m]["sessions"]
        for m in data["claude_code"] if m != "total_cost_usd"
    )

    claude_rows.append(
        f"| **合计** | **{total_input:,}** | **{total_output:,}** | "
        f"**{total_sessions}** | **${data['claude_code']['total_cost_usd']:.2f}** |"
    )

    claude_table = "\n".join(claude_rows)

    # CodeX 信息
    codex = data["codex"]

    markdown = f"""# Daily AI Token Consumption Report

**日期**: {data['date']}

---

## 1. Claude Code 消耗

| 模型 | 输入Token | 输出Token | 会话数 | 成本(USD) |
|------|----------|----------|--------|----------|
{claude_table}

---

## 2. CodeX 消耗

| 服务 | 快速请求 | 慢速请求 | 月费 | 日均成本(USD) |
|------|---------|---------|------|--------------|
| {codex['service'].replace('_', ' ').title()} | {codex.get('fast_requests_used', 'N/A')}/500 | {codex.get('slow_requests_used', 'N/A')} | ${codex['monthly_cost_usd']:.2f} | ${codex['daily_amortized_cost_usd']:.2f} |

---

## 3. 总计

- **今日总成本**: ${data['total_daily_cost_usd']:.2f}
- **本月累计**: *(需要从月度日志计算)*
- **预计月成本**: ${data['total_daily_cost_usd'] * 30:.2f}

---

## 4. 主要工作内容

{data['notes'] if data['notes'] else "*(未填写)*"}

---

## 5. 成本分析

### 效率指标
- Token 单价（加权平均）: ${(data['claude_code']['total_cost_usd'] / (total_input + total_output) * 1_000_000):.4f} / 1M tokens
- 会话平均成本: ${(data['total_daily_cost_usd'] / total_sessions):.2f} / session

### 成本状态
"""

    # 成本预警
    daily_cost = data['total_daily_cost_usd']
    if daily_cost < 3:
        markdown += "🟢 **正常范围** - 日成本在预算内\n"
    elif daily_cost < 10:
        markdown += "🟡 **需要关注** - 日成本偏高，建议检查使用模式\n"
    else:
        markdown += "🔴 **超预算** - 日成本超标，需要立即优化策略\n"

    markdown += f"""
### 优化建议
1. 简单任务优先使用 Haiku（成本降低 90%）
2. 减少不必要的上下文长度
3. 批量处理相似任务

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return markdown

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="生成每日 Token 消耗报告")
    parser.add_argument(
        "--date",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="日期 (YYYY-MM-DD)，默认为今天"
    )
    parser.add_argument(
        "--output-dir",
        default="docs/finance",
        help="报告输出目录"
    )
    parser.add_argument(
        "--notes",
        default="",
        help="当日主要工作内容备注"
    )

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    generate_daily_report(args.date, output_dir, args.notes)

if __name__ == "__main__":
    main()
