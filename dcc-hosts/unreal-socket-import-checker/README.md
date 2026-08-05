# Unreal Socket Import Checker

R38/R40/R54/R60 module for public-safe spatial authoring handoff from Maya sockets / hotspots / pose transfer facts to Unreal runtime socket readiness, API-limited socket authoring, native bridge readiness and gameplay attach readiness.

The module reads `Spatial Authoring Drilldown` evidence and checks whether the public Unreal test project has the required SkeletalMesh / Skeleton targets, socket API and expected engine socket names. It is intentionally read-only in the first pass: missing sockets become owner actions and fix previews, not automatic engine mutation.

## Commands

```powershell
python dcc-hosts/unreal-socket-import-checker/scripts/run_smoke.py
python dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py
python dcc-hosts/unreal-socket-import-checker/scripts/run_socket_authoring_executor.py
python dcc-hosts/unreal-socket-import-checker/scripts/run_native_bridge_readiness.py
python dcc-hosts/unreal-socket-import-checker/scripts/run_gameplay_attach_fixture.py
```

`run_l3_smoke.py` launches `UnrealEditor-Cmd.exe` against the public `AI_Tool_TA_Unreal_L3.uproject` and exports `unreal-socket-import-checker@0.1.0`. `run_native_bridge_readiness.py` launches the same project and exports `unreal-socket-native-bridge-readiness@0.1.0`.

Current R38 artifact:

```text
D:\cs\AIToolTA_Portfolio\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-import-checker-l3-20260805-212131.json
```

Current R61 native bridge source readiness artifact:

```text
D:\cs\AIToolTA_Portfolio\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-bridge-readiness-20260806-055738.json
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

## R60 Native Bridge Readiness

R60 reads the R40 API-limited executor receipt and enters Unreal 5.3.2 headless runtime to check the next real authoring boundary. R61 adds the disabled-by-default public `AI_Tool_TA_SocketBridge` Editor plugin source package, then reruns the readiness probe. The required source files are now present; the remaining blocked boundary is compiled binary plus commandlet visibility.

Current result:

- evidence：L3-readiness / `unreal_socket_native_bridge_readiness_collected`
- gate：`Blocked`
- source API limited：true
- expected / Python-created sockets：2 / 0
- socket classes / editor utility surface：true / true
- native source / plugin / binary / commandlet：true / true / false / false
- missing required native files：0
- checks pass / warning / error：7 / 0 / 2
- assetWrites / productionWrites：0 / 0

业务结论：UE Python 反射路径已经证明不可安全写 socket identity；R61 已经补上可审查 C++ commandlet / BlueprintFunctionLibrary 源码 contract，下一步是构建加载 Editor module，并补 JSON receipt parsing、post-check 和 rollback receipt。

Current source package:

```text
D:\cs\AIToolTA_Portfolio\dcc-hosts\unreal-handoff-inspector\projects\AI_Tool_TA_Unreal_L3\Plugins\AI_Tool_TA_SocketBridge
```
