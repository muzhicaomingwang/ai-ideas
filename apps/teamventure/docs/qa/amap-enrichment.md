# 高德地图信息补全（提升行程真实度）

当行程过于“模板化”时，可以在 AI 生成前增加目的地信息补全：从高德 WebService 拉取目的地的 POI（拓展基地/景点/餐饮等），把结构化结果注入 prompt，让模型尽量引用真实地点名称与区域。

## 开关与配置

该功能在 `python-ai-service` 中默认关闭；开启后生成链路会多一次到高德的 HTTP 请求（并做内存 TTL 缓存）。

在 `apps/teamventure/src/.env.local`（或你实际使用的 env 文件）中添加：

```env
# 高德地图 WebService（可选）
AMAP_ENABLED=true
AMAP_API_KEY=你的高德Key
# 可选
AMAP_TIMEOUT_SECONDS=5
AMAP_CACHE_TTL_SECONDS=3600
AMAP_MAX_POIS_PER_CATEGORY=6
```

然后重启：

```bash
docker compose --env-file apps/teamventure/src/.env.local -f apps/teamventure/src/docker-compose.yml up -d --no-deps python-ai-service
```

## 说明

- 高德 Key 需要开通 WebService API 权限。
- 若高德请求失败/超时，会自动降级为不补全（不影响整体生成）。

