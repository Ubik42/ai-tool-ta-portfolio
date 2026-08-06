# 一.问题反馈

用户要求长期循环开发，不在只剩手动 GUI 采集之前暂停。R75 选择推进 R74 的 Control Rig native bridge readiness：把 public C++ Editor plugin source 从“源码/readiness 完整但 binary 缺失”推进到真实 RunUAT BuildPlugin 编译证据。

# 二.⭐回顾分析

R45 已证明 `CR_HeroFace` compile 方法可以被 Unreal Python 调用，但 direct compile status / diagnostics 不可读。R74 已新增 `AI_Tool_TA_ControlRigBridge` public Editor plugin source 和 runtime readiness artifact，明确剩余 gate 是 compiled binary / commandlet visible。R75 复用 Socket / AnimNotify native bridge 的 BuildPlugin harness 模式，继续保持 build output 在 `D:\cs\_test`，仓库只提交 JSON receipt、日志引用和 DLL hash。

# 三.改动解释

新增 `dcc-hosts/unreal-control-rig-bridge/scripts/run_control_rig_native_bridge_build.py`，执行 RunUAT `BuildPlugin`，检查 RunUAT、MSVC、必要源码文件，临时固定 UE 5.3 兼容 MSVC 14.38，并在结束后恢复 UBT `BuildConfiguration.xml`。生成 artifact：`dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-native-bridge-build-20260806-100928.json`。

同步了 Maya Presenter Pack API、`scripts/validate_loop.ps1`、public manifest、DCC-first manifest、README、public package 文档、AI handoff 和技术报告。R75 Presenter Pack 为 `dcc-hosts/maya-auroraview-host/artifacts/r75-unreal-control-rig-native-bridge-build-presentation-pack-20260806-101502.json`。

# 四.计划&状态

R75 build 结果：L3-build / `Ready` / `unreal_control_rig_native_bridge_plugin_built`，returnCode=0，compiledDlls=1，errorLines=0，compilerVersion=14.38.33130，configRestored=true，DLL bytes=151552，sha256=`9930fe41e8c2893f860eb03059539b5cbbf58e318158be3636200b949a5a476b`，assetWrites=0，engineWrites=0，productionWrites=0。

下一轮优先做 Control Rig native commandlet probe，把 R75 compiled plugin 证据推进到 Unreal runtime-loaded diagnostics。次优先是 MotionBuilder adapter。Maya GUI 9 张截图和 1 段录屏仍留到最后集中采集。
