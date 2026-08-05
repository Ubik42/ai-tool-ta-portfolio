# 一.问题反馈

本轮继续长期循环开发，目标是不要停在 `Platform Variant Public Texture2D Payload Fixture` 的预算证明上，而是把 R30 dry-run generation operation 接成真实 Unreal public fixture 内的受控执行证据。要求仍然是 DCC / 引擎内可展示的工具管线 TA 业务逻辑，不扩写纯前端说明。

# 二.⭐回顾分析

R32 已经把 HeroPanel Mobile 的 texture budget 从“缺真实 Texture2D payload 的 Review”推进到可计算预算对照，但还缺一个更接近生产工具价值的环节：工具决定执行某个变体修复动作时，必须证明 preflight、writeSet、post-check、rollback 和 production write boundary。

本轮选择 `Platform Variant Controlled Executor`：读取 R30 generation plan 与 R32 texture payload artifact，选中 HeroPanel Mobile texture downscale 中 public-safe 的 max texture size clamp。它不是直接宣称修复完成，而是在 Unreal 公开 test project 内执行一次可回滚写入并导出证据。

# 三.改动解释

新增 `platform_variant_forge/controlled_executor.py`、`scripts/run_controlled_executor.py` 和 Unreal Python 执行脚本 `scripts/unreal_python/execute_controlled_variant.py`。执行器进入 Unreal 5.3.2 public test project，读取 `/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor`，记录 preflight fingerprint `2502b08c541495a4` 与 maxTextureSize=0，执行 maxTextureSize=2048 后保存并验证 post-state fingerprint `4374814fafe3a008`，随后 rollback 到 maxTextureSize=0 并确认 fingerprint 回到 `2502b08c541495a4`。

新增 R33 artifact：`dcc-hosts/platform-variant-forge/artifacts/platform-variant-controlled-executor-20260805-200810.json`。结果为 L3 / `Ready` / `unreal_texture_budget_executor_rolled_back`，7 pass / 0 warning / 0 error，1 executed operation，1 post-check pass，1 rollback pass，assetWrites=2，persistentMutation=false。

Maya AuroraView Presenter Pack 接入新增 evidence probe、summary 字段和 demo route 第 17 步。public manifests 升级到 `ai-tool-ta-dcc-first-showcase-r33` / `dcc-first-package@1.30.0`，Presenter Pack 为 `dcc-hosts/maya-auroraview-host/artifacts/r33-platform-variant-controlled-executor-presentation-pack-20260805-200857.json`，30 / 30 evidence present，0 missing，22 demo route steps。同步更新 public package 文档、AI_HANDOFF、Platform Variant 模块文档、DCC-first case page、技术报告和长期计划。

# 四.计划&状态

验证已完成：`python dcc-hosts/platform-variant-forge/scripts/run_controlled_executor.py` 通过；R33 Presenter Pack mayapy export 通过并生成 30 / 30 evidence present、0 missing、22 route steps；两个 manifest、R33 controlled executor artifact 和 R33 Presenter Pack 均通过 `python -m json.tool`。提交前继续跑 `.\scripts\validate_loop.ps1 -Tier quick` 和 `.\scripts\validate_loop.ps1 -Tier package`。

下一轮入口：`Platform Variant Executor Expansion`。优先把 LOD / Nanite / collision 的 candidate receipts、owner approval 边界和 rollback preview 接到当前 executor 报告；如果切线，则做 Character Calibration / Spatial Authoring 的 Maya UI drilldown 与 Unreal 对照。Maya GUI 9 张截图和 1 段录屏继续留到最后集中采集。
