# How to Generate Schema with AI (Prompt Template)

如果你想让 AI 生成高质量的数据库设计，请使用以下 Prompt 模板。
核心技巧是：**显式引用之前的上下文文件**。

## Prompt Template

```markdown
# Context
I am building a Corporate Event Booking system.
Please refer to the following definitions:
1. @rules_for_ai.md (Specifically the "Naming Conventions" section)
2. @glossary.md (Core Entities and Relationships)

# Task
Design the MySQL 8.0 schema for this system.

# Requirements
1. **Naming**: Use `snake_case` for all tables and columns. All tables must start with `t_`.
2. **Entities to Cover**:
   - Employee
   - Team
   - Activity
   - Session (Note the relationship: One Activity has Many Sessions)
   - Booking (The link between Employee and Session)
3. **Business Logic Enforcement**:
   - Ensure a user cannot book the same session twice (Unique Constraint).
   - Ensure we track `booked_count` in the Session table for performance (Denormalization).
   - Include `version` column in `t_session` for Optimistic Locking.
4. **Output**:
   - Provide ONLY the SQL `CREATE TABLE` statements.
   - Add comments to every table and key column.
```

## Why this works?

1.  **Context Injection**: 通过 `@filename` (如果你的 IDE 支持) 或直接粘贴内容，让 AI 知道 "Activity" 和 "Session" 的区别。
2.  **Explicit Constraints**: 明确要求 Unique Constraint 和 Optimistic Locking，否则 AI 可能会忽略并发问题。
3.  **Style Guide**: 强制要求 `t_` 前缀，保证风格统一。
