"""
LLM (OpenAI) Prometheus Metrics

Exposes:
- llm_requests_total: Counter of LLM API calls (labels: model, status)
- llm_tokens_total: Counter of tokens used (labels: model, type=input|output)
- llm_request_duration_seconds: Histogram of request latency
- llm_estimated_cost_usd: Counter of estimated cost in USD

Usage:
    from src.utils.llm_metrics import record_llm_call

    record_llm_call(
        model="gpt-4",
        input_tokens=500,
        output_tokens=200,
        duration_seconds=1.5,
        status="success"
    )
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram

# ==================== Metrics Definition ====================

LLM_REQUESTS_TOTAL = Counter(
    "llm_requests_total",
    "Total number of LLM API requests",
    labelnames=["model", "status"],
)

LLM_TOKENS_TOTAL = Counter(
    "llm_tokens_total",
    "Total number of tokens used",
    labelnames=["model", "type"],  # type: input | output
)

LLM_REQUEST_DURATION_SECONDS = Histogram(
    "llm_request_duration_seconds",
    "LLM request latency in seconds",
    labelnames=["model"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0),
)

LLM_ESTIMATED_COST_USD = Counter(
    "llm_estimated_cost_usd",
    "Estimated cost in USD (approximate)",
    labelnames=["model"],
)


# ==================== Pricing (as of 2024-12, update as needed) ====================
# https://openai.com/pricing

PRICING_PER_1K_TOKENS: dict[str, dict[str, float]] = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    # fallback for unknown models
    "default": {"input": 0.01, "output": 0.03},
}


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate cost in USD based on token usage."""
    pricing = PRICING_PER_1K_TOKENS.get(model, PRICING_PER_1K_TOKENS["default"])
    input_cost = (input_tokens / 1000.0) * pricing["input"]
    output_cost = (output_tokens / 1000.0) * pricing["output"]
    return input_cost + output_cost


# ==================== Recording Function ====================


def record_llm_call(
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
    duration_seconds: float,
    status: str = "success",
) -> None:
    """
    Record LLM call metrics.

    Args:
        model: Model name (e.g., "gpt-4", "gpt-4o-mini")
        input_tokens: Number of input (prompt) tokens
        output_tokens: Number of output (completion) tokens
        duration_seconds: Request latency in seconds
        status: "success" or "error"
    """
    LLM_REQUESTS_TOTAL.labels(model=model, status=status).inc()
    LLM_TOKENS_TOTAL.labels(model=model, type="input").inc(input_tokens)
    LLM_TOKENS_TOTAL.labels(model=model, type="output").inc(output_tokens)
    LLM_REQUEST_DURATION_SECONDS.labels(model=model).observe(duration_seconds)

    if status == "success":
        cost = _estimate_cost(model, input_tokens, output_tokens)
        LLM_ESTIMATED_COST_USD.labels(model=model).inc(cost)


def init_metrics(default_model: str = "gpt-4") -> None:
    """
    Initialize metrics with zero values so they appear in /metrics output.
    Call this at application startup.
    """
    # Initialize with zero values - these will show up in Prometheus
    LLM_REQUESTS_TOTAL.labels(model=default_model, status="success")
    LLM_REQUESTS_TOTAL.labels(model=default_model, status="error")
    LLM_TOKENS_TOTAL.labels(model=default_model, type="input")
    LLM_TOKENS_TOTAL.labels(model=default_model, type="output")
    LLM_REQUEST_DURATION_SECONDS.labels(model=default_model)
    LLM_ESTIMATED_COST_USD.labels(model=default_model)
