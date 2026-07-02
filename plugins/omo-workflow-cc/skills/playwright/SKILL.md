---
name: playwright
description: End-to-end browser testing and QA with Playwright - Page Object Model, role/text locators, web-first assertions, test isolation, parallel execution, screenshot evidence. Load when verifying browser-rendered UI or writing E2E tests.
user-invocable: false
---

# Playwright E2E Testing & Browser QA

Apply these patterns when driving a real browser to verify UI or write end-to-end tests.

## Locator Best Practices
- Prefer user-facing, role/text locators: `getByRole('button', { name: 'Submit' })`, `getByText`, `getByLabel`, `getByPlaceholder`.
- Avoid brittle CSS/XPath tied to structure. Use `data-testid` only when no accessible handle exists.
- Locators are lazy and auto-retry - resolve them at use time, not ahead of time.

## Web-First Assertions
- Use auto-waiting assertions: `await expect(locator).toBeVisible()`, `toHaveText()`, `toHaveValue()`, `toHaveURL()`.
- These retry until the condition holds or times out - do not add manual `waitForTimeout` sleeps.

## Page Object Model
- Encapsulate page interactions in a class exposing intent-level methods (`login(user, pass)`), not raw selectors, so tests read as user flows and selectors live in one place.

## Test Isolation
- Each test starts from a clean state (fresh context/storage). No shared mutable state between tests.
- Use fixtures for setup/teardown; keep tests independently runnable and order-independent.

## Parallel Execution
- Tests run in parallel by default - ensure they don't contend for shared resources (same user, same record).

## Evidence Capture (for QA gates)
- Screenshot key states: `await page.screenshot({ path: '.omo/evidence/<task>-<scenario>.png' })`.
- Capture the console and failed network requests when diagnosing failures.
- Run the happy path AND at least one failure/edge case; assert exact expected values, not "it works".
