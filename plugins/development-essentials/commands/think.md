---
description: 基于仓库与命令证据分析复杂问题,比较选项并给出可执行决策,不修改代码。
disable-model-invocation: true
argument-hint: "<TASK_DESCRIPTION>"
allowed-tools: Read Glob Grep Bash
---

## Objective

Analyze this problem without changing the repository:

$ARGUMENTS

Use relevant file references and constraints from the conversation. Gather only the evidence needed to resolve the question.

## Rules

- Stay read-only. Do not edit, create, rename, or delete files. Use Bash only for non-mutating inspection or calculations over existing data; do not install dependencies or run commands that produce repository artifacts.
- Do not invoke `Task` or claim that another agent performed any part of the analysis.
- Do not expose private chain-of-thought, hidden reasoning, or a step-by-step reasoning transcript. Provide concise conclusions and evidence instead.
- Separate observed facts from inferences and unknowns. Cite repository evidence as `file:line` and summarize relevant command output.
- Treat each hypothesis as falsifiable. Reject hypotheses contradicted by evidence and label unresolved points rather than guessing.
- Compare only materially different options, including their trade-offs, risks, and constraints.
- Recommend a decision when the evidence supports one. If it does not, state the exact missing evidence and the smallest read-only check that would resolve it.

## Output

1. **Hypotheses** — candidate explanations or interpretations and their current status.
2. **Evidence** — observations, citations, command results, and clearly marked inferences or unknowns.
3. **Options** — viable alternatives with concrete trade-offs.
4. **Decision** — the recommended conclusion and concise evidence-based rationale.
5. **Next Steps** — ordered actions or checks; do not perform edits.
