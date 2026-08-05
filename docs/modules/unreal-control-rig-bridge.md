# Unreal Control Rig Bridge

R37 目标：把 Maya Character Calibration 的 Control Rig mapping facts 接到 Unreal runtime readiness，证明角色校准不是停在 DCC 源文件检查，而是能继续进入引擎资产门禁。

## 核心业务逻辑

角色工具链里最容易被低估的坑是“DCC 里映射看起来对，引擎里没有可用的 Control Rig 资产或骨架绑定”。这个模块把问题拆成四层：

- Maya 源头 drilldown 是否 Ready。
- Unreal Python 和 Control Rig / RigVM API 是否可用。
- expected SkeletalMesh / Skeleton 是否存在并能作为绑定目标。
- expected Control Rig asset 是否存在，runtime controls 是否覆盖 Maya required controls。

## 当前实现

代码入口：

- `dcc-hosts/unreal-control-rig-bridge/unreal_control_rig_bridge/contract.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/run_smoke.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py`
- `dcc-hosts/unreal-control-rig-bridge/scripts/unreal_python/probe_control_rig_bridge.py`
- `dcc-hosts/unreal-handoff-inspector/projects/AI_Tool_TA_Unreal_L3/AI_Tool_TA_Unreal_L3.uproject`

R37 已完成：

- 读取 `character-calibration-drilldown-20260805-202259.json` 和对应 Maya L3 source facts。
- 在 Unreal 5.3.2 public `.uproject` 内启用并探测 ControlRig plugin / API。
- 对照 `/Game/AI_Tool_TA/Characters/SK_Hero`、`SK_Hero_Skeleton`、`CR_HeroFace` 以及 TMP 对照路径。
- 输出 source mapping、runtime binding、missing CR asset、runtime control coverage、deformation target coverage 的 evaluation rows。
- 输出 owner actions，owner 分配到 `character-owner`、`control-rig-owner`、`engine-ta`，所有 action 都是 `preview_only`。

## 证据

当前 L3 artifact：

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-205656.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r37-unreal-control-rig-bridge-presentation-pack-20260805-205922.json
```

关键结果：

- report version：`unreal-control-rig-bridge@0.1.0`
- evidence level：L3
- l3 status：`unreal_control_rig_bridge_facts_collected`
- gate：`Blocked`
- Unreal runtime：5.3.2 / Python 3.9.7
- Control Rig API ready：true
- character rows：2
- ready / review / blocked：0 / 0 / 2
- checks pass / warning / error：8 / 1 / 7
- skeletal bindings / Control Rig assets：1 / 0
- assetWrites / productionWrites：0 / 0

Gate 为 `Blocked` 是业务正确结果：approved 角色的 Maya mapping 和 Unreal SkeletalMesh/Skeleton binding 都通过，但 public test project 里还没有 `CR_HeroFace`；TMP 角色继续被 Maya 源头缺陷、缺 SkeletalMesh/Skeleton、缺 Control Rig asset 和 runtime control coverage 阻断。

## 后续

下一步可以生成或导入 public `CR_HeroFace` fixture，再做 runtime control hierarchy、deformation target link、Control Rig compile status 和 owner waiver 检查；也可以并行开发 Spatial Authoring 的 Unreal socket 对照，把挂点/pose transfer 的 Maya drilldown 接到引擎 Skeleton / socket facts。
