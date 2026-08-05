# 一.问题反馈

本轮处理两个关键问题：用户已安装 Blender 并批准 3ds Max runtime，因此需要把 R20/R21 的 readiness 证据升级成真实 DCC runtime L3；同时 Maya GUI 不能长期依赖每次在 Script Editor 粘贴 `show_portfolio()`，需要补外部控制入口。

# 二.⭐回顾分析

Blender / Max 的高价值不在“能打开软件”，而在 DCC 特有事实能否稳定进入同一套发布规则。Blender 侧是 custom properties、collections、material slots、UV layers、collision proxy；3ds Max 侧是 user properties、layer/export root、LOD suffix、material slot、map channel、transform、collision proxy。这些事实都应该被归一化为 `cross-dcc-rule-input@0.1.0`，再进入 Ready / Review / Blocked 门禁。

Maya GUI 的正确使用方式分三层：临时测试可以在 Script Editor 执行一次 `show_portfolio()`；长期使用应安装 shelf；需要外部自动化时，先在 Maya 会话里启动 command bridge，再由外部 shell 给 Maya 发命令。

# 三.改动解释

新增 Maya 外控入口：

- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/external_control.py`
- `dcc-hosts/maya-auroraview-host/scripts/start_maya_command_bridge.py`
- `dcc-hosts/maya-auroraview-host/scripts/send_maya_command.py`
- `shelf/install_shelf_button.py` 新增 `TA Bridge` 按钮，默认监听 `127.0.0.1:7107`。

同步 R22 证据：

- Blender L3：`blender-rule-adapter-bpy-l3@0.1.0`，`bpy_scene_collected`，Blender 5.2.0 LTS background。
- 3ds Max L3：`max-rule-adapter-pymxs-l3@0.1.0`，`pymxs_scene_collected`，3ds Max 2022 batch。
- Public package 升级到 `ai-tool-ta-dcc-first-showcase-r22` / `dcc-first-package@1.19.0`。
- Maya Presenter Pack 默认标签升级到 `r22-blender-max-l3-presentation-pack`。
- 文档同步：public package README / DCC_FIRST / VALIDATION、module docs、长期计划、技术报告。

# 四.计划&状态

本轮验证已完成：

- `python dcc-hosts/blender-rule-adapter/scripts/run_l3_smoke.py`：导出 `blender-rule-adapter-l3-20260805-153156.json`，2 assets，1 Ready，1 Blocked，8 pass，3 warning，1 error。
- `python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py --run-runtime --timeout-seconds 600`：导出 `max-rule-adapter-l3-20260805-153232.json`，runtime collected true，object count 4，13 pass，5 warning，2 error。
- Maya 2024 `mayapy dcc_presentation_export_pack(label="r22-blender-max-l3-presentation-pack")`：导出 `r22-blender-max-l3-presentation-pack-20260805-153957.json`，19 / 19 evidence files present，0 missing required files，12 demo route steps。

关键 artifact：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260805-153232.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r22-blender-max-l3-presentation-pack-20260805-153957.json
```

下一轮入口：

1. 采集 Maya GUI 9 张 PNG 和 1 段 MP4，让 media gate 从 `CapturePending` 进入可审核。
2. 开发 `Animation Continuity Lab`：animation intent schema、headless fixture、Maya animation fact collector。
3. 后续扩 MotionBuilder / Unreal runtime 对照，再进入 Character Calibration 和 Spatial Authoring。
