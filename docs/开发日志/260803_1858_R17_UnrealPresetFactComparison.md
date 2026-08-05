# 一.问题反馈

当前长期目标要求作品集继续围绕 Lightbox 高价值业务逻辑做跨 DCC / 引擎可展示证据。R16 已经能从 Unreal 读取 StaticMesh runtime facts，但还缺少“平台 preset 期望 vs 引擎实际事实 vs waiver 边界”的决策层。

# 二.⭐回顾分析

R16 的 L3++ artifact 已证明 Unreal 5.3.2 / Python 3.9.7 中真实读取了 `SM_HeroPanel_A` 的 source import data、material slot、LOD count 和 collision settings，4 / 4 facts matched。

真实 TA 交付中，读到事实不是终点。更核心的问题是：这些事实放到 PC / Mobile 平台策略下是否能通过，哪些偏差可以通过 owner-scoped waiver 进入 Review，哪些必须继续阻断。R17 因此把 engine facts 接到 preset policy 和 exception waiver。

# 三.改动解释

- `synthetic_unreal_handoff.json` 新增 PC / Mobile `pathPrefix` 和 `exceptionWaivers`。
- `unreal_handoff_inspector.contract` 新增 `unreal-preset-fact-comparison@0.1.0` 生成逻辑。
- 新增 `scripts/run_preset_fact_compare.py`，读取 R16 L3++ artifact 并导出 preset/fact comparison。
- public package 升级到 `ai-tool-ta-dcc-first-showcase-r17` / `dcc-first-package@1.14.0`。
- Presenter Pack 接入第 14 个 required evidence file：Unreal Preset Fact Comparison。
- 前端 DCC-first case page 增加 R17 label 和 preset fact summary。
- 更新 README、public package、module docs、长期开发计划、技术报告和 heartbeat automation。

核心 artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r17-unreal-preset-facts-presentation-pack-20260803-185425.json
```

R17 结果：

```text
report: unreal-preset-fact-comparison@0.1.0
gate: Blocked
presets: 2
asset count: 1
fact rows: 10
matched / drift / waived / blocked: 7 / 1 / 1 / 1
platform split: 1
approved waivers: 1
presenter pack evidence files: 14 / 14
```

验证已通过：

```text
python -m json.tool dcc-hosts\unreal-handoff-inspector\fixtures\synthetic_unreal_handoff.json
python -m json.tool public-case-package\dcc-first-package-manifest.json
python -m json.tool public-case-package\package-manifest.json
python -m json.tool dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
python -m json.tool dcc-hosts\maya-auroraview-host\artifacts\r17-unreal-preset-facts-presentation-pack-20260803-185425.json
python -m py_compile dcc-hosts\maya-auroraview-host\ai_tool_ta_maya_host\api.py dcc-hosts\unreal-handoff-inspector\unreal_handoff_inspector\contract.py dcc-hosts\unreal-handoff-inspector\unreal_handoff_inspector\__init__.py dcc-hosts\unreal-handoff-inspector\scripts\run_smoke.py dcc-hosts\unreal-handoff-inspector\scripts\run_unreal_l3_smoke.py dcc-hosts\unreal-handoff-inspector\scripts\run_preset_fact_compare.py dcc-hosts\unreal-handoff-inspector\scripts\unreal_python\run_l3_inspection.py
python dcc-hosts\unreal-handoff-inspector\scripts\run_preset_fact_compare.py
Maya 2024 mayapy dcc_presentation_export_pack(label="r17-unreal-preset-facts-presentation-pack")
npm run build
R17 manifest / artifact / Presenter Pack consistency check
```

# 四.计划&状态

当前状态：R17 完成。Unreal 线已经从 L2 contract、L3 runtime、L3+ registry fixture、L3++ engine facts 推进到 preset fact / waiver comparison。

下一轮优先级：

1. 定位或安装 Blender CLI，把 `Blender Rule Adapter` 从 L2 contract 升级到真实 `blender --background --python` L3 smoke。
2. 或者把 R17 Unreal preset fact comparison 做成 Maya 内 reviewer 面板，减少 reviewer 打开 JSON 的成本。
3. 采集 Maya GUI 截图/录屏，让 Presenter Pack media gate 从 `CapturePending` 进入可审核状态。

当前目录不是 git 仓库，`git status --short` 返回 `fatal: not a git repository`。
