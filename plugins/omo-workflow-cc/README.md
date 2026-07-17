# omo-workflow-cc — 多代理编排工作流（纯 Claude Code 原生 subagent 版）

本插件是 `omo-workflow` 的**纯 Claude Code 原生版本**：完全使用原生 `Task` 工具 + `agents/*.md` subagent 定义，**不依赖 `codeagent-wrapper`、`models.json`、`routing_table.json` 或任何拦截 hook**。

> 需要外部 CLI 后端路由的原版请用 marketplace 中的 `omo` / `omo-opus` / `omo-kimi`（plugins/omo-workflow）。二者可共存。

## 三个 SKILL 的关系

```
用户需求 → /omo-plan (Prometheus) → 计划文件 → /omo-execute (Atlas) → 完成
                ↓
           /omo (Sisyphus) → 直接执行 → 完成
```

| SKILL | 职责 | 适用场景 |
|-------|------|----------|
| `/omo-plan` | 访谈用户、咨询 metis/oracle、生成工作计划到 `.omo/plans/*.md` | 复杂需求、多模块、需要架构决策 |
| `/omo-execute` | 读取计划、并行委派任务、Final Verification Wave | 执行已生成的计划 |
| `/omo` | 路由到最合适的 subagent、直接完成任务 | 简单任务、已知位置的单文件修改 |

## 选择指南

| 场景 | 推荐 SKILL |
|------|-----------|
| 简单 bug 修复（已知位置） | `/omo` |
| 简单功能增加（单文件） | `/omo` |
| 复杂需求（多模块、架构决策） | `/omo-plan` → `/omo-execute` |
| 未知位置的 bug | `/omo`（会先探索定位） |
| 重构（跨多个模块） | `/omo-plan` → `/omo-execute` |
| UI/UX 修改 | `/omo` 或 `/omo-plan` |
| 文档编写 | `/omo` |

## 目录结构

```
omo-workflow-cc/
├── .claude-plugin/
│   └── plugin.json               # 插件元数据（name/description/author）；组件靠自动发现
├── README.md
├── agents/                       # 10 个原生 subagent（带 YAML frontmatter）
│   ├── code-scout.md             # 代码探索（只读）
│   ├── librarian.md              # 外部文档/OSS（只读）
│   ├── oracle.md                 # 架构/调试咨询（只读）
│   ├── metis.md                  # 预规划分析（只读）
│   ├── momus.md                  # 计划审查（只读）
│   ├── hephaestus.md             # 深度实现
│   ├── frontend-ui-ux-engineer.md# UI/视觉实现
│   ├── document-writer.md        # 文档写作
│   ├── multimodal-looker.md      # 媒体解读
│   └── sisyphus-junior.md        # 快速执行
└── skills/
    ├── omo/SKILL.md              # Sisyphus — 直接执行编排器
    ├── omo-plan/SKILL.md         # Prometheus — 战略规划
    ├── omo-execute/SKILL.md      # Atlas — 计划执行
    ├── frontend-ui-ux/SKILL.md   # 内置技能：前端方法论
    ├── playwright/SKILL.md       # 内置技能：浏览器 E2E/QA
    ├── git-master/SKILL.md       # 内置技能：Git 规范
    └── dev-browser/SKILL.md      # 内置技能：DevTools 调试
```

## 内置技能（bundled skills）

原版通过 `task.py` 把 `hooks/skills/*.md` 片段按 `load_skills` 注入 subagent prompt；本版把它们做成**真正的插件技能**，由具备 `Skill` 工具的实现类 subagent 按需 `Skill()` 加载：

| 技能 | 内容 | 主要使用者 |
|------|------|-----------|
| `frontend-ui-ux` | 原子设计、设计 token、可访问性(WCAG AA)、响应式、BEM | `frontend-ui-ux-engineer`（视觉任务默认加载） |
| `playwright` | E2E/浏览器 QA：Page Object、role/text 定位器、web-first 断言、证据截图 | 浏览器 QA（hephaestus/frontend） |
| `git-master` | Conventional Commits、分支命名、干净历史 | 提交相关任务 |
| `dev-browser` | Chrome DevTools：Elements/Console/Network/Performance、Lighthouse、source maps | 浏览器运行时/性能调试 |

> `frontend-ui-ux-engineer`、`hephaestus`、`document-writer`、`sisyphus-junior` 的 frontmatter `tools` 含 `Skill`，可加载上述技能。只读咨询类(code-scout/oracle/metis/momus/librarian)不加载。
> 对应原版 `visual-engineering` category 的 `default_skills:["frontend-ui-ux"]`：本版由编排器在路由视觉任务时提示 `frontend-ui-ux-engineer` 默认加载 `frontend-ui-ux` 技能。

## Subagent 与 SKILL 的关系

| Subagent | 职责 | Cost / Model | omo | omo-plan | omo-execute |
|----------|------|:---:|:---:|:---:|:---:|
| `code-scout` | 代码探索 | FREE / haiku | ✅ | ✅ | ✅ |
| `librarian` | 外部文档 | CHEAP / haiku | ✅ | ✅ | ✅ |
| `oracle` | 架构咨询 | fable | ✅ | ✅ | ✅(F1) |
| `metis` | 预规划分析 | sonnet | ❌ | ✅ | ❌ |
| `momus` | 计划验证 | fable | ✅ | ✅ | ✅ |
| `hephaestus` | 深度实现 | opus | ✅ | ❌ | ✅ |
| `frontend-ui-ux-engineer` | UI 实现 | sonnet | ✅ | ❌ | ✅ |
| `document-writer` | 文档编写 | sonnet | ✅ | ❌ | ✅ |
| `sisyphus-junior` | 快速执行 | opus | ✅ | ❌ | ✅ |
| `multimodal-looker` | 媒体解读 | sonnet | ✅ | ❌ | ✅ |

## 模型档位映射（env 别名）

agent 文件**不写模型名**，全部使用 Claude Code 档位别名（`fable`/`opus`/`sonnet`/`haiku`），通过环境变量把别名映射到真实模型。切换模型只改 env，agent 定义不动。

| 档位别名 | 映射模型 | 用途 | subagent |
|---------|---------|------|----------|
| `fable` | kimi k3 | 主编排（主会话）+ 咨询决策 | 主会话 / oracle / momus |
| `sonnet` | kimi k3 | 辅助实现 + 写作 + 媒体 | frontend-ui-ux-engineer / metis / document-writer / multimodal-looker |
| `opus` | glm-5.2 | 代码实现核心 | hephaestus / sisyphus-junior |
| `haiku` | 便宜模型 | 高频只读探索 | code-scout / librarian |

`fable` 与 `sonnet` 都映射 kimi k3：主会话无论选哪个档位都恒为 kimi k3；`opus` 独占 glm-5.2，实现类 subagent 不与编排撞模型。

### 配置 env（安装步骤）

插件无法自带 env（Claude Code 插件 `settings.json` 仅支持 `agent`/`subagentStatusLine` 键），请把以下加入 `~/.claude/settings.json` 的 `env` 块：

```json
{
  "env": {
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "k3[1M]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "k3[1M]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-5.2[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "MiniMax-M3[1M]"
  },
  "model": "fable"
}
```

- `"model": "fable"` 锁定主会话档位，确保主编排恒为 kimi k3；勿切到 `opus`，否则主会话变 glm-5.2。
- `[1m]`/`[1M]` 是 1M 上下文窗口后缀，Claude Code 剥离后发给网关。官方仅记录小写 `[1m]`，大写按网关实际认的来。
- 模型 ID（`k3`/`glm-5.2`/`MiniMax-M3`）替换为你网关的实际 ID。

## category → subagent 映射

原版用 `category` 选择领域优化模型；本版直接按域选 subagent：

| 原 category | 原生 subagent |
|-------------|---------------|
| `visual-engineering` | `frontend-ui-ux-engineer` |
| `deep` / `ultrabrain` / `artistry` / `unspecified-high` | `hephaestus` |
| `quick` / `unspecified-low` | `sisyphus-junior` |
| `writing` | `document-writer` |
| `explore`（旧别名） | `code-scout` |

## 核心约束

1. **所有实现工作通过原生 `Task` 工具委派给 subagent**（编排器只负责路由与验证，自己不写实现代码）
2. **subagent 是叶子节点，不能再派生 subagent** —— 所有编排（并行探索、oracle 咨询、Final Verification Wave）只发生在 SKILL 主循环层
3. **必须传递完整上下文**（6 段式委派 prompt）
4. **使用最少够用的 subagent，按域匹配**
5. **续接同一 subagent 用 `SendMessage`**（保留上下文），后台结果用 `TaskOutput` 收集

## 依赖要求

- 仅需 Claude Code 原生能力（Task / SendMessage / TaskOutput / Skill）。
- 无需 `codeagent-wrapper`，无需 `~/.codeagent/models.json` 或 `routing_table.json`，无需任何 hook。

## 与原版的差异

| 方面 | omo-workflow（原版） | omo-workflow-cc（本版） |
|------|----------------------|--------------------------|
| 委派机制 | `task()` → hook 拦截 → `task.py` → `codeagent-wrapper` | 原生 `Task(subagent_type=...)` |
| 模型路由 | `routing_table.json` + `models.json` + 外部 CLI | 每个 `agents/*.md` 的 `model:` frontmatter |
| 后台/续接 | `bg_...` / `background_output` / `ses_...` | `run_in_background` + `TaskOutput` + `SendMessage` |
| 技能注入 | `load_skills=[...]` 注入 prompt | 由 subagent 用 Skill 工具按需加载 |
| hooks | `agent_guard.py`（拦截 Agent）+ 上下文注入 | 无 hook |
| 计划交接 | `/start-work` | `/omo-execute` |
