# 一.问题反馈

继续执行 DCC-first 作品集循环开发。R10.7 的目标是把 R10.6 的 Asset Handoff Decision Packet 从右侧单独功能推进到主展示链路，让 reviewer 在 Runbook、Case Page 和 GUI evidence shotlist 中直接看到 repair preview、owner disposition 和 engine handoff mock。

# 二.⭐回顾分析

R10.4/R10.5 已经把 case page 和 GUI media audit 建起来，R10.6 已经能导出 decision packet，但主线仍停在 6 步 Composite Gate。作品集展示需要把“判定后谁处理、能不能进引擎、哪些修复只是预览”纳入同一条 DCC-first 路线，否则这层核心 TA 业务逻辑会被藏在单独按钮里。

# 三.改动解释

- `showcase_runbook_export_package` 已导出 `handoffDecision` 顶层报告，Runbook 版本升级到 `maya-dcc-showcase-runbook-package@1.4.0`。
- `showcase_runbook_build_case_page` 新增 `Owner / Engine Decision` section、decision artifact row 和 decision summary 字段，Case Page 版本升级到 `maya-dcc-portfolio-case-page@1.1.0`。
- GUI evidence manifest 新增第 9 张 `Asset Handoff Decision` 截图目标，GUI media audit 默认扫描 `assets\dcc-first\r10-7-gui-evidence`。
- `DccFirstCasePage` 已展示 7 段 business route、4 个 artifact、9 张 GUI shots 和 owner/engine decision 摘要。
- public package 升级为 `ai-tool-ta-dcc-first-showcase-r10-7` / `dcc-first-package@1.5.0`，同步 README、VALIDATION、模块文档、Maya host README 和长期计划。

最新 artifacts：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```

# 四.计划&状态

已验证：

- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
- `npm run build`
- Maya 2024 `mayapy` case page smoke：6 sections，7 route steps，7 script steps，9 GUI shots，10 required media files，4 artifact rows，6 reviewer claims。
- Maya 2024 `mayapy` media audit smoke：`CapturePending`，present/review/missing 为 0 / 0 / 10。

下一轮自动推进：

1. R10.8：采集真实 Maya GUI screenshots / route recording，回填 `assets\dcc-first\r10-7-gui-evidence`。
2. R10.9：扩展 engine handoff mock 的 import validation 和 platform preset 预演。
3. R10.10：把 owner disposition 做成 reviewer drill，展示 owner-required / waiver / held / ready 的业务边界。
