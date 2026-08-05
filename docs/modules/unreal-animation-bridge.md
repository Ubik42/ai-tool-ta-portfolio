# Unreal Animation Bridge

R24 目标：把 R23 的 Maya Animation Continuity L3 证据继续推到引擎侧，证明动画交付不是“DCC 里检查完就结束”，而是要对齐 Unreal AnimSequence / Skeleton 的导入语义。

## 核心业务逻辑

动画进引擎后最容易出现的错位不是文件缺失，而是语义漂移：

- Maya take 的 skeleton fingerprint 是否能绑定到 Unreal Skeleton。
- sample rate 和 frame range 是否会被 Unreal 导入或压缩时隐式改变。
- gameplay curve / required channel 是否完整进入 AnimSequence。
- root motion mode 是否和 root translate 曲线一致。
- compression 是否允许 trim frame range 或 remove linear keys。
- 当前公开项目里是否真的有目标 AnimSequence / Skeleton fixture。

R24 的价值是把 Maya keyed animCurve facts 映射成 Unreal runtime readiness，而不是只给一张流程图。工具明确区分三层状态：Maya L3 已有、Unreal Python API 已探测、公开 AnimSequence/Skeleton fixture 仍缺。

## 当前实现

代码入口：

- `dcc-hosts/unreal-animation-bridge/fixtures/synthetic_unreal_animation_bridge.json`
- `dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/contract.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_l3_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/probe_animation_runtime.py`

R24 已完成：

- L2 contract：读取 R23 Maya L3 artifact，把两个 Maya take 映射到 Unreal AnimSequence 预期。
- Unreal runtime readiness：通过 `UnrealEditor-Cmd.exe -run=pythonscript` 进入公开 test `.uproject`，探测 Unreal animation API 和目标资产存在性。
- Presenter Pack 接入：R24 Presenter Pack 会探测 Unreal Animation Bridge readiness artifact，并把 demo route 扩到 14 步。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r24` / `dcc-first-package@1.21.0`。

## 证据

当前 contract artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-contract-20260805-164637.json
```

当前 readiness artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-readiness-20260805-164730.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r24-unreal-animation-bridge-presentation-pack-20260805-164953.json
```

关键结果：

- report version：`unreal-animation-bridge-readiness@0.1.0`
- evidence level：L3-readiness
- l3 status：`unreal_animation_api_probe_collected`
- Unreal runtime：5.3.2 / Python 3.9.7
- API probe：`AnimSequence`、`AnimSequenceFactory`、`Skeleton`、`SkeletalMesh` 可见；`AnimationBlueprintLibrary` 在当前运行时不可见
- expected sequences：2
- present / missing sequences：0 / 2
- assets ready / review / blocked：0 / 1 / 1
- checks pass / warning / error：8 / 3 / 5

Gate 为 `Blocked` 是正确状态：公开 Unreal 项目目前只有 StaticMesh fixture，没有提交 skeletal animation fixture。R24 不把 API readiness 冒充成真实 AnimSequence L3 成功。

## 后续

下一阶段有两条可选路径：

- 轻量路径：继续做 Unreal Animation Bridge L3 asset fixture，准备 public Skeleton / AnimSequence 测试资产，再采集真实 sequence length、sample rate、curve names、root motion 和 compression facts。
- 业务扩展路径：转 Character Calibration & Intent Transfer Studio，把 skeleton fingerprint、joint coverage、topology signature 和 Control Rig mapping 串起来。
