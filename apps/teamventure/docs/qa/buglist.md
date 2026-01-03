# TeamVenture QA Bug List（缺陷清单）

使用方式：
- 每个缺陷一行；必要时在“补充信息”附上请求/响应、截图、日志片段（脱敏）。
- `Severity` 表示影响程度（用户影响/数据风险），`Priority` 表示修复优先级（排期）。
- 推荐给每条缺陷分配唯一 ID（如 `BUG-YYYYMMDD-001`）。

---

## 字段定义（建议）

- `Env`：`dev` / `staging` / `prod`
- `Module`：`auth` / `plans` / `suppliers` / `mq` / `ai-service` / `gateway` / `db` / `redis` / `other`
- `Severity`：`S0-blocker` / `S1-critical` / `S2-major` / `S3-minor` / `S4-trivial`
- `Priority`：`P0` / `P1` / `P2` / `P3`
- `Status`：`new` / `triaged` / `in_progress` / `fixed` / `verified` / `won't_fix` / `duplicate` / `blocked`

---

## Bug List

| ID | Date | Env | Module | Severity | Priority | Title | Steps To Reproduce | Expected | Actual | Evidence (logs/req/resp) | Owner | Status | Fix Version | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BUG- |  |  |  |  |  |  |  |  |  |  |  | new |  |  |

---

## 复现信息模板（复制到 Notes）

```text
API:
Request:
Response:

Auth:

Trace:
- plan_request_id:
- trace_id:

Logs:
- java:
- python:
- nginx:

DB check (optional):
```

