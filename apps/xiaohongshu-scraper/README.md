# 小红书内容抓取服务

> 输入小红书链接，输出完整内容（图片/视频/文本/评论）

## 项目状态

✅ **v0.1.0** - 核心功能已实现

## 功能特性

| 内容类型 | 支持状态 | 说明 |
|---------|---------|------|
| 图片 | ✅ 已实现 | 自动下载所有图片 |
| 视频 | ✅ 已实现 | 自动下载视频文件 |
| 文本 | ✅ 已实现 | 标题、正文、标签 |
| 评论 | ✅ 已实现 | 评论内容、用户名、点赞数 |
| 作者信息 | ✅ 已实现 | 昵称、头像、ID |
| 统计数据 | ✅ 已实现 | 点赞数、收藏数、评论数 |

## 技术栈

- **后端框架**: Python 3.11 + FastAPI
- **浏览器自动化**: Playwright (Chromium)
- **数据模型**: Pydantic v2
- **HTTP客户端**: HTTPX (异步)
- **容器化**: Docker + Docker Compose

## 快速开始

### 方式一：Docker 部署（推荐）

```bash
cd apps/xiaohongshu-scraper

# 构建并启动服务
docker compose up -d

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

### 方式二：本地开发

```bash
cd apps/xiaohongshu-scraper

# 安装依赖（需要 Poetry）
poetry install

# 安装 Playwright 浏览器
poetry run playwright install chromium

# 启动服务
poetry run python -m src.main

# 或使用 uvicorn
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8100
```

## API 接口

服务启动后访问: http://localhost:8100/docs 查看完整 API 文档

### 健康检查

```bash
curl http://localhost:8100/health
```

### 抓取笔记

```bash
curl -X POST http://localhost:8100/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.xiaohongshu.com/explore/xxxxxx",
    "download_media": true,
    "fetch_comments": true,
    "comment_limit": 50
  }'
```

### 解析 URL

```bash
curl -X POST "http://localhost:8100/parse?url=https://www.xiaohongshu.com/explore/xxx"
```

### 检查登录状态

```bash
curl http://localhost:8100/login/status
```

## 输出示例

抓取结果保存在 `output/{note_id}/` 目录下：

```
output/
└── 6479d647xxxx/
    ├── note.json       # 笔记元数据
    ├── images/         # 图片文件
    │   ├── image_1.jpg
    │   └── image_2.jpg
    └── video/          # 视频文件
        └── video.mp4
```

JSON 结构：

```json
{
  "note_id": "6479d647...",
  "url": "https://www.xiaohongshu.com/explore/xxx",
  "type": "image",
  "title": "笔记标题",
  "content": "正文内容 #标签1 #标签2",
  "tags": ["标签1", "标签2"],
  "author": {
    "id": "user_xxx",
    "name": "作者昵称",
    "avatar": "https://..."
  },
  "stats": {
    "likes": 1234,
    "collects": 567,
    "comments": 89,
    "shares": 12
  },
  "images": [
    {
      "url": "https://...",
      "local_path": "output/xxx/images/image_1.jpg"
    }
  ],
  "comments": [
    {
      "id": "comment_1",
      "user_name": "用户名",
      "content": "评论内容",
      "likes": 100
    }
  ],
  "crawled_at": "2024-01-15T10:30:00"
}
```

## 目录结构

```
xiaohongshu-scraper/
├── README.md               # 项目说明
├── pyproject.toml          # Poetry 依赖配置
├── Dockerfile              # 容器镜像
├── docker-compose.yml      # 容器编排
├── docs/
│   └── research-report.md  # 技术调研报告
├── src/
│   ├── main.py             # FastAPI 入口
│   ├── core/
│   │   ├── browser.py      # 浏览器管理器
│   │   └── scraper.py      # 核心抓取逻辑
│   ├── models/
│   │   └── schemas.py      # Pydantic 数据模型
│   └── utils/
│       └── parser.py       # URL 解析工具
├── data/                   # Cookie 存储
└── output/                 # 抓取输出
```

## 登录说明

小红书部分内容需要登录才能访问。本服务支持：

### Cookie 登录（推荐）

1. 在浏览器登录小红书
2. 使用浏览器开发者工具导出 Cookie
3. 保存为 `data/cookies.json`
4. 重启服务自动加载

Cookie 格式：

```json
[
  {
    "name": "web_session",
    "value": "xxx",
    "domain": ".xiaohongshu.com",
    "path": "/"
  }
]
```

### 二维码登录

需要以非 headless 模式启动：

```bash
# 本地开发
HEADLESS=false poetry run python -m src.main

# Docker 方式
HEADLESS=false docker compose up -d
```

## 支持的 URL 格式

- `https://www.xiaohongshu.com/explore/xxxxx`
- `https://www.xiaohongshu.com/discovery/item/xxxxx`
- `https://xhslink.com/xxxxx`
- `http://xhslink.com/a/xxxxx`

## 环境变量

| 变量名 | 默认值 | 说明 |
|-------|-------|------|
| HOST | 0.0.0.0 | 监听地址 |
| PORT | 8100 | 监听端口 |
| HEADLESS | true | 是否无头模式 |

## 风险提示

**本项目仅供学习研究使用**

- 遵守小红书用户协议
- 不用于商业用途
- 控制请求频率，避免对平台造成压力
- 尊重内容创作者版权
- 抓取的内容仅供个人学习，禁止二次传播

## 已知限制

1. **登录墙**: 部分笔记需要登录才能访问
2. **反爬机制**: 频繁请求可能触发验证码
3. **动态加载**: 评论采用懒加载，抓取数量有限
4. **签名验证**: 小红书 API 有签名校验，本服务使用浏览器渲染绕过

## 参考项目

- [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) - 30K+ Star
- [XHS-Downloader](https://github.com/JoeanAmier/XHS-Downloader) - 10K+ Star

## 版本历史

- **v0.1.0** (2024-01) - 初始版本，实现核心抓取功能
