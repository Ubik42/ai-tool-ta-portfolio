# 一.问题反馈

R10.3 首轮已把 `Asset Handoff Gate` 做成右侧 DCC composite panel，但它还只是独立入口。最终展示包需要把它纳入 Runbook business route 和 GUI evidence shotlist，证明它是作品集主线的一部分。

# 二.⭐回顾分析

当前展示逻辑应从“5 个模块都能跑”升级为“5 个模块提供证据流，Asset Handoff Gate 把这些证据流压成一个资产交付判定”。这更接近真实 TA 工具的业务价值：资产是否能 publish，不应靠看多个面板后人工拼结论，而应生成 per-asset Ready / Review / Blocked gate。

# 三.改动解释

- `showcase_runbook_build_plan` 新增 `composite_gate`，指向 `Asset Handoff Gate` 和 `asset_handoff_export_packet`。
- Runbook `presentation_route` 从 5 段升级为 6 段，新增 `Evaluate the composite handoff gate`。
- Runbook live demo script 从 5 步升级为 6 步，新增 handoff gate 演示步骤。
- Runbook GUI click checklist 从 6 项升级为 7 项，新增 `Right rail / Asset Handoff Gate`。
- `showcase_runbook_export_package` 升级为 `maya-dcc-showcase-runbook-package@1.3.0`，导出 package 时同步生成 handoff packet，并写入 `handoffGate` 和 `presentation.additional_artifacts`。
- GUI evidence manifest 升级为 `maya-dcc-gui-evidence-manifest@1.1.0`，截图清单从 7 张升级为 8 张，新增 `Asset Handoff Gate` 截图目标。
- public case package、DCC-first manifest、README、VALIDATION、长期计划、Runbook 模块文档、Asset Handoff 模块文档已指向 R10.3.4 最新 artifacts。

# 四.计划&状态

已验证：

- `npm run build` 通过，仅保留 Vite large chunk 警告。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` smoke 通过：
  - `maya-dcc-showcase-runbook-package@1.3.0`
  - 5 modules，5 module artifacts，1 handoff artifact
  - 6 business route steps，6 script steps，7 checklist items，5 reviewer claims
  - `maya-dcc-gui-evidence-manifest@1.1.0`
  - 8 shots，1 recording，9 required media files
- 最新 artifacts：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-runbook-handoff-package-20260803-164209.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-runbook-handoff-package-asset-handoff-20260803-164209.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-gui-evidence-manifest-20260803-164209.json
```

下一轮：

1. R10.4：把主线 package、handoff packet 和 GUI 证据整理成可直接投递的 portfolio case page。
2. R10.5：采集 R10.3 GUI evidence manifest 中定义的截图和录屏素材。
