# Skill: Obsidian 知识图谱整理

> 基于 DDD 限界上下文原则，模块化整理 Obsidian 笔记

## 触发条件

当用户说：
- "整理知识图谱"
- "整理 Obsidian"
- "organize vault"
- "/organize"

## 执行步骤

### Phase 1: 分析现状

1. **统计基本信息**
```bash
VAULT_PATH="$HOME/Documents/Obsidian Vault"
echo "=== Vault 基本统计 ==="
echo "笔记数量: $(find "$VAULT_PATH" -name '*.md' -not -path '*/.trash/*' | wc -l)"
echo "总行数: $(find "$VAULT_PATH" -name '*.md' -not -path '*/.trash/*' -exec cat {} + | wc -l)"
echo "内部链接: $(grep -roh '\[\[.*\]\]' "$VAULT_PATH" --include='*.md' 2>/dev/null | wc -l)"
echo "空文件: $(find "$VAULT_PATH" -name '*.md' -empty | wc -l)"
```

2. **识别现有领域**
   - 扫描文件夹结构
   - 分析笔记内容关键词
   - 统计主题分布

3. **发现问题**
   - 孤立笔记（无链接）
   - 空文件
   - 根目录堆积
   - 重复/相似文件夹

### Phase 2: 设计限界上下文

基于 DDD 原则划分知识领域：

```
领域类型划分标准：
┌─────────────────────────────────────────────┐
│ Core Domain (核心域)                         │
│ - 最重要、投入最多的知识领域                   │
│ - 直接产生价值的内容                          │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ Supporting Domain (支撑域)                   │
│ - 支持核心域的辅助知识                        │
│ - 方法论、工具、技能                          │
└─────────────────────────────────────────────┘
┌─────────────────────────────────────────────┐
│ Generic Domain (通用域)                      │
│ - 通用知识、日常记录                          │
│ - 读书笔记、日志、人脉                        │
└─────────────────────────────────────────────┘
```

**Module 命名规范：**
- 英文命名，PascalCase
- 例：`AI-Engineering`, `Travel-Product`, `Cognitive-Growth`

### Phase 3: 创建 Module 结构

1. **创建文件夹**
```bash
mkdir -p "$VAULT_PATH/{Module名}/{子领域}"
mkdir -p "$VAULT_PATH/_Inbox"
mkdir -p "$VAULT_PATH/_attachments"
```

2. **迁移笔记**
   - 按内容分类移动到对应 Module
   - 跨领域笔记：主 Module 存放原文，其他 Module 在聚合根中引用

3. **创建聚合根文件**

每个 Module 必须有一个有意义命名的聚合根文件（如 `AI工程实践.md`、`旅行产品.md`），而非通用的 `_Index.md`，格式：

```markdown
# {Module 名称}

> 限界上下文：{职责描述}
> 领域类型：{Core/Supporting/Generic} Domain

## 领域职责
{一句话描述}

## 子领域

### {子领域1}
- [[路径/笔记1|显示名]]
- [[路径/笔记2|显示名]]

### {子领域2}
- ...

---

## 上下游依赖

### 下游（应用此领域）
- [[Other-Module/聚合根名称|模块名]] - 依赖说明

### 上游（依赖领域）
- [[Other-Module/聚合根名称|模块名]] - 依赖说明
```

4. **创建 Home.md**

根目录创建知识图谱入口：

```markdown
# Knowledge Graph Home

## Context Map
{可视化展示 Module 关系}

## 快速导航
| Module | 职责 | 笔记数 |
|--------|------|--------|
| [[Module/聚合根名称|名称]] | 职责 | N |
```

### Phase 4: 建立链接规则

```
规则 1: 对外暴露
  - 每个 Module 只通过聚合根文件对外暴露
  - 外部不应直接链接 Module 内部笔记

规则 2: 链接格式
  - 跨 Module: [[Module/聚合根名称|显示名]]
  - 内部链接: [[子文件夹/笔记名|显示名]]

规则 3: 链接数量
  - 每个 Module 最多 3 个对外依赖
  - 避免形成复杂依赖网络

规则 4: 跨领域内容
  - 原文放在主要相关的 Module
  - 其他 Module 在 _Index.md 中添加引用链接
```

### Phase 5: 清理与验证

1. **删除空文件**
```bash
find "$VAULT_PATH" -name "*.md" -empty -not -path "*/.trash/*" -delete
```

2. **清理空文件夹**
```bash
find "$VAULT_PATH" -type d -empty -delete
```

3. **验证链接**
   - 检查聚合根文件中的链接是否有效
   - 修复断链

4. **生成报告**
   - 各 Module 笔记数
   - 链接密度
   - 待整理项（_Inbox 内容）

## 输出模板

整理完成后，输出以下报告：

```markdown
# 知识图谱整理报告

## 整理前
- 笔记总数: X
- 根目录笔记: X (占比 X%)
- 空文件: X
- 链接密度: X 链接/笔记

## 整理后
| Module | 类型 | 笔记数 | 对外依赖 |
|--------|------|--------|----------|
| AI-Engineering | Core | X | 2 |
| ... | ... | ... | ... |

## Module 依赖图
{Mermaid 图}

## 待处理
- _Inbox 中有 X 篇待分类
- 建议每周 Review 一次
```

## 注意事项

1. **备份优先** - 执行前确认用户已备份
2. **渐进式迁移** - 大型 Vault 分批处理
3. **保持幂等** - 重复执行不应破坏结构
4. **尊重现有链接** - 迁移时更新相关引用

## 示例 Context Map

```
┌─────────── CORE ───────────┐
│  AI-Engineering            │
│  Travel-Product            │
└────────────────────────────┘
         │
         ▼
┌─────── SUPPORTING ─────────┐
│  Tech-Foundation           │
│  Cognitive-Growth          │
│  Work-Sharing              │
└────────────────────────────┘
         │
         ▼
┌─────── GENERIC ────────────┐
│  Reading | Journal | People│
│  _Inbox                    │
└────────────────────────────┘
```
