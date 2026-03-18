# codeagent-wrapper 强制调用规则

本文档定义了所有编排器使用 `codeagent-wrapper` 调用外部 agent 的**强制规则**。所有 3 个编排器（Prometheus、Atlas、Sisyphus）都必须遵循此规则。

## 核心原则

**⚠️ 关键**：`codeagent-wrapper` 是**全局安装的外部 CLI 工具**，该工具有自己的一套 agent 定义。**所有 agent 都必须通过这个工具调度**，不要混淆为 Claude Code 内置工具。

```xml
**CRITICAL ORCHESTRATOR RULE**: You are an orchestrator that NEVER works alone. All agents MUST be launched via `codeagent-wrapper --agent <name>` using the Bash tool. NEVER use Claude Code's built-in Agent tool or subagents. Violating this is FORBIDDEN.
```

## task() → codeagent-wrapper 转换表

TS 源中的 `task()` 调用需要转换为 `codeagent-wrapper --agent` 格式：

| TS 源格式 | 转换后格式 |
|-----------|-----------|
| `task(subagent_type="explore", ...)` | `codeagent-wrapper --agent code-scout ...` |
| `task(subagent_type="librarian", ...)` | `codeagent-wrapper --agent librarian ...` |
| `task(subagent_type="metis", ...)` | `codeagent-wrapper --agent metis ...` |
| `task(subagent_type="momus", ...)` | `codeagent-wrapper --agent momus ...` |
| `task(subagent_type="oracle", ...)` | `codeagent-wrapper --agent oracle ...` |
| `task(category="hephaestus", ...)` | `codeagent-wrapper --agent hephaestus ...` |
| `task(category="frontend-ui-ux-engineer", ...)` | `codeagent-wrapper --agent frontend-ui-ux-engineer ...` |
| `task(category="document-writer", ...)` | `codeagent-wrapper --agent document-writer ...` |

## 转换示例

```typescript
// TS 源
task(subagent_type="explore", run_in_background=true, load_skills=[], description="Find auth", prompt="...")

// 转换后
codeagent-wrapper --agent code-scout - <workdir> <<'EOF'
## Context Pack
...
## Current Task
...
EOF
```

## 需删除的参数

| 参数 | 原因 |
|------|------|
| `run_in_background=true` | codeagent-wrapper 不支持 background 模式 |
| `load_skills=[...]` | codeagent-wrapper 不支持 skills 参数 |
| `session_id` | Claude Code 无 session_id 概念 |

## 强制约束（必须追加到 SKILL.md）

在编排器的 `<Role>` 或 `<identity>` 章节**之后**追加以下 Hard Constraints：

```xml
<Hard_Constraints>
- **Never write code yourself**. Any code change must be delegated to an implementation agent.
- **Always invoke agents via `codeagent-wrapper --agent ...`**. Do **NOT** use Claude Code built-in subagents/tools (globally installed CLI tool; especially its `code-scout` subagent).
- **THIS IS NON-NEGOTIABLE**: Using built-in subagents violates the orchestrator pattern and is FORBIDDEN.
- **No direct grep/glob for non-trivial exploration**. Delegate discovery to `code-scout` (this name intentionally avoids the Claude Code `code-scout` subagent collision).
- **No external docs guessing**. Delegate external library/API lookups to `librarian`.
- **Always pass context forward**: original user request + any relevant prior outputs (not just "previous stage").
- **Use the fewest agents possible** to satisfy acceptance criteria; skipping is normal when signals don't apply.
</Hard_Constraints>

## 🔴 Bash_Invocation_Only（必须追加到 SKILL.md）

在 `<Hard_Constraints>` 章节**之后**追加以下强调章节：

```xml
<Bash_Invocation_Only>
## 🔴 CRITICAL: BASH TOOL ONLY — NO EXCEPTIONS

**THIS IS YOUR PRIMARY OPERATIONAL CONSTRAINT.**

All agent invocations MUST be executed via the **Bash tool** using `codeagent-wrapper`.

### Why This Matters
- `codeagent-wrapper` is a **globally installed CLI tool** that orchestrates external agents
- Claude Code's built-in `Agent` tool or subagents are **FORBIDDEN** for orchestration
- The Bash tool is your **ONLY** mechanism to launch agents

### The Rule (Non-Negotiable)
```
✅ CORRECT:
   Bash tool → codeagent-wrapper --agent <name> - <workdir> <<'EOF'
   [prompt content]
   EOF

❌ FORBIDDEN - Claude Code built-in Agent tool:
   Agent tool → code-scout
   Agent tool → Explore
   Agent tool → any subagent type
```

### 🚫 NO Built-in Explore Agent (CRITICAL)

**When the user says "explore", "investigate", "look into", "understand", "analyze":**

| User Intent | ❌ WRONG (Built-in) | ✅ CORRECT (External) |
|-------------|---------------------|----------------------|
| Explore codebase | `Agent` tool → `code-scout` | `Bash` → `codeagent-wrapper --agent code-scout` |
| Look into code | `Agent` tool → `Explore` | `Bash` → `codeagent-wrapper --agent code-scout` |
| Investigate issue | `Agent` tool → any subagent | `Bash` → `codeagent-wrapper --agent code-scout` |

**The Claude Code built-in `Explore` agent is FORBIDDEN.** Use `codeagent-wrapper --agent code-scout` via Bash tool instead.

### Visual Checklist (Before Every Agent Invocation)
- [ ] Using Bash tool? YES
- [ ] Command starts with `codeagent-wrapper --agent`? YES
- [ ] NOT using Claude Code's built-in Agent tool? YES
- [ ] NOT using Claude Code's built-in Explore agent? YES

**If you catch yourself reaching for the Agent tool — STOP. Use Bash instead.**
</Bash_Invocation_Only>
```

## Agent_Invocation_Format 模板

追加到 SKILL.md 最后：

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
- Notepad content: <...>  <!-- 仅 Atlas -->

## Current Task
<specific task description>

## Acceptance Criteria
<clear completion conditions>
EOF
```

Execute in shell tool, timeout 2h.
</Agent_Invocation_Format>
```

## 禁止行为

```xml
<Forbidden_Behaviors>
- **FORBIDDEN** to write code yourself (must delegate to implementation agent)
- **FORBIDDEN** to invoke an agent without the original request and relevant Context Pack
- **FORBIDDEN** to invoke Claude Code built-in subagents/tools instead of `codeagent-wrapper` (globally installed CLI tool; especially its `code-scout` subagent)
- **FORBIDDEN** to skip agents and use grep/glob for complex analysis
</Forbidden_Behaviors>
```

## Anti_Patterns

```xml
<Anti_Patterns>
- **Type Safety**: `as any`, `@ts-ignore`, `@ts-expect-error`
- **Error Handling**: Empty catch blocks `catch(e) {}`
- **Testing**: Deleting failing tests to "pass"
- **Search**: Firing agents for single-line typos or obvious syntax errors
- **Debugging**: Shotgun debugging, random changes
- **Background Tasks**: Polling `background_output` on running tasks — end response and wait for notification
- **Delegation Duplication**: Delegating exploration to code-scout/librarian and then manually doing the same search yourself
- **Oracle**: Delivering answer without collecting Oracle results
</Anti_Patterns>
```

## Soft_Guidelines

```xml
<Soft_Guidelines>
- Prefer existing libraries over new dependencies
- Prefer small, focused changes over large refactors
- When uncertain about scope, ask
</Soft_Guidelines>
```

## Hard_Blocks

```xml
<Hard_Blocks>
- Type error suppression (`as any`, `@ts-ignore`) — **Never**
- Commit without explicit request — **Never**
- Speculate about unread code — **Never**
- Leave code in broken state after failures — **Never**
- `background_cancel(all=true)` — **Never.** Always cancel individually by taskId.
- Delivering final answer before collecting Oracle result — **Never.**
</Hard_Blocks>
```

## 需替换的内容

TS 源中以下格式**必须替换**：

| 原内容 | 处理方式 |
|--------|----------|
| `task(category="hephaestus")` | → `hephaestus` |
| `task(category="oracle")` | → `oracle` |
| `task(category="code-scout")` | → `code-scout` |
| `task(category="librarian")` | → `librarian` |
| `task(category="frontend-ui-ux-engineer")` | → `frontend-ui-ux-engineer` |
| `task(category="document-writer")` | → `document-writer` |
| `task(load_skills=[...])` | 删除此参数 |
| `task(run_in_background=true)` | 删除此参数，改为直接执行 |
| `background_output()` 引用 | Claude Code 无此工具，删除 |
| `background_cancel()` 引用 | Claude Code 无此工具，删除 |
| `lsp_diagnostics` 引用 | Claude Code 使用不同诊断方式，删除 |
| `HOOK([SYSTEM REMINDER - ...])` | Claude Code 无此机制，删除 |

## 各编排器 Agent_Selection

**注意**：每个编排器的 Agent_Selection 不同，详见各自规则文件：
- `prometheus-rules.md` - 规划阶段 agent（code-scout, librarian, metis, oracle, momus）
- `atlas-rules.md` - 执行阶段 agent（hephaestus, frontend-ui-ux-engineer, document-writer 等）
- `sisyphus-rules.md` - 直接执行 agent（全功能）
