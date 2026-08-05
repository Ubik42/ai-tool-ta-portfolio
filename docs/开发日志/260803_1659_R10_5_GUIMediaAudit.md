# 一.问题反馈

继续执行循环开发。R10.5 的目标是把 R10.4 case page 的 GUI evidence plan 变成可审计的素材回填流程，避免 shotlist 停留在计划层。

# 二.⭐回顾分析

真实 Maya GUI 截图/录屏不能用占位图替代。当前更有价值的第一步，是让工具知道应该收哪些文件、文件应该放在哪里、每个文件是否真的存在、体积是否达到基本阈值，并把结果导出成 public-safe JSON。

# 三.改动解释

- Maya host 新增 `showcase_runbook_audit_gui_media`，默认扫描 `<repo>\assets\dcc-first\r10-5-gui-evidence`。
- Maya host 新增 `showcase_runbook_export_gui_media_audit`，导出 `maya-dcc-gui-media-audit@0.1.0`。
- AuroraView bridge 新增 `showcase_runbook_audit_gui_media` / `showcase_runbook_export_gui_media_audit`。
- `DccFirstCasePage` 新增 `Audit Media` 按钮和 `GUI Media Audit` 结果区，显示 gate、present/review/missing、media root 和每个 expected file。
- public package、DCC-first manifest、README、VALIDATION、Maya host README、长期计划、Runbook / Case Page 模块文档和前端循环队列已同步 R10.5 状态。

最新 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-5-gui-media-audit-20260803-165901.json
```

当前审计结果：

```text
gate: CapturePending
required files: 9
present / review / missing: 0 / 0 / 9
media root: <repo>\assets\dcc-first\r10-5-gui-evidence
```

验证：

```text
npm run build
python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py
Maya 2024 mayapy showcase_runbook_export_gui_media_audit(label="r10-5-gui-media-audit")
manifest / artifact JSON parse and path existence check
```

# 四.计划&状态

R10.5 第一段已完成。下一段继续采集真实 Maya GUI 截图和主流程录屏，让 media audit 从 `CapturePending` 进入 `Ready`。如果继续自动开发，R10.6 可先推进 Asset Handoff Gate 的 owner disposition / repair preview / engine handoff mock。
