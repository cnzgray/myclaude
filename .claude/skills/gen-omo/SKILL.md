---
name: gen-omo
description: |
  将 oh-my-openagent 项目中的 agent .ts 文件批量转换为 Markdown 参考文档。
  当用户提到"批量转换 agents"、"生成 agents md 文档"、"gen-omo"时使用此 skill。
  详细转换规则请参考 references/gen-omo-rules.md。
---

# TS to OMO Markdown 转换器

将 oh-my-openagent 项目中的 agent `.ts` 文件批量转换为 Markdown 参考文档。

## Agent 列表来源

读取 `oh-my-openagent/src/agents/builtin-agents.ts` 文件，从 `agentSources` 对象中提取 agent 列表。

## 处理范围

**⚠️ 单独处理的编排器**：
- **Prometheus (omo-plan)** - 战略规划顾问，使用独立规则 `references/prometheus-rules.md`，输出到 `plugins/omo-workflow/omo-plan/SKILL.md`
- **Atlas (omo-execute)** - 计划执行编排器，使用独立规则 `references/atlas-rules.md`，输出到 `plugins/omo-workflow/omo-execute/SKILL.md`
- **Sisyphus (omo)** - 执行编排器，使用独立规则 `references/sisyphus-rules.md`，输出到 `plugins/omo-workflow/omo/SKILL.md`
- **Sisyphus-junior** - 简化版编排器（暂不处理）

**✅ 需要处理的 Agent**：
除上述编排器外的全部 agent，输出到 `plugins/omo-workflow/references/`。

## 执行步骤

**⚠️ 重要：使用 Subagent 并发执行**

由于要处理的 Agent 数量较多，使用 subagent 为每个 Agent 并发执行转换任务。subagent 的模型继承父 agent.

### 第一步：处理编排器（Prometheus、Atlas、Sisyphus）

这三个编排器**不在** `agentSources` 列表中（或需要特殊处理），需要**手动单独执行**：

1. **Prometheus** → 使用 `references/prometheus-rules.md` 规则
   - 源文件：`oh-my-openagent/src/agents/prometheus/system-prompt.ts` 及相关模块
   - 输出：`plugins/omo-workflow/omo-plan/SKILL.md`

2. **Atlas** → 使用 `references/atlas-rules.md` 规则
   - 源文件：`oh-my-openagent/src/agents/atlas/default.ts`
   - 输出：`plugins/omo-workflow/omo-execute/SKILL.md`

3. **Sisyphus** → 使用 `references/sisyphus-rules.md` 规则
   - 源文件：`oh-my-openagent/src/agents/sisyphus/index.ts`
   - 输出：`plugins/omo-workflow/omo/SKILL.md`

### 第二步：处理普通 Agents

1. **读取 agentSources**：从 `builtin-agents.ts` 获取 agent 列表
2. **过滤**：排除 `sisyphus`、`prometheus`、`atlas`、`sisyphus-junior`
3. **并发转换**：为每个 Agent 启动独立的 subagent，并发读取 ts 文件。**必须带上 `references/gen-omo-rules.md` 文件引用**，让 subagent 按规则生成 md
4. **输出 MD 文件**：所有 MD 文件输出到 `plugins/omo-workflow/references/` 目录

## 输出目录

```
plugins/omo-workflow/references/
```

文件命名：`{agent-name}.md`（小写），如 `oracle.md`、`hephaestus.md`

## 详细规则

转换模板和提取规则请查看 `references/gen-omo-rules.md`。

## ⚠️ Agent 名称映射（重要）

TS 源中的 agent 名称与 codeagent-wrapper 中的名称不同，**必须按以下映射转换**：

| TS 源名称 | codeagent-wrapper 名称 |
|-----------|----------------------|
| `explore` | `code-scout` |
| `librarian` | `librarian` |
| `metis` | `metis` |
| `oracle` | `oracle` |
| `momus` | `momus` |
| `hephaestus` | `hephaestus` |
| `frontend-ui-ux-engineer` | `frontend-ui-ux-engineer` |
| `document-writer` | `document-writer` |

**关键映射**：`explore` → `code-scout`（避免与 Claude Code 内置 subagent 名称冲突）

详见 `references/codeagent-wrapper-rules.md` 中的转换表。
