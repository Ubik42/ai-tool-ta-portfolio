# Cross-DCC Rule Matrix

R2 目标：把 Pyblish 类检查经验抽象成“共享 rule + DCC adapter + validation report”的可展示工具。

## 方法来源

- `maya_publish_rule_reference`
- `maya_rule_adapter_reference`
- `blender_rule_adapter_reference`
- `max_rule_adapter_reference`
- `houdini_rule_adapter_reference`

## 核心业务秘诀

检查工具的价值不在规则数量，而在规则能不能跨资产、跨 DCC、跨项目复用。

正确拆法是：

- DCC adapter 只负责 Collect：把 Maya DAG、Blender custom properties、Max user props、Houdini geometry attrs 归一化。
- 共享 rule 只负责 Validate：读标准 input，输出 status、evidence、fixability。
- Fix Preview 只声明可安全修改的字段和必须人工判断的动作。
- Extract 产出稳定 report，让平台能统计、追踪和复盘。

这套拆法能避免每个 DCC 写一套 if/else 检查脚本。

## 当前实现

代码入口：

- `showcases/portfolio-site/src/data/ruleMatrix.ts`
- `showcases/portfolio-site/src/components/CrossDccRuleMatrix.tsx`
- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`

R2 初版已实现：

- Maya / Blender / 3ds Max / Houdini synthetic adapter。
- 6 条共享 rule：protocol carrier、collision、LOD、material/texture、export root、publish manifest。
- adapter summary：score、pass、review、block、gate。
- cross-DCC rule matrix。
- selected rule detail。
- adapter payload panel。
- Collect / Validate / Fix Preview / Extract 时间线。
- Rule DSL 预览。
- AI brief。
- validation run report JSON。

R2.1 已补：

- rule fixture editor：切换 Asset Protocol 的 synthetic asset context。
- adapter capability toggles：按当前 DCC 开关 collector 能力，影响 skipped、warning 和 report。
- severity heatmap：把 DCC x rule 风险压缩成可扫描热区。
- fix preview queue：把 safe、manual、capability gap 拆成可审查队列。
- report export：导出当前 asset、adapter、capability、evaluation、fix queue 的 JSON。

R2.2 已补：

- rule authoring draft：从项目规范文本生成 DSL 草案，状态分为 `Needs TA Review` 和 `TA Accepted`。
- adapter trace：展示 DCC source field 如何映射到共享 normalized field。
- fix queue action states：`pending`、`approved`、`blocked`、`exported`。
- case-study card：把 R2 的业务问题、核心逻辑、AI 边界、证据链压缩成作品集讲法。
- report JSON 升级到 `cross-dcc-rule-report@0.2.0`，包含 trace、draft 和 queue action state。

R2.3 已补：

- draft accept audit：`Accept Draft` / `Reopen Draft` 会写入审计记录。
- trace payload diff：把 DCC source field、source value、normalized field、normalized value 和 transform 关系展开。
- publish gate report：把 R1 Asset Protocol readiness 和 R2 Rule Matrix gate 合并成最终发布门禁。
- report JSON 升级到 `cross-dcc-rule-report@0.3.0`，包含 `authoringAudit`、`traceDiff` 和 `publishGate`。

R2.4 已补：

- fix preview payload diff：把 fix queue 展开成字段级 before / after payload，区分 `safe_auto`、`manual_only`、`adapter_gap`。
- manual-only owner disposition：为 collision、LOD、material/texture 等人工项记录 reason code、owner question、required evidence 和 policy。
- publish gate 读取 `fixPreviewDiffCount`、`manualDispositionCount`、`ownerDispositionPending`。
- report JSON 升级到 `cross-dcc-rule-report@0.4.0`，包含 `fixPreviewDiff` 和 `manualDispositionReceipt`。

R9.3 DCC-first 已补：

- Maya host 新增 `rule_matrix_collect_scene`、`rule_matrix_validate_scene`、`rule_matrix_preview_fixes`、`rule_matrix_export_report`。
- `Collect Scene` 从 Maya selection 采集 transform、mesh shape、triangles/faces、shadingEngine、parent/root、`aiToolTaProtocol`、schema、LOD、collision、budget。
- `Validate Scene` 在 Maya scene facts 上执行 6 条规则，输出 gate、score、pass/warning/error/skipped、evidence 和 fix preview。
- `Preview Fixes` 只生成 staged mutation，不直接改场景，区分 `safe_auto` 和 `manual_only`。
- `Export DCC Report` 输出 `maya-rule-matrix-dcc-report@1.0.0` artifact。
- React 模块新增 `Maya Scene Rule Run` 面板，展示 facts、validation rows、fix preview、summary 和 JSON payload。

R21 3ds Max adapter 已补：

- 新增 `dcc-hosts/3dsmax-rule-adapter`，用公开 synthetic fixture 归一化 3ds Max user properties、layer/export root、LOD suffix、material slot、map channel、transform 和 collision proxy。
- `contract.py` 输出 `cross-dcc-rule-input@0.1.0`，并复用共享规则判断 protocol、unit/up axis、export root、LOD、material、UV、transform、collision、vertex color。
- `runtime_collector.py` 提供 `pymxs` collector 路径，`run_l3_smoke.py` 默认只导出 readiness，不自动启动 3ds Max batch。
- 本机发现 `3dsmaxbatch.exe`，当前 L3 harness gate 为 `Review`，等待 operator 显式 `--run-runtime`。

## 当前规则设计

| Rule | 业务目的 |
| --- | --- |
| Protocol Carrier | 确认协议字段落在下游稳定 carrier |
| Collision Contract | 阻断缺 collision 或未审查 collision |
| LOD Budget | 同时检查 LOD count、screen size、cull distance |
| Material / Texture Sync | 暴露材质槽和贴图集漂移 |
| Export Root Clean | 收敛 namespace、root、临时节点 |
| Publish Manifest | 把结果、adapter payload、fix preview 提取成 report |

## AI 边界

AI 只做解释和聚类：

- 总结哪些 rule 阻断 publish。
- 把 adapter capability gap 翻译成 TA 能处理的下一步。
- 说明 safe fix 和 manual action 边界。

AI 不改写 rule result，也不把 skipped/warning 当 pass。

## 当前证据

- `assets/cross-dcc-rule-matrix-r2-desktop-full.png`
- `assets/cross-dcc-rule-matrix-r2-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-1-fixture-editor-full.png`
- `assets/cross-dcc-rule-matrix-r2-1-fix-queue-full.png`
- `assets/cross-dcc-rule-matrix-r2-1-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-1-exported-report.json`
- `assets/cross-dcc-rule-matrix-r2-2-authoring-trace-full.png`
- `assets/cross-dcc-rule-matrix-r2-2-queue-actions-full.png`
- `assets/cross-dcc-rule-matrix-r2-2-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-2-exported-report.json`
- `assets/cross-dcc-rule-matrix-r2-3-publish-gate-full.png`
- `assets/cross-dcc-rule-matrix-r2-3-trace-diff-full.png`
- `assets/cross-dcc-rule-matrix-r2-3-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-3-exported-report.json`
- `assets/cross-dcc-rule-matrix-r2-4-fix-diff-full.png`
- `assets/cross-dcc-rule-matrix-r2-4-mobile-tall.png`
- `assets/cross-dcc-rule-matrix-r2-4-exported-report.json`

R2.1 浏览器验证：

- `Hero Character / LOD partial + 3ds Max` 默认 gate 为 `Review`。
- 打开 `Material / Texture` collector 后 gate 变为 `Ready`。
- 导出 report：`adapter=max`、`fixture=character_lod_partial`、`score=100`、`pass=6`、`fixQueue=0`。

R2.2 浏览器验证：

- 修改 Project Spec 后，rule draft 回到 `Needs TA Review`。
- 点击 `Accept Draft` 后，report 内 `authoringDraft.reviewState=accepted`。
- 默认 `Mobile Crate / risky + Maya` 的 fix queue 支持逐条改成 `approved`、`blocked`、`exported`。
- 导出 report 包含 `adapterTrace.length=6` 和 queue action state。

R2.3 浏览器验证：

- `Accept Draft` 后生成 authoring audit。
- 导出 report 包含 `authoringAudit.length>=1`、`traceDiff.length=6`、`publishGate.finalGate=Blocked`。
- publish gate 同时读取 Asset Protocol readiness、Rule Matrix summary、draft accepted 和 trace mapping。

R2.4 浏览器验证：

- 默认 `Mobile Crate / risky + Maya` 导出 `cross-dcc-rule-report@0.4.0`。
- `fixPreviewDiff.summary.total=4`，其中 `safeAuto=1`、`manualOnly=3`、`ready=1`、`review=2`、`blocked=1`。
- `manualDispositionReceipt.summary.total=3`，其中 `ownerRequired=1`、`blocked=1`、`documented=1`。
- Playwright 桌面和移动端无横向溢出。

R9.3 Maya mayapy 验证：

- 创建 `r9_3_rule_matrix_fixture`，生成 `hero_prop_body1` / `hero_prop_socket1`。
- `rule_matrix_collect_scene()` 返回 `count=2`。
- `rule_matrix_validate_scene()` 返回 `validation_rows=6`、`gate=Blocked`。
- `rule_matrix_preview_fixes()` 返回 `fix_preview_total=3`。
- `rule_matrix_export_report()` 导出：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-3-rule-matrix-smoke-20260803-155309.json
```

R21 3ds Max adapter 验证：

- `python dcc-hosts/3dsmax-rule-adapter/scripts/run_smoke.py` 通过。
- L2+ contract：2 assets，1 Ready，0 Review，1 Blocked。
- Checks：13 pass，5 warning，2 error。
- `python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py` 通过。
- L3 readiness：`Review`，collector ready，`3dsmaxbatch.exe` discovered，runtime launch opt-in。

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-readiness-20260804-220959.json
```

## 下一轮

R7.4 状态：

- R2 `accept-rules-r2` 已在 `owner-signoff-ledger@0.1.0` 中签收。
- 签收范围：safe auto-fix 只在 adapter capability 支持时运行；manual-only 和 adapter-gap 项保持 owner-owned。
- 证据入口：`assets/portfolio-case-study-r7-4-exported-report.json`。

下一轮：

- 在 operator 允许时运行 3ds Max `--run-runtime`，把 readiness 升级为 `max-rule-adapter-pymxs-l3@0.1.0`。
- 如果暂不启动 Max batch，继续补 Houdini / MotionBuilder adapter contract 或采集 Maya GUI media。

