---
description: 由单个 code 在同一上下文完成范围分析、行为不变量、小步重构与测试,再由 change-verifier 独立验证。
disable-model-invocation: true
argument-hint: "<REFACTOR_SCOPE>"
allowed-tools: Task TaskOutput SendMessage
---

## Input

- Refactoring target and scope: `$ARGUMENTS`
- Treat constraints, acceptance criteria, and referenced files from the conversation as binding.
- Preserve externally observable behavior unless the user explicitly requests a behavior change.

## Orchestration Rules

- This command is the only orchestration layer. `code` is the implementation leaf and `change-verifier` is the independent validation leaf; neither may delegate.
- Use only the native protocol: `Task(subagent_type="...", run_in_background=..., description="...", prompt="...")`, `TaskOutput`, and `SendMessage(to="...", summary="...", message="...")`.
- Use exactly one `code` context for scope analysis, implementation, testing, and every correction. Do not split analysis from implementation or start a replacement implementation agent.
- The verification gate is blocking. Never claim completion from the implementation report alone.

## Workflow

### 1. Analyze, implement, and test in one context

Start one background implementation task:

`Task(subagent_type="code", run_in_background=true, description="Analyze and implement behavior-preserving refactor", prompt="[CHANGE TYPE] Refactor. [TARGET] $ARGUMENTS. [CONSTRAINTS] Include every applicable instruction and acceptance criterion from the conversation. [REQUEST] In this single context, first resolve the exact files and symbols, trace callers, dependents, data flow, and public boundaries, state evidence-backed behavior invariants, locate existing tests, map invariants to coverage or gaps, discover the relevant commands, and run the narrow baseline. Then implement the smallest behavior-preserving transformation in coherent steps, running a focused checkpoint after each meaningful step and the relevant final tests. Update every affected caller and remove obsolete paths; do not leave aliases or compatibility shims. If ambiguity makes the transformation unsafe, stop before editing and report it. [OUTPUT] Resolved scope and call relationships; behavior invariants; test baseline and actual result; changed files; numbered implementation steps with protected invariant and checkpoint result; justified deviations; every command run with exit status and meaningful output; remaining blockers. Do not delegate.")`

Record its task ID as `<code-task-id>` and agent ID as `<code-agent-id>`. Collect it with `TaskOutput(task_id="<code-task-id>", block=true, timeout=300000)`. Do not open the gate unless the result includes the resolved scope, behavior invariants, changed files, and actual baseline/checkpoint/final command evidence or a concrete execution blocker.

### 2. Enforce the verification gate

Start one independent verifier and retain both its task ID and agent ID:

`Task(subagent_type="change-verifier", run_in_background=true, description="Verify refactor invariants", prompt="[TARGET] $ARGUMENTS. [ACCEPTANCE] <conversation acceptance criteria plus the behavior invariants reported by code>. [CHANGED FILES] <exact code changed-file list>. [REPRODUCTION OR TEST COMMANDS] <baseline, checkpoint, and final commands reported by code>. [REQUEST] Inspect the actual files and independently run the relevant commands. Confirm the resolved scope and callers were handled, every invariant remains true, no obsolete path or compatibility shim remains, and the requested structural outcome is complete. Return exactly PASS or FAIL as the verdict, followed by concrete command output and file evidence. FAIL must list each actionable mismatch.")`

Record its task ID as `<verifier-task-id>` and agent ID as `<verifier-agent-id>`. Collect it with `TaskOutput(task_id="<verifier-task-id>", block=true, timeout=300000)`. PASS is the only successful terminal state.

### 3. Correct failures without losing context

On `FAIL`, call `SendMessage(to="<code-agent-id>", summary="Correct failed code refactor", message="[VERIFIER EVIDENCE] <complete failure evidence>. [REQUIRED CORRECTIONS] <every actionable mismatch>. Continue from the existing refactor context, correct every item without changing the protected behavior, rerun the affected checkpoints and final tests, and return the updated changed files and actual command evidence. Do not delegate.")`. Do not start a fresh implementation task.

After the completion notification, collect the continuation with `TaskOutput(task_id="<code-task-id>", block=true, timeout=300000)` and update the scope, invariant, changed-file, and command handoff. Then call `SendMessage(to="<verifier-agent-id>", summary="Recheck corrected code refactor", message="Inspect the updated files and rerun the full verification gate with this evidence: <updated code handoff>.")` and collect it with `TaskOutput(task_id="<verifier-task-id>", block=true, timeout=300000)`.

Allow at most **two correction attempts** after the initial implementation. Each `SendMessage` continuation of `code` counts as one correction attempt. Stop immediately on PASS. If verification still returns FAIL after the second correction, report the failed gate and remaining evidence; do not describe the refactor as complete.

## Final Output

Report the resolved scope and call relationships, protected behavior invariants, behavior-preserving changes, changed files, baseline/checkpoint/final commands with actual outcomes, correction count, and the verifier's final PASS/FAIL evidence. Omit speculative follow-up work.
