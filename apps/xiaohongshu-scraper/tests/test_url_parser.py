"""
小红书 URL 解析器准确率测试
生成 1000 个测试样例，验证解析准确率
"""
import random
import string
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.parser import XHSUrlParser


def generate_note_id(length: int = 24) -> str:
    """生成随机笔记 ID（模拟真实 ID 格式）"""
    # 小红书笔记 ID 通常是 24 位的十六进制字符串
    return ''.join(random.choices('0123456789abcdef', k=length))


def generate_short_id(length: int = 8) -> str:
    """生成短链接 ID"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_test_cases(count: int = 1000) -> list[dict]:
    """
    生成测试用例

    Returns:
        测试用例列表，每个包含 url, expected_id, url_type
    """
    test_cases = []

    # URL 类型分布（模拟真实场景）
    url_types = [
        # (类型, 权重, 生成函数)
        ("explore", 40),           # 最常见：explore 页面
        ("explore_with_params", 15),  # 带参数的 explore
        ("discovery", 10),         # discovery/item 格式
        ("xhslink", 15),           # 短链接
        ("xhslink_a", 10),         # App 分享短链接
        ("invalid_domain", 3),     # 无效域名（负面测试）
        ("invalid_format", 3),     # 无效格式（负面测试）
        ("empty", 2),              # 空/null（边界测试）
        ("malformed", 2),          # 畸形 URL（边界测试）
    ]

    # 计算权重总和
    total_weight = sum(w for _, w in url_types)

    # 按权重生成测试用例
    for url_type, weight in url_types:
        type_count = int(count * weight / total_weight)

        for _ in range(type_count):
            case = generate_single_case(url_type)
            test_cases.append(case)

    # 补足到指定数量
    while len(test_cases) < count:
        case = generate_single_case("explore")
        test_cases.append(case)

    # 打乱顺序
    random.shuffle(test_cases)

    return test_cases[:count]


def generate_single_case(url_type: str) -> dict:
    """生成单个测试用例"""

    if url_type == "explore":
        note_id = generate_note_id()
        url = f"https://www.xiaohongshu.com/explore/{note_id}"
        return {"url": url, "expected_id": note_id, "url_type": url_type, "should_parse": True}

    elif url_type == "explore_with_params":
        note_id = generate_note_id()
        params = random.choice([
            f"?xsec_token={generate_short_id(32)}",
            f"?source=webshare&xhsshare=pc",
            f"?app_platform=ios&app_version=8.0.0",
            f"?xsec_token={generate_short_id(32)}&source=pc",
            "",
        ])
        url = f"https://www.xiaohongshu.com/explore/{note_id}{params}"
        return {"url": url, "expected_id": note_id, "url_type": url_type, "should_parse": True}

    elif url_type == "discovery":
        note_id = generate_note_id()
        url = f"https://www.xiaohongshu.com/discovery/item/{note_id}"
        return {"url": url, "expected_id": note_id, "url_type": url_type, "should_parse": True}

    elif url_type == "xhslink":
        short_id = generate_short_id()
        url = f"https://xhslink.com/{short_id}"
        return {"url": url, "expected_id": short_id, "url_type": url_type, "should_parse": True}

    elif url_type == "xhslink_a":
        short_id = generate_short_id()
        url = f"http://xhslink.com/a/{short_id}"
        return {"url": url, "expected_id": short_id, "url_type": url_type, "should_parse": True}

    elif url_type == "invalid_domain":
        note_id = generate_note_id()
        # 确保域名不包含 xiaohongshu.com 或 xhslink.com 子串
        domain = random.choice([
            "xhs.cn",
            "redbook.com",
            "example.com",
            "google.com",
            "weibo.com",
            "douyin.com",
        ])
        url = f"https://{domain}/explore/{note_id}"
        return {"url": url, "expected_id": None, "url_type": url_type, "should_parse": False}

    elif url_type == "invalid_format":
        urls = [
            "https://www.xiaohongshu.com/",
            "https://www.xiaohongshu.com/user/profile/123",
            "https://www.xiaohongshu.com/search?keyword=test",
            "https://www.xiaohongshu.com/board/123",
            "not_a_url_at_all",
            "javascript:alert(1)",
        ]
        url = random.choice(urls)
        return {"url": url, "expected_id": None, "url_type": url_type, "should_parse": False}

    elif url_type == "empty":
        url = random.choice(["", None, "   ", "\n\t"])
        return {"url": url, "expected_id": None, "url_type": url_type, "should_parse": False}

    elif url_type == "malformed":
        urls = [
            "https://www.xiaohongshu.com/explore/",  # 缺少 ID
            "https://www.xiaohongshu.com/explore",   # 缺少 ID 和斜杠
            "xiaohongshu.com/explore/abc123",        # 缺少协议
            "//www.xiaohongshu.com/explore/abc123",  # 协议相对 URL
            "https://www.xiaohongshu.com/explore/abc123/extra/path",
        ]
        url = random.choice(urls)
        # 某些畸形 URL 仍然可以被解析
        note_id = XHSUrlParser.extract_note_id(url) if url else None
        return {"url": url, "expected_id": note_id, "url_type": url_type, "should_parse": note_id is not None}

    return {"url": "", "expected_id": None, "url_type": "unknown", "should_parse": False}


def run_accuracy_test(test_cases: list[dict]) -> dict:
    """
    运行准确率测试

    Returns:
        测试结果统计
    """
    results = {
        "total": len(test_cases),
        "correct": 0,
        "incorrect": 0,
        "by_type": {},
        "errors": [],
    }

    for case in test_cases:
        url = case["url"]
        expected_id = case["expected_id"]
        url_type = case["url_type"]
        should_parse = case["should_parse"]

        # 初始化类型统计
        if url_type not in results["by_type"]:
            results["by_type"][url_type] = {"total": 0, "correct": 0, "incorrect": 0}

        results["by_type"][url_type]["total"] += 1

        # 执行解析
        try:
            parsed_id = XHSUrlParser.extract_note_id(url)

            # 判断是否正确
            if should_parse:
                # 期望能解析出 ID
                is_correct = parsed_id == expected_id
            else:
                # 期望解析失败（返回 None）
                is_correct = parsed_id is None

            if is_correct:
                results["correct"] += 1
                results["by_type"][url_type]["correct"] += 1
            else:
                results["incorrect"] += 1
                results["by_type"][url_type]["incorrect"] += 1
                results["errors"].append({
                    "url": url,
                    "expected": expected_id,
                    "actual": parsed_id,
                    "type": url_type,
                })

        except Exception as e:
            results["incorrect"] += 1
            results["by_type"][url_type]["incorrect"] += 1
            results["errors"].append({
                "url": url,
                "expected": expected_id,
                "actual": f"Exception: {str(e)}",
                "type": url_type,
            })

    # 计算准确率
    results["accuracy"] = results["correct"] / results["total"] * 100 if results["total"] > 0 else 0

    # 计算各类型准确率
    for url_type, stats in results["by_type"].items():
        stats["accuracy"] = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0

    return results


def print_report(results: dict):
    """打印测试报告"""
    print("\n" + "=" * 60)
    print("小红书 URL 解析器准确率测试报告")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试样本: {results['total']} 个")
    print()

    print("【总体结果】")
    print(f"  ✓ 正确: {results['correct']}")
    print(f"  ✗ 错误: {results['incorrect']}")
    print(f"  准确率: {results['accuracy']:.2f}%")
    print()

    print("【分类统计】")
    print("-" * 60)
    print(f"{'URL类型':<25} {'总数':>8} {'正确':>8} {'错误':>8} {'准确率':>10}")
    print("-" * 60)

    for url_type, stats in sorted(results["by_type"].items()):
        print(f"{url_type:<25} {stats['total']:>8} {stats['correct']:>8} {stats['incorrect']:>8} {stats['accuracy']:>9.1f}%")

    print("-" * 60)
    print()

    # 显示错误样例（最多 10 个）
    if results["errors"]:
        print("【错误样例】（最多显示 10 个）")
        for i, error in enumerate(results["errors"][:10]):
            print(f"  {i+1}. URL: {error['url'][:60]}...")
            print(f"     期望: {error['expected']}")
            print(f"     实际: {error['actual']}")
            print()

    print("=" * 60)


def save_results(results: dict, test_cases: list[dict], output_dir: str = "./tests/results"):
    """保存测试结果到文件"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 保存统计结果
    stats_file = output_path / f"url_parser_stats_{timestamp}.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        # 移除 errors 中的过多数据
        save_results = {**results, "errors": results["errors"][:100]}
        json.dump(save_results, f, ensure_ascii=False, indent=2)

    # 保存测试用例
    cases_file = output_path / f"url_parser_cases_{timestamp}.json"
    with open(cases_file, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到:")
    print(f"  - {stats_file}")
    print(f"  - {cases_file}")


def main():
    """主函数"""
    print("正在生成 1000 个测试样例...")
    test_cases = generate_test_cases(1000)

    print(f"生成完成，共 {len(test_cases)} 个测试用例")
    print("正在执行解析测试...")

    results = run_accuracy_test(test_cases)

    print_report(results)
    save_results(results, test_cases)

    # 返回准确率是否达标（95% 以上）
    return results["accuracy"] >= 95.0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
