# Sisyphus 编排器转换规则

本文档描述如何将 Sisyphus 编排器的 TypeScript 源文件转换为 Markdown 参考文档。

## 与普通 Agent 的差异

| 特性 | 普通 Agent | Sisyphus |
|------|-----------|----------|
| tool_restrictions | 有 | **无** |
| when_to_use | 有 | **无** |
| Input Contract | 需要 | **不需要** |
| Output | references/*.md | **SKILL.md** (根目录) |
| 被调用方式 | 由 Sisyphus 调用 | 直接响应 `/omo` 命令 |

## 转换模板

```markdown
---
name: omo
description: Use this skill when you see `/omo`. Multi-agent orchestration for "code analysis / bug investigation / fix planning / implementation". Choose the minimal agent set and order based on task type + risk; recipes below show common patterns. 

# Sisyphus - Powerful AI Agent with orchestration capabilities

---

<Role>
${ROLE_CONTENT}
</Role>

<Hard_Constraints>
[追加内容...]
</Hard_Constraints>

<Behavior_Instructions>
${BEHAVIOR_INSTRUCTIONS_CONTENT}
</Behavior_Instructions>

<Clarification_and_Decision_Gate>
[插入内容...]
</Clarification_and_Decision_Gate>

<Routing_Signals>
[插入内容...]
</Routing_Signals>

<Agent_Invocation_Format>
[追加内容...]
</Agent_Invocation_Format>

<Examples>
[追加内容...]
</Examples>

<Tone_and_Style>
${TONE_AND_STYLE_CONTENT}
</Tone_and_Style>

<Constraints>
${CONSTRAINTS_CONTENT}
</Constraints>

<Forbidden_Behaviors>
[追加内容...]
</Forbidden_Behaviors>

<Anti_Patterns>
[追加内容...]
</Anti_Patterns>

<Soft_Guidelines>
[追加内容...]
</Soft_Guidelines>

[替换：Agent Selection 表格]
```

**⚠️ 重要**：
- TS 源 XML 标签 `<Role>`、`<Behavior_Instructions>`、`<Tone_and_Style>`、`<Constraints>` 必须**原样保留**
- 插入/追加的章节也必须用 XML 标签包裹（`<Hard_Constraints>`、`<Clarification_and_Decision_Gate>` 等）
- **不要**使用 Markdown 标题格式（`## Hard Constraints`）

## 提取规则

TS 源内容**完整保留**，仅做以下转换：

| 变量 | 来源 | 处理方式 |
|------|------|----------|
| `${category}` | `SISYPHUS_PROMPT_METADATA.category` | 直接使用 |
| `${ROLE_CONTENT}` | `<Role>...</Role>` | 完整保留，追加 Hard Constraints |
| `${BEHAVIOR_INSTRUCTIONS_CONTENT}` | `<Behavior_Instructions>...</Behavior_Instructions>` | 完整保留，过滤 Claude Code 不适用内容，插入补充章节 |
| `${TONE_AND_STYLE_CONTENT}` | `<Tone_and_Style>...</Tone_and_Style>` | 完整保留 |
| `${CONSTRAINTS_CONTENT}` | `<Constraints>...</Constraints>` | 完整保留，替换 Agent Selection 表格 |

## task() → codeagent-wrapper 转换规则

**⚠️ 重要**：详见 `references/codeagent-wrapper-rules.md`。

## 补充内容（需追加/插入）

TS 源内容**完整保留**（仅做 task() → codeagent-wrapper 转换和 Claude Code 不适用内容过滤）。以下内容作为**补充章节**追加或插入到对应位置，**必须使用 XML 标签包裹**：

### APPEND - Role 之后追加

**⚠️ 强制要求**：详见 `references/codeagent-wrapper-rules.md`：
- "强制约束" 部分：`<Hard_Constraints>`
- **新增** "Bash_Invocation_Only" 部分：`<Bash_Invocation_Only>`（🔴 醒目强调）

### INSERT - Intent Gate 章节中插入

在 TS 源 Intent Gate 的 `### When to Challenge the User` 之后，`## Phase 1 - Codebase Assessment` 之前插入：

```xml
<Clarification_and_Decision_Gate>
Use `AskUserQuestion` whenever **blocking ambiguities or pending decisions** are detected — **not at a fixed point, but as a gate before any implementation agent starts**. This check can trigger at any moment during the workflow:

- **Before routing** — initial request is obviously ambiguous or underspecified
- **After `code-scout`** — exploration reveals unclear scope, conflicting patterns, or multiple valid approaches
- **After `oracle`** — design surfaces architectural choices, tradeoffs, or risks the user must weigh in on

<Ask_When>
**Ambiguities:**
- Multiple valid interpretations that lead to different implementations
- Missing critical context (target file, expected behavior, environment)
- Unclear scope or success criteria for non-trivial changes

**Decisions:**
- `oracle` (or exploration) proposes multiple approaches and there is no clear "best" — the user must choose
- Architectural tradeoffs with different cost/risk profiles (e.g., extend existing module vs. new abstraction)
- Irreversible or high-impact choices (e.g., schema changes, API breaking changes, deletion)
- Scope expansion discovered mid-workflow (e.g., fixing X properly requires also changing Y)
</Ask_When>

<Skip_Clarification_When>
- Exact file path + line number provided and intent is unambiguous
- Single approach with clear rationale and no meaningful alternative
- Standard explanation/analysis request (`how does X work?`)
- Completeness ≥ 8/10 in self-assessment and no pending decisions
</Skip_Clarification_When>
</Clarification_and_Decision_Gate>

<Routing_Signals>
This skill is **routing-first**, not a mandatory `code-scout → oracle → hephaestus` conveyor belt.

| Signal | Add this agent |
|--------|----------------|
| Code location/behavior unclear | `code-scout` |
| External library/API usage unclear | `librarian` |
| Risky change: multi-file/module, public API, data format/config, concurrency, security/perf, or unclear tradeoffs | `oracle` |
| Implementation required | `hephaestus` (or `frontend-ui-ux-engineer` / `document-writer`) |

<Skipping_Heuristics>
- Skip `code-scout` when the user already provided exact file path + line number, or you already have it from context.
- Skip `oracle` when the change is **local + low-risk** (single area, clear fix, no tradeoffs). Line count is a weak signal; risk is the real gate.
- Skip implementation agents when the user only wants analysis/answers (stop after `code-scout`/`librarian`).
</Skipping_Heuristics>

<Common_Recipes>
- Explain code: `code-scout`
- Small localized fix with exact location: `hephaestus`
- Bug fix, location unknown: `code-scout → hephaestus`
- Cross-cutting refactor / high risk: `code-scout → oracle → hephaestus` (optionally `oracle` again for review)
- External API integration: `code-scout` + `librarian` (can run in parallel) → `oracle` (if risk) → implementation agent
- UI-only change: `code-scout → frontend-ui-ux-engineer` (split logic to `hephaestus` if needed)
- Docs-only change: `code-scout → document-writer`
</Common_Recipes>
</Routing_Signals>
```

### APPEND - Behavior_Instructions 之后追加

**⚠️ 强制要求**：详见 `references/codeagent-wrapper-rules.md`：
- `<Agent_Invocation_Format>` 模板
- `<Examples>` 调用示例
- 禁止行为和 Anti_Patterns

## 需删除的内容

以下内容**必须删除**，不输出到 SKILL.md：

| 原内容 | 问题 |
|--------|------|
| `## Background Result Collection` | Claude Code 无 background task 机制 |
| `### Session Continuity (MANDATORY)` | Claude Code 无 session_id 概念 |
| `### Evidence Requirements` | Claude Code 不适用 |
| **跨 SKILL 衔接描述** | 提及 Prometheus、Atlas 等其他编排器的描述 |
| `<Workflow_Relationship>` 章节 | 包含与其他 SKILL 关系的描述 |
| "Plan Agent" 引用（指 Prometheus） | 改为"consult oracle for complex planning" |

## 需替换的内容

详见 `references/codeagent-wrapper-rules.md` 中的"需替换的内容"部分。

### Agent Selection 表格

Sisyphus 是**直接执行编排器**，调用探索+咨询+实现类 agent：

```xml
<Agent_Selection>
| Agent | When to Use | 职责 |
|-------|------------|------|
| `code-scout` | 代码定位、结构分析、bug 查找 | 探索 |
| `librarian` | 外部库/API 文档查找 | 探索 |
| `oracle` | 风险评估、架构设计、技术选型 | 咨询 |
| `hephaestus` | 后端/逻辑代码实现 | **执行** |
| `frontend-ui-ux-engineer` | UI/样式/前端组件实现 | **执行** |
| `document-writer` | 文档编写 | **执行** |
| `multimodal-looker` | 媒体文件解读 | 工具 |
</Agent_Selection>
```

### APPEND - Tone_and_Style 之后追加

**⚠️ 强制要求**：详见 `references/codeagent-wrapper-rules.md`：
- `<Forbidden_Behaviors>`、`<Anti_Patterns>`、`<Soft_Guidelines>`
- `<Hard_Blocks>`

## 执行步骤

1. **读取 ts 文件**：`oh-my-openagent/src/agents/sisyphus/index.ts`
2. **提取 Metadata**：定位 `SISYPHUS_PROMPT_METADATA` 对象
3. **提取 Prompt 各节**：定位 `buildDynamicSisyphusPrompt()` 函数中的 XML 节，**完整保留**
4. **转换 task() 调用**：将 `task()` 替换为 `codeagent-wrapper --agent` 格式
5. **过滤**：删除 `Background Result Collection`、`Session Continuity`、`Evidence Requirements` 等不适用章节
6. **插入补充内容**：按分块在对应位置插入 XML 标签包裹的补充内容
7. **追加补充内容**：在对应位置追加 XML 标签包裹的补充内容（Hard Constraints、Agent Invocation Format、Examples、Forbidden Behaviors 等）
8. **替换**：使用标准 Agent Selection 表格替换 TS 源中的表格
9. **输出**：生成 Markdown 文档到 `plugins/omo-workflow/skills/omo/SKILL.md`

## 注意事项

- **XML 标签必须保留**：TS 源中的 `<Role>...</Role>`、`<Behavior_Instructions>...</Behavior_Instructions>` 等 XML 标签必须**原样保留为 XML 标签**，**不要**转换为 Markdown 章节标题（`## Role`、`### Behavior_Instructions` 等）
- Prompt 内容必须原样复制，不可修改
- 确保输出的 Markdown 格式整洁、符合项目文档规范
