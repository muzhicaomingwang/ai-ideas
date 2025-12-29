# AI Ideas / 产品想法与PRD仓库

> **维护者**: [@muzhicaomingwang](https://github.com/muzhicaomingwang)
> **目标受众**: 产品经理、AI创业者、非技术背景的产品学习者
> **仓库状态**: 🟢 活跃维护中 | 最后更新: 2025-12-29

本仓库用于沉淀「AI 原生产品」的想法池、产品文档（PRD/BP）与可复用模板，并配套一套面向产品人的 AI Coding 课程大纲，支持从 0→1 的快速论证与落地。

**📊 仓库概况**: 5个AI产品想法 | 1个完整PRD+BP样例 | 12周课程体系 | 2,300+行结构化文档

---

## 📚 你可以在这里找到什么

### 1) 想法池（Idea Pool）
`ai-product-ideas.md` - 5个AI产品想法收集与初步分析：

| 想法 | 类型 | 核心价值 | 状态 |
|------|------|---------|------|
| **Ego-Echo** | toC | 10分钟职场情绪复原 | ✅ [完整PRD+BP](prds/) |
| **DeepScan AI** | toProC | 科研/深度调研助手 | 💡 概念阶段 |
| **CodeLegacy AI** | toProC | 代码"考古"与重构专家 | 💡 概念阶段 |
| **LifeLens** | toC | 视觉化生活记录与搜索 | 💡 概念阶段 |
| **GhostAudit** | toB | AI风控分析师 | 💡 概念阶段 |

### 2) 产品文档（PRD / Business Plan）
- **`prds/ego-echo-workplace-recovery-prd.md`**
  Ego-Echo（职场压力复原）微信小程序 MVP 的完整PRD
  包含：目标/范围/用户流程/页面交互/AI Prompt设计/数据结构/API设计/埋点/实验计划/合规与隐私

- **`prds/ego-echo-business-plan.md`**
  Ego-Echo 的完整 Business Plan（经过10轮迭代优化）
  包含：市场分析/产品方案/技术架构/竞争护城河/GTM策略/单位经济/融资计划/风险应对

### 3) 可复用模板（Templates）
- **`templates/business-plan-template.md`**
  0→1 新产品 BP 标准模板
  特色：包含AI特有章节（AI成本估算、安全评估、合规风险等）

### 4) 课程内容（Educational Products）
- **`educational-products/README.md`** - 课程概览（面向产品/设计/非技术背景的 AI 辅助开发）
- **`educational-products/syllabus.md`** - 12周详细大纲（108小时学习内容 + 4个实战项目）

### 5) 架构分析与优化指南（Architecture Analysis）
- **`docs/architecture-analysis.md`**
  仓库深度分析报告（1,200+行）
  包含：架构设计/风险识别/技术债务/变更风险评估/优化路线图

---

## 🎯 仓库的核心原则

> 以下原则适用于本仓库的所有产品与技术讨论。详细应用指南见 [`docs/architecture-analysis.md`](docs/architecture-analysis.md)

1. **结构化优先** - 输入/输出尽量结构化（便于渲染、评测、埋点、复盘）
2. **可验证** - 每个结论尽量配"证据/数据/假设/验证计划"
3. **隐私与安全** - 对情绪/心理相关场景默认采用最小化数据与明确边界；危机内容优先安全兜底
4. **可落地** - 设计必须能转化为工程任务（API、数据结构、指标、实验计划、里程碑）

---

## 🚀 推荐阅读路径

### 快速了解（5分钟）
适合初次访问者，快速了解仓库内容
1. 阅读本 README
2. 浏览想法池：[`ai-product-ideas.md`](ai-product-ideas.md)

### 学习模板写作（15分钟）
适合需要快速写BP的创业者
1. 从模板开始：[`templates/business-plan-template.md`](templates/business-plan-template.md)
2. 参考字段说明和填写建议

### 深度学习样例（1小时）
适合想要学习完整PRD/BP写作方法的产品经理
1. 阅读完整PRD：[`prds/ego-echo-workplace-recovery-prd.md`](prds/ego-echo-workplace-recovery-prd.md)
2. 阅读完整BP：[`prds/ego-echo-business-plan.md`](prds/ego-echo-business-plan.md)
3. 对照模板理解每个章节的写作要点

### 了解架构与风险（30分钟）
适合想要深入理解仓库设计或贡献内容的协作者
1. 阅读架构分析报告：[`docs/architecture-analysis.md`](docs/architecture-analysis.md)
2. 了解文档维护原则和风险点

### 体系化学习（12周）
适合想要系统学习AI辅助开发的非技术产品人员
1. 课程介绍：[`educational-products/README.md`](educational-products/README.md)
2. 详细大纲：[`educational-products/syllabus.md`](educational-products/syllabus.md)
3. 跟随12周课程，完成4个实战项目

---

## 📝 文档维护建议

### 命名规范
- 文件命名尽量稳定（避免破坏链接与目录锚点）
- 新增产品建议在 `prds/` 下按 `产品代号-模块-prd.md` / `产品代号-business-plan.md` 组织

### 版本管理
- PRD/BP 重大变更建议按"版本号 + 日期 + 变更点"记录在文档头部
- 关键里程碑建议打 Git 标签（如 `ego-echo-bp-v2.0`）

### 一致性检查
- 修改核心概念（如产品定位、时间承诺、目标用户）时，请检查是否需要同步更新多个文档
- 参考 [`docs/architecture-analysis.md`](docs/architecture-analysis.md) 第3章了解需要同步的字段清单

---

## 🤝 如何贡献

欢迎提交新的AI产品想法、改进建议或课程实践案例！

### 贡献方式
1. **提交新想法**
   - Fork 本仓库
   - 在 `ai-product-ideas.md` 添加新想法（使用现有模板格式）
   - 提交 Pull Request

2. **改进现有文档**
   - 发现错误或不一致？直接提交 Issue 或 PR
   - 建议遵循本仓库的核心原则（结构化、可验证、可落地）

3. **分享学员作品**
   - 如果您完成了课程实践项目，欢迎提交到 `examples/` 目录
   - 格式：`examples/weekXX-项目名/`

### 贡献者公约
- 尊重原有文档的结构和风格
- 提供充分的上下文和说明
- 遵守隐私与安全原则（不提交敏感信息）

---

## 📄 许可证

本仓库采用 **MIT License** 开源。

- ✅ 可自由使用、修改、分发
- ✅ 商业使用友好
- ⚠️ 请保留原作者署名
- ⚠️ 软件"按原样"提供，不提供任何明示或暗示的保证

详见 [LICENSE](LICENSE) 文件（如需添加）。

---

## 📮 联系方式

- **GitHub Issues**: [提交问题或建议](https://github.com/muzhicaomingwang/ai-ideas/issues)
- **维护者**: [@muzhicaomingwang](https://github.com/muzhicaomingwang)

---

<div align="center">

**⭐ 如果这个仓库对你有帮助，欢迎 Star 支持！**

</div>
