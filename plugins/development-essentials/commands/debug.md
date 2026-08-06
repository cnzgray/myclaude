---
description: 使用 UltraThink 方法系统性调试复杂问题,多代理协同、假设收敛与证据驱动的根因分析。
disable-model-invocation: true
argument-hint: "<TASK_DESCRIPTION>"
allowed-tools: Task Read Glob Grep Bash
---

# UltraThink Debug Orchestrator

## Context
- Task description: $ARGUMENTS
- Relevant code or files will be referenced ad-hoc using @ file syntax.
- Focus: Problem-solving through systematic analysis and multi-agent coordination.

## Execution
Invoke the `debug` agent via the Task tool, passing:
- **Task description**: $ARGUMENTS
- **Relevant file references** (via @file syntax) and any error logs/stack traces.

The `debug` agent runs the full UltraThink methodology (hypothesis generation, multi-agent coordination, user confirmation, evidence-based validation). Wait for it to complete, then present the diagnosis, fix, and validation results to the user, and follow up on any user confirmation the agent requested.
