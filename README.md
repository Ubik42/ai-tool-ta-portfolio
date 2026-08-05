# AI Tool TA Portfolio

这个目录是 AI 工具 TA 作品集总入口，用来组织真正可展示、可解释、可复用的个人 AI 工具案例。

目标是把每个工具讲清楚：

- 它解决的真实问题是什么。
- 核心业务逻辑和工程设计是什么。
- AI 在流程里承担哪一段能力。
- 有什么可运行入口、截图、视频、数据流或测试证据。
- 作为工具管线 TA，可以从里面学到什么方法。

公开发布和 AI 接手入口：

- `PUBLIC_RELEASE.md`
- `docs/AI_HANDOFF.md`
- `public-case-package/DCC_FIRST_PACKAGE.md`

当前稳定展示包：

- `public-case-package/dcc-first-package-manifest.json`
- `dcc-hosts/maya-auroraview-host/artifacts/r63-unreal-socket-native-commandlet-presentation-pack-20260806-063805.json`

## 目录

```text
AIToolTA_Portfolio/
├── README.md
├── PRODUCT.md
├── DESIGN.md
├── docs/
│   ├── 260730_1704_开发计划.md
│   ├── 260730_Lightbox高价值线作品集开发计划.md
│   ├── 260730_Lightbox中高价值扩展线与复杂工具计划.md
│   ├── 260730_作品集拆分与长期开发框架.md
│   ├── lightbox-method-index.md
│   └── case-studies/
├── showcases/
│   └── portfolio-site/
├── dcc-hosts/
│   ├── maya-auroraview-host/
│   ├── blender-rule-adapter/
│   ├── 3dsmax-rule-adapter/
│   ├── unreal-handoff-inspector/
│   ├── animation-continuity-lab/
│   └── unreal-animation-bridge/
├── public-case-package/
└── assets/
```

## 选题池

当前选题分两层：Lightbox 高价值业务插件提供方法源，本仓库提供可公开展示的实现载体。

Lightbox 高价值线：

| 业务线 | 方法价值 |
| --- | --- |
| 资产语义编码 | 用 UV / vertex color / custom attr 这类下游稳定通道承载业务语义 |
| Socket / Pose 作者工具 | 把引擎 JSON 生产转成 DCC pose / template authoring |
| 动画确定性导出 | 强制求值、bake、清理 namespace/root，把 DCC 不确定状态压平成稳定数据 |
| 命名 / 材质 / 贴图同步 | 把命名规范变成配置、解析器、预览、Maya graph 和文件操作 |
| 资产协议检查 | 用 Collect / Validate / Fix / Extract 把项目规范变成门禁、修复和导出 |
| LOD / UV / 法线规则库 | 从命名、材质、目录、LOD 层级推导批量操作和 QC 修复 |

作品集工具模块：

| 工具 | 展示方向 |
| --- | --- |
| `Asset Protocol Workbench` | 资产协议、UV/vertex/custom attr 业务语义编码、LOD/平台预算底座 |
| `Cross-DCC Rule Matrix` | 统一规则 DSL、Maya/Blender/Max/Houdini adapter、Collect/Validate/Fix/Extract |
| `Visual Review Studio` | 固定相机、固定 pass、baseline/variant 差异、HTML report |
| `Texture Delivery Console` | 通道打包、DDS/SpriteSheet/UE import mock、长任务队列和风险解释 |
| `Task Orchestrator` | 工具发现、任务状态、资产包、QC/review/publish 状态流 |

可继续吸收的个人工具和展示实现池：

| 工具 | 展示方向 |
| --- | --- |
| `slidev_ppt_tool` / `beautiful_slidev` | AI 辅助演示文稿生成、Slidev/PPTX 转换、视觉质量控制 |
| `paper_analyser` | 论文解析、结构化阅读、研究案例沉淀 |
| `gdc` | 音视频归档、转录、摘要与资料索引 |
| `codex-RDD` | AI 辅助需求/设计/开发记录工作流 |
| `git_toolsets` | Git 数据查看、收藏/代码资产管理类工具 |

公司内部项目经验只抽象成方法论或匿名案例，不把内部代码、路径、资产和业务细节作为公开展示素材。

## 当前计划

基础计划见 `docs/260730_1704_开发计划.md`。

Lightbox 高价值线驱动的作品集开发计划见 `docs/260730_Lightbox高价值线作品集开发计划.md`。

放宽阈值后的扩展盘点与复杂工具计划见 `docs/260730_Lightbox中高价值扩展线与复杂工具计划.md`。

作品集拆分和长期循环开发框架见 `docs/260730_作品集拆分与长期开发框架.md`。

Public case package 入口见 `public-case-package/README.md`。

DCC-first 长期开发计划见 `docs/260803_DCC-first长期开发计划与环境.md`。

AuroraView 迁移可行性评估见 `docs/260803_1135_AuroraView_DCC迁移可行性评估.md`。

R10.3 Asset Handoff / Publish Gate 开发计划见 `docs/260803_R10_3_AssetHandoffPublishGate开发计划.md`。

当前 DCC-first 状态：Maya AuroraView 宿主已能打开作品集 UI；5 个 Maya 工具模块、Asset Handoff Gate、Owner/Engine Decision、Engine Preflight、PC/Mobile Preset Compare、Animation Continuity Maya L3、Unreal Animation Bridge import L3、Unreal AnimSequence Deep Facts、Character Calibration / Spatial Authoring、Unreal Control Rig / Socket / Gameplay Attach、Platform Variant、Blender `bpy` L3、Blender Controlled Repair、3ds Max `pymxs` L3、3ds Max Controlled Repair、3ds Max Material Texture Manifest Link、Houdini Rule Adapter、Unreal L3++ inspector、Scene Transaction Guard、Groom Export Inspector、Groom Unreal Import Readiness、Groom Alembic Payload Receipt、Groom Alembic Import/Post-check Readiness、Groom Plugin/API Fixture、Groom Controlled Executor、Groom Runtime Fact Collector、Groom Group / Root Projection Inspector 和 Unreal Socket Native Commandlet Probe 都已有可导出的证据。当前 `maya-dcc-presentation-pack@0.1.0` 探测 61 个关键证据文件、51 段展示路线和 GUI media gate；public package 为 `ai-tool-ta-dcc-first-showcase-r63` / `dcc-first-package@1.60.0`，总体 gate 仍为 `CapturePending`，因为 9 张 Maya 截图和 1 段录屏尚未补齐。最新 presenter pack artifact 为 `dcc-hosts/maya-auroraview-host/artifacts/r63-unreal-socket-native-commandlet-presentation-pack-20260806-063805.json`。R63 Unreal Socket Native Commandlet Probe artifact 为 `dcc-hosts/unreal-socket-import-checker/artifacts/unreal-socket-native-commandlet-probe-20260806-063543.json`，基于 R62 packaged plugin 在 `D:\cs\_test` 临时 Unreal project 内执行 `-run=AiToolTaSocketAuthoring`，returnCode=0，commandletLoaded=true，readinessInvocation=true，errorLines=0，assetWrites / engineWrites / productionWrites = 0 / 0 / 0。下一步才进入 JSON receipt parsing、socket write、post-check 和 rollback executor。R59 Groom Group / Root Projection、R58 Max Controlled Repair、R57 Blender Controlled Repair、R56 Houdini Rule Adapter、R55 Groom Runtime Facts、R54 Gameplay Attach、R53 Max Texture Manifest Link 和 R52 Groom Controlled Executor 继续作为受控修复、程序化资产、Groom、socket gameplay、材质贴图与引擎受控执行证据。

模块文档：

- `docs/modules/asset-protocol-workbench.md`
- `docs/modules/cross-dcc-rule-matrix.md`
- `docs/modules/visual-review-studio.md`
- `docs/modules/texture-delivery-console.md`
- `docs/modules/task-orchestrator.md`
- `docs/modules/dcc-showcase-runbook.md`
- `docs/modules/asset-handoff-gate.md`
- `docs/modules/dcc-first-case-page.md`
- `docs/modules/scene-transaction-guard.md`
- `docs/modules/animation-continuity-lab.md`
- `docs/modules/unreal-animation-bridge.md`
- `docs/modules/blender-rule-adapter.md`
- `docs/modules/3dsmax-rule-adapter.md`
- `docs/modules/houdini-rule-adapter.md`
- `docs/modules/unreal-handoff-inspector.md`
- `docs/modules/portfolio-case-study-index.md`
- `docs/case-studies/asset-protocol-workbench.md`

可运行入口：

Maya / AuroraView 宿主入口：

```powershell
cd <repo>\dcc-hosts\maya-auroraview-host
.\scripts\build_frontend_for_maya.ps1
.\scripts\install_maya_auroraview.ps1 -MayaVersion 2024
```

Maya Script Editor：

```python
import sys
host = r"<repo>\dcc-hosts\maya-auroraview-host"
if host not in sys.path:
    sys.path.insert(0, host)

from ai_tool_ta_maya_host import show_portfolio
show_portfolio()
```

浏览器证据台入口：

```powershell
cd <repo>\showcases\portfolio-site
npm install
npm run dev -- --host 127.0.0.1 --port 5181
```

R0 验证截图：

- `assets/portfolio-site-r0-desktop-final.png`
- `assets/portfolio-site-r0-mobile-final.png`

R1 验证截图：

- `assets/asset-protocol-r1-desktop.png`
- `assets/asset-protocol-r1-mobile.png`
- `assets/asset-protocol-r1-1-desktop.png`
- `assets/asset-protocol-r1-1-mobile-tall.png`
- `assets/asset-protocol-r1-2-desktop.png`
- `assets/asset-protocol-r1-2-mobile-tall.png`
- `assets/asset-protocol-r1-3-full.png`
- `assets/asset-protocol-r1-3-mobile-tall.png`
- `assets/asset-protocol-r1-4-full.png`
- `assets/asset-protocol-r1-4-mobile-tall.png`
- `assets/asset-protocol-r1-4-report-full.png`
- `assets/asset-protocol-r1-5-staged-preset-full.png`
- `assets/asset-protocol-r1-5-exported-report.json`

R2 验证截图：

- `assets/cross-dcc-rule-matrix-r2-desktop-full.png`
- `assets/cross-dcc-rule-matrix-r2-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-1-fixture-editor-full.png`
- `assets/cross-dcc-rule-matrix-r2-1-fix-queue-full.png`
- `assets/cross-dcc-rule-matrix-r2-1-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-1-exported-report.json`
- `assets/cross-dcc-rule-matrix-r2-2-authoring-trace-full.png`
- `assets/cross-dcc-rule-matrix-r2-2-queue-actions-full.png`
- `assets/cross-dcc-rule-matrix-r2-2-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-2-exported-report.json`
- `assets/cross-dcc-rule-matrix-r2-3-publish-gate-full.png`
- `assets/cross-dcc-rule-matrix-r2-3-trace-diff-full.png`
- `assets/cross-dcc-rule-matrix-r2-3-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-3-exported-report.json`

R3 验证截图：

- `assets/visual-review-r3-1-pass-matrix-full.png`
- `assets/visual-review-r3-1-clean-ready-full.png`
- `assets/visual-review-r3-1-mobile-tall.png`
- `assets/visual-review-r3-1-exported-report.json`
- `assets/visual-review-r3-2-batch-overview-full.png`
- `assets/visual-review-r3-2-mobile-tall.png`
- `assets/visual-review-r3-2-batch-report.json`
- `assets/visual-review-r3-3-signal-audit-full.png`
- `assets/visual-review-r3-3-mobile-tall.png`
- `assets/visual-review-r3-3-exported-report.json`
- `assets/visual-review-r3-4-drilldown-full.png`
- `assets/visual-review-r3-4-mobile-tall.png`
- `assets/visual-review-r3-4-exported-report.json`
- `assets/visual-review-r3-4-batch-report.json`
- `assets/visual-review-r3-5-queue-full.png`
- `assets/visual-review-r3-5-mobile-tall.png`
- `assets/visual-review-r3-5-exported-report.json`
- `assets/visual-review-r3-5-batch-report.json`
- `assets/visual-review-r3-6-handoff-full.png`
- `assets/visual-review-r3-6-mobile-tall.png`
- `assets/visual-review-r3-6-exported-report.json`
- `assets/visual-review-r3-6-handoff-packet.json`
- `assets/visual-review-r3-6-batch-report.json`
- `assets/visual-review-r3-7-delivery-full.png`
- `assets/visual-review-r3-7-mobile-tall.png`
- `assets/visual-review-r3-7-exported-report.json`
- `assets/visual-review-r3-7-handoff-packet.json`
- `assets/visual-review-r3-7-batch-report.json`
- `assets/visual-review-r3-8-release-full.png`
- `assets/visual-review-r3-8-mobile-tall.png`
- `assets/visual-review-r3-8-exported-report.json`
- `assets/visual-review-r3-8-release-gate.json`
- `assets/visual-review-r3-8-batch-report.json`
- `assets/visual-review-r3-9-fixture-editor-full.png`
- `assets/visual-review-r3-9-mobile-tall.png`
- `assets/visual-review-r3-9-exported-report.json`
- `assets/visual-review-r3-9-release-gate.json`
- `assets/visual-review-r3-9-batch-report.json`
- `assets/visual-review-r3-10-workflow-map-full.png`
- `assets/visual-review-r3-10-mobile-tall.png`
- `assets/visual-review-r3-10-exported-report.json`
- `assets/visual-review-r3-10-batch-report.json`

R4 验证截图：

- `assets/texture-delivery-r4-1-console-full.png`
- `assets/texture-delivery-r4-1-mobile-tall.png`
- `assets/texture-delivery-r4-1-exported-report.json`
- `assets/texture-delivery-r4-6-adapter-layer-full.png`
- `assets/texture-delivery-r4-6-mobile-tall.png`
- `assets/texture-delivery-r4-6-exported-report.json`
- `assets/texture-delivery-r4-6-adapter-plan.json`
- `assets/texture-delivery-r4-7-public-fixture-delta-full.png`
- `assets/texture-delivery-r4-7-mobile-tall.png`
- `assets/texture-delivery-r4-7-exported-report.json`
- `assets/texture-delivery-r4-7-committed-manifest.json`

R5 验证截图：

- `assets/task-orchestrator-r5-1-workbench-full.png`
- `assets/task-orchestrator-r5-1-mobile-tall.png`
- `assets/task-orchestrator-r5-1-exported-report.json`
- `assets/task-orchestrator-r5-2-workbench-full.png`
- `assets/task-orchestrator-r5-2-mobile-tall.png`
- `assets/task-orchestrator-r5-2-exported-report.json`
- `assets/task-orchestrator-r5-3-workbench-full.png`
- `assets/task-orchestrator-r5-3-mobile-tall.png`
- `assets/task-orchestrator-r5-3-exported-report.json`
- `assets/task-orchestrator-r5-4-workbench-full.png`
- `assets/task-orchestrator-r5-4-mobile-tall.png`
- `assets/task-orchestrator-r5-4-exported-report.json`

R6 验证截图：

- `assets/portfolio-case-study-r6-1-index-full.png`
- `assets/portfolio-case-study-r6-1-mobile-tall.png`
- `assets/portfolio-case-study-r6-1-exported-report.json`
- `assets/portfolio-case-study-r6-2-acceptance-full.png`
- `assets/portfolio-case-study-r6-2-mobile-tall.png`
- `assets/portfolio-case-study-r6-2-exported-report.json`
- `assets/portfolio-case-study-r6-3-manifest-full.png`
- `assets/portfolio-case-study-r6-3-mobile-tall.png`
- `assets/portfolio-case-study-r6-3-exported-report.json`

R7 验证截图：

- `assets/portfolio-case-study-r7-1-pending-receipts-full.png`
- `assets/portfolio-case-study-r7-1-mobile-tall.png`
- `assets/portfolio-case-study-r7-1-exported-report.json`
- `assets/cross-dcc-rule-matrix-r2-4-fix-diff-full.png`
- `assets/cross-dcc-rule-matrix-r2-4-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-4-exported-report.json`
- `assets/portfolio-case-study-r7-2-exported-report.json`
- `assets/portfolio-case-study-r7-3-exported-report.json`
- `assets/portfolio-case-study-r7-4-owner-signoff-full.png`
- `assets/portfolio-case-study-r7-4-mobile-tall.png`
- `assets/portfolio-case-study-r7-4-exported-report.json`
- `assets/portfolio-case-study-r7-5-public-package-full.png`
- `assets/portfolio-case-study-r7-5-mobile-tall.png`
- `assets/portfolio-case-study-r7-5-exported-report.json`
- `public-case-package/README.md`
- `public-case-package/MODULES.md`
- `public-case-package/EVIDENCE_INDEX.md`
- `public-case-package/SIGNOFFS.md`
- `public-case-package/VALIDATION.md`
- `public-case-package/package-manifest.json`

R8 验证截图：

- `assets/task-orchestrator-r8-0-impact-full.png`
- `assets/task-orchestrator-r8-0-mobile-tall.png`
- `assets/task-orchestrator-r8-0-exported-report.json`
- `assets/task-orchestrator-r8-1-impact-paths-full.png`
- `assets/task-orchestrator-r8-1-impact-panel.png`
- `assets/task-orchestrator-r8-1-mobile-tall.png`
- `assets/task-orchestrator-r8-1-exported-report.json`
- `fixtures/dependency-impact/r8-1-rifle-release-candidate.json`
- `assets/portfolio-case-study-r8-2-impact-signoff-full.png`
- `assets/portfolio-case-study-r8-2-mobile-tall.png`
- `assets/portfolio-case-study-r8-2-exported-report.json`
- `assets/task-orchestrator-r8-3-scenario-switch-full.png`
- `assets/task-orchestrator-r8-3-mobile-tall.png`
- `assets/task-orchestrator-r8-3-exported-report.json`
- `fixtures/dependency-impact/r8-3-vehicle-trailer-release.json`
- `assets/portfolio-case-study-r8-3-exported-report.json`
- `assets/task-orchestrator-r8-4-comparison-authoring-full.png`
- `assets/task-orchestrator-r8-4-mobile-tall.png`
- `assets/task-orchestrator-r8-4-exported-report.json`
- `fixtures/dependency-impact/r8-4-authoring-draft.json`
- `assets/portfolio-case-study-r8-4-exported-report.json`
- `assets/task-orchestrator-r8-5-replay-trend-full.png`
- `assets/task-orchestrator-r8-5-mobile-tall.png`
- `assets/task-orchestrator-r8-5-exported-report.json`
- `fixtures/dependency-impact/r8-5-batch-variants.json`
- `assets/portfolio-case-study-r8-5-exported-report.json`
- `assets/task-orchestrator-r8-6-contract-sync-full.png`
- `assets/task-orchestrator-r8-6-mobile-tall.png`
- `assets/task-orchestrator-r8-6-exported-report.json`
- `fixtures/dependency-impact/r8-6-adapter-contract-replay.json`
- `assets/portfolio-case-study-r8-6-exported-report.json`
- `assets/task-orchestrator-r8-7-handoff-diff-full.png`
- `assets/task-orchestrator-r8-7-mobile-tall.png`
- `assets/task-orchestrator-r8-7-exported-report.json`
- `fixtures/dependency-impact/r8-7-production-handoff.json`
- `assets/portfolio-case-study-r8-7-exported-report.json`
- `assets/task-orchestrator-r8-8-signed-receipt-full.png`
- `assets/task-orchestrator-r8-8-mobile-tall.png`
- `assets/task-orchestrator-r8-8-exported-report.json`
- `fixtures/dependency-impact/r8-8-signed-receipt-sandbox.json`
- `assets/portfolio-case-study-r8-8-exported-report.json`
- `assets/task-orchestrator-r8-9-credential-drill-full.png`
- `assets/task-orchestrator-r8-9-mobile-tall.png`
- `assets/task-orchestrator-r8-9-exported-report.json`
- `fixtures/dependency-impact/r8-9-credential-release-drill.json`
- `assets/portfolio-case-study-r8-9-exported-report.json`
- `assets/task-orchestrator-r8-10-failure-lineage-full.png`
- `assets/task-orchestrator-r8-10-mobile-tall.png`
- `assets/task-orchestrator-r8-10-exported-report.json`
- `fixtures/dependency-impact/r8-10-adapter-failure-lineage.json`
- `assets/portfolio-case-study-r8-10-exported-report.json`
- `assets/task-orchestrator-r8-11-readiness-replay-full.png`
- `assets/task-orchestrator-r8-11-mobile-tall.png`
- `assets/task-orchestrator-r8-11-exported-report.json`
- `fixtures/dependency-impact/r8-11-live-adapter-readiness.json`
- `assets/portfolio-case-study-r8-11-exported-report.json`
- `assets/task-orchestrator-r8-12-cutover-drill-full.png`
- `assets/task-orchestrator-r8-12-mobile-tall.png`
- `assets/task-orchestrator-r8-12-exported-report.json`
- `fixtures/dependency-impact/r8-12-production-cutover-drill.json`
- `assets/portfolio-case-study-r8-12-exported-report.json`
- `assets/task-orchestrator-r8-13-private-bridge-full.png`
- `assets/task-orchestrator-r8-13-mobile-tall.png`
- `assets/task-orchestrator-r8-13-exported-report.json`
- `fixtures/dependency-impact/r8-13-private-owner-bridge.json`
- `assets/portfolio-case-study-r8-13-exported-report.json`
- `assets/task-orchestrator-r8-14-drift-freeze-full.png`
- `assets/task-orchestrator-r8-14-mobile-tall.png`
- `assets/task-orchestrator-r8-14-exported-report.json`
- `fixtures/dependency-impact/r8-14-production-drift-freeze.json`
- `assets/portfolio-case-study-r8-14-exported-report.json`
- `assets/task-orchestrator-r8-15-rollback-dispute-full.png`
- `assets/task-orchestrator-r8-15-mobile-tall.png`
- `assets/task-orchestrator-r8-15-exported-report.json`
- `fixtures/dependency-impact/r8-15-rollback-dispute-audit.json`
- `assets/portfolio-case-study-r8-15-exported-report.json`
- `assets/task-orchestrator-r8-16-rollout-incident-full.png`
- `assets/task-orchestrator-r8-16-mobile-tall.png`
- `assets/task-orchestrator-r8-16-exported-report.json`
- `fixtures/dependency-impact/r8-16-rollout-incident-exception.json`
- `assets/portfolio-case-study-r8-16-exported-report.json`
- `assets/task-orchestrator-r8-17-budget-confidence-full.png`
- `assets/task-orchestrator-r8-17-mobile-tall.png`
- `assets/task-orchestrator-r8-17-exported-report.json`
- `fixtures/dependency-impact/r8-17-budget-confidence-aging.json`
- `assets/portfolio-case-study-r8-17-exported-report.json`
- `assets/task-orchestrator-r8-18-release-rehearsal-full.png`
- `assets/task-orchestrator-r8-18-mobile-tall.png`
- `assets/task-orchestrator-r8-18-exported-report.json`
- `fixtures/dependency-impact/r8-18-release-rehearsal-quorum-refresh.json`
- `assets/portfolio-case-study-r8-18-exported-report.json`
- `assets/task-orchestrator-r8-19-decision-sla-full.png`
- `assets/task-orchestrator-r8-19-mobile-tall.png`
- `assets/task-orchestrator-r8-19-exported-report.json`
- `fixtures/dependency-impact/r8-19-release-decision-sla-retention.json`
- `assets/portfolio-case-study-r8-19-exported-report.json`
- `assets/task-orchestrator-r8-20-evidence-lockfile-full.png`
- `assets/task-orchestrator-r8-20-mobile-tall.png`
- `assets/task-orchestrator-r8-20-exported-report.json`
- `fixtures/dependency-impact/r8-20-evidence-lockfile-closeout.json`
- `assets/portfolio-case-study-r8-20-exported-report.json`
- `assets/task-orchestrator-r8-21-acceptance-replay-full.png`
- `assets/task-orchestrator-r8-21-mobile-tall.png`
- `assets/task-orchestrator-r8-21-exported-report.json`
- `fixtures/dependency-impact/r8-21-packet-diff-exception-acceptance.json`
- `assets/portfolio-case-study-r8-21-exported-report.json`
- `assets/task-orchestrator-r8-22-readiness-replay-full.png`
- `assets/task-orchestrator-r8-22-mobile-tall.png`
- `assets/task-orchestrator-r8-22-exported-report.json`
- `fixtures/dependency-impact/r8-22-freeze-owner-response-readiness.json`
- `assets/portfolio-case-study-r8-22-exported-report.json`
- `assets/task-orchestrator-r8-23-promotion-acceptance-full.png`
- `assets/task-orchestrator-r8-23-mobile-tall.png`
- `assets/task-orchestrator-r8-23-exported-report.json`
- `fixtures/dependency-impact/r8-23-promotion-sla-acceptance.json`
- `assets/portfolio-case-study-r8-23-exported-report.json`
- `assets/task-orchestrator-r8-24-rollback-waiver-note-full.png`
- `assets/task-orchestrator-r8-24-mobile-tall.png`
- `assets/task-orchestrator-r8-24-exported-report.json`
- `fixtures/dependency-impact/r8-24-rollback-waiver-release-note.json`
- `assets/portfolio-case-study-r8-24-exported-report.json`
- `assets/task-orchestrator-r8-25-approval-expiry-bundle-full.png`
- `assets/task-orchestrator-r8-25-mobile-tall.png`
- `assets/task-orchestrator-r8-25-exported-report.json`
- `fixtures/dependency-impact/r8-25-approval-expiry-rollback-bundle.json`
- `assets/portfolio-case-study-r8-25-exported-report.json`
- `assets/task-orchestrator-r8-26-seal-renewal-handoff-full.png`
- `assets/task-orchestrator-r8-26-mobile-tall.png`
- `assets/task-orchestrator-r8-26-exported-report.json`
- `fixtures/dependency-impact/r8-26-seal-renewal-incident-handoff.json`
- `assets/portfolio-case-study-r8-26-exported-report.json`
- `assets/task-orchestrator-r8-27-replay-burndown-closure-full.png`
- `assets/task-orchestrator-r8-27-mobile-tall.png`
- `assets/task-orchestrator-r8-27-exported-report.json`
- `fixtures/dependency-impact/r8-27-replay-burndown-closure.json`
- `assets/portfolio-case-study-r8-27-exported-report.json`
- `assets/task-orchestrator-r8-28-closure-response-sla-full.png`
- `assets/task-orchestrator-r8-28-mobile-tall.png`
- `assets/task-orchestrator-r8-28-exported-report.json`
- `fixtures/dependency-impact/r8-28-closure-response-sla.json`
- `assets/portfolio-case-study-r8-28-exported-report.json`
- `assets/task-orchestrator-r8-29-operations-acceptance-full.png`
- `assets/task-orchestrator-r8-29-mobile-tall.png`
- `assets/task-orchestrator-r8-29-exported-report.json`
- `fixtures/dependency-impact/r8-29-operations-acceptance.json`
- `assets/portfolio-case-study-r8-29-exported-report.json`
- `assets/task-orchestrator-r8-30-release-train-closeout-full.png`
- `assets/task-orchestrator-r8-30-mobile-tall.png`
- `assets/task-orchestrator-r8-30-exported-report.json`
- `fixtures/dependency-impact/r8-30-release-train-closeout.json`
- `assets/portfolio-case-study-r8-30-exported-report.json`
- `assets/task-orchestrator-r8-31-replay-aging-variance-full.png`
- `assets/task-orchestrator-r8-31-mobile-tall.png`
- `assets/task-orchestrator-r8-31-exported-report.json`
- `fixtures/dependency-impact/r8-31-replay-aging-variance.json`
- `assets/portfolio-case-study-r8-31-exported-report.json`
- `assets/task-orchestrator-r8-32-release-manager-freeze-full.png`
- `assets/task-orchestrator-r8-32-mobile-tall.png`
- `assets/task-orchestrator-r8-32-exported-report.json`
- `fixtures/dependency-impact/r8-32-release-manager-freeze.json`
- `assets/portfolio-case-study-r8-32-exported-report.json`
- `assets/task-orchestrator-r8-33-go-no-go-packet-full.png`
- `assets/task-orchestrator-r8-33-mobile-tall.png`
- `assets/task-orchestrator-r8-33-exported-report.json`
- `fixtures/dependency-impact/r8-33-go-no-go-packet.json`
- `assets/portfolio-case-study-r8-33-exported-report.json`
- `assets/task-orchestrator-r8-34-post-release-readiness-full.png`
- `assets/task-orchestrator-r8-34-mobile-tall.png`
- `assets/task-orchestrator-r8-34-exported-report.json`
- `fixtures/dependency-impact/r8-34-post-release-readiness.json`
- `assets/portfolio-case-study-r8-34-exported-report.json`
- `assets/task-orchestrator-r8-35-release-closeout-full.png`
- `assets/task-orchestrator-r8-35-mobile-tall.png`
- `assets/task-orchestrator-r8-35-exported-report.json`
- `fixtures/dependency-impact/r8-35-release-closeout.json`
- `assets/portfolio-case-study-r8-35-exported-report.json`
- `assets/task-orchestrator-r8-36-final-archive-full.png`
- `assets/task-orchestrator-r8-36-mobile-tall.png`
- `assets/task-orchestrator-r8-36-exported-report.json`
- `fixtures/dependency-impact/r8-36-final-archive.json`
- `assets/portfolio-case-study-r8-36-exported-report.json`
- `assets/task-orchestrator-r8-37-release-memory-full.png`
- `assets/task-orchestrator-r8-37-mobile-tall.png`
- `assets/task-orchestrator-r8-37-exported-report.json`
- `fixtures/dependency-impact/r8-37-release-memory.json`
- `assets/portfolio-case-study-r8-37-exported-report.json`
- `assets/task-orchestrator-r8-38-retention-approval-full.png`
- `assets/task-orchestrator-r8-38-mobile-tall.png`
- `assets/task-orchestrator-r8-38-exported-report.json`
- `fixtures/dependency-impact/r8-38-retention-approval.json`
- `assets/portfolio-case-study-r8-38-exported-report.json`
- `assets/task-orchestrator-r8-39-access-drillbook-full.png`
- `assets/task-orchestrator-r8-39-mobile-tall.png`
- `assets/task-orchestrator-r8-39-exported-report.json`
- `fixtures/dependency-impact/r8-39-access-drillbook-transfer.json`
- `assets/portfolio-case-study-r8-39-exported-report.json`
- `assets/task-orchestrator-r8-40-readiness-expiry-bundle-full.png`
- `assets/task-orchestrator-r8-40-mobile-tall.png`
- `assets/task-orchestrator-r8-40-exported-report.json`
- `fixtures/dependency-impact/r8-40-readiness-expiry-bundle.json`
- `assets/portfolio-case-study-r8-40-exported-report.json`
- `assets/task-orchestrator-r8-41-reviewer-renewal-notary-full.png`
- `assets/task-orchestrator-r8-41-mobile-tall.png`
- `assets/task-orchestrator-r8-41-exported-report.json`
- `fixtures/dependency-impact/r8-41-reviewer-renewal-notary.json`
- `assets/portfolio-case-study-r8-41-exported-report.json`
- `assets/task-orchestrator-r8-42-query-approval-retention-full.png`
- `assets/task-orchestrator-r8-42-mobile-tall.png`
- `assets/task-orchestrator-r8-42-exported-report.json`
- `fixtures/dependency-impact/r8-42-query-approval-retention.json`
- `assets/portfolio-case-study-r8-42-exported-report.json`
- `assets/task-orchestrator-r8-43-exception-response-handoff-full.png`
- `assets/task-orchestrator-r8-43-mobile-tall.png`
- `assets/task-orchestrator-r8-43-exported-report.json`
- `fixtures/dependency-impact/r8-43-exception-response-handoff.json`
- `assets/portfolio-case-study-r8-43-exported-report.json`
- `assets/task-orchestrator-r8-44-acceptance-sla-drill-full.png`
- `assets/task-orchestrator-r8-44-mobile-tall.png`
- `assets/task-orchestrator-r8-44-exported-report.json`
- `fixtures/dependency-impact/r8-44-acceptance-sla-drill.json`
- `assets/portfolio-case-study-r8-44-exported-report.json`
- `assets/task-orchestrator-r8-45-restoration-ops-readiness-full.png`
- `assets/task-orchestrator-r8-45-mobile-tall.png`
- `assets/task-orchestrator-r8-45-exported-report.json`
- `fixtures/dependency-impact/r8-45-restoration-ops-readiness.json`
- `assets/portfolio-case-study-r8-45-exported-report.json`
- `assets/task-orchestrator-r8-46-command-lock-full.png`
- `assets/task-orchestrator-r8-46-mobile-tall.png`
- `assets/task-orchestrator-r8-46-exported-report.json`
- `fixtures/dependency-impact/r8-46-restore-command-lock.json`
- `assets/portfolio-case-study-r8-46-exported-report.json`
- `assets/task-orchestrator-r8-47-redline-packet-full.png`
- `assets/task-orchestrator-r8-47-mobile-tall.png`
- `assets/task-orchestrator-r8-47-exported-report.json`
- `fixtures/dependency-impact/r8-47-restore-execution-redline.json`
- `assets/portfolio-case-study-r8-47-exported-report.json`
- `assets/task-orchestrator-r8-48-abort-closeout-full.png`
- `assets/task-orchestrator-r8-48-mobile-tall.png`
- `assets/task-orchestrator-r8-48-exported-report.json`
- `fixtures/dependency-impact/r8-48-restore-abort-closeout.json`
- `assets/portfolio-case-study-r8-48-exported-report.json`
- `assets/task-orchestrator-r8-49-owner-reconciliation-full.png`
- `assets/task-orchestrator-r8-49-mobile-tall.png`
- `assets/task-orchestrator-r8-49-exported-report.json`
- `fixtures/dependency-impact/r8-49-post-abort-owner-reconciliation.json`
- `assets/portfolio-case-study-r8-49-exported-report.json`
- `assets/task-orchestrator-r8-50-final-signoff-full.png`
- `assets/task-orchestrator-r8-50-mobile-tall.png`
- `assets/task-orchestrator-r8-50-exported-report.json`
- `fixtures/dependency-impact/r8-50-post-restore-owner-signoff.json`
- `assets/portfolio-case-study-r8-50-exported-report.json`
- `assets/task-orchestrator-r8-51-closure-ledger-full.png`
- `assets/task-orchestrator-r8-51-mobile-tall.png`
- `assets/task-orchestrator-r8-51-exported-report.json`
- `fixtures/dependency-impact/r8-51-owner-closure-exception-ledger.json`
- `assets/portfolio-case-study-r8-51-exported-report.json`
- `assets/task-orchestrator-r8-52-closure-seal-full.png`
- `assets/task-orchestrator-r8-52-mobile-tall.png`
- `assets/task-orchestrator-r8-52-exported-report.json`
- `fixtures/dependency-impact/r8-52-owner-reopen-guardrail.json`
- `assets/portfolio-case-study-r8-52-exported-report.json`
- `assets/task-orchestrator-r8-53-receipt-replay-full.png`
- `assets/task-orchestrator-r8-53-mobile-tall.png`
- `assets/task-orchestrator-r8-53-exported-report.json`
- `fixtures/dependency-impact/r8-53-owner-reopen-incident-drillbook.json`
- `assets/portfolio-case-study-r8-53-exported-report.json`
- `assets/task-orchestrator-r8-54-aging-lock-full.png`
- `assets/task-orchestrator-r8-54-mobile-tall.png`
- `assets/task-orchestrator-r8-54-exported-report.json`
- `fixtures/dependency-impact/r8-54-drillbook-acceptance-ledger.json`
- `assets/portfolio-case-study-r8-54-exported-report.json`
- `public-case-package/package-manifest.json`
