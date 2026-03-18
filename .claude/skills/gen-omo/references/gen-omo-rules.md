# TS to MD 转换规则

本文档描述如何将 oh-my-openagent 中的 agent `.ts` 文件转换为 Markdown 参考文档。

## 变量说明

| 变量 | 来源 |
|------|------|
| `${AGENT_NAME}` | `*_PROMPT_METADATA.promptAlias` |
| `${TITLE_SUFFIX}` | 从 prompt 内容中提取角色描述（如 "Strategic Technical Advisor"） |
| `${PROMPT_CONTENT}` | `*_PROMPT` 或 `*_GPT_PROMPT` 完整内容 |
| `${TOOL_RESTRICTIONS}` | 从 `createAgentToolRestrictions([...])` 提取的列表 |
| `${WHEN_TO_USE_CONTENT}` | 从 `useWhen` 提取的 Markdown 表格 |
| `${WHEN_NOT_TO_USE_CONTENT}` | 从 `avoidWhen` 提取的 Markdown 列表 |

**标题格式**：`# ${AGENT_NAME} - ${TITLE_SUFFIX}`，其中 `${TITLE_SUFFIX}` 从 prompt 第一行提取（如 "Strategic Technical Advisor"）。

## 转换模板

**⚠️ 重要格式说明**：
- 文档是纯 Markdown 格式
- XML 标签内的内容**不需要额外的转义**，特别是反引号 `` ` `` 符号
- 直接保留原文即可，不要用 `` ` `` 包裹 XML 内的反引号

```markdown
# ${AGENT_NAME} - ${TITLE_SUFFIX}

## Input Contract (MANDATORY)

You are invoked by Sisyphus orchestrator. Your input MUST contain:
- ## Original User Request - What the user asked for
- ## Context Pack - Prior outputs from explore/librarian (may be "None")
- ## Current Task - Your specific task
- ## Acceptance Criteria - How to verify completion

**Context Pack takes priority over guessing.** Use provided context before searching yourself.

---

${PROMPT_CONTENT}

<tool_restrictions>
${AGENT_NAME} is a read-only advisor. The following tools are FORBIDDEN:
${TOOL_RESTRICTIONS}
</tool_restrictions>

<when_to_use>
${WHEN_TO_USE_CONTENT}
</when_to_use>

<when_not_to_use>
${WHEN_NOT_TO_USE_CONTENT}
</when_not_to_use>
```

## 提取规则

### 1. 标题

- `${AGENT_NAME}`：从 `*_PROMPT_METADATA.promptAlias` 提取
- `${TITLE_SUFFIX}`：从 prompt 内容第一行提取（如 "Strategic Technical Advisor"）

### 2. Prompt 内容

从 `*_PROMPT` 或 `*_GPT_PROMPT` 字符串常量中提取。

**⚠️ 重要：必须原样复制**

prompt 内容必须**逐字逐句原样复制**，包括：
- 开头的角色定义句子（如 "You are a strategic technical advisor..."）
- 所有 XML 标签格式（如 `<context>`, `</context>` 等）
- 所有标点符号，空格、换行
- 注释块（如 `/** ... */`）应删除

**处理方式**：
- 保留 XML 标签格式（如 `<context>`, `<expertise>` 等）
- 移除注释块（如 `/** ... */`）

### 3. Tool Restrictions

从 `createAgentToolRestrictions([...])` 调用中提取工具列表。

**转换规则**：
```typescript
// ts 中的数组
createAgentToolRestrictions(["write", "edit", "task", "apply_patch"])

// 转换为：章节用 XML 包裹，内容保持 Markdown 列表格式
<tool_restrictions>
${AGENT_NAME} is a read-only advisor. The following tools are FORBIDDEN:
- `write` - Cannot create files
- `edit` - Cannot modify files
- `task` - Cannot spawn subagents
- `apply_patch` - Cannot apply patches
</tool_restrictions>
```

常用工具的说明：
| 工具 | 说明 |
|------|------|
| `write` | Cannot create files |
| `edit` | Cannot modify files |
| `task` | Cannot spawn subagents |
| `background_task` | Cannot spawn background tasks |
| `apply_patch` | Cannot apply patches |
| `delegate_task` | Cannot delegate tasks |

### 4. When to Use

从 `*_PROMPT_METADATA.useWhen` 数组中提取。

**转换规则**：
```typescript
// ts 中的 useWhen 数组
useWhen: [
  "Complex architecture design",
  "After completing significant work",
  ...
]

// 转换为：章节用 XML 包裹，内容保持 Markdown 表格格式
<when_to_use>
| Trigger | Action |
|---------|--------|
| Complex architecture design | Consult FIRST |
| After completing significant work | Self-review |
| ... | ... |
</when_to_use>
```

### 5. When NOT to Use

从 `*_PROMPT_METADATA.avoidWhen` 数组中提取，转换为 Markdown 列表格式。

**转换规则**：
```typescript
// ts 中的数组
avoidWhen: [
  "Simple file operations (use direct tools)",
  "First attempt at any fix (try yourself first)",
  ...
]

// 转换为：章节用 XML 包裹，内容保持 Markdown 列表格式
<when_not_to_use>
- Simple file operations (use direct tools)
- First attempt at any fix (try yourself first)
- ...
</when_not_to_use>
```

## 执行步骤

1. **读取 ts 文件**：使用 Read 工具读取目标文件
2. **提取 Metadata**：定位 `*_PROMPT_METADATA` 对象，提取 `promptAlias`, `useWhen`, `avoidWhen`
3. **提取 Prompt**：定位 `*_PROMPT` 常量
4. **提取 Tool Restrictions**：定位 `createAgentToolRestrictions([...])` 调用
5. **拼装 MD**：按照模板结构组合各部分
6. **输出**：生成完整的 Markdown 文档

## 输出格式

生成的 Markdown 应包含：
- 标准化的标题（`# ${AGENT_NAME} - ${TITLE_SUFFIX}`）
- 完整的 Input Contract 说明
- 原始 prompt 内容（XML 标签格式）
- Tool Restrictions（XML 包裹的 Markdown 列表）
- When to Use / When NOT to Use（XML 包裹的 Markdown 内容）

## 注意事项

- Input Contract 部分在 ts 中不存在，需要使用标准模板
- Tool Restrictions 需要从数组手动扩展为带说明的列表
- Prompt 内容必须原样复制，不可修改
- 确保输出的 Markdown 格式整洁、符合项目文档规范
