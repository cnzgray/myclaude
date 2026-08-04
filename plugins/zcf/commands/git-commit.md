---
description: Analyze changes with Git only and auto-generate conventional commit messages with optional emoji; suggests splitting commits when needed, runs local Git hooks by default (use --no-verify to skip)
allowed-tools: Read(**), Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git add *), Bash(git restore --staged *), Bash(git commit *), Bash(git rev-parse *), Bash(git config *), AskUserQuestion
argument-hint: "[--no-verify] [--all] [--amend] [--signoff] [--emoji] [--scope <scope>] [--type <type>]"
# examples:
#   - /git-commit                           # Analyze current changes, generate commit message
#   - /git-commit --all                     # Stage all changes and commit
#   - /git-commit --no-verify               # Skip Git hooks
#   - /git-commit --emoji                   # Include emoji in commit message
#   - /git-commit --scope ui --type feat    # Specify scope and type
#   - /git-commit --amend --signoff         # Amend last commit with signature
---

# Claude Command: Commit (Git-only)

This command works **without any package manager/build tools**, using only **Git** to:

- Read changes (staged/unstaged)
- Determine if changes should be **split into multiple commits**
- Generate **Conventional Commits** style messages with optional emoji for each commit
- Execute `git add` and `git commit` as needed (runs local Git hooks by default; use `--no-verify` to skip)

---

## Usage

```bash
/git-commit
/git-commit --no-verify
/git-commit --emoji
/git-commit --all --signoff
/git-commit --amend
/git-commit --scope ui --type feat --emoji
```

### Options

- `--no-verify`: Skip local Git hooks (`pre-commit`/`commit-msg` etc.).
- `--all`: When staging area is empty, automatically `git add -A` to include all changes in the commit.
- `--amend`: **Amend** the last commit without creating a new one (preserves author and timestamp unless local Git config specifies otherwise).
- `--signoff`: Add `Signed-off-by` line (use when following DCO process).
- `--emoji`: Include emoji prefix in commit message (omit for plain text).
- `--scope <scope>`: Specify commit scope (e.g., `ui`, `docs`, `api`), written to message header.
- `--type <type>`: Force commit type (e.g., `feat`, `fix`, `docs`), overrides automatic detection.

---

## What This Command Does

1. **Repository/Branch Validation**
   - Check if in a Git repository using `git rev-parse --is-inside-work-tree`.
   - Read current branch/HEAD status; if in rebase/merge conflict state, prompt to resolve conflicts first.

2. **Change Detection**
   - Get staged and unstaged changes using `git status --porcelain` and `git diff`.
   - If staged files = 0:
     - If `--all` is passed → Execute `git add -A`.
     - Otherwise prompt choice: continue analyzing unstaged changes for **suggestions**, or cancel to manually group staging.

3. **Split Suggestions (Split Heuristics)**
   - Cluster by **concerns**, **file modes**, **change types** (e.g., source code vs docs/tests; different directories/packages; additions vs deletions).
   - **Don't mix `feat`/`fix`/`refactor` in the same commit**; keep each commit independently revertable.
   - If **multiple independent changesets** or large diff detected (e.g., > 300 lines / across multiple top-level directories), suggest splitting commits with pathspecs for each group (for subsequent `git add <paths>`).

4. **Commit Message Generation (Conventional with Optional Emoji)**
   - Auto-infer `type` (`feat`/`fix`/`docs`/`refactor`/`test`/`chore`/`perf`/`style`/`ci`/`revert`...) and optional `scope`.
   - Generate message header: `[<emoji>] <type>(<scope>)?: <subject>` (first line ≤ 72 chars, imperative mood, emoji included only with `--emoji` flag).
   - **Subject language**: Detect the language of the repo's recent commit history with `git log -n 20 --pretty=%s`, and write `<subject>` in the dominant language of existing commits — Chinese history → Chinese subject (e.g., "添加... / 修复..."), English history → English subject (e.g., "add... / fix..."). Default to English when history is empty or mixed/ambiguous. Type/scope stay in English per Conventional Commits.
   - Generate message body: bullet points (motivation, implementation details, impact scope, risks, BREAKING CHANGE if any).

5. **Execute Commit**
   - Single commit scenario: `git commit [-S] [--no-verify] [-s] -F - <<'EOF'` with the generated message via HEREDOC.
   - Multiple commit scenario (if split accepted): Provide clear instructions for `git add <paths> && git commit -F - <<'EOF' ...` per group; execute sequentially if allowed.

6. **Safe Rollback**
   - If mistakenly staged, use `git restore --staged <paths>` to unstage (command provides instructions, doesn't modify file contents).

---

## Best Practices for Commits

- **Clear subject**: First line ≤ 72 chars, imperative mood (e.g., "add... / fix..." / "添加... / 修复..."), language follows the repo's existing commit history.

---

## Type to Emoji Mapping (When --emoji is Used)

- ✨ `feat`: New feature
- 🐛 `fix`: Bug fix
- 📝 `docs`: Documentation and comments
- 🎨 `style`: Code style/formatting (no semantic changes)
- ♻️ `refactor`: Refactoring (no new features, no bug fixes)
- ⚡️ `perf`: Performance improvements
- ✅ `test`: Add/fix tests, snapshots
- 🔧 `chore`: Build/tools/misc tasks (merge branches, update configs, release tags, pin dependencies, .gitignore, etc.)
- 👷 `ci`: CI/CD configuration and scripts
- ⏪️ `revert`: Revert commits
- Breaking changes: use `feat!:` (or `fix!:` etc.) and add a `BREAKING CHANGE:` paragraph in the body — no special emoji.

> If `--type`/`--scope` is passed, it will **override** auto-detection.

---

## Examples

**Good (--emoji on; without the flag, drop the emoji prefix)**

- ✨ feat(ui): add user authentication flow
- 🐛 fix(api): handle token refresh race condition
- 📝 docs: update API usage examples
- ♻️ refactor(core): extract retry logic into helper
- ✅ test: add unit tests for rate limiter
- 🔧 chore: update git hooks and repository settings
- ⏪️ revert: revert "feat(core): introduce streaming API"

**Example when repo history is Chinese**

- ✨ feat(ui): 添加用户登录流程
- 🐛 fix(api): 处理 token 刷新竞态条件
- 📝 docs: 更新 API 使用示例
- ♻️ refactor(core): 抽取重试逻辑为辅助函数
- ✅ test: 为限流器添加单元测试
- 🔧 chore: 更新 git hooks 和仓库配置

**Split Example**

- `feat(types): add new type defs for payment method`
- `docs: update API docs for new types`
- `test: add unit tests for payment types`
- `fix: address linter warnings in new files` ← (if your repo has hook errors)

---

## Important Notes

- **No source code changes**: Reads only the staging area and commits via HEREDOC; never edits working-directory files.
- **Safety prompts**: In rebase/merge conflict or detached HEAD states, prompt to handle/confirm before continuing.
