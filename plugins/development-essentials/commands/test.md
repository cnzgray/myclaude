---
description: 按真实模块边界由 test-author 审计契约缺口、选择并实施高价值测试,再通过独立验证门。
disable-model-invocation: true
argument-hint: "<COMPONENT_OR_FEATURE>"
allowed-tools: Task TaskOutput SendMessage
---

## Input

- Component, feature, or module scope: `$ARGUMENTS`
- Treat requested behaviors, edge cases, constraints, and referenced files from the conversation as binding.
- Prefer observable contracts and plausible regressions over coverage percentages or tests of implementation details.

## Orchestration Rules

- This command is the only orchestration layer. `test-author` owns module-local gap auditing, test selection, test implementation, and actual test execution; `change-verifier` independently validates the resulting coverage. Both are leaf agents and must not delegate.
- Use only the native protocol: `Task(subagent_type="...", run_in_background=..., description="...", prompt="...")`, `TaskOutput`, and `SendMessage(to="...", summary="...", message="...")`.
- Split the target only along real module or ownership boundaries evidenced by production entry points, consumers, test locations, fixtures, and configuration. A cohesive target gets one `test-author`; independent modules get one each in the same batch. Do not manufacture parallel work or split modules that share the same test ownership boundary.
- The independent verification gate is blocking. An author report or a coverage increase is not proof that an observable contract is defended.

## Workflow

### 1. Audit, select, author, and run by module

Resolve the real module boundaries from `$ARGUMENTS` and referenced repository paths. Launch all independent module authors in one background batch:

`Task(subagent_type="test-author", run_in_background=true, description="Audit and add tests for <module>", prompt="[TARGET MODULE] <one real module within $ARGUMENTS>. [REQUESTED BEHAVIOR] <applicable user requirements and acceptance criteria>. [CONSTRAINTS] <conversation and repository constraints>. [REQUEST] In this single context, first resolve the module boundary and inspect its production contracts, public consumers, existing tests, fixtures, configuration, and test commands. Map existing tests to observable contracts; identify and prioritize evidence-backed gaps at boundaries, error paths, invariants, state transitions, precedence, persistence, or integration points; assign stable gap IDs; and name a plausible regression and suitable test shape for each. Then select the highest-value gaps based on impact and likelihood, run the narrow existing baseline, implement the smallest deterministic tests using existing conventions, and run the focused and relevant final test commands. Edit test files, fixtures, or test configuration only; never modify production code. [OUTPUT] Module boundary; existing contract coverage; prioritized gaps with IDs, evidence, plausible regression, test shape, and discovered command; selected gaps and rationale; changed files; gap-to-test mapping; every baseline, focused, and final command actually run with exit status and meaningful output; unselected or uncovered gaps; product defects or infrastructure blockers. Do not delegate.")`

For each author, record `<test-author-task-id>` for `TaskOutput` and `<test-author-agent-id>` for `SendMessage`, mapped to its module, gap IDs, and owned files. After each completion notification, collect it with `TaskOutput(task_id="<test-author-task-id>", block=true, timeout=300000)`. Never poll a running task. Preserve every module's prioritized gap inventory, selected-gap rationale, gap-to-test mapping, and actual command evidence in the combined handoff.

### 2. Verify observable coverage independently

After all authors finish, start one verifier and retain both its task ID and agent ID:

`Task(subagent_type="change-verifier", run_in_background=true, description="Verify authored contract tests", prompt="[TARGET] $ARGUMENTS. [AUDITED MODULES AND GAPS] <all module boundaries, prioritized gaps, selected IDs, evidence, and plausible regressions reported by test-author agents>. [ACCEPTANCE] <user-observable contract each selected test must defend>. [CHANGED FILES] <all exact files reported by test-author agents>. [REPRODUCTION OR TEST COMMANDS] <all baseline, focused, and final commands with author results>. [REQUEST] Inspect the production contracts and actual tests. Confirm each selected gap maps to a meaningful test that would fail for its stated plausible regression, reject incidental implementation assertions, verify no production code was modified, and run the relevant tests independently. Return exactly PASS or FAIL as the verdict, followed by concrete gap, file, and command evidence. On FAIL identify the responsible gap ID and author-owned file when possible.")`

Record its task ID as `<verifier-task-id>` and agent ID as `<verifier-agent-id>`. Collect it with `TaskOutput(task_id="<verifier-task-id>", block=true, timeout=300000)`. PASS requires both meaningful gap-to-test coverage and successful relevant test execution.

### 3. Correct verification failures

On `FAIL`, route each actionable item to the same `test-author` that owns its module, gap, or file:

`SendMessage(to="<test-author-agent-id>", summary="Correct failed authored contract tests", message="[OWNED MODULE AND GAPS] <module and gap IDs>. [VERIFIER EVIDENCE] <complete findings for this author>. [REQUIRED CORRECTIONS] <all actionable test-only corrections>. Continue in the existing context, preserve the audited observable contracts, correct the tests without modifying production code, rerun every affected focused and final command, and return the updated gap-to-test mapping, changed files, and actual results. Do not delegate.")`

After each completion notification, collect the continuation with `TaskOutput(task_id="<test-author-task-id>", block=true, timeout=300000)` and update the combined gap, mapping, changed-file, and command handoff. Then continue the same verifier with `SendMessage(to="<verifier-agent-id>", summary="Recheck corrected authored tests", message="Inspect the updated files and rerun the full verification gate using this combined evidence: <updated author handoff>.")`; collect it with `TaskOutput(task_id="<verifier-task-id>", block=true, timeout=300000)`.

Allow at most **two correction rounds** after the initial authoring pass. Each round may continue every responsible existing `test-author`, but must not create replacement authors. Stop immediately on PASS. If the second correction still fails, or actual command output proves a product defect or external infrastructure blocker prevents a valid test-only correction, report the failing contract and evidence. Never weaken the expected contract, edit production behavior, or report PASS to escape the loop.

## Final Output

Report audited module boundaries, the prioritized gap inventory, selected gap IDs and rationale, the gap-to-test mapping, changed files, baseline/focused/final commands with actual outcomes, unselected or uncovered gaps, correction rounds, and the verifier's final PASS/FAIL evidence. Distinguish test defects from product or infrastructure blockers.
