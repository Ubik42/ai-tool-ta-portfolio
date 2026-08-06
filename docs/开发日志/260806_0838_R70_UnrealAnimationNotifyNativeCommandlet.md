# 一.问题反馈

R69 已证明 `AI_Tool_TA_AnimNotifyBridge` 能通过 RunUAT `BuildPlugin` 编译，但还没有证明 packaged plugin 能在 Unreal runtime 中加载 commandlet。长期开发不能停在“已编译”，本轮继续推进到 commandlet visibility proof。

# 二.⭐回顾分析

R67 暴露的是玩法挂接的动画时机缺口：socket executor 让 rifle equip path 可审核，但 AnimSequence notify/timing 仍不可读。R68 把缺口落成 public C++ commandlet / library source，R69 证明源码可编译。按照 socket 线 R62-R63 的路径，下一层应该是把 packaged plugin 装进临时 Unreal project 并执行 readiness-only commandlet，而不是直接宣称 native diagnostics 已完成。

# 三.改动解释

新增 `dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_commandlet_probe.py`。脚本读取 R69 build artifact，定位 packaged `AI_Tool_TA_AnimNotifyBridge`，复制 public Unreal project 到 `D:\cs\_test\ai_tool_ta_anim_notify_commandlet_probe`，启用插件并执行：

```text
UnrealEditor-Cmd <temp.uproject> -run=AiToolTaAnimNotifyDiagnostics -Output=<receipt>
```

R70 commandlet artifact：

```text
dcc-hosts/unreal-animation-bridge/artifacts/unreal-animation-notify-native-commandlet-probe-20260806-083144.json
```

结果为 L3-runtime / `Ready` / `unreal_animation_notify_native_commandlet_loaded`：returnCode=0，commandletLoaded=true，readinessInvocation=true，outputStatus=`readiness_invocation_only`，requestedAnimSequencePaths=0，errorLines=0，tempProjectWrites=70，assetWrites=0，engineWrites=0，productionWrites=0。

同步更新 Maya Presenter Pack API、`validate_loop.ps1`、public package manifests、公开包说明、证据索引、验证台账、AI handoff、README、Unreal Animation Bridge 模块文档和两份技术报告。R70 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r70-unreal-animation-notify-native-commandlet-presentation-pack-20260806-083529.json
```

Presenter Pack 结果为 68/68 evidence present，0 missing required files，58 demo route steps，gate 仍为 `CapturePending`。

# 四.计划&状态

R70 已完成代码、artifact、manifest、Presenter Pack 和文档接入。当前公开包为 `ai-tool-ta-dcc-first-showcase-r70` / `dcc-first-package@1.67.0`。

下一轮入口：把 R67 referenced AnimSequence paths 输入 `UAiToolTaAnimNotifyDiagnosticsCommandlet`，生成真实 notify rows，再把结果回连到 `equip.attach` / `gear.attach` owner actions。Maya GUI 截图和录屏继续留到最后集中采集。
