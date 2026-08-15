# 项目规则

## 插件发布规则

- 插件版本号按 **Git 提交批次** 管理：同一个未提交工作区中的多次修改不得重复升版。
- 准备提交包含插件内容（commands、agents、skills、hooks、output-styles）变更的 commit 时，必须在该 commit 中将所有受影响插件的 `.claude-plugin/marketplace.json` `version` 相对提交基线统一做一次 patch 递增，否则 Claude Code 会继续使用旧版本缓存。
- 受影响插件判定：以 marketplace.json 中插件声明的 `source` 和 `commands`/`skills`/`agents` 列表为准；指向被改目录的所有插件都必须在同一个 commit 中升版一次。
- README.md 中的版本标注与该 commit 的 marketplace 版本同步。尚未准备提交时保留上一发布版本，不因每轮编辑单独升号。
- 示例：一个 commit 修改 `plugins/development-essentials/commands/` 时，`cexll`（显式挂载）和 `cexll-essentials`（该目录为 source）各做一次 patch 递增；该 commit 前的工作区迭代不重复递增。
