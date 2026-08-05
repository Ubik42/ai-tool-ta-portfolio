# 一.问题反馈

R9.6 已把 5 个业务模块全部接入 Maya API。下一步不是继续堆新模块，而是把现有能力收束成 Maya 内可展示的统一入口，让作品集具备面试/评审时可直接运行的一条证据链。

# 二.⭐回顾分析

DCC-first 作品集的最终展示要避免“前端页很多但不知道怎么讲”。更合理的演示路径是：

- 打开 Maya 里的 AuroraView 作品集。
- 右侧先运行一个全局 runbook。
- runbook 创建公开 synthetic scene。
- 依次运行 5 个模块的 DCC API。
- 每个模块产生独立 artifact。
- 最后导出统一 package，证明当前作品集已经有 DCC-backed evidence。

这条链路让展示重心回到 TA 能力：fixture 设计、规则验证、相机/Pass、贴图交付、批处理队列和证据包，而不是网页导航。

# 三.改动解释

Maya host:

- 在 `ai_tool_ta_maya_host/api.py` 新增 `showcase_runbook_build_plan`、`showcase_runbook_run_smoke`、`showcase_runbook_export_package`。
- `Build Plan` 输出 5 个模块的 GUI 入口、主 API 和证明点。
- `Run Smoke` 创建 synthetic demo scene fixtures，并执行 Asset Protocol、Rule Matrix、Visual Review、Texture Delivery、Task Orchestrator 五个模块。
- Rule Matrix 只验证明确的 showcase publish targets，避免故意缺协议的 Task review asset 污染演示总 gate。
- `Export Package` 导出 `maya-dcc-showcase-runbook-package@1.0.0`。

前端:

- 新增 `DccShowcaseRunbookPanel.tsx`。
- 在 `auroraviewBridge.ts` 注册 3 个 runbook API。
- 在 `App.tsx` 右侧 rail 挂载 `DCC Showcase Runbook`。
- 在 `styles.css` 增加 runbook 面板、module rows、artifact rows、JSON details 和移动端收敛样式。

文档:

- 更新根 README 当前 DCC-first 状态和模块文档入口。
- 更新 `docs/260803_DCC-first长期开发计划与环境.md`。
- 更新 `dcc-hosts/maya-auroraview-host/README.md`。
- 新增 `docs/modules/dcc-showcase-runbook.md`。

# 四.计划&状态

验证结果：

- `npm run build` 通过，仅保留既有 Vite 大 chunk 警告。
- `python -m py_compile ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` package smoke 通过：
  - plan modules：5
  - smoke modules：5
  - smoke artifacts：5
  - ready：3
  - review：2
  - blocked：0
  - package gate：Review
  - artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-7-dcc-showcase-runbook-package-20260803-161632.json
```

下一轮自主推进：

- R10 展示收束：压缩主演示路径、补 Maya GUI 点击清单、截图/录屏证据和 public case package 指向当前 DCC-first artifacts。
