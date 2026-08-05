# 一.问题反馈

用户要求长期循环开发，不在未完成时停下；手动操作保留到最后。当前轮选择 Lightbox 高价值提炼中的 Spatial Authoring & Pose Transfer Workbench，目标是把 socket / hotspot / pose frame / mirror / locator preview 从计划推进到 DCC runtime 证据。

# 二.⭐回顾分析

R26 已完成 Character Calibration Maya L3，但 Lightbox 覆盖表中“空间热点、Socket、Pose Transfer、mirror、locator preview”仍停在低覆盖。这个方向的核心价值是把引擎挂点、VFX 热点和姿态迁移的业务事实提前锁在 DCC，而不是等导入引擎后靠人工发现错挂点、错空间、缺 mirror 或缺 owner。

本轮采用 public synthetic fixture，包含一个 approved rifle authoring row 和一个 intentionally blocked backpack row。Blocked row 故意保留 missing joints、world-space socket、large offset、missing mirror pair、bad hotspot owner/semantic、duplicate/out-of-range pose frame、missing preview locator 和 unapproved pose transfer，用于证明工具能解释真实失败路径。

# 三.改动解释

新增 `dcc-hosts/spatial-authoring-workbench` 模块：fixture、contract、Maya collector、headless smoke、Maya L3 runner 和 README。Maya L3 会用 `mayapy` 创建 public synthetic joints / locators / custom attrs，再回读 joint DAG、locator transform 和 payload，输出 `spatial-authoring-maya-l3@0.1.0`。

同步接入 `ai_tool_ta_maya_host.api` 的 Presenter Pack：新增 Spatial Authoring artifact probe、demo route 第 11 步、summary 字段和 reviewer claim。public package 升级到 `ai-tool-ta-dcc-first-showcase-r27` / `dcc-first-package@1.24.0`，R27 Presenter Pack 为 24 / 24 evidence files present、0 missing required files、16 demo route steps。

同步更新 `public-case-package` README、DCC_FIRST_PACKAGE、EVIDENCE_INDEX、VALIDATION、`docs/AI_HANDOFF.md`、模块文档和技术报告，明确 Spatial Authoring 已是 Maya L3，不再是“待开发 fixture”。

# 四.计划&状态

R27 当前结果：

- Spatial Authoring L2 contract：`<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-contract-20260805-181516.json`
- Spatial Authoring Maya L3：`<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-maya-l3-20260805-181524.json`
- R27 Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r27-spatial-authoring-l3-presentation-pack-20260805-181612.json`
- 结果：2 spatial authoring rows，1 Ready，1 intentionally Blocked，11 pass / 2 warning / 7 error。

下一轮默认进入 `Platform Variant Forge`：PC/Mobile policy fixture -> variant plan contract -> preset comparison reuse -> optional Unreal material/LOD fact probe -> Presenter Pack row -> docs -> targeted validation。
