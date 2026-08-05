# DCC-first Public Package

This is the current reviewer entry point for the AI Tool TA portfolio.

The portfolio is now demonstrated inside Maya through AuroraView. The browser build remains the embedded UI surface and evidence browser; the primary proof is the Maya-hosted R30 Cross-DCC / Engine / Animation / Character / Spatial / Platform Variant Generation Reviewer Pack.

## Current Package

| Field | Value |
| --- | --- |
| Package | `ai-tool-ta-dcc-first-showcase-r30` |
| Version | `dcc-first-package@1.27.0` |
| Source report | `maya-dcc-portfolio-case-page@1.1.0` |
| Gate | `CapturePending` |
| Modules | 5 |
| DCC artifacts | 15 |
| Case page sections | 6 |
| Case page artifacts | 6 |
| Business route steps | 7 |
| Presenter pack report | `maya-dcc-presentation-pack@0.1.0` |
| Presenter pack evidence files | 27 / 27 present |
| Presenter pack missing required files | 0 |
| Presenter demo route steps | 19 |
| GUI evidence shots | 9 |
| GUI evidence recordings | 1 |
| GUI media audit | `CapturePending` |
| GUI media present/review/missing | 0 / 0 / 10 |
| Asset handoff gate | `Review` |
| Asset handoff assets | 2 |
| Handoff decision repair actions | 2 |
| Handoff owner dispositions | 2 |
| Engine handoff ready/held | 1 / 1 |
| Engine preflight gate | `Review` |
| Engine preflight ready/held | 1 / 1 |
| Engine import sidecars | 1 |
| Engine preset comparison | `Review` |
| Platform split / held across presets | 1 / 1 |
| Blender rule adapter | `Blocked` L3 |
| Blender adapter assets ready/blocked | 1 / 1 |
| Blender adapter checks pass/warn/error | 8 / 3 / 1 |
| Blender L3 harness | `Blocked`, `bpy_scene_collected`, Blender 5.2.0 LTS |
| 3ds Max rule adapter | `Blocked` L3 |
| 3ds Max adapter assets ready/review/blocked | 1 / 0 / 1 |
| 3ds Max adapter checks pass/warn/error | 13 / 5 / 2 |
| 3ds Max L3 harness | `Blocked`, `pymxs_scene_collected`, 3ds Max 2022 batch |
| Unreal handoff inspector | `Blocked` L3++ |
| Unreal inspector import ready/blocked | 1 / 1 |
| Unreal inspector checks pass/review/blocked | 14 / 2 / 4 |
| Unreal registry fixture matched | 2 / 2 |
| Unreal engine facts matched | 4 / 4 |
| Unreal preset fact comparison | `Blocked` |
| Unreal preset fact rows matched/drift/waived/blocked | 7 / 1 / 1 / 1 |
| Unreal preset platform split / approved waivers | 1 / 1 |
| Unreal preset fact review | `Blocked` |
| Unreal preset review rows / queue / waivers | 10 / 3 / 1 |
| Scene transaction guard | `Review` |
| Scene transaction created/deleted/modified | 2 / 2 / 2 |
| Scene transaction rollback/risk rows | 9 / 4 |
| Animation continuity | `Blocked` L3 |
| Animation continuity assets ready/review/blocked | 1 / 0 / 1 |
| Animation continuity checks pass/warn/error | 11 / 3 / 6 |
| Animation continuity runtime | `maya_anim_curves_collected`, Maya 2026 batch |
| Unreal animation bridge | `Blocked` L3 |
| Unreal animation bridge assets ready/review/blocked | 1 / 0 / 1 |
| Unreal animation bridge checks pass/warn/error | 12 / 1 / 5 |
| Unreal animation bridge runtime | `unreal_animsequence_assets_imported`, Unreal 5.3.2, 2 / 2 sequences present, 4 synthetic assets imported |
| Character calibration | `Blocked` L3 |
| Character calibration assets ready/review/blocked | 1 / 0 / 1 |
| Character calibration checks pass/warn/error | 10 / 2 / 6 |
| Character calibration runtime | `maya_character_calibration_collected`, Maya 2026 |
| Spatial authoring | `Blocked` L3 |
| Spatial authoring assets ready/review/blocked | 1 / 0 / 1 |
| Spatial authoring checks pass/warn/error | 11 / 2 / 7 |
| Spatial authoring runtime | `maya_spatial_authoring_collected`, Maya 2026 |
| Platform variant forge | `Blocked` L3-linked |
| Platform variant assets / variants | 2 / 3 |
| Platform variant variants ready/review/blocked | 2 / 0 / 1 |
| Platform variant checks pass/warn/error | 21 / 1 / 8 |
| Platform variant runtime | `platform_variant_plan_joined_to_unreal_facts`, Unreal preset fact rows 10 |
| Platform variant Unreal runtime | `Blocked` L3 |
| Platform variant Unreal runtime variants ready/review/blocked | 0 / 2 / 1 |
| Platform variant Unreal runtime checks pass/warn/error | 21 / 4 / 2 |
| Platform variant Unreal runtime engine | `unreal_variant_runtime_assets_collected`, Unreal 5.3.2 |
| Platform variant generation plan | `Blocked` L3-derived |
| Platform variant generation operations ready/review/blocked/satisfied | 1 / 3 / 2 / 5 |
| Platform variant generation owner approvals required | 6 |
| Blocked modules | 0 |
| Host | Maya 2024 / AuroraView |

## Maya Entry

Run in Maya Script Editor:

```python
import sys
host = r"<repo>\dcc-hosts\maya-auroraview-host"
if host not in sys.path:
    sys.path.insert(0, host)

from ai_tool_ta_maya_host import show_portfolio
show_portfolio()
```

Then follow the Presenter Pack route:

1. Open Maya host through `show_portfolio()`.
2. Export the DCC-first case page from `Task Orchestrator`.
3. Run the composite Asset Handoff Gate and Decision Packet.
4. Compare PC and Mobile engine presets.
5. Review the Unreal Handoff Inspector.
6. Review Unreal preset facts inside the Maya-hosted case page.
7. Run Scene Transaction Guard.
8. Run `python <repo>\dcc-hosts\animation-continuity-lab\scripts\run_l3_smoke.py`.
9. Run `python <repo>\dcc-hosts\unreal-animation-bridge\scripts\run_import_l3_smoke.py`.
10. Run `python <repo>\dcc-hosts\character-calibration-studio\scripts\run_l3_smoke.py`.
11. Run `python <repo>\dcc-hosts\spatial-authoring-workbench\scripts\run_l3_smoke.py`.
12. Run `python <repo>\dcc-hosts\platform-variant-forge\scripts\run_smoke.py`.
13. Run `python <repo>\dcc-hosts\platform-variant-forge\scripts\run_unreal_runtime_probe.py`.
14. Run `python <repo>\dcc-hosts\platform-variant-forge\scripts\run_generation_plan.py`.
15. Review the Blender Rule Adapter artifact.
16. Run `python <repo>\dcc-hosts\blender-rule-adapter\scripts\run_l3_smoke.py`.
17. Run `python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_l3_smoke.py --run-runtime --timeout-seconds 600`.
18. Audit GUI media after final Maya screenshots and recording are captured.
19. Export and hand off the Presenter Pack.

## Presenter Pack Artifact

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r30-platform-variant-generation-plan-presentation-pack-20260805-190107.json
```

The Presenter Pack is the current public-facing DCC-first delivery object. It binds the Maya entry, 19-step demo route, 7-step business route, public package manifest, 27 key evidence file probes, GUI media audit, reviewer claims, preset fact reviewer queue, Scene Transaction Guard, Animation Continuity Lab, Unreal Animation Bridge import L3, Character Calibration Maya L3, Spatial Authoring Maya L3, Platform Variant Forge, Platform Variant Unreal Runtime Probe, Platform Variant Generation Planner, Blender bpy L3 adapter, 3ds Max pymxs L3 adapter, and mutation boundaries. Current gate is `CapturePending` because code and JSON evidence are complete while 9 Maya screenshots and 1 route recording are still missing.

## Case Page Artifact

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
```

The case page is the core case report inside the Presenter Pack. It binds the Maya entry, 7-step business route, live demo script, GUI evidence plan, runbook package, Asset Handoff Gate packet, Decision Packet, and validation commands into one reviewable JSON report.

## Runbook Artifact

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
```

The artifact proves:

- Asset Protocol has Maya custom attr inspection evidence.
- Cross-DCC Rule Matrix has scene facts, validation rows, and fix preview.
- Visual Review has camera rig, pass manifest, and capture preview.
- Texture Delivery has material/file node inspection and manifest validation.
- Task Orchestrator has scene discovery, dry-run task events, and receipts.
- Asset Handoff Decision has repair previews, owner dispositions, and engine handoff intents.

## GUI Evidence Manifest

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
```

This manifest defines 9 required Maya GUI screenshots, 1 primary route recording, file naming, target panels, and acceptance criteria. It is the capture checklist for turning the current DCC-first package into portfolio media.

## GUI Media Audit

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```

Current media root:

```text
<repo>\assets\dcc-first\r10-7-gui-evidence
```

The audit is intentionally `CapturePending`: 0 present, 0 review, 10 missing. It proves the package can check real Maya screenshots/recording after capture without treating the shotlist itself as finished media.

## Asset Handoff Gate

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
```

This packet is the first composite DCC business gate. It creates 2 synthetic Maya handoff assets, evaluates protocol, rule, texture, visual, and task queue evidence, then outputs 1 Ready asset, 1 Review asset, 0 Blocked assets, 3 preview actions, and a `Review` batch gate.

## Asset Handoff Decision Packet

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
```

Source packet:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-source-20260803-171316.json
```

The decision packet is now part of the R10.7 main case route above the composite gate. It keeps the same 2 synthetic assets, then adds 2 repair preview rows, 2 owner disposition rows, and 2 engine handoff mock rows. The Ready asset can produce an engine import intent; the Review asset is held for owner disposition. No engine write or owner approval is executed.

## Engine Handoff Preflight

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-8-engine-handoff-preflight-fixture-20260803-172302.json
```

Source decision packet:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-8-engine-handoff-preflight-fixture-decision-source-20260803-172302.json
```

The preflight packet is the R10.8 layer above Decision Packet. It applies the PC Unreal import preset to each engine handoff intent, checks path prefix, platform, LOD, triangle budget, texture budget, protocol carrier and receipt state, then emits 1 dry-run import sidecar for the Ready asset and holds 1 Review asset for owner disposition. No Unreal or engine write is executed.

## Engine Preset Comparison

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-9-engine-preset-comparison-20260803-172927.json
```

Source decision packet:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-9-engine-preset-comparison-decision-source-20260803-172927.json
```

The comparison packet is the R10.9 layer above Engine Preflight. It runs the same decision intent through PC and Mobile presets. The Ready asset creates a PC import sidecar but is blocked by the Mobile path/platform preset; the Review asset remains held across both presets. This shows the TA boundary between DCC readiness, platform-specific import rules, and owner disposition.

## Unreal Handoff Inspector

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

This is the first engine-side evidence row in the DCC-first package. It takes DCC import intents into an Unreal-style inspection contract: mount root, platform preset, asset class, source fingerprint, existing asset conflict, material dependencies, LOD, collision, owner state, and Python plugin readiness. The fixture has 2 public-safe import intents: 1 import-ready dry-run command and 1 intentionally blocked import. Current evidence level is L3++: Unreal 5.3.2 ran the Python script through `UnrealEditor-Cmd.exe`, imported a public `SM_HeroPanel_A` StaticMesh fixture, created `M_HeroPanel` Material, matched 2 / 2 Asset Registry rows, and matched 4 / 4 engine facts: source import data, material slot assignment, LOD count and collision settings.

## Unreal Preset Fact Comparison

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

This is the R17 layer above the Unreal L3++ artifact. It compares the actual Unreal runtime facts against PC and Mobile platform policy, including content path prefix, source import data, material slot, LOD count and collision policy. The result is intentionally not a green happy path: PC has an approved single-LOD public-fixture waiver, while Mobile stays blocked by platform path and LOD policy. The artifact reports 10 fact rows: 7 matched, 1 drift, 1 waived, 1 blocked, with 1 platform split and 1 approved waiver.

## Unreal Preset Fact Review

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json
```

This is the R18 Maya-hosted reviewer projection above the preset comparison. It keeps the source Unreal L3++ facts read-only, but turns the comparison into an operator queue: Mobile engine path is blocked, Mobile LOD is drift, and PC LOD is an approved waiver that still needs owner/expiry review. The artifact reports 10 rows, 3 attention rows, 1 blocked row, and 1 waiver row.

## Scene Transaction Guard

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-20260804-195730.json
```

This is the R19 Maya-hosted tool safety layer. It captures a scoped scene before and after a synthetic tool mutation, fingerprints both states, and exports created / deleted / modified rows plus selection and timeline context changes. The artifact reports 2 created nodes, 2 deleted nodes, 2 modified nodes, 9 rollback preview actions, and 4 risk rows. This is the portfolio proof that DCC tools expose their write boundary instead of hiding scene mutation behind a success message.

## Animation Continuity Lab

```text
<repo>\dcc-hosts\animation-continuity-lab\artifacts\animation-continuity-maya-l3-20260805-162744.json
```

This is the R23 animation handoff evidence layer. It creates public synthetic Maya transforms and keyed animCurves, then checks rig identity, skeleton fingerprint, take range, sample rate, required channel coverage, duplicate normalized channel identities, sub-frame keys, keys outside take range, root motion policy, animated scale leakage, and additive animation layer ownership. The artifact reports 2 takes, 1 Ready take, 1 intentionally Blocked take, 11 pass checks, 3 warnings, and 6 errors. No production animation scene, asset, MotionBuilder scene, or engine asset is mutated.

## Unreal Animation Bridge

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-import-l3-20260805-173309.json
```

This is the R25 animation-to-engine import layer. It reads the R23 Maya Animation Continuity L3 artifact, generates two public Maya FBX clips through `mayapy`, then enters Unreal 5.3.2 Python to import synthetic Skeleton / SkeletalMesh / AnimSequence assets. The artifact reports L3, 2 / 2 expected sequences present, 4 imported synthetic assets, 1 Ready clip, 1 intentionally Blocked clip, 12 pass checks, 1 warning, and 5 errors. The remaining Blocked state comes from the `Attack_A` business defect sample, not from missing Unreal runtime coverage.

## Character Calibration Studio

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json
```

This is the R26 character transfer evidence layer. It creates public synthetic Maya character meshes and joint DAGs, then checks topology signature, required joint coverage, TMP joint leakage, skin influence budget, calibration delta, face parameter coverage/range, Control Rig mapping and mirror pair coverage. The artifact reports L3, 2 character rows, 1 Ready row, 1 intentionally Blocked row, 10 pass checks, 2 warnings and 6 errors. No production character scene, DNA asset, Control Rig asset or engine asset is mutated.

## Spatial Authoring Workbench

```text
<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-maya-l3-20260805-181524.json
```

This is the R27 socket / hotspot / pose transfer evidence layer. It creates public synthetic Maya joints and locators, then checks parent joint coverage, local offset tolerance, mirror pair symmetry, hotspot semantic and owner, pose frame coverage/range, transform scale, local-space consistency, preview locator presence and pose transfer approval. The artifact reports L3, 2 spatial authoring rows, 1 Ready row, 1 intentionally Blocked row, 11 pass checks, 2 warnings and 7 errors. No production Maya scene, engine socket asset or private gameplay data is mutated.

## Platform Variant Forge

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-forge-contract-20260805-183315.json
```

This is the R28 PC to Mobile asset variant planning layer. It reads public-safe source asset facts, joins them to the existing Unreal preset fact comparison artifact, and checks target path policy, owner approval, triangle budget, texture memory, material slots, draw calls, LOD coverage, Nanite policy, shader feature downgrade and collision simplification. The artifact reports `L3-linked`, 2 source assets, 3 planned variants, 2 Ready variants, 1 intentionally Blocked Mobile variant, 21 pass checks, 1 warning and 8 errors. No scene, mesh, texture, material or Unreal asset is mutated.

## Platform Variant Unreal Runtime Probe

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-unreal-runtime-20260805-185026.json
```

This is the R29 runtime-vs-plan layer above Platform Variant Forge. It runs Unreal 5.3.2 Python against the public test project, ensures synthetic StaticMesh fixture variants exist under `/Game/AI_Tool_TA`, then compares runtime path, LOD count, material slot count, Nanite state, collision state and source evidence join against the R28 variant plan. The artifact reports L3, 3 planned variants, 0 Ready runtime variants, 2 Review variants, 1 intentionally Blocked variant, 21 pass checks, 4 warnings and 2 errors. No production Unreal asset is mutated; writes are limited to public fixture assets.

## Platform Variant Generation Planner

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-generation-plan-20260805-190052.json
```

This is the R30 dry-run generation layer above the R29 runtime probe. It reads runtime drift rows and the R28 variant plan, then emits explicit Unreal operation contracts for missing LODs, Nanite policy, material merge, texture downscale, collision simplification, source import and target variant creation. The artifact reports `L3-derived`, 11 operations: 1 Ready, 3 Review, 2 Blocked and 5 already Satisfied. The gate remains `Blocked` because the synthetic vehicle source/target assets are absent; HeroPanel LOD and texture operations stay `Review` until geometry and texture facts are readable. No production asset is mutated.

## Blender Rule Adapter

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260804-201125.json
```

This is the first non-Maya evidence row in the DCC-first package. The adapter normalizes Blender object custom properties, collections, material slots, UV evidence, and collision proxy hints into the same Cross-DCC Rule Matrix input shape used by the Maya route. The fixture has 2 public-safe assets: 1 Ready asset and 1 intentionally Blocked asset. Current evidence level is L3 because Blender 5.2.0 LTS runs the same contract through `bpy` in background mode.

## Blender L3 Harness

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json
```

This is the R22 bridge from contract adapter to real Blender runtime. The code includes `bpy_collector.py`, `scripts\run_blender_l3.py`, and `scripts\run_l3_smoke.py`. On this machine Blender 5.2.0 LTS exports `bpy_scene_collected`; the gate remains `Blocked` because the synthetic fixture intentionally includes one blocked asset. No production Blender scene, asset, or engine data is mutated.

## 3ds Max Rule Adapter

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
```

This is the R22 non-Maya adapter row. It normalizes 3ds Max user properties, layer/export root, LOD suffixes, material slots, map channels, transform state and collision proxies into `cross-dcc-rule-input@0.1.0`. The public fixture has 2 assets: 1 Ready static prop and 1 intentionally Blocked hero prop. It reports 13 pass checks, 5 warnings and 2 errors, exposing UV channel budget, UV quality, material naming, transform and collision failure paths without referencing proprietary scenes.

## 3ds Max L3 Harness

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260805-153232.json
```

This is the R22 bridge from Max contract adapter to real `pymxs` runtime. `3dsmaxbatch.exe` ran the synthetic fixture and exported `pymxs_scene_collected` with 4 runtime-collected objects. The gate remains `Blocked` because the fixture intentionally includes one blocked asset. No production Max scene, asset or engine data is mutated.

## DCC Presenter Pack

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r30-platform-variant-generation-plan-presentation-pack-20260805-190107.json
```

The Presenter Pack is the R30 delivery layer above the case page. It does not create new production claims; it probes whether the public package, case page, GUI audit, handoff decision, engine preflight, preset comparison, Animation Continuity Lab, Unreal Animation Bridge import L3, Character Calibration Maya L3, Spatial Authoring Maya L3, Platform Variant Forge, Platform Variant Unreal Runtime Probe, Platform Variant Generation Planner, Blender adapter, Blender L3 runtime, 3ds Max adapter, Max L3 runtime, Unreal L3++ inspector, Unreal preset fact comparison, Maya-hosted preset fact review, and Scene Transaction Guard artifacts are present and ready to show from Maya. It reports 27 / 27 evidence files present, 0 missing required files, 19 demo route steps, and `CapturePending` media status.

## Validation

```powershell
cd <repo>\showcases\portfolio-site
npm run build
```

```powershell
python -m py_compile <repo>\dcc-hosts\maya-auroraview-host\ai_tool_ta_maya_host\api.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\blender-rule-adapter\blender_rule_adapter\contract.py <repo>\dcc-hosts\blender-rule-adapter\blender_rule_adapter\bpy_collector.py <repo>\dcc-hosts\blender-rule-adapter\scripts\run_smoke.py <repo>\dcc-hosts\blender-rule-adapter\scripts\run_l3_smoke.py <repo>\dcc-hosts\blender-rule-adapter\scripts\run_blender_l3.py
python <repo>\dcc-hosts\blender-rule-adapter\scripts\run_smoke.py
python <repo>\dcc-hosts\blender-rule-adapter\scripts\run_l3_smoke.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\3dsmax-rule-adapter\max_rule_adapter\contract.py <repo>\dcc-hosts\3dsmax-rule-adapter\max_rule_adapter\runtime_collector.py <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_smoke.py <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_l3_smoke.py <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_3dsmax_l3.py
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_smoke.py
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_l3_smoke.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\unreal-handoff-inspector\unreal_handoff_inspector\contract.py <repo>\dcc-hosts\unreal-handoff-inspector\scripts\run_smoke.py
python <repo>\dcc-hosts\unreal-handoff-inspector\scripts\run_smoke.py
python <repo>\dcc-hosts\unreal-handoff-inspector\scripts\run_unreal_l3_smoke.py
python <repo>\dcc-hosts\unreal-handoff-inspector\scripts\run_preset_fact_compare.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\animation-continuity-lab\animation_continuity_lab\contract.py <repo>\dcc-hosts\animation-continuity-lab\animation_continuity_lab\maya_collector.py <repo>\dcc-hosts\animation-continuity-lab\scripts\run_smoke.py <repo>\dcc-hosts\animation-continuity-lab\scripts\run_l3_smoke.py <repo>\dcc-hosts\animation-continuity-lab\scripts\run_maya_l3.py
python <repo>\dcc-hosts\animation-continuity-lab\scripts\run_smoke.py
python <repo>\dcc-hosts\animation-continuity-lab\scripts\run_l3_smoke.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\unreal-animation-bridge\unreal_animation_bridge\contract.py <repo>\dcc-hosts\unreal-animation-bridge\scripts\run_smoke.py <repo>\dcc-hosts\unreal-animation-bridge\scripts\run_l3_smoke.py <repo>\dcc-hosts\unreal-animation-bridge\scripts\run_import_l3_smoke.py <repo>\dcc-hosts\unreal-animation-bridge\scripts\generate_maya_fbx_fixture.py <repo>\dcc-hosts\unreal-animation-bridge\scripts\unreal_python\probe_animation_runtime.py <repo>\dcc-hosts\unreal-animation-bridge\scripts\unreal_python\import_animsequence_fixture.py
python <repo>\dcc-hosts\unreal-animation-bridge\scripts\run_smoke.py
python <repo>\dcc-hosts\unreal-animation-bridge\scripts\run_l3_smoke.py
python <repo>\dcc-hosts\unreal-animation-bridge\scripts\run_import_l3_smoke.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\character-calibration-studio\character_calibration_studio\contract.py <repo>\dcc-hosts\character-calibration-studio\character_calibration_studio\maya_collector.py <repo>\dcc-hosts\character-calibration-studio\scripts\run_smoke.py <repo>\dcc-hosts\character-calibration-studio\scripts\run_l3_smoke.py <repo>\dcc-hosts\character-calibration-studio\scripts\run_maya_l3.py
python <repo>\dcc-hosts\character-calibration-studio\scripts\run_smoke.py
python <repo>\dcc-hosts\character-calibration-studio\scripts\run_l3_smoke.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\spatial-authoring-workbench\spatial_authoring_workbench\contract.py <repo>\dcc-hosts\spatial-authoring-workbench\spatial_authoring_workbench\maya_collector.py <repo>\dcc-hosts\spatial-authoring-workbench\scripts\run_smoke.py <repo>\dcc-hosts\spatial-authoring-workbench\scripts\run_l3_smoke.py <repo>\dcc-hosts\spatial-authoring-workbench\scripts\run_maya_l3.py
python <repo>\dcc-hosts\spatial-authoring-workbench\scripts\run_smoke.py
python <repo>\dcc-hosts\spatial-authoring-workbench\scripts\run_l3_smoke.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\platform-variant-forge\platform_variant_forge\contract.py <repo>\dcc-hosts\platform-variant-forge\scripts\run_smoke.py
python <repo>\dcc-hosts\platform-variant-forge\scripts\run_smoke.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\platform-variant-forge\platform_variant_forge\runtime_contract.py <repo>\dcc-hosts\platform-variant-forge\scripts\run_unreal_runtime_probe.py <repo>\dcc-hosts\platform-variant-forge\scripts\unreal_python\probe_variant_runtime.py
python <repo>\dcc-hosts\platform-variant-forge\scripts\run_unreal_runtime_probe.py
```

```powershell
python -m py_compile <repo>\dcc-hosts\platform-variant-forge\platform_variant_forge\generation_plan.py <repo>\dcc-hosts\platform-variant-forge\scripts\run_generation_plan.py
python <repo>\dcc-hosts\platform-variant-forge\scripts\run_generation_plan.py
```

Maya 2024 `mayapy` smoke:

- case page report: `maya-dcc-portfolio-case-page@1.1.0`
- report version: `maya-dcc-showcase-runbook-package@1.4.0`
- modules: 5
- artifacts: 5
- case page sections: 6
- case page artifact rows: 4
- ready: 3
- review: 2
- blocked: 0
- business route steps: 7
- live demo script steps: 7
- GUI checklist items: 7
- GUI evidence shots: 9
- GUI evidence recordings: 1
- GUI media audit report: `maya-dcc-gui-media-audit@0.2.0`
- GUI media audit gate: `CapturePending`
- GUI media present/review/missing: 0 / 0 / 10
- asset handoff report: `maya-asset-handoff-gate@0.1.0`
- asset handoff gate: `Review`
- asset handoff assets: 2
- asset handoff ready/review/blocked: 1 / 1 / 0
- asset handoff decision report: `maya-asset-handoff-decision-packet@0.1.0`
- asset handoff decision repair actions: 2
- asset handoff decision owner dispositions: 2
- asset handoff decision engine ready/held: 1 / 1
- engine handoff preflight report: `maya-engine-handoff-preflight@0.1.0`
- engine handoff preflight ready/held: 1 / 1
- engine handoff import sidecars: 1
- engine preset comparison report: `maya-engine-handoff-preset-comparison@0.1.0`
- engine preset platform split / held across presets: 1 / 1
- presenter pack report: `maya-dcc-presentation-pack@0.1.0`
- presenter pack gate: `CapturePending`
- animation continuity report: `animation-continuity-maya-l3@0.1.0`
- animation continuity L3 status: `maya_anim_curves_collected`
- animation continuity assets ready/review/blocked: 1 / 0 / 1
- animation continuity checks pass/warn/error: 11 / 3 / 6
- unreal animation bridge report: `unreal-animation-bridge-import-l3@0.1.0`
- unreal animation bridge evidence / L3 status: L3 / `unreal_animsequence_assets_imported`
- unreal animation bridge assets ready/review/blocked: 1 / 0 / 1
- unreal animation bridge checks pass/warn/error: 12 / 1 / 5
- unreal animation bridge missing sequences: 0
- unreal animation bridge imported assets: 4
- character calibration report: `character-calibration-maya-l3@0.1.0`
- character calibration L3 status: `maya_character_calibration_collected`
- character calibration assets ready/review/blocked: 1 / 0 / 1
- character calibration checks pass/warn/error: 10 / 2 / 6
- spatial authoring report: `spatial-authoring-maya-l3@0.1.0`
- spatial authoring L3 status: `maya_spatial_authoring_collected`
- spatial authoring assets ready/review/blocked: 1 / 0 / 1
- spatial authoring checks pass/warn/error: 11 / 2 / 7
- platform variant forge report: `platform-variant-forge-contract@0.1.0`
- platform variant forge evidence / L3 status: L3-linked / `platform_variant_plan_joined_to_unreal_facts`
- platform variant forge gate: `Blocked`
- platform variant forge assets / variants: 2 / 3
- platform variant forge variants ready/review/blocked: 2 / 0 / 1
- platform variant forge checks pass/warn/error: 21 / 1 / 8
- platform variant forge source fact rows: 10
- platform variant Unreal runtime report: `platform-variant-unreal-runtime@0.1.0`
- platform variant Unreal runtime evidence / L3 status: L3 / `unreal_variant_runtime_assets_collected`
- platform variant Unreal runtime variants ready/review/blocked: 0 / 2 / 1
- platform variant Unreal runtime checks pass/warn/error: 21 / 4 / 2
- platform variant Unreal runtime engine: Unreal 5.3.2
- platform variant generation plan report: `platform-variant-generation-plan@0.1.0`
- platform variant generation plan evidence / L3 status: L3-derived / `runtime_drift_to_generation_plan`
- platform variant generation plan operations ready/review/blocked/satisfied: 1 / 3 / 2 / 5
- platform variant generation plan owner approvals required: 6
- blender rule adapter report: `blender-rule-adapter-contract@0.1.0`
- blender evidence level / L3 status: L3 / `bpy_scene_collected`
- blender adapter gate: `Blocked`
- blender adapter assets ready/blocked: 1 / 1
- blender adapter checks pass/warn/error: 8 / 3 / 1
- 3ds Max rule adapter report: `max-rule-adapter-contract@0.1.0`
- 3ds Max evidence level / L3 status: L3 / `pymxs_scene_collected`
- 3ds Max adapter gate: `Blocked`
- 3ds Max adapter assets ready/review/blocked: 1 / 0 / 1
- 3ds Max adapter checks pass/warn/error: 13 / 5 / 2
- 3ds Max L3 readiness report: `max-rule-adapter-pymxs-l3@0.1.0`
- 3ds Max L3 readiness gate: `Blocked`
- 3ds Max batch discovered: true
- unreal handoff inspector report: `unreal-handoff-inspector-contract@0.4.0`
- unreal evidence level / L3 status: L3++ / `unreal_engine_facts_matched`
- unreal engine / Python: Unreal 5.3.2 / Python 3.9.7
- unreal registry fixture matched: 2 / 2
- unreal engine facts matched: 4 / 4
- unreal source import / material slot / LOD / collision: matched / matched / 1 / 1 simple shape
- unreal inspector gate: `Blocked`
- unreal inspector import ready/blocked: 1 / 1
- unreal inspector checks pass/review/blocked: 14 / 2 / 4
- unreal preset fact comparison report: `unreal-preset-fact-comparison@0.1.0`
- unreal preset fact rows matched/drift/waived/blocked: 7 / 1 / 1 / 1
- unreal preset fact platform split / approved waivers: 1 / 1
- unreal preset fact review report: `maya-unreal-preset-fact-review@0.1.0`
- unreal preset fact review rows / queue / blocked / waivers: 10 / 3 / 1 / 1
- presenter pack evidence files present/missing: 27 / 0
- presenter pack demo route steps: 19
- reviewer claims: 13

## Legacy Package

The R8 public package remains in `README.md`, `EVIDENCE_INDEX.md`, `SIGNOFFS.md`, and `VALIDATION.md` as the historical browser evidence ledger. The current final presentation route starts from the R30 Maya Cross-DCC / Engine / Animation / Character / Spatial / Platform Variant Generation Reviewer Pack.
