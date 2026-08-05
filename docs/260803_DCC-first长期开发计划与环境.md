# DCC-first 长期开发计划与环境

> 更新于 2026-08-04  
> 主线目标：把当前 Web 作品集证据台迁移成 DCC/引擎内真实工具展示。Web 页面保留为索引、证据包和报告浏览器，不再作为最终主展示形态。

跨 DCC / 引擎持续开发框架见：

```text
<repo>\docs\技术报告\260803_1801_跨DCC引擎持续开发框架.md
```

## 一.问题反馈

当前作品集已经有 React 工具台、5 个工具模块和 public case package，但展示载体偏 Web dashboard。最终作品集应尽量在 DCC/引擎内展示工具，尤其是 Maya 内的 shelf / PySide / AuroraView 面板，体现工具管线 TA 的真实业务能力。

## 二.⭐回顾分析

AuroraView 已更新到 `auroraview-v0.5.10`，适合作为长期 DCC 前端宿主：

- Maya / Houdini / Nuke / 3ds Max：走 `QtWebView`。
- Unreal / 非 Qt 宿主：后续走 HWND / native mode。
- React / Vue 前端：可以打包成 `dist` 后通过 `load_file`、`asset_root` 或 `auroraview://` 加载。
- 前端和 Python：通过 `bind_api`、`bind_call`、`emit`、`on` 双向通信。

当前 portfolio 前端依赖很轻，仅 `react`、`react-dom`、`lucide-react`，没有远端接口，适合被嵌入 DCC。迁移前必须保证 Vite 构建资源路径为相对路径。

## 三.开发环境

长期根目录：

```text
<repo>
```

DCC 宿主目录：

```text
<repo>\dcc-hosts\maya-auroraview-host
```

前端目录：

```text
<repo>\showcases\portfolio-site
```

前端构建产物：

```text
<repo>\showcases\portfolio-site\dist\index.html
```

AuroraView 参考仓：

```text
<local-workspace>\_reference\github\_front_end\auroraview
```

Maya 侧依赖安装：

```powershell
"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" -m pip install "auroraview[qt]>=0.5.10"
```

前端构建：

```powershell
cd <repo>\showcases\portfolio-site
npm install
npm run build
```

Maya Script Editor 最小启动：

```python
import sys
host = r"<repo>\dcc-hosts\maya-auroraview-host"
if host not in sys.path:
    sys.path.insert(0, host)

from ai_tool_ta_maya_host import show_portfolio
show_portfolio()
```

## 四.长期开发循环

每一轮只做一个清晰闭环：

1. 读取最新 `docs/开发日志`、技术报告、manifest 和真实 artifact。
2. 选一个高价值业务场景：Maya、Blender、Unreal 或其他目标 DCC/引擎。
3. 准备 synthetic scene / test project / import intent fixture，避免依赖内部资产。
4. 实现确定性核心逻辑：DCC API、engine Python、headless adapter 或协议合约。
5. 接入展示入口：Maya AuroraView、目标 DCC/引擎 runtime smoke，或 Presenter Pack 证据行。
6. 导出 JSON / report / evidence package。
7. 跑可重复验证：`py_compile`、`json.tool`、headless smoke、Unreal/Blender/Maya runtime、前端 build。
8. 更新 README、module doc、public package、技术报告和开发日志。

判断一轮完成的标准：

- 至少产生一个新的真实 DCC/引擎 runtime 证据，或在外部运行时缺失时产生明确的 L2 contract artifact。
- 结果能被 Maya Presenter Pack、目标 DCC/引擎 smoke 或 public package 引用。
- 有可复现 fixture。
- 有导出 JSON。
- 有验证命令记录。
- 有开发日志记录本轮边界、结果和下一轮入口。

## 五.阶段计划

### R9.0 DCC Host Layer

目标：在 Maya 中打开当前 portfolio UI。

- 创建 `maya-auroraview-host`。
- 安装/验证 `auroraview[qt]`。
- 前端 Vite 改为相对路径构建。
- Maya 内用 `QtWebView` 加载 `dist/index.html`。
- 暴露基础 API：`environment_status`、`scene_get_selection`。

### R9.1 Maya Bridge

状态：前端 Bridge 面板初版已完成，等待 Maya GUI 中逐按钮确认。

目标：前端开始感知 live Maya scene。

- 已新增 React AuroraView runtime adapter：探测 `window.auroraview`、监听 `auroraviewready`、封装 `auroraview.api.*` 调用。
- 已新增右侧 `Maya Bridge` 面板。
- 已支持查看当前选择。
- 已支持创建 synthetic asset fixture。
- 已支持向当前选择写入 `aiToolTaProtocol`。
- 已支持 inspect 协议记录。
- 已支持导出 bridge report。

### R9.2 Asset Protocol DCC 化

状态：第三段已完成，Asset Protocol 当前 payload 已接入 Maya Bridge 写入源，Maya `Inspect` 回读结果已能进入 Asset Protocol Workbench，并生成可导出的 DCC evidence report。

目标：把最贴近 Maya TA 的模块先做实。

- 已建立前端 `DccPayloadContext`，业务模块可以发布当前 DCC payload。
- 已让 `Asset Protocol Workbench` 发布当前编辑中的 encoded payload、readiness、diff 和 report。
- 已让 `Maya Bridge` 的 `Write Attr` 使用 active payload，而不是默认样例 payload。
- 已让 `Maya Bridge` 的 `Inspect` 写回 shared scene inspection。
- 已在 `Asset Protocol Workbench` 增加 `DCC Scene Payload` 面板，展示 scene row、protocol row、matched row、stale/match/drift 状态和首个 scene row diff。
- 已在 `Asset Protocol Workbench` 增加 `DCC Evidence Report` 面板，聚合 editor report、active payload、Maya inspect rows、scene diff、validation 和 audit trail。
- 已支持下载 `asset-protocol-dcc-evidence@1.0.0` JSON。
- 已能读取 Maya selection。
- 已能写入 `aiToolTaProtocol` custom attr。
- 已能展示 active payload 与 scene payload before/after。
- 检查命名、平台预算、LOD 语义字段。
- 已能导出 asset protocol report 和 DCC evidence report。

### R9.3 Cross-DCC Rule Matrix DCC 化

状态：第一段已完成，Cross-DCC Rule Matrix 已有 Maya Scene Rule Run 面板和 Maya host `rule_matrix_*` API。

- 已支持从 Maya selection 采集真实 scene facts：transform、mesh shape、triangle/face、shadingEngine、parent/root、`aiToolTaProtocol` schema、LOD、collision、budget。
- 已支持 6 条规则的 Maya validation：Protocol Carrier、Collision Contract、LOD Budget、Material / Texture Sync、Export Root Clean、Publish Manifest。
- 已支持 fix preview，不直接修改场景，区分 `safe_auto` 和 `manual_only`。
- 已支持导出 `maya-rule-matrix-dcc-report@1.0.0` JSON artifact。
- React `Cross-DCC Rule Matrix` 已新增 `Maya Scene Rule Run` 区域，展示 collect facts、validation rows、fix preview、summary gate 和导出路径。
- 后续保留 Blender/Houdini adapter 入口。

### R9.4 Visual Review DCC 化

状态：第一段已完成，Visual Review Studio 已接入 Maya camera rig / pass manifest / capture preview / report export。

- Maya host 已新增 `visual_review_create_camera_rig`、`visual_review_build_pass_manifest`、`visual_review_preview_capture`、`visual_review_export_report`。
- 已支持创建 basic/detail camera rig，共 10 个 review cameras。
- 已支持从 Maya scene meshes 按 `LOD0` / `DT` / other 分桶。
- 已支持 5 个 pass preset：`rb_lod0`、`wb_lod0`、`rb_dt`、`wb_dt`、`solo_b`。
- capture preview 当前只规划输出路径，不强制 playblast，方便 headless smoke 和 GUI 后续扩展。
- React `Visual Review Studio` 已新增 `Maya Capture Setup` 面板，展示 camera / mesh / pass / image / gate、pass rows、output path 和 JSON payload。

### R9.5 Texture Delivery DCC 化

状态：第一段已完成，Texture Delivery Console 已接入 Maya material / texture path inspection / validation / manifest export。

- Maya host 已新增 `texture_delivery_create_fixture`、`texture_delivery_inspect_scene`、`texture_delivery_validate_scene`、`texture_delivery_export_manifest`。
- 已支持创建 synthetic material / file texture fixture，生成 BaseColor、Normal、ORM 三类贴图节点。
- 已支持扫描 Maya mesh、material、shadingEngine、file texture node、贴图路径、role、resolution、colorSpace。
- 已支持 5 条场景验证：Material Binding、Texture Source Paths、Texture Role Naming、Texture Color Space、Texture Platform Budget。
- React `Texture Delivery Console` 已新增 `Maya Texture Inspection` 面板，展示 source rows、validation rows、gate、artifact path 和 JSON payload。
- 已支持导出 `maya-texture-delivery-dcc-report@1.0.0` JSON artifact。

### R9.6 Task Orchestrator DCC 化

状态：第一段已完成，Task Orchestrator 已接入 Maya scene discovery / queue build / dry-run / report export。

- Maya host 已新增 `task_orchestrator_create_fixture`、`task_orchestrator_discover_scene`、`task_orchestrator_build_queue`、`task_orchestrator_run_dry_run`、`task_orchestrator_export_report`。
- 已支持创建 synthetic batch fixture：一个 ready asset 和一个 intentionally review asset。
- 已支持从 Maya scene assets 采集 mesh、protocol、material、texture node、triangle budget、visible state、review/blocker。
- 已支持为每个 asset 生成 5 类任务：Protocol Collect、Material Validate、Texture Validate、Visual Manifest、Evidence Packet Export。
- dry-run 不改场景，输出 task events 和 per-asset receipts。
- React `Task Orchestrator` 已新增 `Maya Batch Queue` 面板，展示 assets、queue tasks、receipts、gate 和 JSON payload。
- 已支持导出 `maya-task-orchestrator-dcc-report@1.0.0` JSON artifact。

### R9.7 DCC Showcase Runbook

状态：第一段已完成，右侧全局 DCC Showcase Runbook 已成为 Maya 内统一演示入口。

- Maya host 已新增 `showcase_runbook_build_plan`、`showcase_runbook_run_smoke`、`showcase_runbook_export_package`。
- `Build Plan` 输出 5 个 DCC 模块的 GUI 入口、核心 API 和证明点。
- `Run Smoke` 创建 synthetic demo scene fixtures，执行 Asset Protocol、Rule Matrix、Visual Review、Texture Delivery、Task Orchestrator 五个模块的 DCC API。
- `Export Package` 导出统一 `maya-dcc-showcase-runbook-package@1.0.0`，内部包含模块计划、smoke summary、模块 artifact 列表和最终展示结论。
- React 右侧 rail 已新增 `DCC Showcase Runbook` 面板，展示 connected state、gate、module rows、artifact rows 和 JSON payload。
- 干净 Maya scene 的 smoke 结果：5 modules，5 artifacts，3 Ready，2 Review，0 Blocked，overall gate 为 Review。

### R10 展示收束

状态：已完成，当前公开展示入口已切到 DCC-first package。

- `showcase_runbook_build_plan` 已新增 live demo script 和 Maya GUI click checklist。
- `showcase_runbook_export_package` 已升级为 `maya-dcc-showcase-runbook-package@1.3.0`，包含 presentation、reviewer claims、evidence requirements、Asset Handoff Gate artifact 和 public case package 指针。
- React `DCC Showcase Runbook` 面板已展示 live demo script 和 GUI click checklist。
- `public-case-package/DCC_FIRST_PACKAGE.md` 已成为当前 reviewer 入口。
- `public-case-package/dcc-first-package-manifest.json` 已记录 DCC-first package id、Maya/AuroraView host、gate、验证 artifact 和命令。
- 最新 Maya 2024 `mayapy` package smoke 结果：5 modules，5 module artifacts，1 handoff artifact，3 Ready，2 Review，0 Blocked，live demo script 6 步，GUI checklist 7 项，overall gate 为 Review。

### R10.1 展示主线压缩

状态：已完成，5 个模块已压成一条资产交付业务主线。

- `showcase_runbook_build_plan` 已新增 `showcase_positioning`，明确工具壳和 5 个模块的关系：壳是 DCC 展示与证据编排层，模块是同一资产发布链路的业务阶段。
- `showcase_runbook_build_plan` 已新增 6 段 `presentation_route`：Author Contract、Publish Gate、Visual Review、Texture Delivery、Batch Handoff、Composite Handoff Gate。
- React `DCC Showcase Runbook` 面板已在模块列表之前展示 positioning 和 business route，让 Maya 内展示从业务问题进入，而不是从功能按钮进入。
- 最新 Maya 2024 `mayapy` package smoke 结果：`maya-dcc-showcase-runbook-package@1.3.0`，6 business route steps，5 modules，5 module artifacts，1 handoff artifact，0 Blocked。

### R10.2 GUI 证据采集清单

状态：已完成，Maya GUI 截图/录屏素材清单已可由 DCC API 导出。

- Maya host 已新增 `showcase_runbook_build_gui_evidence_manifest` 和 `showcase_runbook_export_gui_evidence_manifest`。
- React `DCC Showcase Runbook` 面板已新增 `Evidence Shotlist` 按钮，导出 GUI evidence manifest 并展示截图 target、文件名、must-show 和 acceptance。
- GUI evidence manifest 定义 8 张 Maya 截图、1 段主流程录屏、6 段业务主线和 9 个 required media files。
- 最新 Maya 2024 `mayapy` smoke 结果：`maya-dcc-gui-evidence-manifest@1.1.0`，8 shots，1 recording，6 business route steps。

### R10.3 Asset Handoff / Publish Gate

状态：R10.3.4 已完成，Maya 内右侧 `Asset Handoff Gate` 复合业务入口已接入 Runbook 和 GUI evidence shotlist。

- Maya host 已新增 `asset_handoff_create_fixture`、`asset_handoff_collect`、`asset_handoff_evaluate_gate`、`asset_handoff_preview_actions`、`asset_handoff_export_packet`。
- React 右侧 rail 已新增 `Asset Handoff Gate` 面板，支持 Fixture / Collect / Evaluate Gate / Preview Actions / Export Packet。
- 首轮业务闭环会创建 2 个 synthetic handoff assets，合并协议、规则、贴图、视觉和任务队列证据，输出 per-asset gate 和 handoff actions。
- 最新 Maya 2024 `mayapy` smoke 结果：`maya-asset-handoff-gate@0.1.0`，2 assets，1 Ready，1 Review，0 Blocked，3 preview actions，overall gate 为 Review。
- Runbook package 已把 Asset Handoff Gate 作为第 6 段业务主线和 additional artifact 导出。

### R10.4 DCC-first Case Page

状态：已完成，Runbook、Asset Handoff Gate 和 GUI evidence manifest 已合成可投递 case page。

- Maya host 已新增 `showcase_runbook_build_case_page` 和 `showcase_runbook_export_case_page`。
- React `Task Orchestrator` 证据视图已新增 `R10.4 DCC-first Case Page`，展示业务主线、复合门禁、证据 artifact 和 GUI 采集计划。
- `public-case-package/DCC_FIRST_PACKAGE.md` 和 `public-case-package/dcc-first-package-manifest.json` 已把当前主入口指向 `maya-dcc-portfolio-case-page@1.0.0`。
- 最新 Maya 2024 `mayapy` smoke 结果：5 sections，6 business route steps，6 live demo script steps，8 GUI shots，1 recording，3 supporting artifacts，Asset Handoff Gate 为 Review。
- 最新 case page artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-4-dcc-first-case-page-20260803-165515.json
```

### R10.5 GUI Media Capture Audit

状态：第一段已完成，Maya GUI 素材审计框架已接入；真实截图/录屏仍待采集。

- Maya host 已新增 `showcase_runbook_audit_gui_media` 和 `showcase_runbook_export_gui_media_audit`。
- React `R10.4 DCC-first Case Page` 已新增 `Audit Media` 按钮，导出 `maya-dcc-gui-media-audit@0.1.0`。
- 默认媒体目录为 `<repo>\assets\dcc-first\r10-5-gui-evidence`。
- 当前审计结果为 `CapturePending`：required files 9，present 0，review 0，missing 9。
- 最新 media audit artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-5-gui-media-audit-20260803-165901.json
```

### R10.6 Asset Handoff Decision Packet

状态：第一段已完成，Asset Handoff Gate 已从判定包推进到 TA 决策层。

- Maya host 已新增 `asset_handoff_build_decision_packet` 和 `asset_handoff_export_decision_packet`。
- React 右侧 `Asset Handoff Gate` 面板已新增 `Decision Packet` 按钮。
- Decision packet 在现有 gate 之上补齐 repair preview、owner disposition 和 engine handoff mock。
- 最新 Maya 2024 `mayapy` smoke 结果：`maya-asset-handoff-decision-packet@0.1.0`，2 assets，1 Ready，1 Review，2 repair preview rows，2 owner dispositions，1 engine-ready intent，1 held engine intent，0 engine writes。
- 最新 decision packet artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-6-asset-handoff-decision-packet-20260803-170527.json
```

### R10.7 Decision Packet 主线化

状态：已完成，Decision Packet 已纳入 Runbook / Case Page / GUI evidence shotlist。

- `showcase_runbook_export_package` 已导出 `handoffDecision` 顶层报告，Runbook 版本升级到 `maya-dcc-showcase-runbook-package@1.4.0`。
- `showcase_runbook_build_case_page` 已新增 `Owner / Engine Decision` section、decision artifact row 和 decision summary 字段，case page 版本升级到 `maya-dcc-portfolio-case-page@1.1.0`。
- GUI evidence manifest 已新增第 9 张 `Asset Handoff Decision` 截图目标，版本升级到 `maya-dcc-gui-evidence-manifest@1.2.0`。
- GUI media audit 默认扫描 `<repo>\assets\dcc-first\r10-7-gui-evidence`，版本升级到 `maya-dcc-gui-media-audit@0.2.0`。
- React `R10.7 DCC-first Case Page` 已展示 7 段业务路线、4 个 artifact、9 张 GUI shots 和 owner/engine decision 摘要。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r10-7` / `dcc-first-package@1.5.0`。
- 最新 Maya 2024 `mayapy` smoke 结果：6 sections，7 route steps，7 script steps，9 GUI shots，10 required media files，4 artifact rows，6 reviewer claims，decision repair actions 2，owner required 1，engine ready/held 1 / 1。
- 最新 R10.7 artifacts：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```

### R10.8 Engine Handoff Preflight

状态：已完成，engine handoff mock 已推进到平台 preset 预检和 dry-run sidecar。

- Maya host 已新增 `engine_handoff_build_preflight_packet` 和 `engine_handoff_export_preflight_packet`。
- React 右侧 `Asset Handoff Gate` 面板已新增 `Engine Preflight` 按钮。
- 当前 PC Unreal preset 会检查 engine path、platform、LOD、triangle budget、texture budget、protocol carrier 和 receipt state。
- Ready 资产生成 1 个 dry-run import sidecar；Review 资产保持 owner-held，不进入 sidecar。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r10-8` / `dcc-first-package@1.6.0`。
- 最新 Maya 2024 `mayapy` smoke 结果：2 preflight rows，1 preflight-ready，1 held，1 import sidecar，8 pass checks，1 hold check，0 engine writes。
- 最新 R10.8 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-8-engine-handoff-preflight-fixture-20260803-172302.json
```

### R10.9 Engine Preset Comparison

状态：已完成，PC / Mobile engine preflight preset 对比已接入。

- Maya host 已新增 `engine_handoff_build_preset_comparison` 和 `engine_handoff_export_preset_comparison`。
- React 右侧 `Asset Handoff Gate` 面板已新增 `Preset Compare` 按钮。
- 当前对比同一批 engine handoff intents 在 PC / Mobile preset 下的 gate、sidecar、held、blocked 差异。
- Ready 资产在 PC 下生成 dry-run sidecar，在 Mobile 下因 engine path prefix 与 platform preset 不匹配被挡住。
- Review 资产跨 PC / Mobile 都保持 owner-held。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r10-9` / `dcc-first-package@1.7.0`。
- 最新 Maya 2024 `mayapy` smoke 结果：2 presets，2 comparison rows，1 platform split，1 held-across-presets，1 ready sidecar，0 engine writes。
- 最新 R10.9 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-9-engine-preset-comparison-20260803-172927.json
```

### R11 DCC Presenter Pack

状态：已完成，当前 DCC-first 证据链已收束成 Maya 内可一键导出的展示包。

- Maya host 已新增 `dcc_presentation_build_pack` 和 `dcc_presentation_export_pack`。
- React `R11 DCC Presenter Pack` 页面已新增 `Presenter Pack` 按钮，导出后展示 gate、证据文件 present/missing、GUI media present/review/missing 和 artifact path。
- Presenter Pack 探测 11 个关键证据文件：public manifest、DCC package readme、Maya host readme、case page、runbook、GUI evidence manifest、GUI media audit、Asset Handoff Gate、Decision Packet、Engine Preflight、Engine Preset Comparison。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r11` / `dcc-first-package@1.8.0`。
- 当前总 gate 为 `CapturePending`：代码、JSON artifact、展示路线都存在；真实 Maya 截图/录屏仍缺 10 个媒体文件。
- 最新 R11 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r11-dcc-presentation-pack-20260803-174307.json
```

### R12 Blender Rule Adapter / Cross-DCC Presenter Pack

状态：第一段已完成，作品集已加入首个非 Maya 证据行。

- 新增 `dcc-hosts/blender-rule-adapter`，包含公开 synthetic fixture、纯 Python adapter contract、smoke 脚本和 artifact 输出。
- Blender adapter 把 object custom properties、collections、material slots、UV evidence、collision proxy hints 归一化为 Cross-DCC Rule Matrix 输入。
- fixture 包含 2 个公开安全资产：1 个 Ready、1 个 intentionally Blocked，用于证明失败路径和 fix preview 不是口头描述。
- 当前证据等级为 L2：本机未找到 Blender CLI，不能声称真实 `bpy` headless smoke；L3 升级条件是安装 Blender 后运行 `blender --background --python`。
- Maya Presenter Pack 已探测 Blender adapter artifact，证据文件从 11 提升到 12，demo route 从 6 提升到 7。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r12` / `dcc-first-package@1.9.0`。
- 最新 Blender adapter artifact：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260803-180736.json
```

- 最新 R12 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r12-cross-dcc-presentation-pack-20260803-180759.json
```

### R13 Unreal Handoff Inspector / Engine Evidence

状态：第一段已完成，作品集已加入首个 engine-side 证据行。

- 新增 `dcc-hosts/unreal-handoff-inspector`，包含公开 synthetic Unreal handoff fixture、纯 Python inspector contract、smoke 脚本和 artifact 输出。
- Unreal inspector 把 DCC import intent 放到 Unreal Content Registry / AssetImportTask 语义下检查：mount root、platform preset、asset class、source fingerprint、content conflict、material dependencies、LOD policy、collision policy、owner state、Python plugin readiness。
- fixture 包含 2 个公开安全 import intents：1 个 import-ready dry-run command，1 个 intentionally Blocked import。
- 当前证据等级为 L2：本机已找到 `UnrealEditor-Cmd.exe`，但没有配置测试 `.uproject`；L3 升级条件是设置 `AI_TOOL_TA_UNREAL_PROJECT` 后运行 Unreal Python smoke。
- Maya Presenter Pack 已探测 Unreal inspector artifact，证据文件从 12 提升到 13，demo route 从 7 提升到 8。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r13` / `dcc-first-package@1.10.0`。
- 最新 Unreal inspector artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-contract-20260803-181658.json
```

- 最新 R13 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r13-engine-presentation-pack-20260803-181814.json
```

### R14 Unreal Handoff Inspector L3

状态：已完成，Unreal engine-side 证据从 L2 contract 升级为真实 Unreal Python L3 smoke。

- 新增公开最小 Unreal project：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\projects\AI_Tool_TA_Unreal_L3\AI_Tool_TA_Unreal_L3.uproject
```

- 新增 `scripts\run_unreal_l3_smoke.py`，调用 `UnrealEditor-Cmd.exe -run=pythonscript`。
- 新增 Unreal 内执行脚本 `scripts\unreal_python\run_l3_inspection.py`，在 Unreal Python 中导出同 schema 报告。
- L3 artifact 记录 Unreal 5.3.2、Python 3.9.7、Asset Registry queried、0 engine writes、0 asset writes。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r14` / `dcc-first-package@1.11.0`。
- 最新 Unreal L3 artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-182430.json
```

- 最新 R14 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r14-unreal-l3-presentation-pack-20260803-182540.json
```

### R15 Unreal Registry Fixture

状态：已完成，Unreal engine-side 证据从 L3 runtime query 升级为 L3+ real registry fixture。

- `run_l3_inspection.py` 在公开 test project 内导入 `SM_HeroPanel_A.obj`，生成 `/Game/AI_Tool_TA/Props/SM_HeroPanel_A` StaticMesh。
- 同脚本创建 `/Game/AI_Tool_TA/Materials/M_HeroPanel` Material。
- Artifact 记录 Asset Registry queried、2 / 2 expected path-class rows matched、0 missing、0 class mismatch。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r15` / `dcc-first-package@1.12.0`。
- 最新 Unreal L3+ artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-183417.json
```

- 最新 R15 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r15-unreal-registry-fixture-presentation-pack-20260803-183547.json
```

### R16 Unreal Engine Facts

状态：已完成，Unreal engine-side 证据从 L3+ registry fixture 升级为 L3++ engine fact evidence。

- `unreal-handoff-inspector-contract` 升级到 `@0.4.0`。
- `run_l3_inspection.py` 在 Unreal Python 中读取 StaticMesh source import data、material slot assignment、LOD count 和 collision settings。
- Artifact 记录 engine facts 4 / 4 matched：source import matched、material assigned、LOD count = 1、simple collision shape count = 1。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r16` / `dcc-first-package@1.13.0`。
- Presenter Pack 已收束 Unreal L3++、Blender L2、case page、GUI audit、handoff gate、engine preflight 和 preset comparison。
- 最新 Unreal L3++ artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

- 最新 R16 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r16-unreal-engine-facts-presentation-pack-20260803-184326.json
```

### R17 Unreal Preset Fact Comparison

状态：已完成，Unreal engine facts 已接入 PC / Mobile preset policy 和 exception waiver。

- 新增 `unreal-preset-fact-comparison@0.1.0`。
- `synthetic_unreal_handoff.json` 新增 preset path prefix 和 `exceptionWaivers`。
- `run_preset_fact_compare.py` 读取 R16 L3++ artifact，输出 matched / drift / waived / blocked。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r17` / `dcc-first-package@1.14.0`。
- Presenter Pack 证据文件从 13 个升级到 14 个。
- 最新 Unreal preset fact comparison artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

- 最新 R17 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r17-unreal-preset-facts-presentation-pack-20260803-185425.json
```

### R18 Unreal Preset Fact Review

状态：已完成，R17 preset comparison 已投影成 Maya/AuroraView 内 reviewer queue。

- 新增 `maya-unreal-preset-fact-review@0.1.0`。
- `MayaPortfolioApi` 新增 `unreal_preset_fact_review_load` / `unreal_preset_fact_review_export`。
- `DccFirstCasePage` 新增 `Preset Facts` 按钮和 reviewer 面板，展示 preset summary、asset platform split、fact rows、owner action 和 waiver expiry。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r18` / `dcc-first-package@1.15.0`。
- Presenter Pack 证据文件从 14 个升级到 15 个，demo route 从 8 段升级到 9 段。
- 最新 Unreal preset fact review artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json
```

- 最新 R18 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-presentation-pack-20260803-190613.json
```

### R19 Scene Transaction Guard

状态：已完成，DCC 工具执行前后的 scene mutation 已变成 Maya 内可导出的 transaction receipt。

- 新增 `maya-scene-transaction-guard@0.1.0`。
- `MayaPortfolioApi` 新增 `scene_transaction_create_fixture` / `scene_transaction_capture_state` / `scene_transaction_run_guard` / `scene_transaction_export_receipt`。
- `DccFirstCasePage` 新增 `Txn Guard` 按钮和 Scene Transaction Guard 面板，展示 before/after fingerprint、created/deleted/modified rows、selection/time context、risk rows 和 rollback preview。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r19` / `dcc-first-package@1.16.0`。
- Presenter Pack 证据文件从 15 个升级到 16 个，demo route 从 9 段升级到 10 段。
- 最新 Scene Transaction Guard artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-20260804-195730.json
```

- 最新 R19 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-presentation-pack-20260804-195754.json
```

### R20 Blender L3 Harness

状态：已完成 readiness 闭环，真实 Blender L3 运行被本机缺 `blender.exe` 明确阻塞。

- 新增 `blender_rule_adapter\bpy_collector.py`，在 Blender runtime 中创建公开 synthetic scene，采集 object custom properties、collections、material slots、textures 和 UV layers。
- 新增 `scripts\run_blender_l3.py`，用于 `blender --background --python`。
- 新增 `scripts\run_l3_smoke.py`，普通 Python 下先定位 Blender CLI；找不到时导出 readiness artifact，不冒充 L3 成功。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r20` / `dcc-first-package@1.17.0`。
- Presenter Pack 证据文件从 16 个升级到 17 个，demo route 从 10 段升级到 11 段。
- 最新 Blender L3 readiness artifact：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-readiness-20260804-201125.json
```

- 最新 R20 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r20-blender-l3-harness-presentation-pack-20260804-201419.json
```

### R21 3ds Max Rule Adapter

状态：已完成 L2+ contract 和 opt-in L3 readiness 闭环，真实 Max batch 运行等待 operator 显式允许。

- 新增 `dcc-hosts\3dsmax-rule-adapter`。
- 从 Lightbox 3ds Max Pyblish 类插件经验提炼 user properties、layer/export root、LOD suffix、material slot、map channel、transform、collision proxy 等核心业务事实。
- 新增 `max_rule_adapter\contract.py`，把公开 synthetic fixture 转成 `cross-dcc-rule-input@0.1.0`。
- 新增 `max_rule_adapter\runtime_collector.py` 和 `scripts\run_3dsmax_l3.py`，提供真实 `pymxs` collector 路径。
- 新增 `scripts\run_l3_smoke.py`，普通 Python 下定位 `3dsmaxbatch.exe` 并导出 readiness；默认不启动 3ds Max batch。
- public package 已升级到 `ai-tool-ta-dcc-first-showcase-r21` / `dcc-first-package@1.18.0`。
- Presenter Pack 证据文件从 17 个升级到 19 个，demo route 从 11 段升级到 12 段。

最新 3ds Max adapter artifact：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
```

最新 3ds Max L3 readiness artifact：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-readiness-20260804-220959.json
```

最新 R21 Presenter Pack artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r21-3dsmax-rule-adapter-presentation-pack-20260804-221449.json
```

## 六.当前优先级

立即推进顺序：

1. 3ds Max runtime：在 operator 明确允许后运行 `python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py --run-runtime`，把 R21 readiness 转成真实 `max-rule-adapter-pymxs-l3@0.1.0`。
2. 跨 DCC 证据：安装或定位 Blender CLI 后复跑 `python dcc-hosts/blender-rule-adapter/scripts/run_l3_smoke.py`，把 R20 readiness 转成真实 `blender-rule-adapter-bpy-l3@0.1.0`。
3. GUI media：采集真实 Maya 截图/录屏素材到 `assets\dcc-first\r10-7-gui-evidence`，让 audit 从 `CapturePending` 进入可审核媒体包。
4. 下一条 adapter：如果不启动 Max/Blender runtime，选择 Houdini / MotionBuilder 建公开 fixture contract。
5. 业务扩展暂停：owner disposition drill 等边缘功能先不做，避免从跨 DCC / 引擎展示目标漂移。

R10.3 具体计划见 `docs/260803_R10_3_AssetHandoffPublishGate开发计划.md`。

Task Orchestrator 暂停继续追加 R8.x 报告，只保留为证据治理和 public package 索引。

## 七.当前环境验证

已完成：

- `<local-workspace>\_reference\github\_front_end\auroraview` 更新到 `auroraview-v0.5.10`。
- Maya 2024 `mayapy` 已安装 `auroraview[qt]>=0.5.10`。
- `auroraview 0.5.10`、`QtWebView`、`qtpy`、`_core` 导入正常。
- `showcases/portfolio-site` 已设置 `base: "./"`，`dist/index.html` 已生成相对资源路径。
- `npm run build` 通过，仅保留 Vite 大 chunk 警告。
- `maya-auroraview-host` Python 包 `py_compile` 通过。
- Maya GUI 已由用户手动验证：`show_portfolio()` 能正确弹出 AuroraView 界面并加载 portfolio UI。
- React 右侧 `Maya Bridge` 面板已接入 6 个 Python API 按钮。
- R9.2 已把 `Asset Protocol Workbench` 当前 payload 接入 `Maya Bridge` 写入源。
- R9.2 已把 Maya `Inspect` 回读结果接回 `Asset Protocol Workbench`。
- R9.2 已新增 `DCC Evidence Report` 面板和导出。
- R9.3 已把 `Cross-DCC Rule Matrix` 接入 Maya scene collect / validate / fix preview / report export。
- R9.4 已把 `Visual Review Studio` 接入 Maya review camera rig / pass manifest / capture preview / report export。
- R9.5 已把 `Texture Delivery Console` 接入 Maya texture fixture / inspection / validation / manifest export。
- R9.6 已把 `Task Orchestrator` 接入 Maya scene discovery / queue build / dry-run / report export。
- R9.7 已新增全局 `DCC Showcase Runbook`，可在 Maya 内生成演示计划、运行 5 模块 DCC smoke、导出统一 package。
- R10 已把 `DCC Showcase Runbook` 升级为当前公开展示入口，并将 public case package 指向 DCC-first package。
- R10.7 已把 5 个模块、Asset Handoff Gate、Asset Handoff Decision Packet 压成 7 段资产交付业务主线，当前导出 `maya-dcc-showcase-runbook-package@1.4.0`。
- R10.7 已新增 GUI evidence manifest 导出，当前生成 9 张截图和 1 段录屏的 Maya GUI 采集清单。
- R10.7 已升级 DCC-first case page，当前导出 `maya-dcc-portfolio-case-page@1.1.0`。
- R10.7 已升级 GUI media audit，当前导出 `maya-dcc-gui-media-audit@0.2.0`，状态为 `CapturePending`。
- R10.6/R10.7 已新增并主线化 Asset Handoff Decision Packet，当前导出 `maya-asset-handoff-decision-packet@0.1.0`。
- R10.8 已新增 Engine Handoff Preflight，当前导出 `maya-engine-handoff-preflight@0.1.0`。
- R10.9 已新增 Engine Preset Comparison，当前导出 `maya-engine-handoff-preset-comparison@0.1.0`。
- R11 已新增 DCC Presenter Pack，当前导出 `maya-dcc-presentation-pack@0.1.0`。
- R12 已新增 Blender Rule Adapter L2 合约并纳入 Cross-DCC Presenter Pack。
- R13 已新增 Unreal Handoff Inspector L2 合约并纳入 Cross-DCC / Engine Presenter Pack。
- R14 已将 Unreal Handoff Inspector 升级为 `UnrealEditor-Cmd.exe -run=pythonscript` L3 smoke。
- R15 已将 Unreal Handoff Inspector 升级为 L3+ registry fixture：StaticMesh / Material 两条真实 Asset Registry row 匹配。
- R16 已将 Unreal Handoff Inspector 升级为 L3++ engine facts：source import、material slot、LOD、collision 四类真实 StaticMesh fact 匹配。
- R17 已新增 Unreal Preset Fact Comparison：10 条 PC / Mobile preset fact rows 输出 7 matched、1 drift、1 waived、1 blocked。
- R18 已新增 Unreal Preset Fact Review：Maya 内 reviewer queue 输出 10 rows、3 attention rows、1 blocked、1 waiver。
- R19 已新增 Scene Transaction Guard：Maya 内 transaction receipt 输出 2 created、2 deleted、2 modified、9 rollback actions、4 risk rows。
- R20 已新增 Blender L3 readiness harness：collector ready、Blender CLI missing gate、Presenter Pack 17 / 17 evidence files、11 demo route steps。
- R21 已新增 3ds Max Rule Adapter：L2+ contract 输出 2 assets、13 pass、5 warning、2 error；L3 readiness 发现 `3dsmaxbatch.exe`、collector ready、Presenter Pack 19 / 19 evidence files、12 demo route steps。
- R10.3 已新增 `Asset Handoff Gate` 复合业务入口，导出 `maya-asset-handoff-gate@0.1.0`。
- Maya 2024 `mayapy` headless smoke 通过：
  - 创建 `ai_tool_ta_fixture1`。
  - 创建 `hero_prop_body1` / `hero_prop_socket1`。
  - 写入 `aiToolTaProtocol` custom attr。
  - inspect 返回 2 条协议记录。
  - 导出 smoke report：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-headless-smoke-20260803-114155.json
```

R9.1 前端 Bridge smoke report：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-bridge-panel-smoke-20260803-152358.json
```

R9.2 active payload smoke report：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-2-active-payload-smoke-20260803-152936.json
```

R9.2 inspect feedback smoke report：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-2-inspect-feedback-smoke-20260803-154209.json
```

R9.2 DCC evidence report smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-2-dcc-evidence-report-smoke-20260803-154521.json
```

R9.3 Rule Matrix DCC smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-3-rule-matrix-smoke-20260803-155309.json
```

R9.4 Visual Review DCC smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-4-visual-review-smoke-20260803-155811.json
```

R9.5 Texture Delivery DCC smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-5-texture-delivery-smoke-20260803-160419.json
```

R9.6 Task Orchestrator DCC smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-6-task-orchestrator-smoke-20260803-161017.json
```

R9.7 DCC Showcase Runbook package smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-7-dcc-showcase-runbook-package-20260803-161632.json
```

R10.3.4 DCC-first runbook handoff package smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-runbook-handoff-package-20260803-164209.json
```

R10.3.4 GUI evidence manifest smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-gui-evidence-manifest-20260803-164209.json
```

R10.3.4 Asset Handoff Gate package smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-runbook-handoff-package-asset-handoff-20260803-164209.json
```

R10.4 DCC-first case page smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-4-dcc-first-case-page-20260803-165515.json
```

R10.4 supporting artifacts：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-4-dcc-first-case-page-runbook-20260803-165515.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-4-dcc-first-case-page-runbook-asset-handoff-20260803-165515.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-4-dcc-first-case-page-gui-evidence-20260803-165515.json
```

R10.5 GUI media audit smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-5-gui-media-audit-20260803-165901.json
```

R10.6 Asset Handoff Decision Packet smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-6-asset-handoff-decision-packet-20260803-170527.json
```

R10.7 DCC-first case page smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
```

R10.7 supporting artifacts：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```

R10.8 Engine Handoff Preflight smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-8-engine-handoff-preflight-fixture-20260803-172302.json
```

R10.9 Engine Preset Comparison smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-9-engine-preset-comparison-20260803-172927.json
```

R11 DCC Presenter Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r11-dcc-presentation-pack-20260803-174307.json
```

R12 Blender Rule Adapter smoke：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260803-180736.json
```

R12 Cross-DCC Presenter Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r12-cross-dcc-presentation-pack-20260803-180759.json
```

R13 Unreal Handoff Inspector smoke：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-contract-20260803-181658.json
```

R13 Cross-DCC / Engine Presenter Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r13-engine-presentation-pack-20260803-181814.json
```

R14 Unreal Handoff Inspector L3 smoke：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-182430.json
```

R14 Cross-DCC / Engine Presenter Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r14-unreal-l3-presentation-pack-20260803-182540.json
```

R15 Unreal Handoff Inspector L3+ registry fixture smoke：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-183417.json
```

R15 Cross-DCC / Engine Presenter Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r15-unreal-registry-fixture-presentation-pack-20260803-183547.json
```

R16 Unreal Handoff Inspector L3++ engine facts smoke：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

R16 Cross-DCC / Engine Presenter Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r16-unreal-engine-facts-presentation-pack-20260803-184326.json
```

R17 Unreal Preset Fact Comparison smoke：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

R17 Cross-DCC / Engine Presenter Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r17-unreal-preset-facts-presentation-pack-20260803-185425.json
```

R18 Unreal Preset Fact Review smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json
```

R18 Cross-DCC / Engine Reviewer Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-presentation-pack-20260803-190613.json
```

R19 Scene Transaction Guard smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-20260804-195730.json
```

R19 Cross-DCC / Engine Reviewer Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-presentation-pack-20260804-195754.json
```

R20 Blender L3 readiness smoke：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-readiness-20260804-201125.json
```

R20 Cross-DCC / Engine Reviewer Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r20-blender-l3-harness-presentation-pack-20260804-201419.json
```

R21 3ds Max Rule Adapter smoke：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
```

R21 3ds Max L3 readiness smoke：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-readiness-20260804-220959.json
```

R21 Cross-DCC / Engine Reviewer Pack smoke：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r21-3dsmax-rule-adapter-presentation-pack-20260804-221449.json
```

待进入 Maya GUI 验证：

- 右侧 `Maya Bridge` 面板的 `Status`、`Selection`、`Fixture`、`Write Attr`、`Inspect`、`Export` 按钮逐项点击结果。
- 切换 Asset Protocol fixture / 修改字段后，`Maya Bridge` 的 `Active Payload` 是否同步变化。
- 点 `Inspect` 后，`Asset Protocol Workbench` 内 `DCC Scene Payload` 是否显示节点 match/drift/missing 和 diff。
- 点 `Export DCC Evidence` 后，浏览器下载的 JSON 是否包含 active payload、scene evidence、validation evidence。
- 点 `Task Orchestrator` 证据视图的 `Preset Facts` 后，是否展示 10 条 fact rows、3 条 review queue、PC waiver 和 Mobile blocked/drift row。
- 点 `Task Orchestrator` 证据视图的 `Txn Guard` 后，是否展示 transaction summary、risk rows、rollback preview 和 generated artifact path。
- 点 `Task Orchestrator` 证据视图的 `Presenter Pack` 后，是否展示 19 个 evidence file probes、Unreal inspector evidence row、Unreal preset fact comparison/review rows、Blender adapter evidence row、Blender L3 readiness gate、3ds Max adapter evidence row、Max L3 readiness gate 和 `CapturePending` media gate。
- 切到 `Cross-DCC Rule Matrix`，点 `Collect Scene` / `Validate Scene` / `Preview Fixes` / `Export DCC Report`，确认 Maya Scene Rule Run 面板回写结果。
- 切到 `Visual Review Studio`，点 `Create Rig` / `Build Manifest` / `Preview Capture` / `Export DCC Review`，确认 Maya Capture Setup 面板回写结果。
- 切到 `Texture Delivery Console`，点 `Create Fixture` / `Inspect Textures` / `Validate Scene` / `Export Manifest`，确认 Maya Texture Inspection 面板回写结果。
- 切到 `Task Orchestrator`，点 `Create Fixture` / `Discover Scene` / `Build Queue` / `Dry Run` / `Export Report`，确认 Maya Batch Queue 面板回写结果。
- 在右侧 `DCC Showcase Runbook` 点 `Build Plan` / `Run Smoke` / `Export Package`，确认统一演示包回写结果。
- 关闭、resize、重复打开是否稳定。

## R22 当前断点：Blender / 3ds Max runtime L3 与 Maya 外控入口

时间：2026-08-05 15:40

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r22 / dcc-first-package@1.19.0
```

本轮已把 Blender 和 3ds Max 从 readiness 升到真实 runtime L3：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260805-153232.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r22-blender-max-l3-presentation-pack-20260805-153957.json
```

验证结论：

- Blender：`blender-rule-adapter-bpy-l3@0.1.0`，Blender 5.2.0 LTS background，`bpy_scene_collected`。
- 3ds Max：`max-rule-adapter-pymxs-l3@0.1.0`，3ds Max 2022 batch，`pymxs_scene_collected`，runtime object count 4。
- Presenter Pack：19 / 19 evidence files present，0 missing required files，12 demo route steps。
- Gate：`CapturePending`，只因为 Maya GUI 9 张 PNG 和 1 段 MP4 未采集。
- Blender/Max adapter gate 为 `Blocked` 是 synthetic fixture 中故意放一个失败资产，代表发布阻断业务逻辑，不是 runtime 缺失。

Maya 外控入口：

```text
<repo>\dcc-hosts\maya-auroraview-host\ai_tool_ta_maya_host\external_control.py
<repo>\dcc-hosts\maya-auroraview-host\scripts\start_maya_command_bridge.py
<repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py
```

使用方式：

```python
exec(open(r"<repo>\dcc-hosts\maya-auroraview-host\shelf\install_shelf_button.py", "r").read())
```

安装后 shelf 有 `AI Tool TA` 和 `TA Bridge` 两个按钮。每个 Maya 会话点击一次 `TA Bridge` 后，外部 shell 可以执行：

```powershell
python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --show-portfolio
python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --export-presenter-pack r22-blender-max-l3-presentation-pack
```

下一轮入口：

1. 采集 Maya GUI 截图/录屏，让 media gate 从 `CapturePending` 变成可审核。
2. 开 `Animation Continuity Lab`，先做 animation intent schema、headless fixture、Maya animation fact collector。
3. 后续接 MotionBuilder / Unreal runtime 对照，再开 Character Calibration 和 Spatial Authoring。

## R23 循环开发执行规则：轻量验证优先

本工程进入长期循环开发后，每轮只闭环一个高价值业务任务。默认不做全量重型检测，按变更范围选择验证档位：

```powershell
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
.\scripts\validate_loop.ps1 -Tier ui
.\scripts\validate_loop.ps1 -Tier animation
.\scripts\validate_loop.ps1 -Tier spatial-authoring
.\scripts\validate_loop.ps1 -Tier blender
.\scripts\validate_loop.ps1 -Tier max
.\scripts\validate_loop.ps1 -Tier full
```

验证策略详见：

```text
<repo>\docs\技术报告\260805_长期循环开发框架与轻量验证策略.md
```

R23 已完成 `Animation Continuity Lab` Maya L3：

```text
<repo>\dcc-hosts\animation-continuity-lab\artifacts\animation-continuity-maya-l3-20260805-162744.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r23-animation-continuity-l3-presentation-pack-20260805-163040.json
```

R23 结果：Maya 2026 `mayapy` keyed animCurve facts collected，2 animation takes，1 Ready / 1 Blocked，11 pass / 3 warning / 6 error；Presenter Pack 20 / 20 evidence files present，0 missing required files，13 demo route steps。

R24 已完成 `Unreal Animation Bridge` L3-readiness：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-readiness-20260805-164730.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r24-unreal-animation-bridge-presentation-pack-20260805-164953.json
```

R24 结果：Unreal 5.3.2 Python runtime probe collected，`AnimSequence` / `AnimSequenceFactory` / `Skeleton` / `SkeletalMesh` API 可见，2 个 expected AnimSequence 资产缺失；Bridge gate 为 `Blocked`，这代表 public skeletal animation fixture 未补，不是 runtime 没跑。

默认下一轮开发 `Unreal AnimSequence Fixture L3` 或 `Character Calibration & Intent Transfer Studio`：

```text
public skeleton/sequence fixture -> Unreal runtime collector -> continuity comparison -> Presenter Pack row -> docs
```

只有修改 runtime adapter 时才跑对应 DCC runtime；只有发布里程碑才跑 `full`；只改文档或 manifest 时不跑 Blender/Max/Unreal。

## R25 循环开发断点：Unreal Animation Bridge import L3

R25 已完成 `Unreal Animation Bridge` import L3：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-contract-20260805-173354.json
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-readiness-20260805-173401.json
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-import-l3-20260805-173309.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r25-unreal-animation-import-l3-presentation-pack-20260805-173624.json
```

R25 结果：Maya 2026 `mayapy` + `fbxmaya` 生成两段 public synthetic FBX；Unreal 5.3.2 `UnrealEditor-Cmd.exe` 通过 `AssetImportTask` + `FbxImportUI` 导入并保存 synthetic Skeleton / SkeletalMesh / AnimSequence；2 / 2 expected sequences present，4 imported assets，1 Ready clip，1 intentionally Blocked clip。Bridge gate 的 `Blocked` 来自 `Attack_A` 业务故障样本，不是 runtime 或 fixture 缺失。

默认下一轮开发 `Character Calibration & Intent Transfer Studio`：

```text
topology / joint coverage fixture -> Maya collector -> calibration rule evaluation -> Presenter Pack row -> docs
```

## R26 循环开发断点：Character Calibration Maya L3

R26 已完成 `Character Calibration & Intent Transfer Studio` Maya L3：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-contract-20260805-175045.json
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r26-character-calibration-l3-presentation-pack-20260805-175238.json
```

R26 结果：Maya 2026 `mayapy` 生成 public synthetic character meshes / joint DAG / custom attrs，并采集 topology signature、joint coverage、skin influence budget、calibration delta、face parameters、Control Rig mapping 和 mirror pair coverage。结果为 2 character rows，1 Ready，1 intentionally Blocked，10 pass / 2 warning / 6 error。Bridge gate 的 `Blocked` 来自临时角色样本的业务故障，不是 Maya runtime 缺失。

默认下一轮开发 `Spatial Authoring & Pose Transfer Workbench`：

```text
socket / hotspot / pose frame fixture -> Maya collector -> pose transfer rule evaluation -> Presenter Pack row -> docs
```

## R27 循环开发断点：Spatial Authoring Maya L3

R27 已完成 `Spatial Authoring & Pose Transfer Workbench` Maya L3：

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-contract-20260805-181516.json
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-maya-l3-20260805-181524.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r27-spatial-authoring-l3-presentation-pack-20260805-181612.json
```

R27 结果：Maya 2026 `mayapy` 生成 public synthetic joints / locator DAG / custom attrs，并采集 socket parent joint、local offset、mirror pair、hotspot semantic/owner、pose frame coverage、local space、preview locator 和 pose transfer approval。结果为 2 spatial authoring rows，1 Ready，1 intentionally Blocked，11 pass / 2 warning / 7 error。Bridge gate 的 `Blocked` 来自临时背包样本的业务故障，不是 Maya runtime 缺失。

默认下一轮开发 `Platform Variant Forge`：

```text
PC/Mobile policy fixture -> variant plan contract -> preset comparison reuse -> optional Unreal material/LOD fact probe -> Presenter Pack row -> docs
```

## R28 循环开发断点：Platform Variant Forge

R28 已完成 `Platform Variant Forge` L3-linked 首版：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-forge-contract-20260805-183315.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r28-platform-variant-forge-presentation-pack-20260805-183402.json
```

R28 结果：普通 Python smoke 读取 public-safe PC/Mobile variant fixture，并连接已有 Unreal preset fact comparison L3++ artifact。报告覆盖 target engine path、owner approval、triangle / texture memory / material slot / draw call budget、LOD coverage、Nanite policy、shader feature downgrade 和 collision simplification policy。结果为 2 source assets，3 platform variants，2 Ready，1 intentionally Blocked Mobile variant，21 pass / 1 warning / 8 error。`Blocked` 来自 Mobile 临时背包样本的业务故障，不是证据链缺失。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r28 / dcc-first-package@1.25.0
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier platform-variant
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Platform Variant Unreal Runtime Probe`：

```text
variant plan artifact -> Unreal StaticMesh / material / texture / collision fact probe -> runtime-vs-plan comparison -> Presenter Pack row -> docs
```

## R29 循环开发断点：Platform Variant Unreal Runtime Probe

R29 已完成 `Platform Variant Unreal Runtime Probe` L3：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-unreal-runtime-20260805-185026.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r29-platform-variant-unreal-runtime-presentation-pack-20260805-185113.json
```

R29 结果：`run_unreal_runtime_probe.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public test project，读取 R28 variant plan 后用 Unreal Python 采集 StaticMesh / material slot / LOD / Nanite / collision runtime facts。结果为 3 variants，0 Ready，2 Review，1 intentionally Blocked，21 pass / 4 warning / 2 error。`Review` 来自真实 runtime drift：PC/Mobile HeroPanel 已存在但 runtime LOD 数不足，PC Nanite 策略未满足；`Blocked` 来自 synthetic vehicle TMP 样本缺失源资产和目标资产。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r29 / dcc-first-package@1.26.0
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier platform-variant-unreal
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Platform Variant Auto LOD / Material Bake Planner`：

```text
runtime drift artifact -> LOD/material/texture fix plan -> Unreal Python generation contract -> Presenter Pack row -> docs
```

## R30 循环开发断点：Platform Variant Auto LOD / Material Bake Planner

R30 已完成 `Platform Variant Generation Planner` L3-derived：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-generation-plan-20260805-190052.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r30-platform-variant-generation-plan-presentation-pack-20260805-190107.json
```

R30 结果：`run_generation_plan.py` 读取 R29 Unreal runtime drift 和 R28 variant plan，把 generic warning 转成可审核的 dry-run operation contract。操作覆盖 missing LOD、Nanite policy、material merge、texture downscale、collision simplification、source import 和 target variant creation。结果为 11 operations，1 Ready，3 Review，2 Blocked，5 Satisfied，owner approval required 6。`Blocked` 来自 synthetic vehicle 缺源资产/目标资产；HeroPanel 的 LOD/texture bake 保持 Review，因为当前 public fixture 的几何/贴图 runtime facts 不足以执行 destructive bake。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r30 / dcc-first-package@1.27.0
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier platform-variant-generation
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Platform Variant Texture Runtime Collector / Controlled Executor`：

```text
generation plan artifact -> texture/material runtime fact collector or public-scope executor -> re-check gate -> Presenter Pack row -> docs
```

## R31 循环开发断点：Platform Variant Texture Runtime Collector

R31 已完成 `Platform Variant Texture Runtime Collector` L3：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-runtime-20260805-191529.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r31-platform-variant-texture-runtime-presentation-pack-20260805-191803.json
```

R31 结果：`run_texture_runtime_probe.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public test project，读取 R28 variant plan 和 R29 runtime artifact 后用 Unreal Python 采集 StaticMesh material slots、material dependency query、material expression texture references、Texture2D size / estimated memory / compression / sRGB / readability。结果为 3 variants，1 Ready，1 Review，1 intentionally Blocked，19 pass / 1 warning / 1 error。`Review` 来自 Mobile HeroPanel 的 synthetic material 没有真实 Texture2D payload；这已经不再是 collector 缺失，而是下一轮需要构造 public Texture2D payload fixture 或进入受控 executor 的明确输入。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r31 / dcc-first-package@1.28.0
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier platform-variant-texture
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Platform Variant Public Texture2D Payload Fixture / Controlled Executor`：

```text
texture runtime artifact -> public Texture2D payload fixture or controlled Unreal operation executor -> runtime re-check -> Presenter Pack row -> docs
```

## R32 循环开发断点：Platform Variant Public Texture2D Payload Fixture

R32 已完成 `Platform Variant Public Texture2D Payload Fixture` L3：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-payload-runtime-20260805-193515.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r32-platform-variant-texture-payload-presentation-pack-20260805-194432.json
```

R32 结果：`run_texture_payload_probe.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public test project，运行时生成 2048 public PNG，导入为 `/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor`，挂到 `M_HeroPanel`，然后重新采集 StaticMesh -> material -> Texture2D facts。结果为 3 variants，2 Ready，0 Review，1 intentionally Blocked，20 pass / 0 warning / 1 error。HeroPanel Mobile 已经从“缺真实贴图 payload 的 Review”进入 Ready；剩余 Blocked 只来自 synthetic vehicle 缺源资产/目标资产。最终提交的幂等 rerun 为 assetWrites=0，写入范围只限 `/Game/AI_Tool_TA` public fixture；Texture2D 为 2048 max dimension、约 16 MB、sRGB true。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r32 / dcc-first-package@1.29.0
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier platform-variant-texture-payload
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Platform Variant Controlled Executor`：

```text
generation plan + texture payload artifact -> select safe public fixture operation -> preflight fingerprint -> execute in /Game/AI_Tool_TA public scope -> post-check -> rollback artifact -> Presenter Pack row -> docs
```

## R33 循环开发断点：Platform Variant Controlled Executor

R33 已完成 `Platform Variant Controlled Executor` L3：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-controlled-executor-20260805-200810.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r33-platform-variant-controlled-executor-presentation-pack-20260805-200857.json
```

R33 结果：`run_controlled_executor.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public test project，读取 R30 generation plan 和 R32 texture payload artifact，选择 HeroPanel Mobile texture downscale 的 public-safe max texture size clamp。执行器先记录 `/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor` preflight fingerprint `2502b08c541495a4` 和 maxTextureSize=0，再执行 maxTextureSize=2048 并保存，post-check fingerprint 变为 `4374814fafe3a008`，最后 rollback 到 maxTextureSize=0 并确认 fingerprint 回到 `2502b08c541495a4`。报告为 L3 / `Ready` / `unreal_texture_budget_executor_rolled_back`，7 pass / 0 warning / 0 error，1 executed operation，1 post-check pass，1 rollback pass，assetWrites=2，persistentMutation=false。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r33 / dcc-first-package@1.30.0
Presenter Pack evidence: 30 / 30 present, 0 missing, 22 route steps
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier platform-variant-executor
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Platform Variant Executor Expansion`：

```text
controlled executor artifact -> add LOD / Nanite / collision candidate receipts -> approval and rollback boundaries -> public-safe non-production proof -> Presenter Pack row -> docs
```

## R34 循环开发断点：Platform Variant Executor Expansion Receipts

R34 已完成 `Platform Variant Executor Expansion Receipts`：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-executor-expansion-20260805-201222.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r34-platform-variant-executor-expansion-presentation-pack-20260805-201419.json
```

R34 结果：`run_executor_expansion.py` 读取 R30 generation plan 和 R33 controlled executor artifact，把 LOD / Nanite / collision 三类后续高风险操作转成 approval / rollback receipts。结果为 L3-derived / `Review` / `executor_receipts_linked_to_rolled_back_unreal_write`，5 receipts，2 no-op verified，1 approval-ready，2 readiness-only，0 blocked，3 owner approvals required，3 rollback receipts，productionWrites=0。Review 的原因是 LOD 几何事实可读性和 owner approval，不是 runtime 缺失。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r34 / dcc-first-package@1.31.0
Presenter Pack evidence: 31 / 31 present, 0 missing, 23 route steps
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier platform-variant-executor-expansion
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Character / Spatial Maya UI Drilldown`：

```text
existing Maya L3 artifact -> select one character calibration or spatial authoring business row -> build AuroraView drilldown data/API -> export artifact -> Presenter Pack row -> docs
```

## R35 循环开发断点：Character Calibration Drilldown

R35 已完成 `Character Calibration Drilldown`：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-drilldown-20260805-202259.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r35-character-calibration-drilldown-presentation-pack-20260805-202448.json
```

R35 结果：`run_drilldown.py` 读取 `character-calibration-maya-l3-20260805-175057.json`，把 Character Calibration Maya L3 的 flat validation rows 转成 AuroraView / Maya 面板可直接消费的 topology、skeleton、skin、calibration、face、Control Rig 和 mirror drilldown panels。结果为 L3-derived / `Blocked` / `maya_character_calibration_rows_to_drilldown`，2 character drilldowns，14 panels，1 Ready，1 intentionally Blocked，8 issue rows，8 owner actions，6 owner-required，2 manual-review，productionWrites=0。这个 gate 继承自 synthetic temp sculpt 的业务阻断，不是 runtime 缺失。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r35 / dcc-first-package@1.32.0
Presenter Pack evidence: 32 / 32 present, 0 missing, 24 route steps
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier character-drilldown
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Spatial Authoring Drilldown`：

```text
spatial-authoring-maya-l3 artifact -> socket / hotspot / pose transfer panels -> owner actions / fix previews -> Presenter Pack row -> docs
```

## R36 循环开发断点：Spatial Authoring Drilldown

R36 已完成 `Spatial Authoring Drilldown`：

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-drilldown-20260805-203713.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r36-spatial-authoring-drilldown-presentation-pack-20260805-204017.json
```

R36 结果：`run_drilldown.py` 读取 `spatial-authoring-maya-l3-20260805-181524.json`，把 Spatial Authoring Maya L3 的 flat validation rows 转成 AuroraView / Maya 面板可直接消费的 protocol carrier、parent joint、socket、mirror pair、hotspot、pose frame、transform、preview locator 和 pose transfer drilldown panels。结果为 L3-derived / `Blocked` / `maya_spatial_authoring_rows_to_drilldown`，2 spatial drilldowns，18 panels，1 Ready，1 intentionally Blocked，9 issue rows，9 owner actions，7 owner-required，2 manual-review，productionWrites=0。这个 gate 继承自 synthetic temp backpack 的业务阻断，不是 runtime 缺失。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r36 / dcc-first-package@1.33.0
Presenter Pack evidence: 33 / 33 present, 0 missing, 25 route steps
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier spatial-drilldown
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Unreal Control Rig Bridge` 或 `Unreal Socket Import Checker`：

```text
character/spatial drilldown artifact -> public Unreal runtime fixture -> Control Rig or socket facts comparison -> owner actions / rollback boundary -> Presenter Pack row -> docs
```

## R37 循环开发断点：Unreal Control Rig Bridge

R37 已完成 `Unreal Control Rig Bridge` L3：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-205656.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r37-unreal-control-rig-bridge-presentation-pack-20260805-205922.json
```

R37 结果：`run_l3_smoke.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public `AI_Tool_TA_Unreal_L3.uproject`，读取 R35 Character Calibration Drilldown artifact，采集 Control Rig / RigVM API、SkeletalMesh / Skeleton binding 和 expected Control Rig asset path facts。结果为 L3 / `Blocked` / `unreal_control_rig_bridge_facts_collected`，2 character rows，0 Ready，0 Review，2 Blocked，8 pass，1 warning，7 error，1 个 approved SkeletalMesh/Skeleton binding，0 个 expected Control Rig asset，assetWrites=0，productionWrites=0。Blocked 是业务门禁：approved 行缺 `CR_HeroFace`，TMP 行同时被 Maya 源头缺陷和 Unreal 目标缺失阻断。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r37 / dcc-first-package@1.34.0
Presenter Pack evidence: 34 / 34 present, 0 missing, 26 route steps
```

验证命令：

```powershell
.\scripts\validate_loop.ps1 -Tier unreal-control-rig
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Unreal Socket Import Checker`：

```text
spatial-authoring-drilldown artifact -> public Unreal Skeleton / socket facts -> socket / hotspot / pose transfer comparison -> owner actions / rollback boundary -> Presenter Pack row -> docs
```


## R38 循环开发断点：Unreal Socket Import Checker

R38 已完成 `Unreal Socket Import Checker` L3：

```text
<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-import-checker-l3-20260805-212131.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r38-unreal-socket-import-checker-presentation-pack-20260805-213500.json
```

R38 结果：`run_l3_smoke.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public `AI_Tool_TA_Unreal_L3.uproject`，读取 R36 Spatial Authoring Drilldown artifact，采集 SkeletalMesh / Skeleton / SkeletalMeshSocket API、目标资产存在性和 expected socket coverage。结果为 L3 / `Blocked` / `unreal_socket_facts_collected`，2 spatial rows，0 Ready，0 Review，2 Blocked，9 pass，2 warning，9 error，socket API ready，4 expected sockets，0 runtime sockets，assetWrites=0，productionWrites=0。Blocked 是业务门禁：approved rifle 行缺 `SK_Hand_L` / `SK_Hand_R`，TMP backpack 行同时被 Maya 源头缺陷和 Unreal 目标缺失阻断。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r38 / dcc-first-package@1.35.0
Presenter Pack evidence: 35 / 35 present, 0 missing, 27 route steps
```

验证命令：

```powershell
python -m py_compile dcc-hosts/unreal-socket-import-checker/unreal_socket_import_checker/contract.py dcc-hosts/unreal-socket-import-checker/scripts/run_smoke.py dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py dcc-hosts/unreal-socket-import-checker/scripts/unreal_python/probe_socket_import_checker.py
python dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

默认下一轮开发 `Control Rig / Socket Authoring Controlled Executor` 或 `Unreal AnimSequence Fact Deepening`：

```text
R37/R38/R34 artifacts -> public Unreal runtime facts -> controlled write or post-check contract -> rollback / owner receipt -> Presenter Pack row -> docs
```

## R39 循环开发断点：Platform Variant StaticMesh Post-check

R39 已完成 `Platform Variant StaticMesh Post-check` L3：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-staticmesh-postcheck-20260805-215500.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r39-platform-variant-staticmesh-postcheck-presentation-pack-20260805-215900.json
```

R39 结果：UnrealEditor-Cmd 5.3 进入 public `AI_Tool_TA_Unreal_L3.uproject`，只读采集 2 个目标 StaticMesh 的 LOD / Nanite / collision facts，并验证 R34 的 5 条 LOD / Nanite / collision receipts。结果为 L3 / `Review` / `unreal_staticmesh_postcheck_collected`，2 target assets present，2 / 2 no-op receipts matched，1 approval-ready Nanite receipt，2 readiness-only LOD receipts，3 owner-held rows，32 pass，3 warning，0 error，assetWrites=0，productionWrites=0。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r39 / dcc-first-package@1.36.0
Presenter Pack evidence: 36 / 36 present, 0 missing, 28 route steps
```

## R40 循环开发断点：Unreal Socket Authoring Executor

R40 已完成 `Unreal Socket Authoring Executor` L3 readiness：

```text
<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-authoring-executor-20260805-222014.json
<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-api-docs-20260805-222200.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r40-unreal-socket-authoring-executor-presentation-pack-20260805-222519.json
```

R40 结果：读取 R38 socket readiness artifact，只选择 approved rifle 行进入受控 Unreal executor，TMP backpack 行保持 held / no-write。Unreal 5.3 Python 暴露 `SkeletalMesh.add_socket(socket, add_to_skeleton=False)`，但 commandlet-created `SkeletalMeshSocket.socket_name` 和 `bone_name` 不可写；构造参数和 `rename()` 只改 UObject name，不改 socket identity。结果为 L3 / `Blocked` / `unreal_socket_authoring_executor_api_limited`，selected/held 1 / 1，expected/created sockets 2 / 0，9 pass / 0 warning / 2 error，assetWrites=0，productionWrites=0。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r40 / dcc-first-package@1.37.0
Presenter Pack evidence: 38 / 38 present, 0 missing, 29 route steps
```

下一轮入口：

```text
Unreal AnimSequence Fact Deepening 或 public Control Rig asset fixture / runtime hierarchy -> runtime facts -> owner/readiness receipt -> Presenter Pack row -> docs -> targeted validation
```

## R41 循环开发断点：Unreal AnimSequence Deep Facts

R41 已完成 `Unreal AnimSequence Deep Facts` L3：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-deep-facts-20260805-224206.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r41-unreal-animation-deep-facts-presentation-pack-20260805-224616.json
```

R41 结果：`run_deep_facts.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public `AI_Tool_TA_Unreal_L3.uproject`，只读读取 R25 已导入的两个 AnimSequence。采集 play length、derived frame span、direct frame-rate、curve metadata API、root motion setting、compression setting 和 write boundary。结果为 L3 / `Blocked` / `unreal_animsequence_deep_facts_collected`，2 runtime rows，2 / 2 duration frame spans matched，0 Ready，1 Review，1 Blocked，15 pass，2 warning，1 error，assetWrites=0，productionWrites=0。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r41 / dcc-first-package@1.38.0
Presenter Pack evidence: 39 / 39 present, 0 missing, 30 route steps
```

下一轮入口：

```text
public Control Rig asset fixture / runtime hierarchy -> Unreal runtime facts -> owner/readiness receipt -> Presenter Pack row -> docs -> targeted validation
```

## R42 循环开发断点：Unreal Control Rig Fixture Authoring

R42 已完成 `Unreal Control Rig Fixture Authoring` 和 post-authoring `Unreal Control Rig Bridge` 复验：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-fixture-authoring-20260805-230323.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-230343.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r42-unreal-control-rig-fixture-authoring-presentation-pack-20260805-230853.json
```

R42 结果：`run_fixture_authoring.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public `AI_Tool_TA_Unreal_L3.uproject`，只选择 R37 approved 角色行，使用 `ControlRigBlueprintFactory` / `AssetTools` 创建 `/Game/AI_Tool_TA/Characters/CR_HeroFace`，用 `RigHierarchyController.add_control` 写入 `CTRL_brow_L`、`CTRL_brow_R`、`CTRL_eye_L`、`CTRL_eye_R`、`CTRL_jaw`，保存 1 个 public fixture asset，productionWrites=0。fixture authoring 为 L3 / `Ready` / `unreal_control_rig_fixture_authoring_collected`，operations/held 1 / 1，required/runtime/missing controls 5 / 5 / 0。复跑 bridge 后 approved 行 Ready，TMP 行 Blocked，整体 L3 / `Blocked`，10 pass / 1 warning / 5 error，assetWrites=0。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r42 / dcc-first-package@1.39.0
Presenter Pack evidence: 40 / 40 present, 0 missing, 31 route steps
```

下一轮入口：

```text
Control Rig deformation target link / compile status 或 gameplay attach fixture -> runtime facts -> owner/readiness receipt -> Presenter Pack row -> docs -> targeted validation
```

## R43 循环开发断点：Unreal Control Rig Deformation Link

R43 已完成 `Unreal Control Rig Deformation Link` L3：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-232729.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r43-unreal-control-rig-deformation-link-presentation-pack-20260805-233308.json
```

R43 结果：`run_deformation_link.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public `AI_Tool_TA_Unreal_L3.uproject`，只读 `CR_HeroFace`、`SK_Hero_Skeleton` 和 Maya `controlRigMappings`。它把 control presence 推进到 control -> deformation target -> Skeleton target match、hierarchy shape / offset 可读性和 compile API visibility。结果为 L3 / `Blocked` / `unreal_control_rig_deformation_link_collected`，2 character rows，10 control links，5 runtime controls，5 shape/offset-readable controls，2 Skeleton target matches，0 direct compile-status rows，12 pass / 2 warning / 6 error，assetWrites=0，productionWrites=0。关键业务结论：控件存在不等于绑定可交付，approved 行还缺 `Eye_L`、`Eye_R`、`Jaw` Skeleton target matches。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r43 / dcc-first-package@1.40.0
Presenter Pack evidence: 41 / 41 present, 0 missing, 32 route steps
```

下一轮入口：

```text
Control Rig direct compile status bridge / public face skeleton fixture 或 gameplay attach fixture -> runtime facts -> owner/readiness receipt -> Presenter Pack row -> docs -> targeted validation
```

## R44 循环开发断点：Unreal Control Rig Face Skeleton Fixture

R44 已完成 `Unreal Control Rig Face Skeleton Fixture` L3，并复跑 post-face bridge / deformation-link：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-face-skeleton-fixture-20260805-235115.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-235140.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-235154.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r44-unreal-control-rig-face-skeleton-fixture-presentation-pack-20260805-235700.json
```

R44 结果：`run_face_skeleton_fixture.py` 先用 Maya 2026 `mayapy` 生成 public face Skeleton FBX，再由 Unreal 5.3.2 导入 `/Game/AI_Tool_TA/Characters/SK_HeroFace` 和 `SK_HeroFace_Skeleton`。artifact 为 L3 / `Review`，required target matches 4 / 4，previous R43 missing targets resolved 3 / 3，assetWrites=2，productionWrites=0。复跑 `run_l3_smoke.py` 后 approved 行 Ready；复跑 `run_deformation_link.py` 后 approved 行从 Blocked 推进到 Review，runtime controls 5，Skeleton target matches 5，shape/offset-readable controls 5，0 direct compile-status rows，13 pass / 2 warning / 5 error，assetWrites=0。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r44 / dcc-first-package@1.41.0
Presenter Pack evidence: 42 / 42 present, 0 missing, 33 route steps
```

下一轮入口：

```text
Control Rig direct compile status bridge 或 gameplay attach fixture / Groom Export Inspector -> runtime facts -> owner/readiness receipt -> Presenter Pack row -> docs -> targeted validation
```

## R45 循环开发断点：Unreal Control Rig Compile Status Bridge

R45 已完成 `Unreal Control Rig Compile Status Bridge` L3：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-compile-status-20260806-001504.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r45-unreal-control-rig-compile-status-presentation-pack-20260806-001919.json
```

R45 结果：`run_compile_status.py` 调用本机 UnrealEditor-Cmd 5.3，打开 public `AI_Tool_TA_Unreal_L3.uproject`，读取 R44 post-face deformation-link artifact，加载 public `CR_HeroFace`，调用可见的 `ControlRigBlueprint` compile 方法，并记录 direct status / diagnostics / compile settings、package dirty-state 和 no-save boundary。结果为 L3 / `Blocked` / `unreal_control_rig_compile_status_collected`，2 character rows，approved 行 Review，TMP 行 Blocked，compile candidate / method visible / invoked / succeeded = 1 / 1 / 1 / 1，direct status / diagnostics / settings = 0 / 0 / 1，dirtyAfter=0，10 pass / 2 warning / 4 error，assetWrites=0，productionWrites=0。

当前 public package：

```text
ai-tool-ta-dcc-first-showcase-r45 / dcc-first-package@1.42.0
Presenter Pack evidence: 43 / 43 present, 0 missing, 34 route steps
```

下一轮入口：

```text
Control Rig Editor Utility / C++ diagnostic bridge，或 gameplay attach fixture / Groom Export Inspector -> runtime facts -> owner/readiness receipt -> Presenter Pack row -> docs -> targeted validation
```

## R46 循环开发断点：Groom Export Inspector

R46 已完成 `Groom Export Inspector` Maya L3：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-export-inspector-maya-l3-20260806-003711.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r46-groom-export-inspector-presentation-pack-20260806-004101.json
```

R46 结果：`run_l3_smoke.py` 调用 Maya 2026 `mayapy`，创建 public synthetic scalp planes 和 curve strands，从 Maya 场景回读 root UV、strand ID、guide flag、Alembic payload 和 Unreal Groom / Binding intent。结果为 L3 / `Blocked` / `maya_groom_export_facts_collected`，2 groom rows，1 Ready，1 Blocked，11 strands，2 guides，root UV missing / duplicate strand IDs = 1 / 1，11 pass / 2 warning / 7 error，9 owner actions，assetWrites=0，productionWrites=0。

Public package:

```text
ai-tool-ta-dcc-first-showcase-r46 / dcc-first-package@1.43.0
Presenter Pack evidence: 44 / 44 present, 0 missing, 35 route steps
public-case-package r8-70 / public-case-package@3.40.0
```

下一轮入口：

```text
Groom Unreal import readiness 或 gameplay attach fixture -> runtime facts -> owner/readiness receipt -> Presenter Pack row -> docs -> targeted validation
```

## R47 循环开发断点：Groom Unreal Import Readiness

R47 已完成 `Groom Unreal Import Readiness` Unreal L3：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-unreal-readiness-20260806-010008.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r47-groom-unreal-readiness-presentation-pack-20260806-010323.json
```

R47 结果：`run_unreal_readiness.py` 调用 UnrealEditor-Cmd 5.3，打开 public `AI_Tool_TA_Unreal_L3.uproject`，读取 R46 Groom Export Inspector Maya L3 artifact，只读采集 Groom/Alembic API visibility、target SkeletalMesh presence、expected Groom / Binding assets 和 zero-write boundary。结果为 L3 / `Blocked` / `unreal_groom_import_readiness_collected`，2 groom rows，source Ready / Blocked = 1 / 1，AssetImportTask visible rows = 2，AlembicImportFactory visible rows = 2，target SkeletalMesh present rows = 1，GroomAsset / GroomBindingAsset API visible rows = 0 / 0，expected Groom / Binding assets present = 0 / 0，12 pass / 4 warning / 6 error，10 owner actions，assetWrites=0，productionWrites=0。

Public package:

```text
ai-tool-ta-dcc-first-showcase-r47 / dcc-first-package@1.44.0
Presenter Pack evidence: 45 / 45 present, 0 missing, 36 route steps
public-case-package r8-71 / public-case-package@3.41.0
```

下一轮入口：

```text
Groom Alembic executor 或 gameplay attach fixture -> runtime facts -> owner/readiness receipt -> Presenter Pack row -> docs -> targeted validation
```
