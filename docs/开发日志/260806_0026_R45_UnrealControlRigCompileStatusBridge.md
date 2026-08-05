# 一.问题反馈

用户要求长期循环开发，不在只剩人工 Maya GUI 采集前停下。本轮延续 R44 后的角色绑定业务线：Face Skeleton target 已闭环，剩下要确认 Unreal Control Rig compile readiness 不能只停留在“API surface 可见”。

# 二.⭐回顾分析

R44 已把 approved 角色从 Skeleton target Blocked 推进到 compile-status Review：`CR_HeroFace`、5 个 runtime controls、`SK_HeroFace_Skeleton` target coverage 和 shape/offset facts 都可读。真正剩余风险是 compile 方法能否被工具调用，以及 UE Python 是否能读到 direct compile status / diagnostics。

R45 的判断是：可以先做 transient compile probe，而不是等待 C++/Editor Utility。它能证明 public fixture 上 compile method visible / invoked / succeeded、dirty-state 和 no-save boundary；如果 direct diagnostics 仍不可读，就明确保持 Review，不把方法调用包装成完整 compile approval。

# 三.改动解释

新增 `unreal_control_rig_bridge/compile_status.py`、`scripts/run_compile_status.py` 和 Unreal commandlet 脚本 `scripts/unreal_python/collect_control_rig_compile_status.py`。脚本读取最新 post-face deformation-link artifact，进入 public Unreal 5.3.2 项目，加载 `CR_HeroFace`，调用 `recompile_vm_if_required` / `recompile_vm` 可见方法，采集 direct status / diagnostics / compile settings、package dirty before/after 和写入边界。

Presenter Pack 新增 `unreal-control-rig-compile-status` evidence probe，demo route 增至 34 步。`public-case-package` manifest、README、DCC_FIRST_PACKAGE、EVIDENCE_INDEX、VALIDATION、MODULES、AI_HANDOFF、模块文档和技术报告同步到 `ai-tool-ta-dcc-first-showcase-r45` / `dcc-first-package@1.42.0`。

# 四.计划&状态

R45 结果：Compile Status Bridge 为 L3 / `Blocked` / `unreal_control_rig_compile_status_collected`，2 character rows，approved 行 Review，TMP 行 Blocked，compile candidate / method visible / invoked / succeeded = 1 / 1 / 1 / 1，direct status / diagnostics / settings = 0 / 0 / 1，dirtyAfter=0，10 pass / 2 warning / 4 error，assetWrites=0，productionWrites=0。

当前 Presenter Pack：`dcc-hosts/maya-auroraview-host/artifacts/r45-unreal-control-rig-compile-status-presentation-pack-20260806-001919.json`，43/43 evidence files present，0 missing required files，34 demo route steps。下一轮入口：Control Rig Editor Utility / C++ diagnostic bridge，或转 gameplay attach fixture / Groom Export Inspector。
