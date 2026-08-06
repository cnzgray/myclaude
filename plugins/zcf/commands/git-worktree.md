---
description: Safely add, list, remove, prune, and migrate Git worktrees under ../.zcf/<project>/
argument-hint: "<add|list|remove|prune|migrate> [path] [-b <branch>] [-o|--open] [--track] [--guess-remote] [--detach] [--checkout] [--lock] [--from <source>] [--stash [<stash-ref>]]"
disable-model-invocation: true
allowed-tools: Bash(git rev-parse *), Bash(git worktree *), Bash(git branch *), Bash(git status *), Bash(git stash *), Bash(git ls-files *), Bash(git -C *), Bash(mkdir *), Bash(cp *), Bash(dirname *), Bash(basename *), Bash(command *), Bash(code *), Bash(cursor *), Bash(webstorm *), Bash(subl *), Bash(open *), AskUserQuestion
---

# Git Worktree

Execute `$ARGUMENTS` directly and report concise results.

## Shared Safety

1. Verify a non-bare Git worktree.
2. Resolve the main repository from the absolute Git common directory, then set:
   - project name = main repository basename;
   - managed base = the main repository's parent plus `.zcf/<project>`.
   - create the managed base with `mkdir -p` only after these values and the boundary are validated.
3. Accept only a single relative path segment matching `[A-Za-z0-9._-]+`. Reject absolute paths, separators, `.` and `..`. Every add/remove/migrate target must resolve beneath the managed base and appear in `git worktree list --porcelain` when the operation requires an existing worktree.
4. Never use `--force` for worktree removal, discard changes, drop migration stashes, or delete branches automatically.

## Operations

### `add <path>`

- Refuse an existing path. With `--detach`, reject `-b` and create no branch.
- Otherwise choose `-b <branch>` or default to `<path>`, and refuse if that local branch already exists or is checked out in any worktree; always create it from the selected base instead of silently reusing it.
- Select the base from local `main`, then `master`. If neither exists, ask for the base revision instead of guessing.
- Pass through `--track`, `--guess-remote`, and `--checkout` only when compatible with the chosen branch mode.
- Create the worktree with its absolute managed path. Apply `git worktree lock` only with `--lock`.
- Copy only top-level ignored `.env` and `.env.*` files reported by `git ls-files --others --ignored --exclude-standard`; exclude names containing `example`, `sample`, or `template`, use `cp -p` to preserve metadata, and never overwrite an existing target file.
- With `-o`/`--open`, use the first available CLI among Cursor, VS Code, WebStorm, Sublime Text, then the platform opener. Without the flag, do not open an IDE.

### `list`

Run `git worktree list --porcelain` and summarize path, branch or detached state, lock state, and prunable entries.

### `remove <path>`

- Resolve only the registered managed worktree; never remove the main repository.
- Check tracked, untracked, and ignored files with `git -C <path> status --porcelain --ignored`. Refuse removal if anything would be lost.
- Show the exact path and branch, then require confirmation.
- Run normal `git worktree remove`; prune stale metadata only after success. Do not delete the branch.

### `prune`

Run `git worktree prune --dry-run`, show exactly what Git would remove, require confirmation, then run `git worktree prune`. If there is nothing to prune, stop.

### `migrate <target>`

- Require exactly one source: `--from <source>` or `--stash [<stash-ref>]`.
- Resolve the target as a registered managed worktree and require its tracked/untracked state to be clean.
- `--from`: resolve the source worktree, show its changes, and require confirmation. Create a named stash including untracked files in the source, then apply that stash in the target.
- `--stash`: show the selected stash, defaulting to `stash@{0}`, require confirmation, then apply it in the target.
- Never drop the stash. On conflict, stop immediately; report the target conflict state and the retained stash reference so recovery remains possible. On success, report that the stash is intentionally retained as a backup.

## Result

Report the executed Git operations, absolute worktree path, branch, copied environment filenames, retained migration stash, and any required manual recovery. Never claim success for a denied or failed step.
