---
name: frontend-ui-ux
description: Frontend design methodology - atomic design, CSS custom properties for theming, design token systems, accessibility-first (WCAG 2.1 AA), responsive design, BEM/CSS Modules, component isolation. Load when implementing or refactoring UI, styling, layout, or design systems.
user-invocable: false
---

# Frontend UI/UX Methodology

Apply these technical methodologies when building or refactoring user interfaces.

## Atomic Design
Compose UI from the smallest reusable units up: **atoms** (button, input, label) → **molecules** (search field = input + button) → **organisms** (header, card list) → **templates** → **pages**. Keep atoms presentational and stateless; push state up to organisms/pages.

## Theming with CSS Custom Properties
- Define a design-token layer as CSS variables on `:root` (and a `[data-theme]` scope for dark/alt themes).
- Reference tokens, never hard-coded values, in components: `color: var(--color-text)` not `#111`.
- Token categories: color, spacing scale, typography (size/line-height/weight), radius, shadow, z-index, motion duration/easing.

## Design Token System
- One source of truth for scales (e.g. spacing `4/8/12/16/24/32`, type `12/14/16/20/24/32`).
- Semantic aliases over raw values: `--color-danger` → `--red-600`, so theming changes one mapping.

## Accessibility-First (WCAG 2.1 AA)
- Semantic HTML first (`button`, `nav`, `main`, `label for`); ARIA only to fill gaps.
- Color contrast ≥ 4.5:1 for text, 3:1 for large text/UI.
- Keyboard operable: visible focus ring, logical tab order, no keyboard traps.
- Respect `prefers-reduced-motion`; provide text alternatives for non-text content.

## Responsive Design
- Mobile-first: base styles for small screens, layer `min-width` media queries up.
- Prefer fluid layouts (`clamp()`, `minmax()`, flex/grid) over fixed breakpoints where possible.

## Naming Methodology
- Use BEM (`block__element--modifier`) or CSS Modules for component isolation - pick whichever the codebase already uses.
- Keep specificity flat; avoid deep descendant selectors and `!important`.

## Component Isolation
- A component owns its styles, state, and a clear prop contract. No reaching into a child's internals.
- Match the existing project's design system and conventions before introducing new patterns.
