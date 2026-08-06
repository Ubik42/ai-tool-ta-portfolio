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
python dcc-hosts/unreal-control-rig-bridge/scripts/run_control_rig_native_bridge_build.py
```

`run_l3_smoke.py` launches `UnrealEditor-Cmd.exe` against the public `AI_Tool_TA_Unreal_L3.uproject` and exports `unreal-control-rig-bridge@0.1.0`.

Current R75 artifacts:

```text
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-native-bridge-readiness-20260806-094558.json
<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-native-bridge-build-20260806-100928.json
```

R75 build result:

- evidence level: L3-build
- l3 status: `unreal_control_rig_native_bridge_plugin_built`
- gate: `Ready`
- RunUAT: UE 5.3 `BuildPlugin`
- compiled DLLs: 1
- compiler version: 14.38.33130
- returnCode / errorLines: 0 / 0
- configRestored: true
- assetWrites / engineWrites / productionWrites: 0 / 0 / 0

R74 readiness result:

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

R45 proved `CR_HeroFace` compile methods can be invoked through Unreal Python, but direct compile diagnostics/status are not readable. R74 turned that gap into public C++ Editor plugin source plus a runtime readiness artifact; R75 proves the source compiles into a packaged Editor DLL. The next concrete step is a commandlet visibility probe against the packaged plugin.
