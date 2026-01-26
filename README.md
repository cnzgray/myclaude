# Claude Code Marketplace

个人 Claude Code 插件市场。

## 快捷配置

在 `~/.claude/settings.json` 中添加以下内容：

```json
{
  "enabledPlugins": {
    "cexll-dev@my-marketplace": true,
    "cexll-essentials@my-marketplace": true,
    "zcf@my-marketplace": true
  },
  "extraKnownMarketplaces": {
    "my-marketplace": {
      "source": {
        "source": "github",
        "repo": "cnzgray/myclaude"
      }
    }
  },
  "outputStyle": "cexll-essentials:Linus Torvalds"
}
```

## 插件列表

- **cexll-dev** - 开发工作流，包含需求澄清和并行 codeagent 执行
  - 依赖：需从 [cexll/myclaude releases](https://github.com/cexll/myclaude/releases) 安装 `codeagent-wrapper` 到 `~/.claude/bin/`
  - 推荐：配合原生 [Codex](https://github.com/openai/codex) 或 [Gemini CLI](https://github.com/google-gemini/gemini-cli) 使用效果更佳
- **cexll-essentials** - 核心开发工具（debug、bugfix、optimize、code、review 等）
- **zcf** - Git 实用工具（commit、worktree、分支清理、rollback）

## Output Styles

可用的输出风格（配置到 `outputStyle` 字段）：

| Style | 说明 |
|-------|------|
| `cexll-essentials:Linus Torvalds` | Linus Torvalds 风格，技术直接、KISS/YAGNI 原则 |
| `zcf:engineer-professional.cn` | 专业工程师风格（中文） |
| `zcf:engineer-professional.en` | 专业工程师风格（英文） |
| `zcf:laowang-engineer.cn` | 老王工程师风格（中文） |
| `zcf:laowang-engineer.en` | 老王工程师风格（英文） |
| `zcf:linus-torvalds.cn` | Linus Torvalds 风格（中文） |
| `zcf:linus-torvalds.en` | Linus Torvalds 风格（英文） |
| `zcf:nekomata-engineer.cn` | 猫又工程师风格（中文） |
| `zcf:nekomata-engineer.en` | 猫又工程师风格（英文） |
| `zcf:ojousama-engineer.cn` | 大小姐工程师风格（中文） |
| `zcf:ojousama-engineer.en` | 大小姐工程师风格（英文） |
