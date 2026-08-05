# Character Calibration & Intent Transfer Studio

R26 目标：把角色 DNA / 拓扑 / joint coverage / face control / Control Rig mapping 这条高价值角色业务线从计划推进到 Maya runtime L3 证据。

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
- `dcc-hosts/character-calibration-studio/scripts/run_smoke.py`
- `dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py`
- `dcc-hosts/character-calibration-studio/scripts/run_maya_l3.py`

R26 已完成：

- L2 contract：2 个 public-safe character rows，1 Ready，1 intentionally Blocked。
- Maya L3：Maya 2026 `mayapy` 创建 synthetic mesh / joint DAG / custom attrs，再从 Maya 场景采集真实 topology counts、joint names 和 calibration payload。
- Presenter Pack 接入：R26 Presenter Pack 探测 Character Calibration Maya L3 artifact，并把 demo route 扩到 15 步。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r26` / `dcc-first-package@1.23.0`。

## 证据

当前 L2 contract artifact：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-contract-20260805-175045.json
```

当前 Maya L3 artifact：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r26-character-calibration-l3-presentation-pack-20260805-175238.json
```

关键结果：

- report version：`character-calibration-maya-l3@0.1.0`
- evidence level：L3
- l3 status：`maya_character_calibration_collected`
- Maya runtime：2026
- assets ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：10 / 2 / 6

Gate 为 `Blocked` 是正确状态：`Hero Head Approved` Ready；`Hero Head Temporary Sculpt` 保留 topology mismatch、missing Eye_R/Jaw、TMP joint、skin influence overflow、calibration delta overflow、face param missing/out-of-range、Control Rig mapping mismatch 等业务故障。

## 后续

下一阶段可以继续做：

- Character Calibration UI drilldown：在 Maya/AuroraView 中展示 topology/joint/control mapping 差异。
- Unreal Control Rig bridge：把 Maya mapping facts 对照到 Unreal Control Rig / Skeleton 资产。
- Character LOD Bake Planner：把 topology / normal / tangent / vertex color payload 接到角色 LOD 生成链。
