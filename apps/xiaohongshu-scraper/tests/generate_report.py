"""
生成 1000 个测试案例的 Markdown 报告
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from test_url_parser import generate_test_cases, run_accuracy_test
from utils.parser import XHSUrlParser


def generate_markdown_report(test_cases: list[dict], results: dict) -> str:
    """生成 Markdown 格式的测试报告"""

    lines = []

    # 标题
    lines.append("# 小红书 URL 解析器测试报告")
    lines.append("")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(">")
    lines.append(f"> 测试样本: {results['total']} 个")
    lines.append(">")
    lines.append(f"> 准确率: **{results['accuracy']:.2f}%**")
    lines.append("")

    # 目录
    lines.append("## 目录")
    lines.append("")
    lines.append("- [测试概要](#测试概要)")
    lines.append("- [分类统计](#分类统计)")
    lines.append("- [测试案例明细](#测试案例明细)")
    lines.append("  - [explore 类型](#explore-类型)")
    lines.append("  - [explore_with_params 类型](#explore_with_params-类型)")
    lines.append("  - [discovery 类型](#discovery-类型)")
    lines.append("  - [xhslink 类型](#xhslink-类型)")
    lines.append("  - [xhslink_a 类型](#xhslink_a-类型)")
    lines.append("  - [invalid_domain 类型](#invalid_domain-类型)")
    lines.append("  - [invalid_format 类型](#invalid_format-类型)")
    lines.append("  - [empty 类型](#empty-类型)")
    lines.append("  - [malformed 类型](#malformed-类型)")
    lines.append("")

    # 测试概要
    lines.append("## 测试概要")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总测试数 | {results['total']} |")
    lines.append(f"| 正确数 | {results['correct']} |")
    lines.append(f"| 错误数 | {results['incorrect']} |")
    lines.append(f"| 准确率 | {results['accuracy']:.2f}% |")
    lines.append("")

    # 分类统计
    lines.append("## 分类统计")
    lines.append("")
    lines.append("| URL类型 | 总数 | 正确 | 错误 | 准确率 |")
    lines.append("|---------|------|------|------|--------|")

    for url_type in ["explore", "explore_with_params", "discovery", "xhslink", "xhslink_a",
                     "invalid_domain", "invalid_format", "empty", "malformed"]:
        if url_type in results["by_type"]:
            stats = results["by_type"][url_type]
            lines.append(f"| {url_type} | {stats['total']} | {stats['correct']} | {stats['incorrect']} | {stats['accuracy']:.1f}% |")

    lines.append("")

    # 测试案例明细
    lines.append("## 测试案例明细")
    lines.append("")

    # 按类型分组
    cases_by_type = {}
    for case in test_cases:
        url_type = case["url_type"]
        if url_type not in cases_by_type:
            cases_by_type[url_type] = []
        cases_by_type[url_type].append(case)

    # 类型说明
    type_descriptions = {
        "explore": "标准 explore 页面格式，最常见的小红书笔记链接",
        "explore_with_params": "带查询参数的 explore 链接，如 xsec_token、source 等",
        "discovery": "旧版 discovery/item 格式链接",
        "xhslink": "小红书短链接格式",
        "xhslink_a": "App 分享的短链接格式（/a/ 路径）",
        "invalid_domain": "无效域名测试（负面测试）",
        "invalid_format": "无效格式测试（负面测试）",
        "empty": "空值/null 测试（边界测试）",
        "malformed": "畸形 URL 测试（边界测试）",
    }

    for url_type in ["explore", "explore_with_params", "discovery", "xhslink", "xhslink_a",
                     "invalid_domain", "invalid_format", "empty", "malformed"]:
        if url_type not in cases_by_type:
            continue

        cases = cases_by_type[url_type]

        lines.append(f"### {url_type} 类型")
        lines.append("")
        lines.append(f"> {type_descriptions.get(url_type, '')}")
        lines.append(">")
        lines.append(f"> 共 {len(cases)} 个测试案例")
        lines.append("")

        lines.append("| # | URL | 期望ID | 实际ID | 结果 |")
        lines.append("|---|-----|--------|--------|------|")

        for i, case in enumerate(cases, 1):
            url = case["url"] or "(空)"
            expected = case["expected_id"] or "None"

            # 执行解析获取实际结果
            actual = XHSUrlParser.extract_note_id(case["url"])
            actual_str = actual or "None"

            # 判断结果
            if case["should_parse"]:
                is_correct = actual == case["expected_id"]
            else:
                is_correct = actual is None

            result = "✓" if is_correct else "✗"

            # 截断过长的 URL
            url_display = url[:60] + "..." if len(url) > 60 else url
            expected_display = expected[:24] + "..." if len(expected) > 24 else expected
            actual_display = actual_str[:24] + "..." if len(actual_str) > 24 else actual_str

            # 转义 Markdown 特殊字符
            url_display = url_display.replace("|", "\\|")

            lines.append(f"| {i} | `{url_display}` | `{expected_display}` | `{actual_display}` | {result} |")

        lines.append("")

    # 附录
    lines.append("## 附录")
    lines.append("")
    lines.append("### 支持的 URL 模式")
    lines.append("")
    lines.append("```python")
    lines.append("PATTERNS = [")
    lines.append('    r"xiaohongshu\\.com/explore/([a-zA-Z0-9]+)",')
    lines.append('    r"xiaohongshu\\.com/discovery/item/([a-zA-Z0-9]+)",')
    lines.append('    r"xhslink\\.com/a/([a-zA-Z0-9]+)",')
    lines.append('    r"xhslink\\.com/([a-zA-Z0-9]+)",')
    lines.append("]")
    lines.append("```")
    lines.append("")
    lines.append("### 测试环境")
    lines.append("")
    lines.append("- Python 3.11+")
    lines.append("- 测试框架: 自定义测试脚本")
    lines.append(f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    return "\n".join(lines)


def main():
    print("正在生成 1000 个测试案例...")
    test_cases = generate_test_cases(1000)

    print("正在执行解析测试...")
    results = run_accuracy_test(test_cases)

    print("正在生成 Markdown 报告...")
    report = generate_markdown_report(test_cases, results)

    # 保存报告
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"url_parser_report_{timestamp}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n报告已生成: {report_file}")
    print(f"准确率: {results['accuracy']:.2f}%")

    return str(report_file)


if __name__ == "__main__":
    main()
