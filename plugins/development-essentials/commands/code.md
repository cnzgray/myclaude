---
description: 由开发协调者主导的功能实现,协同架构师、实现工程师、集成专家与代码审查员,渐进式开发并做质量验证。
disable-model-invocation: true
argument-hint: "<FEATURE_DESCRIPTION>"
allowed-tools: Task Read Glob Grep
---

## Context
- Feature/functionality to implement: $ARGUMENTS
- Existing codebase structure and patterns will be referenced using @ file syntax.
- Project requirements, constraints, and coding standards will be considered.

## Execution
Invoke the `code` agent via the Task tool, passing:
- **Feature description**: $ARGUMENTS
- **Relevant file references** (via @file syntax) and project context.

The `code` agent handles requirements analysis, implementation strategy, progressive development, and quality validation. Wait for it to complete, then summarize the implementation plan, code changes, testing strategy, and next actions for the user.
