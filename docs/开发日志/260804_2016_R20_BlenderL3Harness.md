# 背景

R19 已完成 Maya Scene Transaction Guard，当前作品集主线是 DCC-first / engine-aware 展示。跨 DCC 证据里 Blender 仍只有 L2 contract，因此本轮推进 R20：补一个能进入真实 Blender runtime 的 L3 harness，同时在本机没有 Blender CLI 时输出明确 readiness gate。

# 实现

- 新增 `dcc-hosts/blender-rule-adapter/blender_rule_adapter/bpy_collector.py`：在 Blender runtime 内创建公开 synthetic scene，采集 object custom properties、collections、material slots、textures 和 UV layers，再复用现有 Cross-DCC rule evaluation。
- 新增 `dcc-hosts/blender-rule-adapter/scripts/run_blender_l3.py`：供 `blender --background --python` 调用，成功时导出 `blender-rule-adapter-bpy-l3@0.1.0`。
- 新增 `dcc-hosts/blender-rule-adapter/scripts/run_l3_smoke.py`：普通 Python launcher，先搜索 Blender CLI；找不到时导出 `blender-rule-adapter-l3-readiness@0.1.0`，记录 collector ready、CLI missing、生产写入为 0。
- `MayaPortfolioApi.dcc_presentation_build_pack` 接入 `blender-l3-harness` evidence probe，Presenter Pack demo route 从 10 步升到 11 步，key evidence 从 16 个升到 17 个。
- `DccFirstCasePage`、`public-case-package` manifest、README、VALIDATION、模块文档和技术报告同步到 R20 / `dcc-first-package@1.17.0`。

# 验证

- `python -m py_compile`：Maya API、Blender contract、`bpy_collector.py`、L2/L3 scripts 均通过。
- `python dcc-hosts/blender-rule-adapter/scripts/run_smoke.py`：导出 `blender-rule-adapter-contract-20260804-201125.json`，2 assets，1 Ready，1 Blocked，8 pass，3 warning，1 error。
- `python dcc-hosts/blender-rule-adapter/scripts/run_l3_smoke.py`：导出 `blender-rule-adapter-l3-readiness-20260804-201125.json`，gate `Blocked`，collector ready，Blender CLI missing。
- `npm run build`：TypeScript 和 Vite build 通过，仅保留既有 chunk size warning。
- Maya 2024 `mayapy dcc_presentation_export_pack(label="r20-blender-l3-harness-presentation-pack")`：导出 `r20-blender-l3-harness-presentation-pack-20260804-201419.json`，17 / 17 evidence present，0 missing required，11 demo route steps，overall gate `CapturePending`。

# 下一步

1. 如果安装或定位到 Blender CLI，直接复跑 `python dcc-hosts/blender-rule-adapter/scripts/run_l3_smoke.py`，把 readiness artifact 升级成真实 `blender-rule-adapter-bpy-l3@0.1.0`。
2. 如果短期没有 Blender，优先采集 9 张 Maya GUI 截图和 1 段 route recording，让 R20 Presenter Pack 的 media gate 从 `CapturePending` 进入可审核状态。
3. 后续可选择 Houdini / 3ds Max / MotionBuilder 中一条公开 synthetic fixture，继续扩展非 Maya adapter 覆盖面。
