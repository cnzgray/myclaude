---
description: 以可重复基线驱动性能优化,独立复测指标并验证功能回归。
disable-model-invocation: true
argument-hint: "<PERFORMANCE_TARGET>"
allowed-tools: Task TaskOutput SendMessage
---

## Context

- Performance target or bottleneck: $ARGUMENTS
- Relevant files, workload constraints, acceptance criteria, and prior measurements may be referenced from the conversation.

## Workflow

You are the orchestration layer. Subagents are leaf workers; do not implement, profile, or verify the change yourself.

### 1. Establish the baseline

Invoke one profiler synchronously:

`Task(subagent_type="optimize-profiler", run_in_background=false, description="Establish optimization baseline", prompt="[MODE] Baseline. [TARGET] $ARGUMENTS. [CONTEXT] Include all relevant file references, workload constraints, acceptance criteria, and prior measurements from the conversation. Establish a runnable, repeatable benchmark and collect baseline samples plus hotspot evidence. Return READY or BLOCKED; the exact command, working directory, environment/configuration, data fixture, warm-ups, iterations/sample count, primary metric and direction, raw-value summary, variance/noise, minimum meaningful improvement, guardrail metrics, and evidence-backed hotspots. Do not edit files or estimate unmeasured gains.")`

If the result is `BLOCKED`, stop. Report the missing prerequisite and evidence. Do not invoke `optimize`, and do not claim an improvement without a measured baseline.

Freeze the complete baseline protocol. Its command, working directory, environment/configuration, runtime/tool versions, data fixture, setup and cache state, warm-ups, iterations, sample count, aggregation, metric calculation, acceptance threshold, and guardrails are immutable for every later comparison.

### 2. Implement the optimization

Invoke one implementation agent synchronously and retain its agent id for follow-ups:

`Task(subagent_type="optimize", run_in_background=false, description="Implement measured optimization", prompt="[TARGET] $ARGUMENTS. [BASELINE] Pass the complete optimize-profiler baseline report verbatim. [CONTEXT] Pass relevant files, constraints, and functional acceptance criteria from the conversation. Optimize only evidence-backed hotspots. Edit the implementation, run the supplied benchmark protocol, and run relevant functional tests. Return changed files, rationale tied to hotspot evidence, exact benchmark/test commands, and actual results. Do not claim unmeasured improvement.")`

### 3. Independently measure and regress

After implementation, launch these two independent checks together in one batch with `run_in_background=true`:

- `Task(subagent_type="optimize-profiler", run_in_background=true, description="Remeasure optimization", prompt="[MODE] Comparison. [TARGET] $ARGUMENTS. [PROTOCOL] Pass the frozen baseline protocol and baseline samples verbatim. Execute exactly that protocol against the changed tree; do not substitute its command, working directory, environment/configuration, runtime/tool versions, data fixture, setup/cache state, warm-ups, iterations, sample count, aggregation, metric calculation, thresholds, or guardrails. Return PASS, FAIL, or BLOCKED with before/after raw-value summaries, variance, absolute and relative deltas, guardrail results, and protocol identity evidence. PASS only when the primary metric clears the predefined meaningful-improvement threshold without guardrail regression.")`
- `Task(subagent_type="change-verifier", run_in_background=true, description="Verify optimization regression safety", prompt="[TARGET] $ARGUMENTS. [ACCEPTANCE] Pass the functional acceptance criteria and behavior that must remain unchanged. [CHANGED FILES] Pass the optimize agent's exact changed-file list. [COMMANDS] Pass the reproduction or test commands from the baseline and optimize result. Independently inspect the changes and run the relevant commands. Return PASS or FAIL with actual command output and concrete evidence.")`

Wait for each completion notification, then collect each result once with `TaskOutput(task_id="<task-id>", block=true, timeout=300000)`; never poll a running task.

### 4. Correct failures

Success requires both an `optimize-profiler` `PASS` and a `change-verifier` `PASS`. A flat or noisy result, a missed threshold, a guardrail regression, `BLOCKED`, or verifier `FAIL` is not success.

On failure, continue the same implementation agent with:

`SendMessage(to="<optimize-agent-id>", summary="Correct failed optimization", message="The independent checks failed. Here are the profiler and verifier reports verbatim: <reports>. Diagnose the evidence, correct the implementation, and rerun the frozen benchmark protocol plus relevant functional tests. Return the changed files and actual command results.")`

Collect the same `optimize` agent's continuation with `TaskOutput(task_id="<optimize-task-id>", block=true, timeout=300000)`. Then repeat both independent checks from step 3 against the new tree, passing the latest changed-file list and command results. Make at most **two correction attempts**. Never start a fresh `optimize` agent for a correction.

If both checks still do not pass after two corrections, stop and report the measured results and unresolved evidence without claiming improvement. Otherwise report the baseline, identical-protocol comparison, functional verification, changed files, and measured outcome.
