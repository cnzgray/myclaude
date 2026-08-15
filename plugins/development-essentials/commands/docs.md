---
description: 委派 docs-writer 根据实际代码为指定范围编写适用文档。
disable-model-invocation: true
argument-hint: "<CODE_SCOPE_DESCRIPTION>"
allowed-tools: Task
---

Delegate the complete request exactly once:

`Task(subagent_type="docs-writer", run_in_background=false, description="Document requested code scope", prompt="[SCOPE] $ARGUMENTS. [CONTEXT] Include relevant file references, intended audience, documentation location, constraints, and requested document types from the conversation. Read the implementation and write only the applicable documentation. Ground every symbol, command, configuration value, and example in the repository; run relevant documentation checks or scoped commands and report exact results.")`

Return the `docs-writer` result. Do not create additional agents, inspect the code independently, or edit documentation in the command layer.
