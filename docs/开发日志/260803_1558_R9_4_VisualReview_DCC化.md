# 一.问题反馈

R9.3 已把 Cross-DCC Rule Matrix 接入 Maya scene collect / validate / fix preview。长期目标仍是 DCC-first 作品集，因此下一轮选择 `Visual Review Studio`，把原本浏览器内的 pass matrix、shot manifest、capture report 推进到 Maya 场景上下文。

# 二.⭐回顾分析

Visual Review 的业务秘诀是固定视觉评审变量：相机、LOD 分桶、材质 pass、输出命名、跳过原因和评审证据。第一段 DCC 化不应直接追求真实 playblast，而应先把 Maya 内可复现的 capture contract 建起来：

- Maya 中创建 review camera rig。
- 从 scene mesh 命名推导 LOD0 / DT / other。
- 根据 camera group 和 pass preset 生成 manifest。
- capture preview 先规划输出路径，后续 GUI 再接真实 playblast。
- report 产出 JSON artifact，保证可回放和可复查。

# 三.改动解释

Maya host:

- 在 `ai_tool_ta_maya_host/api.py` 新增 `visual_review_create_camera_rig`、`visual_review_build_pass_manifest`、`visual_review_preview_capture`、`visual_review_export_report`。
- camera rig 创建 basic/detail 两组共 10 个 cameras，并写入 `aiToolTaReviewCamera` 标记。
- pass manifest 支持 5 个 preset：`rb_lod0`、`wb_lod0`、`rb_dt`、`wb_dt`、`solo_b`。
- capture preview 当前只规划输出图片路径，不直接执行 playblast。
- export 输出 `maya-visual-review-dcc-report@1.0.0`。

前端:

- 在 `auroraviewBridge.ts` 注册 4 个 Visual Review Maya API。
- 在 `VisualReviewStudio.tsx` 新增 `Maya Capture Setup` 面板，提供 `Create Rig`、`Build Manifest`、`Preview Capture`、`Export DCC Review` 四个动作。
- 面板展示 cameras、meshes、passes、images、gate、pass rows、output path 和 raw JSON。
- 在 `styles.css` 增加面板样式和移动端收敛。

文档:

- 更新根 README 当前 DCC-first 状态。
- 更新 `docs/260803_DCC-first长期开发计划与环境.md`。
- 更新 `dcc-hosts/maya-auroraview-host/README.md`。
- 更新 `docs/modules/visual-review-studio.md`。

# 四.计划&状态

验证结果：

- `npm run build` 通过，仅保留既有 Vite 大 chunk 警告。
- `python -m py_compile ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` smoke 通过：
  - rig count：10
  - manifest gate：Ready
  - passes run：5
  - passes skipped：0
  - image count：50
  - planned captures：50
  - artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-4-visual-review-smoke-20260803-155811.json
```

下一轮自主推进：

- R9.5 Texture Delivery DCC 化：从 Maya materials / file texture nodes / color space / missing path 中生成 texture inspection、风险校验和交付 manifest。
