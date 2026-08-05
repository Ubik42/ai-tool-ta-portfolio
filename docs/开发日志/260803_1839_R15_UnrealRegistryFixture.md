# 一.问题反馈

持续循环开发要求作品集不要停在 Maya-first 或前端壳展示。本轮接 R14 继续推进 Unreal Handoff Inspector：R14 已经能在 Unreal Python runtime 内执行并查询 Asset Registry，但 `/Game` 仍为空，证据还缺少真实引擎资产行。

# 二.⭐回顾分析

R14 的价值是证明 inspector 进入了 Unreal runtime；R15 的价值是证明它不只是“打开 Unreal 查空 registry”，而是可以在公开 test project 中创建可被 Content Registry 识别的资产，再用机器可读 artifact 记录 path/class 匹配结果。

这更贴近真实工具管线 TA 的业务秘诀：DCC 侧 Ready 只说明可以生成 import intent，引擎侧还要验证目标路径、资产类型、现有资产、依赖、LOD/collision 和 owner state。当前 R15 先把最关键的 registry path/class 对比闭合，后续再读取 import data、material slot、LOD count 和 collision settings。

# 三.改动解释

升级 Unreal Handoff Inspector：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\unreal_handoff_inspector\contract.py
<repo>\dcc-hosts\unreal-handoff-inspector\scripts\unreal_python\run_l3_inspection.py
<repo>\dcc-hosts\unreal-handoff-inspector\scripts\run_unreal_l3_smoke.py
```

新增公开 StaticMesh 源文件：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\fixtures\unreal_sources\SM_HeroPanel_A.obj
```

Unreal Python smoke 现在会在公开 test project 内：

- 导入 `SM_HeroPanel_A.obj`，生成 `/Game/AI_Tool_TA/Props/SM_HeroPanel_A` StaticMesh。
- 创建 `/Game/AI_Tool_TA/Materials/M_HeroPanel` Material。
- 查询 Asset Registry。
- 对 2 条 expected rows 做 path/class 匹配。
- 把结果写入 `unrealRegistryEvidence`。

最终 Unreal artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-183417.json
```

结果：

```text
reportVersion: unreal-handoff-inspector-contract@0.3.0
evidenceLevel: L3+
l3Status: unreal_registry_fixture_matched
registry matched: 2 / 2
missing: 0
class mismatch: 0
Unreal runtime: 5.3.2
Python: 3.9.7
intent ready / blocked: 1 / 1
checks pass / review / blocked: 14 / 2 / 4
```

更新 public package / Presenter Pack / Maya API / React UI / 文档到 R15：

```text
ai-tool-ta-dcc-first-showcase-r15
dcc-first-package@1.12.0
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r15-unreal-registry-fixture-presentation-pack-20260803-183547.json
```

验证已执行：

```text
python -m py_compile ...
python -m json.tool ...
npm run build
python dcc-hosts/unreal-handoff-inspector/scripts/run_smoke.py
python dcc-hosts/unreal-handoff-inspector/scripts/run_unreal_l3_smoke.py
Maya 2024 mayapy dcc_presentation_export_pack(label="r15-unreal-registry-fixture-presentation-pack")
PowerShell R15 manifest / artifact / uasset consistency assertion
```

# 四.计划&状态

当前完成度：DCC / 引擎展示主线约 88%。Maya 内宿主、核心业务模块、跨 DCC L2、Unreal L3+ registry fixture、public package、Presenter Pack 和一致性验证都已闭合。

下一轮推荐顺序：

1. Unreal L3++：读取 StaticMesh source import data、material slot、LOD count 和 collision settings，把 registry path/class 匹配升级为更完整的 engine import contract。
2. Blender L3：定位或安装 Blender CLI，运行 `blender --background --python`，把 Blender Rule Adapter 从 L2 contract 推到真实 `bpy` evidence。
3. Maya GUI evidence：采集 Maya 内 AuroraView 9 张截图和 1 段主路线录屏，让 media audit 从 `CapturePending` 进入可审核状态。
