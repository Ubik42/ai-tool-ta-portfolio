# 一.问题反馈

上一轮已经把 engine preflight 和 PC/Mobile preset comparison 接入 DCC 证据链。本轮不继续扩展 owner drill 等边缘功能，改为收束展示入口：作品集最终需要在 Maya/AuroraView 内可复现、可导出、可验收。

# 二.⭐回顾分析

R10.7 case page、GUI media audit、Asset Handoff Gate、Decision Packet、R10.8 Engine Preflight、R10.9 Preset Comparison 已经足够支撑核心业务主线。当前短板不是业务逻辑不足，而是最终展示交付对象还不集中：reviewer 需要知道从 Maya 怎么进入、看哪些证据、哪些 JSON 已存在、真实 GUI 媒体还缺什么。

因此 R11 选择做 DCC Presenter Pack：把 case page 和关键 artifact 探测收束成一个 Maya 内导出的展示包，同时明确保持 `CapturePending`，不伪装 GUI 截图/录屏已完成。

# 三.改动解释

- Maya API 新增 `dcc_presentation_build_pack` / `dcc_presentation_export_pack`，导出 `maya-dcc-presentation-pack@0.1.0`。
- Presenter Pack 会探测 11 个关键证据文件：public manifest、DCC package readme、Maya host readme、case page、runbook、GUI evidence manifest、GUI media audit、Asset Handoff Gate、Decision Packet、Engine Preflight、Engine Preset Comparison。
- React `DccFirstCasePage` 升级为 `R11 DCC Presenter Pack`，新增 `Presenter Pack` 按钮和导出结果区，展示 gate、evidence present/missing、GUI media present/review/missing 和 artifact path。
- public package 升级到 `ai-tool-ta-dcc-first-showcase-r11` / `dcc-first-package@1.8.0`，总体 gate 调整为 `CapturePending`，source case gate 保留 `Review`。
- 同步更新 root README、Maya host README、DCC-first package、validation ledger、case page module doc、长期开发计划和 frontend sprint queue。

# 四.计划&状态

本轮验证：

- `npm run build` 通过，仅保留既有 Vite 大 chunk warning。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy dcc_presentation_export_pack(label="r11-dcc-presentation-pack")` 通过。
- manifest/artifact consistency 通过。

最终 R11 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r11-dcc-presentation-pack-20260803-174307.json
```

当前状态：

- package：`ai-tool-ta-dcc-first-showcase-r11` / `dcc-first-package@1.8.0`
- report：`maya-dcc-presentation-pack@0.1.0`
- gate：`CapturePending`
- evidence files：11 present / 0 missing required
- GUI media：0 present / 0 review / 10 missing
- demo route：6 steps

下一步只建议推进真实 Maya GUI 截图/录屏采集和展示 polish，暂停继续追加 owner drill 等边缘业务功能。
