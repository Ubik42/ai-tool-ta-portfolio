# 一.问题反馈

继续长期循环开发，不在仅剩手动 GUI 采集前停下。本轮接 R71：native AnimNotify commandlet 已能读取 public AnimSequence，并确认 `equip.attach` / `gear.attach` 缺失；下一步必须证明工具能在引擎内受控写入、复查和回滚，而不是只停在诊断报告。

# 二.⭐回顾分析

R67 attach timing readiness 提供两条业务意图：`AS_Hero_RunStart` 需要 `equip.attach`，`AS_Hero_Attack_A` 需要 `gear.attach`。R71 的 native diagnostics 已证明 commandlet 能读到 2/2 public AnimSequence，但 notifyRows=0，业务 gate 正确 Blocked。

R72 的关键点是把 Lightbox 式检查从“发现问题/给 owner action”推进到“受控执行/可复查/可回滚”。实现上只允许 `/Game/AI_Tool_TA/...` public fixture 路径，写入必须同时带 `-Apply -Rollback -AllowPublicFixtureWrite`，commandlet 保存后立即 post-check，再删除 created notifies 并保存回滚；Python harness 额外备份并恢复目标 `.uasset` hash。

# 三.改动解释

扩展 `AI_Tool_TA_AnimNotifyBridge` commandlet：默认保持 R71 read-only diagnostics；当 input 含 `requests` 且命令行带 apply/rollback/public fixture 授权时，使用 `UAnimSequenceBase::Notifies` 写入 named native notify，设置 trigger time、track index 和 receipt metadata，保存、post-check、rollback，并输出 `ai-tool-ta-anim-notify-authoring-result@0.1.0`。

新增 `dcc-hosts/unreal-animation-bridge/scripts/run_anim_notify_native_controlled_write.py`：读取 R67 attach timing readiness 和最新 AnimNotify bridge build artifact，生成 controlled-write input receipt，复制 public Unreal project 到 `D:\cs\_test`，安装 packaged plugin，运行 `AiToolTaAnimNotifyDiagnostics -Apply -Rollback -AllowPublicFixtureWrite`，并记录 pre/final uasset hash。

新增证据：

- `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-bridge-build-20260806-090905.json`
- `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-controlled-write-20260806-090946.json`
- `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-native-notify-controlled-write-receipts\unreal-animation-notify-native-controlled-write-input-20260806-090946.json`
- `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-native-notify-controlled-write-receipts\unreal-animation-notify-native-controlled-write-output-20260806-090946.json`
- `<repo>\dcc-hosts\maya-auroraview-host\artifacts\r72-unreal-animation-notify-native-controlled-write-presentation-pack-20260806-091404.json`

同步更新 Maya Presenter Pack API、`validate_loop.ps1`、public package manifests、README、Evidence/Validation ledger、Unreal Animation Bridge 模块文档、handoff 和技术报告。R72 public package 为 `ai-tool-ta-dcc-first-showcase-r72` / `dcc-first-package@1.69.0`，Presenter Pack 为 70/70 evidence files present，0 missing required files，60 demo route steps。

# 四.计划&状态

当前状态：R72 L3-runtime-controlled-write 完成，UnrealEditor-Cmd returnCode=0，commandletLoaded=true，outputStatus=`apply_postcheck_rollback_completed`，requestCount=2，applied=2，postCheckPresent=2，rollbackRemoved=2，postRollbackPresent=0，assetWrites=4，engineWrites=0，productionWrites=0，persistentMutation=false，finalHashRestored=true。

下一轮最短入口：把 R72 controlled write 结果接回 gameplay attach readiness，让 `primaryWeapon` 这类 approved intent 从 timing Blocked 进入 executor-backed Review/Ready 判断；或推进 Control Rig native diagnostic bridge / MotionBuilder adapter。Maya GUI screenshots 和 route recording 继续留到最后集中采集。
