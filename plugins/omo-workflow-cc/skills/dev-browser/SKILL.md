---
name: dev-browser
description: Chrome DevTools mastery for debugging and profiling - Elements/Console/Network/Performance/Application tabs, network waterfall and timing analysis, Lighthouse audits, responsive-mode debugging, source maps. Load when diagnosing browser runtime, network, or performance issues.
user-invocable: false
---

# Dev Browser - Chrome DevTools Mastery

Apply these techniques when diagnosing browser-side runtime, network, or performance problems.

## Elements
- Inspect the live DOM and computed styles; toggle pseudo-states (`:hover`, `:focus`) and classes to reproduce states.
- Use the computed/box-model panes to debug layout, spacing, and stacking (z-index) issues.

## Console
- Read errors and stack traces; reproduce with ad-hoc expressions.
- Use `$0` for the selected element, `monitorEvents`, `console.table` for structured data.

## Network
- Read the waterfall: DNS/connect/TTFB/content-download timing to locate the slow segment.
- Inspect request/response headers, payloads, status codes, and caching; throttle to simulate slow networks; check for blocking/serialized requests.

## Performance
- Record a profile to find long tasks, layout thrashing, and excessive re-renders.
- Watch for forced synchronous layout (read-after-write on layout properties) and oversized main-thread work.

## Application
- Inspect localStorage/sessionStorage, cookies, IndexedDB, service workers, and cache storage when debugging state/auth/offline issues.

## Lighthouse
- Run audits for performance, accessibility, best practices, SEO; treat the opportunities/diagnostics as a prioritized fix list.

## Responsive & Source Maps
- Use device/responsive mode to reproduce viewport-specific bugs.
- Ensure source maps are loaded so breakpoints and stack traces map to original source, not bundled output.
