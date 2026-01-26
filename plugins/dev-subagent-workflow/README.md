# /dsub - Subagent Dev Workflow（不依赖 codeagent-wrapper）

## 目标

在 `plugins/dev-workflow` 的流程基础上，提供一个**纯 subagent** 的轻量级端到端开发工作流：
- 不调用 `codeagent-wrapper`
- 通过 `Task` 工具调度多个 agent（分析 / 产出计划 / 执行实现与测试）

## 流程

```
/dsub 触发
  ↓
AskUserQuestion（需求澄清 + feature_name）
  ↓
dsub-analysis（子代理：代码库探索 + 任务拆分 + UI 判断）
  ↓
dsub-plan-generator（子代理：生成 dev-plan.md）
  ↓
用户确认
  ↓
dsub-task-worker（子代理：按依赖分层并行实现 + 测试 + 覆盖率）
  ↓
完成总结
```

## 使用

```bash
/dsub "实现邮箱+密码登录，并返回 JWT"
```

## 输出

```
.claude/specs/{feature_name}/
└── dev-plan.md
```

## 目录结构

```
dev-subagent-workflow/
├── README.md
├── commands/
│   └── dsub.md
└── agents/
    ├── dsub-analysis.md
    ├── dsub-plan-generator.md
    └── dsub-task-worker.md
```
