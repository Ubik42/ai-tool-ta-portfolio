# Unreal Handoff Inspector

This is the engine-side evidence adapter for the AI Tool TA portfolio.

It consumes public synthetic Unreal import intents and a synthetic Content Registry snapshot, then checks the parts that DCC preflight cannot prove by itself:

- Unreal mount root and content path policy.
- Platform preset and asset class policy.
- Source fingerprint vs sidecar fingerprint.
- Existing asset conflict.
- Material and texture dependency availability.
- LOD and collision policy.
- Owner hold state before import task preview.
- Unreal Python automation readiness.

Current state is L3++ Unreal engine fact evidence plus R17 preset fact comparison. The public test project under `projects/AI_Tool_TA_Unreal_L3` is opened through `UnrealEditor-Cmd.exe -run=pythonscript`; the smoke imports the public `SM_HeroPanel_A.obj` as a StaticMesh, creates `M_HeroPanel` as a Material, queries Unreal Asset Registry, and validates source import data, material slot assignment, LOD count and collision settings. The R17 comparison then checks these runtime facts against PC / Mobile preset policy and an explicit exception waiver row.

Run the pure Python contract smoke:

```powershell
python dcc-hosts/unreal-handoff-inspector/scripts/run_smoke.py
```

Run the Unreal L3++ smoke:

```powershell
python dcc-hosts/unreal-handoff-inspector/scripts/run_unreal_l3_smoke.py
```

Run the R17 preset fact comparison:

```powershell
python dcc-hosts/unreal-handoff-inspector/scripts/run_preset_fact_compare.py
```

Latest L3++ artifact:

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

Latest preset fact comparison artifact:

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

R17 result: 10 preset/fact rows, 7 matched, 1 drift, 1 waived, 1 blocked. PC keeps the single-LOD public fixture as an approved waiver; Mobile stays blocked by platform path and LOD policy.
