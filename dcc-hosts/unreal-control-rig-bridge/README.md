# Unreal Control Rig Bridge

Public-safe character Control Rig handoff from Maya calibration facts to Unreal runtime readiness.

The module reads `Character Calibration Drilldown` evidence and checks whether the public Unreal test project has the required Control Rig API, SkeletalMesh/Skeleton binding targets and expected Control Rig asset paths. Later layers author a public `CR_HeroFace` fixture, import a public face Skeleton, check deformation target links, invoke transient compile methods, and now expose a native C++ bridge readiness gate for direct diagnostics/status. Runtime probes stay scoped to public fixtures and record write boundaries.

## Commands

```powershell
python dcc-hosts/unreal-control-rig-bridge/scripts/run_smoke.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_fixture_authoring.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_face_skeleton_fixture.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_deformation_link.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_compile_status.py
python dcc-hosts/unreal-control-rig-bridge/scripts/run_control_rig_native_bridge_readiness.py
```

`run_l3_smoke.py` launches `UnrealEditor-Cmd.exe` against the public `AI_Tool_TA_Unreal_L3.uproject` and exports `unreal-control-rig-bridge@0.1.0`.

Current R74 artifact:

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-native-bridge-readiness-20260806-094558.json
```

R74 result:

- evidence level: L3-readiness
- l3 status: `unreal_control_rig_native_bridge_readiness_collected`
- gate: `Blocked`
- Unreal runtime: 5.3.2 / Python 3.9.7
- runtimeEntered: true
- Control Rig / RigVM classes visible: true
- native source complete: true
- missing required native files: 0
- compiled bridge binary / commandlet visible: false / false
- checks pass / warning / error: 5 / 0 / 2
- assetWrites / engineWrites / productionWrites: 0 / 0 / 0

The current `Blocked` gate is intentional business evidence. R45 proved `CR_HeroFace` compile methods can be invoked through Unreal Python, but direct compile diagnostics/status are not readable. R74 turns that gap into public C++ Editor plugin source plus a runtime readiness artifact; the next concrete step is BuildPlugin, then a commandlet visibility probe.
