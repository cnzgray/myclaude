---
description: 按故障面并行收集诊断线索,由 debug 深度复现核实,经命令层确认后交给 code 实施根因修复并由 change-verifier 质量门控。
disable-model-invocation: true
argument-hint: "<TASK_DESCRIPTION>"
allowed-tools: Task TaskOutput SendMessage AskUserQuestion
---

## Context
- Fault or task description: $ARGUMENTS
- The command is the only orchestration layer. `debug-probe` and `debug` are read-only diagnostic leaves; `code` is the implementation leaf; `change-verifier` is the independent validation leaf.
- Preserve existing repository patterns and use only evidence from the supplied files, logs, and commands.

## Execution

### 1. Parallel fault-surface probes
Split the report into the distinct, relevant fault surfaces (for example input/data flow, control flow/state, dependency/configuration, or I/O/concurrency). Start one background `debug-probe` task per surface in the **same batch**; do not serialize independent probes:

```text
Task(subagent_type="debug-probe", run_in_background=true, description="Probe <fault surface>", prompt="[TASK] $ARGUMENTS\n[FAULT SURFACE] <one distinct surface>\n[REQUEST] Read the relevant files and logs and run only safe diagnostic or reproduction commands. Stay read-only. Return root-cause clues in this format: location, hypothesis, concrete evidence, and suggested verification. Do not edit or prescribe a final patch.")
```

Collect every probe in the batch with `TaskOutput(task_id="<probe-task-id>", block=true, timeout=300000)` after its completion notification before dispatching deep diagnosis. Keep each output associated with its fault surface.

### 2. Deep reproduction and diagnosis
Start one background deep-diagnosis task with the task description, all probe outputs, relevant file references, and any reproduction command:

```text
Task(subagent_type="debug", run_in_background=true, description="Reproduce and confirm the root cause", prompt="[TASK] $ARGUMENTS\n[PROBE OUTPUTS] <all collected debug-probe results>\n[FILES AND LOGS] <relevant references from the conversation>\n[REPRODUCTION COMMAND] <supplied command, or state that none was supplied>\n[REQUEST] Independently inspect the code and dependencies, run the reproduction or other safe diagnostic commands, and confirm or reject each leading hypothesis. Stay read-only. Return confirmed root cause, exact reproduction steps and observed result, affected scope, repair constraints, and remaining uncertainty. Report only commands actually run and evidence actually observed.")
```

Collect it with `TaskOutput(task_id="<debug-task-id>", block=true, timeout=300000)`. If the result explicitly says the root cause could not be confirmed, stop and report the missing evidence; do not ask for implementation. Otherwise require a diagnosis and concrete evidence before opening the confirmation step.

### 3. Confirm the diagnosis in the command layer
Present the diagnosis, evidence, reproduction result, impact, and repair constraints to the user through the command layer (not through the `debug` agent):

```text
AskUserQuestion(questions=[{question="根据上述证据确认该诊断并继续实施修复吗?\n诊断: <confirmed root cause>\n证据: <observed evidence>\n复现: <observed reproduction result>\n影响: <affected scope>\n修复约束: <repair constraints>",header="确认诊断",options=[{label="确认并修复",description="继续交给 code 实施,再独立验证"},{label="暂不修复",description="停止实施并保留当前诊断"}],multiSelect=false}])
```

If the user does not confirm, stop without editing and report the diagnosis and the requested follow-up. If the diagnosis is confirmed, pass the confirmation and the complete evidence to `code`.

### 4. Implement the confirmed fix
Start one background implementation task and record both its task ID and agent ID:

```text
Task(subagent_type="code", run_in_background=true, description="Implement the confirmed root-cause fix", prompt="[CHANGE TYPE] Bugfix. [BUG] $ARGUMENTS\n[CONFIRMED ROOT CAUSE] <debug result>\n[REPRODUCTION AND EVIDENCE] <exact steps, commands, and observed results>\n[IMPACT] <affected scope>\n[REPAIR CONSTRAINTS] <constraints from debug>\n[REQUEST] Implement the minimal root-cause fix using existing repository patterns. Run the relevant reproduction or test commands yourself and report exact changed files, commands, and observed results; never claim unrun validation. Do not delegate.")
```

Record its task ID as `<code-task-id>` and agent ID as `<code-agent-id>`. Collect the implementation with `TaskOutput(task_id="<code-task-id>", block=true, timeout=300000)`.

### 5. Verify and bounded correction
Start a background `change-verifier` task and pass the four required inputs:

```text
Task(subagent_type="change-verifier", run_in_background=true, description="Verify the confirmed root-cause fix", prompt="[TARGET] $ARGUMENTS\n[ACCEPTANCE CONDITIONS] The confirmed diagnosis must no longer reproduce, the stated impact must be addressed, and unrelated behavior must remain compatible with existing patterns.\n[CHANGED FILES] <exact files reported by code>\n[REPRODUCTION OR TEST COMMAND] <exact command reported by code>\n[REQUEST] Read the changed files, run the reproduction or test command, and independently check each condition. Return exactly PASS or FAIL with concrete actual evidence.")
```

Collect it with `TaskOutput(task_id="<verifier-task-id>", block=true, timeout=300000)`. On `PASS` with evidence, report the diagnosis, fix, files, and validation. On `FAIL`, send the complete findings to the **same** original `code` agent instead of creating a replacement:

```text
SendMessage(to="<code-agent-id>", summary="Correct failed code root-cause fix", message="[VERIFICATION FAILED] <verifier's concrete evidence and failed conditions>\n[ROOT CAUSE] <confirmed diagnosis>\n[ACTION] Correct the current fix, rerun the relevant reproduction or test command, and report exact changed files and observed results.")
```

Collect the continuation with `TaskOutput(task_id="<code-task-id>", block=true, timeout=300000)`, then start another `change-verifier` task with the same four inputs. Count each `SendMessage` continuation of `code` as one correction loop and allow at most two loops. If the second correction still fails, stop with `FAIL` and all observed evidence; do not start a third loop.

## Final report
Include probe surfaces and clues, the deep diagnosis and reproduction evidence, the user's confirmation outcome, files changed, commands actually run and observed results, verifier status, and any `code` correction-loop count or remaining failure.
