---
description: 由 code 叶节点实施功能,再由 change-verifier 独立验证,失败时续接原实施任务并限次纠正。
disable-model-invocation: true
argument-hint: "<FEATURE_DESCRIPTION>"
allowed-tools: Task TaskOutput SendMessage
---

## Context
- Feature/functionality to implement: $ARGUMENTS
- The command is the only orchestration layer. The `code` agent is a leaf implementer; it does not delegate to other agents.
- Preserve the repository's existing patterns and keep the change limited to the requested behavior.

## Execution

### 1. Implement
Start one background implementation task:

```text
Task(subagent_type="code", run_in_background=true, description="Implement the requested feature", prompt="[TARGET] $ARGUMENTS\n[REQUEST] Analyze the existing code and its established patterns, implement the requested behavior, and run the relevant reproduction or test commands. Do not delegate. Report the changed files, implementation decisions, exact commands run, and observed results; never claim a command was run when it was not.")
```
Record both the returned task ID (for `TaskOutput`) and agent ID (for `SendMessage`).

Collect the completed implementation with:

```text
TaskOutput(task_id="<code-task-id>", block=true, timeout=300000)
```

### 2. Verify
After implementation completes, start one background verifier task. Pass all four required inputs from the implementation result and the request:

```text
Task(subagent_type="change-verifier", run_in_background=true, description="Verify the implementation", prompt="[TARGET] $ARGUMENTS\n[ACCEPTANCE CONDITIONS] Derive and list the observable acceptance conditions from the request.\n[CHANGED FILES] <exact files reported by the code task>\n[REPRODUCTION OR TEST COMMAND] <exact command reported by the code task>\n[REQUEST] Read the changed files, run the supplied reproduction or test command, and independently check every acceptance condition. Return exactly PASS or FAIL with concrete observed evidence, including command output or the reason a condition failed.")
```

Collect the verifier result with `TaskOutput(task_id="<verifier-task-id>", block=true, timeout=300000)`. A verifier result is successful only when it is `PASS` and includes actual evidence; treat any `FAIL`, missing evidence, or unparseable result as failure.

### 3. Bounded correction loop
- On `PASS`, report the implementation and verifier evidence and stop.
- On `FAIL`, send the complete verifier findings to the **same** original `code` task; do not start a replacement implementation task:

```text
SendMessage(to="<code-agent-id>", summary="Correct failed implementation", message="[VERIFICATION FAILED] <verifier's concrete evidence and failed acceptance conditions>\n[TARGET] $ARGUMENTS\n[ACTION] Re-inspect the existing patterns, correct the root cause in the current implementation, rerun the relevant reproduction or test command, and report the exact changed files and observed results.")
```

  Then collect that task's continuation with `TaskOutput(task_id="<code-task-id>", block=true, timeout=300000)` and start a new `change-verifier` task with the same four inputs. Count each SendMessage continuation as one correction loop; allow at most two loops. If the second correction still fails, stop and report `FAIL` with all observed evidence rather than starting a third loop.

## Final report
Include the target, files changed, implementation summary, every command actually run and its observed result, verifier `PASS`/`FAIL`, and (if applicable) the correction-loop count and remaining failure evidence.
