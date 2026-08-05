# Asset Handoff Gate

R10.3 目标：把前面 5 个 DCC 模块的能力组合成一个真实 TA 业务闭环。它不作为第 6 个并列模块出现，而是右侧 rail 的 DCC composite gate：选择一批 Maya 资产，判断是否能进入 publish / review / engine handoff。

## 核心业务逻辑

资产交付不是单点检查。一个资产能不能交付，至少要同时看：

- 协议：是否有稳定的 `aiToolTaProtocol`，schema 是否正确。
- 规则：命名、LOD、collision、material、export root 是否满足发布门禁。
- 贴图：material / file node / role / color space / source path 是否可追踪。
- 视觉：是否能进入固定 camera/pass review manifest。
- 队列：是否能生成 dry-run task events 和 per-asset receipt。

R10.3 的首轮实现把这些证据合并为 per-asset gate，并导出 handoff packet。

R10.6 把 gate 继续推进到决策层：每个资产不仅有 Ready / Review / Blocked，还要有 repair preview、owner disposition 和 engine handoff mock。这样 reviewer 看到的不只是“哪里错了”，还包括“谁能决策、怎么预修复、能不能进入引擎交付预演”。

R10.8 把 engine handoff mock 继续推进到 preflight：Ready intent 必须通过平台 preset、路径、LOD、预算、协议和 receipt 检查后，才生成 dry-run import sidecar；Review intent 保持 owner-held，不进入 sidecar。

R10.9 把 preflight 推进到平台对比：同一批 engine intent 同时跑 PC / Mobile preset，让 reviewer 看到 PC 可生成 sidecar、Mobile 因路径和平台 preset 被挡住，owner-held 资产跨平台保持 held。

R13 把 sidecar 对比推进到 engine-side inspection：Unreal Handoff Inspector 用公开 Content Registry / AssetImportTask fixture 检查 mount root、source fingerprint、dependency、LOD、collision、owner state，并只生成 dry-run import command preview。

R14 把 engine-side inspection 升级到 Unreal Python L3：公开 Unreal test project 已能通过 `UnrealEditor-Cmd.exe -run=pythonscript` 打开，查询 Asset Registry，记录 Unreal 5.3.2 / Python 3.9.7 runtime snapshot，并保持 engine writes / asset writes 为 0。

R15 把 engine-side inspection 升级到 Unreal registry fixture：公开 Unreal test project 内生成 `SM_HeroPanel_A` StaticMesh 和 `M_HeroPanel` Material，并验证 2 / 2 Asset Registry path/class rows 匹配。

R16 把 engine-side inspection 升级到 StaticMesh engine facts：source import data、material slot assignment、LOD count 和 collision settings 4 / 4 匹配。

R17 把 engine-side facts 接到 PC / Mobile preset 和 exception waiver policy：10 条 preset/fact 行输出 7 matched、1 drift、1 waived、1 blocked，PC 单 LOD 是显式 waiver，Mobile 仍被平台路径和 LOD policy 阻断。

## 当前实现

代码入口：

- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
- `showcases/portfolio-site/src/components/AssetHandoffGatePanel.tsx`
- `showcases/portfolio-site/src/lib/auroraviewBridge.ts`

Maya API：

- `asset_handoff_create_fixture`
- `asset_handoff_collect`
- `asset_handoff_evaluate_gate`
- `asset_handoff_preview_actions`
- `asset_handoff_export_packet`
- `asset_handoff_build_decision_packet`
- `asset_handoff_export_decision_packet`
- `engine_handoff_build_preflight_packet`
- `engine_handoff_export_preflight_packet`
- `engine_handoff_build_preset_comparison`
- `engine_handoff_export_preset_comparison`

React 面板：

- 右侧 rail 的 `Asset Handoff Gate`
- `Fixture`
- `Collect`
- `Evaluate Gate`
- `Preview Actions`
- `Export Packet`
- `Decision Packet`
- `Engine Preflight`
- `Preset Compare`

## Smoke 内容

`asset_handoff_create_fixture` 创建 2 个 synthetic assets：

- Ready asset：有 protocol、material、file node、collision、LOD 和 budget。
- Review asset：有 valid protocol，但故意缺 material / texture 绑定。

`asset_handoff_export_packet` 输出：

- per-asset gate。
- blocker / review list。
- protocol、rule、texture、visual、queue evidence。
- safe_auto / manual_only preview actions。
- JSON handoff packet。

`asset_handoff_export_decision_packet` 输出：

- repair preview：safe_auto / manual_only / blocked 的预修复动作。
- owner disposition：TA / Material Owner / Gameplay Owner 的决策状态。
- engine handoff mock：Ready asset 生成 engine import intent，Review asset 进入 held state。
- source handoff packet：保留原始 gate packet 的 artifact 路径。

`engine_handoff_export_preflight_packet` 输出：

- platform preset：当前为 PC Unreal import preset。
- preflight rows：Ready 资产通过 8 条检查，Review 资产保持 held。
- import sidecar：只为 Ready 资产生成 dry-run import sidecar。
- source decision packet：保留 decision packet 的 artifact 路径。

`engine_handoff_export_preset_comparison` 输出：

- preset summaries：PC / Mobile 两套 preset 的 gate、sidecar、held、blocked 计数。
- comparison rows：逐资产列出 PC 与 Mobile 下的状态差异。
- platform split：Ready 资产 PC 可 sidecar，Mobile 因路径/preset 被挡住。
- held across presets：Review 资产两套 preset 都保持 owner-held。

## 验证结果

- `npm run build` 通过。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` package smoke 通过：
  - report version：`maya-asset-handoff-gate@0.1.0`
  - asset count：2
  - ready：1
  - review：1
  - blocked：0
  - preview actions：3
  - package gate：Review
- Maya 2024 `mayapy` decision packet smoke 通过：
  - report version：`maya-asset-handoff-decision-packet@0.1.0`
  - repair actions：2
  - owner dispositions：2
  - owner required：1
  - engine ready/held：1 / 1
  - engine writes：0
- Maya 2024 `mayapy` engine preflight smoke 通过：
  - report version：`maya-engine-handoff-preflight@0.1.0`
  - preflight ready/held：1 / 1
  - import sidecars：1
  - pass/hold checks：8 / 1
  - engine writes：0
- Maya 2024 `mayapy` preset comparison smoke 通过：
  - report version：`maya-engine-handoff-preset-comparison@0.1.0`
  - presets：PC / Mobile
  - platform split / held across presets：1 / 1
  - ready sidecars：1
  - engine writes：0
- smoke artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
```

- decision artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
```

- engine preflight artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-8-engine-handoff-preflight-fixture-20260803-172302.json
```

- engine preset comparison artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-9-engine-preset-comparison-20260803-172927.json
```

- Unreal L3++ inspector artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

- Unreal preset fact comparison artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

## 下一轮

当前主线已推进到 R17：Maya sidecar / preset comparison 已接到 Unreal-side L3++ engine facts 和 waiver policy。下一轮优先把 R17 comparison 做成 Maya 内 reviewer 面板，或推进 Blender L3。
