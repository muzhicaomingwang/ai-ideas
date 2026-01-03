# TeamVenture 后端接口回归（Postman / Newman）

## 前置

- 确保已把域名映射到本机（用于和 Nginx `server_name` 一致）：
  - `/etc/hosts` 增加：`127.0.0.1 api.teamVenture.com`
- 确保服务已启动（Docker Compose）：
  - `docker compose -f apps/teamVenture/src/docker-compose.yml up -d`
- 如要走真实大模型生成：
  - `apps/teamVenture/src/.env.local` 中设置 `OPENAI_API_KEY`
  - compose 已通过 `env_file` 注入到 `java-business-service`/`python-ai-service`

## Postman（手工执行）

- 导入：
  - Collection：`apps/teamVenture/docs/qa/postman/teamventure.postman_collection.json`
  - Environment：`apps/teamVenture/docs/qa/postman/teamventure.postman_environment.json`
- 选择环境后，按顺序运行：
  - `Auth/Auth - WeChat Login`
  - `Plans/Plans - Generate (Async)`（会自动轮询到生成完成）
  - 再运行 Suppliers、Confirm、Contact 等接口

## Newman（一键回归）

要求：本机已安装 `newman`（例如：`npm i -g newman`）。

```bash
newman run apps/teamVenture/docs/qa/postman/teamventure.postman_collection.json \
  -e apps/teamVenture/docs/qa/postman/teamventure.postman_environment.json
```

