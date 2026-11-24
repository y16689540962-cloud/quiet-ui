# ui-copy-kit

给"AI 生成的网页爱加解释性小字"这个毛病配一把尺子，外加一条常驻规则。

没有尺子的时候，去味只能靠感觉；有了尺子，A 版和 B 版才能比较。

## 三个部分

| 路径 | 作用 |
|---|---|
| `audit_copy.py` | 扫一个页面（或目录），按 R1–R18 列出小字标记，`--json` / `--budget N` |
| `rule.md` | 常驻规则文本，与 `~/.dsh/AGENTS.md` §9 同源 |
| `fixtures/` | 校准用的官方 before/after 页面（来自 unslop-ui 仓库 `examples/`） |
| `pilot/` | A/B 试点产物（见下） |

## 校准：先证明尺子是准的

用别人已经做好的 before/after 一对页面做基准，不自说自话：

```
$ python3 audit_copy.py fixtures/before-landing.html
fixtures/before-landing.html  tells=18  text_runs=24
$ python3 audit_copy.py fixtures/after-landing.html
fixtures/after-landing.html  tells=0  text_runs=11
```

**18 → 0**，且 18 条逐条对应仓库维护者自己删掉的字符串（眉标签、`01 //`、假徽章、
`Live · v2.4 ·` 串联、"Click the button above…"、重复 label 的 placeholder…）。
尺子在这对样本上既不漏也不误报，才有资格去量别的页面。

## A/B 试点：n=1，只说明"规则可执行"

同一句提示（做一个 SaaS 登录/注册页），两个互不可见的子代理，唯一变量是规则文本：

| 产物 | tells | 可见文字段 |
|---|---|---|
| `pilot/A-before-rule.html` 无规则 | **5** | 31 |
| `pilot/B/index.html` 规则贴在提示里 | **0** | 15 |

A 被扫出的 5 条：一条编造的客户证言（`"We moved every client project…" / Rowan Mesa /
Founder, Studio Wren`）+ `SOC 2 Type II · SAML SSO` + `Welcome back.` +
`Sign in to keep every project moving.` + `or continue with email`。

## 6×3 矩阵（2026-11-24 跑完）

同一批 6 个场景提示，三臂各 6 个互不可见的子代理。A 臂在"临时移除 §9"的窗口里跑
（备份 → 移除 → 跑完立刻恢复，校验和与备份一致），B/C 在 §9 常驻下跑。

| 页面 | A 无规则 | B §9 常驻 | C §9 + unslop-ui |
|---|---|---|---|
| 01 SaaS 仪表盘 | 1 | 0 | 0 |
| 02 登录/注册 | 3 | 0 | 0 |
| 03 设置页 | 0 | 0 | 0 |
| 04 待办 | 1 | 0 | 0 |
| 05 游戏 HUD | 0 | 0 | 0 |
| 06 笔记落地页 | 4 | 0 | 0 |
| **合计** | **9** | **0** | **0** |
| 可见文字段合计 | 342 | 194 | 175 |

**三个结论**

1. **基线没想象中脏。** A 臂 6 页只有 9 条（1.5 条/页），集中在落地页（4）和登录页（3）。
   "AI 页面全是解释性小字"这个前提，对这个模型只成立在落地页/登录页这类营销界面。
2. **§9 把剩下的清零，并砍掉 43% 的文字量**（342 → 194 段）。结构没被砍坏：
   label 5→12、button 24→24、表头 11→11、heading 19→15。
3. **unslop-ui 没加分。** C 与 B 都是 0 条，C 还略薄（194 → 175）。
   设置页少了一个 "更改套餐" 动作（B 有、C 没有）——n=1，不能断定是技能删的，
   但它是"收尾清理"这条路唯一的可观测代价。

**一个关于量具的教训**：第一版扫描器在 A 臂上报 47 条，其中 38 条是误报
（`12.4%` 涨幅、`Visa •••• 4242`、12 个月份轴标签、`设计/评审/研究` 任务标签）。
加了"数据上下文"和"祖先 class"两处判据后是 9 条。**先拿真人产出的 before/after 校准，
再拿它去比两版 AI 产物**——否则比的只是自己的噪声。

## 附带拿到的数据点：会话内热注入真的生效

A 臂写完页面约 1 分钟后，§9 才写进 `~/.dsh/AGENTS.md`。它的收尾消息说"文案按 AGENTS.md §9
收敛"，并**回头把已经交付的文件改了**：

| 同一文件 | tells | 可见文字段 |
|---|---|---|
| `pilot/A-before-rule.html`（07:24 快照） | 5 | 31 |
| `pilot/A-after-rule.html`（07:28，agent 自行重写） | **0** | 22 |

删掉的正是清单里的类别：整块证言、`SOC 2 ·` 状态行、问候语、副标题、`or continue with`。
**没有矫枉过正**：4 个 `label`、3 个 `aria-label`、5 个按钮、Terms/Privacy 链接全部保留。

这条证明的是"一个正在跑的会话读到 §9 后会照着改"；不等于"生成时的第一笔就干净"。

**这只是通路证据，不是效应量。** 试点样本量 1、只测登录页。效应大小看上面的 6×3 矩阵。

## 用法

```bash
# 单页
python3 audit_copy.py page.html
# 整个目录，超过 1 条就退出码 1（放进 CI 或提交前检查）
python3 audit_copy.py src/pages --budget 1
# 机器可读
python3 audit_copy.py src --json
```

某条报错了但确有理由（真实状态、法律文字），在这一行加 `audit:ok` 注释即可放行。

## 已知局限

- 纯启发式：`text-xs`、`tracking-` 这类类名和短语表驱动，换个设计系统就漏。**只用相对比较，别拿绝对值当验收。**
- 中文短语表比英文短，中文页面召回率更低。
- 不解析 JSX 表达式：`{t('key')}` 这类动态文案看不到，只会看到字面量。
- 判"真实状态"靠类名和固定词表，数据驱动的徽章也可能被误报。
- 删文字时保留 `aria-label`、`alt`、可见 label 是硬要求；整页没字是 bug，不是干净。

## 和 `unslop-ui` 的分工

`unslop-ui`（`~/.dsh/skills/unslop-ui`，MIT，v1.0.1）是**收尾清理**：读页面、按 U1–U25
给判断、出表格、改文件。它不负责"生成时就不写脏"，也没有计数脚本可用——
本目录的 `audit_copy.py` 补的正是这个空。

注意它和已装的 `unslop`（heydamir，视觉向）描述有重叠，两个都可能被触发：
要清理文案指名 `unslop-ui`，要重做视觉指名 `unslop`。

---

## 按方案原文重跑（2026-11-24 08:36）

前面那轮矩阵用的是我改过的 §9。按要求把 §9 恢复成方案 §5 原文后重跑 B/C：

| | tells | 可见文字段 | 回复长度 |
|---|---|---|---|
| B（§9 原文） | 0 | 158 | 153–184 字符（约 2 句） |
| C（§9 原文 + unslop-ui） | 0 | 152 | **282–1143 字符** |

产物在 `matrix2/`，截图在 `shots/`。

**三条新发现**

1. **方案的 6 行规则本身够用。** 原文没有「禁编造背书」「导航项/表头豁免」，B 臂仍 0 条。
2. **§9 第 6 条与 unslop-ui 直接冲突。** 技能要求交「verdict + 表格 + 清单」的报告，
   C 臂回复因此膨胀到 B 臂的 2–7 倍。「只生成页面，回复一两句话」在有技能介入时必然失效。
3. **人眼复核（4 页截图）抓到扫描器漏的三类**：`↓` 箭头、`✓` 要点列表、页脚标语。
   A 落地页/登录页这三类都有；B2/C2 没有。B2 残留的 `uppercase` 是产品 wordmark 和表头
   （合法），`spark-dot`/`end-dot` 是图表数据点（合法）——**0 条这次是真的干净**。

**过删**：C2 落地页把整个页脚（版权 + 隐私/条款链接）删掉了。法律文字属七类应当保留。

## 方案 §8 的 quiet-ui

建在 `skills/quiet-ui/`（`~/.dsh/skills/quiet-ui` 是指向它的软链）：`SKILL.md`（六条硬规则 + 三问 + 五步 + 12 个分组件规则 +
矫枉过正与无障碍条款 + 清理流程 + 收尾清单）、`scripts/audit_copy.py`（R1–R21）、
`tests/`（4 个夹具，`python3 tests/run_tests.py` 全绿）。

---

## 目录结构

```
audit_copy.py          R1–R21 扫描器（标准库，无依赖）
README.md              校准、试点、矩阵、人眼复核的全部数据
LICENSE                MIT
fixtures/              unslop-ui 官方的 before/after 一对页面（MIT，来自 felipebasurto/unslop-ui）
pilot/                 第一个 A/B 试点（含"规则事后生效"的两版）
matrix/                第一轮 6×3（§9 为改造版）
matrix2/               第二轮 B/C（§9 为方案 §5 原文）
shots/                 人眼复核用的截图
skills/quiet-ui/       兜底 skill：SKILL.md + scripts/audit_copy.py + tests/
```

## 用

```bash
python3 audit_copy.py <文件或目录>            # 列标记
python3 audit_copy.py <目录> --budget 1      # 超过 1 条退出码 1
python3 audit_copy.py <目录> --json          # 机器可读
python3 skills/quiet-ui/tests/run_tests.py   # 扫描器自检
```

## 来源与授权

本仓库 MIT。`fixtures/` 内的两个页面取自 [felipebasurto/unslop-ui](https://github.com/felipebasurto/unslop-ui)
的 `examples/`（MIT），仅用于校准扫描器，未做修改。`skills/quiet-ui` 为本仓库原创。
`matrix/`、`matrix2/`、`pilot/`、`shots/` 下的页面均为 AI 生成产物，仅供评测参照，不是可上线的设计。
