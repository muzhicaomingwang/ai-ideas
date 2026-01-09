# QA 可执行脚本（后端 API 全覆盖）

对应测试计划：`apps/teamVenture/docs/qa/backend-api-step-by-step-test-plan.md:1`

## 脚本

- 全覆盖回归（启动 + 健康检查 + 登录 + 生成轮询 + 列表/详情/确认/供应商/联系记录 + MQ 观测 + 失败日志）  
  `apps/teamVenture/docs/qa/scripts/run_backend_api_full_coverage.sh:1`
- 回填行程版本号（修复历史库 `plans.itinerary_version` 缺失/NULL 导致 CAS 永久冲突）  
  `apps/teamventure/docs/qa/scripts/backfill_itinerary_version.sh:1`
- 行程更新联调冒烟（仅走 Nginx 网关，不直连 Java）  
  `apps/teamventure/docs/qa/scripts/e2e_itinerary_update_test.sh:1`

## 使用方法

1) 先确保 `/etc/hosts` 有：
```text
127.0.0.1 api.teamVenture.com
```

2) 运行（默认使用 `apps/teamVenture/src/.env.local`）：
```bash
bash apps/teamVenture/docs/qa/scripts/run_backend_api_full_coverage.sh
```

3) 指定环境（推荐显式指定）：
```bash
bash apps/teamVenture/docs/qa/scripts/run_backend_api_full_coverage.sh --env-file apps/teamVenture/src/.env.dev
```

4) 只想直连 Java（不走网关）：
```bash
bash apps/teamVenture/docs/qa/scripts/run_backend_api_full_coverage.sh --base-url http://localhost:8080
```

## 备注

- 脚本默认不会打印 `.env.local` 里的敏感信息；bug 提交也请勿附带 `OPENAI_API_KEY`。
- 如果你们希望把这套脚本接到 CI，再加上 `newman`（可输出 JUnit/HTML 报告）更方便。
