# Lesson 02: 定义世界 —— 领域共同语言与 UI 线框图

## 1. 教学目标
学会如何通过“结构化文档”将业务需求转化为 AI 能够精准理解的设计。

## 2. 传统开发的痛点
- **需求模糊**：你说“用户报名”，AI 可能会理解为“创建账户”。
- **界面随意**：AI 生成的界面结构混乱，不符合你的审美或用户体验。

## 3. 核心工具：Ubiquitous Language (UL)
在 DDD 中，UL 是连接业务和代码的纽带。

### 实操演示：编写 Glossary
打开 `01_Ubiquitous_Language/glossary.md`。
注意看 **Activity** 和 **Session** 的区别：
- **Activity**: 羽毛球。
- **Session**: 周五晚上 8 点的羽毛球。
这是两个不同的表。如果你不明确定义，AI 极大概率会将它们合并为一个 `Event` 表，导致后期无法扩展。

## 4. 核心工具：ASCII 线框图 (Layout as Code)
我们不给 AI 图片，因为目前的 AI 解析图片布局的准确率不足以直接写代码。
我们给它 **ASCII Wireframes**。

### 实操演示：理解布局
查看 `02_UI_UX_Design_Specs/page_layouts_ascii.md`。
```text
+--------------------------------+
| [NavBar: TeamVenture]          |
+--------------------------------+
```
这段文本告诉 AI：
1. 这里有一个容器。
2. 里面有一个叫 `NavBar` 的组件。
3. 文本内容是 `TeamVenture`。
这比“页面顶部有个导航栏”这种描述要精准得多。

## 5. 将 UI 逻辑结构化
查看 `02_UI_UX_Design_Specs/interaction_flows.md`。
我们不在这里写代码（不要写 `function handleClick`）。
我们写 **状态机 (State Machine)**：
- "WHEN user clicks 'Book'..."
- "IF Session is Full THEN ..."
- "ELSE ..."

**这就是 AI 的伪代码。**

## 6. 课后练习
尝试增加一个新实体：“场地 (Venue)”。
1. 在 `glossary.md` 中增加 Venue 的定义。
2. 修改 `page_layouts_ascii.md`，在详情页增加场地信息展示块。
3. 观察如果你把这些给 AI，它是否能理解一个 Session 必须关联一个 Venue？

---
**下一课预告**：我们将进入最硬核的部分 —— `Lesson 03: 契约优先，从数据库到 API`。
