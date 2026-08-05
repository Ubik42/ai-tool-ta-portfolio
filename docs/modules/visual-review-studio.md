# Visual Review Studio

R3 目标：把 `maya_visual_review_reference / visual_compare_reference` 的武器视觉评审经验抽象成公开可运行工具。重点不是渲染漂亮图，而是把视觉评审里的变量固定成可复盘合同。

## 方法来源

- `maya_visual_review_reference/shelf/tools/visual_compare_reference/camera_capture.py`
- `maya_visual_review_reference/shelf/tools/visual_compare_reference/diff_viewer.py`
- `maya_visual_review_reference/shelf/tools/visual_compare_reference/batch_runner.py`
- `maya_visual_review_reference/shelf/tools/visual_compare_reference/report_html.py`
- `maya_visual_review_reference/shelf/tools/visual_compare_reference/wecom_notify.py`

## 核心业务秘诀

视觉评审工具的价值不是截图，而是固定变量：

- A/B import diff：通过导入前后 mesh shape 差异记录槽位几何，避免 namespace、引用和命名不稳定。
- LOD 分桶：mesh 短名先匹配 `LOD0`，再匹配 `DT`，其他 mesh 在固定 pass 中隐藏。
- Pass 合同：同一相机下固定红蓝、白蓝、solo B 三类材质和可见性，让主观差异可解释。
- 跳过逻辑：缺 LOD0 或 DT 时跳过对应 pass，并把原因写入报告。
- 证据包：输出图片、scene backup、HTML overview、通知摘要和 JSON report。

这套逻辑让 review 从“看图感觉不对”变成“哪一个 pass、哪一个 LOD、哪一个阈值导致不能过”。

## 当前实现

代码入口：

- `showcases/portfolio-site/src/data/visualReview.ts`
- `showcases/portfolio-site/src/components/VisualReviewStudio.tsx`
- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`

R3.1 已实现：

- 3 个 synthetic review fixtures：DT 缺失、材质漂移、干净变体。
- A/B slot import diff model：记录 source、unit、mesh、material、missing texture。
- LOD0 / DT / other classifier。
- 5 个 pass preset：`rb_lod0`、`wb_lod0`、`rb_dt`、`wb_dt`、`solo_b`。
- pass run / skip matrix：根据 LOD bucket 和相机组决定是否生成图片。
- shot manifest：按 `<camera>_<LOD>_<kind>.png` 输出命名。
- scene backup contract：`wb_lod0` pass 可导出 `<variant>.ma`。
- review finding engine：unit、LOD、texture、silhouette、bbox、material、camera coverage。
- deterministic gate：`Ready` / `Review` / `Blocked`。
- AI review draft：只总结 findings，不参与 gate 判定。
- notification preview：模拟企业微信群通知摘要。
- report JSON：`visual-review-report@0.1.0`。

R3.2 已补：

- batch runner overview：对所有 review fixtures 生成批处理行。
- capture status 与 review gate 分离：截图能产出不代表资产可发布。
- batch summary：统计 capture ok / failed、Ready / Review / Blocked。
- batch item reason：保留每个 variant 的输出目录、图片数量、pass run / skip 和 gate 原因。
- batch report export：导出 `visual-batch-review@0.1.0`。
- batch notification preview：模拟批处理完成后的企业微信摘要。

R3.3 已补：

- signal thresholds：把 silhouette、bbox、material、camera coverage 做成可解释阈值条。
- diff signal gate：每个信号单独计算 `Ready` / `Review` / `Blocked`，并记录关联 pass。
- review audit trail：AI draft edit、regenerate、Needs Fix、Accept Review 都写入 audit。
- report JSON 升级到 `visual-review-report@0.2.0`，包含 `diffSignals` 和 `reviewAudit`。

R3.4 已补：

- per-pass drilldown：点击 pass 后展开 status、gate、output pattern、camera shot、material contract。
- signal-to-pass jump：点击 signal threshold 会跳到第一个关联 pass，并高亮对应 signal。
- pass evidence graph：每个 pass 关联 deterministic signal、camera shots、linked findings 和 next action。
- batch item detail：点击 batch 行后展开单个 variant 的 evidence、primary signal、top findings、first skipped pass 和 report preview。
- report JSON 升级到 `visual-review-report@0.3.0`，包含 `passDrilldowns`。
- batch report JSON 升级到 `visual-batch-review@0.2.0`，每个 item 带失败摘要字段。

R3.5 已补：

- review queue drilldown：从 deterministic finding 生成可处理队列项。
- owner / gate filters：按 `artist`、`ta`、`reviewer` 和 `Blocked` / `Review` / `Ready` 筛选。
- queue detail：每个 item 保留 source finding、severity、priority、evidence、related passes、next check、handoff note。
- queue state actions：支持 `Mark Todo`、`Mark Blocked`、`Mark Ready`，并写入 review audit。
- report JSON 升级到 `visual-review-report@0.4.0`，包含 `reviewQueueSummary` 和当前 queue state。
- batch report JSON 升级到 `visual-batch-review@0.3.0`，每个 item 带 queue blocked / todo / ready 统计。

R3.6 已补：

- owner handoff packet：把 review queue 按 `artist`、`ta`、`reviewer` 聚合成交接包。
- section message preview：每个 owner 生成自己的 gate、queue 统计、output 目录和 priority action 列表。
- shared evidence：交接包统一携带 output dir、overview HTML、scene backup 和 image count。
- handoff export：单独导出 `visual-review-handoff@0.1.0`，用于模拟企业微信或评审系统交接。
- report JSON 升级到 `visual-review-report@0.5.0`，包含完整 `handoffPacket`。
- batch report JSON 升级到 `visual-batch-review@0.4.0`，每个 item 带 handoff owners 和 handoff preview。

R3.7 已补：

- handoff delivery states：每个 owner section 都有 `draft`、`sent`、`failed`、`read`、`acknowledged`、`not_required` 状态。
- delivery receipt：记录 channel、recipient、attempts、last event、next action。
- delivery actions：支持 `Send Packet`、`Simulate Fail`、`Mark Read`、`Acknowledge`，并写入 review audit。
- retry logic：失败后重新发送会递增 attempts，`read` 不等于 `acknowledged`。
- handoff packet JSON 升级到 `visual-review-handoff@0.2.0`，包含 `deliverySummary` 和每个 section 的 `delivery`。
- report JSON 升级到 `visual-review-report@0.6.0`，batch report JSON 升级到 `visual-batch-review@0.5.0`。

R3.8 已补：

- final release gate：把 capture contract、signal thresholds、queue resolution、handoff ack、review decision、evidence package 合成最终发布门禁。
- release criteria：每项 criterion 保留 gate、summary、evidence 和 next action。
- release decision：输出 `release_candidate`、`hold_for_review`、`blocked_from_release`。
- release note preview：生成可交给 reviewer / publisher 的候选发布摘要。
- release gate export：单独导出 `visual-review-release-gate@0.1.0`。
- report JSON 升级到 `visual-review-report@0.7.0`，batch report JSON 升级到 `visual-batch-review@0.6.0`。

R3.9 已补：

- runtime fixture editor：在当前 fixture 上调 silhouette、bbox、material、camera coverage、B 单位、B 材质数、missing textures、B DT mesh 数。
- scenario presets：`Clean Candidate`、`DT Blocker`、`Texture Review`、`Camera Gap`、`Unit Mismatch` 可快速切换典型生产风险。
- edit invalidation：每次修改 fixture 都清空旧 review decision、queue state、handoff delivery 和 audit，避免旧结论套到新数据。
- fixture edit snapshot：报告导出 `before / after`、`changedFields` 和 `mode`，让评审人知道当前结果来自原始 fixture 还是 runtime 编辑。
- batch runner 联动：batch report 使用编辑后的 fixture 列表，单个 item 也携带 `fixtureEditSummary`。
- report JSON 升级到 `visual-review-report@0.8.0`，batch report JSON 升级到 `visual-batch-review@0.7.0`。

R3.10 已补：

- workflow map：把长页拆成 `Setup`、`Capture`、`Triage`、`Handoff`、`Batch`、`Draft` 六段。
- focus preset：提供 `Full Workbench`、`Review Focus`、`Release Focus`，快速切换展示密度。
- anchor jump：每个 workflow row 可跳转到对应段，适合演示和复盘。
- collapsible sections：每段可单独隐藏，折叠后保留摘要和恢复按钮。
- gate hint：导航行显示对应 workflow 段当前 `Ready` / `Review` / `Blocked` 状态。
- 本轮不改业务报告 schema，report JSON 继续使用 `visual-review-report@0.8.0`，batch report 继续使用 `visual-batch-review@0.7.0`。

R9.4 DCC-first 已补：

- Maya host 新增 `visual_review_create_camera_rig`、`visual_review_build_pass_manifest`、`visual_review_preview_capture`、`visual_review_export_report`。
- `Create Rig` 在 Maya 中创建 basic/detail camera rig，共 10 个 review cameras，并用 `aiToolTaReviewCamera` 标记 group。
- `Build Manifest` 从 Maya scene mesh 名称推导 `LOD0` / `DT` / other 分桶，并根据 cameras 和 pass preset 生成 run / skip。
- `Preview Capture` 规划 capture 输出路径，当前不强制 playblast，保持 headless 可测，GUI 下一步再接真实截图。
- `Export DCC Review` 输出 `maya-visual-review-dcc-report@1.0.0` artifact。
- React 模块新增 `Maya Capture Setup` 面板，展示 camera / mesh / pass / image / gate、pass rows、output path 和 JSON payload。

## 当前规则设计

| 信号 | 业务目的 |
| --- | --- |
| Unit mismatch | 阻断 A/B 不同单位导致的 overlay 误判 |
| LOD pass skip | 阻断缺少 LOD0 / DT 的不可比较资产 |
| Missing textures | 提醒 sourceimages 或贴图包缺失 |
| Silhouette delta | 区分轻微差异、需复核差异和阻断差异 |
| BBox delta | 暴露比例、root transform 或导出单位问题 |
| Material drift | 发现 shader slot 合并、材质绑定丢失或贴图同步风险 |
| Camera coverage | 保证 default/detail camera 足够覆盖审查视角 |

## AI 边界

AI 在这个模块里只做 review comment 草案：

- 把 deterministic findings 聚合成给 artist/reviewer 的说明。
- 解释 pass skip、材质漂移、单位风险。
- 生成通知摘要和复盘文字。

AI 不改变 pass run / skip，不覆盖阈值，不把人工接受写成自动通过。

## 当前证据

- `assets/visual-review-r3-1-pass-matrix-full.png`
- `assets/visual-review-r3-1-clean-ready-full.png`
- `assets/visual-review-r3-1-mobile-tall.png`
- `assets/visual-review-r3-1-exported-report.json`
- `assets/visual-review-r3-2-batch-overview-full.png`
- `assets/visual-review-r3-2-mobile-tall.png`
- `assets/visual-review-r3-2-batch-report.json`
- `assets/visual-review-r3-3-signal-audit-full.png`
- `assets/visual-review-r3-3-mobile-tall.png`
- `assets/visual-review-r3-3-exported-report.json`
- `assets/visual-review-r3-4-drilldown-full.png`
- `assets/visual-review-r3-4-mobile-tall.png`
- `assets/visual-review-r3-4-exported-report.json`
- `assets/visual-review-r3-4-batch-report.json`
- `assets/visual-review-r3-5-queue-full.png`
- `assets/visual-review-r3-5-mobile-tall.png`
- `assets/visual-review-r3-5-exported-report.json`
- `assets/visual-review-r3-5-batch-report.json`
- `assets/visual-review-r3-6-handoff-full.png`
- `assets/visual-review-r3-6-mobile-tall.png`
- `assets/visual-review-r3-6-exported-report.json`
- `assets/visual-review-r3-6-handoff-packet.json`
- `assets/visual-review-r3-6-batch-report.json`
- `assets/visual-review-r3-7-delivery-full.png`
- `assets/visual-review-r3-7-mobile-tall.png`
- `assets/visual-review-r3-7-exported-report.json`
- `assets/visual-review-r3-7-handoff-packet.json`
- `assets/visual-review-r3-7-batch-report.json`
- `assets/visual-review-r3-8-release-full.png`
- `assets/visual-review-r3-8-mobile-tall.png`
- `assets/visual-review-r3-8-exported-report.json`
- `assets/visual-review-r3-8-release-gate.json`
- `assets/visual-review-r3-8-batch-report.json`
- `assets/visual-review-r3-9-fixture-editor-full.png`
- `assets/visual-review-r3-9-mobile-tall.png`
- `assets/visual-review-r3-9-exported-report.json`
- `assets/visual-review-r3-9-release-gate.json`
- `assets/visual-review-r3-9-batch-report.json`
- `assets/visual-review-r3-10-workflow-map-full.png`
- `assets/visual-review-r3-10-mobile-tall.png`
- `assets/visual-review-r3-10-exported-report.json`
- `assets/visual-review-r3-10-batch-report.json`

R3.1 浏览器验证：

- 默认 `Rifle DT Gap` 案例 gate 为 `Blocked`，DT pass 被跳过，finding 包含 unit mismatch、LOD skip、texture、silhouette、bbox、material。
- 切到 `Pistol Clean Variant` 后，5 个 pass 全部 `run`。
- 点击 `Accept Review` 后导出 report，`decisionState=accepted`。
- 导出 report：`reportVersion=visual-review-report@0.1.0`、`fixtureId=pistol_clean`、`gate=Ready`、`imageCount=45`。
- 桌面和移动端截图已确认核心模块可读。

R3.2 浏览器验证：

- `Batch Runner Overview` 显示 3 个 fixture：capture 全部 ok，gate 分布为 1 Ready、1 Review、1 Blocked。
- 点击 batch 行可切回对应 fixture。
- 导出 batch report：`reportVersion=visual-batch-review@0.1.0`、`success=3`、`failed=0`、`blocked=1`。
- 移动端长图已确认 batch summary 单列展示，batch table 保持横向滚动容器。

R3.3 浏览器验证：

- `Signal Thresholds` 展示 4 个 deterministic diff signal。
- 修改 AI draft 后会生成 `draft_edited` audit event。
- 点击 `Needs Fix` 和 `Accept Review` 后会继续写入 audit。
- 导出 report：`reportVersion=visual-review-report@0.2.0`、`diffSignals.length=4`、`reviewAudit.length>=3`。

R3.4 浏览器验证：

- 点击 `Material Drift` signal 后会切到 `White / Blue LOD0` pass，并在 drilldown 内高亮该 signal。
- 点击 `White / Blue DT` pass 后，drilldown 展示 detail cameras、output pattern、linked material/texture findings 和 next action。
- 点击 `Blade Material Shift` batch 行后，batch item detail 展示 primary signal、top findings、first skipped pass 和 report preview。
- 导出 report：`reportVersion=visual-review-report@0.3.0`、`passDrilldowns.length=5`、batch item detail 字段可序列化。

R3.5 浏览器验证：

- `Review Queue Drilldown` 显示 blocked / todo / ready 和 owner split。
- 按 owner / gate 筛选后，队列行保持可选，详情展示 source finding、related passes、next check 和 handoff note。
- 点击 related pass 会跳回 `Pass Drilldown`。
- 点击 `Mark Ready` 会更新 queue state，并向 audit trail 写入 `queue_ready`。
- 导出 report：`reportVersion=visual-review-report@0.4.0`、`reviewQueueSummary`、`reviewQueue` 扩展字段和 audit 可序列化。
- 导出 batch report：`reportVersion=visual-batch-review@0.3.0`，每个 item 带 queue 统计。

R3.6 浏览器验证：

- `Owner Handoff Packet` 展示 artist / TA / reviewer 三类 owner 卡片。
- 点击 `TA` owner 后，消息预览只展示 TA 负责的单位/相机类 action。
- 点击 `Mark Ready` 后，handoff packet 的 queue 统计和 message preview 随当前 queue state 更新。
- 导出 handoff packet：`packetVersion=visual-review-handoff@0.1.0`，`sections.length=3`。
- 导出 report：`reportVersion=visual-review-report@0.5.0`，包含完整 `handoffPacket`。
- 导出 batch report：`reportVersion=visual-batch-review@0.4.0`，每个 item 包含 `handoffOwners` 和 `handoffPreview`。

R3.7 浏览器验证：

- 点击 `Send Packet` 后 owner delivery state 变为 `sent`，audit 写入 `handoff_sent`。
- 点击 `Simulate Fail` 后 state 变为 `failed`，再次 `Send Packet` attempts 递增。
- 点击 `Mark Read` 后 state 变为 `read`，点击 `Acknowledge` 后 state 变为 `acknowledged`。
- 导出 handoff packet：`packetVersion=visual-review-handoff@0.2.0`，包含 `deliverySummary` 和 owner delivery receipt。
- 导出 report：`reportVersion=visual-review-report@0.6.0`，audit 包含 handoff delivery actions。
- 导出 batch report：`reportVersion=visual-batch-review@0.5.0`，每个 item 包含 `handoffDelivery`。

R3.8 浏览器验证：

- 切到 `Pistol Clean Variant`，点击 `Accept Review` 后 final release gate 变为 `Ready`。
- release decision 输出 `release_candidate`，6 个 criteria 全部 `Ready`。
- 导出 release gate：`reportVersion=visual-review-release-gate@0.1.0`。
- 导出 report：`reportVersion=visual-review-report@0.7.0`，包含完整 `releaseGate`。
- 导出 batch report：`reportVersion=visual-batch-review@0.6.0`，每个 item 包含 release gate / decision / preview。

R3.9 浏览器验证：

- 切到 `Pistol Clean Variant`，应用 `DT Blocker` preset 后，variant DT mesh count 变为 0，DT pass 被跳过。
- report gate 变为 `Blocked`，release decision 变为 `blocked_from_release`。
- 导出 report：`reportVersion=visual-review-report@0.8.0`，`fixtureEditSummary.mode=runtime_fixture_editor`，`changedFields` 包含 `variant DT mesh count`。
- 导出 release gate：`reportVersion=visual-review-release-gate@0.1.0`，gate 为 `Blocked`。
- 导出 batch report：`reportVersion=visual-batch-review@0.7.0`，`pistol_clean` item 携带编辑摘要并进入 blocked 统计。

R3.10 浏览器验证：

- `Workflow Map` 显示 6 个 section，默认 `6 / 6 sections open`。
- 点击 `Release Focus` 后只保留 `Setup`、`Triage`、`Handoff`、`Batch` 四段展开。
- 点击 `Capture` 行的 `Show` 后恢复 capture 段，`Signal Thresholds` 重新可见。
- 点击 `Draft` 行的 `Show` 后恢复 AI draft 和 evidence package，`Export Report`、`Export Batch` 保持可用。
- 导出 report：`reportVersion=visual-review-report@0.8.0`，证明 UI polish 未破坏业务报告。
- 导出 batch report：`reportVersion=visual-batch-review@0.7.0`。

R9.4 Maya mayapy 验证：

- 创建 4 个合成 mesh：A/B LOD0 和 A/B DT。
- `visual_review_create_camera_rig()` 返回 `rig_count=10`。
- `visual_review_build_pass_manifest()` 返回 `manifest_gate=Ready`、`passes_run=5`、`passes_skipped=0`、`image_count=50`。
- `visual_review_preview_capture()` 返回 `planned_captures=50`。
- `visual_review_export_report()` 导出：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-4-visual-review-smoke-20260803-155811.json
```

## 下一轮

- 进入 R9.5 Texture Delivery DCC 化：读取 Maya material / file texture path / color space，生成贴图交付 inspection 和 manifest。

