# 一.问题反馈

用户要求长期循环开发，不能在未完成时停下。本轮继续沿 Lightbox 高价值业务线推进 `Platform Variant Forge`，补齐 R30 里 texture bake / downscale 只能停在 Review 的运行时证据缺口。

# 二.⭐回顾分析

R30 已经能把 Unreal runtime drift 转成 dry-run generation operations，但 texture 相关 operation 的证据仍停在“尚未采集 runtime texture facts”。这在真实 TA 管线里不够，因为平台降级的核心不只是 LOD 和 Nanite，还包括材质槽、材质依赖、Texture2D 尺寸、估算内存、压缩和色彩空间这些引擎侧事实。

本轮选择做 `Platform Variant Texture Runtime Collector`：进入 Unreal public test project，沿 planned StaticMesh -> material slot -> material asset -> dependency / expression texture -> Texture2D settings 采集事实。结果证明 collector 可运行，且能把 Mobile HeroPanel 的问题从“不知道贴图事实”缩小成“synthetic material 没有真实 Texture2D payload”。这给下一轮 public Texture2D fixture 或 controlled executor 提供了明确输入。

# 三.改动解释

新增 `platform_variant_forge.texture_runtime`，把 R28 variant plan、R29 runtime artifact 和 Unreal texture snapshot 合成 `platform-variant-texture-runtime@0.1.0` 报告，输出 per-variant texture gate、pass/warning/error rows 和 dry-run texture action preview。

新增 Unreal Python 采集脚本 `scripts/unreal_python/collect_texture_runtime.py`，在 `/Game/AI_Tool_TA` public fixture 范围内读取 StaticMesh material slots、material dependency query、material expression texture references、Texture2D size / estimated memory / compression / sRGB / readability。新增外部 launcher `scripts/run_texture_runtime_probe.py`，负责定位 UnrealEditor-Cmd、项目、plan artifact 和最新 runtime artifact。

更新 Maya AuroraView host Presenter Pack：默认包切到 R31，增加 texture runtime artifact probe、demo route 第 15 步、summary 字段和 reviewer claim。更新 `validate_loop.ps1`，新增 `platform-variant-texture` tier，quick compile 覆盖新模块，package smoke 期待 28 个 evidence。

更新 public-case-package manifest、README、DCC_FIRST_PACKAGE、EVIDENCE_INDEX、VALIDATION、AI_HANDOFF、模块文档、长期计划和技术报告。当前 public package 为 `ai-tool-ta-dcc-first-showcase-r31` / `dcc-first-package@1.28.0`。

# 四.计划&状态

R31 状态：已完成。最终 texture runtime artifact 为 `dcc-hosts/platform-variant-forge/artifacts/platform-variant-texture-runtime-20260805-191529.json`；Presenter Pack 为 `dcc-hosts/maya-auroraview-host/artifacts/r31-platform-variant-texture-runtime-presentation-pack-20260805-191803.json`。

验证结果：`python dcc-hosts/platform-variant-forge/scripts/run_texture_runtime_probe.py` 已通过，Unreal 5.3.2 / Python 3.9.7 输出 L3 artifact；3 variants，1 Ready，1 Review，1 Blocked；19 pass，1 warning，1 error；assetWrites=0。`.\scripts\validate_loop.ps1 -Tier quick` 通过；`.\scripts\validate_loop.ps1 -Tier package` 通过，package smoke 结果为 R31 / 1.28.0 / 28 evidence / 0 missing。

下一轮入口：优先开发 `Platform Variant Public Texture2D Payload Fixture`，让 Mobile downscale 从“缺真实贴图 payload 的 Review”进入可计算 texture budget 对照；或开发 `Controlled Executor`，从 R30 operation contract 中选择 public fixture 内可执行、可 rollback 的非破坏性动作。
