# 界面文案规则

六条，贴在 `AGENTS.md`、`CLAUDE.md` 或项目级 agent 配置里，让 agent 不再给界面补防御性解释。装了 [`quiet-ui`](skills/quiet-ui/SKILL.md) 的话可以省掉这一步。

```
界面文案规则：
- 页面文字只允许：标题、字段标签、按钮动词、真实数据、错误提示、空状态、法律必需文字。
- 不要加副标题、图注、辅助说明、提示框、眉标签，用层级、分组、留白和图标表达含义。
- 不要加问候语、页脚废话（Made with / Powered by）、"Demo data""仅供参考"之类标签、页面底部小结。
- 不要用"·""•""|"把小字串在一起。
- 保留 aria-label、图片 alt 和输入框标签。
- 只生成页面，回复一两句话，不要附加解释段落。
```

这条规则在 6 个界面、3 种配置下跑过，数字在 [README](README.md)。`audit_copy.py` 检查它有没有被遵守。

存量页面另外用 [unslop-ui](https://github.com/felipebasurto/unslop-ui) 收尾清理。
