# zhimeng's Agent

基于 Obsidian 知识库的智能问答助手，可以像我一样回答问题。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      飞书机器人                              │
│                    (zhimeng's Agent)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ 用户提问
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Retriever  │→ │  Reranker   │→ │    LLM Generator    │ │
│  │  (检索器)    │  │  (重排序)    │  │  (Claude/GPT-4)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   ChromaDB 向量数据库                        │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Obsidian Vault 文档索引                  │  │
│  │  ~/Documents/Obsidian Vault/                         │  │
│  │  - AI-Engineering/                                   │  │
│  │  - Cognitive-Growth/                                 │  │
│  │  - Memory Engineering/                               │  │
│  │  - ...                                               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈

- **后端**: Python 3.11 + FastAPI
- **RAG 框架**: LangChain
- **向量数据库**: ChromaDB (本地持久化)
- **Embedding**: OpenAI text-embedding-3-small
- **LLM**: Claude 3.5 Sonnet / GPT-4
- **飞书集成**: 飞书开放平台 API

## 快速开始

### 1. 安装依赖

```bash
cd apps/zhimeng-agent
poetry install
```

### 2. 配置环境变量

```bash
cp config/.env.example config/.env
# 编辑 .env 填入 API 密钥
```

### 3. 建立索引

```bash
poetry run python src/indexer.py
```

### 4. 启动服务

```bash
poetry run uvicorn src.main:app --reload --port 8001
```

### 5. 测试问答

```bash
curl -X POST http://localhost:8001/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是 Memory Engineering?"}'
```

## 目录结构

```
zhimeng-agent/
├── README.md
├── pyproject.toml
├── config/
│   ├── .env.example
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── main.py           # FastAPI 入口
│   ├── indexer.py        # 文档索引器
│   ├── retriever.py      # 检索器
│   ├── llm_client.py     # LLM 客户端
│   └── feishu_bot.py     # 飞书机器人集成
├── tests/
│   └── test_retriever.py
└── docs/
    └── architecture.md
```

## API 接口

### POST /ask

问答接口

**请求**:
```json
{
  "question": "什么是认知负荷?",
  "top_k": 5,
  "include_sources": true
}
```

**响应**:
```json
{
  "answer": "认知负荷是指...",
  "sources": [
    {"file": "Cognitive-Growth/认知负荷理论.md", "score": 0.92},
    {"file": "AI-Engineering/Prompt设计.md", "score": 0.85}
  ],
  "tokens_used": 1234
}
```

### POST /index

重建索引

```json
{
  "paths": ["AI-Engineering", "Cognitive-Growth"],
  "force": false
}
```

### GET /health

健康检查

## 飞书机器人集成

机器人收到消息后，调用 `/ask` 接口，将回答发送给用户。

```python
# 消息处理流程
1. 用户 @机器人 提问
2. 飞书 Webhook 触发
3. 调用 /ask 接口
4. 返回回答 + 来源引用
```

## 配置说明

### 知识库路径

```python
OBSIDIAN_VAULT_PATH = "~/Documents/Obsidian Vault/"
```

### 索引配置

```python
INDEX_CONFIG = {
    "chunk_size": 1000,        # 分块大小
    "chunk_overlap": 200,      # 重叠大小
    "exclude_patterns": [      # 排除的文件/目录
        "_attachments",
        "_Inbox",
        "*.docx"
    ]
}
```

### LLM 配置

```python
LLM_CONFIG = {
    "provider": "anthropic",   # anthropic / openai
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.3,
    "max_tokens": 2000
}
```

## 开发计划

- [x] 基础架构设计
- [ ] 文档索引器实现
- [ ] 检索器实现
- [ ] LLM 集成
- [ ] FastAPI 服务
- [ ] 飞书机器人集成
- [ ] 增量索引更新
- [ ] 对话记忆
