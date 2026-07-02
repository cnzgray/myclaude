---
name: git-master
description: Git hygiene - Conventional Commits (feat/fix/refactor/chore), branch naming conventions, clean history (rebase before merge), meaningful commit messages with scope and body. Load when creating commits, branches, or shaping git history.
user-invocable: false
---

# Git Master

Apply these conventions for any git operation.

## Conventional Commits
Format: `type(scope): subject`
- **Types**: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `perf`, `build`, `ci`, `style`.
- **Subject**: imperative mood, lowercase, no trailing period, ≤ ~72 chars ("add retry to fetch", not "added retries.").
- **Scope**: the affected module/area in parentheses, e.g. `fix(auth): ...`.
- **Body** (when non-trivial): explain the *why* and any consequences, wrapped at ~72 cols, separated from the subject by a blank line.
- **Breaking changes**: add `!` after type/scope (`feat(api)!: ...`) and a `BREAKING CHANGE:` footer.

## Branch Naming
`type/short-description` or `type/ticket-description`, e.g. `feat/oauth-login`, `fix/1234-null-token`. Lowercase, hyphen-separated.

## Clean History
- Make atomic commits: one logical change per commit; don't mix refactor + feature.
- Tidy a local branch with interactive rebase before merging; do not rewrite shared/published history.
- Never use destructive commands (`reset --hard`, force-push, `checkout --`) without explicit approval. Never amend commits unless asked.

## Discipline
- Only commit when the user explicitly requests it.
- Study the repo's existing `git log` style and match it (some projects use emoji, some don't).
- Run the project's pre-commit checks (lint/test) before committing.
