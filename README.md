# ui-copy-kit

<img src="assets/landing-annotated.png" width="100%" alt="同一个提示词下，无规则与规则常驻两版落地页的对比，左侧标出扫描器命中的 8 处">

扫描网页里多余的说明文字：副标题、图注、提示框、页脚废话、假徽章、`·` 串联的状态串，等等。

附一套在 DeepSeek 上跑过的对比数据，用来判断"禁止加解释性小字"这条规则到底有没有用。

## 用

```bash
python3 audit_copy.py page.html               # 列出命中的标记
python3 audit_copy.py src/pages --budget 1    # 超过 1 条退出码 1，可当提交前检查
python3 audit_copy.py src --json              # 机器可读
python3 skills/quiet-ui/tests/run_tests.py    # 扫描器自检
```

某条报得不对、但确有理由（真实状态、法律文字），在那一行加 `audit:ok` 注释即可放行。

## 给 agent 用

把这个仓库的链接丢给 agent，说清要清理哪个文件。规则写在 `skills/quiet-ui/SKILL.md`，
下面有六条硬规则、五步流程和分组件说明；扫描器是 `audit_copy.py`。不需要安装。

## 规则

R1–R21，Python 标准库，无依赖。逐条说明见 [skills/quiet-ui/SKILL.md](skills/quiet-ui/SKILL.md)。

| 编号 | 抓什么 |
|---|---|
| R1 R2 | 眉标签、`01 //` 编号 |
| R3 | `·` `•` `\|` 串联（数据对、掩码卡号已排除） |
| R4 R10 | 标题下的副标题、复述标题的段落 |
| R5 R19 | 辅助说明、提示框（错误/警告/空状态豁免） |
| R6 R18 | 问候语、`or continue with` 这类衔接词 |
| R7 R8 | 营销套话、无出处的数字与背书 |
| R9 | 页面自我描述（"本节说明…"） |
| R11 R15 | 硬编码徽章、`<figcaption>` 图注 |
| R12 R13 R14 | 页脚废话、Demo data 标签、底部小结 |
| R16 | placeholder 重复 label |
| R17 | 引号证言 + 头衔署名 |
| R20 R21 | shadcn 描述组件、按钮后的箭头 |

## 校准

拿别人做好的样本验一遍，再用来量自己的页面。`fixtures/` 是 [felipebasurto/unslop-ui](https://github.com/felipebasurto/unslop-ui) 仓库自带的一对 before/after：

```
before-landing.html  tells=18  text_runs=24
after-landing.html   tells=0   text_runs=11
```

18 条逐条对应该仓库维护者自己删掉的字符串。在这对样本上不漏报也不误报。

## 实测

6 个界面场景（仪表盘、登录页、设置页、待办、游戏 HUD、落地页），三种配置，每种 6 个互不可见的子代理。

第一轮，常驻规则用的是我改写过的版本：

| 页面 | A 无规则 | B 规则常驻 | C 规则 + unslop-ui |
|---|---|---|---|
| 仪表盘 | 1 | 0 | 0 |
| 登录注册 | 3 | 0 | 0 |
| 设置页 | 0 | 0 | 0 |
| 待办 | 1 | 0 | 0 |
| 游戏 HUD | 0 | 0 | 0 |
| 落地页 | 4 | 0 | 0 |
| 合计 | 9 | 0 | 0 |
| 可见文字段 | 342 | 194 | 175 |

第二轮，规则换成方案原文的 6 条，重跑 B/C：

| | 标记 | 可见文字段 | 回复长度 |
|---|---|---|---|
| B 规则原文 | 0 | 158 | 153–184 字符 |
| C 规则原文 + unslop-ui | 0 | 152 | 282–1143 字符 |

A 臂在临时移除规则的窗口里跑（备份、移除、跑完恢复，校验和一致），B/C 在规则常驻下跑。

登录页那一对，红框是扫描器报出的位置：

<img src="assets/auth-annotated.png" width="100%" alt="登录页对比：左侧标出欢迎语、副标题、衔接词、复选框说明和状态点五处命中，右侧为零">

### 说明

- 无规则时每页 1.5 条，集中在落地页和登录页。仪表盘、设置页、HUD 基本没有这个问题。
- 加规则后标记清零，可见文字段减少 43%，`label`、按钮、表头、标题的数量没有下降。
- C 臂的回复涨到 B 臂的 2–7 倍：unslop-ui 要求交"判定 + 表格 + 清单"的报告，和"回复一两句话"这条规则冲突。
- 每格只有 1 个样本。差异很大，但只能说明方向。
- 第一版扫描器在 A 臂上报了 47 条，其中 38 条是误报（`12.4%` 涨幅、`Visa •••• 4242`、12 个月份轴标签、任务标签）。修到 9 条之后才开始比。

### 人眼复核

`shots/` 是四张截图。无规则那臂的落地页和登录页有眉标签、`✓` 要点列表、状态点、页脚标语；B/C 两臂没有。

看截图时发现扫描器漏了三类：`↓` 箭头、`✓` 要点列表、页脚标语。B 臂里剩下的 `uppercase` 是产品 wordmark 和表头，`spark-dot` 是图表数据点，都正常。

## 已知限制

- 纯启发式，靠类名和短语表。换一套设计系统就会漏。
- 只适合做相对比较，绝对值不可当验收线。
- 中文短语表比英文短，中文页面召回率更低。
- 不解析 JSX 表达式，`{t('key')}` 这类动态文案看不到。
- 判"真实状态"靠类名，数据驱动的徽章也会误报。

## 目录

```
audit_copy.py          R1–R21 扫描器
assets/                README 用的对比图
fixtures/              校准用的 before/after（unslop-ui，MIT）
pilot/                 第一组 A/B，含规则事后生效的两版
matrix/                第一轮 6×3
matrix2/               第二轮 B/C（规则换回原文）
shots/                 人眼复核截图
skills/quiet-ui/       兜底 skill：SKILL.md + scripts/audit_copy.py + tests/
```

`~/.dsh/skills/quiet-ui` 指向 `skills/quiet-ui`，改仓库即改生效的 skill。

## 许可

MIT。`fixtures/` 取自 felipebasurto/unslop-ui（MIT），未修改。

`matrix/`、`matrix2/`、`pilot/`、`shots/` 里的页面是模型生成的评测产物，不是可上线的设计。
