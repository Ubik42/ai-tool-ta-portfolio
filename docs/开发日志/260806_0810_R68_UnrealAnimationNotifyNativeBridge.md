# 一.问题反馈

继续长期循环开发 AI Tool TA 作品集。R67 已证明 approved rifle equip path 不能只靠 socket executor 和 AnimSequence 存在性放行，还缺可读且已 authored 的 attach notify timing。本轮目标是把这个缺口推进成真实 UE native bridge 工程任务。

# 二.⭐回顾分析

R67 的核心事实是：UE 5.3 Python 能读取 AnimSequence 的 duration / frame span / data model 等 deep facts，但 `AnimationBlueprintLibrary` 不可用，notify properties 不可读，`equip.attach` / `gear.attach` 两个 timing event 缺失。这个问题不适合继续写说明卡片，应该落到 UE Editor 插件、commandlet 和 Editor Utility contract。

本轮沿用 SocketBridge 的三段式经验：先放入 public C++ source contract，再用 Unreal Python runtime probe 检查 class surface / plugin source / binary / commandlet readiness，最后由后续轮次编译和运行 commandlet diagnostics。

# 三.改动解释

新增 public UE Editor plugin source：

```text
dcc-hosts/unreal-handoff-inspector/projects/AI_Tool_TA_Unreal_L3/Plugins/AI_Tool_TA_AnimNotifyBridge
```

插件定义 `UAiToolTaAnimNotifyDiagnosticsCommandlet` 和 `UAiToolTaAnimNotifyBridgeLibrary::CollectAnimNotifyDiagnostics`。native library 读取 `UAnimSequenceBase::Notifies`，输出 notifyName、notify class、notify state class、trackIndex、triggerTime、endTriggerTime 和 duration。commandlet 支持从 R67 attach timing report 中提取 `animationAssetPaths`，后续可直接跑 native diagnostics。

新增 Python readiness：

```text
dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/native_notify_bridge.py
dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_bridge_readiness.py
dcc-hosts/unreal-animation-bridge/scripts/unreal_python/probe_anim_notify_native_bridge.py
```

R68 artifact：

```text
dcc-hosts/unreal-animation-bridge/artifacts/unreal-animation-notify-native-bridge-readiness-20260806-080502.json
```

结果为 L3-readiness / `Blocked` / `unreal_animation_notify_native_bridge_readiness_collected`，sourceRequiresNativeBridge=true，runtimeEntered=true，animSequenceClassesVisible=true，hasNativeSource=true，hasAnimNotifyBridgePlugin=true，missingRequiredNativeFiles=0，hasCompiledBridgeBinary=false，commandletVisible=false，8 pass / 0 warning / 2 error，assetWrites=0，engineWrites=0，productionWrites=0。

同步更新 Maya Presenter Pack API、`validate_loop.ps1`、public package manifests、公开包说明、证据索引、验证台账、AI handoff、README 和 Unreal Animation Bridge 模块文档。R68 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r68-unreal-animation-notify-native-bridge-presentation-pack-20260806-080752.json
```

Presenter Pack 结果为 66/66 evidence present，0 missing required files，56 demo route steps，gate 仍为 `CapturePending`。

# 四.计划&状态

R68 已完成代码、artifact、manifest、Presenter Pack 和文档接入。当前公开包为 `ai-tool-ta-dcc-first-showcase-r68` / `dcc-first-package@1.65.0`。

下一轮优先入口：编译 `AI_Tool_TA_AnimNotifyBridge`，加载 `UAiToolTaAnimNotifyDiagnosticsCommandlet`，对 R67 referenced public AnimSequence 跑 native diagnostics。如果编译链路受阻，再转 Control Rig native diagnostic bridge 或 MotionBuilder adapter。Maya GUI 9 张截图和 1 段录屏继续留到最后集中采集。
