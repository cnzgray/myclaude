# Claude Code Marketplace

个人 Claude Code 插件市场。

## 快捷配置

在 `~/.claude/settings.json` 中添加以下内容：

```json
{
  "enabledPlugins": {
    "cexll@cnzgray-marketplace": true,
    "zcf@cnzgray-marketplace": true
  },
  "extraKnownMarketplaces": {
    "cnzgray-marketplace": {
      "source": {
        "source": "github",
        "repo": "cnzgray/myclaude"
      }
    }
  },
  "outputStyle": "cexll-essentials:Linus Torvalds"
}
```

在 `~/.codeagent/models.json` 中添加默认配置：

```json
{
  "default_backend": "codex",
  "default_model": "gpt-5.2",
  "agents": {
    "code-explorer": {
      "backend": "claude",
      "model": "claude-sonnet-4-5-20250929",
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/do/agents/code-explorer.md"
    },
    "code-reviewer": {
      "backend": "claude",
      "model": "claude-sonnet-4-5-20250929",
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/do/agents/code-reviewer.md"
    },
    "code-architect": {
      "backend": "claude",
      "model": "claude-sonnet-4-5-20250929",
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/do/agents/code-architect.md"
    },
    "develop": {
      "backend": "codex",
      "model": "gpt-5.2",
      "yolo": true,
      "reasoning": "xhigh",
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/omo/references/develop.md"
    },
    "explore": {
      "backend": "opencode",
      "model": "opencode/grok-code",
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/omo/references/explore.md"
    },
    "oracle": {
      "backend": "claude",
      "model": "claude-opus-4-5-20251101",
      "yolo": true,
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/omo/references/oracle.md"
    },
    "librarian": {
      "backend": "claude",
      "model": "claude-sonnet-4-5-20250929",
      "yolo": true,
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/omo/references/librarian.md"
    },
    "frontend-ui-ux-engineer": {
      "backend": "gemini",
      "model": "gemini-3-pro-preview",
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/omo/references/frontend-ui-ux-engineer.md"
    },
    "document-writer": {
      "backend": "gemini",
      "model": "gemini-3-flash-preview",
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/omo/references/document-writer.md"
    }
  }
}
```

## 插件列表

### 全功能插件

- **cexll** `v6.3.1` - All in One，集成所有开发命令、agents 和 skills
  - 依赖：需从 [cexll/myclaude releases](https://github.com/cexll/myclaude/releases) 安装 `codeagent-wrapper` 到 `~/.claude/bin/`
  - 推荐：配合原生 [Codex](https://github.com/openai/codex) 或 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 使用效果更佳
- **zcf** `v3.5.1` - Git 实用工具（commit、worktree、分支清理、rollback）

### 独立插件

- **cexll-essentials** `v6.3.1` - 核心开发命令和工具（debug、bugfix、optimize、code、review 等）
- **cexll-dev** `v6.3.1` - 轻量级开发工作流，依赖 `codeagent-wrapper`
- **dev-subagent** `v0.1.0` - 开发工作流（subagent 版本），不依赖 `codeagent-wrapper`

### Skills 插件

- **cexll-skills** `v6.3.1` - 全部 Agent Skills（codeagent、do、omo），依赖 `codeagent-wrapper`
- **cexll-codeagent** `v6.3.1` - CodeAgent Skill，依赖 `codeagent-wrapper`
- **cexll-do** `v6.3.1` - 结构化特性开发工作流，依赖 `codeagent-wrapper`
- **cexll-omo** `v6.3.1` - OmO 多代理编排器，依赖 `codeagent-wrapper`

### 第三方插件

- **vue-skills** - Agent skills for Vue 3 development（来源：[hyf0/vue-skills](https://github.com/hyf0/vue-skills)）
- **vueuse-skills** - Agent Skills for VueUse（来源：[vueuse/skills](https://github.com/vueuse/skills)）

## codeagent-wrapper 安装与使用

多数插件依赖 `codeagent-wrapper`，它是一个 CLI 工具，用于将任务分发给不同的 AI 后端执行。

### 安装

从 [cexll/myclaude releases](https://github.com/cexll/myclaude/releases) 下载对应平台的二进制文件，放入 `~/.claude/bin/`：

```bash
# macOS (Apple Silicon)
curl -L -o ~/.claude/bin/codeagent-wrapper \
  https://github.com/cexll/myclaude/releases/latest/download/codeagent-wrapper-darwin-arm64
chmod +x ~/.claude/bin/codeagent-wrapper

# macOS (Intel)
curl -L -o ~/.claude/bin/codeagent-wrapper \
  https://github.com/cexll/myclaude/releases/latest/download/codeagent-wrapper-darwin-amd64
chmod +x ~/.claude/bin/codeagent-wrapper

# Linux (amd64)
curl -L -o ~/.claude/bin/codeagent-wrapper \
  https://github.com/cexll/myclaude/releases/latest/download/codeagent-wrapper-linux-amd64
chmod +x ~/.claude/bin/codeagent-wrapper
```

### 支持的后端

| 后端             | 标识       | 说明                                 |
| ---------------- | ---------- | ------------------------------------ |
| OpenAI Codex     | `codex`    | 默认后端                             |
| Anthropic Claude | `claude`   | Claude CLI                           |
| Google Gemini    | `gemini`   | Gemini CLI                           |
| OpenCode         | `opencode` | OpenCode CLI（默认模型 `grok-code`） |

推荐安装原生 [Codex](https://github.com/openai/codex) 或 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 以获得最佳效果。

### 核心参数

| 参数               | 说明                                    |
| ------------------ | --------------------------------------- |
| `--backend <name>` | 选择 AI 后端（codex / claude / gemini） |
| `--parallel`       | 并行执行模式                            |
| `--full-output`    | 输出完整结果（默认为摘要模式）          |
| `--agent <name>`   | 指定执行 agent                          |

### 环境变量

| 变量                             | 说明                     |
| -------------------------------- | ------------------------ |
| `CODEX_TIMEOUT`                  | 超时时间（默认 2 小时）  |
| `CODEAGENT_SKIP_PERMISSIONS`     | 跳过 Claude CLI 权限检查 |
| `CODEAGENT_MAX_PARALLEL_WORKERS` | 并行任务数上限           |

### Agent 模型配置

创建 `~/.codeagent/models.json` 配置 agent 与后端/模型的映射。

**完整结构：**

```json
{
  "default_backend": "codex",
  "default_model": "gpt-5.2",
  "backends": {
    "codex": { "base_url": "", "api_key": "sk-..." },
    "claude": { "base_url": "", "api_key": "sk-ant-..." }
  },
  "agents": {
    "develop": {
      "backend": "codex",
      "model": "o3",
      "prompt_file": "~/.codeagent/prompts/develop.md",
      "description": "核心开发 agent",
      "reasoning": "high",
      "yolo": true
    },
    "code-explorer": {
      "backend": "opencode",
      "model": "opencode/grok-code"
    },
    "code-reviewer": {
      "backend": "claude",
      "model": "claude-sonnet-4-20250514"
    },
    "code-architect": {
      "backend": "gemini",
      "model": "gemini-2.5-pro"
    }
  }
}
```

**顶层字段：**

| 字段              | 类型   | 必填 | 说明                                              |
| ----------------- | ------ | ---- | ------------------------------------------------- |
| `default_backend` | string | 是   | 默认后端（codex / claude / gemini / opencode）    |
| `default_model`   | string | 是   | 默认模型名称                                      |
| `backends`        | object | 否   | 后端级别的 base_url 和 api_key 配置               |
| `agents`          | object | 是   | agent 预设，映射 agent 名称到后端/模型/提示词配置 |

**Agent 配置字段：**

| 字段          | 类型    | 必填 | 说明                                                             |
| ------------- | ------- | ---- | ---------------------------------------------------------------- |
| `backend`     | string  | 是   | 使用的后端（覆盖 default_backend）                               |
| `model`       | string  | 是   | 使用的模型（覆盖 default_model）                                 |
| `prompt_file` | string  | 否   | 自定义提示词文件路径（支持 `~/` 展开），详见下方内置 prompt 列表 |
| `description` | string  | 否   | agent 描述                                                       |
| `yolo`        | boolean | 否   | YOLO 模式，跳过确认（默认 false）                                |
| `reasoning`   | string  | 否   | 推理强度（后端相关，如 `"high"`）                                |
| `base_url`    | string  | 否   | API 地址覆盖（优先于 backends 配置）                             |
| `api_key`     | string  | 否   | API Key 覆盖（优先于 backends 配置）                             |

**动态 Agent：** 在 `~/.codeagent/agents/<name>.md` 放置提示词文件即可自动注册 agent，无需在 models.json 中显式声明，将使用 `default_backend` 和 `default_model`。

**解析优先级：** agents 配置 > 动态 agent 文件 > default_backend / default_model。Agent 级别的 `base_url` / `api_key` 覆盖 backends 级别配置。

**内置 Prompt 文件：** 安装 cexll 插件后，prompt 文件位于插件缓存目录下，可直接用于 `prompt_file` 配置：

配置示例：

```json
{
  "agents": {
    "code-architect": {
      "backend": "gemini",
      "model": "gemini-2.5-pro",
      "prompt_file": "~/.claude/plugins/cache/cnzgray-marketplace/cexll/6.3.1/cexll-skills/skills/do/agents/code-architect.md"
    }
  }
}
```

## Output Styles

可用的输出风格（配置到 `outputStyle` 字段）：

| Style                             | 说明                                           |
| --------------------------------- | ---------------------------------------------- |
| `cexll-essentials:Linus Torvalds` | Linus Torvalds 风格，技术直接、KISS/YAGNI 原则 |
| `zcf:engineer-professional.cn`    | 专业工程师风格（中文）                         |
| `zcf:engineer-professional.en`    | 专业工程师风格（英文）                         |
| `zcf:laowang-engineer.cn`         | 老王工程师风格（中文）                         |
| `zcf:laowang-engineer.en`         | 老王工程师风格（英文）                         |
| `zcf:linus-torvalds.cn`           | Linus Torvalds 风格（中文）                    |
| `zcf:linus-torvalds.en`           | Linus Torvalds 风格（英文）                    |
| `zcf:nekomata-engineer.cn`        | 猫又工程师风格（中文）                         |
| `zcf:nekomata-engineer.en`        | 猫又工程师风格（英文）                         |
| `zcf:ojousama-engineer.cn`        | 大小姐工程师风格（中文）                       |
| `zcf:ojousama-engineer.en`        | 大小姐工程师风格（英文）                       |
