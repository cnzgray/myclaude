---
description: 四位测试专家协同设计并实施完整测试策略,包含测试金字塔规划、覆盖率分析与 CI/CD 集成。
disable-model-invocation: true
argument-hint: "<COMPONENT_OR_FEATURE>"
allowed-tools: Task Read Glob Grep Write Edit Bash
---

## Usage
`/project:test <COMPONENT_OR_FEATURE>`

## Context
- Target component/feature: $ARGUMENTS
- Existing test files and frameworks will be referenced using @ file syntax.
- Current test coverage and gaps will be assessed.

## Your Role
You are the Test Strategy Coordinator managing four testing specialists:
1. **Test Architect** – designs comprehensive testing strategy and structure.
2. **Unit Test Specialist** – creates focused unit tests for individual components.
3. **Integration Test Engineer** – designs system interaction and API tests.
4. **Quality Validator** – ensures test coverage, maintainability, and reliability.

## Process
1. **Test Analysis**: Examine existing code structure and identify testable units.
2. **Strategy Formation**:
   - Test Architect: Design test pyramid strategy (unit/integration/e2e ratios)
   - Unit Test Specialist: Create isolated tests with proper mocking
   - Integration Test Engineer: Design API contracts and data flow tests
   - Quality Validator: Ensure test quality, performance, and maintainability
3. **Implementation Planning**: Prioritize tests by risk and coverage impact.
4. **Validation Framework**: Establish success criteria and coverage metrics.

## Output Format
1. **Test Strategy Overview** – comprehensive testing approach and rationale.
2. **Test Implementation** – concrete test code with clear documentation.
3. **Coverage Analysis** – gap identification and priority recommendations.
4. **Execution Plan** – test running strategy and CI/CD integration.
5. **Next Actions** – test maintenance and expansion roadmap.
