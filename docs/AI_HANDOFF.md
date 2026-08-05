# AI 接手说明

## 1. 最终展示效果

目标不是网页作品集，而是 DCC / 引擎内展示的工具管线 TA 能力。

最终 reviewer 应看到：

- Maya 2024 内通过 AuroraView 打开工具面板。
- 面板里有资产协议、规则矩阵、视觉评审、贴图交付、任务编排、资产放行、引擎预检、场景事务保护、动画连续性、角色校准、Groom Export Inspector、空间作者、Unreal socket readiness / authoring readiness、平台变体规划、Unreal runtime 对照、generation planner、texture runtime collector、public Texture2D payload fixture、controlled executor、executor expansion receipts、StaticMesh post-check 等模块。
- 每个模块能导出 JSON artifact，说明业务事实、规则判定、fix preview、owner 边界和写入边界。
- 非 Maya 证据已经覆盖 Blender `bpy` L3、3ds Max `pymxs` L3、Unreal Python L3++；动画线已有 Maya `mayapy` L3 keyed animCurve 证据、Unreal Animation Bridge import L3 和 Unreal AnimSequence Deep Facts L3；角色线已有 Character Calibration Maya L3、Character Calibration Drilldown、Unreal Control Rig Bridge L3、Unreal Control Rig Fixture Authoring L3、Unreal Control Rig Face Skeleton Fixture L3、Unreal Control Rig Deformation Link L3 和 Unreal Control Rig Compile Status Bridge L3；groom 线已有 Groom Export Inspector Maya L3、Groom Unreal Import Readiness L3 和 Groom Alembic Payload Receipt L3；空间作者线已有 Spatial Authoring Maya L3、Spatial Authoring Drilldown、Unreal Socket Import Checker L3 和 Unreal Socket Authoring Executor API-limited L3 证据；平台变体线已有连接 Unreal preset facts 的 `L3-linked` planning artifact、Unreal runtime-vs-plan L3 artifact、runtime drift -> generation plan artifact、Unreal material / texture runtime artifact、public Texture2D payload L3 artifact、受控 Unreal executor L3 artifact、LOD/Nanite/collision executor receipt artifact，以及 read-only StaticMesh post-check artifact。
- Presenter Pack 把所有关键证据汇总成 reviewer 可读的发布包。

当前稳定展示包：

```text
public-case-package/DCC_FIRST_PACKAGE.md
public-case-package/dcc-first-package-manifest.json
dcc-hosts/maya-auroraview-host/artifacts/r48-groom-alembic-payload-presentation-pack-20260806-012304.json
```

## 2. 当前完成度

稳定基线：R48。

已完成：

- Maya AuroraView Host / Presenter Pack
- Asset Protocol Workbench
- Cross-DCC Rule Matrix
- Visual Review Studio
- Texture Delivery Console
- Task Orchestrator
- Asset Handoff Gate
- Unreal Handoff Inspector
- Scene Transaction Guard
- Animation Continuity Lab Maya L3
- Unreal Animation Bridge import L3
- Unreal AnimSequence Deep Facts L3
- Character Calibration Studio Maya L3
- Character Calibration Drilldown L3-derived
- Unreal Control Rig Bridge L3
- Unreal Control Rig Fixture Authoring L3
- Unreal Control Rig Face Skeleton Fixture L3
- Unreal Control Rig Deformation Link L3
- Unreal Control Rig Compile Status Bridge L3
- Groom Export Inspector Maya L3
- Groom Unreal Import Readiness L3
- Groom Alembic Payload Receipt L3
- Spatial Authoring Workbench Maya L3
- Spatial Authoring Drilldown L3-derived
- Unreal Socket Import Checker L3
- Platform Variant Forge L3-linked
- Platform Variant Unreal Runtime Probe L3
- Platform Variant Generation Planner L3-derived
- Platform Variant Texture Runtime Collector L3
- Platform Variant Public Texture2D Payload Fixture L3
- Platform Variant Controlled Executor L3
- Platform Variant Executor Expansion Receipts L3-derived
- Platform Variant StaticMesh Post-check L3
- Unreal Socket Authoring Executor L3 API-limited readiness
- Blender Rule Adapter L3
- 3ds Max Rule Adapter L3
- Maya command bridge
- 轻量验证脚本 `scripts/validate_loop.ps1`

仍缺：

- Maya GUI 9 张 PNG 和 1 段 MP4，留到最后人工采集。
- MotionBuilder、Houdini、Control Rig compile status Editor Utility / C++ bridge、socket C++ / Editor Utility Blueprint adapter、Groom Alembic import/post-check 等后续工具线。

## 3. R48 当前断点与已完成工具线

`Animation Continuity Lab` 已完成首轮闭环：L2 contract smoke、Maya `mayapy` L3 keyed animCurve collector、Presenter Pack 接入、public manifest 接入和模块文档。

`Unreal Animation Bridge` 已完成 import L3 闭环：读取 R23 Maya L3 artifact，生成 public Maya FBX clips，通过 UnrealEditor-Cmd 进入公开 test `.uproject`，导入并采集 Skeleton / SkeletalMesh / AnimSequence runtime facts。

`Unreal AnimSequence Deep Facts` 已完成 R41 闭环：读取 R25 import L3 artifact，通过 UnrealEditor-Cmd 只读打开 public `.uproject` 中已有 AnimSequence，采集 play length、derived frame span、direct frame-rate、curve metadata API、root motion setting、compression setting 和 read-only boundary。结果为 L3 / `Blocked` / `unreal_animsequence_deep_facts_collected`，2 runtime rows，2 / 2 duration frame spans matched，0 Ready，1 Review，1 Blocked，15 pass，2 warning，1 error，assetWrites=0。`RunStart` 因 UE Python 不暴露 curve names 进入 Review，`Attack_A` 保留 R25 source bridge 业务错误。

`Character Calibration Studio` 已完成 Maya L3 闭环：生成 public synthetic character mesh / joint DAG / calibration attrs，采集 topology signature、joint coverage、skin influence budget、calibration delta、face params、Control Rig mapping 和 mirror pair coverage。

`Character Calibration Drilldown` 已完成 R35 闭环：读取 Character Calibration Maya L3 artifact，把 flat rule rows 投影成 Maya/AuroraView 可消费的 topology、skeleton、skin、calibration、face、Control Rig、mirror drilldown panels，并输出 owner action、fix preview 和 mutation boundary。结果为 L3-derived / `Blocked` / `maya_character_calibration_rows_to_drilldown`，2 character drilldowns，14 panels，8 issue rows，8 owner actions，6 owner-required，2 manual-review，productionWrites=0。

`Unreal Control Rig Bridge` 已完成 R42 复验闭环：读取 Character Calibration Drilldown artifact，通过 UnrealEditor-Cmd 进入 public `.uproject`，采集 ControlRig / RigVM API、SkeletalMesh / Skeleton 绑定和 expected Control Rig asset path facts。post-authoring 结果为 L3 / `Blocked` / `unreal_control_rig_bridge_facts_collected`，2 character rows，1 Ready，0 Review，1 Blocked，10 pass，1 warning，5 error，1 个 SkeletalMesh/Skeleton binding，1 个 expected Control Rig asset，assetWrites=0，productionWrites=0。approved 行已 Ready，TMP 行被 Maya 源头和 Unreal 目标同时阻断。

`Unreal Control Rig Fixture Authoring` 已完成 R42 闭环：读取 R37 bridge artifact，只选择 approved 角色行，通过 Unreal 5.3.2 Python 创建 `/Game/AI_Tool_TA/Characters/CR_HeroFace`，用 `RigHierarchyController.add_control` 写入 5 个 required controls，保存 1 个 public fixture asset，TMP 行 held。结果为 L3 / `Ready` / `unreal_control_rig_fixture_authoring_collected`，operations/held 1 / 1，created/saved assets 1 / 1，required/runtime/missing controls 5 / 5 / 0，assetWrites=1，productionWrites=0。

`Unreal Control Rig Deformation Link` 已完成 R43 闭环：读取 R42 post-authoring bridge 和 fixture authoring artifact，通过 Unreal 5.3.2 Python 只读 `CR_HeroFace`、`SK_Hero_Skeleton` 和 Maya `controlRigMappings`，输出 control -> deformation target -> Skeleton target match、hierarchy shape/offset readability 和 compile API surface。结果为 L3 / `Blocked` / `unreal_control_rig_deformation_link_collected`，2 character rows，10 control links，5 runtime controls，5 shape/offset-readable controls，2 Skeleton target matches，0 direct compile-status rows，12 pass / 2 warning / 6 error，assetWrites=0，productionWrites=0。关键结论：控件存在不等于绑定可交付，approved 行仍缺 `Eye_L`、`Eye_R`、`Jaw` Skeleton target matches。

`Unreal Control Rig Face Skeleton Fixture` 已完成 R44 闭环：Maya 2026 `mayapy` 生成 public face Skeleton FBX，Unreal 5.3.2 导入 `/Game/AI_Tool_TA/Characters/SK_HeroFace` 和 `SK_HeroFace_Skeleton`，确认 required target matches 4 / 4、previous R43 missing resolved 3 / 3、assetWrites=2、productionWrites=0。随后复跑 bridge / deformation-link：post-face deformation link 为 L3 / `Blocked`，2 character rows，10 control links，5 runtime controls，5 Skeleton target matches，approved 行从 Blocked 变 Review，TMP 行继续 Blocked，13 pass / 2 warning / 5 error，assetWrites=0。当前剩余角色线核心缺口是 direct compile status 的 Editor Utility / C++ bridge。

`Unreal Control Rig Compile Status Bridge` 已完成 R45 闭环：读取 R44 post-face deformation-link artifact，通过 Unreal 5.3.2 Python 加载 public `CR_HeroFace`，调用可见的 `ControlRigBlueprint` compile 方法，并记录 direct status / diagnostic 可读性、compile settings、package dirty-state 和 no-save boundary。结果为 L3 / `Blocked` / `unreal_control_rig_compile_status_collected`，2 character rows，approved 行 Review，TMP 行 Blocked，compile candidate / method visible / invoked / succeeded = 1 / 1 / 1 / 1，direct status / diagnostics / settings = 0 / 0 / 1，dirtyAfter=0，10 pass / 2 warning / 4 error，assetWrites=0，productionWrites=0。关键结论：compile 方法可调用，但 UE Python 仍不能提供 direct diagnostic/status，因此不把方法调用包装成完整 compile approval。

`Groom Export Inspector` 已完成 R46 闭环：Maya 2026 `mayapy` 创建 public synthetic scalp planes 和 curve strands，从 Maya 场景回读 root UV、strand ID、guide flag、Alembic payload 和 Unreal Groom / Binding intent。结果为 L3 / `Blocked` / `maya_groom_export_facts_collected`，2 groom rows，approved 行 Ready，TMP 行 Blocked，11 strands，2 guides，root UV missing / duplicate strand IDs = 1 / 1，11 pass / 2 warning / 7 error，9 owner actions，assetWrites=0，productionWrites=0。关键结论：groom 交付不是 mesh 交付，root UV、guide curve、strand ID 和 Alembic payload 是一等发布事实。

`Groom Unreal Import Readiness` 已完成 R47 闭环：读取 R46 Groom Export Inspector Maya L3 artifact，通过 Unreal 5.3.2 `UnrealEditor-Cmd -run=pythonscript` 进入 public `.uproject`，只读采集 Groom/Alembic API visibility、target SkeletalMesh presence、expected Groom / Binding assets 和 zero-write boundary。结果为 L3 / `Blocked` / `unreal_groom_import_readiness_collected`，2 groom rows，source Ready / Blocked = 1 / 1，AssetImportTask visible rows = 2，AlembicImportFactory visible rows = 2，target SkeletalMesh present rows = 1，GroomAsset / GroomBindingAsset API visible rows = 0 / 0，expected Groom / Binding assets present = 0 / 0，12 pass / 4 warning / 6 error，10 owner actions，assetWrites=0，productionWrites=0。关键结论：Alembic import API 可见只说明可进入导入通道，Groom 资产发布仍必须显式证明 Groom 插件/API 和 Binding 目标环境。

`Groom Alembic Payload Receipt` 已完成 R48 闭环：读取 R46 Groom Export Inspector Maya L3 source facts，通过 Maya 2026 `mayapy` 加载 `AbcExport`，只选择 approved groom 行写出 public synthetic `.abc` cache，并把 TMP groom 行保持 held。结果为 L3 / `Blocked` / `maya_groom_alembic_payload_exported`，selected / held rows = 1 / 1，exportSucceeded=1，cacheFiles=1，cacheBytes=10271，cacheHashes=1，14 pass / 0 warning / 2 error，2 owner actions，assetWrites=1 仅限 repo artifact cache，engineWrites=0，productionWrites=0。关键结论：Maya 侧 Alembic cache 可以真实生成，但坏 groom 行必须继续阻断，不能为了展示而写入 cache。

`Spatial Authoring Workbench` 已完成 Maya L3 闭环：生成 public synthetic joints / locator attrs，采集 socket parent joint、offset、mirror pair、hotspot semantic/owner、pose frame、local space、preview locator 和 pose transfer approval。

`Spatial Authoring Drilldown` 已完成 R36 闭环：读取 Spatial Authoring Maya L3 artifact，把 flat rule rows 投影成 Maya/AuroraView 可消费的 protocol、parent joint、socket、mirror、hotspot、pose frame、transform、preview locator、pose transfer drilldown panels，并输出 owner action、fix preview 和 mutation boundary。结果为 L3-derived / `Blocked` / `maya_spatial_authoring_rows_to_drilldown`，2 spatial drilldowns，18 panels，9 issue rows，9 owner actions，7 owner-required，2 manual-review，productionWrites=0。

`Unreal Socket Import Checker` 已完成 R38 闭环：读取 Spatial Authoring Drilldown artifact，通过 UnrealEditor-Cmd 进入 public `.uproject`，采集 SkeletalMesh / Skeleton / SkeletalMeshSocket API、目标资产存在性和 expected socket coverage。结果为 L3 / `Blocked` / `unreal_socket_facts_collected`，2 spatial rows，0 Ready，0 Review，2 Blocked，9 pass，2 warning，9 error，socket API ready，4 expected sockets，0 runtime sockets，assetWrites=0，productionWrites=0。approved rifle 行被缺 `SK_Hand_L` / `SK_Hand_R` 阻断，TMP backpack 行被 Maya 源头和 Unreal 目标同时阻断。

`Unreal Socket Authoring Executor` 已完成 R40 闭环：读取 R38 socket readiness artifact，只选择 approved rifle 行进入受控 Unreal executor，TMP backpack 行保持 held / no-write。Unreal 5.3.2 Python 暴露 `SkeletalMesh.add_socket(socket, add_to_skeleton=False)`，但 commandlet-created `SkeletalMeshSocket.socket_name` 和 `bone_name` 是 read-only；构造参数和 `rename()` 只改 UObject name，不改 socket identity。结果为 L3 / `Blocked` / `unreal_socket_authoring_executor_api_limited`，selected/held 1 / 1，expected/created sockets 2 / 0，9 pass / 0 warning / 2 error，assetWrites=0，productionWrites=0。这是正确的 API-limited gate，不能伪装成 socket auto-fix 成功。

`Platform Variant Forge` 已完成 R28 首版闭环：读取 public-safe PC/Mobile variant fixture，连接已有 Unreal preset fact comparison L3++ artifact，检查 target path、owner approval、triangle/texture/material/draw budget、LOD coverage、Nanite、shader feature、collision policy，输出 `L3-linked` planning artifact。本轮没有新增 Unreal 写入，定位是平台派生计划和门禁证据。

`Platform Variant Unreal Runtime Probe` 已完成 R29 runtime-vs-plan 闭环：通过 UnrealEditor-Cmd 进入公开 test `.uproject`，采集计划中 PC/Mobile target StaticMesh 的 path、LOD、material slot、Nanite、collision runtime facts，并与 R28 variant plan 对照。结果为 L3，3 variants，0 Ready / 2 Review / 1 Blocked，21 pass / 4 warning / 2 error；写入只发生在 `/Game/AI_Tool_TA` 公开 fixture。

`Platform Variant Generation Planner` 已完成 R30 dry-run generation 闭环：读取 R29 runtime drift 与 R28 plan，生成 missing LOD、Nanite policy、material merge、texture downscale、collision simplification、source import、target variant creation 等 11 个 operation contract，结果为 1 Ready / 3 Review / 2 Blocked / 5 Satisfied。该 artifact 不写 Unreal 资产，只给出 deterministic params、Unreal Python preview、writeSet、rollback 和 owner approval 边界。

`Platform Variant Texture Runtime Collector` 已完成 R31 material / texture runtime 闭环：通过 UnrealEditor-Cmd 进入公开 test `.uproject`，采集计划中 StaticMesh 的 material slots、material dependency query、material expression texture references、Texture2D 尺寸/估算内存/压缩/sRGB/readability。结果为 L3，3 variants，1 Ready / 1 Review / 1 Blocked，19 pass / 1 warning / 1 error；assetWrites=0。Mobile HeroPanel 的 Review 明确来自 synthetic material 没有真实 Texture2D payload，不是 collector 缺失。

`Platform Variant Public Texture2D Payload Fixture` 已完成 R32 public payload 闭环：通过 UnrealEditor-Cmd 进入公开 test `.uproject`，生成 public 2048 PNG，导入为 `/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor`，挂到 `M_HeroPanel`，再采集 StaticMesh -> material -> Texture2D facts。结果为 L3，3 variants，2 Ready / 0 Review / 1 Blocked，20 pass / 0 warning / 1 error；最终提交的幂等 rerun 为 assetWrites=0，写入边界仍只限 `/Game/AI_Tool_TA` public fixture。HeroPanel Mobile 已经从缺 payload 的 Review 进入 Ready，剩余 Blocked 是故意保留的 vehicle 缺源资产样本。

`Platform Variant Controlled Executor` 已完成 R33 受控执行闭环：读取 R30 generation plan 和 R32 texture payload artifact，选择 HeroPanel Mobile texture downscale 的 public-safe max texture size clamp，记录 preflight fingerprint，执行 `0 -> 2048`，验证 post-state，再 rollback 到 `0` 并确认 fingerprint 回到 `2502b08c541495a4`。结果为 L3 / `Ready` / `unreal_texture_budget_executor_rolled_back`，7 pass / 0 warning / 0 error，1 executed operation，1 post-check pass，1 rollback pass，assetWrites=2，persistentMutation=false。

`Platform Variant Executor Expansion Receipts` 已完成 R34 闭环：读取 R30 generation operations 和 R33 rolled-back executor proof，把 LOD / Nanite / collision 后续操作转成 approval / rollback receipts。结果为 L3-derived / `Review` / `executor_receipts_linked_to_rolled_back_unreal_write`，5 receipts，2 no-op verified，1 approval-ready，2 readiness-only，0 blocked，3 owner approvals required，3 rollback receipts，productionWrites=0。

`Platform Variant StaticMesh Post-check` 已完成 R39 闭环：读取 R34 executor receipts，通过 UnrealEditor-Cmd 进入 public `.uproject`，只读采集 2 个目标 StaticMesh 的 LOD / Nanite / collision facts，并验证 5 条 receipt 的当前状态。结果为 L3 / `Review` / `unreal_staticmesh_postcheck_collected`，5 receipts，2 targets，2 target assets present，2 / 2 no-op matched，1 approval-ready，2 readiness-only，3 owner actions，32 pass，3 warning，0 error，assetWrites=0，productionWrites=0。

核心文件：

```text
dcc-hosts/animation-continuity-lab/fixtures/synthetic_animation_scene.json
dcc-hosts/animation-continuity-lab/animation_continuity_lab/contract.py
dcc-hosts/animation-continuity-lab/animation_continuity_lab/maya_collector.py
dcc-hosts/animation-continuity-lab/scripts/run_smoke.py
dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py
dcc-hosts/animation-continuity-lab/scripts/run_maya_l3.py
dcc-hosts/unreal-animation-bridge/fixtures/synthetic_unreal_animation_bridge.json
dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/contract.py
dcc-hosts/unreal-animation-bridge/scripts/run_smoke.py
dcc-hosts/unreal-animation-bridge/scripts/run_l3_smoke.py
dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py
dcc-hosts/unreal-animation-bridge/scripts/generate_maya_fbx_fixture.py
dcc-hosts/unreal-animation-bridge/scripts/unreal_python/probe_animation_runtime.py
dcc-hosts/unreal-animation-bridge/scripts/unreal_python/import_animsequence_fixture.py
dcc-hosts/character-calibration-studio/fixtures/synthetic_character_calibration_scene.json
dcc-hosts/character-calibration-studio/character_calibration_studio/contract.py
dcc-hosts/character-calibration-studio/character_calibration_studio/drilldown.py
dcc-hosts/character-calibration-studio/character_calibration_studio/maya_collector.py
dcc-hosts/character-calibration-studio/scripts/run_smoke.py
dcc-hosts/character-calibration-studio/scripts/run_drilldown.py
dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py
dcc-hosts/character-calibration-studio/scripts/run_maya_l3.py
dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/contract.py
dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/fixture_authoring.py
dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/deformation_link.py
dcc-hosts/unreal-control-rig-bridge/scripts/run_smoke.py
dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py
dcc-hosts/unreal-control-rig-bridge/scripts/run_fixture_authoring.py
dcc-hosts/unreal-control-rig-bridge/scripts/run_deformation_link.py
dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/probe_control_rig_bridge.py
dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/author_control_rig_fixture.py
dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/collect_control_rig_deformation_link.py
dcc-hosts/spatial-authoring-workbench/fixtures/synthetic_spatial_authoring_scene.json
dcc-hosts/spatial-authoring-workbench/spatial_authoring_workbench/contract.py
dcc-hosts/spatial-authoring-workbench/spatial_authoring_workbench/drilldown.py
dcc-hosts/spatial-authoring-workbench/spatial_authoring_workbench/maya_collector.py
dcc-hosts/spatial-authoring-workbench/scripts/run_smoke.py
dcc-hosts/spatial-authoring-workbench/scripts/run_drilldown.py
dcc-hosts/spatial-authoring-workbench/scripts/run_l3_smoke.py
dcc-hosts/spatial-authoring-workbench/scripts/run_maya_l3.py
dcc-hosts/unreal-socket-import-checker/unreal_socket_import_checker/contract.py
dcc-hosts/unreal-socket-import-checker/scripts/run_smoke.py
dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py
dcc-hosts/unreal-socket-import-checker/scripts/unreal_python/probe_socket_import_checker.py
dcc-hosts/platform-variant-forge/fixtures/synthetic_platform_variant_plan.json
dcc-hosts/platform-variant-forge/platform_variant_forge/contract.py
dcc-hosts/platform-variant-forge/platform_variant_forge/runtime_contract.py
dcc-hosts/platform-variant-forge/platform_variant_forge/generation_plan.py
dcc-hosts/platform-variant-forge/platform_variant_forge/texture_runtime.py
dcc-hosts/platform-variant-forge/platform_variant_forge/controlled_executor.py
dcc-hosts/platform-variant-forge/platform_variant_forge/executor_expansion.py
dcc-hosts/platform-variant-forge/platform_variant_forge/staticmesh_postcheck.py
dcc-hosts/platform-variant-forge/scripts/run_smoke.py
dcc-hosts/platform-variant-forge/scripts/run_unreal_runtime_probe.py
dcc-hosts/platform-variant-forge/scripts/run_generation_plan.py
dcc-hosts/platform-variant-forge/scripts/run_texture_runtime_probe.py
dcc-hosts/platform-variant-forge/scripts/run_texture_payload_probe.py
dcc-hosts/platform-variant-forge/scripts/run_controlled_executor.py
dcc-hosts/platform-variant-forge/scripts/run_executor_expansion.py
dcc-hosts/platform-variant-forge/scripts/run_staticmesh_postcheck.py
dcc-hosts/platform-variant-forge/scripts/unreal_python/probe_variant_runtime.py
dcc-hosts/platform-variant-forge/scripts/unreal_python/collect_texture_runtime.py
dcc-hosts/platform-variant-forge/scripts/unreal_python/execute_controlled_variant.py
dcc-hosts/platform-variant-forge/scripts/unreal_python/collect_staticmesh_postcheck.py
```

已生成首个 L2 artifact：

```text
dcc-hosts/animation-continuity-lab/artifacts/animation-continuity-contract-20260805-160346.json
```

当前 L3 artifact：

```text
dcc-hosts/animation-continuity-lab/artifacts/animation-continuity-maya-l3-20260805-162744.json
```

当前 R23 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r23-animation-continuity-l3-presentation-pack-20260805-163040.json
```

当前 Unreal Animation Bridge import L3：

```text
dcc-hosts/unreal-animation-bridge/artifacts/unreal-animation-bridge-import-l3-20260805-173309.json
```

当前 Character Calibration Maya L3：

```text
dcc-hosts/character-calibration-studio/artifacts/character-calibration-maya-l3-20260805-175057.json
```

当前 Character Calibration Drilldown：

```text
dcc-hosts/character-calibration-studio/artifacts/character-calibration-drilldown-20260805-202259.json
```

当前 Unreal Control Rig Bridge / Face Skeleton / Deformation / Compile Status：

```text
dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-fixture-authoring-20260805-230323.json
dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-face-skeleton-fixture-20260805-235115.json
dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-bridge-l3-20260805-235140.json
dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-deformation-link-20260805-235154.json
dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-compile-status-20260806-001504.json
```

当前 Spatial Authoring Maya L3：

```text
dcc-hosts/spatial-authoring-workbench/artifacts/spatial-authoring-maya-l3-20260805-181524.json
```

当前 Spatial Authoring Drilldown：

```text
dcc-hosts/spatial-authoring-workbench/artifacts/spatial-authoring-drilldown-20260805-203713.json
```

当前 Unreal Socket Import Checker：

```text
dcc-hosts/unreal-socket-import-checker/artifacts/unreal-socket-import-checker-l3-20260805-212131.json
```

上一轮 R27 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r27-spatial-authoring-l3-presentation-pack-20260805-181612.json
```

当前 Platform Variant Forge artifact：

```text
dcc-hosts/platform-variant-forge/artifacts/platform-variant-forge-contract-20260805-183315.json
```

当前 Platform Variant Unreal Runtime Probe：

```text
dcc-hosts/platform-variant-forge/artifacts/platform-variant-unreal-runtime-20260805-185026.json
```

当前 Platform Variant Generation Planner：

```text
dcc-hosts/platform-variant-forge/artifacts/platform-variant-generation-plan-20260805-190052.json
```

当前 Platform Variant Texture Runtime Collector：

```text
dcc-hosts/platform-variant-forge/artifacts/platform-variant-texture-runtime-20260805-191529.json
```

当前 Platform Variant Public Texture2D Payload Fixture：

```text
dcc-hosts/platform-variant-forge/artifacts/platform-variant-texture-payload-runtime-20260805-193515.json
```

当前 Platform Variant Controlled Executor：

```text
dcc-hosts/platform-variant-forge/artifacts/platform-variant-controlled-executor-20260805-200810.json
```

当前 Platform Variant Executor Expansion Receipts：

```text
dcc-hosts/platform-variant-forge/artifacts/platform-variant-executor-expansion-20260805-201222.json
```

当前 R48 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r48-groom-alembic-payload-presentation-pack-20260806-012304.json
```

这条线的最终效果：

- 检查动画交付中的 rig identity、skeleton fingerprint、Take range、sample rate、required channel coverage。
- 检查 sub-frame keys、channel identity collision、root motion policy、scale drift、active additive layers。
- 通过 Maya `mayapy` 生成真实 keyed animCurve runtime evidence。
- Unreal 侧已接入 import L3；Character Calibration 已有 Maya L3、R35 drilldown、R42 Unreal Control Rig Fixture Authoring、post-authoring bridge、R43 Control Rig Deformation Link、R44 Face Skeleton Fixture 和 R45 Compile Status Bridge；Groom Export Inspector 已有 Maya L3、R47 Unreal Import Readiness 和 R48 Maya Alembic Payload Receipt；Spatial Authoring 已有 Maya L3、R36 drilldown、R38 Unreal Socket Import Checker 和 R40 socket API-limited executor；Platform Variant Forge 已把 PC/Mobile 派生计划接到 Unreal preset facts、Unreal runtime-vs-plan L3、dry-run generation plan、material / texture runtime facts、public Texture2D payload、受控 Unreal execute / post-check / rollback，以及 LOD/Nanite/collision approval receipts。后续可继续补 MotionBuilder、Editor Utility/C++ diagnostic bridge、socket C++ adapter 或 Groom Alembic import/post-check。

继续开发时优先做 Groom Alembic import/post-check、gameplay attach fixture、Control Rig Editor Utility / C++ diagnostic bridge，或 Animation Blueprint Library / C++ adapter 让曲线名不再停留在 Python metadata warning。如果只验证当前 R48，运行：

```powershell
python dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py
python dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py
python dcc-hosts/unreal-animation-bridge/scripts/run_deep_facts.py
python dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py
python dcc-hosts/character-calibration-studio/scripts/run_drilldown.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_fixture_authoring.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_face_skeleton_fixture.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_deformation_link.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_compile_status.py
python dcc-hosts/groom-export-inspector/scripts/run_l3_smoke.py
python dcc-hosts/groom-export-inspector/scripts/run_unreal_readiness.py
python dcc-hosts/groom-export-inspector/scripts/run_alembic_payload.py
python dcc-hosts/spatial-authoring-workbench/scripts/run_l3_smoke.py
python dcc-hosts/spatial-authoring-workbench/scripts/run_drilldown.py
python dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py
python dcc-hosts/unreal-socket-import-checker/scripts/run_socket_authoring_executor.py
python dcc-hosts/platform-variant-forge/scripts/run_smoke.py
python dcc-hosts/platform-variant-forge/scripts/run_unreal_runtime_probe.py
python dcc-hosts/platform-variant-forge/scripts/run_generation_plan.py
python dcc-hosts/platform-variant-forge/scripts/run_texture_runtime_probe.py
python dcc-hosts/platform-variant-forge/scripts/run_texture_payload_probe.py
python dcc-hosts/platform-variant-forge/scripts/run_controlled_executor.py
python dcc-hosts/platform-variant-forge/scripts/run_executor_expansion.py
python dcc-hosts/platform-variant-forge/scripts/run_staticmesh_postcheck.py
```

当前 R48 public package 为 `ai-tool-ta-dcc-first-showcase-r48` / `dcc-first-package@1.45.0`，Presenter Pack 47 / 47 evidence files present，0 missing required files，37 demo route steps；Groom Export Inspector 已确认 Maya runtime 可回读 root UV、strand ID、guide curve、Alembic payload 和 Unreal binding intent，Groom Unreal Import Readiness 已确认 UE 5.3 runtime 可进入、AssetImportTask / AlembicImportFactory 可见、`SK_HeroFace` 存在但 GroomAsset / GroomBindingAsset API 和期望 Groom / Binding 资产仍缺失，Groom Alembic Payload Receipt 已确认 approved groom 能写出 public synthetic `.abc` cache 且 TMP groom 被 held。gate 仍为 `CapturePending`，只因为 Maya GUI media 还没采集。

## 4. 长期开发规则

每轮只闭环一个高价值业务任务。

默认验证：

```powershell
.\scripts\validate_loop.ps1 -Tier quick
```

只在对应模块变化时跑对应 runtime 档位；只有发布里程碑跑 `full`。

详细策略：

```text
docs/技术报告/260805_长期循环开发框架与轻量验证策略.md
```

## 5. 公开仓边界

公开仓应包含：

- `dcc-hosts`
- `showcases`
- `public-case-package`
- `fixtures`
- `docs`
- `scripts`
- `README.md`
- `PUBLIC_RELEASE.md`
- `PRODUCT.md`
- `DESIGN.md`

公开仓应排除：

- `lightbox提取`
- `assets` 下的大截图/录屏
- `node_modules`
- `dist`
- `.tmp`
- DCC 二进制场景和本地缓存
