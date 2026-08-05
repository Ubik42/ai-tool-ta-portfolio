# DCC Showcase Runbook

R9.7/R10 目标：把已完成的 DCC 模块收束成 Maya 内统一演示入口。它不是新的业务工具，而是作品集展示层的证据编排器。

## 核心业务逻辑

展示一个 AI Tool TA 作品集时，最重要的不是逐页讲 UI，而是证明每个模块都有 DCC 上下文、真实 Maya API、可复查 JSON artifact 和明确 gate。Runbook 负责把这些证明点编成一条可重复演示链：

- 演示计划：列出 5 个模块的 GUI 入口、主 API 和证明点。
- synthetic scene：创建公开可复现的 demo fixtures，不依赖内部资产。
- module smoke：按模块执行 DCC API，输出各自 artifact。
- package export：把计划、business route、smoke summary、artifact 列表、Asset Handoff Gate artifact、Asset Handoff Decision Packet、live demo script、GUI checklist、reviewer claims 和最终结论写入统一 JSON。

## 当前实现

代码入口：

- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
- `showcases/portfolio-site/src/components/DccShowcaseRunbookPanel.tsx`
- `showcases/portfolio-site/src/components/DccFirstCasePage.tsx`
- `showcases/portfolio-site/src/lib/auroraviewBridge.ts`

Maya API：

- `showcase_runbook_build_plan`
- `showcase_runbook_run_smoke`
- `showcase_runbook_export_package`
- `showcase_runbook_export_case_page`

React 面板：

- 右侧 rail 的 `DCC Showcase Runbook`
- `Build Plan`
- `Run Smoke`
- `Export Package`
- `Evidence Shotlist`
- DCC-first positioning
- 7 段 business route
- live demo script 列表
- GUI click checklist 折叠清单
- GUI evidence shotlist 折叠清单

`Task Orchestrator` 证据视图中的 `R10.7 DCC-first Case Page` 使用同一组 Runbook / Handoff / Decision / GUI evidence API 导出 `maya-dcc-portfolio-case-page@1.1.0`，通过 `Audit Media` 导出 `maya-dcc-gui-media-audit@0.2.0`。

## Smoke 内容

`showcase_runbook_run_smoke` 会创建 synthetic demo scene fixtures，并运行：

- Asset Protocol：创建 protocol fixture，inspect custom attr payload，导出 `maya-asset-protocol-showcase@1.0.0`。
- Rule Matrix：对明确 publish targets 执行 collect / validate / fix preview / report export。
- Visual Review：创建 review camera rig，生成 pass manifest 和 capture preview。
- Texture Delivery：创建 texture fixture，扫描 file nodes，验证 colorSpace / path / budget。
- Task Orchestrator：创建 ready/review batch assets，生成 dry-run queue 和 receipts。

## 验证结果

- `npm run build` 通过。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` package smoke 通过：
  - plan modules：5
  - smoke modules：5
  - smoke artifacts：5
  - ready：3
  - review：2
  - blocked：0
  - business route steps：7
  - live demo script steps：7
  - GUI checklist items：7
  - GUI evidence shots：9
  - GUI evidence recordings：1
  - additional artifacts：2
  - package gate：Review
- smoke artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
```
- GUI evidence manifest：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
```

- Asset Handoff Gate artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
```

- Case page artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
```

- GUI media audit artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```

- Asset Handoff Decision Packet artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
```

## 当前公开入口

R10 已把 public case package 指向当前 DCC-first artifact：

- `public-case-package/DCC_FIRST_PACKAGE.md`
- `public-case-package/dcc-first-package-manifest.json`

R10.7 已完成：Asset Handoff Decision Packet 已纳入 runbook / case page 主线叙事，reviewer 可以沿 7 步业务路线看到 repair preview、owner disposition 和 engine handoff mock。
