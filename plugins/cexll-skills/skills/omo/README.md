# omo - 多代理编排

OmO 是一个多代理编排 skill，会根据任务风险和信息缺口，把请求路由给最合适的专用代理，而不是固定走一条流水线。

## 安装

```bash
python install.py --module omo
```

## 用法

```text
/omo <你的任务>
```

用户显式输入 `/omo` 后，会进入当前会话的 OmO 模式。后续同一会话中的普通提问会继续优先使用 OmO 的路由策略，直到会话状态过期或被清理。

## 代理层级

| 代理 | 角色 | 后端 | 模型 |
|-------|------|------|------|
| `oracle` | 技术顾问，处理高风险决策 | claude | claude-opus-4-5 |
| `librarian` | 外部资料检索 | claude | claude-sonnet-4-5 |
| `repo-explore` | 代码库搜索与定位 | opencode | grok-code |
| `develop` | 代码实现 | codex | gpt-5.2 |
| `frontend-ui-ux-engineer` | UI / UX 专项实现 | gemini | gemini-3-pro |
| `document-writer` | 文档编写 | gemini | gemini-3-flash |

## 路由信号

这个 skill 以“路由优先”为核心，不要求必须经过固定阶段。

| 信号 | 增加的代理 |
|------|-----------|
| 代码位置或行为不清楚 | `repo-explore` |
| 外部库 / API 用法不清楚 | `librarian` |
| 变更风险较高（多文件、公共 API、安全、性能） | `oracle` |
| 需要落地实现 | `develop` / `frontend-ui-ux-engineer` |
| 需要补文档 | `document-writer` |

### 跳过规则

- 已知精确文件路径和行号时，可以跳过 `repo-explore`
- 变更范围局部且风险低时，可以跳过 `oracle`
- 用户只要分析、不要求落地时，可以跳过实现代理

## 常见编排模式

| 任务 | 推荐编排 |
|------|---------|
| 解释代码 | `repo-explore` |
| 已知位置的小修复 | 直接 `develop` |
| 位置未知的缺陷修复 | `repo-explore → develop` |
| 跨模块重构 | `repo-explore → oracle → develop` |
| 接入外部 API | `repo-explore + librarian → oracle → develop` |
| 纯 UI 修改 | `repo-explore → frontend-ui-ux-engineer` |
| 纯文档修改 | `repo-explore → document-writer` |

## 上下文包模板

每次调用代理时都应包含以下结构：

```text
## Original User Request
<原始用户请求>

## Context Pack
- Explore output: <...>
- Librarian output: <...>
- Oracle output: <...>
- Known constraints: <测试要求、时间预算、仓库约定等>

## Current Task
<当前要执行的具体任务>

## Acceptance Criteria
<清晰的完成标准>
```

如果某一项没有内容，写 `None` 即可。

## 代理调用示例

```bash
codeagent-wrapper --agent <agent_name> - <workdir> <<'EOF'
## Original User Request
...

## Context Pack
...

## Current Task
...

## Acceptance Criteria
...
EOF
```

超时时间为 2 小时。

## Hook 机制

OmO 带有一组会话级 hooks，用来维持“当前会话已经进入 OmO 模式”这一状态。它们的作用不是执行编排本身，而是为后续轮次自动补充路由上下文。

### `UserPromptSubmit`

- 当用户输入 `/omo` 时，hook 会将当前会话标记为 OmO 模式
- 状态会写入工作区下的 `.claude/omo/<conversation>.json`
- 在同一会话后续的普通提问里，如果当前仍处于 OmO 模式，hook 会自动注入额外上下文，提醒模型继续优先采用 OmO 路由、尽量选择最少代理，并把前文上下文继续传递下去
- 如果本轮输入本身还是一个命令（以 `/` 开头），则不会额外注入这段上下文

### `SessionStart`

- 当会话恢复、压缩后继续、或重新进入同一会话时，hook 会尝试读取之前保存的 OmO 状态
- 如果状态仍然有效，会补充一条恢复提示，告诉模型该会话之前已经进入 OmO 模式，恢复后仍应延续 OmO 的路由策略
- 同时会刷新状态时间，避免活跃会话中的状态过早过期

### `SessionEnd`

- 会记录最近一次会话结束的原因和时间
- 当结束原因是 `clear` 或 `logout` 时，会直接删除对应的 OmO 状态文件，避免新会话错误继承旧状态
- 其他结束原因不会删除状态，这样下次恢复会话时仍能继续沿用 OmO 模式

### 状态存储与过期

- 状态文件保存在工作区的 `.claude/omo/` 目录下
- 默认过期时间为 12 小时
- 会优先根据 `transcript_path` 识别同一会话；如果没有，则退化为基于 `session_id` 或其他会话信息生成 key

## 示例

```bash
# 只做分析
/omo 这个函数是怎么工作的？
# → repo-explore

# 缺陷修复，但位置未知
/omo 修复认证相关的 bug
# → repo-explore → develop

# 接入外部 API
/omo 增加 Stripe 支付集成
# → repo-explore + librarian → oracle → develop

# UI 修改
/omo 重做 dashboard 布局
# → repo-explore → frontend-ui-ux-engineer
```

## 配置

代理与模型的映射定义在 `~/.codeagent/models.json` 中：

```json
{
  "default_backend": "codex",
  "default_model": "gpt-5.2",
  "agents": {
    "oracle": {
      "backend": "claude",
      "model": "claude-opus-4-5-20251101",
      "yolo": true
    },
    "librarian": {
      "backend": "claude",
      "model": "claude-sonnet-4-5-20250929",
      "yolo": true
    },
    "repo-explore": {
      "backend": "opencode",
      "model": "opencode/grok-code"
    },
    "frontend-ui-ux-engineer": {
      "backend": "gemini",
      "model": "gemini-3-pro-preview"
    },
    "document-writer": {
      "backend": "gemini",
      "model": "gemini-3-flash-preview"
    },
    "develop": {
      "backend": "codex",
      "model": "gpt-5.2",
      "yolo": true,
      "reasoning": "xhigh"
    }
  }
}
```

## 硬性约束

1. 不要自己直接写实现代码，优先委派给实现代理
2. 必须把原始请求和已有上下文持续向后传递
3. 对于非平凡的代码探索，不要直接 `grep/glob`，优先用 `repo-explore`
4. 对外部文档或 API 不要凭经验猜测，优先用 `librarian`
5. 始终使用最少够用的代理，跳过不必要的代理是正常行为

## 依赖要求

- `codeagent-wrapper`，并且支持 `--agent`
- 后端 CLI：`claude`、`opencode`、`codex`、`gemini`
