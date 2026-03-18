# Prometheus 编排器转换规则

本文档描述如何将 Prometheus 编排器的 TypeScript 源文件转换为 Markdown 参考文档。

## 与普通 Agent 的差异

| 特性 | 普通 Agent | Prometheus |
|------|-----------|------------|
| tool_restrictions | 有 | **无**（通过 prometheus-md-only hook 强制） |
| when_to_use | 有 | **无** |
| Input Contract | 需要 | **不需要** |
| Output | references/*.md | **SKILL.md**（独立 skill 目录） |
| 被调用方式 | 由 Sisyphus 调用 | 独立规划阶段编排器 |
| 结构 | 单个 prompt | **模块化**（多个 .ts 文件组合） |

## 转换模板

```markdown
---
name: omo-plan
description: Use this skill when you see `/omo-plan`. Strategic planning consultant that interviews users, consults Metis for gap analysis, and generates work plans. Works before Sisyphus in the workflow.
---

# Prometheus - Strategic Planning Consultant

---

<Identity_and_Constraints>
${IDENTITY_CONSTRAINTS_CONTENT}
</Identity_and_Constraints>

<Interview_Mode>
${INTERVIEW_MODE_CONTENT}
</Interview_Mode>

<Plan_Generation>
${PLAN_GENERATION_CONTENT}
</Plan_Generation>

<High_Accuracy_Mode>
${HIGH_ACCURACY_MODE_CONTENT}
</High_Accuracy_Mode>

<Plan_Template>
${PLAN_TEMPLATE_CONTENT}
</Plan_Template>

<Behavioral_Summary>
${BEHAVIORAL_SUMMARY_CONTENT}
</Behavioral_Summary>

<Agent_Invocation_Format>
[插入内容...]
</Agent_Invocation_Format>
```

## 源文件结构

Prometheus 的 prompt 由以下模块组合而成：

| 文件 | 内容 | 映射到 |
|------|------|--------|
| `identity-constraints.ts` | 核心身份约束、绝对规则、Turn 终止规则 | `<Identity_and_Constraints>` |
| `interview-mode.ts` | 访谈模式策略 | `<Interview_Mode>` |
| `plan-generation.ts` | 计划生成流程、Metis 咨询 | `<Plan_Generation>` |
| `high-accuracy-mode.ts` | Momus 审核循环 | `<High_Accuracy_Mode>` |
| `plan-template.ts` | 工作计划 Markdown 模板 | `<Plan_Template>` |
| `behavioral-summary.ts` | 行为总结与交接程序 | `<Behavioral_Summary>` |

## 提取规则

### 1. 标题

- 从 `system-prompt.ts` 提取 `PROMETHEUS_SYSTEM_PROMPT` 的第一行识别角色描述
- 格式：`# Prometheus - Strategic Planning Consultant`

### 2. 模块内容

从 `system-prompt.ts` 组合的 `PROMETHEUS_SYSTEM_PROMPT` 中，按模块提取各节内容。

**⚠️ 重要：必须原样复制**
- 保留 XML 标签格式（如 `<system-reminder>`）
- 移除 TS 注释块（如 `/** ... */`）

### 3. 组合方式

```typescript
// system-prompt.ts 中的组合
export const PROMETHEUS_SYSTEM_PROMPT = `${PROMETHEUS_IDENTITY_CONSTRAINTS}
${PROMETHEUS_INTERVIEW_MODE}
${PROMETHEUS_PLAN_GENERATION}
${PROMETHEUS_HIGH_ACCURACY_MODE}
${PROMETHEUS_PLAN_TEMPLATE}
${PROMETHEUS_BEHAVIORAL_SUMMARY}`
```

## task() → codeagent-wrapper 转换规则

**⚠️ 重要**：详见 `references/codeagent-wrapper-rules.md`。

## 补充内容（需追加/插入）

### APPEND - 最后追加

**⚠️ 强制要求**：在 `<Agent_Invocation_Format>` 之前追加 `<Bash_Invocation_Only>` 章节。详见 `references/codeagent-wrapper-rules.md` 中的 "Bash_Invocation_Only" 部分。

**注意**：**不要**插入 `<Workflow_Relationship>` 章节，各 SKILL 应独立运作。

```xml
<Agent_Invocation_Format>
```bash
codeagent-wrapper --agent <agent_name> - <workdir> <<'EOF'
## Original User Request
<original request>

## Context Pack (include anything relevant; write "None" if absent)
- Explore output: <...>
- Librarian output: <...>
- Metis output: <...>
- Oracle output: <...>
- Known constraints: <tests to run, time budget, repo conventions, etc.>

## Current Task
<specific task description>

## Acceptance Criteria
<clear completion conditions>
EOF
```

Execute in shell tool, timeout 2h.
</Agent_Invocation_Format>
```

### Agent_Selection

Prometheus 是**纯规划编排器**，调用分析+咨询类 agent：

```xml
<Agent_Selection>
| Agent | When to Use | 职责 |
|-------|------------|------|
| `code-scout` | 了解代码库结构、定位相关代码 | 探索 |
| `librarian` | 查找外部库/API 文档和最佳实践 | 探索 |
| `metis` | 意图分类、差距分析、工作量估算 | **仅此编排器** |
| `oracle` | 架构设计、技术选型、风险评估 | 咨询 |
| `momus` | 验证工作计划可执行性、引用有效性 | 与 Atlas 共享 |
</Agent_Selection>
```

## 需删除的内容

以下内容**必须删除**，不输出到 SKILL.md：

| 原内容 | 问题 |
|--------|------|
| `session_id` 相关引用 | Claude Code 无 session_id 概念 |
| `background_output()` 和 `background_cancel()` 引用 | Claude Code 无这些工具 |
| `lsp_*` 工具引用 | Claude Code 使用不同诊断方式 |
| `HOOK([SYSTEM REMINDER - ...])` 引用 | Claude Code 无此 HOOK 机制 |
| `<Workflow_Relationship>` 章节 | 包含与其他 SKILL（Atlas、Sisyphus）的关系描述 |
| 提及 "Sisyphus"、"Atlas" 的描述 | 各 SKILL 独立运作，不应互相引用 |

## 需替换的内容

| 原内容 | 处理方式 |
|--------|----------|
| `task(subagent_type="explore")` | 替换为 `codeagent-wrapper --agent code-scout` |
| `task(subagent_type="librarian")` | 替换为 `codeagent-wrapper --agent librarian` |
| `task(subagent_type="metis")` | 替换为 `codeagent-wrapper --agent metis` |
| `task(load_skills=[...])` | 删除此参数 |
| `run_in_background=true` | 删除此参数，改为直接执行 |

## 执行步骤

1. **读取源文件**：`oh-my-openagent/src/agents/prometheus/system-prompt.ts`
2. **提取各模块**：读取各 .ts 文件（identity-constraints.ts、interview-mode.ts 等）
3. **组合 Prompt**：按 `system-prompt.ts` 中的组合顺序拼接
4. **转换 task() 调用**：替换为 `codeagent-wrapper --agent` 格式
5. **删除不适用内容**：移除 session_id、background_*、lsp_*、HOOK 引用
6. **插入补充内容**：追加 Agent_Invocation_Format 和 Workflow_Relationship
7. **输出**：生成 Markdown 文档到 `plugins/omo-workflow/skills/omo-plan/SKILL.md`

## 输出目录

```
plugins/omo-workflow/skills/omo-plan/SKILL.md
```

## 注意事项

- **XML 标签必须保留**：使用 `<Identity_and_Constraints>`、`<Interview_Mode>` 等作为章节标签
- Prompt 内容必须原样复制，不可修改
- Prometheus 是**纯规划 agent**，永远不写代码
- 确保输出的 Markdown 格式整洁、符合项目文档规范
