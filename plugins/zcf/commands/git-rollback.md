---
description: Preview or execute a guarded rollback of a local Git branch with reset or revert
argument-hint: "[--branch <branch>] [--target <rev>] [--mode reset|revert] [--depth <n>] [--dry-run] [--yes]"
disable-model-invocation: true
allowed-tools: Bash(git branch *), Bash(git tag *), Bash(git log *), Bash(git reflog *), Bash(git status *), Bash(git rev-parse *), Bash(git show-ref *), Bash(git merge-base *), Bash(git worktree *), Bash(git switch *), Bash(git reset *), Bash(git revert *), AskUserQuestion
---

# Git Rollback

Preview by default. Execute only when `--yes` is present; `--dry-run` always wins and never mutates history or the working tree.

## Resolve the Plan

1. Verify a Git worktree and require a completely clean tracked/untracked state before either mode.
2. Accept only an existing local branch. Do not treat `origin/<name>` or another remote-tracking ref as a local branch.
3. Refuse a branch checked out in another worktree. Switch to the selected local branch only after all checks pass.
4. Resolve `--target` to a commit and require it to be an ancestor of the selected branch. If arguments are omitted, list up to `--depth` recent commits/tags/reflog entries and ask the user to choose.
5. Require an explicit mode:
   - `reset`: move the branch to the target and discard later commits from that branch history;
   - `revert`: create reverse commits for `<target>..HEAD`, preserving history and the target itself.
6. Show branch, current HEAD, resolved target, commits affected, exact commands, and push implications.

Without `--yes`, stop after this preview. Never infer execution from a conversational response after a dry run; require a new invocation with `--yes`.

## Execution Guards

- `reset` on `main`, `master`, `production`, or a `release/*` branch requires a typed confirmation naming the full branch even with `--yes`. Abort on mismatch.
- Before reset, create `backup/rollback-<original-short-sha>` at the original HEAD and verify the backup ref exists. This protects commits, not uncommitted files; the clean-worktree guard remains mandatory.
- Before revert, detect merge commits in `<target>..HEAD`. Stop and request an explicit mainline strategy instead of guessing.

## Execute

- Reset: `git reset --hard <resolved-target>` only after the backup and all confirmations succeed.
- Revert: `git revert --no-edit <resolved-target>..HEAD`. If any revert fails, run `git revert --abort`, verify the branch state, and report the conflict; do not leave a partial sequence.
- Verify final HEAD, status, and affected log range.
- Never push automatically. For reset, suggest `git push --force-with-lease` only after the user reviews the local result; for revert, suggest a normal push.

Report the backup ref, resulting HEAD, created revert commits, or the exact reason execution stopped.
