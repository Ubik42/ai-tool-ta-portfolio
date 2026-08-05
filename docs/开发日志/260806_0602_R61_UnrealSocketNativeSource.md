# 一.问题反馈

R60 把 Unreal socket 写入缺口定位到 native bridge：UE Python 可见 socket/editor utility API，但不能安全写 `SkeletalMeshSocket.socket_name` / `bone_name`，public project 又缺 `AI_Tool_TA_SocketBridge` source/plugin/binary/commandlet。

本轮目标是先补 public Unreal plugin 源码骨架，把“没有 native 工程面”的缺口推进成“源码 contract 已存在，等待构建加载和 receipt executor”。

# 二.⭐回顾分析

Socket / hotspot / gameplay attach 是空间作者线的高价值业务点。核心不是创建一个 socket，而是把 Maya authoring facts、Unreal Skeleton runtime facts、写入边界、post-check 和 rollback receipt 串起来。R40 的 API-limited 结论必须被尊重，R61 不能绕回 Python 反射写 identity。

因此本轮选择 disabled-by-default Editor plugin source：既让 reviewer 看到真实 C++ commandlet / BlueprintFunctionLibrary contract，又不让未编译模块破坏当前 Unreal headless runtime smoke。

# 三.改动解释

新增 public Unreal project 下的 `AI_Tool_TA_SocketBridge` plugin source package：`.uplugin`、`Build.cs`、module skeleton、`UAiToolTaSocketAuthoringCommandlet` 和 `UAiToolTaSocketBridgeLibrary`。Library 暴露 dry-run / apply 形态的 Skeleton socket write path，Commandlet 暴露 `-Input` / `-Output` / `-Apply` contract，并在 public skeleton 中把 apply mode 保持为未完成的安全边界。

修复 `native_bridge.py` 的 required file path 比较，统一正反斜杠归一化。复跑 readiness 后，`hasNativeSource=true`、`hasSocketBridgePlugin=true`、`missingRequiredNativeFiles=0`；由于没有 compiled binary 和 loaded commandlet，gate 仍正确为 `Blocked`。

# 四.计划&状态

当前 R61 artifact：`dcc-hosts/unreal-socket-import-checker/artifacts/unreal-socket-native-bridge-readiness-20260806-055738.json`。结果为 L3-readiness / `Blocked` / `unreal_socket_native_bridge_readiness_collected`，sourceApiLimited=true，expectedSockets=2，createdSocketsViaPython=0，socketClassesVisible=true，editorUtilitySurfaceVisible=true，hasNativeSource=true，hasSocketBridgePlugin=true，hasCompiledBridgeBinary=false，commandletVisible=false，missingRequiredNativeFiles=0，7 pass / 0 warning / 2 error，assetWrites=0，productionWrites=0。

当前 R61 Presenter Pack：`dcc-hosts/maya-auroraview-host/artifacts/r61-unreal-socket-native-source-presentation-pack-20260806-060018.json`，59 / 59 evidence files present，0 missing required files，49 demo route steps。下一步若继续 socket 线，应构建 Editor module、让 commandlet runtime-visible，并补 JSON receipt parsing、socket write post-check 和 rollback receipt；否则转 MotionBuilder、Control Rig diagnostic bridge 或 Animation Blueprint Library / C++ adapter。
