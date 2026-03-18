# Atlas 编排器转换规则

本文档描述如何将 Atlas 编排器的 TypeScript 源文件转换为 Markdown 参考文档。

## 与普通 Agent 的差异

| 特性 | 普通 Agent | Atlas |
|------|-----------|-------|
| tool_restrictions | 有 | **无** |
| when_to_use | 有 | **无** |
| Input Contract | 需要 | **不需要** |
| Output | references/*.md | **SKILL.md**（独立 skill 目录） |
| 被调用方式 | 由其他 agent 调用 | 直接响应 `/start-work` 命令 |
| 结构 | 单个 prompt | **模块化**（多个 .ts 文件组合） |

## 转换模板

```markdown
---
name: omo-execute
description: Use this skill when you see `/omo-execute`. Master orchestrator that executes work plans from Prometheus. Reads `.sisyphus/plans/{name}.md`, delegates tasks to specialists, and verifies everything until completion.
---

# Atlas - Master Orchestrator

---

<identity>
${IDENTITY_CONTENT}
</identity>

<mission>
${MISSION_CONTENT}
</mission>

<delegation_system>
${DELEGATION_SYSTEM_CONTENT}
</delegation_system>

<auto_continue>
${AUTO_CONTINUE_CONTENT}
</auto_continue>

<workflow>
${WORKFLOW_CONTENT}
</workflow>

<parallel_execution>
${PARALLEL_EXECUTION_CONTENT}
</parallel_execution>

<notepad_protocol>
${NOTEPAD_PROTOCOL_CONTENT}
</notepad_protocol>

<verification_rules>
${VERIFICATION_RULES_CONTENT}
</verification_rules>

<boundaries>
${BOUNDARIES_CONTENT}
</boundaries>

<critical_overrides>
${CRITICAL_OVERRIDES_CONTENT}
</critical_overrides>

<post_delegation_rule>
${POST_DELEGATION_RULE_CONTENT}
</post_delegation_rule>

<Agent_Invocation_Format>
[插入内容...]
</Agent_Invocation_Format>
```

## 源文件结构

Atlas 的 prompt 直接定义在 `default.ts` 中，使用 XML 标签包裹各个模块。

## 提取规则

### 1. 标题

- 格式：`# Atlas - Master Orchestrator`

### 2. 各节内容

从 `default.ts` 的 `ATLAS_SYSTEM_PROMPT` 字符串中，按 XML 标签提取各节内容。

**⚠️ 重要：必须原样复制**
- 保留 XML 标签格式
- 移除 TS 注释块

## task() → codeagent-wrapper 转换规则

**⚠️ 重要**：详见 `references/codeagent-wrapper-rules.md`。

## 补充内容（需追加/插入）

### APPEND - 最后追加

**⚠️ 强制要求**：在 `<Agent_Invocation_Format>` 之前追加 `<Bash_Invocation_Only>` 章节。详见 `references/codeagent-wrapper-rules.md` 中的 "Bash_Invocation_Only" 部分。

```xml
<Agent_Invocation_Format>
```bash
codeagent-wrapper --agent <agent_name> - <workdir> <<'EOF'
## Original User Request
<original request>

## Context Pack (include anything relevant; write "None" if absent)
- Explore output: <...>
- Librarian output: <...>
- Oracle output: <...>
- Notepad content: <...>

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

Atlas 是**执行编排器**，根据计划文件调用实现+验证类 agent：

```xml
<Agent_Selection>
| Agent | When to Use | 职责 |
|-------|------------|------|
| `code-scout` | 任务需要代码定位或结构分析时 | 探索 |
| `librarian` | 任务需要外部库/API 文档时 | 探索 |
| `hephaestus` | 后端/逻辑代码实现任务 | **执行** |
| `frontend-ui-ux-engineer` | UI/样式/前端组件实现任务 | **执行** |
| `document-writer` | 文档编写任务 | **执行** |
| `momus` | Final Verification Wave 验证任务 | 与 Prometheus 共享 |
</Agent_Selection>
```

## 需删除的内容

| 原内容 | 问题 |
|--------|------|
| `session_id` 相关引用 | Claude Code 无 session_id 概念 |
| `background_output()` 和 `background_cancel()` 引用 | Claude Code 无这些工具 |
| `lsp_diagnostics` 引用 | Claude Code 使用不同诊断方式 |
| `HOOK([SYSTEM REMINDER - ...])` 引用 | Claude Code 无此 HOOK 机制 |
| `<Workflow_Relationship>` 章节 | 包含与其他 SKILL（Prometheus、Sisyphus）的关系描述 |
| 提及 "Prometheus"、"Sisyphus" 的描述 | 各 SKILL 独立运作，不应互相引用 |
| "Atlas vs Sisyphus" 对比表格 | 跨 SKILL 衔接描述 |

## 需替换的内容

| 原内容 | 处理方式 |
|--------|----------|
| `task(subagent_type="explore")` | 替换为 `codeagent-wrapper --agent code-scout` |
| `task(subagent_type="librarian")` | 替换为 `codeagent-wrapper --agent librarian` |
| `task(category="...")` | 替换为对应 agent 名称 |
| `run_in_background=true` | 删除此参数 |
| `session_id` 用于恢复 | Claude Code 无此机制，需重新理解上下文 |

## 执行步骤

1. **读取源文件**：`oh-my-openagent/src/agents/atlas/default.ts`
2. **提取各节**：按 XML 标签分割各节内容
3. **转换 task() 调用**：替换为 `codeagent-wrapper --agent` 格式
4. **删除不适用内容**：移除 session_id、background_*、lsp_*、HOOK 引用
5. **删除跨 SKILL 衔接描述**：移除 Workflow_Relationship 和提及其他编排器的内容
6. **插入补充内容**：追加 Agent_Invocation_Format（**不要**插入 Workflow_Relationship）
7. **输出**：生成 Markdown 文档到 `plugins/omo-workflow/skills/omo-execute/SKILL.md`

## 输出目录

```
plugins/omo-workflow/skills/omo-execute/SKILL.md
```

## 注意事项

- **XML 标签必须保留**：使用 `<identity>`、`<mission>`、`<workflow>` 等作为章节标签
- Atlas 是**纯执行编排器**，永远不写代码
- Atlas 与 Prometheus 配合：Prometheus 规划，Atlas 执行
- 确保输出的 Markdown 格式整洁、符合项目文档规范
