---
description: Create reviewed Conventional Commits from current Git changes, with optional splitting, emoji, signoff, and amend
argument-hint: "[--no-verify] [--all] [--amend] [--signoff] [--emoji] [--scope <scope>] [--type <type>]"
disable-model-invocation: true
allowed-tools: Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git add *), Bash(git restore --staged *), Bash(git commit *), Bash(git rev-parse *), Bash(git config *), AskUserQuestion
---

# Git Commit

Create one or more commits using Git only. The command itself never edits working-tree files; local hooks may do so, so compare and report status before and after committing.

## Rules

1. Parse `$ARGUMENTS`. Hooks run unless `--no-verify` is present.
2. Verify this is a Git worktree. Stop on unresolved merge/rebase conflicts. Warn and require confirmation for detached HEAD.
3. Inspect `git status --porcelain`, staged diff, unstaged diff, and recent subjects before proposing any mutation.
4. `--all` means the plan includes `git add -A`, even when some files are already staged. Without it, preserve the current staging boundary.
5. Split only independent, separately revertable concerns. Do not mix feature, fix, refactor, docs, or tests merely because they are currently staged together. Never attempt partial-hunk staging; ask the user to stage hunks manually when path-level grouping is insufficient.
6. Before every `git add`, `git restore --staged`, normal commit, multi-commit sequence, or amend:
   - show exact paths, grouping, and complete proposed message(s);
   - explain any staging changes;
   - ask for confirmation once. Abort on rejection.
7. For an accepted split, unstage only the affected paths, stage one approved group at a time, commit it, then continue. Do not alter file contents.

## Commit Messages

- Format: `[emoji] type(scope): subject`; emoji appears only with `--emoji`.
- Common types: `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `style`, `ci`, `chore`, `revert`.
- `--type` and `--scope` override inference.
- Keep the subject imperative and at most 72 characters. Match the dominant language of the last 20 commit subjects; default to English if mixed or empty.
- Add a body only when motivation, risk, migration, or a breaking change needs explanation. Use `!` and a `BREAKING CHANGE:` paragraph when applicable.

## Execution

- Build `git commit` from the approved flags: `--amend`, `--no-verify`, and `--signoff` as requested. Pass the exact approved message via stdin with `-F -`.
- `--amend` rewrites the last commit and always requires the same explicit confirmation; never claim timestamps or commit identity remain unchanged.
- If a hook or commit fails, stop, preserve the current index, and report the exact failure. Do not retry with `--no-verify` unless the user requested it.
- Finish with `git status --short` and the new commit subject(s).
