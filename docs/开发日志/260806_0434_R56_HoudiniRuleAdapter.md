# 一.问题反馈

用户要求长期循环开发，不在未完成前停下；当前作品集必须继续基于 Lightbox 高价值业务逻辑做 DCC / 引擎内可展示工具，不漂移成纯前端说明。

本轮选择 Houdini Rule Adapter：补齐非 Maya / Max / Blender 之外的程序化资产交付线，把 HDA、PDG、bake receipt 这类 Houdini 核心业务事实接入 Cross-DCC Rule Matrix。

# 二.⭐回顾分析

R55 已完成 Groom Runtime Fact Collector，Presenter Pack 为 `r55-groom-runtime-facts-presentation-pack-20260806-040806.json`，53/53 evidence files present，43 demo route steps。

本机未发现 `hython.exe`，因此 Houdini 不能宣称真实 L3 runtime 成功。本轮采用两层证据：普通 Python contract smoke 证明业务规则与 fixture schema；hython readiness harness 明确导出 blocked gate，并记录 collector / launcher 已 ready。

Houdini 线的业务重点不是 mesh 常规属性，而是 procedural publish 是否可冻结、可复现、可拆输出角色、可追踪 cook/wedge/bake 收据。

# 三.改动解释

新增 `dcc-hosts/houdini-rule-adapter`：

- `fixtures/synthetic_houdini_scene.json`：公开 synthetic Houdini procedural fixture，包含 1 个 Ready cliff kit 和 1 个 Blocked fracture setup。
- `houdini_rule_adapter/contract.py`：把 HDA locked state、detail attrs、`OUT_*` nodes、geometry attrs、packed prototypes、PDG wedges、bake receipts 归一化成 `cross-dcc-rule-input@0.1.0` 并输出 rule rows。
- `houdini_rule_adapter/hou_collector.py`：真实 hython 可用时创建 public subnet fixture，并通过 `hou` 回收 runtime facts。
- `scripts/run_smoke.py`、`scripts/run_houdini_l3.py`、`scripts/run_l3_smoke.py`：分别提供普通 contract smoke、hython collector、自动 discovery/readiness 入口。

接入 `MayaPortfolioApi.dcc_presentation_build_pack()`：新增 Houdini contract/readiness 两个 evidence probe，demo route 从 43 步扩展到 45 步，summary 增加 Houdini gate、asset/check counts、hython availability 和 collector readiness。

更新 public package：

- `ai-tool-ta-dcc-first-showcase-r56` / `dcc-first-package@1.53.0`
- `ai-tool-ta-public-case-package-r8-80` / `public-case-package@3.50.0`
- R56 Presenter Pack：`dcc-hosts/maya-auroraview-host/artifacts/r56-houdini-rule-adapter-presentation-pack-20260806-042654.json`
- 当前结果：55/55 evidence files present，0 missing required files，45 demo route steps，gate=`CapturePending`。

同步 README、AI_HANDOFF、public evidence/validation、DCC_FIRST_PACKAGE、Lightbox 覆盖报告、工程摘要和 Houdini 模块文档。

# 四.计划&状态

已完成代码、artifact、manifest、Presenter Pack 和文档接入。

当前正式证据：

- `dcc-hosts/houdini-rule-adapter/artifacts/houdini-rule-adapter-contract-20260806-041956.json`
- `dcc-hosts/houdini-rule-adapter/artifacts/houdini-rule-adapter-l3-readiness-20260806-041956.json`
- `dcc-hosts/maya-auroraview-host/artifacts/r56-houdini-rule-adapter-presentation-pack-20260806-042654.json`

待验证：

- `.\scripts\validate_loop.ps1 -Tier quick`
- `.\scripts\validate_loop.ps1 -Tier houdini`
- `.\scripts\validate_loop.ps1 -Tier package`
- `python -m json.tool` 检查 R56 artifact / manifest
- `git diff --check`

下一轮入口：如果能定位 `hython.exe`，先升级 Houdini L3；否则继续 MotionBuilder adapter、Control Rig Editor Utility / C++ diagnostic bridge、socket C++ / Editor Utility adapter 或 Groom group/root projection 细分 fixture。
