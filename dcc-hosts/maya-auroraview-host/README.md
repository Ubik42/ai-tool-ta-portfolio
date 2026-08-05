# Maya AuroraView Host

这个目录是 AI Tool TA 作品集的 Maya 宿主层。

目标：

- 在 Maya 内打开 AuroraView 面板。
- 加载 `showcases/portfolio-site/dist/index.html`。
- 通过 Python API bridge 暴露 Maya 场景能力。
- 逐步把 Web 工具台迁移成 DCC-first 工具展示。

## 环境

安装 Maya 侧依赖：

```powershell
.\scripts\install_maya_auroraview.ps1 -MayaVersion 2024
```

构建前端：

```powershell
.\scripts\build_frontend_for_maya.ps1
```

## Maya 启动

在 Maya Script Editor 里执行：

```python
import sys
host = r"<repo>\dcc-hosts\maya-auroraview-host"
if host not in sys.path:
    sys.path.insert(0, host)

from ai_tool_ta_maya_host import show_portfolio
show_portfolio()
```

也可以执行：

```python
exec(open(r"<repo>\dcc-hosts\maya-auroraview-host\shelf\install_shelf_button.py", "r").read())
```

然后从 shelf 按钮打开。

## Maya 外部控制

Maya GUI 需要一个已打开的 Maya 进程承载窗口；启动后可以用本地 command bridge 从外部发命令。先在 Maya 里执行一次：

```python
exec(open(r"<repo>\dcc-hosts\maya-auroraview-host\scripts\start_maya_command_bridge.py", "r").read())
```

或点击 shelf 里的 `TA Bridge`。之后外部 shell 可以控制已打开的 Maya：

```powershell
python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --show-portfolio
python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --export-presenter-pack r22-blender-max-l3-presentation-pack
```

这个 bridge 按 Maya 会话存在；重开 Maya 后需要再次启动，后续可接入 `userSetup.py` 做自动启动。

## 当前 API

Python 侧已预留基础 API：

- `environment_status`
- `scene_get_selection`
- `scene_create_protocol_fixture`
- `asset_apply_protocol_payload`
- `asset_inspect_protocol`
- `rule_matrix_collect_scene`
- `rule_matrix_validate_scene`
- `rule_matrix_preview_fixes`
- `rule_matrix_export_report`
- `visual_review_create_camera_rig`
- `visual_review_build_pass_manifest`
- `visual_review_preview_capture`
- `visual_review_export_report`
- `texture_delivery_create_fixture`
- `texture_delivery_inspect_scene`
- `texture_delivery_validate_scene`
- `texture_delivery_export_manifest`
- `task_orchestrator_create_fixture`
- `task_orchestrator_discover_scene`
- `task_orchestrator_build_queue`
- `task_orchestrator_run_dry_run`
- `task_orchestrator_export_report`
- `asset_handoff_create_fixture`
- `asset_handoff_collect`
- `asset_handoff_evaluate_gate`
- `asset_handoff_preview_actions`
- `asset_handoff_export_packet`
- `asset_handoff_build_decision_packet`
- `asset_handoff_export_decision_packet`
- `showcase_runbook_build_plan`
- `showcase_runbook_run_smoke`
- `showcase_runbook_export_package`
- `showcase_runbook_export_gui_evidence_manifest`
- `showcase_runbook_audit_gui_media`
- `showcase_runbook_export_gui_media_audit`
- `showcase_runbook_export_case_page`
- `dcc_presentation_build_pack`
- `dcc_presentation_export_pack`
- `report_export_json`

React 前端右侧已接入 `Maya Bridge` 面板，对应按钮：

- `Status`：读取 Maya / AuroraView 环境状态。
- `Selection`：读取当前 Maya 选择。
- `Fixture`：创建 synthetic asset fixture，并自动选择生成节点。
- `Write Attr`：向当前选择写入 active workbench payload 的 `aiToolTaProtocol` JSON。
- `Inspect`：读取当前选择上的协议数据，并回填到 `Asset Protocol Workbench` 的 `DCC Scene Payload` 面板。
- `Export`：导出当前 bridge 结果 JSON。

`Cross-DCC Rule Matrix` 模块内已接入 `Maya Scene Rule Run`：

- `Collect Scene`：从 Maya selection 采集 transform、mesh、material、parent/root、协议字段。
- `Validate Scene`：执行 6 条 publish rule，并输出 gate / score / evidence。
- `Preview Fixes`：生成 `safe_auto` / `manual_only` 修复预览，不直接改场景。
- `Export DCC Report`：导出 `maya-rule-matrix-dcc-report@1.0.0` JSON artifact。

`Visual Review Studio` 模块内已接入 `Maya Capture Setup`：

- `Create Rig`：创建 basic/detail review camera rig。
- `Build Manifest`：从 scene meshes 和 cameras 生成 pass manifest。
- `Preview Capture`：规划 capture 输出路径，不直接强制 playblast。
- `Export DCC Review`：导出 `maya-visual-review-dcc-report@1.0.0` JSON artifact。

`Texture Delivery Console` 模块内已接入 `Maya Texture Inspection`：

- `Create Fixture`：创建 synthetic mesh、material、shadingEngine 和 BaseColor / Normal / ORM file nodes。
- `Inspect Textures`：扫描 scene meshes、materials、file texture nodes、路径、role、resolution、colorSpace。
- `Validate Scene`：执行材质绑定、贴图路径、role 命名、色彩空间、平台预算验证。
- `Export Manifest`：导出 `maya-texture-delivery-dcc-report@1.0.0` JSON artifact。

`Task Orchestrator` 模块内已接入 `Maya Batch Queue`：

- `Create Fixture`：创建 ready/review 两个 synthetic batch assets。
- `Discover Scene`：扫描 mesh、protocol、material、texture node、triangle budget、visible state、review/blocker。
- `Build Queue`：为每个 asset 生成 Protocol / Material / Texture / Visual / Export 五类 dry-run tasks。
- `Dry Run`：执行不改场景的 task event 模拟，并生成 per-asset receipts。
- `Export Report`：导出 `maya-task-orchestrator-dcc-report@1.0.0` JSON artifact。

右侧全局 `DCC Showcase Runbook` 已接入：

- `Build Plan`：输出 5 个 DCC 模块的演示路径、主 API 和证明点。
- `Run Smoke`：创建 synthetic demo scene fixtures，并执行 5 个 DCC 模块的 smoke。
- `Export Package`：导出 `maya-dcc-showcase-runbook-package@1.4.0` 统一演示证据包，包含 7 段业务主线、live demo script、GUI click checklist、reviewer claims、handoff artifact、decision artifact 和 public case package 指针。
- `Evidence Shotlist`：导出 `maya-dcc-gui-evidence-manifest@1.2.0` GUI 媒体采集清单，包含 9 张截图、1 段录屏和验收标准。

`Task Orchestrator` 证据视图的 `R10.7 DCC-first Case Page` 已接入：

- `Export Case Page`：调用 `showcase_runbook_export_case_page`，导出 `maya-dcc-portfolio-case-page@1.1.0`，把 Maya entry、7 段 business route、runbook artifact、Asset Handoff Gate artifact、Decision Packet、GUI evidence manifest 和 public package 指针合成可投递 case page。
- `Audit Media`：调用 `showcase_runbook_export_gui_media_audit`，扫描 `assets/dcc-first/r10-7-gui-evidence`，导出 `maya-dcc-gui-media-audit@0.2.0`，逐项报告 9 张截图和 1 段录屏的 Missing / Review / Present 状态。
- `Presenter Pack`：调用 `dcc_presentation_export_pack`，导出 `maya-dcc-presentation-pack@0.1.0`，把当前 public package、case page、GUI media audit、handoff decision、engine preflight、preset comparison、Animation Continuity、Unreal Animation Bridge、Character Calibration、Spatial Authoring、Platform Variant Forge / runtime / generation / texture / payload / controlled executor evidence、Blender/3ds Max adapter evidence、Unreal Python L3++ engine facts、Unreal preset fact / waiver comparison、preset fact review artifact 和 Scene Transaction Guard 收束成 Maya 内 R33 Cross-DCC / Engine 展示包。
- `Preset Facts`：调用 `unreal_preset_fact_review_export`，导出 `maya-unreal-preset-fact-review@0.1.0`，把 PC / Mobile preset fact rows 投影成 Maya 内 reviewer queue，显示 blocked、drift、waived 和 matched 行及 owner action。
- `Txn Guard`：调用 `scene_transaction_export_receipt`，导出 `maya-scene-transaction-guard@0.1.0`，显示工具执行前后的 fingerprint、created/deleted/modified rows、selection/time 上下文变化、risk rows 和 rollback preview。

右侧全局 `Asset Handoff Gate` 已接入：

- `Fixture`：创建 2 个 synthetic handoff assets，一个 Ready，一个 Review。
- `Collect`：采集协议、规则、贴图、视觉和任务队列证据。
- `Evaluate Gate`：输出 per-asset gate、blocker/review list 和 evidence summary。
- `Preview Actions`：输出 safe_auto / manual_only handoff actions。
- `Export Packet`：导出 `maya-asset-handoff-gate@0.1.0` JSON artifact。
- `Decision Packet`：导出 `maya-asset-handoff-decision-packet@0.1.0`，在 gate 后补 repair preview、owner disposition 和 engine handoff mock。
- `Engine Preflight`：导出 `maya-engine-handoff-preflight@0.1.0`，按 PC Unreal preset 校验 engine import intent，输出 dry-run sidecar 和 held rows。
- `Preset Compare`：导出 `maya-engine-handoff-preset-comparison@0.1.0`，对比 PC / Mobile preset 下同一批 engine intents 的平台差异。

当前 active payload 来源：

- 默认：fallback asset protocol payload。
- 打开 `Asset Protocol Workbench` 后：当前 fixture / editor state / encoded payload / readiness / diff / report。

## 已验证

- Maya 2024 `mayapy` 已安装 `auroraview 0.5.10` 和 `qtpy`。
- `QtWebView` 可导入。
- 前端 `dist/index.html` 已生成相对资源路径。
- headless smoke 已能创建 synthetic fixture、写入 `aiToolTaProtocol`、inspect 并导出 JSON。
- Maya GUI 已能通过 `show_portfolio()` 正确弹出界面。
- 前端 `Maya Bridge` 面板构建通过，最新 smoke report：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-bridge-panel-smoke-20260803-152358.json
```
- R9.2 active payload 写入 smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-2-active-payload-smoke-20260803-152936.json
```
- R9.2 inspect feedback smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-2-inspect-feedback-smoke-20260803-154209.json
```
- R9.2 DCC evidence report smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-2-dcc-evidence-report-smoke-20260803-154521.json
```
- R9.3 Rule Matrix DCC smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-3-rule-matrix-smoke-20260803-155309.json
```
- R9.4 Visual Review DCC smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-4-visual-review-smoke-20260803-155811.json
```
- R9.5 Texture Delivery DCC smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-5-texture-delivery-smoke-20260803-160419.json
```
- R9.6 Task Orchestrator DCC smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-6-task-orchestrator-smoke-20260803-161017.json
```
- R9.7 DCC Showcase Runbook package smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-7-dcc-showcase-runbook-package-20260803-161632.json
```
- R10.3.4 DCC-first runbook handoff package smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-runbook-handoff-package-20260803-164209.json
```
- R10.3.4 GUI evidence manifest smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-gui-evidence-manifest-20260803-164209.json
```
- R10.3.4 Asset Handoff Gate package smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-3-4-runbook-handoff-package-asset-handoff-20260803-164209.json
```
- R10.7 DCC-first case page smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
```
- R10.7 runbook / handoff / decision / GUI supporting artifacts：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
```
- R10.7 GUI media audit smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```
- R10.8 Engine Handoff Preflight smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-8-engine-handoff-preflight-fixture-20260803-172302.json
```
- R10.9 Engine Preset Comparison smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-9-engine-preset-comparison-20260803-172927.json
```
- R11 DCC Presenter Pack smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r11-dcc-presentation-pack-20260803-174307.json
```

  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r11` / `dcc-first-package@1.8.0`
  - gate：`CapturePending`
  - evidence files present/missing：11 / 0
  - GUI media present/review/missing：0 / 0 / 10

- R12 Cross-DCC Presenter Pack smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r12-cross-dcc-presentation-pack-20260803-180759.json
```

  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r12` / `dcc-first-package@1.9.0`
  - gate：`CapturePending`
  - evidence files present/missing：12 / 0
  - Blender adapter：L2 / `Blocked`
  - GUI media present/review/missing：0 / 0 / 10

- R13 Cross-DCC / Engine Presenter Pack smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r13-engine-presentation-pack-20260803-181814.json
```

  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r13` / `dcc-first-package@1.10.0`
  - gate：`CapturePending`
  - evidence files present/missing：13 / 0
  - Unreal inspector：L2 / `Blocked`
  - Blender adapter：L2 / `Blocked`
  - GUI media present/review/missing：0 / 0 / 10

- R16 Cross-DCC / Engine Presenter Pack smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r16-unreal-engine-facts-presentation-pack-20260803-184326.json
```

  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r16` / `dcc-first-package@1.13.0`
  - gate：`CapturePending`
  - evidence files present/missing：13 / 0
  - Unreal inspector：L3++ / `unreal_engine_facts_matched`
  - Unreal engine facts：4 / 4 matched
  - Blender adapter：L2 / `Blocked`
  - GUI media present/review/missing：0 / 0 / 10

- R17 Cross-DCC / Engine Presenter Pack smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r17-unreal-preset-facts-presentation-pack-20260803-185425.json
```

  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r17` / `dcc-first-package@1.14.0`
  - gate：`CapturePending`
  - evidence files present/missing：14 / 0
  - Unreal preset facts matched/drift/waived/blocked：7 / 1 / 1 / 1
  - Unreal preset fact platform split / approved waivers：1 / 1
  - Unreal inspector：L3++ / `unreal_engine_facts_matched`
  - Blender adapter：L2 / `Blocked`
  - GUI media present/review/missing：0 / 0 / 10

- R18 Unreal Preset Fact Review smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json
```

  - report version：`maya-unreal-preset-fact-review@0.1.0`
  - gate：`Blocked`
  - fact rows / review queue：10 / 3
  - matched / drift / waived / blocked：7 / 1 / 1 / 1
  - source evidence：L3++ / `unreal_engine_facts_matched`

- R18 Cross-DCC / Engine Reviewer Pack smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-presentation-pack-20260803-190613.json
```

  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r18` / `dcc-first-package@1.15.0`
  - gate：`CapturePending`
  - evidence files present/missing：15 / 0
  - demo route steps：9
  - Unreal preset review rows / queue / blocked / waivers：10 / 3 / 1 / 1
  - GUI media present/review/missing：0 / 0 / 10

- R19 Scene Transaction Guard smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-20260804-195730.json
```

  - report version：`maya-scene-transaction-guard@0.1.0`
  - gate：`Review`
  - before/after fingerprint：`8d096c2e9a7dccca` / `e048ce005ffd65c3`
  - created/deleted/modified：2 / 2 / 2
  - rollback actions / risk rows：9 / 4

- R19 Cross-DCC / Engine Reviewer Pack smoke 通过：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-presentation-pack-20260804-195754.json
```

  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r19` / `dcc-first-package@1.16.0`
  - gate：`CapturePending`
  - evidence files present/missing：16 / 0
  - demo route steps：10
  - scene transaction gate / rollback / risk rows：Review / 9 / 4
  - GUI media present/review/missing：0 / 0 / 10

## 下一步

- 安装 Blender 后把 `blender-rule-adapter` 升级为 `blender --background --python` L3 smoke。
- 采集真实 Maya GUI 截图和录屏到 `assets/dcc-first/r10-7-gui-evidence`，让 media audit 从 `CapturePending` 进入可审核状态。
