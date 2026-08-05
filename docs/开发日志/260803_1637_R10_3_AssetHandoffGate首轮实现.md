# 一.问题反馈

前一轮已经把 DCC-first 展示包、业务主线和 GUI 证据清单打通，但作品集仍主要在证明“5 个模块都能跑”。下一步需要一个更像真实 TA 工具的复合闭环：在 Maya 内选择或创建一批资产，一次性判断它们能否进入 publish / review / engine handoff。

# 二.⭐回顾分析

Asset Handoff / Publish Gate 的价值在于把资产交付看成组合判定，而不是单点检查。真实交付需要同时看协议、规则、贴图、视觉和队列证据：

- 协议负责资产语义和平台约束。
- 规则负责 publish gate 和 fix preview。
- 贴图负责材质图、file node、色彩空间和源路径。
- 视觉负责固定 camera/pass review manifest。
- 队列负责 dry-run task events 和 per-asset receipt。

首轮实现选择放在右侧 rail，作为 DCC composite panel，不新增第 6 个并列模块。

# 三.改动解释

- Maya host 新增 `asset_handoff_create_fixture`、`asset_handoff_collect`、`asset_handoff_evaluate_gate`、`asset_handoff_preview_actions`、`asset_handoff_export_packet`。
- `asset_handoff_create_fixture` 创建 2 个 synthetic handoff assets：一个 Ready，一个 Review。
- `asset_handoff_export_packet` 导出 `maya-asset-handoff-gate@0.1.0`，包含 per-asset gate、blocker/review list、协议/规则/贴图/视觉/队列证据和 preview actions。
- AuroraView bridge 新增 5 个 `asset_handoff_*` 方法。
- React 新增右侧 `Asset Handoff Gate` 面板，支持 Fixture / Collect / Evaluate Gate / Preview Actions / Export Packet。
- public case package、DCC-first manifest、README、VALIDATION、长期计划、Maya host README、模块文档已接入 R10.3 artifact。

# 四.计划&状态

已验证：

- `npm run build` 通过，仅保留 Vite large chunk 警告。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` smoke 通过：`maya-asset-handoff-gate@0.1.0`，2 assets，1 Ready，1 Review，0 Blocked，3 preview actions，overall gate 为 Review。
- 最新 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-asset-handoff-gate-20260803-163744.json
```

下一轮：

1. R10.3.4：把 Asset Handoff Gate 接入 Runbook business route 和 GUI evidence shotlist。
2. R10.4：把主线 package、handoff packet 和 GUI 证据整理成可直接投递的 portfolio case page。
