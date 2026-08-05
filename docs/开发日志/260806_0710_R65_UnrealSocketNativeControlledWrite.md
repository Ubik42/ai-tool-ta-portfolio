# 一.问题反馈

本轮继续 socket native bridge 线。R64 已证明 commandlet 能解析 approved JSON receipt、加载 public Skeleton 并输出 wouldCreate dry-run rows，但还没有证明它能真正创建 socket、保存、post-check、rollback，并留下可审计的写入边界。

# 二.⭐回顾分析

高价值业务点是 guarded execution：工具管线 TA 不能只做“建议修复”或“看起来可以写”，必须把 apply guard、public fixture scope、post-check、rollback、write counter、hash restore 做成同一条执行证据。这里对应 Lightbox 高价值插件里的核心经验：真实生产工具要把写入边界和回滚证据显式暴露给 reviewer。

# 三.改动解释

- 扩展 `AiToolTaSocketAuthoringCommandlet.cpp`：`-Apply` 必须同时带 `-Rollback` 和 `-AllowPublicFixtureWrite`，且目标 Skeleton 必须在 `/Game/AI_Tool_TA`。
- commandlet 现在会创建 approved sockets，保存 temp public Skeleton package，post-check socket presence，再删除本轮创建的 sockets 并保存 rollback。
- 新增 `dcc-hosts/unreal-socket-import-checker/scripts/run_native_controlled_write.py`：复制 public Unreal project 到 `D:\cs\_test`，备份 `SK_Hero_Skeleton.uasset`，运行 apply/post-check/rollback，并把 uasset 字节恢复到 preflight hash。
- 新增 R65 build artifact：`dcc-hosts/unreal-socket-import-checker/artifacts/unreal-socket-native-bridge-build-20260806-070743.json`。
- 新增 R65 controlled-write artifact：`dcc-hosts/unreal-socket-import-checker/artifacts/unreal-socket-native-controlled-write-20260806-070821.json`。
- 更新 Maya Presenter Pack API、`validate_loop.ps1`、两个 manifest 和公开文档，把 package 推进到 `ai-tool-ta-dcc-first-showcase-r65` / `dcc-first-package@1.62.0`。
- 新增 R65 Presenter Pack：`dcc-hosts/maya-auroraview-host/artifacts/r65-unreal-socket-native-controlled-write-presentation-pack-20260806-071240.json`。

# 四.计划&状态

已验证：

- `python -m py_compile dcc-hosts\unreal-socket-import-checker\scripts\run_native_controlled_write.py`
- `python dcc-hosts\unreal-socket-import-checker\scripts\run_native_bridge_build.py`
- `python dcc-hosts\unreal-socket-import-checker\scripts\run_native_controlled_write.py`
- `.\scripts\validate_loop.ps1 -Tier package`
- Maya mayapy 导出 R65 Presenter Pack：63 / 63 evidence files present，0 missing required files，53 demo route steps，gate=`CapturePending`

当前状态：R65 已证明 native commandlet 能在 Unreal 5.3 临时工程内创建 2 个 approved sockets，保存 temp public Skeleton，post-check 2 个 socket 存在，rollback 删除 2 个 socket，并恢复 uasset preflight hash；returnCode=0，assetWrites=2，engineWrites=0，productionWrites=0，persistentMutation=false。下一轮优先把 gameplay attach readiness 接到 controlled write 结果，或转向 Control Rig / MotionBuilder 等未完成运行时线。
