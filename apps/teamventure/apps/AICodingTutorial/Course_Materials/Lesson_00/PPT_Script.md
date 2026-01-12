# Lesson 00: PPT 制作脚本

**主题**：AI Coding 第一步：上下文与规则设定 (Setting the Stage)
**目标**：教会学员如何“初始化”AI，消除代码生成的随机性。
**建议时长**：5-8 分钟

---

## Slide 1: 封面页
- **主标题**：基于文档的 AI 编程 (Document-Driven AI Coding)
- **副标题**：Lesson 00 - 驯服随机性：为 AI 设定行为准则
- **演讲者**：[您的名字]
- **配图建议**：一个机器人正在阅读一本厚厚的“规则书”，背景是整齐的代码块。

> **Speaker Notes**: 
> 大家好，欢迎来到 AI Coding 实战课程。
> 很多人用 AI 写代码，觉得效果像“抽卡”，时好时坏。
> 今天这第一节课，我们不写一行代码，我们来教大家如何“驯服”AI，让它从一个随性的聊天机器人，变成一个严谨的工程伙伴。

---

## Slide 2: 痛点：为什么 AI 写的代码不能用？
- **标题**：The Problem: Context Hallucination (上下文幻觉)
- **正文要点**：
    1.  **风格不统一**：一会儿用 Java 8，一会儿用 Java 17。
    2.  **架构混乱**：把业务逻辑塞进 Controller，数据库字段瞎编。
    3.  **命名随意**：`userId`, `User_ID`, `uID` 混用。
- **核心结论**：AI 不缺智商，缺的是**上下文 (Context)**。

> **Speaker Notes**: 
> 为什么 AI 经常写出“能跑但很烂”的代码？
> 因为它不知道你项目的“物理定律”。它不知道你用的是 COLA 架构，也不知道你规定表名必须加 `t_` 前缀。
> 当信息缺失时，AI 就会开始“猜”，这就是随机性的来源。

---

## Slide 3: 解决方案：上下文注入 (Context Injection)
- **标题**：The Solution: Prime the AI (预热/初始化)
- **图示**：
    - Left: AI (Blank Brain)
    - Arrow: Inject "Rules" & "Conventions"
    - Right: AI (Expert Engineer)
- **核心概念**：
    - **Single Source of Truth (唯一真理源)**
    - **Constraint-Based Generation (基于约束的生成)**

> **Speaker Notes**: 
> 解决办法很简单：把 AI 当作一个刚入职的高级工程师。
> 在让他干活之前，你必须先给他做“入职培训”。
> 我们通过“上下文注入”，把项目的所有规则先喂给它。

---

## Slide 4: 核心资产：两份“宪法”文件
- **标题**：The Two Pillars of Stability
- **分栏设计**：
    - **左栏：行为准则 (`rules_for_ai.md`)**
        - "宪法"
        - 规定做什么、不做什么
        - e.g. "禁止硬编码密码", "Controller 必须纯净"
    - **右栏：技术规范 (`project_convention.md`)**
        - "物理定律"
        - 技术栈与命名法
        - e.g. "Java 17", "MySQL 8", "Snake_case for DB"

> **Speaker Notes**: 
> 我们把这个“入职培训”浓缩成了两个 Markdown 文件。
> 左边是《行为准则》，这是宪法，规定了安全红线和架构原则。
> 右边是《技术规范》，这是物理定律，规定了语言版本和命名习惯。
> 这两个文件，是我们在本课程中所有后续操作的基石。

---

## Slide 5: 深度解析：Rules for AI
- **标题**：Document 1: rules_for_ai.md
- **代码/文本片段**：
    ```markdown
    ## 3. 架构约束
    * Controller 层仅负责 HTTP 转换。
    * 严禁在 Controller 中直接查询数据库。
    
    ## 4. 安全红线
    * 零信任：严禁在代码中硬编码 Token。
    ```
- **重点高亮**：No Assumptions (无假设原则) —— 不知道就问，别猜！

> **Speaker Notes**: 
> 让我们看一眼 `rules_for_ai.md` 的核心内容。
> 最重要的一条是“No Assumptions”——无假设原则。
> 我们明确告诉 AI：如果你不知道业务逻辑（比如订单多久过期），你要停下来问我，而不是自己编一个“30分钟”。

---

## Slide 6: 深度解析：Project Conventions
- **标题**：Document 2: project_convention.md
- **代码/文本片段**：
    ```markdown
    ## Tech Stack
    * Backend: Java 17 + Spring Boot 3 + COLA
    * DB: MySQL 8.0
    
    ## Naming
    * Class: PascalCase (BookingService)
    * DB Table: snake_case (t_booking)
    ```
- **作用**：消除技术栈的歧义。

> **Speaker Notes**: 
> 接下来是 `project_convention.md`。
> 这里定义了技术栈。如果不写这个，AI 可能会给你用 JUnit 4 而不是 JUnit 5，或者用 Lombok 但忘了加注解。
> 把这些写死，AI 就没有了“自由发挥”的空间，从而保证了输出的稳定性。

---

## Slide 7: 工作流演示 (Workflow)
- **标题**：Action: How to initialize a session?
- **步骤图**：
    1.  **Open Chat** (ChatGPT / Claude / IDE)
    2.  **Paste Rules** (Copy content of `rules_for_ai.md`)
    3.  **Paste Conventions** (Copy content of `project_convention.md`)
    4.  **Confirm** (Wait for AI to say "Understood")
- **截图**：一张实际的 Chat 界面截图，显示用户粘贴了长文本。

> **Speaker Notes**: 
> 具体怎么操作呢？非常简单。
> 每次当你开启一个新的 Chat 窗口，或者开始一个新的任务时。
> 第一件事，不是提需求，而是把这两个文件的内容复制粘贴进去。
> 告诉 AI：“这是我们的规则，请确认。”
> (稍后在视频演示环节，我会演示一次)

---

## Slide 8: 预期结果 (Expected Outcome)
- **标题**：The "Aha!" Moment
- **对比**：
    - **Before**: "Here is a simple Controller code..." (Generic, simple)
    - **After**: "Understood. Based on your COLA architecture, I will create a clean Adapter layer and separate the Domain logic..." (Professional, specific)
- **核心价值**：建立了信任 (Trust)。

> **Speaker Notes**: 
> 当你做完这一步，你会发现 AI 的语气都变了。
> 它不再是一个泛泛而谈的助手，而是一个懂你架构的工程师。
> 这就是我们想要的“专业感”。

---

## Slide 9: 总结与预告
- **标题**：Summary & Next Step
- **总结点**：
    1. AI 需要上下文。
    2. 用两份文档锁定规则与技术栈。
    3. 每次对话前先“注入”这些文档。
- **预告**：Lesson 01 - Defining the World
    - 如何让 AI 理解业务？
    - 构建 Ubiquitous Language (领域共同语言)。

> **Speaker Notes**: 
> 总结一下：今天的课没有写代码，但比写代码更重要。我们设定了舞台。
> 下一节课，我们将在这个舞台上，开始构建我们的世界——定义“什么是活动，什么是场次”。
> 那是 DDD 真正发挥威力的地方。下节课见。

---

## Slide 10: (End Screen)
- **Logo**: TeamVenture / AI Coding Tutorial
- **Text**: Happy Coding!
