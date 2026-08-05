# DCC-first Public Package

This is the current reviewer entry point for the AI Tool TA portfolio.

The portfolio is now demonstrated inside Maya through AuroraView. The browser build remains the embedded UI surface and evidence browser; the primary proof is the Maya-hosted R22 Cross-DCC / Engine Reviewer Pack.

## Current Package

| Field | Value |
| --- | --- |
| Package | `ai-tool-ta-dcc-first-showcase-r22` |
| Version | `dcc-first-package@1.19.0` |
| Source report | `maya-dcc-portfolio-case-page@1.1.0` |
| Gate | `CapturePending` |
| Modules | 5 |
| DCC artifacts | 7 |
| Case page sections | 6 |
| Case page artifacts | 6 |
| Business route steps | 7 |
| Presenter pack report | `maya-dcc-presentation-pack@0.1.0` |
| Presenter pack evidence files | 19 / 19 present |
| Presenter pack missing required files | 0 |
| Presenter demo route steps | 12 |
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

Then use the right rail:

1. `DCC Showcase Runbook` / `Build Plan`
2. `DCC Showcase Runbook` / `Run Smoke`
3. `DCC Showcase Runbook` / `Export Package`
4. `Asset Handoff Gate` / `Fixture` / `Export Packet`
5. `Asset Handoff Gate` / `Decision Packet`
6. `Task Orchestrator` evidence view / `Export Case Page`
7. `Task Orchestrator` evidence view / `Audit Media`
8. `Task Orchestrator` evidence view / `Preset Facts`
9. `Task Orchestrator` evidence view / `Txn Guard`
10. `Task Orchestrator` evidence view / `Presenter Pack`
11. Run `python <repo>\dcc-hosts\blender-rule-adapter\scripts\run_l3_smoke.py` when validating the Blender L3 readiness harness.
12. Run `python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_l3_smoke.py --run-runtime --timeout-seconds 600` when validating the Max adapter runtime evidence.
13. Inspect the module rows, live demo script, GUI checklist, handoff asset rows, decision rows, engine comparison rows, Unreal inspector rows, preset fact review rows, transaction risk rows, rollback preview, Blender adapter rows, Blender L3 readiness gate, 3ds Max adapter rows, Max L3 readiness gate, media audit rows, and generated artifact paths.

## Presenter Pack Artifact

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r22-blender-max-l3-presentation-pack-20260805-153957.json
```

The Presenter Pack is the current public-facing DCC-first delivery object. It binds the Maya entry, 12-step demo route, 7-step business route, public package manifest, 19 key evidence file probes, GUI media audit, reviewer claims, preset fact reviewer queue, Scene Transaction Guard, Blender bpy L3 adapter, 3ds Max pymxs L3 adapter, and mutation boundaries. Current gate is `CapturePending` because code and JSON evidence are complete while 9 Maya screenshots and 1 route recording are still missing.

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
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r22-blender-max-l3-presentation-pack-20260805-153957.json
```

The Presenter Pack is the R22 delivery layer above the case page. It does not create new production claims; it probes whether the public package, case page, GUI audit, handoff decision, engine preflight, preset comparison, Blender adapter, Blender L3 runtime, 3ds Max adapter, Max L3 runtime, Unreal L3++ inspector, Unreal preset fact comparison, Maya-hosted preset fact review, and Scene Transaction Guard artifacts are present and ready to show from Maya. It reports 19 / 19 evidence files present, 0 missing required files, 12 demo route steps, and `CapturePending` media status.

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
- presenter pack evidence files present/missing: 19 / 0
- presenter pack demo route steps: 12
- reviewer claims: 13

## Legacy Package

The R8 public package remains in `README.md`, `EVIDENCE_INDEX.md`, `SIGNOFFS.md`, and `VALIDATION.md` as the historical browser evidence ledger. The current final presentation route starts from the R21 Maya Cross-DCC / Engine Reviewer Pack.
