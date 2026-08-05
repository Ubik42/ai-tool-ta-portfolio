# Asset Handoff / Publish Gate 开发计划

## 一.问题反馈

当前作品集已经能证明 5 个 DCC 模块都可运行，但下一步需要一个更像真实生产工具的复合业务闭环：选择一批 Maya 资产后，工具能一次性判断它们是否具备交付条件，并给出协议、规则、贴图、视觉和批处理证据。

## 二.⭐回顾分析

R10.3 不再继续强化展示层。新工具目标是做一个 DCC 内的 `Asset Handoff / Publish Gate`：

- 输入：Maya selection 或 synthetic handoff fixture。
- 业务问题：这批资产能否进入 publish / review / engine handoff。
- 核心逻辑：收集 scene facts，合并协议、规则、贴图、视觉 pass、任务队列结果，形成一个资产级 gate。
- 输出：per-asset gate、blocker list、fix preview、evidence packet、handoff manifest。

它吸收 Lightbox 里最有价值的业务秘诀：资产交付不是单点检查，而是协议、命名、材质、贴图、LOD、review 和队列状态的组合判定。

## 三.改动解释

计划新增 Maya API：

- `asset_handoff_create_fixture`
- `asset_handoff_collect`
- `asset_handoff_evaluate_gate`
- `asset_handoff_preview_actions`
- `asset_handoff_export_packet`

计划新增 React 面板：

- 名称：`Asset Handoff Gate`
- 位置：优先作为现有 `Task Orchestrator` 或 right rail 的 DCC-first composite panel，避免立刻制造第 6 个并列模块。
- UI 内容：asset rows、gate summary、blocker rows、fix/action preview、artifact path、raw JSON。

第一轮 smoke 标准：

- Maya 2024 `mayapy` 可创建 2 个 synthetic handoff assets。
- 至少 1 个 asset 为 Ready，1 个 asset 为 Review。
- 输出协议证据、规则证据、贴图证据、任务队列证据。
- 导出 `maya-asset-handoff-gate@0.1.0` JSON artifact。

## 四.计划&状态

开发顺序：

1. R10.3.1：Maya host API 和 headless smoke。
2. R10.3.2：AuroraView bridge 和 React composite panel。
3. R10.3.3：导出 handoff packet，并把 artifact 接入 Runbook / public case package。
4. R10.3.4：补模块文档和 GUI evidence shotlist。

当前状态：R10.3.1 / R10.3.2 / R10.3.3 / R10.3.4 已完成。

已完成：

- Maya host 已新增 `asset_handoff_*` API。
- React 右侧 rail 已新增 `Asset Handoff Gate` composite panel。
- public case package 已接入 handoff packet artifact。
- Runbook business route 已新增第 6 段 Composite Handoff Gate。
- GUI evidence shotlist 已新增 Asset Handoff Gate 截图目标。
- Maya 2024 `mayapy` smoke 通过：2 synthetic handoff assets，1 Ready，1 Review，0 Blocked，3 preview actions。
- 最新 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-runbook-handoff-package-asset-handoff-20260803-164209.json
```

下一轮：

1. R10.4：把主线 package、handoff packet 和 GUI 证据整理成可直接投递的 portfolio case page。
2. R10.5：采集 R10.3 GUI evidence manifest 中定义的截图和录屏素材。
