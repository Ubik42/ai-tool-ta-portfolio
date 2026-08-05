# Groom Export Inspector

R46/R47/R48/R49/R50/R52/R55/R59 目标：把 Lightbox 提炼出的 XGen / groom 到 Unreal 高价值链路从计划推进到 Maya runtime L3、Unreal runtime readiness、真实 Maya Alembic cache receipt、Unreal import/post-check readiness、Groom plugin/API public fixture readiness、controlled executor rollback proof、runtime fact readback 和 group/root projection 细分，覆盖 root UV、strand ID、guide curve、curve-only Alembic payload、Maya `AbcExport`、Unreal Groom / Binding intent、目标 SkeletalMesh、Groom/Alembic API 可见性、cache sha256 continuity、AssetImportTask dry-run、HairStrands/AlembicHairImporter 项目配置、真实 `GroomAsset` / `GroomBindingAsset` post-check、runtime 属性/方法/调用事实回读、curve root 投影、groom group、guide coverage、material slot routing 和回滚边界。

## 核心业务逻辑

Groom 不是普通 mesh 导出。头发资产出问题时，常见失败不是模型拓扑，而是下游无法稳定绑定和复现：

- 每根 strand 是否有稳定 ID，便于 cache diff 和错误定位。
- root UV 是否存在且在 [0,1] 范围，保证 Unreal Binding 能把毛发根部贴回 scalp。
- guide curve 是否随导出保留，避免插值发束失去作者控制。
- Alembic payload 是否明确包含 root UV / strand ID / guide curve。
- Unreal Groom、Binding、SkeletalMesh、material slot 是否已声明。
- Unreal runtime 是否暴露 GroomAsset / GroomBindingAsset、AssetImportTask、AlembicImportFactory，以及目标 SkeletalMesh 是否存在。
- R48 `.abc` cache 是否能被 Unreal runtime 读到并和 receipt sha256 对齐。
- Unreal import/post-check 是否能 dry-run 出任务、工厂、目标资产和 no-write gate。
- public Unreal project 是否显式请求 HairStrands / AlembicHairImporter / AlembicImporter / GeometryCache，并在 runtime 中暴露 Groom import API。
- approved `.abc` 进入真实 Unreal `AssetImportTask` 后，产物是否确实是 `GroomAsset`，是否能继续创建 `GroomBindingAsset`，是否能在资产存在期间读取 runtime 属性、方法面和 callable facts，以及失败时是否能干净回滚。
- strand root CV 投影回 scalp `root_uv` 后，是否与存储 root UV、groom group UV 区间、guide 覆盖和 Unreal hair material slot 一致。
- 临时 description / TMP groom 是否被拦截在 owner review。

## 当前实现

代码入口：

- `dcc-hosts/groom-export-inspector/fixtures/synthetic_groom_export_scene.json`
- `dcc-hosts/groom-export-inspector/fixtures/synthetic_groom_group_projection_scene.json`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/contract.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/maya_collector.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/unreal_readiness.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/alembic_payload.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/alembic_import_postcheck.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/plugin_api_fixture.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/controlled_executor.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/groom_runtime_facts.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/group_root_projection.py`
- `dcc-hosts/groom-export-inspector/scripts/run_smoke.py`
- `dcc-hosts/groom-export-inspector/scripts/run_l3_smoke.py`
- `dcc-hosts/groom-export-inspector/scripts/run_maya_l3.py`
- `dcc-hosts/groom-export-inspector/scripts/run_unreal_readiness.py`
- `dcc-hosts/groom-export-inspector/scripts/run_alembic_payload.py`
- `dcc-hosts/groom-export-inspector/scripts/run_alembic_import_postcheck.py`
- `dcc-hosts/groom-export-inspector/scripts/run_groom_plugin_api_fixture.py`
- `dcc-hosts/groom-export-inspector/scripts/run_groom_controlled_executor.py`
- `dcc-hosts/groom-export-inspector/scripts/run_groom_runtime_facts.py`
- `dcc-hosts/groom-export-inspector/scripts/run_group_root_projection.py`
- `dcc-hosts/groom-export-inspector/scripts/run_maya_group_root_projection.py`
- `dcc-hosts/groom-export-inspector/scripts/run_maya_alembic_payload.py`
- `dcc-hosts/groom-export-inspector/scripts/unreal_python/probe_groom_import_readiness.py`
- `dcc-hosts/groom-export-inspector/scripts/unreal_python/probe_groom_alembic_import_postcheck.py`
- `dcc-hosts/groom-export-inspector/scripts/unreal_python/probe_groom_plugin_api_fixture.py`
- `dcc-hosts/groom-export-inspector/scripts/unreal_python/execute_groom_controlled_executor.py`
- `dcc-hosts/groom-export-inspector/scripts/unreal_python/collect_groom_runtime_facts.py`

R46 已完成：

- L2 contract：2 个 public-safe groom rows，1 Ready，1 intentionally Blocked。
- Maya L3：Maya 2026 `mayapy` 创建 synthetic scalp planes 和 curve strands，再从 Maya 场景回读 root UV、strand ID、guide flag、Alembic export payload 和 Unreal binding intent。
- Presenter Pack 接入：R46 Presenter Pack 探测 Groom Export Inspector Maya L3 artifact，并把 demo route 扩到 35 步。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r46` / `dcc-first-package@1.43.0`。
- R47 Unreal readiness：Unreal 5.3.2 commandlet 读取 R46 Maya groom facts，检查 AssetImportTask、AlembicImportFactory、GroomAsset / GroomBindingAsset API、目标 `SK_HeroFace`、期望 Groom / Binding 资产和 no-write boundary。
- Presenter Pack 接入：R47 Presenter Pack 探测 Groom Unreal Import Readiness artifact，并把 demo route 扩到 36 步、evidence probes 扩到 45 个。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r47` / `dcc-first-package@1.44.0`。
- R48 Alembic payload：Maya 2026 `mayapy` 加载 `AbcExport`，只选择 approved groom 行写出 public synthetic `.abc` cache，记录 bytes / sha256，并把 TMP groom 保持 held。
- Presenter Pack 接入：R48 Presenter Pack 探测 Groom Alembic Payload Receipt 和实际 `.abc` cache，并把 demo route 扩到 37 步、evidence probes 扩到 47 个。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r48` / `dcc-first-package@1.45.0`。
- R49 Alembic import/post-check：Unreal 5.3.2 commandlet 读取 R48 `.abc` cache，验证 sha256 continuity，dry-run `AssetImportTask`，检查 Alembic factory、Groom API、目标 `SK_HeroFace`、期望 Groom / Binding 资产和 no-write boundary。
- Presenter Pack 接入：R49 Presenter Pack 探测 Groom Alembic Import/Post-check artifact，并把 demo route 扩到 38 步、evidence probes 扩到 48 个。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r49` / `dcc-first-package@1.46.0`。
- R50 plugin/API fixture：public Unreal `.uproject` 显式启用 `GeometryCache`、`AlembicImporter`、`HairStrands`、`AlembicHairImporter`，Unreal 5.3.2 commandlet 进入项目后采集 Groom / Hair / Alembic / GeometryCache class surface。
- Presenter Pack 接入：R50 Presenter Pack 探测 Groom Plugin/API Public Fixture artifact，并把 demo route 扩到 39 步、evidence probes 扩到 49 个。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r50` / `dcc-first-package@1.47.0`。
- R52 controlled executor：Unreal 5.3.2 commandlet 只选择 approved curve-only groom cache，创建 `/Game/AI_Tool_TA/Grooms` public fixture 目录，通过 `HairStrandsFactory` 执行 `AssetImportTask`，检查 `GroomAsset`、`GroomLibrary` binding API、`GroomBindingAsset`、commandlet HairStrands logs 和 rollback receipt。
- Presenter Pack 接入：R52 Presenter Pack 探测 Groom Controlled Executor artifact，并把 demo route 扩到 40 步、evidence probes 扩到 50 个。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r52` / `dcc-first-package@1.49.0`。
- R55 runtime facts：Unreal 5.3.2 在 controlled executor 证据之上重新导入 approved curve-only public cache，创建 `GroomAsset` / `GroomBindingAsset`，在资产存在期间读取 package、property、method surface 和 callable facts，然后 rollback。
- Presenter Pack 接入：R55 Presenter Pack 探测 Groom Runtime Fact Collector artifact，并把 demo route 扩到 43 步、evidence probes 扩到 53 个。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r55` / `dcc-first-package@1.52.0`。
- R59 group/root projection：Maya 2026 `mayapy` 创建 grouped groom public fixture，从 curve root CV 投影到 scalp `root_uv`，检查 group definition、strand membership、projection drift、group UV region、guide coverage、material-slot routing 和 Alembic group payload。
- Presenter Pack 接入：R59 Presenter Pack 探测 Groom Group / Root Projection artifact，并把 demo route 扩到 48 步、evidence probes 扩到 58 个。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r59` / `dcc-first-package@1.56.0`。

## 证据

当前 Maya L3 artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-export-inspector-maya-l3-20260806-003711.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r59-groom-group-root-projection-presentation-pack-20260806-052010.json
```

关键结果：

- report version：`groom-export-inspector-maya-l3@0.1.0`
- evidence level：L3
- l3 status：`maya_groom_export_facts_collected`
- Maya runtime：2026
- assets ready / review / blocked：1 / 0 / 1
- strands / guides：11 / 2
- root UV missing / duplicate strand IDs：1 / 1
- checks pass / warning / error：11 / 2 / 7
- owner actions：9
- assetWrites / productionWrites：0 / 0

Gate 为 `Blocked` 是正确状态：`Hero Hair Approved` Ready；`Hero Hair Temporary Groom` 保留 TMP description、缺 root_uv scalp set、duplicate strand ID、missing root UV、guide 缺失、Alembic payload flags 缺失、frame range 错误和 Unreal binding intent 缺失。

当前 Unreal readiness artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-unreal-readiness-20260806-010008.json
```

关键结果：

- report version：`groom-unreal-readiness@0.1.0`
- evidence level：L3
- l3 status：`unreal_groom_import_readiness_collected`
- Unreal runtime：5.3.2
- source rows Ready / Blocked：1 / 1
- AssetImportTask / AlembicImportFactory visible rows：2 / 2
- GroomAsset / GroomBindingAsset API visible rows：0 / 0
- target SkeletalMesh present rows：1
- expected Groom / Binding assets present rows：0 / 0
- checks pass / warning / error：12 / 4 / 6
- owner actions：10
- assetWrites / productionWrites：0 / 0

Gate 为 `Blocked` 是正确状态：R47 已证明 UE runtime 可以进入并读取目标 `SK_HeroFace`，但本 public project 还没有可用的 GroomAsset / GroomBindingAsset API surface，也还没有导入期望的 Groom / Binding 资产；这必须作为 Alembic executor 之前的 readiness gate 暴露。

当前 Alembic Payload artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-alembic-payload-20260806-030023.json
<repo>\dcc-hosts\groom-export-inspector\artifacts\cache\groom-alembic-r52-hair-schema\groom_hero_hair_001.abc
```

关键结果：

- report version：`groom-alembic-payload@0.2.0`
- evidence level：L3
- l3 status：`maya_groom_curve_only_alembic_payload_exported`
- Maya runtime：2026
- selected / held rows：1 / 1
- cache files / bytes / hashes：1 / 12808 / 1
- curve-only / schema inspected / schema compatible / meshShapeRows：2 / 1 / 1 / 0
- checks pass / warning / error：16 / 0 / 2
- owner actions：2
- assetWrites / engineWrites / productionWrites：1 / 0 / 0

Gate 为 `Blocked` 是正确状态：approved groom 已写出真实 public synthetic curve-only Alembic cache，并通过 Maya AbcImport schema probe 确认 `meshShapeRows=0`；TMP groom 仍因 source groom row 和 cache payload contract 不合格被 held，不进入 cache。

当前 Alembic Import/Post-check artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-alembic-import-postcheck-20260806-030028.json
```

关键结果：

- report version：`groom-alembic-import-postcheck@0.1.0`
- evidence level：L3
- l3 status：`unreal_groom_alembic_import_postcheck_blocked`
- Unreal runtime：5.3.2
- operations / import candidates：2 / 1
- cache hash matched rows：1
- AssetImportTask dry-run / Alembic factory visible / Groom API ready：2 / 2 / 2
- target SkeletalMesh present rows：1
- expected Groom / Binding assets present rows：0 / 0
- import executed / held：0 / 2
- checks pass / warning / error：25 / 2 / 1
- owner actions：3
- assetWrites / engineWrites / productionWrites：0 / 0 / 0

Gate 为 `Blocked` 是正确状态：R52 post-check 已证明 curve-only `.abc` 可以被 Unreal runtime 读取并和 sha256 receipt 对齐，AssetImportTask/Alembic factory 可 dry-run，Groom API ready，`SK_HeroFace` 存在；它仍保持 no-write，因为真实导入和 BindingAsset 创建必须进入 controlled executor，而不是在 readiness probe 中偷偷写资产。

当前 Groom Plugin/API Fixture artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-plugin-api-fixture-20260806-020048.json
```

关键结果：

- report version：`groom-plugin-api-fixture@0.1.0`
- evidence level：L3
- l3 status：`unreal_groom_plugin_api_fixture_ready`
- Unreal runtime：5.3.2
- required plugin descriptors / project requests：4 / 4
- Groom / Hair / Alembic / GeometryCache class rows：47 / 56 / 14 / 16
- Groom import API ready / AlembicImportFactory visible：true / true
- checks pass / warning / error：10 / 0 / 0
- assetWrites / engineWrites / productionWrites：0 / 0 / 0

Gate 为 `Ready`：R50 证明 R49 的 Groom API 缺口来自 public project 未显式请求 HairStrands/Alembic hair stack，而不是本机 UE 缺失这些插件。R52 已继续进入真实 GroomAsset / BindingAsset 创建、post-check 和 rollback receipt。

当前 Groom Controlled Executor artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-controlled-executor-20260806-030046.json
```

关键结果：

- report version：`groom-controlled-executor@0.1.0`
- evidence level：L3
- l3 status：`unreal_groom_executor_import_binding_rolled_back`
- Unreal runtime：5.3.2
- selected / import attempted / import succeeded：1 / true / true
- imported asset class：`GroomAsset`
- wrong imported class：false
- GroomAsset post-check / BindingAsset post-check：true / true
- binding attempted：true，通过 `GroomLibrary.create_new_groom_binding_asset_with_path`
- rollback passed / residual assets：true / 0
- checks pass / warning / error：11 / 0 / 0
- assetWrites / engineWrites / productionWrites：6 / 0 / 0
- persistent mutation：false

Gate 为 `Ready`：R52 证明关键阻断不在 Unreal runtime 或项目插件，而在 Alembic payload schema。旧 asset-root cache 混入 scalp mesh 后会被泛 Alembic 路径消费；curve-only cache 满足 UE Hair translator 条件后，`HairStrandsFactory` 能导入 `GroomAsset`，并能在同一 commandlet 中创建、检查和回滚 `GroomBindingAsset`。

当前 Groom Runtime Fact Collector artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-runtime-facts-20260806-040118.json
```

关键结果：

- report version：`groom-runtime-facts@0.1.0`
- evidence level：L3
- l3 status：`unreal_groom_runtime_facts_collected`
- Unreal runtime：5.3.2
- runtime assets present：3，分别是 `GroomAsset`、`GroomBindingAsset` 和目标 `SkeletalMesh`
- readable properties / method surface / callable facts：23 / 40 / 11
- checks pass / warning / error：11 / 0 / 0
- rollback passed / residual assets：true / 0
- assetWrites / engineWrites / productionWrites：6 / 0 / 0

Gate 为 `Ready`：R55 证明 Groom 线已经不只是导入成功，而是能在真实 Unreal 资产存在期间回读审查所需 runtime surface，并在同一 commandlet 内清理所有 public fixture residue。

当前 Groom Group / Root Projection artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-group-root-projection-20260806-051721.json
```

关键结果：

- report version：`groom-group-root-projection@0.1.0`
- evidence level：L3
- l3 status：`maya_groom_group_root_projection_collected`
- Maya runtime：2026
- assets ready / review / blocked：1 / 0 / 1
- strand projection rows / group coverage rows：10 / 4
- projection matched / group matched / material matched strands：6 / 7 / 8
- max projection drift：0.175
- checks pass / warning / error：10 / 1 / 7
- assetWrites / engineWrites / productionWrites：0 / 0 / 0

Gate 为 `Blocked` 是正确状态：approved groom 已证明 6 / 6 root projection 匹配、3 / 3 group coverage 匹配；TMP groom 被 draft protocol、缺失/重复 strand identity、root projection drift、undeclared group、guide 缺失、target scalp section 缺失、material slot 和 Alembic group payload 问题阻断。

## 后续

下一阶段可以继续做：

- 增加更多 hair schema 变体：不同 guide density、宽度/root UV 属性缺失、错误 scalp proximity、LOD hair group split。
- 增加更多导入后 GroomAsset / BindingAsset 细分项：group count、binding target mesh、root projection stats；如果 Python surface 不足，再评估 Editor Utility / C++ bridge。
- 将 Groom 证据接入 Maya GUI 的专用 reviewer panel，展示 root UV、guide、curve-only cache hash、import post-check 和 rollback receipt 的闭环。
