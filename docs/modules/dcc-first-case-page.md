# DCC-first Case Page / Presenter Pack

R51 当前目标：保留 R10.7 case page 作为核心案例报告，同时用 Maya 内一键导出的 Cross-DCC / Engine Reviewer Pack，把 case page、GUI media audit、handoff decision、engine preflight、preset comparison、Animation Continuity Maya L3、Unreal Animation Bridge import L3、Unreal AnimSequence Deep Facts、Character Calibration Maya L3、Character Calibration Drilldown、Unreal Control Rig Bridge L3 after face Skeleton fixture、Unreal Control Rig Fixture Authoring、Unreal Control Rig Face Skeleton Fixture、Unreal Control Rig Deformation Link、Unreal Control Rig Compile Status Bridge、Groom Export Inspector Maya L3、Groom Unreal Import Readiness、Groom Alembic Payload Receipt、Groom Alembic Import/Post-check Readiness、Groom Plugin/API Public Fixture Readiness、Groom Controlled Executor、Spatial Authoring Maya L3、Spatial Authoring Drilldown、Unreal Socket Import Checker、Unreal Socket Authoring Executor、Platform Variant Forge、Platform Variant Unreal Runtime Probe、Platform Variant Generation Planner、Platform Variant Texture Runtime Collector、Platform Variant Public Texture2D Payload Fixture、Platform Variant Controlled Executor、Platform Variant Executor Expansion Receipts、Platform Variant StaticMesh Post-check、Blender bpy L3 runtime、3ds Max pymxs L3 runtime、Unreal Python L3++ engine fact evidence、Unreal preset fact / waiver comparison、Maya-hosted preset fact reviewer queue、Scene Transaction Guard 和 public package manifest 收束成可投递展示包。

## 核心业务逻辑

这个页面解决的是作品集展示的最后一公里：TA 工具不是只证明“能点按钮”，还要证明一条资产从作者协议到交付门禁的业务链路能被复盘。

- Case thesis：说明这是 Maya-hosted AI Tool TA portfolio，不是浏览器 dashboard。
- DCC entry：给出 Maya Script Editor / shelf 入口。
- Business route：按资产交付逻辑组织 7 段流程。
- Composite gate：把 Asset Handoff Gate 的 Ready / Review / Blocked 作为最终业务判定。
- Owner / Engine decision：把 repair preview、owner disposition、engine handoff mock 放进主案例。
- Media plan：把 9 张截图和 1 段录屏变成明确采集清单。
- Presenter Pack：探测 50 个关键证据文件是否存在，并把总体 gate 压成 `CapturePending` / `Review` / `Ready`。
- Preset Fact Review：把 Unreal preset comparison 的 blocked / drift / waived / matched rows 投影成 Maya 内 reviewer queue。
- Scene Transaction Guard：把 Maya 工具运行前后的 scene mutation 输出为 fingerprint、risk rows 和 rollback preview。

## 当前实现

代码入口：

- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
- `showcases/portfolio-site/src/components/DccFirstCasePage.tsx`
- `showcases/portfolio-site/src/lib/auroraviewBridge.ts`

Maya API：

- `showcase_runbook_build_case_page`
- `showcase_runbook_export_case_page`
- `showcase_runbook_audit_gui_media`
- `showcase_runbook_export_gui_media_audit`
- `asset_handoff_export_decision_packet`
- `dcc_presentation_build_pack`
- `dcc_presentation_export_pack`
- `unreal_preset_fact_review_load`
- `unreal_preset_fact_review_export`
- `scene_transaction_export_receipt`

React 入口：

- `Task Orchestrator` 证据视图顶部的 `R51 Cross-DCC / Engine Reviewer Pack`
- `Export Case Page` 按钮
- `Presenter Pack` 按钮
- `Preset Facts` 按钮
- `Txn Guard` 按钮
- 7 段 business route
- Composite Gate 摘要
- Owner / Engine Decision 摘要
- Evidence artifact rows：case page、handoff、decision、GUI manifest、engine preflight、engine preset comparison、Animation Continuity Lab、Unreal Animation Bridge、Unreal AnimSequence Deep Facts、Character Calibration、Character Calibration Drilldown、Unreal Control Rig Bridge、Unreal Control Rig Fixture Authoring、Unreal Control Rig Face Skeleton Fixture、Unreal Control Rig Deformation Link、Unreal Control Rig Compile Status Bridge、Groom Export Inspector、Groom Unreal Import Readiness、Groom Alembic Payload Receipt、Groom Alembic Import/Post-check Readiness、Groom Plugin/API Public Fixture、Groom Controlled Executor、Spatial Authoring、Spatial Authoring Drilldown、Unreal Socket Import Checker、Unreal Socket Authoring Executor、Unreal Socket API docs probe、Platform Variant Forge、Platform Variant Unreal Runtime Probe、Platform Variant Generation Planner、Platform Variant Texture Runtime Collector、Platform Variant Public Texture2D Payload Fixture、Platform Variant Controlled Executor、Platform Variant Executor Expansion Receipts、Platform Variant StaticMesh Post-check、Blender rule adapter、Blender L3 harness、3ds Max rule adapter、3ds Max L3 harness、Unreal handoff inspector、Unreal preset fact comparison、Unreal preset fact review、Scene Transaction Guard
- GUI evidence plan
- GUI media audit
- Presenter Pack evidence file probes
- Asset Handoff Decision Packet artifact row

## 验证结果

- `npm run build` 通过。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` case page smoke 通过：
  - report version：`maya-dcc-portfolio-case-page@1.1.0`
  - sections：6
  - business route steps：7
  - live demo script steps：7
  - GUI shots：9
  - GUI recordings：1
  - handoff assets：2
  - handoff ready/review/blocked：1 / 1 / 0
  - decision repair actions：2
  - decision owner required：1
  - decision engine ready/held：1 / 1
  - supporting artifacts：4
- Maya 2024 `mayapy` media audit smoke 通过：
  - report version：`maya-dcc-gui-media-audit@0.2.0`
  - gate：`CapturePending`
  - required files：10
  - present/review/missing：0 / 0 / 10
- Maya 2024 `mayapy` handoff decision smoke 通过：
  - report version：`maya-asset-handoff-decision-packet@0.1.0`
  - repair actions：2
  - owner dispositions：2
  - engine ready/held：1 / 1
- Maya 2024 `mayapy` presenter pack smoke 通过：
  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r51` / `dcc-first-package@1.48.0`
  - gate：`CapturePending`
  - demo route steps：40
  - key evidence files：50
  - present/missing required evidence files：50 / 0
  - Animation Continuity：L3 / `Blocked` / `maya_anim_curves_collected`
  - Animation Continuity assets ready/blocked：1 / 1
  - Unreal Animation Bridge：L3 / `Blocked` / `unreal_animsequence_assets_imported`
  - Unreal Animation Bridge assets ready/review/blocked：1 / 0 / 1
  - Unreal AnimSequence Deep Facts：L3 / `Blocked` / `unreal_animsequence_deep_facts_collected`
  - Unreal AnimSequence Deep Facts assets ready/review/blocked：0 / 1 / 1
  - Unreal AnimSequence Deep Facts pass/warn/error：15 / 2 / 1
  - Character Calibration：L3 / `Blocked` / `maya_character_calibration_collected`
  - Character Calibration assets ready/review/blocked：1 / 0 / 1
  - Character Calibration Drilldown：L3-derived / `Blocked` / `maya_character_calibration_rows_to_drilldown`
  - Character Calibration Drilldown assets / panels：2 / 14
  - Character Calibration Drilldown owner actions / owner required / manual review：8 / 6 / 2
  - Unreal Control Rig Bridge：L3 / `Blocked` / `unreal_control_rig_bridge_facts_collected`
  - Unreal Control Rig Bridge rows ready/review/blocked：1 / 0 / 1
  - Unreal Control Rig Bridge pass/warn/error：10 / 1 / 5
  - Unreal Control Rig Bridge API / skeletal bindings / CR assets：ready / 1 / 1
  - Unreal Control Rig Bridge assetWrites / productionWrites：0 / 0
  - Unreal Control Rig Fixture Authoring：L3 / `Ready` / `unreal_control_rig_fixture_authoring_collected`
  - Unreal Control Rig Fixture Authoring operations / held：1 / 1
  - Unreal Control Rig Fixture Authoring controls required/runtime/missing：5 / 5 / 0
  - Unreal Control Rig Fixture Authoring assetWrites / productionWrites：1 / 0
  - Unreal Control Rig Face Skeleton Fixture：L3 / `Review` / `unreal_control_rig_face_skeleton_fixture_imported`
  - Unreal Control Rig Face Skeleton Fixture target matches / previous missing resolved：4 / 4, 3 / 3
  - Unreal Control Rig Face Skeleton Fixture assetWrites / productionWrites：2 / 0
  - Unreal Control Rig Deformation Link：L3 / `Blocked` / `unreal_control_rig_deformation_link_collected`
  - Unreal Control Rig Deformation Link rows ready/review/blocked：0 / 1 / 1
  - Unreal Control Rig Deformation Link controls / runtime / Skeleton matches：10 / 5 / 5
  - Unreal Control Rig Deformation Link shape-or-offset readable / direct compile status：5 / 0
  - Unreal Control Rig Deformation Link pass/warn/error：13 / 2 / 5
  - Unreal Control Rig Deformation Link assetWrites / productionWrites：0 / 0
  - Unreal Control Rig Compile Status Bridge：L3 / `Blocked` / `unreal_control_rig_compile_status_collected`
  - Unreal Control Rig Compile Status rows ready/review/blocked：0 / 1 / 1
  - Unreal Control Rig Compile Status candidates / methods / invoked / succeeded：1 / 1 / 1 / 1
  - Unreal Control Rig Compile Status direct status / diagnostics / settings：0 / 0 / 1
  - Unreal Control Rig Compile Status dirty before/after：0 / 0
  - Unreal Control Rig Compile Status pass/warn/error：10 / 2 / 4
  - Unreal Control Rig Compile Status assetWrites / productionWrites：0 / 0
  - Spatial Authoring：L3 / `Blocked` / `maya_spatial_authoring_collected`
  - Spatial Authoring assets ready/review/blocked：1 / 0 / 1
  - Spatial Authoring Drilldown：L3-derived / `Blocked` / `maya_spatial_authoring_rows_to_drilldown`
  - Spatial Authoring Drilldown assets / panels：2 / 18
  - Spatial Authoring Drilldown owner actions / owner required / manual review：9 / 7 / 2
  - Unreal Socket Import Checker：L3 / `Blocked` / `unreal_socket_facts_collected`
  - Unreal Socket Authoring Executor：L3 / `Blocked` / `unreal_socket_authoring_executor_api_limited`
  - Unreal Socket Authoring Executor selected/held：1 / 1
  - Unreal Socket Authoring Executor expected/created sockets：2 / 0
  - Platform Variant Forge：L3-linked / `Blocked` / `platform_variant_plan_joined_to_unreal_facts`
  - Platform Variant Forge variants ready/review/blocked：2 / 0 / 1
  - Platform Variant Unreal Runtime Probe：L3 / `Blocked` / `unreal_variant_runtime_assets_collected`
  - Platform Variant Unreal Runtime variants ready/review/blocked：0 / 2 / 1
  - Platform Variant Unreal Runtime checks pass/warn/error：21 / 4 / 2
  - Platform Variant Generation Planner：L3-derived / `Blocked` / `runtime_drift_to_generation_plan`
  - Platform Variant Generation operations ready/review/blocked/satisfied：1 / 3 / 2 / 5
  - Platform Variant Texture Runtime Collector：L3 / `Blocked` / `unreal_material_texture_facts_collected`
  - Platform Variant Texture Runtime variants ready/review/blocked：1 / 1 / 1
  - Platform Variant Texture Runtime checks pass/warn/error：19 / 1 / 1
  - Platform Variant Public Texture2D Payload Fixture：L3 / `Blocked` / `unreal_texture_payload_fixture_collected`
  - Platform Variant Texture Payload variants ready/review/blocked：2 / 0 / 1
  - Platform Variant Texture Payload checks pass/warn/error：20 / 0 / 1
  - Platform Variant Controlled Executor：L3 / `Ready` / `unreal_texture_budget_executor_rolled_back`
  - Platform Variant Controlled Executor executed/post/rollback：1 / 1 / 1
  - Platform Variant Controlled Executor checks pass/warn/error：7 / 0 / 0
  - Platform Variant Controlled Executor writes / persistent mutation：2 asset writes / false
  - Platform Variant Executor Expansion：L3-derived / `Review` / `executor_receipts_linked_to_rolled_back_unreal_write`
  - Platform Variant Executor Expansion receipts：5，LOD / Nanite / collision
  - Platform Variant Executor Expansion no-op / approval-ready / readiness-only / blocked：2 / 1 / 2 / 0
  - Blender adapter：L3 / `Blocked` / `bpy_scene_collected`
  - 3ds Max adapter：L3 / `Blocked` / `pymxs_scene_collected`
  - Animation/Max/Blender/Platform gate 的 `Blocked` 来自 synthetic fixture 中故意保留的失败资产、平台阻断或 runtime drift，不是 runtime 缺失
  - Unreal inspector：L3++ / `unreal_engine_facts_matched`
  - Unreal engine facts：4 / 4 matched
  - Unreal preset fact rows matched/drift/waived/blocked：7 / 1 / 1 / 1
  - Unreal preset review rows / queue / blocked / waivers：10 / 3 / 1 / 1
  - Scene transaction gate / rollback / risk rows：Review / 9 / 4
  - GUI media present/review/missing：0 / 0 / 10
  - Groom Controlled Executor：L3 / `Blocked` / `unreal_groom_executor_wrong_asset_class_rolled_back`
  - Groom Controlled Executor import：selected=1，attempted=true，succeeded=true，imported class=`StaticMesh`
  - Groom Controlled Executor binding / rollback：binding attempted=false，rollback=true，residual assets=0，persistentMutation=false

## 当前 artifact

Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r51-groom-controlled-executor-presentation-pack-20260806-022956.json
```

Unreal Control Rig Bridge original R37：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-205656.json
```

Unreal Control Rig Fixture Authoring：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-fixture-authoring-20260805-230323.json
```

Unreal Control Rig Bridge after face Skeleton fixture：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-235140.json
```

Unreal Control Rig Face Skeleton Fixture：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-face-skeleton-fixture-20260805-235115.json
```

Unreal Control Rig Deformation Link：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-235154.json
```

Unreal Control Rig Compile Status Bridge：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-compile-status-20260806-001504.json
```

Platform Variant Unreal Runtime Probe：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-unreal-runtime-20260805-185026.json
```

Platform Variant Generation Planner：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-generation-plan-20260805-190052.json
```

Platform Variant Texture Runtime Collector：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-runtime-20260805-191529.json
```

Platform Variant Public Texture2D Payload Fixture：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-payload-runtime-20260805-193515.json
```

Platform Variant Controlled Executor：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-controlled-executor-20260805-200810.json
```

Platform Variant Executor Expansion Receipts：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-executor-expansion-20260805-201222.json
```

Unreal Animation Bridge：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-import-l3-20260805-173309.json
```

Animation Continuity Lab：

```text
<repo>\dcc-hosts\animation-continuity-lab\artifacts\animation-continuity-maya-l3-20260805-162744.json
```

Character Calibration：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json
```

Character Calibration Drilldown：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-drilldown-20260805-202259.json
```

Spatial Authoring：

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-maya-l3-20260805-181524.json
```

Spatial Authoring Drilldown：

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-drilldown-20260805-203713.json
```

Scene Transaction Guard：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-20260804-195730.json
```

Unreal preset fact review：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json
```

Unreal inspector：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

Unreal preset fact comparison：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

Blender adapter：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260804-201125.json
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json
```

3ds Max adapter：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
```

3ds Max L3 runtime：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260805-153232.json
```

Case page：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
```

Supporting artifacts：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
```

Media audit：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```

Handoff decision packet：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
```

## 下一轮

下一轮优先解决 Groom `.abc` 导入为 `StaticMesh` 的 importer mode/schema/桥接问题、gameplay attach fixture 或 Houdini 非 Maya adapter。Maya GUI 截图/录屏保留到最后集中采集。


## R39 Platform Variant StaticMesh Post-check

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-staticmesh-postcheck-20260805-215500.json`，demo route 增至 28 步，evidence probe 增至 36 个。

## R40 Unreal Socket Authoring Executor

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-authoring-executor-20260805-222014.json` 和 `<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-api-docs-20260805-222200.json`，demo route 增至 29 步，evidence probe 增至 38 个。

R40 的结论是 API-limited gate：Unreal 5.3 Python 能看到 `SkeletalMesh.add_socket(socket, add_to_skeleton=False)`，但 commandlet-created `SkeletalMeshSocket.socket_name` 和 `bone_name` 不可写，因此受控 executor 只输出安全阻断和 owner/readiness 证据，不把 socket auto-fix 伪装成成功。

## R41 Unreal AnimSequence Deep Facts

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-deep-facts-20260805-224206.json`，demo route 增至 30 步，evidence probe 增至 39 个。R41 不重新导入 FBX，只读采集 existing public AnimSequence 的 duration、derived frame span、frame-rate、curve/root/compression metadata visibility，并保持 assetWrites=0。

## R42 Unreal Control Rig Fixture Authoring

R42 Presenter Pack 接入 `<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-fixture-authoring-20260805-230323.json` 和 post-authoring bridge `<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-230343.json`，demo route 增至 31 步，evidence probe 增至 40 个。R42 通过 Unreal Python 创建 public `CR_HeroFace`，写入 5 个 required controls，生产写入为 0；复跑 bridge 后 approved 角色行 Ready，TMP 行继续 Blocked。

## R43 Unreal Control Rig Deformation Link

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-232729.json`，demo route 增至 32 步，evidence probe 增至 41 个。R43 通过 Unreal Python 只读 `CR_HeroFace`、`SK_Hero_Skeleton` 和 Maya controlRigMappings，证明 5 个 runtime controls 和 shape/offset facts 都可读，但 public Skeleton 只确认 2 个 deformation target matches，direct compile status 仍为 0 行可读；这使 approved 角色在更深的绑定层继续 Blocked，且 assetWrites=0。

## R44 Unreal Control Rig Face Skeleton Fixture

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-face-skeleton-fixture-20260805-235115.json`、post-face bridge `<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-235140.json` 和 post-face deformation link `<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-235154.json`，demo route 增至 33 步，evidence probe 增至 42 个。R44 通过 Maya 生成 public face Skeleton FBX 并导入 Unreal，确认 required target matches 4 / 4，previous missing resolved 3 / 3；复查后 Skeleton target matches 从 2 提升到 5，approved 行从 Blocked 推进到 Review，剩余阻断集中在 direct compile status API 不可读和 TMP 源头故障。

## R45 Unreal Control Rig Compile Status Bridge

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-compile-status-20260806-001504.json`，demo route 增至 34 步，evidence probe 增至 43 个。R45 通过 Unreal Python 对 public `CR_HeroFace` 执行只读编译状态采集，确认 compile method visible / invoked / succeeded = 1 / 1 / 1，dirtyAfter=0，assetWrites=0。结论是 approved 行处于 Review：编译动作可调用，但 direct status / diagnostics 仍不可读，不能把“调用成功”包装成“Control Rig 可交付批准”。

## R46 Groom Export Inspector

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-export-inspector-maya-l3-20260806-003711.json`，demo route 增至 35 步，evidence probe 增至 44 个。R46 通过 Maya 2026 `mayapy` 创建 public scalp planes 和 curve strands，并从 Maya 场景回读 root UV、strand ID、guide curve、Alembic payload 和 Unreal binding intent。结果为 L3 / `Blocked`，2 groom rows，1 Ready，1 Blocked，11 strands，2 guides，root UV missing / duplicate strand IDs = 1 / 1，9 owner actions，assetWrites=0。核心业务发现：groom 交付必须把 root UV、guide curve 和 stable strand ID 当作发布事实，而不是附属 mesh 属性。

## R47 Groom Unreal Import Readiness

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-unreal-readiness-20260806-010008.json`，demo route 增至 36 步，evidence probe 增至 45 个。R47 通过 Unreal 5.3.2 `UnrealEditor-Cmd -run=pythonscript` 进入 public `.uproject`，读取 R46 Maya groom facts 并采集 Groom/Alembic API visibility、target SkeletalMesh presence、expected Groom / Binding assets 和 zero-write boundary。结果为 L3 / `Blocked`，2 groom rows，source Ready / Blocked = 1 / 1，AssetImportTask visible rows = 2，AlembicImportFactory visible rows = 2，target SkeletalMesh present rows = 1，GroomAsset / GroomBindingAsset API visible rows = 0 / 0，expected Groom / Binding assets present = 0 / 0，12 pass / 4 warning / 6 error，10 owner actions，assetWrites=0。核心业务发现：Groom 导入必须先证明 UE 侧插件/API/目标绑定环境可用，不能因为 Alembic import API 可见就假装 Groom 资产已经可发布。

## R48 Groom Alembic Payload Receipt

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-alembic-payload-20260806-011837.json` 和 `<repo>\dcc-hosts\groom-export-inspector\artifacts\cache\groom-alembic-r48\groom_hero_hair_001.abc`，demo route 增至 37 步，evidence probe 增至 47 个。R48 通过 Maya 2026 `mayapy` 加载 `AbcExport`，只选择 approved groom 行写出 public synthetic Alembic cache，并记录 bytes/hash；TMP groom 因 source/cache contract 不合格继续 held。结果为 L3 / `Blocked`，selected / held = 1 / 1，exportSucceeded=1，cacheFiles=1，cacheBytes=10271，cacheHashes=1，14 pass / 0 warning / 2 error，2 owner actions，assetWrites=1 仅限 repo artifact cache，engineWrites=0，productionWrites=0。核心业务发现：能生成 cache 不等于能放行全部 groom；坏行必须继续挡在 cache payload 之前。

## R49 Groom Alembic Import/Post-check Readiness

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-alembic-import-postcheck-20260806-013949.json`，demo route 增至 38 步，evidence probe 增至 48 个。R49 通过 Unreal 5.3.2 `UnrealEditor-Cmd -run=pythonscript` 读取 R48 `.abc` cache，验证 sha256 continuity，dry-run `AssetImportTask`，检查 `AlembicImportFactory`、Groom API、目标 `SK_HeroFace`、期望 Groom / Binding 资产和 zero-write boundary。结果为 L3 / `Blocked`，2 operations，1 import candidate，cache hash matched rows = 1，AssetImportTask dry-run rows = 2，AlembicImportFactory visible rows = 2，Groom API ready rows = 0，target SkeletalMesh present rows = 1，import executed / held = 0 / 2，24 pass / 2 warning / 2 error，4 owner actions，assetWrites=0，engineWrites=0，productionWrites=0。核心业务发现：`.abc` cache 连续性和 Alembic factory 可见只能证明导入通路可预检；Groom publish ready 必须继续等待 Groom API、目标 GroomAsset / BindingAsset 和受控 executor rollback receipt。

## R50 Groom Plugin/API Public Fixture Readiness

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-plugin-api-fixture-20260806-020048.json`，demo route 增至 39 步，evidence probe 增至 49 个。R50 在 public Unreal `.uproject` 显式启用 `GeometryCache`、`AlembicImporter`、`HairStrands`、`AlembicHairImporter`，再通过 Unreal 5.3.2 commandlet 采集 plugin descriptor、project request 和 Python API class surface。结果为 L3 / `Ready`，4/4 plugin descriptors found，4/4 project plugin requests，Groom / Hair / Alembic / GeometryCache class rows = 47 / 56 / 14 / 16，Groom import API ready=true，AlembicImportFactory visible=true，10 pass / 0 warning / 0 error，assetWrites=0，engineWrites=0，productionWrites=0。核心业务发现：R49 的 Groom API 缺口可以通过 public fixture plugin 配置消除，下一步应进入 controlled executor 的真实导入、post-check 和 rollback receipt。

## R51 Groom Controlled Executor

当前 Presenter Pack 已接入 `<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-controlled-executor-20260806-022310.json`，demo route 增至 40 步，evidence probe 增至 50 个。R51 读取 R49 post-check 和 R50 plugin/API fixture，只选择 approved public `.abc` cache，进入 Unreal 5.3.2 执行 `AssetImportTask`，再检查导入 class、binding method、post-check 和 rollback receipt。结果为 L3 / `Blocked` / `unreal_groom_executor_wrong_asset_class_rolled_back`，import attempted/succeeded=true/true，imported asset class=`StaticMesh`，wrongImportedClass=true，BindingAsset 未创建，rollback=true，residual assets=0，assetWrites=4，engineWrites=0，productionWrites=0，persistentMutation=false。核心业务发现：当前缺口已收窄到 Alembic hair importer 的 mode/schema 或 Editor Utility / C++ bridge，不再是 plugin/API readiness。
