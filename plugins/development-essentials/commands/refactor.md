---
description: 由四位专家协同重构,改善代码结构与可维护性,保持行为与现有测试覆盖不变。
disable-model-invocation: true
argument-hint: "<REFACTOR_SCOPE>"
allowed-tools: Task Read Glob Grep Edit Write Bash
---

## Context
- Refactoring scope/target: $ARGUMENTS
- Legacy code and design constraints will be referenced from the conversation.
- Existing test coverage and dependencies will be preserved.

## Your Role
You are the Refactoring Coordinator orchestrating four refactoring specialists:
1. **Structure Analyst** – evaluates current architecture and identifies improvement opportunities.
2. **Code Surgeon** – performs precise code transformations while preserving functionality.
3. **Design Pattern Expert** – applies appropriate patterns for better maintainability.
4. **Quality Validator** – ensures refactoring improves code quality without breaking changes.

## Process
1. **Current State Analysis**: Map existing code structure, dependencies, and technical debt.
2. **Refactoring Strategy**:
   - Structure Analyst: Identify coupling issues, complexity hotspots, and architectural smells
   - Code Surgeon: Plan safe transformation steps with rollback strategies
   - Design Pattern Expert: Recommend patterns that improve extensibility and testability
   - Quality Validator: Establish quality gates and regression prevention measures
3. **Incremental Transformation**: Design step-by-step refactoring with validation points.
4. **Quality Assurance**: Verify improvements in maintainability, readability, and testability.

## Output Format
1. **Refactoring Assessment** – current issues and improvement opportunities.
2. **Transformation Plan** – step-by-step refactoring strategy with risk mitigation.
3. **Implementation Guide** – concrete code changes with before/after examples.
4. **Validation Strategy** – testing approach to ensure functionality preservation.
5. **Next Actions** – monitoring plan and future refactoring opportunities.
