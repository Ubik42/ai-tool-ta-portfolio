# DCC-first Case Page / Presenter Pack

R32 当前目标：保留 R10.7 case page 作为核心案例报告，同时用 Maya 内一键导出的 Cross-DCC / Engine Reviewer Pack，把 case page、GUI media audit、handoff decision、engine preflight、preset comparison、Animation Continuity Maya L3、Unreal Animation Bridge import L3、Character Calibration Maya L3、Spatial Authoring Maya L3、Platform Variant Forge、Platform Variant Unreal Runtime Probe、Platform Variant Generation Planner、Platform Variant Texture Runtime Collector、Platform Variant Public Texture2D Payload Fixture、Blender bpy L3 runtime、3ds Max pymxs L3 runtime、Unreal Python L3++ engine fact evidence、Unreal preset fact / waiver comparison、Maya-hosted preset fact reviewer queue、Scene Transaction Guard 和 public package manifest 收束成可投递展示包。

## 核心业务逻辑

这个页面解决的是作品集展示的最后一公里：TA 工具不是只证明“能点按钮”，还要证明一条资产从作者协议到交付门禁的业务链路能被复盘。

- Case thesis：说明这是 Maya-hosted AI Tool TA portfolio，不是浏览器 dashboard。
- DCC entry：给出 Maya Script Editor / shelf 入口。
- Business route：按资产交付逻辑组织 7 段流程。
- Composite gate：把 Asset Handoff Gate 的 Ready / Review / Blocked 作为最终业务判定。
- Owner / Engine decision：把 repair preview、owner disposition、engine handoff mock 放进主案例。
- Media plan：把 9 张截图和 1 段录屏变成明确采集清单。
- Presenter Pack：探测 29 个关键证据文件是否存在，并把总体 gate 压成 `CapturePending` / `Review` / `Ready`。
- Preset Fact Review：把 Unreal preset comparison 的 blocked / drift / waived / matched rows 投影成 Maya 内 reviewer queue。
- Scene Transaction Guard：把 Maya 工具运行前后的 scene mutation 输出为 fingerprint、risk rows 和 rollback preview。

## 当前实现

代码入口：

- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
- `showcases/portfolio-site/src/components/DccFirstCasePage.tsx`
- `showcases/portfolio-site/src/lib/auroraviewBridge.ts`

Maya API：

- `showcase_runbook_build_case_page`
- `showcase_runbook_export_case_page`
- `showcase_runbook_audit_gui_media`
- `showcase_runbook_export_gui_media_audit`
- `asset_handoff_export_decision_packet`
- `dcc_presentation_build_pack`
- `dcc_presentation_export_pack`
- `unreal_preset_fact_review_load`
- `unreal_preset_fact_review_export`
- `scene_transaction_export_receipt`

React 入口：

- `Task Orchestrator` 证据视图顶部的 `R32 Cross-DCC / Engine Reviewer Pack`
- `Export Case Page` 按钮
- `Presenter Pack` 按钮
- `Preset Facts` 按钮
- `Txn Guard` 按钮
- 7 段 business route
- Composite Gate 摘要
- Owner / Engine Decision 摘要
- Evidence artifact rows：case page、handoff、decision、GUI manifest、engine preflight、engine preset comparison、Animation Continuity Lab、Unreal Animation Bridge、Character Calibration、Spatial Authoring、Platform Variant Forge、Platform Variant Unreal Runtime Probe、Platform Variant Generation Planner、Platform Variant Texture Runtime Collector、Platform Variant Public Texture2D Payload Fixture、Blender rule adapter、Blender L3 harness、3ds Max rule adapter、3ds Max L3 harness、Unreal handoff inspector、Unreal preset fact comparison、Unreal preset fact review、Scene Transaction Guard
- GUI evidence plan
- GUI media audit
- Presenter Pack evidence file probes
- Asset Handoff Decision Packet artifact row

## 验证结果

- `npm run build` 通过。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` case page smoke 通过：
  - report version：`maya-dcc-portfolio-case-page@1.1.0`
  - sections：6
  - business route steps：7
  - live demo script steps：7
  - GUI shots：9
  - GUI recordings：1
  - handoff assets：2
  - handoff ready/review/blocked：1 / 1 / 0
  - decision repair actions：2
  - decision owner required：1
  - decision engine ready/held：1 / 1
  - supporting artifacts：4
- Maya 2024 `mayapy` media audit smoke 通过：
  - report version：`maya-dcc-gui-media-audit@0.2.0`
  - gate：`CapturePending`
  - required files：10
  - present/review/missing：0 / 0 / 10
- Maya 2024 `mayapy` handoff decision smoke 通过：
  - report version：`maya-asset-handoff-decision-packet@0.1.0`
  - repair actions：2
  - owner dispositions：2
  - engine ready/held：1 / 1
- Maya 2024 `mayapy` presenter pack smoke 通过：
  - report version：`maya-dcc-presentation-pack@0.1.0`
  - package：`ai-tool-ta-dcc-first-showcase-r32` / `dcc-first-package@1.29.0`
  - gate：`CapturePending`
  - demo route steps：21
  - key evidence files：29
  - present/missing required evidence files：29 / 0
  - Animation Continuity：L3 / `Blocked` / `maya_anim_curves_collected`
  - Animation Continuity assets ready/blocked：1 / 1
  - Unreal Animation Bridge：L3 / `Blocked` / `unreal_animsequence_assets_imported`
  - Unreal Animation Bridge assets ready/review/blocked：1 / 0 / 1
  - Character Calibration：L3 / `Blocked` / `maya_character_calibration_collected`
  - Character Calibration assets ready/review/blocked：1 / 0 / 1
  - Spatial Authoring：L3 / `Blocked` / `maya_spatial_authoring_collected`
  - Spatial Authoring assets ready/review/blocked：1 / 0 / 1
  - Platform Variant Forge：L3-linked / `Blocked` / `platform_variant_plan_joined_to_unreal_facts`
  - Platform Variant Forge variants ready/review/blocked：2 / 0 / 1
  - Platform Variant Unreal Runtime Probe：L3 / `Blocked` / `unreal_variant_runtime_assets_collected`
  - Platform Variant Unreal Runtime variants ready/review/blocked：0 / 2 / 1
  - Platform Variant Unreal Runtime checks pass/warn/error：21 / 4 / 2
  - Platform Variant Generation Planner：L3-derived / `Blocked` / `runtime_drift_to_generation_plan`
  - Platform Variant Generation operations ready/review/blocked/satisfied：1 / 3 / 2 / 5
  - Platform Variant Texture Runtime Collector：L3 / `Blocked` / `unreal_material_texture_facts_collected`
  - Platform Variant Texture Runtime variants ready/review/blocked：1 / 1 / 1
  - Platform Variant Texture Runtime checks pass/warn/error：19 / 1 / 1
  - Platform Variant Public Texture2D Payload Fixture：L3 / `Blocked` / `unreal_texture_payload_fixture_collected`
  - Platform Variant Texture Payload variants ready/review/blocked：2 / 0 / 1
  - Platform Variant Texture Payload checks pass/warn/error：20 / 0 / 1
  - Blender adapter：L3 / `Blocked` / `bpy_scene_collected`
  - 3ds Max adapter：L3 / `Blocked` / `pymxs_scene_collected`
  - Animation/Max/Blender/Platform gate 的 `Blocked` 来自 synthetic fixture 中故意保留的失败资产、平台阻断或 runtime drift，不是 runtime 缺失
  - Unreal inspector：L3++ / `unreal_engine_facts_matched`
  - Unreal engine facts：4 / 4 matched
  - Unreal preset fact rows matched/drift/waived/blocked：7 / 1 / 1 / 1
  - Unreal preset review rows / queue / blocked / waivers：10 / 3 / 1 / 1
  - Scene transaction gate / rollback / risk rows：Review / 9 / 4
  - GUI media present/review/missing：0 / 0 / 10

## 当前 artifact

Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r32-platform-variant-texture-payload-presentation-pack-20260805-194432.json
```

Platform Variant Unreal Runtime Probe：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-unreal-runtime-20260805-185026.json
```

Platform Variant Generation Planner：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-generation-plan-20260805-190052.json
```

Platform Variant Texture Runtime Collector：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-runtime-20260805-191529.json
```

Platform Variant Public Texture2D Payload Fixture：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-payload-runtime-20260805-193515.json
```

Unreal Animation Bridge：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-import-l3-20260805-173309.json
```

Animation Continuity Lab：

```text
<repo>\dcc-hosts\animation-continuity-lab\artifacts\animation-continuity-maya-l3-20260805-162744.json
```

Character Calibration：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json
```

Spatial Authoring：

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-maya-l3-20260805-181524.json
```

Scene Transaction Guard：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-20260804-195730.json
```

Unreal preset fact review：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json
```

Unreal inspector：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

Unreal preset fact comparison：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

Blender adapter：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260804-201125.json
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json
```

3ds Max adapter：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
```

3ds Max L3 runtime：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260805-153232.json
```

Case page：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
```

Supporting artifacts：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
```

Media audit：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```

Handoff decision packet：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
```

## 下一轮

下一轮优先扩展 Unreal AnimSequence/Skeleton public fixture、Character Calibration 或 Spatial Authoring，并采集 Maya GUI 截图/录屏，让 media audit 从 `CapturePending` 进入可审核状态。
