# Unreal Animation Bridge

R73 目标：把 Maya Animation Continuity L3、Unreal AnimSequence runtime facts、gameplay attach readiness、native notify diagnostics、native controlled write 和 gameplay attach timing controlled readiness 串成同一条业务链。动画交付不是“DCC 里检查完就结束”，也不是“Unreal 里有 AnimSequence 就结束”，而是要证明 Skeleton / frame / curve / notify timing 能支撑真实玩法挂接，并且能在引擎内受控写入、复查、回滚，再合成玩法交付门禁。

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
- `dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/native_notify_bridge.py`
- `dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/gameplay_timing_controlled.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_l3_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_deep_facts.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_attach_timing_readiness.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_bridge_readiness.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_bridge_build.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_commandlet_probe.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_diagnostics.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_controlled_write.py`
- `dcc-hosts/unreal-animation-bridge/scripts/run_gameplay_attach_timing_controlled_readiness.py`
- `dcc-hosts/unreal-animation-bridge/scripts/generate_maya_fbx_fixture.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/probe_animation_runtime.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/import_animsequence_fixture.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/collect_animsequence_deep_facts.py`
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/probe_anim_notify_native_bridge.py`
- `dcc-hosts/unreal-handoff-inspector/projects/AI_Tool_TA_Unreal_L3/Plugins/AI_Tool_TA_AnimNotifyBridge`

已完成：

- L2 contract：读取 R23 Maya L3 artifact，把两个 Maya take 映射到 Unreal AnimSequence 预期。
- Maya FBX fixture：通过 Maya 2026 `mayapy` + `fbxmaya` 现场生成两段 public synthetic FBX，不提交二进制源文件。
- Unreal runtime import：通过 `UnrealEditor-Cmd.exe -run=pythonscript` 进入公开 test `.uproject`，用 `AssetImportTask` + `FbxImportUI` 导入并保存 synthetic Skeleton / SkeletalMesh / AnimSequence。
- Runtime facts：采集 `AnimSequence` 存在性、绑定 Skeleton、play length、可用 API 方法、导入选项、重命名路径和写入边界。
- AnimSequence deep facts：读取已导入 public AnimSequence，采集 play length、derived frame span、curve/root/compression metadata 和 notify property readability。
- Attach timing readiness：读取 R66 gameplay attach controlled readiness，把 socket executor 证据继续连接到 AnimSequence notify/timing 规则。
- Native notify bridge readiness：读取 R67 attach timing readiness，通过 Unreal 5.3 headless probe 确认 AnimSequence/AnimNotify runtime 类和 public C++ source contract，把 notify timing 缺口推进到 native commandlet / Editor Utility build gate。
- Native notify bridge build：通过 RunUAT BuildPlugin 编译 `AI_Tool_TA_AnimNotifyBridge`，记录 DLL hash、compilerVersion、errorLines 和 no-write boundary。
- Native notify commandlet probe：把 R69 packaged plugin 复制到临时 Unreal project，执行 `-run=AiToolTaAnimNotifyDiagnostics`，记录 commandletLoaded、readiness output receipt 和 no-write boundary。
- Native notify diagnostics：读取 R67 animationAssetPaths，喂给 packaged commandlet，加载 2/2 public AnimSequence，输出 native notify rows，并把缺失的 `equip.attach` / `gear.attach` 保持为业务 Blocked。
- Native notify controlled write：在临时 Unreal project 中把 `equip.attach` 和 `gear.attach` 写入 public AnimSequence，保存后 post-check，再 rollback 并恢复 `.uasset` hash。
- Gameplay attach timing controlled readiness：合并 R66 socket executor、R67 timing gate 和 R72 notify controlled write，输出玩法挂接是否已经 socket + notify 双 executor-backed。
- Presenter Pack 接入：R73 Presenter Pack 会探测 Unreal Animation Bridge contract、import L3、deep facts、attach timing readiness、native notify bridge readiness、native build artifact、commandlet probe artifact、native diagnostics artifact、native controlled write artifact 和 gameplay attach timing controlled readiness artifact，并保持 61 步 demo route。
- public manifest 接入：当前公开包已升级到 `ai-tool-ta-dcc-first-showcase-r73` / `dcc-first-package@1.70.0`。

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

当前 native notify bridge readiness artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-bridge-readiness-20260806-080502.json
```

当前 native notify bridge build artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-bridge-build-20260806-090905.json
```

当前 native notify commandlet probe artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-commandlet-probe-20260806-083144.json
```

当前 native notify diagnostics artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-diagnostics-20260806-085035.json
```

当前 native notify controlled write artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-controlled-write-20260806-090946.json
```

当前 gameplay attach timing controlled readiness artifact：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-gameplay-attach-timing-controlled-readiness-20260806-092934.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r73-unreal-gameplay-attach-timing-controlled-readiness-presentation-pack-20260806-093254.json
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

## R68 Native Notify Bridge Readiness

R68 把 R67 的缺口继续推进一层：不是继续说“Python 读不到 notify”，而是在 public Unreal project 里加入 `AI_Tool_TA_AnimNotifyBridge` Editor plugin source，定义两个入口：

- `UAiToolTaAnimNotifyDiagnosticsCommandlet`
- `UAiToolTaAnimNotifyBridgeLibrary::CollectAnimNotifyDiagnostics`

native library 读取 `UAnimSequenceBase::Notifies`，输出 notifyName、notify class、notify state class、trackIndex、triggerTime、endTriggerTime 和 duration。readiness probe 通过 UnrealEditor-Cmd 进入 public `.uproject`，检查 runtime class surface、source file completeness、plugin source、binary 和 commandlet visibility。

当前结果：L3-readiness / `Blocked` / `unreal_animation_notify_native_bridge_readiness_collected`，sourceRequiresNativeBridge=true，runtimeEntered=true，AnimSequence/AnimNotify runtime classes visible=true，hasNativeSource=true，hasAnimNotifyBridgePlugin=true，missingRequiredNativeFiles=0，hasCompiledBridgeBinary=false，commandletVisible=false，8 pass / 0 warning / 2 error，assetWrites=0，engineWrites=0，productionWrites=0。

关键结论：R67 的 2 个 missing attach timing events 已经变成明确的 engine-native 诊断桥任务。R68 之后的推进顺序是 BuildPlugin、加载 commandlet、对 public AnimSequence 跑 diagnostics，再决定是否需要受控 authored notify 写入。

## R69 Native Notify Bridge Build

R69 通过 Unreal Automation Tool `BuildPlugin` 编译 public `AI_Tool_TA_AnimNotifyBridge` Editor plugin，输出目录在 `D:\cs\_test\ai_tool_ta_anim_notify_builds`，不提交编译产物，只提交 JSON 证据。

当前结果：L3-build / `Ready` / `unreal_animation_notify_native_bridge_plugin_built`，runUATFound=true，msvcFound=true，returnCode=0，compiledDlls=1，errorLines=0，compilerVersion=14.38.33130，configRestored=true，DLL bytes=195584，sha256=`1f42afb1a87dae5baa2dae759adb521b96ffde233449a999aaaeea19d67be459`，assetWrites=0，engineWrites=0，productionWrites=0。

关键结论：native notify bridge 已从 source/readiness 进入 compiled proof。

## R70 Native Notify Commandlet Probe

R70 使用 R69 packaged plugin，在 `D:\cs\_test\ai_tool_ta_anim_notify_commandlet_probe` 创建临时 Unreal project，启用 `AI_Tool_TA_AnimNotifyBridge`，执行 `UnrealEditor-Cmd -run=AiToolTaAnimNotifyDiagnostics -Output=<receipt>`，不读取业务 AnimSequence，只做 readiness-only invocation。

当前结果：L3-runtime / `Ready` / `unreal_animation_notify_native_commandlet_loaded`，returnCode=0，commandletLoaded=true，readinessInvocation=true，outputStatus=`readiness_invocation_only`，requestedAnimSequencePaths=0，errorLines=0，tempProjectWrites=70，assetWrites=0，engineWrites=0，productionWrites=0。

关键结论：native notify bridge 不只“能编译”，已经能被 Unreal runtime 加载为 commandlet。下一步可以把 R67 referenced AnimSequence paths 输入 commandlet，产出真实 notify rows，再回连到 `equip.attach` / `gear.attach` owner actions。

## R71 Native Notify Diagnostics

R71 使用 R70 已验证可见的 commandlet，把 R67 attach timing readiness 中的两条 `animationAssetPaths` 写成 input receipt，再在临时 Unreal project 中执行 `UnrealEditor-Cmd -run=AiToolTaAnimNotifyDiagnostics -Input=<receipt> -Output=<receipt>`。

当前结果：L3-runtime-diagnostics / `Blocked` / `unreal_animation_notify_native_diagnostics_collected_with_timing_gaps`，returnCode=0，commandletLoaded=true，diagnosticsCompleted=true，outputStatus=`diagnostics_completed`，requestedAnimSequencePaths=2，loadedSequences=2，notifyRows=0，required/missing attach timing events=2 / 2，timingReady=0，timingBlocked=2，errorLines=0，tempProjectWrites=70，assetWrites=0，engineWrites=0，productionWrites=0。

关键结论：native 诊断链路已经从“能加载 commandlet”推进到“能读取具体 public AnimSequence”。当前 Blocked 不是工具链失败，而是业务资产真的没有 `equip.attach` / `gear.attach` notify；R72 已把这个缺口推进到受控 public fixture notify authoring、post-check 和 rollback。

## R72 Native Notify Controlled Write

R72 在 R71 commandlet 上加入受控写入模式。`run_anim_notify_native_controlled_write.py` 从 R67 attach timing readiness 生成两条请求：`AS_Hero_RunStart` 在 0.35s 写入 `equip.attach`，`AS_Hero_Attack_A` 在 0.48s 写入 `gear.attach`。脚本把 public Unreal project 复制到 `D:\cs\_test`，安装 R72 packaged plugin，只允许 `/Game/AI_Tool_TA/...` 路径，并要求 `-Apply -Rollback -AllowPublicFixtureWrite` 才会修改 public fixture。

当前结果：L3-runtime-controlled-write / `Ready` / `unreal_animation_notify_native_controlled_write_rolled_back`，returnCode=0，commandletLoaded=true，outputStatus=`apply_postcheck_rollback_completed`，requestCount=2，loadedSequences=2，applied=2，postCheckPresent=2，rollbackRemoved=2，postRollbackPresent=0，assetWrites=4，engineWrites=0，productionWrites=0，persistentMutation=false，finalHashRestored=true。

关键结论：动画 notify 线已经从问题诊断推进到真实引擎内 guarded authoring。工具不仅能指出 `equip.attach` / `gear.attach` 缺失，还能在临时 public fixture 中写入、保存、复查、回滚并恢复 `.uasset` hash。

## R73 Gameplay Attach Timing Controlled Readiness

R73 不重复启动 Unreal，而是读取 R66 gameplay attach controlled readiness、R67 attach timing readiness 和 R72 native notify controlled write，生成 `unreal-gameplay-attach-timing-controlled-readiness@0.1.0`。它回答的是最终业务问题：一个挂接意图是否同时有受控 socket coverage 和受控 AnimSequence notify timing coverage。

当前结果：L3-derived / `Review` / `unreal_gameplay_attach_timing_controlled_readiness_linked`，notifyControlledWriteReady=true，timingReadyByControlledWrite=1，heldBySocketOrSource=1，timingBlocked=0，required/covered attach timing events=2 / 2，missingAttachTimingEventsAfterControlledWrite=0，productionWrites=0，persistentMutation=false，finalHashRestored=true。

关键结论：approved rifle equip path 已经由 socket executor 和 notify executor 双证据支撑，进入可审核状态；backpack 仍然因为 source owner temporary / source deep facts 保持 held。这比单独展示 socket 或 notify 更接近真实 Lightbox 管线的发布门禁。

## 后续

下一阶段有两条高价值路径：

- 继续动画线：做 MotionBuilder adapter，把同一批 take / event / slot intent 接到 DCC 动画源。
- 业务扩展：补 Control Rig native diagnostic bridge，读取编译诊断和 control metadata，或做更复杂的引擎内 runtime post-check。
