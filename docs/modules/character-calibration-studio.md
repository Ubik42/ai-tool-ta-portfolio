# Character Calibration & Intent Transfer Studio

R26-R43 目标：把角色 DNA / 拓扑 / joint coverage / face control / Control Rig mapping 这条高价值角色业务线从计划推进到 Maya runtime L3 证据、Maya/AuroraView drilldown 数据，并接到 Unreal Control Rig runtime readiness、public fixture authoring 与 deformation target link。

## 核心业务逻辑

角色资产最危险的问题不是“文件能不能导出”，而是下游角色系统是否还能相信它：

- mesh topology signature 是否和 approved head topology 一致。
- required deformation / face joints 是否完整。
- TMP joint 是否泄漏到 runtime。
- skin influence 是否超过平台预算。
- wrap / sculpt calibration delta 是否超过 DNA / expression transfer 容差。
- face parameters 是否缺失或越界。
- Control Rig controls 是否映射到正确 joint，而不是临时目标。

## 当前实现

代码入口：

- `dcc-hosts/character-calibration-studio/fixtures/synthetic_character_calibration_scene.json`
- `dcc-hosts/character-calibration-studio/character_calibration_studio/contract.py`
- `dcc-hosts/character-calibration-studio/character_calibration_studio/maya_collector.py`
- `dcc-hosts/character-calibration-studio/character_calibration_studio/drilldown.py`
- `dcc-hosts/character-calibration-studio/scripts/run_smoke.py`
- `dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py`
- `dcc-hosts/character-calibration-studio/scripts/run_maya_l3.py`
- `dcc-hosts/character-calibration-studio/scripts/run_drilldown.py`

R26 已完成：

- L2 contract：2 个 public-safe character rows，1 Ready，1 intentionally Blocked。
- Maya L3：Maya 2026 `mayapy` 创建 synthetic mesh / joint DAG / custom attrs，再从 Maya 场景采集真实 topology counts、joint names 和 calibration payload。
- Presenter Pack 接入：R26 Presenter Pack 探测 Character Calibration Maya L3 artifact，并把 demo route 扩到 15 步。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r26` / `dcc-first-package@1.23.0`。

R35 已完成：

- 读取 Maya L3 artifact，把 flat evaluation rows 投影成 topology / skeleton / skin / calibration / face / Control Rig / mirror panels。
- 输出 asset selector、default blocked asset、owner action rows、fix preview、mutation boundary 和 productionWrites=0。
- 结果为 2 character drilldowns，14 panels，8 issue rows，8 owner actions，6 owner_required，2 manual_review。
- Presenter Pack 接入：R35 Presenter Pack 探测 Character Calibration Drilldown artifact，并把 demo route 扩到 24 步。

R37 已完成：

- 读取 R35 Character Calibration Drilldown artifact，把 Maya source mapping facts 对照到 Unreal 5.3.2 Control Rig API、SkeletalMesh / Skeleton binding 和 expected Control Rig asset paths。
- 通过 UnrealEditor-Cmd 进入 public test `.uproject`，收集 ControlRig / RigVM / SkeletalMesh / Skeleton / Asset Registry API 可用性。
- 结果为 L3 / `Blocked` / `unreal_control_rig_bridge_facts_collected`；2 character rows，0 Ready，0 Review，2 Blocked，8 pass，1 warning，7 error。
- approved 角色行已经找到 `/Game/AI_Tool_TA/Characters/SK_Hero` 和 Skeleton 绑定，但缺 `/Game/AI_Tool_TA/Characters/CR_HeroFace`；TMP 行同时被 Maya 源头缺陷、缺 SkeletalMesh/Skeleton 和缺 CR asset 阻断。
- 该桥接层只读 public Unreal fixture，assetWrites=0，productionWrites=0。

R42 已完成：

- 新增 Unreal Control Rig Fixture Authoring harness，只选择 approved 角色行进入 public fixture authoring，TMP 行 held。
- 通过 Unreal 5.3.2 Python 创建 `/Game/AI_Tool_TA/Characters/CR_HeroFace`，写入 5 个 required controls，并保持 productionWrites=0。
- 复跑 Unreal Control Rig Bridge 后，approved 行变为 Ready；TMP 行继续 Blocked，整体 gate 保持 Blocked。

R43 已完成：

- 新增 Unreal Control Rig Deformation Link read-only collector，读取 `CR_HeroFace`、`SK_Hero_Skeleton` 和 Maya `controlRigMappings`。
- 输出 control -> deformation target -> Unreal Skeleton target 的链接事实，同时采集 Control Rig hierarchy shape/offset readability 和 compile API surface。
- 结果为 L3 / `Blocked` / `unreal_control_rig_deformation_link_collected`；10 control links，5 runtime controls，5 shape/offset-readable controls，2 Skeleton target matches，0 direct compile-status rows，assetWrites=0。
- 业务结论：approved 行的 CR asset / controls 已经存在，但 public Skeleton 没有确认 `Eye_L`、`Eye_R`、`Jaw`，不能把“控件存在”包装成“角色绑定可交付”。

## 证据

当前 L2 contract artifact：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-contract-20260805-175045.json
```

当前 Maya L3 artifact：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json
```

当前 Drilldown artifact：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-drilldown-20260805-202259.json
```

当前 Unreal Control Rig artifacts：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-fixture-authoring-20260805-230323.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-230343.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-232729.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r43-unreal-control-rig-deformation-link-presentation-pack-20260805-233308.json
```

关键结果：

- report version：`character-calibration-maya-l3@0.1.0`
- evidence level：L3
- l3 status：`maya_character_calibration_collected`
- Maya runtime：2026
- assets ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：10 / 2 / 6
- drilldown assets / panels：2 / 14
- owner actions / owner required / manual review：8 / 6 / 2
- Unreal Control Rig Bridge：L3 / `Blocked` / `unreal_control_rig_bridge_facts_collected`
- Unreal Control Rig Fixture Authoring：L3 / `Ready` / `unreal_control_rig_fixture_authoring_collected`
- Unreal engine：5.3.2
- Control Rig API ready：true
- Unreal fixture operations / held：1 / 1
- Unreal fixture controls required / runtime / missing：5 / 5 / 0
- Unreal bridge ready / review / blocked：1 / 0 / 1
- Unreal bridge pass / warning / error：10 / 1 / 5
- Unreal bridge skeletal bindings / Control Rig assets：1 / 1
- Unreal bridge assetWrites / productionWrites：0 / 0
- Unreal Control Rig Deformation Link：L3 / `Blocked` / `unreal_control_rig_deformation_link_collected`
- Unreal deformation link controls / runtime / Skeleton matches：10 / 5 / 2
- Unreal deformation link shape-or-offset readable / direct compile status：5 / 0
- Unreal deformation link pass / warning / error：12 / 2 / 6
- Unreal deformation link assetWrites / productionWrites：0 / 0

Gate 为 `Blocked` 是正确状态：`Hero Head Approved` Ready；`Hero Head Temporary Sculpt` 保留 topology mismatch、missing Eye_R/Jaw、TMP joint、skin influence overflow、calibration delta overflow、face param missing/out-of-range、Control Rig mapping mismatch 等业务故障。

## 后续

下一阶段可以继续做：

- Control Rig compile bridge：用 Editor Utility / C++ 补 direct compile status，并导入 public face skeleton fixture 或 owner waiver。
- Character LOD Bake Planner：把 topology / normal / tangent / vertex color payload 接到角色 LOD 生成链。
