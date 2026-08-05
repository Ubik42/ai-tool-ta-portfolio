# Unreal Socket Import Checker

R38 module for public-safe spatial authoring handoff from Maya sockets / hotspots / pose transfer facts to Unreal runtime socket readiness.

The module reads `Spatial Authoring Drilldown` evidence and checks whether the public Unreal test project has the required SkeletalMesh / Skeleton targets, socket API and expected engine socket names. It is intentionally read-only in the first pass: missing sockets become owner actions and fix previews, not automatic engine mutation.

## Commands

```powershell
python dcc-hosts/unreal-socket-import-checker/scripts/run_smoke.py
python dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py
```

`run_l3_smoke.py` launches `UnrealEditor-Cmd.exe` against the public `AI_Tool_TA_Unreal_L3.uproject` and exports `unreal-socket-import-checker@0.1.0`.

Current R38 artifact:

```text
D:\cs\AIToolTA_Portfolio\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-import-checker-l3-20260805-212131.json
```

## Current Result

- evidence：L3 / `unreal_socket_facts_collected`
- gate：`Blocked`
- runtime：Unreal 5.3.2 Python
- rows ready / review / blocked：0 / 0 / 2
- checks pass / warning / error：9 / 2 / 9
- socket API：ready
- expected / runtime sockets：4 / 0
- assetWrites / productionWrites：0 / 0

Blocked 是业务门禁：approved rifle 的 SkeletalMesh / Skeleton 存在但缺 `SK_Hand_L` 和 `SK_Hand_R` socket；TMP backpack 的 Unreal target 不存在，同时 Maya 源头仍有 missing joints、world-space socket、offset 和 pose transfer 问题。
