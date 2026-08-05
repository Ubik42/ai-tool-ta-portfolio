# Unreal Socket Import Checker

R38/R40/R54/R60 目标：把 `Spatial Authoring Workbench` 的 Maya socket / hotspot / pose transfer facts 接到 Unreal runtime readiness、API-limited authoring executor、native bridge readiness 和 gameplay attach readiness，证明挂点交付不是停在 DCC locator，而是能继续进入引擎资产门禁。

## 核心业务逻辑

这个工具解决的是 gameplay attach point 的交付可信度：

- Maya 源头声明了哪些 socket export names。
- socket 是否挂在有效 parent joint，offset / space / mirror / preview 是否干净。
- Unreal public project 里目标 SkeletalMesh / Skeleton 是否存在。
- Unreal Python 是否能访问 SkeletalMesh / Skeleton / SkeletalMeshSocket API。
- expected socket names 是否真的在 engine asset 上可见。
- 缺失 socket 只输出 owner action 和 fix preview，不自动写引擎资产。

核心秘诀是把 DCC authoring readiness 和 engine socket readiness 分开判定。一个 Maya Ready 行如果 Unreal 没有对应 socket，仍然必须 Blocked；一个 TMP 行如果源头和 engine target 都有问题，也要同时暴露两层阻断。

## 当前实现

代码入口：

- `dcc-hosts/unreal-socket-import-checker/unreal_socket_import_checker/contract.py`
- `dcc-hosts/unreal-socket-import-checker/unreal_socket_import_checker/controlled_executor.py`
- `dcc-hosts/unreal-socket-import-checker/unreal_socket_import_checker/native_bridge.py`
- `dcc-hosts/unreal-socket-import-checker/unreal_socket_import_checker/gameplay_attach.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/run_smoke.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/run_socket_authoring_executor.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/run_native_bridge_readiness.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/run_gameplay_attach_fixture.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/unreal_python/probe_socket_import_checker.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/unreal_python/execute_socket_authoring.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/unreal_python/probe_native_socket_bridge.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/unreal_python/probe_socket_api_docs.py`
- `dcc-hosts/unreal-socket-import-checker/scripts/unreal_python/probe_gameplay_attach_runtime.py`

数据来源：

- `dcc-hosts/spatial-authoring-workbench/artifacts/spatial-authoring-drilldown-20260805-203713.json`
- public Unreal project：`dcc-hosts/unreal-handoff-inspector/projects/AI_Tool_TA_Unreal_L3/AI_Tool_TA_Unreal_L3.uproject`

## 证据

```text
<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-import-checker-l3-20260805-212131.json
<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-authoring-executor-20260805-222014.json
<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-bridge-readiness-20260806-053757.json
<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-api-docs-20260805-222200.json
<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-gameplay-attach-fixture-20260806-034615.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r60-unreal-socket-native-bridge-presentation-pack-20260806-054048.json
```

当前结果：

- report version：`unreal-socket-import-checker@0.1.0`
- evidence level：L3
- l3 status：`unreal_socket_facts_collected`
- gate：`Blocked`
- runtime：Unreal 5.3.2 Python
- rows ready / review / blocked：0 / 0 / 2
- checks pass / warning / error：9 / 2 / 9
- socket API：ready
- expected / runtime sockets：4 / 0
- owner actions：11
- assetWrites / productionWrites：0 / 0

Blocked 是业务门禁，不是 runtime 缺失：`Rifle Socket Authoring Approved` 的 `/Game/AI_Tool_TA/Characters/SK_Hero` 和 Skeleton 存在，但缺 `SK_Hand_L`、`SK_Hand_R` socket；`Backpack Socket Temporary Blocked` 的 Unreal target 缺失，且 Maya 源头仍有 missing joints、world-space socket、offset、hotspot owner 和 pose transfer approval 问题。

## R40 Socket Authoring Executor

R40 尝试把 R38 的 approved rifle 缺 socket 问题推进到 engine-side controlled executor。结果不是成功 auto-fix，而是一个有价值的真实阻断证据：

- source selection：只选择 `spatial-rifle-authoring-001`；`spatial-backpack-tmp-002` 保持 held / no-write。
- runtime：Unreal 5.3.2 commandlet Python。
- gate：`Blocked`
- l3 status：`unreal_socket_authoring_executor_api_limited`
- selected / held rows：1 / 1
- expected / created sockets：2 / 0
- checks pass / warning / error：9 / 0 / 2
- assetWrites / engineWrites / productionWrites：0 / 0 / 0
- rollback：preflight fingerprint 保持恢复，因为没有可命名 socket 被实际创建。

API docs probe 证明了卡点：UE 5.3 Python 暴露 `SkeletalMesh.add_socket(socket, add_to_skeleton=False)`，但 commandlet-created `SkeletalMeshSocket` 的 `socket_name` 和 `bone_name` 是 read-only；构造参数和 `rename()` 只改变 UObject name，不改变 socket identity；`initialize_socket_from_location()` 需要 SkeletalMeshComponent，但仍不会设置 socket name。这个结论让工具不会把“看起来有 add_socket API”误判成“可安全自动修 socket”。

## R60 Native Bridge Readiness

R60 把 R40 的 API-limited 结论推进为 native bridge readiness contract：Unreal 5.3.2 headless runtime 能看见 SkeletalMesh / Skeleton / SkeletalMeshSocket classes 和 Editor Utility surface，但 public `.uproject` 目前没有 `Source`、没有 `AI_Tool_TA_SocketBridge` plugin、没有 compiled bridge binary、没有 commandlet class，并缺 6 个 required native files。

当前结果：L3-readiness / `Blocked` / `unreal_socket_native_bridge_readiness_collected`；sourceApiLimited=true，expectedSockets=2，createdSocketsViaPython=0，socketClassesVisible=true，editorUtilitySurfaceVisible=true，hasNativeSource=false，hasSocketBridgePlugin=false，hasCompiledBridgeBinary=false，commandletVisible=false，6 pass / 0 warning / 3 error，assetWrites / productionWrites = 0 / 0。

业务结论：socket 自动写入的下一步是实现 C++ commandlet / Editor Utility wrapper，把 socketName、boneName 和 relative transform 放进可 post-check / rollback 的 native write path。

## 后续

下一步不要继续在 UE 5.3 Python `SkeletalMeshSocket` identity 字段上消耗时间。更高价值的路线是实现 Unreal C++ / Editor Utility Blueprint socket authoring adapter，或把 Control Rig / animation curve / compression 这类 Python 可读写度更高的引擎事实继续做深。


## R40 Presenter Pack

当前最终 Presenter Pack 已升级为 `<repo>\dcc-hosts\maya-auroraview-host\artifacts\r60-unreal-socket-native-bridge-presentation-pack-20260806-054048.json`；Unreal Socket Import Checker 是空间作者线的 R38 L3 runtime coverage，Unreal Socket Authoring Executor 是 R40 API-limited execution readiness 证据，Unreal Socket Native Bridge Readiness 是 R60 native handoff contract 证据。

## R54 Gameplay Attach Fixture

R54 把 socket readiness 推到实际玩法装备挂接：manifest 声明 `rifle-primary-equip` 和 `backpack-temp-equip` 两个 gameplay intent，Unreal 5.3.2 headless 只读检查 attachable StaticMesh、AnimSequence、Actor/SceneComponent attach API，以及 R38 runtime socket facts。

当前结果：L3-linked / `Blocked` / `unreal_gameplay_attach_fixture_linked`；2 intents，0 Ready / 0 Review / 2 Blocked；attachable assets present=2，animation assets present=2；required/missing runtime sockets=4 / 4；required/missing hotspot semantics=2 / 1；15 pass / 1 warning / 6 error；assetWrites / productionWrites = 0 / 0。

业务结论：prop 资产和动画资产存在还不够，角色 Skeleton 上的 socket 合约没落地时，equip/attach 就必须被工具挡住并输出 owner action。
