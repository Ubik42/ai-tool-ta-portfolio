# Unreal Control Rig Bridge

R37 module for public-safe character Control Rig handoff from Maya calibration facts to Unreal runtime readiness.

The module reads `Character Calibration Drilldown` evidence and checks whether the public Unreal test project has the required Control Rig API, SkeletalMesh/Skeleton binding targets and expected Control Rig asset paths. It is intentionally read-only: the first bridge pass does not create Control Rig assets or mutate production content.

## Commands

```powershell
python dcc-hosts/unreal-control-rig-bridge/scripts/run_smoke.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py
```

`run_l3_smoke.py` launches `UnrealEditor-Cmd.exe` against the public `AI_Tool_TA_Unreal_L3.uproject` and exports `unreal-control-rig-bridge@0.1.0`.

Current R37 artifact:

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-205656.json
```

R37 result:

- evidence level: L3
- l3 status: `unreal_control_rig_bridge_facts_collected`
- gate: `Blocked`
- Unreal runtime: 5.3.2 / Python 3.9.7
- Control Rig API ready: true
- character rows: 2
- ready / review / blocked: 0 / 0 / 2
- checks pass / warning / error: 8 / 1 / 7
- skeletal mesh + skeleton bindings: 1
- expected Control Rig assets present: 0
- assetWrites / productionWrites: 0 / 0

The `Blocked` gate is intentional business evidence. The approved Maya character row reaches Unreal and finds the public SkeletalMesh/Skeleton binding, but the expected `CR_HeroFace` Control Rig asset is absent. The TMP row is blocked both by source Maya calibration defects and missing Unreal targets. This keeps Control Rig approval as an engine-side handoff gate instead of a checkbox in the Maya source tool.
