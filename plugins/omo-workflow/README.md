# omo-workflow - 多代理编排工作流

omo-workflow 是一个多代理编排系统，包含三个独立的 SKILL，覆盖从规划到执行的完整流程。

## 三个 SKILL 的关系

```
用户需求 → /omo-plan (Prometheus) → 计划文件 → /omo-execute (Atlas) → 完成
                ↓
           /omo (Sisyphus) → 直接执行 → 完成
```

| SKILL | 命令 | 职责 | 适用场景 |
|-------|------|------|----------|
| `/omo-plan` | 战略规划 | 访谈用户、咨询 Metis、生成工作计划 | 复杂需求、多模块、需要架构决策 |
| `/omo-execute` | 计划执行 | 读取计划、分配任务、Final Verification Wave | 执行已生成的计划 |
| `/omo` | 直接执行 | 路由到最合适的代理、直接完成任务 | 简单任务、已知位置的单文件修改 |

## 选择指南

| 场景 | 推荐 SKILL |
|------|-----------|
| 简单 bug 修复（已知位置） | `/omo` |
| 简单功能增加（单文件） | `/omo` |
| 复杂需求（多模块、架构决策） | `/omo-plan` → `/omo-execute` |
| 未知位置的 bug | `/omo` (会先探索定位) |
| 需要外部 API 集成 | `/omo-plan` (需要规划) |
| 重构（跨多个模块） | `/omo-plan` → `/omo-execute` |
| UI/UX 修改 | `/omo` 或 `/omo-plan` |
| 文档编写 | `/omo` |

## 目录结构

```
omo-workflow/
├── README.md              # 本文件
├── models.json.sample     # 模型配置示例
├── mcp.json.sample       # MCP 配置示例
├── omo/                  # Sisyphus - 直接执行
│   ├── SKILL.md
│   ├── README.md
│   └── hooks/            # OmO 模式 hooks
├── omo-plan/             # Prometheus - 战略规划
│   ├── SKILL.md
│   └── README.md
├── omo-execute/          # Atlas - 计划执行
│   ├── SKILL.md
│   └── README.md
└── agents/               # 共享的 Agent 参考文档
    ├── code-scout.md
    ├── librarian.md
    ├── oracle.md
    ├── hephaestus.md
    ├── frontend-ui-ux-engineer.md
    ├── document-writer.md
    ├── metis.md
    ├── momus.md
    └── multimodal-looker.md
```

## 安装

```bash
python install.py --module omo
```

## Agent 与 SKILL 的关系

| Agent | 职责 | Cost | omo | omo-plan | omo-execute |
|-------|------|:----:|:---:|:---:|:---:|
| `code-scout` | 代码探索 | FREE | ✅ | ✅ | ✅ |
| `librarian` | 外部文档 | CHEAP | ✅ | ✅ | ✅ |
| `oracle` | 架构咨询 | EXPENSIVE | ✅ | ✅ | ❌ |
| `metis` | 预规划分析 | EXPENSIVE | ❌ | ✅ | ❌ |
| `momus` | 计划验证 | EXPENSIVE | ❌ | ✅ | ✅ |
| `hephaestus` | 代码实现 | EXPENSIVE | ✅ | ❌ | ✅ |
| `frontend-ui-ux-engineer` | UI实现 | - | ✅ | ❌ | ✅ |
| `document-writer` | 文档编写 | - | ✅ | ❌ | ✅ |
| `multimodal-looker` | 媒体解读 | CHEAP | ✅ | ❌ | ❌ |

## 核心约束

1. **所有代理必须通过 `codeagent-wrapper` 调用**
2. **禁止自己写实现代码**（编排器只负责路由）
3. **必须传递完整上下文**
4. **使用最少够用的代理**

## 依赖要求

- `codeagent-wrapper`，并且支持 `--agent`
- 后端 CLI：`claude`、`opencode`、`codex`、`gemini`
