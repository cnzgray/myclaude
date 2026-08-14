---
description: 使用系统性深度分析方法调试复杂问题,多代理协同、假设收敛与证据驱动的根因分析。
disable-model-invocation: true
argument-hint: "<TASK_DESCRIPTION>"
allowed-tools: Task Read Glob Grep Bash
---

# Debug Orchestrator

## Context
- Task description: $ARGUMENTS
- Relevant code or files will be referenced from the conversation.
- Focus: Problem-solving through systematic analysis and multi-agent coordination.

## Execution
Delegate to the `debug` agent, passing:
- **Task description**: $ARGUMENTS
- **Relevant file references** and any error logs/stack traces from the conversation.

The `debug` agent runs the full systematic methodology (hypothesis generation, multi-agent coordination, user confirmation, evidence-based validation). Wait for it to complete, then present the diagnosis, fix, and validation results to the user, and follow up on any user confirmation the agent requested.
