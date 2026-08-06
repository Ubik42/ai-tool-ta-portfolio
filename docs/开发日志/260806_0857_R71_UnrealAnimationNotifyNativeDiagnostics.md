# 一.问题反馈

继续长期循环开发，不在仅剩手动 GUI 采集前停下。本轮接 R70：native AnimNotify commandlet 已能加载，但还没有把 R67 referenced AnimSequence paths 喂给 commandlet 做真实 notify/timing 诊断。

# 二.⭐回顾分析

R67 attach timing readiness 已有两个 public fixture 动画路径：`/Game/AI_Tool_TA/Animations/AS_Hero_RunStart` 和 `/Game/AI_Tool_TA/Animations/AS_Hero_Attack_A`，分别要求 `equip.attach` 和 `gear.attach`。

R70 packaged `AI_Tool_TA_AnimNotifyBridge` 的 commandlet 已支持 `-Input=<json>`，会递归读取 `animationAssetPaths`，加载 `UAnimSequence`，通过 native C++ 读取 `UAnimSequence::Notifies`，输出 notifyName / class / track / triggerTime / duration rows。这正好补上 UE Python 读不到 protected notify properties 的业务缺口。

本轮实际运行结果：UnrealEditor-Cmd 返回 0，commandletLoaded=true，outputStatus=`diagnostics_completed`，2/2 public AnimSequence 加载成功，notifyRows=0，missingAttachTimingEvents=2，productionWrites=0。结论是 runtime 链路已通，Blocked 是业务资产缺少 `equip.attach` / `gear.attach` notify，不是工具失败。

# 三.改动解释

新增 `dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_diagnostics.py`：读取 R67 attach timing artifact 和 R69 build artifact，生成 diagnostics input receipt，创建 `D:\cs\_test\ai_tool_ta_anim_notify_diagnostics` 临时 Unreal project，启用 packaged plugin，执行 `AiToolTaAnimNotifyDiagnostics`，解析 output receipt 并输出 L3-runtime-diagnostics artifact。

新增证据：

- `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-diagnostics-20260806-085035.json`
- `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-native-notify-diagnostics-receipts\unreal-animation-notify-native-diagnostics-input-20260806-085035.json`
- `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-native-notify-diagnostics-receipts\unreal-animation-notify-native-diagnostics-output-20260806-085035.json`
- `<repo>\dcc-hosts\maya-auroraview-host\artifacts\r71-unreal-animation-notify-native-diagnostics-presentation-pack-20260806-085351.json`

同步更新 Maya Presenter Pack API、`validate_loop.ps1`、public package manifests、README、Evidence/Validation ledger、Unreal Animation Bridge 模块文档、handoff 和技术报告。R71 public package 为 `ai-tool-ta-dcc-first-showcase-r71` / `dcc-first-package@1.68.0`，Presenter Pack 为 69/69 evidence files present，0 missing required files，59 demo route steps。

# 四.计划&状态

当前状态：R71 runtime diagnostics 完成，整体 gate 仍为 `CapturePending`，原因是 Maya GUI screenshots/recording 尚未采集；动画 timing 业务 gate 为 `Blocked`，原因是 public fixture AnimSequence 没有 authored attach notify。

下一轮最短入口：做受控 public fixture notify authoring / post-check / rollback，把 `equip.attach` 和 `gear.attach` 写入临时 public Unreal fixture，确认 native diagnostics 从 missing -> matched，并恢复 uasset hash 或明确记录受控 public fixture 写入边界。手动 Maya GUI 采集继续留到最后。
