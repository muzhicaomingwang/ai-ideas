# Apps Gateway - 统一 Nginx 服务

统一的 API 网关，服务于所有 apps 目录下的应用。

## 服务路由

| 路由前缀 | 目标服务 | 说明 |
|---------|---------|------|
| `/api/v1/` | TeamVenture Java | 业务 API |
| `/ai/` | TeamVenture Python | AI 服务 |
| `/xhs/` | XHS Scraper | 小红书抓取服务 |
| `/oss/` | MinIO | 对象存储 |
| `/minio/` | MinIO Console | 存储管理界面 |

## 启动顺序

**必须先启动 Nginx 创建共享网络**：

```bash
# 1. 首先启动 Nginx（创建共享网络）
cd apps/nginx
docker compose up -d

# 2. 然后启动各应用服务
cd ../teamventure/src
docker compose up -d

cd ../../xiaohongshu-scraper
docker compose up -d
```

## 端口清单

| 服务 | 端口 | 说明 |
|-----|------|------|
| Nginx HTTP | 80 | API 网关 |
| Nginx HTTPS | 443 | API 网关(SSL) |
| Nginx Exporter | 9113 | Prometheus 指标 |

## API 访问示例

```bash
# TeamVenture API
curl http://localhost/api/v1/health

# XHS Scraper API
curl http://localhost/xhs/health

# 抓取小红书内容
curl -X POST http://localhost/xhs/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.xiaohongshu.com/explore/xxx"}'
```

## SSL 证书

将证书文件放在 `ssl/` 目录：
- `ssl/cert.pem` - 证书文件
- `ssl/key.pem` - 私钥文件

开发环境可生成自签名证书：
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/CN=localhost"
```

## 网络架构

```
┌─────────────────────────────────────────────────────┐
│                 apps-shared-network                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────┐    ┌─────────────────────────────┐   │
│  │  Nginx   │───▶│ TeamVenture                 │   │
│  │  :80     │    │ ├─ java-business-service    │   │
│  │  :443    │    │ ├─ python-ai-service        │   │
│  └──────────┘    │ ├─ mysql, redis, rabbitmq   │   │
│       │          │ └─ minio, prometheus...      │   │
│       │          └─────────────────────────────┘   │
│       │                                             │
│       │          ┌─────────────────────────────┐   │
│       └─────────▶│ XHS Scraper                 │   │
│                  │ └─ xhs-scraper-service      │   │
│                  └─────────────────────────────┘   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## 添加新服务

1. 在新服务的 `docker-compose.yml` 中添加：
   ```yaml
   networks:
     apps-shared-network:
       external: true
   ```

2. 在 `nginx.conf` 中添加 upstream 和 location 配置

3. 重启 Nginx：
   ```bash
   docker compose restart nginx
   ```
