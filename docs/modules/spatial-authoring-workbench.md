# Spatial Authoring & Pose Transfer Workbench

R27-R36 目标：把 Lightbox 高价值线里的 socket / hotspot / locator preview / pose frame / mirror transfer，从“规则设想”推进到 Maya runtime L3 证据，并进一步生成 Maya/AuroraView 可消费的 drilldown 数据。

## 核心业务逻辑

空间作者工具的价值不是画几个 locator，而是把“引擎可相信的挂点事实”提前锁在 DCC：

- socket 是否挂在真实 runtime joint 上。
- local offset 是否在容差内，避免把 world-space 误当 local-space 导出。
- 左右 socket 是否成对、对称、互相声明 mirror。
- hotspot 是否有稳定语义和 owner，避免 VFX / gameplay 接口靠口头约定。
- pose frame 是否唯一、在帧域内、可作为 pose transfer 的源和目标。
- preview locator 是否存在，reviewer 能否在 DCC 内直接看见问题。
- pose transfer 是否有 required pair、local-space 边界和 owner approval。

## 当前实现

代码入口：

- `dcc-hosts/spatial-authoring-workbench/fixtures/synthetic_spatial_authoring_scene.json`
- `dcc-hosts/spatial-authoring-workbench/spatial_authoring_workbench/contract.py`
- `dcc-hosts/spatial-authoring-workbench/spatial_authoring_workbench/maya_collector.py`
- `dcc-hosts/spatial-authoring-workbench/spatial_authoring_workbench/drilldown.py`
- `dcc-hosts/spatial-authoring-workbench/scripts/run_smoke.py`
- `dcc-hosts/spatial-authoring-workbench/scripts/run_l3_smoke.py`
- `dcc-hosts/spatial-authoring-workbench/scripts/run_maya_l3.py`
- `dcc-hosts/spatial-authoring-workbench/scripts/run_drilldown.py`

R27 完成项：

- L2 contract：2 个 public-safe spatial authoring rows，1 Ready，1 intentionally Blocked。
- Maya L3：Maya `mayapy` 创建 synthetic joints / locators / custom attrs，再从 Maya 场景采集 joint DAG、locator transform、socket/hotspot/pose frame payload。
- 规则检查：协议载体、父 joint、socket offset、mirror symmetry、hotspot semantic/owner、pose frame coverage/range、scale、space、preview locator、pose transfer boundary。
- Presenter Pack 接入：R27 Presenter Pack 探测 Spatial Authoring Maya L3 artifact，并把 demo route 扩到 16 步。

R36 完成项：

- Drilldown projection：读取 Spatial Authoring Maya L3 artifact，把 flat rule rows 转成 protocol、parent joint、sockets、mirror、hotspots、pose frames、transforms、preview locators、pose transfer 9 类面板。
- Owner action：把 7 个 owner-required 动作和 2 个 manual-review 动作拆出来，明确 technical-animation-owner、gameplay-vfx-owner、animation-owner 和 reviewer 边界。
- Presenter Pack 接入：R36 Presenter Pack 探测 Spatial Authoring Drilldown artifact，并把 demo route 扩到 25 步。

## 证据

当前 L2 contract artifact：

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-contract-20260805-181516.json
```

当前 Maya L3 artifact：

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-maya-l3-20260805-181524.json
```

当前 Spatial Authoring Drilldown artifact：

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-drilldown-20260805-203713.json
```

关键结果以最新 manifest 为准：

- report version：`spatial-authoring-maya-l3@0.1.0`
- evidence level：L3
- l3 status：`maya_spatial_authoring_collected`
- assets ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：11 / 2 / 7
- drilldown evidence / L3 status：L3-derived / `maya_spatial_authoring_rows_to_drilldown`
- drilldown assets / panels：2 / 18
- drilldown owner actions / owner required / manual review：9 / 7 / 2

Gate 为 `Blocked` 是正确状态：`Rifle Socket Authoring Approved` Ready；`Backpack Socket Temporary Blocked` 保留 missing joints、world-space socket、large offset、missing mirror pair、bad hotspot owner/semantic、duplicate/out-of-range pose frame、missing preview locator 和 unapproved pose transfer 等业务故障。

## 后续

下一阶段可以继续做：

- Unreal socket import checker：把 Maya socket facts 对照到 Unreal Skeleton / StaticMesh sockets。
- Pose transfer repair preview：生成只读修复计划，区分可自动 mirror 的 locator 和必须 owner 确认的 transfer。
