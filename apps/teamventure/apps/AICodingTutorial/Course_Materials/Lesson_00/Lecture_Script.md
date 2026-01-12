# Lesson 00: 视频录制逐字稿 (Lecture Script)

**准备工作**：
1.  打开 PPT，停留在 Slide 1。
2.  打开 IDE (VS Code)，侧边栏展开 `apps/AICodingTutorial` 目录。
3.  打开一个 AI 对话窗口（ChatGPT, Claude, 或 IDE 内置 Chat）。
4.  准备好 `rules_for_ai.md` 和 `project_convention.md` 的内容。

---

## Part 1: 开场引入 (配合 PPT Slide 1-3)

**(Slide 1: Title)**
大家好，我是[你的名字]。欢迎来到《基于文档的 AI 编程》系列教程。
今天我们讲第 0 课：Setting the Stage，也就是环境设定。

**(Slide 2: The Problem)**
作为开发者，我们现在每天都在用 AI 写代码。
但你有没有遇到过这种情况：你让 AI 写个登录功能，它给你生成了一堆代码。
结果你发现，它用的库是你项目里没有的；它的变量命名风格和你不一样；甚至它把 SQL 直接写在了 Controller 里。
你改这些代码花的时间，比你自己写还要长。
这就是**随机性**带来的痛点。

**(Slide 3: The Solution)**
为什么会这样？不是 AI 笨，而是因为 AI 不知道你的“上下文”。
在它眼里，你的项目是透明的。它只能按照它训练数据里的“平均水平”来猜。
所以，AI Coding 的第一原则就是：**Context is King (上下文为王)**。
我们必须把项目里的“隐性知识”，变成显性的文档，喂给 AI。

---

## Part 2: 核心资产解读 (配合 IDE 演示 + Slide 4-6)

**(切换到 IDE 界面)**
好，现在我带大家看一看，我们这个教程里最重要的两个“立国之本”。
请大家看到 `apps/AICodingTutorial/00_Meta_Context` 这个目录。

**(打开 rules_for_ai.md)**
第一个文件，叫 `rules_for_ai.md`。我们可以把它看作是给 AI 的**宪法**。
大家看这里（鼠标选中 "3. 架构约束"）：
我们明确规定了：Controller 层只能做 HTTP 转换，严禁写业务逻辑。
再看这里（鼠标选中 "4. 安全红线"）：
我们告诉它，绝对不能硬编码 Token。
这就像是新员工入职手册，规定了什么是“对的事”。

**(打开 project_convention.md)**
第二个文件，叫 `project_convention.md`。这是我们的**物理定律**。
这里定义了我们的技术栈：Java 17, Spring Boot 3, COLA 架构。
还有命名规范：表名必须以 `t_` 开头。
有了这个，AI 就不会再给你用 Java 8 的老语法，也不会给你生成 `userTable` 这种奇怪的表名了。

---

## Part 3: 实操演示 (配合 AI Chat 窗口 + Slide 7-8)

**(切换到 AI Chat 窗口)**
现在，我们来模拟一次真实的开发场景。
假设我要开始今天的开发工作了。

**(动作：复制粘贴)**
我先去把 `rules_for_ai.md` 的内容复制下来。
粘贴到对话框里。
然后，加一句 Prompt（提示词）：
> "这是项目的行为准则 (Behavior Rules)。请阅读并确认。"
发送。

**(等待 AI 回复)**
看，AI 回复了：“已收到，我会严格遵守这些安全和架构规则。”

**(动作：再次复制粘贴)**
接着，我复制 `project_convention.md`。
粘贴，并输入：
> "这是项目的技术规范 (Technical Conventions)。后续生成的代码必须符合这些定义。"
发送。

**(等待 AI 回复)**
好，AI 确认了：“明白，技术栈是 Java 17 + Spring Boot，数据库表名使用 snake_case。”

**(Slide 8: Expected Outcome)**
现在，这个 AI 就已经不是几分钟前那个通用的 AI 了。
它现在是**你团队的一员**。它脑子里装满了你的架构思想和代码规范。
在接下来的所有对话中，只要在这个 Session 里，它生成的每一行代码，都会默认遵守这些规则。

---

## Part 4: 总结 (配合 PPT Slide 9-10)

**(切回 PPT Slide 9)**
总结一下今天的内容：
1.  AI 写不好代码，通常是因为缺上下文。
2.  我们需要准备两份核心文档：行为准则和技术规范。
3.  每次开工前，先“喂”这两份文档，完成 AI 的初始化。

**(Slide 10: End)**
这只是第一步。
现在的 AI 虽然懂了规则，但它还不知道我们要造什么产品。
下一节课，我们将进入更有趣的部分：**定义世界**。
我们将教 AI 理解什么是“活动”，什么是“场次”，以及如何用 ASCII 码画出 UI 图。
下节课见！
