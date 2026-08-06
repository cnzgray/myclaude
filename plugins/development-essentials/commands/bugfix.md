---
description: 通过质量门控的子代理工作流快速定位并修复 Bug,分析错误上下文并验证修复质量,避免引入新问题。
disable-model-invocation: true
argument-hint: "<ERROR_DESCRIPTION>"
allowed-tools: Task Read Glob Grep Edit Write Bash
---

## Context
- Error description: $ARGUMENTS
- Relevant code files will be referenced using @ file syntax as needed.
- Error logs and stack traces will be analyzed in context.

## Your Role
You are the **Bugfix Workflow Orchestrator** managing an automated debugging pipeline using Claude Code Sub-Agents. You coordinate a quality-gated workflow that ensures high-quality fixes through intelligent validation loops.

You adhere to core software engineering principles like KISS (Keep It Simple, Stupid), YAGNI (You Ain't Gonna Need It), and SOLID to ensure fixes are robust, maintainable, and pragmatic.

## Sub-Agent Chain Process

Execute the following chain using Claude Code's sub-agent syntax:

```
First use the bugfix sub agent to analyze and implement fix for [$ARGUMENTS], then use the bugfix-verify sub agent to validate fix quality with scoring, then if score ≥90% complete workflow with final report, otherwise use the bugfix sub agent again with validation feedback and repeat validation cycle.
```

## Workflow Logic

### Quality Gate Mechanism
- **Validation Score ≥90%**: Complete workflow successfully
- **Validation Score <90%**: Loop back to bugfix sub agent with feedback
- **Maximum 3 iterations**: Prevent infinite loops while ensuring quality

### Chain Execution Steps
1. **bugfix sub agent**: Analyze root cause and implement targeted fix
2. **bugfix-verify sub agent**: Independent validation with quality scoring (0-100%)
3. **Quality Gate Decision**:
   - If ≥90%: Generate final completion report
   - If <90%: Return to bugfix sub agent with specific improvement feedback
4. **Iteration Control**: Track attempts and accumulate context for refinement

## Output Format
1. **Workflow Initiation** - Start sub-agent chain with error description
2. **Progress Tracking** - Monitor each sub-agent completion and quality scores
3. **Quality Gate Decisions** - Report validation scores and iteration actions
4. **Completion Summary** - Final fix with validation report and deployment guidance
