# Unreal Animation Bridge

R67 目标：把 Maya Animation Continuity L3、Unreal AnimSequence runtime facts 和 gameplay attach readiness 串成同一条业务链。动画交付不是“DCC 里检查完就结束”，也不是“Unreal 里有 AnimSequence 就结束”，而是要证明 Skeleton / frame / curve / notify timing 能支撑真实玩法挂接。

## 核心业务逻辑

动画进引擎后最容易出现的错位不是文件缺失，而是语义漂移：

- Maya take 的 skeleton fingerprint 是否能绑定到 Unreal Skeleton。
- sample rate 和 frame range 是否会被 Unreal 导入或压缩时隐式改变。
- gameplay curve / required channel 是否完整进入 AnimSequence。
- gameplay attach 的 notify timing 是否可读、是否已经 authored。
- root motion mode 是否和 root translate 曲线一致。
- compression 是否允许 trim frame range 或 remove linear keys。
- 当前公开项目里是否真的有目标 AnimSequence / Skeleton fixture。

这条线的价值是把 Maya keyed animCurve facts 映射成 Unreal runtime import facts，再把 gameplay attach intent 映射到 AnimSequence notify/timing gate。工具明确区分五层状态：Maya L3 已有、L2 合约已建立、Unreal Python API 可进入、公开 AnimSequence/Skeleton fixture 已由脚本自动生成并导入、gameplay attach 只有在 socket coverage 与 animation timing 都通过后才可发布。

## 当前实现

代码入口：

- `dcc-hosts/unreal-animation-bridge/fixtures/synthetic_unreal_animation_bridge.json`
- `dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/contract.py`
- `dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/deep_facts.py`
- `dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/attach_timing.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_l3_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_deep_facts.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_attach_timing_readiness.py`
- `dcc-hosts/unreal-animation-bridge/scripts/generate_maya_fbx_fixture.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/probe_animation_runtime.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/import_animsequence_fixture.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/collect_animsequence_deep_facts.py`

已完成：

- L2 contract：读取 R23 Maya L3 artifact，把两个 Maya take 映射到 Unreal AnimSequence 预期。
- Maya FBX fixture：通过 Maya 2026 `mayapy` + `fbxmaya` 现场生成两段 public synthetic FBX，不提交二进制源文件。
- Unreal runtime import：通过 `UnrealEditor-Cmd.exe -run=pythonscript` 进入公开 test `.uproject`，用 `AssetImportTask` + `FbxImportUI` 导入并保存 synthetic Skeleton / SkeletalMesh / AnimSequence。
- Runtime facts：采集 `AnimSequence` 存在性、绑定 Skeleton、play length、可用 API 方法、导入选项、重命名路径和写入边界。
- AnimSequence deep facts：读取已导入 public AnimSequence，采集 play length、derived frame span、curve/root/compression metadata 和 notify property readability。
- Attach timing readiness：读取 R66 gameplay attach controlled readiness，把 socket executor 证据继续连接到 AnimSequence notify/timing 规则。
- Presenter Pack 接入：R67 Presenter Pack 会探测 Unreal Animation Bridge contract、import L3、deep facts 和 attach timing readiness artifact，并保持 55 步 demo route。
- public manifest 接入：当前公开包已升级到 `ai-tool-ta-dcc-first-showcase-r67` / `dcc-first-package@1.64.0`。

## 证据

当前 contract artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-contract-20260805-173354.json
```

当前 readiness artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-readiness-20260805-173401.json
```

当前 import L3 artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-import-l3-20260805-173309.json
```

当前 deep facts artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-deep-facts-20260805-224206.json
```

当前 attach timing readiness artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-attach-timing-readiness-20260806-074254.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r67-unreal-animation-attach-timing-readiness-presentation-pack-20260806-074822.json
```

关键结果：

- report version：`unreal-animation-bridge-import-l3@0.1.0`
- evidence level：L3
- l3 status：`unreal_animsequence_assets_imported`
- Unreal runtime：5.3.2 / Python 3.9.7
- API probe：`AssetImportTask`、`FbxImportUI`、`FbxSkeletalMeshImportData`、`FbxAnimSequenceImportData`、`AnimSequence`、`Skeleton`、`SkeletalMesh` 可见
- expected sequences：2
- present / missing sequences：2 / 0
- imported assets：4
- assets ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：12 / 1 / 5

Gate 为 `Blocked` 是正确状态：`RunStart` 已 Ready；`Attack_A` 作为故障样本保留了 rig fingerprint、sample rate、frame range、curve coverage、sub-frame 和 root motion 问题。R25 已证明 Unreal import runtime 能跑通，Blocked 不再代表缺 skeletal animation fixture。

## R41 AnimSequence Deep Facts

R41 不重新导入 FBX，也不保存 Unreal asset。它读取 R25 已生成的 public AnimSequence，采集：

- play length 和按 expected sample rate 推导出的 frame span。
- direct frame-rate metadata 是否能读到。
- curve metadata API 是否能暴露曲线名。
- root motion setting / compression setting 是否能通过 Unreal Python 读取。
- read-only mutation boundary。

当前结果：L3 / `Blocked` / `unreal_animsequence_deep_facts_collected`，2 runtime rows，2 / 2 duration frame spans matched，0 Ready / 1 Review / 1 Blocked，15 pass / 2 warning / 1 error，assetWrites=0。`RunStart` 进入 Review 是因为 UE Python 没有暴露 curve names；`Attack_A` 保持 Blocked 是因为 R25 source bridge row 仍有 skeleton、sample rate、curve coverage、sub-frame 和 root motion 错误。

## R67 Attach Timing Readiness

R67 读取 R66 Gameplay Attach Controlled Readiness 和 R41 AnimSequence Deep Facts，按 gameplay slot 要求明确的 timing event：

- `primaryWeapon` 需要 `equip.attach`。
- `backpack` 需要 `gear.attach`。
- 其他 attach intent 默认需要 `attach.commit`。

当前结果：L3-derived / `Blocked` / `unreal_animation_attach_timing_readiness_linked`，intentCount=2，timingReady=0，timingBlocked=1，heldBySocketOrSource=1，notifyReadableIntents=0，required/missing attach timing events=2 / 2，AnimationBlueprintLibrary=false，AnimationDataModel=true，5 pass / 1 warning / 5 error，assetWrites=0，engineWrites=0，productionWrites=0。

关键结论：R66 已经让 approved rifle equip path 因 socket executor 证据进入 Review，但 R67 证明这还不够。真正玩法挂接必须知道在哪个动画事件点 attach；当前 UE 5.3 Python 不能读取 `notifies` / `anim_notify_tracks` / `marker_data`，所以工具正确给出 Blocked gate 和 owner actions，而不是把“有 socket + 有动画资产”误判成可发布。

## 后续

下一阶段有两条可选路径：

- 继续动画线：补 Animation Notify C++ / Editor Utility bridge 或 Animation Blueprint Library adapter，让 notify timing 和 curve names 不再停留在 Python metadata warning。
- 业务扩展：继续做 Animation Blueprint Library / C++ adapter 读取 curve names，或接 R42 Control Rig fixture 做 deformation target link / compile status。
