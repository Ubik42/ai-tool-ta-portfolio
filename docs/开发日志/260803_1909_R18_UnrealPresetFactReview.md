# 一.问题反馈

用户要求设置长期任务和持续开发框架，并让 Codex 循环任务持续开发 `AIToolTA_Portfolio`。本轮承接前序 Lightbox 高价值提炼，继续把作品集从前端展示拉回 DCC / 引擎内展示。

当前环境检查结果：

- heartbeat 自动化 `ai-tool-ta-portfolio-dcc` 已存在并处于 `ACTIVE`，每 2 小时回到当前 task。
- R17 baseline 已存在：`ai-tool-ta-dcc-first-showcase-r17` / `dcc-first-package@1.14.0`。
- Blender CLI 当前未在 PATH 和常见安装目录中找到，本轮不在安装/定位 Blender 的边缘点上消耗时间。

# 二.⭐回顾分析

R17 已完成 Unreal preset fact comparison：基于 Unreal L3++ engine facts，对 PC / Mobile preset policy、path prefix、source import data、material slot、LOD count、collision policy 和 exception waiver 做比较。结果是 10 条 fact rows：7 matched、1 drift、1 waived、1 blocked；PC 单 LOD 是 approved waiver，Mobile path/LOD 仍然 blocked/drift。

问题是 R17 仍偏 JSON artifact。对作品集演示来说，更高价值的是在 Maya/AuroraView 里展示 reviewer 如何直接看到：

- 哪个平台阻断。
- 哪条是 drift。
- 哪条是 approved waiver。
- 每条 row 应该 accept、owner review、verify waiver，还是 hold engine import。

因此本轮选择 R18：把 Unreal preset comparison 投影成 Maya-hosted reviewer queue，而不是继续扩写边缘 owner drill，也不等待 Blender 环境。

# 三.改动解释

后端：

- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
  - 新增 `unreal_preset_fact_review_load`。
  - 新增 `unreal_preset_fact_review_export`。
  - 新增 review row action 映射：matched -> accept，waived -> verify waiver owner and expiry，drift -> send to owner for preset policy decision，blocked -> hold engine import until policy is fixed。
  - `dcc_presentation_build_pack` 新增 `unreal-preset-fact-review` required evidence probe。
  - Presenter Pack demo route 从 8 段升级到 9 段。

前端：

- `showcases/portfolio-site/src/lib/auroraviewBridge.ts`
  - 新增 `unreal_preset_fact_review_load` / `unreal_preset_fact_review_export` bridge 方法。
- `showcases/portfolio-site/src/components/DccFirstCasePage.tsx`
  - 顶部新增 `Preset Facts` 按钮。
  - 新增 `Unreal Preset Fact Review` 面板，展示 gate、rows/queue、matched/drift/waived/blocked、preset summary、asset platform split、每条 fact row 的 actual/expected/action/waiver。
  - 页面当前态升级为 R18 Cross-DCC / Engine Reviewer Pack。
- `showcases/portfolio-site/src/styles.css`
  - 新增 blocked/drift/waived/matched 状态样式。
  - 新增 reviewer fact list 紧凑布局和窄屏响应式约束。

证据包：

- 新增 R18 review artifact：
  `<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json`
- 新增 R18 Presenter Pack：
  `<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-presentation-pack-20260803-190613.json`
- public package 升级到：
  `ai-tool-ta-dcc-first-showcase-r18` / `dcc-first-package@1.15.0`

文档：

- 更新根 `README.md` 当前状态。
- 更新 `public-case-package/README.md`、`DCC_FIRST_PACKAGE.md`、`VALIDATION.md`。
- 更新 `dcc-hosts/maya-auroraview-host/README.md`。
- 更新 `docs/modules/dcc-first-case-page.md`、`docs/modules/unreal-handoff-inspector.md`。
- 更新 `docs/260803_DCC-first长期开发计划与环境.md` 和 `docs/技术报告/260803_1801_跨DCC引擎持续开发框架.md`。

# 四.计划&状态

验证结果：

- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- `npm run build` 通过。
- Maya 2024 `mayapy` 导出 `unreal_preset_fact_review_export(label="r18-unreal-preset-fact-review")` 通过。
- R18 review artifact summary：10 rows，3 review queue，7 matched，1 drift，1 waived，1 blocked，1 approved waiver。
- Maya 2024 `mayapy` 导出 `dcc_presentation_export_pack(label="r18-unreal-preset-fact-review-presentation-pack")` 通过。
- R18 Presenter Pack summary：15 / 15 evidence present，0 missing required，9 demo route steps，gate 为 `CapturePending`。

下一轮优先级：

1. Blender L3：安装或定位 Blender CLI，把 `blender-rule-adapter` 从 L2 contract 推到真实 `blender --background --python` smoke。
2. GUI media：采集 9 张 Maya 截图和 1 段 route recording，让 media audit 从 `CapturePending` 进入可审核状态。
3. Presentation polish：用 R18 Reviewer Pack 作为最终入口检查 Maya 内文字密度、路径显示和 reviewer 读取顺序。
