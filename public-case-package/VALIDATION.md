# Validation Ledger

## Current DCC-first Validation

| Command id | Command | Proves |
| --- | --- | --- |
| `validate-r56-houdini-rule-adapter` | `python dcc-hosts/houdini-rule-adapter/scripts/run_smoke.py` | Houdini Rule Adapter exports L2+ contract evidence from public fixtures: HDA metadata, detail attributes, `OUT_*` roles, packed prototypes, PDG wedges and frozen bake receipts normalize into Cross-DCC rule rows; 2 assets, 1 Ready, 1 Blocked, 11 / 2 / 5 checks. |
| `validate-r56-houdini-l3-readiness` | `python dcc-hosts/houdini-rule-adapter/scripts/run_l3_smoke.py` | The hython launcher searches PATH, `AI_TOOL_TA_HYTHON` and common SideFX paths, confirms collector readiness, and reports `Blocked` because `hython.exe` is not installed or discoverable on this machine. |
| `validate-r56-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r56-houdini-rule-adapter-presentation-pack")` | DCC Presenter Pack probes 55 key evidence files including Houdini contract/readiness artifacts, reports 55 present / 0 missing required files, and exports 45 demo route steps. |
| `validate-r55-groom-runtime-facts` | `python dcc-hosts/groom-export-inspector/scripts/run_groom_runtime_facts.py` | Unreal 5.3.2 headless imports the approved curve-only GroomAsset / GroomBindingAsset fixture, reads runtime property/method/call facts while assets exist, and rolls back. Reports L3 Ready, 3 runtime assets present, 23 readable properties, 40 method-surface entries, 11 callable facts, 11 / 0 / 0 checks, residual assets=0, assetWrites=6, productionWrites=0. |
| `validate-r55-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r55-groom-runtime-facts-presentation-pack")` | DCC Presenter Pack probes 53 key evidence files including Groom Runtime Fact Collector, reports 53 present / 0 missing required files, and exports 43 demo route steps. |
| `validate-r54-unreal-gameplay-attach-fixture` | `python dcc-hosts/unreal-socket-import-checker/scripts/run_gameplay_attach_fixture.py` | Unreal 5.3.2 headless links R38 socket facts and gameplay attach manifest to runtime attachable/animation/API facts. Reports L3-linked, 2 intents, 0 Ready, 2 Blocked, attachable assets present=2, animation assets present=2, missing runtime sockets=4, 15 / 1 / 6 checks, and assetWrites=0 / productionWrites=0. |
| `validate-r54-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r54-unreal-gameplay-attach-fixture-presentation-pack")` | DCC Presenter Pack probes 52 key evidence files including Unreal Gameplay Attach Fixture, reports 52 present / 0 missing required files, and exports 42 demo route steps. |
| `validate-r53-max-texture-manifest-link` | `python dcc-hosts/3dsmax-rule-adapter/scripts/run_texture_manifest_link.py` | Reads the latest real 3ds Max `pymxs` L3 artifact and joins material bitmap slots to the public texture delivery manifest. Reports L3-derived, 2 assets, 1 Ready, 1 Blocked, 3 material rows, 4 slot textures, 4 manifest textures, 0 missing manifest textures, 2 missing required semantics, and 13 / 1 / 2 checks. |
| `validate-r53-max-l3-runtime` | `python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py --run-runtime --timeout-seconds 600` | 3ds Max 2022 batch runs the public fixture through `pymxs`, exports `max-rule-adapter-pymxs-l3@0.1.0`, and includes material-to-texture rows for R53 package-link validation. |
| `validate-r53-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r53-max-texture-manifest-link-presentation-pack")` | DCC Presenter Pack probes 51 key evidence files including Max Material Texture Manifest Link, reports 51 present / 0 missing required files, and exports 41 demo route steps. |
| `validate-r52-groom-controlled-executor` | `python dcc-hosts/groom-export-inspector/scripts/run_groom_controlled_executor.py` | Unreal 5.3.2 Python selects the approved curve-only groom `.abc`, executes `AssetImportTask` through `HairStrandsFactory`, creates `GroomAsset` and `GroomBindingAsset`, verifies post-checks, rolls back public fixture writes, reports residual assets=0, and keeps engineWrites=0 / productionWrites=0. |
| `validate-r52-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r52-groom-hair-schema-executor-presentation-pack")` | DCC Presenter Pack probes 50 key evidence files including curve-only Groom Controlled Executor, reports 50 present / 0 missing required files, and exports 40 demo route steps. |
| `validate-r50-groom-plugin-api-fixture` | `python dcc-hosts/groom-export-inspector/scripts/run_groom_plugin_api_fixture.py` | Unreal 5.3.2 Python enters the public project with HairStrands/Alembic plugins enabled, verifies 4/4 descriptors, 4/4 project requests, Groom import API readiness, Alembic factory visibility and zero asset/engine/production writes. |
| `validate-r50-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r50-groom-plugin-api-fixture-presentation-pack")` | DCC Presenter Pack probes 49 key evidence files including Groom Plugin/API Public Fixture Readiness, reports 49 present / 0 missing required files, and exports 39 demo route steps. |
| `validate-r49-groom-alembic-import-postcheck` | `python dcc-hosts/groom-export-inspector/scripts/run_alembic_import_postcheck.py` | Unreal 5.3.2 Python enters the public project, reads the R48 `.abc` cache, verifies cache sha256 continuity, dry-runs AssetImportTask / AlembicImportFactory setup, confirms target `SK_HeroFace`, holds import execution, reports Groom API and expected Groom / Binding asset gaps, and keeps assetWrites=0. |
| `validate-r49-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r49-groom-alembic-import-postcheck-presentation-pack")` | DCC Presenter Pack probes 48 key evidence files including Groom Alembic Import/Post-check Readiness, reports 48 present / 0 missing required files, and exports 38 demo route steps. |
| `validate-r48-groom-alembic-payload` | `python dcc-hosts/groom-export-inspector/scripts/run_alembic_payload.py` | Maya 2026 `mayapy` loads `AbcExport`, writes the approved public groom row to `.abc`, records cache bytes/hash, holds the TMP groom row, and keeps engineWrites=0 / productionWrites=0. |
| `validate-r48-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r48-groom-alembic-payload-presentation-pack")` | DCC Presenter Pack probes 47 key evidence files including Groom Alembic Payload Receipt and exported cache, reports 47 present / 0 missing required files, and exports 37 demo route steps. |
| `validate-r47-groom-unreal-readiness` | `python dcc-hosts/groom-export-inspector/scripts/run_unreal_readiness.py` | Unreal 5.3.2 Python enters the public project and exports read-only Groom import readiness: 2 groom rows, source Ready / Blocked = 1 / 1, AssetImportTask and AlembicImportFactory visible, `SK_HeroFace` present, GroomAsset / GroomBindingAsset API not visible, expected Groom / Binding assets absent, 12 pass / 4 warning / 6 error, assetWrites=0. |
| `validate-r47-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r47-groom-unreal-readiness-presentation-pack")` | DCC Presenter Pack probes 45 key evidence files including Groom Unreal Import Readiness, reports 45 present / 0 missing required files, and exports 36 demo route steps. |
| `validate-r46-groom-export-inspector` | `python dcc-hosts/groom-export-inspector/scripts/run_l3_smoke.py` | Maya 2026 mayapy creates the public groom fixture and exports L3 groom handoff facts: 2 groom rows, 1 Ready, 1 Blocked, 11 strands, 2 guides, 1 missing root UV row, 1 duplicate strand ID row, 11 pass / 2 warning / 7 error, assetWrites=0. |
| `validate-r46-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r46-groom-export-inspector-presentation-pack")` | DCC Presenter Pack probes 44 key evidence files including Groom Export Inspector, reports 44 present / 0 missing required files, and exports 35 demo route steps. |
| `validate-r45-unreal-control-rig-compile-status` | `python dcc-hosts/unreal-control-rig-bridge/scripts/run_compile_status.py` | Unreal 5.3.2 Python invokes public `CR_HeroFace` compile methods: 2 character rows, approved row Review, TMP row Blocked, compile method visible / invoked / succeeded = 1 / 1 / 1, direct status 0, diagnostics 0, compile settings 1, dirtyAfter=0, assetWrites=0, productionWrites=0. |
| `validate-r45-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r45-unreal-control-rig-compile-status-presentation-pack")` | DCC Presenter Pack probes 43 key evidence files including Control Rig Compile Status Bridge, reports 43 present / 0 missing required files, and exports 34 demo route steps. |
| `validate-r44-unreal-control-rig-face-skeleton-fixture` | `python dcc-hosts/unreal-control-rig-bridge/scripts/run_face_skeleton_fixture.py` | Maya 2026 mayapy generates a public face Skeleton FBX; Unreal 5.3.2 imports `SK_HeroFace` / `SK_HeroFace_Skeleton`; required target matches are 4 / 4, previous R43 missing targets resolved are 3 / 3, assetWrites=2, productionWrites=0. |
| `validate-r44-unreal-control-rig-bridge-post-face-skeleton` | `python dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py` | Post-face bridge reads `SK_HeroFace` / `SK_HeroFace_Skeleton` and `CR_HeroFace`: 2 character rows, approved row Ready, TMP row Blocked, 10 pass / 1 warning / 5 error, assetWrites=0. |
| `validate-r44-unreal-control-rig-deformation-link-post-face-skeleton` | `python dcc-hosts/unreal-control-rig-bridge/scripts/run_deformation_link.py` | Post-face deformation-link reports 5 Skeleton target matches, approved row Review, TMP row Blocked, 13 pass / 2 warning / 5 error, assetWrites=0. |
| `validate-r44-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r44-unreal-control-rig-face-skeleton-fixture-presentation-pack")` | DCC Presenter Pack probes 42 key evidence files including Face Skeleton Fixture, reports 42 present / 0 missing required files, and exports 33 demo route steps. |
| `validate-r43-unreal-control-rig-deformation-link` | `python dcc-hosts/unreal-control-rig-bridge/scripts/run_deformation_link.py` | Unreal 5.3.2 Python reads `CR_HeroFace`, maps 10 controls across 2 character rows, confirms 5 runtime controls, 5 shape/offset-readable controls, 2 Skeleton target matches, 0 direct compile-status rows, and keeps assetWrites=0. |
| `validate-r43-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r43-unreal-control-rig-deformation-link-presentation-pack")` | DCC Presenter Pack probes 41 key evidence files including Control Rig Deformation Link, reports 41 present / 0 missing required files, and exports 32 demo route steps. |
| `validate-r42-unreal-control-rig-fixture-authoring` | `python dcc-hosts/unreal-control-rig-bridge/scripts/run_fixture_authoring.py` | Unreal 5.3.2 Python creates `CR_HeroFace` under `/Game/AI_Tool_TA`, adds 5 required controls to the runtime hierarchy, saves 1 public fixture asset, and keeps productionWrites=0. |
| `validate-r42-unreal-control-rig-bridge-post-authoring` | `python dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py` | Post-authoring bridge reports 2 character rows with approved `char-hero-head-001` Ready, TMP row Blocked, 10 pass / 1 warning / 5 error and assetWrites=0. |
| `validate-r42-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r42-unreal-control-rig-fixture-authoring-presentation-pack")` | DCC Presenter Pack probes 40 key evidence files including Control Rig Fixture Authoring, reports 40 present / 0 missing required files, and exports 31 demo route steps. |
| `validate-r41-unreal-animation-deep-facts` | `python dcc-hosts/unreal-animation-bridge/scripts/run_deep_facts.py` | Unreal 5.3.2 Python reads 2 existing public AnimSequence assets without import/save, matches 2 / 2 duration frame spans, records curve/root/compression metadata visibility, and keeps assetWrites=0. |
| `validate-r41-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r41-unreal-animation-deep-facts-presentation-pack")` | DCC Presenter Pack probes 39 key evidence files including Unreal AnimSequence Deep Facts, reports 39 present / 0 missing required files, and exports 30 demo route steps. |
| `validate-r40-unreal-socket-authoring-executor` | `python dcc-hosts/unreal-socket-import-checker/scripts/run_socket_authoring_executor.py` | Unreal 5.3.2 Python selects 1 approved socket operation and holds 1 blocked row; the gate is L3 / Blocked / `unreal_socket_authoring_executor_api_limited` because `socket_name` and `bone_name` are read-only in commandlet-created sockets, with 9 pass, 0 warning, 2 error and assetWrites=0. |
| `validate-r40-unreal-socket-api-docs` | `UnrealEditor-Cmd -run=pythonscript scripts/unreal_python/probe_socket_api_docs.py` | Captures UE 5.3 socket authoring API docstrings and property write attempts, proving `add_socket(socket, add_to_skeleton=False)` is visible while socket identity fields are read-only. |
| `validate-r40-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r40-unreal-socket-authoring-executor-presentation-pack")` | DCC Presenter Pack probes 38 key evidence files including Unreal Socket Authoring Executor and API docs, reports 38 present / 0 missing required files, and exports 29 demo route steps. |
| `validate-r39-platform-variant-staticmesh-postcheck` | `python dcc-hosts/platform-variant-forge/scripts/run_staticmesh_postcheck.py` | Unreal 5.3.2 Python validates 5 R34 StaticMesh LOD / Nanite / collision receipts against read-only runtime facts: 2 target assets present, 2 / 2 no-op receipts matched, 3 owner-held rows, 32 pass, 3 warning, 0 error and assetWrites=0. |
| `validate-r39-dcc-presenter-pack` | `Maya mayapy dcc_presentation_build_pack(label="r39-platform-variant-staticmesh-postcheck-presentation-pack")` | DCC Presenter Pack probes 36 key evidence files including Platform Variant StaticMesh Post-check, reports 36 present / 0 missing required files, and exports 28 demo route steps. |
| `validate-r38-unreal-socket-import-checker` | `python dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py` | Unreal 5.3.2 Python collects SkeletalMesh/Skeleton socket API readiness and expected socket coverage from Spatial Authoring drilldown facts, reporting L3 / Blocked with 9 pass, 2 warnings, 9 errors and assetWrites=0. |
| `validate-r38-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r38-unreal-socket-import-checker-presentation-pack")` | DCC Presenter Pack probes 35 key evidence files including Unreal Socket Import Checker, reports 35 present / 0 missing required files, and exports 27 demo route steps. |
| `validate-r37-unreal-control-rig-bridge` | `python dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py` | Unreal 5.3.2 Python collects Control Rig API, SkeletalMesh/Skeleton binding and expected Control Rig asset coverage from Character Calibration drilldown facts, reporting L3 / Blocked with 8 pass, 1 warning, 7 errors and assetWrites=0. |
| `validate-r37-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r37-unreal-control-rig-bridge-presentation-pack")` | DCC Presenter Pack probes 34 key evidence files including Unreal Control Rig Bridge, reports 34 present / 0 missing required files, and exports 26 demo route steps. |
| `validate-r36-spatial-authoring-drilldown` | `python dcc-hosts/spatial-authoring-workbench/scripts/run_drilldown.py` | Maya L3 spatial authoring facts are converted into 2 UI-ready drilldowns, 18 panels, 9 issue rows, 9 owner actions, 7 owner-required actions and 2 manual-review actions. |
| `validate-r36-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r36-spatial-authoring-drilldown-presentation-pack")` | DCC Presenter Pack probes 33 key evidence files including Spatial Authoring Drilldown, reports 33 present / 0 missing required files, and exports 25 demo route steps. |
| `validate-r35-character-calibration-drilldown` | `python dcc-hosts/character-calibration-studio/scripts/run_drilldown.py` | Maya L3 character calibration facts are converted into 2 UI-ready drilldowns, 14 panels, 8 issue rows, 8 owner actions, 6 owner-required actions and 2 manual-review actions. |
| `validate-r35-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r35-character-calibration-drilldown-presentation-pack")` | DCC Presenter Pack probes 32 key evidence files including Character Calibration Drilldown, reports 32 present / 0 missing required files, and exports 24 demo route steps. |
| `validate-r34-platform-variant-executor-expansion` | `python dcc-hosts/platform-variant-forge/scripts/run_executor_expansion.py` | R30 LOD/Nanite/collision generation operations are converted into 5 approval / rollback receipts linked to the R33 rolled-back Unreal executor proof: 2 no-op verified, 1 approval-ready, 2 readiness-only, 0 blocked. |
| `validate-r34-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r34-platform-variant-executor-expansion-presentation-pack")` | DCC Presenter Pack probes 31 key evidence files including Platform Variant Executor Expansion Receipts, reports 31 present / 0 missing required files, and exports 23 demo route steps. |
| `validate-r33-platform-variant-controlled-executor` | `python dcc-hosts/platform-variant-forge/scripts/run_controlled_executor.py` | Unreal 5.3.2 Python applies `/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor` max texture size 0 -> 2048, verifies the post-state, rolls back to fingerprint `2502b08c541495a4`, and reports 7 pass checks, 0 warnings and 0 errors. |
| `validate-r33-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r33-platform-variant-controlled-executor-presentation-pack")` | DCC Presenter Pack probes 30 key evidence files including Platform Variant Controlled Executor, reports 30 present / 0 missing required files, and exports 22 demo route steps. |
| `validate-r32-platform-variant-texture-payload` | `python dcc-hosts/platform-variant-forge/scripts/run_texture_payload_probe.py` | Unreal 5.3.2 Python imports a generated public 2048 Texture2D, wires it to `M_HeroPanel`, and rechecks 3 variants as 2 Ready / 0 Review / 1 Blocked with 20 pass checks, 0 warnings and 1 error. |
| `validate-r32-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r32-platform-variant-texture-payload-presentation-pack")` | DCC Presenter Pack probes 29 key evidence files including Platform Variant Public Texture2D Payload Fixture, reports 29 present / 0 missing required files, and exports 21 demo route steps. |
| `validate-r31-platform-variant-texture-runtime` | `python dcc-hosts/platform-variant-forge/scripts/run_texture_runtime_probe.py` | Unreal 5.3.2 Python collects material slot, dependency query and Texture2D budget facts for 3 planned variants, reporting 1 Ready / 1 Review / 1 Blocked, 19 pass checks, 1 warning and 1 error. |
| `validate-r31-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r31-platform-variant-texture-runtime-presentation-pack")` | DCC Presenter Pack probes 28 key evidence files including Platform Variant Texture Runtime Collector, reports 28 present / 0 missing required files, and exports 20 demo route steps. |
| `validate-r30-platform-variant-generation-plan` | `python dcc-hosts/platform-variant-forge/scripts/run_generation_plan.py` | R29 runtime drift is converted into `platform-variant-generation-plan@0.1.0`, reporting 11 dry-run operations: 1 Ready, 3 Review, 2 Blocked and 5 Satisfied, with owner approval and rollback boundaries. |
| `validate-r30-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r30-platform-variant-generation-plan-presentation-pack")` | DCC Presenter Pack probes 27 key evidence files including Platform Variant Generation Planner, reports 27 present / 0 missing required files, and exports 19 demo route steps. |
| `validate-r29-platform-variant-unreal-runtime` | `python dcc-hosts/platform-variant-forge/scripts/run_unreal_runtime_probe.py` | Unreal 5.3.2 Python collects runtime StaticMesh facts for 3 planned variants, reports 0 Ready / 2 Review / 1 Blocked runtime variants, and compares runtime path, LOD, material, Nanite and collision state against the variant plan. |
| `validate-r29-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r29-platform-variant-unreal-runtime-presentation-pack")` | DCC Presenter Pack probes 26 key evidence files including Platform Variant Unreal Runtime Probe, reports 26 present / 0 missing required files, and exports 18 demo route steps. |
| `validate-r28-platform-variant-forge` | `python dcc-hosts/platform-variant-forge/scripts/run_smoke.py` | Contract evaluates 2 public source assets and 3 platform variants, reports 2 Ready variants and 1 Blocked Mobile variant, and joins the plan to Unreal preset fact comparison evidence. |
| `validate-r28-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r28-platform-variant-forge-presentation-pack")` | DCC Presenter Pack probes 25 key evidence files including Platform Variant Forge, reports 25 present / 0 missing required files, and exports 17 demo route steps. |
| `validate-r27-spatial-authoring-contract` | `python dcc-hosts/spatial-authoring-workbench/scripts/run_smoke.py` | Contract evaluates 2 public spatial authoring rows, reports 1 Ready and 1 Blocked socket/hotspot/pose-transfer sample without entering Maya. |
| `validate-r27-spatial-authoring-l3` | `python dcc-hosts/spatial-authoring-workbench/scripts/run_l3_smoke.py` | Maya 2026 `mayapy` creates synthetic joints/locators and exports `spatial-authoring-maya-l3@0.1.0`, reporting 2 assets, 1 Ready, 1 Blocked, 11 pass checks, 2 warnings and 7 errors. |
| `validate-r27-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r27-spatial-authoring-l3-presentation-pack")` | DCC Presenter Pack probes 24 key evidence files including Spatial Authoring Maya L3, reports 24 present / 0 missing required files, and exports 16 demo route steps. |
| `validate-r26-character-calibration-contract` | `python dcc-hosts/character-calibration-studio/scripts/run_smoke.py` | Contract evaluates 2 public character calibration rows, reports 1 Ready and 1 Blocked topology/joint/control mapping sample without entering Maya. |
| `validate-r26-character-calibration-l3` | `python dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py` | Maya 2026 `mayapy` creates synthetic character meshes/joints and exports `character-calibration-maya-l3@0.1.0`, reporting 2 assets, 1 Ready, 1 Blocked, 10 pass checks, 2 warnings and 6 errors. |
| `validate-r26-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r26-character-calibration-l3-presentation-pack")` | DCC Presenter Pack probes 23 key evidence files including Character Calibration Maya L3, reports 23 present / 0 missing required files, and exports 15 demo route steps. |
| `validate-r25-unreal-animation-bridge-contract` | `python dcc-hosts/unreal-animation-bridge/scripts/run_smoke.py` | Contract reads the Maya Animation Continuity L3 artifact, maps 2 takes to Unreal AnimSequence/Skeleton expectations, and reports 1 Ready / 1 Blocked before runtime import. |
| `validate-r25-unreal-animation-bridge-import-l3` | `python dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py` | Maya 2026 `mayapy` generates two public FBX clips, Unreal 5.3.2 imports synthetic Skeleton/SkeletalMesh/AnimSequence assets, reports 2 / 2 sequences present, 4 imported assets, 1 Ready clip and 1 Blocked business defect sample. |
| `validate-r25-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r25-unreal-animation-import-l3-presentation-pack")` | DCC Presenter Pack probes 22 key evidence files including Unreal Animation Bridge import L3, reports 22 present / 0 missing required files, and exports 14 demo route steps. |
| `validate-r24-unreal-animation-bridge-contract` | `python dcc-hosts/unreal-animation-bridge/scripts/run_smoke.py` | Contract reads the R23 Maya Animation Continuity L3 artifact, maps 2 takes to Unreal AnimSequence expectations, and reports 1 Ready / 1 Blocked before runtime asset probing. |
| `validate-r24-unreal-animation-bridge-readiness` | `python dcc-hosts/unreal-animation-bridge/scripts/run_l3_smoke.py` | Unreal 5.3.2 Python enters the public test project, probes AnimSequence / Skeleton API availability, reports 2 expected sequences missing, and keeps the bridge at L3-readiness instead of claiming full AnimSequence L3. |
| `validate-r24-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r24-unreal-animation-bridge-presentation-pack")` | DCC Presenter Pack probes 21 key evidence files including Unreal Animation Bridge readiness, reports 21 present / 0 missing required files, and exports 14 demo route steps. |
| `validate-r23-animation-continuity-l3` | `python dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py` | Maya 2026 `mayapy` runs the public synthetic animation fixture, exports `animation-continuity-maya-l3@0.1.0`, reports 2 animation takes, 1 Ready, 1 Blocked, 11 pass checks, 3 warnings, 6 errors, and real keyed animCurve collection. |
| `validate-r23-dcc-presenter-pack` | `Maya mayapy dcc_presentation_export_pack(label="r23-animation-continuity-l3-presentation-pack")` | DCC Presenter Pack probes 20 key evidence files including Animation Continuity, Blender, 3ds Max and Unreal runtime artifacts, reports 20 present / 0 missing required files, and exports 13 demo route steps. |
| `validate-r10-dcc-build` | `npm run build` | Current embedded React UI compiles for Maya/AuroraView. |
| `validate-r10-dcc-api` | `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` | Maya host API surface is syntactically valid. |
| `validate-r10-7-case-page` | `Maya 2024 mayapy showcase_runbook_export_case_page(label="r10-7-dcc-first-case-page")` | Case page exports 6 sections, 7 business route steps, 7 live demo script steps, 9 GUI shots, 1 recording, 4 artifact rows, and 6 reviewer claims. |
| `validate-r10-7-gui-media-audit` | `Maya 2024 mayapy showcase_runbook_export_gui_media_audit(label="r10-7-gui-media-audit")` | GUI media audit scans the R10.7 media root, exports 10 expected media rows, and correctly reports CapturePending with 10 missing files before real capture. |
| `validate-r10-7-handoff-decision` | `Maya 2024 mayapy asset_handoff_export_decision_packet(label="r10-7-dcc-first-case-page-runbook-asset-handoff-decision")` | Asset Handoff Decision Packet exports 2 repair preview rows, 2 owner disposition rows, 1 engine-ready intent, 1 held engine intent, and zero engine writes. |
| `validate-r10-8-engine-preflight` | `Maya 2024 mayapy engine_handoff_export_preflight_packet(label="r10-8-engine-handoff-preflight-fixture", platform_preset="pc")` | Engine Handoff Preflight exports 2 preflight rows, 1 dry-run import sidecar, 1 owner-held row, 8 passing checks, 1 hold check, and zero engine writes. |
| `validate-r10-9-engine-preset-comparison` | `Maya 2024 mayapy engine_handoff_export_preset_comparison(label="r10-9-engine-preset-comparison", platform_presets=["pc", "mobile"])` | Engine preset comparison exports 2 preset summaries, 2 asset comparison rows, 1 platform split, 1 held-across-presets row, 1 ready sidecar, and zero engine writes. |
| `validate-r22-blender-l3-runtime` | `python dcc-hosts/blender-rule-adapter/scripts/run_l3_smoke.py` | Blender 5.2.0 LTS runs the public synthetic fixture through `bpy`, exports `blender-rule-adapter-bpy-l3@0.1.0`, reports 2 assets, 1 Ready, 1 Blocked, 8 pass checks, 3 warnings, 1 error. |
| `validate-r22-max-l3-runtime` | `python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py --run-runtime --timeout-seconds 600` | 3ds Max 2022 batch runs the public synthetic fixture through `pymxs`, exports `max-rule-adapter-pymxs-l3@0.1.0`, reports 2 assets, 1 Ready, 1 Blocked, 13 pass checks, 5 warnings, 2 errors. |
| `validate-r22-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r22-blender-max-l3-presentation-pack")` | DCC Presenter Pack probes 19 key evidence files including Blender and Max runtime L3 artifacts, reports 19 present / 0 missing required files, and exports 12 demo route steps. |
| `validate-r21-max-rule-adapter` | `python dcc-hosts/3dsmax-rule-adapter/scripts/run_smoke.py` | 3ds Max Rule Adapter exports L2+ contract evidence from public fixtures: 2 assets, 1 Ready, 1 Blocked, 13 pass checks, 5 warnings, 2 errors, and Max batch availability. |
| `validate-r21-max-l3-readiness` | `python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py` | 3ds Max L3 readiness harness discovers `3dsmaxbatch.exe`, confirms collector readiness, keeps runtime launch opt-in, and reports `Review` without production writes. |
| `validate-r21-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r21-3dsmax-rule-adapter-presentation-pack")` | DCC Presenter Pack probes 19 key evidence files including Max adapter and Max L3 readiness, reports 19 present / 0 missing required files, and exports 12 demo route steps. |
| `validate-r20-blender-l3-harness` | `python dcc-hosts/blender-rule-adapter/scripts/run_l3_smoke.py` | Blender L3 readiness harness compiles the real `bpy` collector path, searches Blender CLI, reports collector ready, and records `Blocked` because this machine has no discoverable `blender.exe`. |
| `validate-r20-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r20-blender-l3-harness-presentation-pack")` | DCC Presenter Pack probes 17 key evidence files including Blender L3 readiness, reports 17 present / 0 missing required files, and exports 11 demo route steps. |
| `validate-r19-scene-transaction-guard` | `Maya 2024 mayapy scene_transaction_export_receipt(label="r19-scene-transaction-guard")` | Scene Transaction Guard exports before/after fingerprints, 2 created nodes, 2 deleted nodes, 2 modified nodes, selection/time changes, 9 rollback preview actions, and 4 risk rows. |
| `validate-r19-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r19-scene-transaction-guard-presentation-pack")` | DCC Presenter Pack probes 16 key evidence files including Scene Transaction Guard, reports 16 present / 0 missing required files, and exports 10 demo route steps. |
| `validate-r18-unreal-preset-fact-review` | `Maya 2024 mayapy unreal_preset_fact_review_export(label="r18-unreal-preset-fact-review")` | Maya-hosted preset fact reviewer projects the R17 comparison into 10 review rows, 3 attention rows, 1 blocked row, and 1 waiver row without scene or engine writes. |
| `validate-r18-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r18-unreal-preset-fact-review-presentation-pack")` | DCC Presenter Pack probes 15 key evidence files including the preset fact review artifact, reports 15 present / 0 missing required files, and exports 9 demo route steps. |
| `validate-r17-unreal-preset-fact-comparison` | `python dcc-hosts/unreal-handoff-inspector/scripts/run_preset_fact_compare.py` | Unreal preset fact comparison reads the R16 L3++ artifact, compares engine facts against PC / Mobile preset policy and waiver rows, and exports 10 fact rows: 7 matched, 1 drift, 1 waived, 1 blocked. |
| `validate-r17-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r17-unreal-preset-facts-presentation-pack")` | DCC Presenter Pack probes 14 key evidence files including Unreal preset fact comparison, reports 14 present / 0 missing required files, and keeps the overall gate at CapturePending until real Maya GUI media exists. |
| `validate-r16-unreal-engine-facts` | `python dcc-hosts/unreal-handoff-inspector/scripts/run_unreal_l3_smoke.py` | UnrealEditor-Cmd runs Unreal Python against the public test `.uproject`, exports `unreal-handoff-inspector-contract@0.4.0`, and matches 4 / 4 StaticMesh engine facts: source import data, material slot, LOD count and collision settings. |
| `validate-r16-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r16-unreal-engine-facts-presentation-pack")` | DCC Presenter Pack probes 13 key evidence files including Unreal L3++ and Blender evidence, reports 13 present / 0 missing required files, and keeps the overall gate at CapturePending until real Maya GUI media exists. |
| `validate-r15-unreal-registry-fixture` | `python dcc-hosts/unreal-handoff-inspector/scripts/run_unreal_l3_smoke.py` | UnrealEditor-Cmd runs Unreal Python against the public test `.uproject`, exports `unreal-handoff-inspector-contract@0.3.0`, imports public StaticMesh / creates Material fixture assets, queries Asset Registry, and matches 2 / 2 expected path/class rows. |
| `validate-r15-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r15-unreal-registry-fixture-presentation-pack")` | DCC Presenter Pack probes 13 key evidence files including Unreal L3+ and Blender evidence, reports 13 present / 0 missing required files, and keeps the overall gate at CapturePending until real Maya GUI media exists. |
| `validate-r14-unreal-l3-inspector` | `python dcc-hosts/unreal-handoff-inspector/scripts/run_unreal_l3_smoke.py` | UnrealEditor-Cmd runs Unreal Python against the public test `.uproject`, exports `unreal-handoff-inspector-contract@0.2.0`, records Unreal 5.3.2 / Python 3.9.7 runtime, queries Asset Registry, and keeps engine writes at 0. |
| `validate-r14-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r14-unreal-l3-presentation-pack")` | DCC Presenter Pack probes 13 key evidence files including Unreal L3 and Blender evidence, reports 13 present / 0 missing required files, and keeps the overall gate at CapturePending until real Maya GUI media exists. |
| `validate-r13-unreal-handoff-inspector` | `python dcc-hosts/unreal-handoff-inspector/scripts/run_smoke.py` | Unreal Handoff Inspector exports L2 engine-side contract evidence: 2 import intents, 1 import-ready command, 1 blocked import, Unreal CLI available, test project missing, 14 pass checks, 2 review checks, 4 blocked checks. |
| `validate-r13-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r13-engine-presentation-pack")` | DCC Presenter Pack exports 8 demo route steps, probes 13 key evidence files including Blender and Unreal evidence, reports 13 present / 0 missing required files, and keeps the overall gate at CapturePending until real Maya GUI media exists. |
| `validate-r12-blender-rule-adapter` | `python dcc-hosts/blender-rule-adapter/scripts/run_smoke.py` | Blender Rule Adapter exports L2 contract evidence from a public fixture: 2 assets, 1 Ready, 1 Blocked, 8 pass checks, 3 warnings, 1 error, and L3 status `blocked_by_missing_blender_cli`. |
| `validate-r12-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r12-cross-dcc-presentation-pack")` | Historical R12 Presenter Pack exported 7 demo route steps, probed 12 key evidence files including Blender adapter evidence, and reported 12 present / 0 missing required files. |
| `validate-r11-dcc-presenter-pack` | `Maya 2024 mayapy dcc_presentation_export_pack(label="r11-dcc-presentation-pack")` | Historical R11 Presenter Pack exported 6 demo route steps, probed 11 key evidence files, and reported 11 present / 0 missing required files. |
| `validate-r10-7-dcc-smoke` | `Maya 2024 mayapy showcase_runbook_export_package(label="r10-7-dcc-first-case-page-runbook")` | DCC-first package exports 5 modules, 5 module artifacts, 1 handoff artifact, 1 decision artifact, 0 blocked modules, 7 business route steps, 7 live demo script steps, 7 GUI checklist items, and 6 reviewer claims. |
| `validate-r10-7-gui-evidence` | `Maya 2024 mayapy showcase_runbook_export_gui_evidence_manifest(label="r10-7-dcc-first-case-page-gui-evidence")` | GUI evidence manifest exports 9 screenshot targets, 1 recording target, 7 business route steps, and 10 required media files. |
| `validate-r10-7-asset-handoff` | `Maya 2024 mayapy asset_handoff_export_packet(label="r10-7-dcc-first-case-page-runbook-asset-handoff")` | Asset Handoff Gate exports 2 synthetic assets, 1 Ready asset, 1 Review asset, 0 Blocked assets, 3 preview actions, and protocol/rule/texture/visual/queue evidence. |

Latest case page artifact:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-20260803-171316.json
```

Latest runbook artifact:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-20260803-171316.json
```

Latest GUI evidence manifest:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-gui-evidence-20260803-171316.json
```

Latest GUI media audit:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-gui-media-audit-20260803-171316.json
```

Latest Asset Handoff Gate packet:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-20260803-171316.json
```

Latest Asset Handoff Decision packet:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-7-dcc-first-case-page-runbook-asset-handoff-decision-20260803-171316.json
```

Latest Engine Handoff Preflight packet:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-8-engine-handoff-preflight-fixture-20260803-172302.json
```

Latest Engine Preset Comparison packet:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-9-engine-preset-comparison-20260803-172927.json
```

Latest Blender Rule Adapter contract:

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260804-201125.json
```

Latest Blender L3 runtime:

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json
```

Latest 3ds Max Rule Adapter contract:

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
```

Latest 3ds Max L3 runtime:

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260806-032411.json
```

Latest 3ds Max Material Texture Manifest Link:

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-texture-manifest-link-20260806-032426.json
```

Latest Unreal Handoff Inspector contract:

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

Latest Unreal Preset Fact Comparison:

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

Latest Unreal Preset Fact Review:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json
```

Latest Scene Transaction Guard:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-20260804-195730.json
```

Latest Unreal Animation Bridge readiness:

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-readiness-20260805-164730.json
```

Latest Animation Continuity L3:

```text
<repo>\dcc-hosts\animation-continuity-lab\artifacts\animation-continuity-maya-l3-20260805-162744.json
```

Latest DCC Presenter Pack:

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r53-max-texture-manifest-link-presentation-pack-20260806-032705.json
```

## Commands

| Command id | Command | Proves |
| --- | --- | --- |
| `validate-build` | `npm run build` | TypeScript and Vite production bundle compile with the current data model. |
| `validate-css-constraints` | `rg "#[0-9a-fA-F]{3,8}|[0-9]+px [0-9]+px [1-9][0-9]px|border-(left|right): [2-9]" src/styles.css` | No banned hex colors, large soft shadows, or wide side-stripe borders were introduced. |
| `validate-playwright-r6-3` | `python - <<PLAYWRIGHT_R6_3` | Task Orchestrator evidence view renders manifest and avoids horizontal overflow. |
| `validate-exported-report` | `assert reportVersion, modules, caseCardContracts, reviewerAcceptance, evidenceManifest, evidenceIndex counts` | Exported JSON is machine-checkable. |
| `validate-playwright-r7-1` | `python - <<PLAYWRIGHT_R7_1` | Pending receipt review panel renders and exports the R7.1 report. |
| `validate-playwright-r7-2` | `python - <<PLAYWRIGHT_R7_2` | Rule Matrix renders fix preview and manual disposition evidence. |
| `validate-playwright-r7-3` | `python - <<PLAYWRIGHT_R7_3` | Texture Delivery renders approved package delta and committed manifest. |
| `validate-playwright-r7-4` | `python - <<PLAYWRIGHT_R7_4` | Owner signoff ledger closes R2/R4 receipts and exports R7.4 report. |
| `validate-playwright-r7-5` | `python - <<PLAYWRIGHT_R7_5` | Public package panel renders, exports `portfolio-case-study-report@0.8.0`, and package files exist. |
| `validate-playwright-r8-0` | `node - <<PLAYWRIGHT_R8_0` | Dependency impact panel renders 5 assets, 3 paths, 4 decisions, and 3 receipts. |
| `validate-playwright-r8-1` | `node - <<PLAYWRIGHT_R8_1` | Public dependency dataset, path steps, decision matrix, and `task-orchestrator-report@0.6.0` export are verified. |
| `validate-playwright-r8-2` | `node - <<PLAYWRIGHT_R8_2` | Public package 0.2 renders, R8 impact receipt is closed, and `portfolio-case-study-report@0.9.0` exports. |
| `validate-playwright-r8-3` | `node - <<PLAYWRIGHT_R8_3` | Scenario switch and receipt drilldown render, vehicle dataset counts match, and `task-orchestrator-report@0.7.0` exports. |
| `validate-playwright-r8-4` | `node - <<PLAYWRIGHT_R8_4` | Scenario comparison, fixture authoring draft, receipt closure simulation, and `task-orchestrator-report@0.8.0` export are verified. |
| `validate-playwright-r8-5` | `node - <<PLAYWRIGHT_R8_5` | Batch fixture variants, adapter replay dry-run, regression score trend, and `task-orchestrator-report@0.9.0` export are verified. |
| `validate-playwright-r8-6` | `node - <<PLAYWRIGHT_R8_6` | Adapter contract replay, external receipt sync mock, replay failure recovery, and `task-orchestrator-report@1.0.0` export are verified. |
| `validate-playwright-r8-7` | `node - <<PLAYWRIGHT_R8_7` | Production handoff diff, adapter owner approval packet, held payload retry ledger, and `task-orchestrator-report@1.1.0` export are verified. |
| `validate-playwright-r8-8` | `node - <<PLAYWRIGHT_R8_8` | Signed receipt sandbox, production adapter smoke harness, rollback receipt verification, and `task-orchestrator-report@1.2.0` export are verified. |
| `validate-playwright-r8-9` | `node - <<PLAYWRIGHT_R8_9` | Credential boundary drill, receipt retention audit, cross-module release drill, and `task-orchestrator-report@1.3.0` export are verified. |
| `validate-playwright-r8-10` | `node - <<PLAYWRIGHT_R8_10` | Adapter failure injection matrix, receipt lineage graph, reviewer packet diff, and `task-orchestrator-report@1.4.0` export are verified. |
| `validate-playwright-r8-11` | `node - <<PLAYWRIGHT_R8_11` | Live adapter readiness simulator, owner approval closeout, mutation replay rehearsal, and `task-orchestrator-report@1.5.0` export are verified. |
| `validate-playwright-r8-12` | `node - <<PLAYWRIGHT_R8_12` | Production adapter cutover checklist, post-cutover receipt monitor, emergency stop drill, and `task-orchestrator-report@1.6.0` export are verified. |
| `validate-playwright-r8-13` | `node - <<PLAYWRIGHT_R8_13` | Private owner receipt bridge, cutover signoff diff, production route shadow replay, and `task-orchestrator-report@1.7.0` export are verified. |
| `validate-playwright-r8-14` | `node - <<PLAYWRIGHT_R8_14` | Production drift audit, owner SLA monitor, release freeze replay, and `task-orchestrator-report@1.8.0` export are verified. |
| `validate-playwright-r8-15` | `node - <<PLAYWRIGHT_R8_15` | Adapter rollback adjudicator, receipt dispute replay, audit export diff, and `task-orchestrator-report@1.9.0` export are verified. |
| `validate-playwright-r8-16` | `node - <<PLAYWRIGHT_R8_16` | Rollout wave planner, incident replay notebook, owner exception ledger, and `task-orchestrator-report@1.10.0` export are verified. |
| `validate-playwright-r8-17` | `node - <<PLAYWRIGHT_R8_17` | Rollback budget simulator, release confidence heatmap, evidence aging policy, and `task-orchestrator-report@1.11.0` export are verified. |
| `validate-playwright-r8-18` | `node - <<PLAYWRIGHT_R8_18` | Release rollback rehearsal, owner quorum simulator, stale evidence auto-refresh queue, and `task-orchestrator-report@1.12.0` export are verified. |
| `validate-playwright-r8-19` | `node - <<PLAYWRIGHT_R8_19` | Release decision board, owner SLA escalation queue, evidence retention purge rehearsal, and `task-orchestrator-report@1.13.0` export are verified. |
| `validate-playwright-r8-20` | `node - <<PLAYWRIGHT_R8_20` | Release evidence compactor, reviewer packet lockfile, production readiness exception closeout, and `task-orchestrator-report@1.14.0` export are verified. |
| `validate-playwright-r8-21` | `node - <<PLAYWRIGHT_R8_21` | Locked packet diff viewer, exception burn-down dashboard, reviewer acceptance replay, and `task-orchestrator-report@1.15.0` export are verified. |
| `validate-playwright-r8-22` | `node - <<PLAYWRIGHT_R8_22` | Accepted packet freeze, exception owner response importer, release readiness replay diff, and `task-orchestrator-report@1.16.0` export are verified. |
| `validate-playwright-r8-23` | `node - <<PLAYWRIGHT_R8_23` | Frozen packet promotion gate, owner response SLA reconciliation, readiness acceptance ledger, and `task-orchestrator-report@1.17.0` export are verified. |
| `validate-playwright-r8-24` | `node - <<PLAYWRIGHT_R8_24` | Promotion rollback preview, SLA exception waiver ledger, candidate packet release note generator, and `task-orchestrator-report@1.18.0` export are verified. |
| `validate-playwright-r8-25` | `node - <<PLAYWRIGHT_R8_25` | Release-note reviewer approval loop, waiver expiry monitor, rollback rehearsal bundle diff, and `task-orchestrator-report@1.19.0` export are verified. |
| `validate-playwright-r8-26` | `node - <<PLAYWRIGHT_R8_26` | Approval evidence seal, waiver renewal simulator, rollback drill incident handoff, and `task-orchestrator-report@1.20.0` export are verified. |
| `validate-playwright-r8-27` | `node - <<PLAYWRIGHT_R8_27` | Sealed approval replay, waiver expiry burn-down, incident closure acceptance packet, and `task-orchestrator-report@1.21.0` export are verified. |
| `validate-playwright-r8-28` | `node - <<PLAYWRIGHT_R8_28` | Closure acceptance replay, waiver owner response importer, incident SLA scoreboard, and `task-orchestrator-report@1.22.0` export are verified. |
| `validate-playwright-r8-29` | `node - <<PLAYWRIGHT_R8_29` | Incident closure diff viewer, waiver SLA reconciliation, release operations acceptance ledger, and `task-orchestrator-report@1.23.0` export are verified. |
| `validate-playwright-r8-30` | `node - <<PLAYWRIGHT_R8_30` | Operations packet signoff diff, release train readiness board, owner escalation closeout, and `task-orchestrator-report@1.24.0` export are verified. |
| `validate-playwright-r8-31` | `node - <<PLAYWRIGHT_R8_31` | Release train replay receipt, owner closeout aging audit, publish rehearsal variance report, and `task-orchestrator-report@1.25.0` export are verified. |
| `validate-playwright-r8-32` | `node - <<PLAYWRIGHT_R8_32` | Release manager daily digest, late owner risk forecast, package acceptance freeze diff, and `task-orchestrator-report@1.26.0` export are verified. |
| `validate-playwright-r8-33` | `node - <<PLAYWRIGHT_R8_33` | Release acceptance waiver summary, freeze exception closure board, publish go/no-go packet, and `task-orchestrator-report@1.27.0` export are verified. |
| `validate-playwright-r8-34` | `node - <<PLAYWRIGHT_R8_34` | Publish decision receipt replay, post-release watch window board, rollback readiness delta, and `task-orchestrator-report@1.28.0` export are verified. |
| `validate-playwright-r8-35` | `node - <<PLAYWRIGHT_R8_35` | Release closeout receipt seal, watch escalation replay, rollback drill closeout packet, and `task-orchestrator-report@1.29.0` export are verified. |
| `validate-playwright-r8-36` | `node - <<PLAYWRIGHT_R8_36` | Closeout acceptance replay, escalation aging board, final release archive packet, and `task-orchestrator-report@1.30.0` export are verified. |
| `validate-playwright-r8-37` | `node - <<PLAYWRIGHT_R8_37` | Archive integrity audit, release memory search, archived packet restore rehearsal, and `task-orchestrator-report@1.31.0` export are verified. |
| `validate-playwright-r8-38` | `node - <<PLAYWRIGHT_R8_38` | Archive retention policy simulator, release memory diff timeline, restore approval packet, and `task-orchestrator-report@1.32.0` export are verified. |
| `validate-playwright-r8-39` | `playwright-cli run-code .playwright-cli/r8-39-verify.js` | Archive access review ledger, restore incident drillbook, release memory ownership transfer, and `task-orchestrator-report@1.33.0` export are verified. |
| `validate-playwright-r8-40` | `playwright-cli run-code .playwright-cli/r8-40-verify.js` | Restore readiness replay audit, archive permission expiry monitor, release memory audit export bundle, and `task-orchestrator-report@1.34.0` export are verified. |
| `validate-playwright-r8-41` | `playwright-cli run-code --filename=.playwright-cli/r8-41-verify.js` | Audit bundle reviewer signoff queue, permission renewal replay simulator, restore memory evidence notarization, and `task-orchestrator-report@1.35.0` export are verified. |
| `validate-playwright-r8-42` | `playwright-cli run-code --filename=.playwright-cli/r8-42-verify.js` | Release memory query replay, restore approval comparison, audit packet retention renewal dashboard, and `task-orchestrator-report@1.36.0` export are verified. |
| `validate-playwright-r8-43` | `playwright-cli run-code --filename=.playwright-cli/r8-43-verify.js` | Audit query exception ledger, retention owner response importer, restore memory packet handoff, and `task-orchestrator-report@1.37.0` export are verified. |
| `validate-playwright-r8-44` | `playwright-cli run-code --filename=.playwright-cli/r8-44-verify.js` | Restore packet acceptance replay, handoff owner SLA board, archive restoration drill exporter, and `task-orchestrator-report@1.38.0` export are verified. |
| `validate-playwright-r8-45` | `playwright-cli run-code --filename=.playwright-cli/r8-45-verify.js` | Restoration drill acceptance ledger, archive drill owner response importer, restore operations readiness digest, and `task-orchestrator-report@1.39.0` export are verified. |
| `validate-playwright-r8-46` | `playwright-cli run-code --filename=.playwright-cli/r8-46-verify.js` | Restore readiness exception closeout, archive ops SLA escalation queue, restore command rehearsal lock, and `task-orchestrator-report@1.40.0` export are verified. |
| `validate-playwright-r8-47` | `playwright-cli run-code --filename=.playwright-cli/r8-47-verify.js` | Restore lock reviewer signoff queue, archive command rollback rehearse diff, restore execution redline packet, and `task-orchestrator-report@1.41.0` export are verified. |
| `validate-playwright-r8-48` | `playwright-cli run-code --filename=.playwright-cli/r8-48-verify.js` | Restore redline owner override simulator, archive execution blackbox recorder, restore abort drill closeout ledger, and `task-orchestrator-report@1.42.0` export are verified. |
| `validate-playwright-r8-49` | `playwright-cli run-code --filename=.playwright-cli/r8-49-verify.js` | Restore incident replay notarization, archive restore execution variance report, post-abort owner evidence reconciliation, and `task-orchestrator-report@1.43.0` export are verified. |
| `validate-playwright-r8-50` | `playwright-cli run-code --filename=.playwright-cli/r8-50-verify.js` | Restore acceptance final attestation, archive incident delta aging board, post-restore owner signoff packet, and `task-orchestrator-report@1.44.0` export are verified. |
| `validate-playwright-r8-51` | `playwright-cli run-code --filename=.playwright-cli/r8-51-verify.js` | Signoff dispute replay, archive acceptance freeze diff, owner closure exception ledger, and `task-orchestrator-report@1.45.0` export are verified. |
| `validate-playwright-r8-52` | `playwright-cli run-code --filename=.playwright-cli/r8-52-verify.js` | Closure evidence seal, archive terminal package diff, owner reopen guardrail simulator, and `task-orchestrator-report@1.46.0` export are verified. |
| `validate-playwright-r8-53` | `playwright-cli run-code --filename=.playwright-cli/r8-53-verify.js` | Sealed closure receipt replay, terminal archive retention renewal, owner reopen incident drillbook, and `task-orchestrator-report@1.47.0` export are verified. |
| `validate-playwright-r8-54` | `playwright-cli run-code --filename=.playwright-cli/r8-54-verify.js` | Receipt replay aging lock, retention exception burn-down, drillbook acceptance ledger, and `task-orchestrator-report@1.48.0` export are verified. |

## Current Gate

| Field | Value |
| --- | --- |
| Release gate | `Ready` |
| Blocking receipts | `[]` |
| Package files | 28 |
| Validation commands | 50 |
