# Claude Code 工程师风格插件

这个插件为Claude Code提供多种专业的工程师输出风格，严格遵循SOLID、KISS、DRY、YAGNI原则，专为经验丰富的开发者设计。

## 快速开始

### 1. 插件安装

将插件目录复制到Claude Code的插件目录：

```bash
# 复制插件到Claude Code插件目录
cp -r my-plugin ~/.claude-plugins/
```

### 2. 启用插件

#### 方法一：通过Claude Code界面启用
1. 打开Claude Code设置
2. 导航到"插件"(Plugins)选项卡
3. 找到"my-plugin"并启用它
4. 重启Claude Code

#### 方法二：通过命令行启用
如果您的Claude Code版本支持命令行配置：

```bash
# 启用插件
claude code plugin enable my-plugin

# 重启Claude Code以使更改生效
claude code restart
```

### 3. 使用工程师风格

启用插件后，您可以在对话中指定使用特定的工程师风格：

```
请以工程师专业版模式帮我审查这段代码
```

或

```
使用linus-torvalds风格重构这个函数
```

### 4. 可用的输出风格

插件提供以下工程师输出风格：

- **engineer-professional**: 工程师专业版 - 严格遵循软件工程最佳实践
- **linus-torvalds**: Linux内核风格 - 直接、务实的技术导向
- **laowang-engineer**: 老王工程师风格 - 经验丰富、注重实用性
- **nekomata-engineer**: Nekomata工程师风格 - 创新、注重细节
- **ojousama-engineer**: Oujousama工程师风格 - 优雅、精致的代码风格

## 插件特性

### 危险操作确认机制
所有高风险操作都会要求明确确认：
- 文件系统操作（删除、移动）
- Git提交操作
- 系统配置更改
- 数据操作
- 网络请求
- 包管理操作

### 编程原则遵循
- **KISS原则**: 追求极致简洁
- **YAGNI原则**: 仅实现必需功能
- **DRY原则**: 杜绝代码重复
- **SOLID原则**: 单一职责、开闭、里氏替换、接口分离、依赖反转

### 命令执行标准
- 跨平台兼容性
- 统一的路径处理
- 优化的工具优先级
- 高效的批量操作

## 目录结构

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # 插件配置文件
├── hooks/
│   └── hooks.json           # Hook配置
└── hooks-handlers/
    ├── session-start.sh     # 会话启动处理器
    └── output-styles/       # 输出风格定义
        ├── engineer-professional.md
        ├── linus-torvalds.md
        ├── laowang-engineer.md
        ├── nekomata-engineer.md
        └── ojousama-engineer.md
```

## 自定义和扩展

### 添加新的输出风格

1. 在`hooks-handlers/output-styles/`目录下创建新的风格文件
2. 在`session-start.sh`中注册新的风格
3. 更新`hooks.json`以支持新风格

### 修改现有风格

编辑对应的`.md`文件来调整输出行为和指导原则。

## 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请通过以下方式联系：

- 作者: zgray
- 邮箱: cnzgray@gmail.com

## 许可证

本插件遵循MIT许可证。

---

*本插件基于Claude Code插件系统开发，遵循官方插件开发规范。*