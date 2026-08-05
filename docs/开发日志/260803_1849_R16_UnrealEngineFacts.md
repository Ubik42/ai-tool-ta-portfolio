# 一.问题反馈

用户要求作品集不要停留在前端展示，要继续围绕 Lightbox 高价值业务逻辑做 DCC / 引擎内可展示工具。当前循环需要把 Unreal 证据从“能调起 Unreal 和查 Asset Registry”继续推到更接近真实 TA 交付判断的 engine facts。

# 二.⭐回顾分析

R15 已完成 L3+ registry fixture：公开 test `.uproject` 内能生成 `SM_HeroPanel_A` StaticMesh 和 `M_HeroPanel` Material，并验证 2 / 2 Asset Registry path-class rows matched。

R16 的价值是把判断从“资产存在且类型正确”推进到“引擎实际消费到的关键事实正确”：source import data、material slot assignment、LOD count、collision settings。这更接近资产交付到 Unreal 后 TA 会排查的真实问题。

# 三.改动解释

- `unreal-handoff-inspector-contract` 升级到 `@0.4.0`。
- `run_l3_inspection.py` 在 Unreal Python 中读取 StaticMesh engine facts，并在需要时把 `M_HeroPanel` 绑定到 slot 0。
- Unreal artifact 新增 `unrealEngineFactEvidence`，4 / 4 facts matched 后 evidence level 升级为 `L3++`，`l3Status=unreal_engine_facts_matched`。
- Maya Presenter Pack、public package manifest、case page 数据和模块文档同步到 R16 / `dcc-first-package@1.13.0`。
- 长期循环框架改为 DCC / 引擎通用闭环，不再把完成标准写死为 Maya-only。

核心 artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r16-unreal-engine-facts-presentation-pack-20260803-184326.json
```

验证已通过：

```text
python -m json.tool public-case-package\dcc-first-package-manifest.json
python -m json.tool public-case-package\package-manifest.json
python -m json.tool dcc-hosts\unreal-handoff-inspector\projects\AI_Tool_TA_Unreal_L3\AI_Tool_TA_Unreal_L3.uproject
python -m py_compile dcc-hosts\maya-auroraview-host\ai_tool_ta_maya_host\api.py dcc-hosts\unreal-handoff-inspector\unreal_handoff_inspector\contract.py dcc-hosts\unreal-handoff-inspector\scripts\run_smoke.py dcc-hosts\unreal-handoff-inspector\scripts\run_unreal_l3_smoke.py dcc-hosts\unreal-handoff-inspector\scripts\unreal_python\run_l3_inspection.py
npm run build
R16 manifest / artifact / Presenter Pack consistency check
```

一致性结果：

```text
package: ai-tool-ta-dcc-first-showcase-r16
version: dcc-first-package@1.13.0
unrealEvidence: L3++
engineFacts: 4/4
presenterEvidenceFiles: 13
presenterMissingRequiredFiles: 0
```

# 四.计划&状态

当前状态：R16 完成。Unreal 线已从 L2 contract、L3 runtime、L3+ registry fixture 推进到 L3++ engine facts。

下一轮优先级：

1. 把 R16 Unreal engine facts 接到 PC / Mobile preset comparison 和 exception waiver policy，对比“preset 期望”和“引擎实际事实”。
2. 安装 Blender 后推进 `Blender Rule Adapter` 到真实 `blender --background --python` L3 smoke。
3. 采集 Maya GUI 截图/录屏，让 Presenter Pack 的 media gate 从 `CapturePending` 进入可审核状态。

当前目录不是 git 仓库，`git status --short` 返回 `fatal: not a git repository`。
