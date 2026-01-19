from __future__ import annotations

from src.services.markdown_optimizer import MarkdownOptimizer


def test_optimizer_guardrail_detects_dropped_pois():
    original = """
# 团建行程方案

## 参考行程

### Day 1
- A
- B

### Day 2
- C
- D
"""
    optimized_bad = """
# 团建行程方案

## 参考行程

### Day 1
- A

### Day 2
- C
"""
    assert MarkdownOptimizer._drops_user_pois(original, optimized_bad) is True

    optimized_ok = """
# 团建行程方案

## 参考行程

### Day 1
- A
- B

### Day 2
- C
- D
"""
    assert MarkdownOptimizer._drops_user_pois(original, optimized_ok) is False

