# Unreal Animation Bridge

Public-safe bridge from Maya animation continuity facts to Unreal AnimSequence import evidence.

R25 scope:

- Read the R23 Maya Animation Continuity L3 artifact.
- Generate two public synthetic Maya FBX clips through `mayapy` and `fbxmaya`.
- Import the clips into the local public Unreal test project through `UnrealEditor-Cmd.exe`.
- Save only synthetic `/Game/AI_Tool_TA` Skeleton / SkeletalMesh / AnimSequence assets.
- Export contract, readiness, and import L3 artifacts.

Current R25 result:

- Import report: `unreal-animation-bridge-import-l3@0.1.0`
- Evidence level: `L3`
- Runtime status: `unreal_animsequence_assets_imported`
- Unreal runtime: 5.3.2 / Python 3.9.7
- Imported assets: 4 public synthetic assets
- Runtime sequence presence: 2 / 2
- Business result: 1 Ready clip, 1 Blocked clip

The remaining `Blocked` gate is intentional business evidence: `Attack_A` keeps rig/sample-rate/channel/root-motion defects from the Maya source artifact. The Unreal import itself is now proven, not merely ready.
