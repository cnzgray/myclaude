---
description: 协同四位优化专家识别并优化性能瓶颈,建立性能基线、改进算法复杂度并设计扩展策略。
disable-model-invocation: true
argument-hint: "<PERFORMANCE_TARGET>"
allowed-tools: Task Read Glob Grep
---

## Context
- Performance target/bottleneck: $ARGUMENTS
- Relevant code and profiling data will be referenced from the conversation.
- Current performance metrics and constraints will be analyzed.

## Execution
Delegate to the `optimize` agent, passing:
- **Performance target**: $ARGUMENTS
- **Relevant file references** and profiling data from the conversation.

The `optimize` agent handles baseline measurement, bottleneck analysis, solution design, and impact validation. Wait for it to complete, then summarize the performance analysis, optimization strategy, implementation plan, and measurement framework for the user.
