# 一.问题反馈

继续执行 DCC-first 作品集循环开发。本轮收束 R10.9：把 R10.8 的单 preset engine preflight 扩展为 PC / Mobile preset comparison。用户要求本轮完成后报告当前开发进度并暂停，不继续在边缘点上扩写。

# 二.⭐回顾分析

R10.8 已能证明 Ready intent 需要经过平台 preset 预检才生成 dry-run import sidecar，但它只展示 PC preset。真实管线里同一资产经常会出现 PC 可交付、Mobile 因路径、平台、预算或 LOD 被挡住的情况。R10.9 因此只补平台差异对比，不继续做更细的展示枝节。

# 三.改动解释

- Maya host 新增 `engine_handoff_build_preset_comparison` 和 `engine_handoff_export_preset_comparison`。
- `AssetHandoffGatePanel` 新增 `Preset Compare` 按钮，并展示 preset summary 与 per-asset comparison rows。
- `auroraviewBridge` 已加入 preset comparison API 白名单。
- public package 升级为 `ai-tool-ta-dcc-first-showcase-r10-9` / `dcc-first-package@1.7.0`。
- README、Maya host README、Asset Handoff Gate 模块文档、长期计划、VALIDATION 和 public package 清单已同步。

最新 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-9-engine-preset-comparison-20260803-172927.json
```

# 四.计划&状态

已验证：

- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
- `npm run build`
- Maya 2024 `mayapy` preset comparison smoke：2 presets，2 comparison rows，1 platform split，1 held-across-presets，1 ready sidecar，0 engine writes。

暂停点：

1. 当前作品集已经具备 DCC 内完整主线：5 个模块、Composite Handoff Gate、Owner / Engine Decision、Engine Preflight、PC/Mobile preset comparison。
2. 下一步不要继续扩边缘小功能，优先做真实 Maya GUI 截图/录屏证据和最终演示收束。
3. 如果继续开发，R10.10 只建议做 owner disposition drill；之后进入 R11 展示稳定化。
