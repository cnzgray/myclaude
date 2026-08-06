---
description: Preview or delete merged and stale Git branches with protected-branch and worktree guards
argument-hint: "[--base <branch>] [--stale <days>] [--remote] [--force] [--dry-run] [--yes]"
disable-model-invocation: true
allowed-tools: Bash(git fetch *), Bash(git config *), Bash(git branch *), Bash(git remote *), Bash(git push *), Bash(git for-each-ref *), Bash(git log *), Bash(git rev-parse *), Bash(git symbolic-ref *), Bash(git worktree *), AskUserQuestion
---

# Clean Git Branches

Preview by default. Delete only when `--yes` is present; `--dry-run` always wins. Preview does not fetch, so it reports the repository's current refs; remote refs are refreshed and revalidated before remote deletion.

## Candidate Rules

1. Verify a Git worktree.
2. Resolve `--base`; otherwise use the local branch behind the remote default, then local `main` or `master`. Stop if no unambiguous base exists.
3. Build the protected set from:
   - the base and current branch;
   - every branch checked out in any worktree;
   - `main`, `master`, `develop`, `production`, and `release/*`;
   - exact names or glob patterns from all `branch.cleanup.protected` Git config values.
4. Protection is absolute: `--force`, `--remote`, and `--yes` never override it.
5. Merged candidates are branches fully merged into the resolved base.
6. Validate `--stale <days>` as a positive integer. When present, report branches whose last commit is older than the threshold. An unmerged stale branch is report-only unless `--force` is also present.
7. Local and remote refs are separate candidates. Preserve each remote name, never assume `origin`, and exclude symbolic remote `HEAD` refs.

## Preview

Show one table containing the full ref, local/remote kind, last commit date, merged status, stale status, protection reason, and proposed deletion command. Separate deletable candidates from protected and report-only branches.

- Without `--yes`, stop after the table.
- `--remote` is required for every remote deletion.
- `--force` changes eligible local deletion from `git branch -d` to `git branch -D` and permits the listed unmerged stale candidates. It does not broaden the protected set.
- If `--force` would delete any unmerged branch, require a typed confirmation listing every full branch name even with `--yes`; abort unless the response matches the complete list.

## Execute

1. If remote candidates exist, fetch each involved remote with `--prune`, then recompute the full candidate set. Abort if the base, current branch, protection set, worktree occupancy, or candidates changed; show the revised preview and require a new invocation.
2. Delete local candidates one at a time with `git branch -d`, or `-D` only when approved by `--force`.
3. Delete remote candidates one at a time with `git push <remote> --delete <branch>` only when `--remote` is present.
4. Stop on the first failure. Report branches already deleted, the failed command, and untouched remaining candidates; never claim an all-or-nothing rollback.
5. Finish by listing surviving branches. Never delete tags or working-tree files.

Optional protection configuration:

```bash
git config --add branch.cleanup.protected develop
git config --add branch.cleanup.protected 'release/*'
git config --get-all branch.cleanup.protected
```
