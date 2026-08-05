# Unreal Control Rig Bridge

R37-R45 目标：把 Maya Character Calibration 的 Control Rig mapping facts 接到 Unreal runtime readiness，并继续推进到 public Control Rig fixture authoring、face Skeleton fixture、hierarchy coverage、deformation target link 和 compile invocation readiness，证明角色校准不是停在 DCC 源文件检查，而是能继续进入引擎资产门禁。

## 核心业务逻辑

角色工具链里最容易被低估的坑是“DCC 里映射看起来对，引擎里没有可用的 Control Rig 资产或骨架绑定”。这个模块把问题拆成四层：

- Maya 源头 drilldown 是否 Ready。
- Unreal Python 和 Control Rig / RigVM API 是否可用。
- expected SkeletalMesh / Skeleton 是否存在并能作为绑定目标。
- expected Control Rig asset 是否存在，runtime controls 是否覆盖 Maya required controls。
- authored controls 是否能链接到 Unreal Skeleton deformation targets，compile 方法是否能调用，以及 direct status / diagnostics 是否能被稳定读取。

## 当前实现

代码入口：

- `dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/contract.py`
- `dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/fixture_authoring.py`
- `dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/face_skeleton_fixture.py`
- `dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/deformation_link.py`
- `dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/compile_status.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/run_smoke.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/run_fixture_authoring.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/run_face_skeleton_fixture.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/run_deformation_link.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/run_compile_status.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/generate_face_skeleton_fbx.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/probe_control_rig_bridge.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/author_control_rig_fixture.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/import_face_skeleton_fixture.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/collect_control_rig_deformation_link.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/collect_control_rig_compile_status.py`
- `dcc-hosts/unreal-handoff-inspector/projects/AI_Tool_TA_Unreal_L3/AI_Tool_TA_Unreal_L3.uproject`

R37 已完成：

- 读取 `character-calibration-drilldown-20260805-202259.json` 和对应 Maya L3 source facts。
- 在 Unreal 5.3.2 public `.uproject` 内启用并探测 ControlRig plugin / API。
- 对照 `/Game/AI_Tool_TA/Characters/SK_Hero`、`SK_Hero_Skeleton`、`CR_HeroFace` 以及 TMP 对照路径。
- 输出 source mapping、runtime binding、missing CR asset、runtime control coverage、deformation target coverage 的 evaluation rows。
- 输出 owner actions，owner 分配到 `character-owner`、`control-rig-owner`、`engine-ta`，所有 action 都是 `preview_only`。

R42 已完成：

- 读取 R37 bridge artifact，只选择 approved public 角色行进入 controlled fixture authoring，TMP 行 held / no mutation。
- 通过 Unreal 5.3.2 `ControlRigBlueprintFactory` / `AssetTools` 创建 `/Game/AI_Tool_TA/Characters/CR_HeroFace`。
- 通过 `RigHierarchyController.add_control` 写入 `CTRL_brow_L`、`CTRL_brow_R`、`CTRL_eye_L`、`CTRL_eye_R`、`CTRL_jaw`。
- 保存 1 个 public fixture asset；`.uasset` 受 `.gitignore` 排除，仓库交付 deterministic authoring harness + JSON receipt。
- 复跑 bridge 后 approved 行变成 Ready，TMP 行继续被源头缺陷和 Unreal 目标缺失阻断。

R43 已完成：

- 新增 read-only Deformation Link collector，读取 post-authoring bridge artifact 和 fixture authoring artifact。
- 通过 Unreal 5.3.2 Python 读取 `CR_HeroFace` hierarchy controls、shape/offset facts、`SK_Hero_Skeleton` reference pose bone names 和 ControlRigBlueprint VM / compile API surface。
- 把 Maya `controlRigMappings` 里的 `CTRL_* -> joint` 映射投影到 Unreal runtime controls 与 Skeleton target match。
- 输出直接 compile status API-limited 的 warning，不把 `recompile_vm` 等方法存在伪装成 compile success。
- 结果揭示：`CR_HeroFace` 已有 5 个 runtime controls 和 5 个 shape/offset-readable controls，但 Skeleton 只确认 `Head` target；`Eye_L`、`Eye_R`、`Jaw` 未在 public Skeleton 中匹配，approved 行继续 Blocked。

R44 已完成：

- 新增 Face Skeleton Fixture：Maya 2026 `mayapy` 生成 public `SK_HeroFace_SkeletonFixture.fbx`，Unreal 5.3.2 导入为 `/Game/AI_Tool_TA/Characters/SK_HeroFace` 和 `SK_HeroFace_Skeleton`。
- Face Skeleton artifact 确认 required targets `Head`、`Jaw`、`Eye_L`、`Eye_R` 为 4 / 4 present，R43 缺的 `Eye_L`、`Eye_R`、`Jaw` 为 3 / 3 resolved，assetWrites=2，productionWrites=0。
- `expected_unreal_targets()` 的 approved 行切到 `SK_HeroFace` / `SK_HeroFace_Skeleton`，复跑 bridge 后 approved 行保持 Ready，TMP 行继续 Blocked。
- 复跑 Deformation Link 后 Skeleton target matches 从 2 提升到 5，approved 行从 Blocked 推进到 Review；剩余 Review 来自 direct compile status 仍无法通过 UE Python 稳定读取。

R45 已完成：

- 新增 Compile Status Bridge：读取 R44 post-face deformation-link artifact，通过 Unreal 5.3.2 Python 加载 public `CR_HeroFace`。
- 调用可见的 `ControlRigBlueprint` compile 方法，记录 compile method visible / invocation attempted / invocation succeeded，补上 package dirty before/after 和 no-save 边界。
- 结果证明 approved 行 compile 方法可见、可调用且不会留下 dirty package；但 UE Python 仍没有 direct status / diagnostic readback，所以 approved 行保持 Review，不包装成完全 Ready。

## 证据

当前 L3 artifacts：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-fixture-authoring-20260805-230323.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-face-skeleton-fixture-20260805-235115.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-235140.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-235154.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-compile-status-20260806-001504.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r46-groom-export-inspector-presentation-pack-20260806-004101.json
```

关键结果：

- fixture authoring report version：`unreal-control-rig-fixture-authoring@0.1.0`
- fixture gate：`Ready`
- fixture operations / held：1 / 1
- fixture created / saved assets：1 / 1
- fixture hierarchy readable rows：1
- fixture required / runtime / missing controls：5 / 5 / 0
- fixture assetWrites / productionWrites：1 / 0
- report version：`unreal-control-rig-bridge@0.1.0`
- evidence level：L3
- l3 status：`unreal_control_rig_bridge_facts_collected`
- gate：`Blocked`
- Unreal runtime：5.3.2 / Python 3.9.7
- Control Rig API ready：true
- character rows：2
- ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：10 / 1 / 5
- skeletal bindings / Control Rig assets：1 / 1
- assetWrites / productionWrites：0 / 0
- face Skeleton fixture report version：`unreal-control-rig-face-skeleton-fixture@0.1.0`
- face Skeleton fixture evidence：L3 / `unreal_control_rig_face_skeleton_fixture_imported`
- face Skeleton fixture gate：`Review`
- face Skeleton required targets / matches：4 / 4
- previous missing targets / resolved：3 / 3
- face Skeleton assetWrites / productionWrites：2 / 0
- deformation link report version：`unreal-control-rig-deformation-link@0.1.0`
- deformation link evidence：L3 / `unreal_control_rig_deformation_link_collected`
- deformation link gate：`Blocked`
- deformation link character rows：2
- deformation link rows ready / review / blocked：0 / 1 / 1
- deformation link controls / runtime controls / Skeleton matches：10 / 5 / 5
- shape-or-offset readable controls：5
- direct compile status rows：0
- deformation link checks pass / warning / error：13 / 2 / 5
- deformation link assetWrites / productionWrites：0 / 0
- compile status report version：`unreal-control-rig-compile-status@0.1.0`
- compile status evidence：L3 / `unreal_control_rig_compile_status_collected`
- compile status gate：`Blocked`
- compile status rows ready / review / blocked：0 / 1 / 1
- compile candidate / method visible / invoked / succeeded：1 / 1 / 1 / 1
- direct status / diagnostics / compile settings readable：0 / 0 / 1
- package dirtyAfter rows：0
- compile status checks pass / warning / error：10 / 2 / 4
- compile status assetWrites / productionWrites：0 / 0

Gate 仍为 `Blocked` 是业务正确结果：approved 角色的 Maya mapping、`SK_HeroFace_Skeleton` target coverage、`CR_HeroFace` asset、5 个 runtime controls 和 transient compile invocation 已经通过，approved 行只剩 direct diagnostic/status readback Review；TMP 角色继续被 Maya 源头缺陷、缺 SkeletalMesh/Skeleton、缺 Control Rig asset 和 runtime control coverage 阻断。

## 后续

下一步可以继续做 Control Rig compile status 的 Editor Utility / C++ bridge、owner waiver drilldown，或并行深化 Spatial Authoring 的 gameplay attach fixture。
