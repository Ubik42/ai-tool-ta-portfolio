# 一.问题反馈

用户要求长期循环开发 AI Tool TA 作品集，未完全做完且不只剩用户手动操作时不暂停。当前方向继续围绕 Lightbox 高价值业务逻辑，把 DCC / 引擎内可展示的工具链做成可运行、可验证、可交接的作品集案例。

# 二.⭐回顾分析

R29 已经把 Platform Variant Forge 推进到 Unreal Runtime Probe：可从 Unreal Python 采集公开 synthetic StaticMesh 运行时事实，并对比 PC/Mobile variant 计划中的路径、LOD、材质、Nanite 和碰撞状态。

R30 选择继续补业务闭环中最关键的一段：不是只看出问题，而是把 runtime drift 转成可执行前的生成计划。这个计划对应真实管线里很核心的经验：平台变体不能直接粗暴改资产，必须把 LOD、材质合批、贴图降级、Nanite 策略、碰撞简化、路径命名、缺失目标资产创建等动作拆成带 owner approval、rollback、前置条件和证据来源的 operation contract。

本轮结论是：公开 synthetic 证据可以稳定生成 dry-run 计划，但 gate 仍为 Blocked，因为 Vehicle_Cinematic_PC / Vehicle_Mobile_LOD2 等源资产和目标资产不存在；HeroPanel 的 LOD / texture bake 类操作处于 Review，因为公开 fixture 目前没有可读的 geometry / texture 尺寸事实，不把 destructive bake 冒充为真实执行成功。

# 三.改动解释

新增 `platform_variant_forge.generation_plan`，把 R29 runtime artifact 和 R28 variant plan 汇总为 generation plan artifact。输出包含 operation type、source variant、target platform、preconditions、runtime evidence、approval requirement、rollback strategy、executor readiness 和 blocking reason。

新增 `scripts/run_generation_plan.py`，提供固定入口生成 `platform-variant-generation-plan-*.json`。`scripts/validate_loop.ps1` 增加 `platform-variant-generation` tier，并把生成计划模块纳入 quick compile。

更新 Maya AuroraView host API：Presenter Pack 默认提升到 R30；证据探针增加 Platform Variant Generation Plan；demo route 增加运行 generation plan 的步骤；summary 和 reviewer claims 加入 R30 的 gate、operation count、ready/review/blocked/satisfied/owner approval 统计。

更新 public-case-package manifest、README、DCC_FIRST_PACKAGE、EVIDENCE_INDEX、VALIDATION、AI_HANDOFF、模块文档和技术报告。当前 public package 为 `ai-tool-ta-dcc-first-showcase-r30` / `dcc-first-package@1.27.0`，Presenter Pack 为 `r30-platform-variant-generation-plan-presentation-pack-20260805-190107.json`。

# 四.计划&状态

R30 状态：已完成。最终 generation plan artifact 为 `dcc-hosts/platform-variant-forge/artifacts/platform-variant-generation-plan-20260805-190052.json`；Presenter Pack 为 `dcc-hosts/maya-auroraview-host/artifacts/r30-platform-variant-generation-plan-presentation-pack-20260805-190107.json`。

验证结果：`.\scripts\validate_loop.ps1 -Tier platform-variant-generation` 已通过并生成最终 artifact；`.\scripts\validate_loop.ps1 -Tier quick` 通过；`.\scripts\validate_loop.ps1 -Tier package` 通过，package smoke 结果为 R30 / 1.27.0 / 27 evidence / 0 missing。JSON manifest 和关键 artifact 均通过 `python -m json.tool`。

下一轮入口：优先开发 Platform Variant Texture Runtime Collector，用 Unreal Python 进一步采集材质贴图引用、贴图尺寸、压缩设置和平台 override 事实，减少 R30 里 texture downscale / material merge 只能停在 Review 的情况。之后再推进 controlled executor，把 dry-run operation 中 executorReady 的非破坏性动作接成可控执行。
