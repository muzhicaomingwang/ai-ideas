# AI Agent Constitution (Behavior Rules)

此文件定义了 AI 在本项目中生成代码和文档时必须遵守的**最高法则**。

## 1. 唯一真理源 (Single Source of Truth)
*   **术语一致性**：必须严格遵守 `01_Ubiquitous_Language/glossary.md` 中的术语定义。严禁创造同义词（例如：如果定义了 `Booking`，就不要使用 `Reservation` 或 `Appointment`）。
*   **设计一致性**：前端代码必须引用 `02_UI_UX_Design_Specs/design_tokens.json` 中的变量，严禁硬编码颜色值（Hex/RGB）或魔法数字。
*   **契约优先**：数据库 Schema (`03_Database_First`) 和 API Spec (`04_Backend_Architecture`) 一经确认，即为不可变契约。代码必须适应契约，而不是反过来。

## 2. 代码生成原则
*   **防御性编程**：假设输入总是恶意的。所有 API 接口必须包含参数校验（JSR-303/380）。
*   **无假设原则 (No Assumptions)**：遇到文档中未定义的业务逻辑（如：“订单超时时间是多少？”），**必须停止并询问**，而不是自己编造一个默认值。
*   **保持上下文**：在修改现有文件时，先读取并理解其原有的代码风格、命名习惯和注释规范，保持风格统一。

## 3. 架构约束
*   **分层隔离**：
    *   Controller 层仅负责 HTTP 转换和权限检查。
    *   Service/Domain 层负责业务逻辑。
    *   Repository/Mapper 层负责数据访问。
    *   严禁在 Controller 中直接查询数据库或编写复杂业务逻辑。
*   **依赖管理**：不要随意引入新的第三方库。如果是必须的，请先请求确认。

## 4. 安全红线
*   **零信任**：严禁在代码中硬编码任何密钥、密码或 Token。所有敏感配置必须通过环境变量注入。
*   **SQL 注入**：严禁使用字符串拼接构建 SQL。必须使用参数化查询或 ORM 框架的安全方法。

---
**Instruction to User**: Whenever you start a new chat session, please paste the content of this file first to "prime" the AI.
