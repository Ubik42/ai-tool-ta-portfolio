# 一.问题反馈

继续长期循环开发 AI Tool TA 作品集。当前目标是基于 Lightbox 高价值业务逻辑继续做 DCC / 引擎内可展示工具，不在前端说明层停留。

R66 已经把 Unreal native controlled socket write 接到 gameplay attach readiness，但这只能说明 socket executor 证据足够让 approved rifle equip path 进入 review；真实玩法挂接还需要动画事件点，不能把“有 socket + 有 AnimSequence”误判为可发布。

# 二.⭐回顾分析

本轮读取 R66 gameplay attach controlled readiness 和 Unreal AnimSequence Deep Facts。R66 里 `rifle-primary-equip` 已由 controlled executor 证据进入 `ReadyByControlledExecutor`，`backpack-temp-equip` 仍是 source held。AnimSequence deep facts 证明 public AnimSequence 资产存在、duration/frame-span 可读，但 UE 5.3 Python 下 `notifies` 是 protected，`anim_notify_tracks` / `marker_data` 不存在，当前不能读取 notify event names。

业务结论：socket readiness 是装备挂接的空间门禁，AnimSequence notify/timing 是玩法触发门禁。两者必须同时成立。当前 attach timing gate 正确为 `Blocked`，不是工具失败。

# 三.改动解释

新增 `unreal_animation_bridge.attach_timing` 和 `scripts/run_attach_timing_readiness.py`，把 R66 gameplay readiness 与 AnimSequence deep facts join 成 `unreal-animation-attach-timing-readiness@0.1.0` artifact。规则按 slot role 要求 timing event：`primaryWeapon` 需要 `equip.attach`，`backpack` 需要 `gear.attach`，其他默认 `attach.commit`。

新增 artifact：

```text
dcc-hosts/unreal-animation-bridge/artifacts/unreal-animation-attach-timing-readiness-20260806-074254.json
```

结果为 L3-derived / `Blocked` / `unreal_animation_attach_timing_readiness_linked`，intentCount=2，timingReady=0，timingBlocked=1，heldBySocketOrSource=1，notifyReadableIntents=0，missingAttachTimingEvents=2，assetWrites=0，engineWrites=0，productionWrites=0。

同步更新 Maya Presenter Pack API、`validate_loop.ps1`、public package manifests、公开包说明、证据索引、验证台账、AI handoff、Unreal Animation Bridge 模块文档和两份技术报告。R67 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r67-unreal-animation-attach-timing-readiness-presentation-pack-20260806-074822.json
```

Presenter Pack 结果为 65/65 evidence present，0 missing required files，55 demo route steps，gate 仍为 `CapturePending`。

# 四.计划&状态

R67 已完成代码、artifact、manifest、Presenter Pack 和文档接入。当前公开包为 `ai-tool-ta-dcc-first-showcase-r67` / `dcc-first-package@1.64.0`。

下一轮优先入口：做 Animation Notify C++ / Editor Utility bridge，解决 UE 5.3 Python 下 AnimSequence notify 不可读的问题；备选是 MotionBuilder adapter 或 Control Rig Editor Utility / C++ diagnostic bridge。Maya GUI 9 张截图和 1 段录屏继续留到最后集中采集。
