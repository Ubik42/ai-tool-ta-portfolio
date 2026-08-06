# 一.问题反馈

继续长期循环开发，不在仅剩手动 GUI 采集前停下。本轮接 R72：native AnimNotify 已能在 Unreal temp public fixture 中写入、post-check、rollback 并恢复 `.uasset` hash，但 socket executor、animation timing gate 和 notify controlled write 仍是分散证据，还没有合成一个玩法挂接交付门禁。

# 二.⭐回顾分析

Lightbox 高价值点不是单个 API 调通，而是把 DCC intent、引擎 runtime facts、受控写入收据、owner 状态和发布门禁合成可审核结论。R66 已证明 approved rifle equip 的 socket 可以由 native executor 创建并回滚；R67 证明 socket 通过后仍需要 AnimSequence attach timing；R72 证明 `equip.attach` / `gear.attach` 可以由 native commandlet 写入并回滚。

R73 的业务判断：approved rifle equip 同时具备 socket executor 和 notify executor 证据，可以从 timing Blocked 推进到 executor-backed Review；temporary backpack 虽然 notify 可写，但 source owner 仍是 temporary，必须继续 held。

# 三.改动解释

新增 `unreal_animation_bridge.gameplay_timing_controlled` 和 `scripts/run_gameplay_attach_timing_controlled_readiness.py`。脚本读取 R66 gameplay attach controlled readiness、R67 attach timing readiness、R72 native notify controlled write，输出 `unreal-gameplay-attach-timing-controlled-readiness@0.1.0`，不重新启动 Unreal，不产生新引擎写入。

新增证据：

- `<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-gameplay-attach-timing-controlled-readiness-20260806-092934.json`
- `<repo>\dcc-hosts\maya-auroraview-host\artifacts\r73-unreal-gameplay-attach-timing-controlled-readiness-presentation-pack-20260806-093254.json`

同步更新 Maya Presenter Pack API、`validate_loop.ps1`、public package manifests、README、Evidence/Validation ledger、Unreal Animation Bridge 模块文档、handoff 和技术报告。R73 public package 为 `ai-tool-ta-dcc-first-showcase-r73` / `dcc-first-package@1.70.0`，Presenter Pack 为 71/71 evidence files present，0 missing required files，61 demo route steps。

# 四.计划&状态

当前状态：R73 L3-derived readiness 完成，gate=`Review`，fullFixtureGate=`Blocked`，notifyControlledWriteReady=true，timingReadyByControlledWrite=1，heldBySocketOrSource=1，timingBlocked=0，required/covered attach timing events=2 / 2，missingAttachTimingEventsAfterControlledWrite=0，productionWrites=0，persistentMutation=false，finalHashRestored=true。

下一轮最短入口：推进 Control Rig native diagnostic bridge 或 MotionBuilder adapter。Maya GUI screenshots 和 route recording 继续留到最后集中采集。
