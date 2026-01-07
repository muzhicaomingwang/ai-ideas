# 主动式AI（Proactive AI / Agentic AI）调研报告

> 调研日期：2026年1月5日
> 调研人：九日增长顾问

---

## 一、核心结论

**2026年是Agentic AI大规模落地元年。** AI正从"被动响应"（你问我答）转向"主动执行"（预判需求、自主完成任务）。

### 关键数据

| 维度 | 数据 |
|------|------|
| 2024年全球AI Agent市场规模 | 52.9亿美元 |
| 2030年预测规模 | 471亿美元（CAGR ~44%） |
| Agentic AI领域融资（2年内） | 超20亿美元 |
| 企业采用率（使用AI） | 88% |
| 正在试验AI Agent的企业 | 62% |

---

## 二、从被动到主动：范式转变

### 2.1 传统AI vs 主动式AI

| 维度 | 传统AI（Reactive） | 主动式AI（Proactive） |
|------|-------------------|---------------------|
| 交互模式 | 你问，我答 | 预判需求，主动行动 |
| 任务范围 | 单次问答 | 端到端任务执行 |
| 人工干预 | 每步都需要 | 最小化干预 |
| 典型产品 | ChatGPT早期版本 | OpenAI Operator、Claude Agent |

### 2.2 主动式AI的四大特征

1. **预判行为（Anticipatory）** - 在事件发生前预测可能的行动和结果
2. **自主性（Autonomy）** - 最小人工输入，实时决策
3. **适应性（Adaptability）** - 从历史交互中学习，持续优化
4. **上下文感知（Context Awareness）** - 理解并处理环境信息

---

## 三、技术标准化进展

### 3.1 MCP（Model Context Protocol）—— "AI的USB-C"

Anthropic于2024年11月推出的开放标准，已成为**行业事实标准**。

**采用情况：**
- 2025年3月：OpenAI正式采用MCP
- 2025年5月：Microsoft Build大会宣布Windows 11支持MCP
- 已集成：ChatGPT、Cursor、Gemini、VS Code、Replit、Sourcegraph

**治理架构：**
- Anthropic将MCP捐赠给Linux Foundation旗下的**Agentic AI Foundation（AAIF）**
- 联合创始成员：Anthropic、Block、OpenAI
- 支持者：Google、Microsoft、AWS、Cloudflare、Bloomberg

### 3.2 Agent2Agent Protocol

- 2025年4月由Google推出
- MCP解决Agent如何使用工具，Agent2Agent解决Agent之间如何通信
- 两者协同设计，均已捐赠给Linux Foundation

### 3.3 Agent Skills（新标准）

- Anthropic于2025年12月推出
- 定义Agent的能力边界和专业领域
- 与MCP形成互补的标准体系

---

## 四、头部玩家与产品

### 4.1 OpenAI

| 产品 | 能力 | 亮点 |
|------|------|------|
| **Operator** | 自主上网执行任务 | 2025年5月升级至o3模型，金融分析成本降低70% |
| **ChatGPT Pulse** | 每日主动推送个性化研究 | 从被动到主动的标志性产品 |
| **GPT Atlas** | Agentic Browser | 浏览器作为主动参与者 |

### 4.2 Anthropic

| 产品 | 能力 | 亮点 |
|------|------|------|
| **Claude Computer Use** | 操作电脑（浏览器、CLI、鼠标） | 业界最早的Computer Use能力 |
| **MCP生态** | 连接外部工具和数据源 | 成为行业标准 |

### 4.3 Google

| 产品 | 能力 | 亮点 |
|------|------|------|
| **Gemini 2.5 Pro** | 操作系统级整合（AIOS） | 医疗影像诊断准确率提升37% |
| **Jules AI** | 主动式编程助手 | Suggested Tasks自动扫描代码库 |

### 4.4 国内玩家

| 产品 | 能力 | 亮点 |
|------|------|------|
| **DeepSeek R1** | 超强推理能力 | SuperCLUE榜单65.18分登顶，工业故障预测92%准确率 |
| **MasterAgent** | 自主可控方案 | 国产替代路线 |

---

## 五、应用场景与落地案例

### 5.1 已规模化的场景

| 场景 | 应用形式 | 效果 |
|------|----------|------|
| 客服 | 自动关闭工单 | Telus：57,000员工使用，单次交互节省40分钟 |
| 金融 | 自动拉取报告+合规审核 | 成本降低70% |
| 供应链 | 自动重新调度运输 | 实时响应突发状况 |
| 编程 | 自动修复TODO、代码审查 | Jules AI Suggested Tasks |

### 5.2 前沿探索场景

| 场景 | 研究机构 | 进展 |
|------|----------|------|
| 物理世界主动助手 | CMU | 日常物品变身移动机器人，预判人类需求 |
| 智慧城市 | 某项目 | 交通+能源Agent协同，碳排放降低18% |
| 具身智能 | 多家 | 从虚拟助手到实体伙伴（家庭服务、工业质检） |

### 5.3 Agentic Browser（新品类）

2025年中涌现的新品类：
- Perplexity Comet
- Browser Company Dia
- OpenAI GPT Atlas
- Microsoft Edge Copilot

---

## 六、技术架构趋势

### 6.1 混合AI架构（2026主流）

> 不再争论"LLM vs 知识系统"，而是两者融合。

- **LLM**：提供神经网络直觉
- **符号/语义系统**：提供结构化推理
- **Knowledge Graph**：作为协调中枢

### 6.2 GraphRAG

知识图谱驱动的RAG架构，成为企业自动化的核心：
- 共享记忆
- 跨部门Agent协调
- 数据系统连接

### 6.3 Multi-Agent协作

- 2025年是Agent元年
- 2026年是Multi-Agent生产化元年
- 典型架构：专业Agent分工 + 中央协调器

---

## 七、风险与挑战

### 7.1 技术风险

| 风险 | 描述 | 缓解措施 |
|------|------|----------|
| 提示注入攻击 | 恶意提示操控Agent行为 | 安全审计、输入过滤 |
| 工具权限问题 | 组合工具可能泄露文件 | 最小权限原则 |
| 工具欺骗 | 相似工具替代受信任工具 | 工具签名验证 |

### 7.2 落地风险

| 风险 | Gartner预测 |
|------|-------------|
| 项目失败率 | 到2025年底，30%早期Agentic AI项目将在5年内失败 |
| "孤独Agent"问题 | 企业部署数百个Agent，但大多闲置 |

### 7.3 治理挑战

- 数据治理不完善
- 监督机制缺失
- 责任边界模糊

---

## 八、市场预测

| 时间节点 | 预测 |
|----------|------|
| 2025年底 | 25%使用GenAI的企业将试点Agentic AI |
| 2027年 | 增长至50% |
| 2025-2027年 | 编程、客服、数据分析等标准化场景全面落地 |
| 2030年 | 全球Agent市场规模突破471亿美元 |

---

## 九、给增长型产品的启示

### 9.1 产品机会

1. **Agentic功能嵌入现有产品**
   - 工具类APP可增加"主动建议"功能
   - 从用户触发转向产品主动触发

2. **Voice Agent**
   - ASR → NLU → 任务规划 → 执行 → TTS 全链路
   - 适合客服、助手类场景

3. **垂直领域Agent**
   - 轻运营重转化的产品，Agent可进一步降低人力依赖
   - 适合金融、法务、医疗等专业领域

### 9.2 风险提示

- 避免"为了Agent而Agent"，先验证用户真实需求
- 控制Agent边界，保留人工干预入口
- 关注安全合规，尤其是数据隐私

---

## 十、信息源

- [2026 is set to be the year of agentic AI - Nextgov](https://www.nextgov.com/artificial-intelligence/2025/12/2026-set-be-year-agentic-ai-industry-predicts/410324/)
- [Enterprise AI and agentic software trends shaping 2026 - Intelligent CIO](https://www.intelligentcio.com/north-america/2025/12/24/enterprise-ai-and-agentic-software-trends-shaping-2026/)
- [The trends that will shape AI and tech in 2026 - IBM](https://www.ibm.com/think/news/ai-tech-trends-predictions-2026)
- [In 2026, AI will move from hype to pragmatism - TechCrunch](https://techcrunch.com/2026/01/02/in-2026-ai-will-move-from-hype-to-pragmatism/)
- [AI 2026 trends: bubbles, agents, demand for ROI - Axios](https://www.axios.com/2026/01/01/ai-2026-money-openai-google-anthropic-agents)
- [AI agents arrived in 2025 - The Conversation](https://theconversation.com/ai-agents-arrived-in-2025-heres-what-happened-and-the-challenges-ahead-in-2026-272325)
- [Agentic AI Foundation - Anthropic](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
- [Why the Model Context Protocol Won - The New Stack](https://thenewstack.io/why-the-model-context-protocol-won/)
- [2025年AI Agent发展趋势 - 知乎](https://zhuanlan.zhihu.com/p/17658886144)
- [ChatGPT Pulse - VentureBeat](https://venturebeat.com/ai/chatgpt-pulse-delivers-daily-personalized-research-moving-ai-from-reactive)
- [CMU Proactive AI Research](https://www.cmu.edu/news/stories/archives/2025/november/cmu-researchers-use-ai-to-turn-everyday-objects-into-proactive-assistants)
- [Jules Proactive AI - StartupHub](https://www.startuphub.ai/ai-news/ai-research/2025/jules-proactive-ai-transforms-dev-workflows/)

---

*报告完成于 2026年1月5日*
