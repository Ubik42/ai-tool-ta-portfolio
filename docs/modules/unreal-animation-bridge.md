# Unreal Animation Bridge

R25 目标：把 R23 的 Maya Animation Continuity L3 证据继续推到引擎侧，证明动画交付不是“DCC 里检查完就结束”，而是要用 Unreal 真实导入结果对齐 AnimSequence / Skeleton 语义。

## 核心业务逻辑

动画进引擎后最容易出现的错位不是文件缺失，而是语义漂移：

- Maya take 的 skeleton fingerprint 是否能绑定到 Unreal Skeleton。
- sample rate 和 frame range 是否会被 Unreal 导入或压缩时隐式改变。
- gameplay curve / required channel 是否完整进入 AnimSequence。
- root motion mode 是否和 root translate 曲线一致。
- compression 是否允许 trim frame range 或 remove linear keys。
- 当前公开项目里是否真的有目标 AnimSequence / Skeleton fixture。

R25 的价值是把 Maya keyed animCurve facts 映射成 Unreal runtime import facts，而不是只给一张流程图。工具明确区分四层状态：Maya L3 已有、L2 合约已建立、Unreal Python API 可进入、公开 AnimSequence/Skeleton fixture 已由脚本自动生成并导入。

## 当前实现

代码入口：

- `dcc-hosts/unreal-animation-bridge/fixtures/synthetic_unreal_animation_bridge.json`
- `dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/contract.py`
- `dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/deep_facts.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_l3_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_deep_facts.py`
- `dcc-hosts/unreal-animation-bridge/scripts/generate_maya_fbx_fixture.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/probe_animation_runtime.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/import_animsequence_fixture.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/collect_animsequence_deep_facts.py`

R25 已完成：

- L2 contract：读取 R23 Maya L3 artifact，把两个 Maya take 映射到 Unreal AnimSequence 预期。
- Maya FBX fixture：通过 Maya 2026 `mayapy` + `fbxmaya` 现场生成两段 public synthetic FBX，不提交二进制源文件。
- Unreal runtime import：通过 `UnrealEditor-Cmd.exe -run=pythonscript` 进入公开 test `.uproject`，用 `AssetImportTask` + `FbxImportUI` 导入并保存 synthetic Skeleton / SkeletalMesh / AnimSequence。
- Runtime facts：采集 `AnimSequence` 存在性、绑定 Skeleton、play length、可用 API 方法、导入选项、重命名路径和写入边界。
- Presenter Pack 接入：R25 Presenter Pack 会探测 Unreal Animation Bridge contract + import L3 artifact，并保持 14 步 demo route。
- public manifest 接入：当前公开包已继续升级到 `ai-tool-ta-dcc-first-showcase-r26` / `dcc-first-package@1.23.0`。

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

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r41-unreal-animation-deep-facts-presentation-pack-20260805-224616.json
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

## 后续

下一阶段有两条可选路径：

- 继续动画线：补 Animation Blueprint Library / C++ adapter 或 Control Rig curve bridge，让 curve names 不再停留在 Python metadata warning。
- 业务扩展：做 public Control Rig asset fixture / runtime hierarchy，把 skeleton fingerprint、joint coverage、topology signature 和 Control Rig mapping 串起来。
