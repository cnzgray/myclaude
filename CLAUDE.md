# 项目规则

## 插件发布规则

- 修改任何插件内容（commands、agents、skills、hooks、output-styles）后，**必须同时升 `.claude-plugin/marketplace.json` 中对应插件的 `version` 字段**（patch 递增），否则 Claude Code 按插件版本缓存，不重新拉取更新。
- 受影响插件判定：以 marketplace.json 中插件声明的 `source` 和 `commands`/`skills`/`agents` 列表为准，指向被改目录的所有插件都要升版本。
- README.md 中的版本标注同步更新。
- 示例：改 `plugins/development-essentials/commands/` 需升 `cexll`（显式挂载）和 `cexll-essentials`（该目录为 source）。
