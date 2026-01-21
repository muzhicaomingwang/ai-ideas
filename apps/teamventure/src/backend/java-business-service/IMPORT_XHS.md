# 小红书导入（XHS Import）

## API

- `POST /api/v1/import/xiaohongshu/resolve-note-id`
  - 入参: `{ "link": "<小红书客户端分享文本/链接>" }`
  - 出参: `{ "note_id": "...", "resolved_url": "..." }`
- `POST /api/v1/import/xiaohongshu/parse`
  - 入参: `{ "link": "<小红书客户端分享文本/链接>" }`
  - 出参: `ParseResponse`，包含 `note_id` 及 `images`（已上传 OSS 的图片 URL 列表）

## RapidAPI 配置

需要设置以下环境变量（对应 `application.yml` 的 `teamventure.import.xhs.rapidapi.*`）：

- `TEAMVENTURE_IMPORT_XHS_RAPIDAPI_BASE_URL`
- `TEAMVENTURE_IMPORT_XHS_RAPIDAPI_HOST`
- `TEAMVENTURE_IMPORT_XHS_RAPIDAPI_KEY`
