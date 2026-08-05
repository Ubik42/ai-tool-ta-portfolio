# AI 接手说明

## 1. 最终展示效果

目标不是网页作品集，而是 DCC / 引擎内展示的工具管线 TA 能力。

最终 reviewer 应看到：

- Maya 2024 内通过 AuroraView 打开工具面板。
- 面板里有资产协议、规则矩阵、视觉评审、贴图交付、任务编排、资产放行、引擎预检、场景事务保护、动画连续性、角色校准、空间作者、平台变体规划、Unreal runtime 对照、generation planner、texture runtime collector 和 public Texture2D payload fixture 等模块。
- 每个模块能导出 JSON artifact，说明业务事实、规则判定、fix preview、owner 边界和写入边界。
- 非 Maya 证据已经覆盖 Blender `bpy` L3、3ds Max `pymxs` L3、Unreal Python L3++；动画线已有 Maya `mayapy` L3 keyed animCurve 证据和 Unreal Animation Bridge import L3；角色线已有 Character Calibration Maya L3；空间作者线已有 Spatial Authoring Maya L3；平台变体线已有连接 Unreal preset facts 的 `L3-linked` planning artifact、Unreal runtime-vs-plan L3 artifact、runtime drift -> generation plan artifact、Unreal material / texture runtime artifact 和 public Texture2D payload L3 artifact。
- Presenter Pack 把所有关键证据汇总成 reviewer 可读的发布包。

当前稳定展示包：

```text
public-case-package/DCC_FIRST_PACKAGE.md
public-case-package/dcc-first-package-manifest.json
dcc-hosts/maya-auroraview-host/artifacts/r32-platform-variant-texture-payload-presentation-pack-20260805-194432.json
```

## 2. 当前完成度

稳定基线：R32。

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
- Character Calibration Studio Maya L3
- Spatial Authoring Workbench Maya L3
- Platform Variant Forge L3-linked
- Platform Variant Unreal Runtime Probe L3
- Platform Variant Generation Planner L3-derived
- Platform Variant Texture Runtime Collector L3
- Platform Variant Public Texture2D Payload Fixture L3
- Blender Rule Adapter L3
- 3ds Max Rule Adapter L3
- Maya command bridge
- 轻量验证脚本 `scripts/validate_loop.ps1`

仍缺：

- Maya GUI 9 张 PNG 和 1 段 MP4，留到最后人工采集。
- MotionBuilder、Houdini、Unreal animation fact deepening、Character Calibration / Spatial Authoring UI drilldown、Platform Variant controlled executor 等后续工具线。

## 3. R32 当前断点与已完成工具线

`Animation Continuity Lab` 已完成首轮闭环：L2 contract smoke、Maya `mayapy` L3 keyed animCurve collector、Presenter Pack 接入、public manifest 接入和模块文档。

`Unreal Animation Bridge` 已完成 import L3 闭环：读取 R23 Maya L3 artifact，生成 public Maya FBX clips，通过 UnrealEditor-Cmd 进入公开 test `.uproject`，导入并采集 Skeleton / SkeletalMesh / AnimSequence runtime facts。

`Character Calibration Studio` 已完成 Maya L3 闭环：生成 public synthetic character mesh / joint DAG / calibration attrs，采集 topology signature、joint coverage、skin influence budget、calibration delta、face params、Control Rig mapping 和 mirror pair coverage。

`Spatial Authoring Workbench` 已完成 Maya L3 闭环：生成 public synthetic joints / locator attrs，采集 socket parent joint、offset、mirror pair、hotspot semantic/owner、pose frame、local space、preview locator 和 pose transfer approval。

`Platform Variant Forge` 已完成 R28 首版闭环：读取 public-safe PC/Mobile variant fixture，连接已有 Unreal preset fact comparison L3++ artifact，检查 target path、owner approval、triangle/texture/material/draw budget、LOD coverage、Nanite、shader feature、collision policy，输出 `L3-linked` planning artifact。本轮没有新增 Unreal 写入，定位是平台派生计划和门禁证据。

`Platform Variant Unreal Runtime Probe` 已完成 R29 runtime-vs-plan 闭环：通过 UnrealEditor-Cmd 进入公开 test `.uproject`，采集计划中 PC/Mobile target StaticMesh 的 path、LOD、material slot、Nanite、collision runtime facts，并与 R28 variant plan 对照。结果为 L3，3 variants，0 Ready / 2 Review / 1 Blocked，21 pass / 4 warning / 2 error；写入只发生在 `/Game/AI_Tool_TA` 公开 fixture。

`Platform Variant Generation Planner` 已完成 R30 dry-run generation 闭环：读取 R29 runtime drift 与 R28 plan，生成 missing LOD、Nanite policy、material merge、texture downscale、collision simplification、source import、target variant creation 等 11 个 operation contract，结果为 1 Ready / 3 Review / 2 Blocked / 5 Satisfied。该 artifact 不写 Unreal 资产，只给出 deterministic params、Unreal Python preview、writeSet、rollback 和 owner approval 边界。

`Platform Variant Texture Runtime Collector` 已完成 R31 material / texture runtime 闭环：通过 UnrealEditor-Cmd 进入公开 test `.uproject`，采集计划中 StaticMesh 的 material slots、material dependency query、material expression texture references、Texture2D 尺寸/估算内存/压缩/sRGB/readability。结果为 L3，3 variants，1 Ready / 1 Review / 1 Blocked，19 pass / 1 warning / 1 error；assetWrites=0。Mobile HeroPanel 的 Review 明确来自 synthetic material 没有真实 Texture2D payload，不是 collector 缺失。

`Platform Variant Public Texture2D Payload Fixture` 已完成 R32 public payload 闭环：通过 UnrealEditor-Cmd 进入公开 test `.uproject`，生成 public 2048 PNG，导入为 `/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor`，挂到 `M_HeroPanel`，再采集 StaticMesh -> material -> Texture2D facts。结果为 L3，3 variants，2 Ready / 0 Review / 1 Blocked，20 pass / 0 warning / 1 error；最终提交的幂等 rerun 为 assetWrites=0，写入边界仍只限 `/Game/AI_Tool_TA` public fixture。HeroPanel Mobile 已经从缺 payload 的 Review 进入 Ready，剩余 Blocked 是故意保留的 vehicle 缺源资产样本。

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
dcc-hosts/character-calibration-studio/character_calibration_studio/maya_collector.py
dcc-hosts/character-calibration-studio/scripts/run_smoke.py
dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py
dcc-hosts/character-calibration-studio/scripts/run_maya_l3.py
dcc-hosts/spatial-authoring-workbench/fixtures/synthetic_spatial_authoring_scene.json
dcc-hosts/spatial-authoring-workbench/spatial_authoring_workbench/contract.py
dcc-hosts/spatial-authoring-workbench/spatial_authoring_workbench/maya_collector.py
dcc-hosts/spatial-authoring-workbench/scripts/run_smoke.py
dcc-hosts/spatial-authoring-workbench/scripts/run_l3_smoke.py
dcc-hosts/spatial-authoring-workbench/scripts/run_maya_l3.py
dcc-hosts/platform-variant-forge/fixtures/synthetic_platform_variant_plan.json
dcc-hosts/platform-variant-forge/platform_variant_forge/contract.py
dcc-hosts/platform-variant-forge/platform_variant_forge/runtime_contract.py
dcc-hosts/platform-variant-forge/platform_variant_forge/generation_plan.py
dcc-hosts/platform-variant-forge/platform_variant_forge/texture_runtime.py
dcc-hosts/platform-variant-forge/scripts/run_smoke.py
dcc-hosts/platform-variant-forge/scripts/run_unreal_runtime_probe.py
dcc-hosts/platform-variant-forge/scripts/run_generation_plan.py
dcc-hosts/platform-variant-forge/scripts/run_texture_runtime_probe.py
dcc-hosts/platform-variant-forge/scripts/run_texture_payload_probe.py
dcc-hosts/platform-variant-forge/scripts/unreal_python/probe_variant_runtime.py
dcc-hosts/platform-variant-forge/scripts/unreal_python/collect_texture_runtime.py
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

当前 R26 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r26-character-calibration-l3-presentation-pack-20260805-175238.json
```

当前 Spatial Authoring Maya L3：

```text
dcc-hosts/spatial-authoring-workbench/artifacts/spatial-authoring-maya-l3-20260805-181524.json
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

当前 R32 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r32-platform-variant-texture-payload-presentation-pack-20260805-194432.json
```

这条线的最终效果：

- 检查动画交付中的 rig identity、skeleton fingerprint、Take range、sample rate、required channel coverage。
- 检查 sub-frame keys、channel identity collision、root motion policy、scale drift、active additive layers。
- 通过 Maya `mayapy` 生成真实 keyed animCurve runtime evidence。
- Unreal 侧已接入 import L3；Spatial Authoring 已有 Maya L3；Platform Variant Forge 已把 PC/Mobile 派生计划接到 Unreal preset facts、Unreal runtime-vs-plan L3、dry-run generation plan、material / texture runtime facts 和 public Texture2D payload。后续可继续补 MotionBuilder、Unreal socket 对照、受控 Unreal executor 或更细的 Unreal curve/compression facts。

继续开发时优先做 Platform Variant controlled executor，或深化 Character Calibration / Spatial Authoring UI drilldown。如果只验证当前 R32，运行：

```powershell
python dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py
python dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py
python dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py
python dcc-hosts/spatial-authoring-workbench/scripts/run_l3_smoke.py
python dcc-hosts/platform-variant-forge/scripts/run_smoke.py
python dcc-hosts/platform-variant-forge/scripts/run_unreal_runtime_probe.py
python dcc-hosts/platform-variant-forge/scripts/run_generation_plan.py
python dcc-hosts/platform-variant-forge/scripts/run_texture_runtime_probe.py
python dcc-hosts/platform-variant-forge/scripts/run_texture_payload_probe.py
```

当前 R32 public package 为 `ai-tool-ta-dcc-first-showcase-r32` / `dcc-first-package@1.29.0`，Presenter Pack 29 / 29 evidence files present，0 missing required files，21 demo route steps；Spatial Authoring 已到 `L3` / `maya_spatial_authoring_collected`，Platform Variant Forge 已到 `L3-linked` / `platform_variant_plan_joined_to_unreal_facts`，Platform Variant Unreal Runtime Probe 已到 `L3` / `unreal_variant_runtime_assets_collected`，Platform Variant Generation Planner 已到 `L3-derived` / `runtime_drift_to_generation_plan`，Platform Variant Texture Runtime Collector 已到 `L3` / `unreal_material_texture_facts_collected`，Platform Variant Public Texture2D Payload Fixture 已到 `L3` / `unreal_texture_payload_fixture_collected`。gate 仍为 `CapturePending`，只因为 Maya GUI media 还没采集。

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
