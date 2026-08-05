# Module Briefs

## 1. Asset Protocol Workbench

Business scenario: asset intake and downstream handoff fail when fields, aliases, and severity rules live in tribal memory.

Core secret: treat the handoff as a protocol. The tool makes canonical fields, DCC aliases, severity, reviewer notes, and export payloads visible in one place.

Deterministic core: schema groups, alias mapping, DCC profile selection, required field status, fixture replay, and JSON export.

AI boundary: AI can explain missing fields and suggest protocol wording. It cannot silently rename canonical fields or weaken release criteria.

Key evidence: `../docs/modules/asset-protocol-workbench.md`

## 2. Cross-DCC Rule Matrix

Business scenario: a QA rule is rarely identical across Maya, Blender, Houdini, and Max. Real pipelines need different detection paths, fixability boundaries, and owner decisions.

Core secret: split rule detection from fix preview and manual-only disposition. The impressive part is not auto-fix itself, but making "can fix", "should not fix", and "needs owner" auditable.

Deterministic core: fixture matrix, normalized rule outputs, fix preview payload, risk tags, manual disposition receipt, and owner signoff.

AI boundary: AI can draft rule copy and explain risk. It cannot decide that a destructive scene mutation is safe.

Key evidence: `../docs/modules/cross-dcc-rule-matrix.md`

## 3. Visual Review Studio

Business scenario: visual review loses value when comments are free text with no pass contract or production lane.

Core secret: make subjective review operational. The module binds visual slots, rubric lanes, annotation status, queue state, and pass criteria into exportable evidence.

Deterministic core: review lane data, annotation records, pass contract JSON, queue filtering, and evidence export.

AI boundary: AI can summarize visual feedback and propose review wording. It cannot pass a shot without explicit rubric evidence.

Key evidence: `../docs/modules/visual-review-studio.md`

## 4. Texture Delivery Console

Business scenario: texture publish tools often hide the highest-risk decision: when a package moves from dry-run analysis to approved mutation.

Core secret: separate publish intent, public synthetic fixture, approved package delta, and committed file manifest. The TA value is the mutation boundary, not a prettier upload form.

Deterministic core: dry-run evaluation, channel validation, package delta diff, approved mutation receipt, committed file manifest, and export report.

AI boundary: AI can describe risk and help prepare review text. It cannot mutate delivery packages without an accepted receipt.

Key evidence: `../docs/modules/texture-delivery-console.md`

## 5. Task Orchestrator

Business scenario: a portfolio of tools becomes credible only when every module shares evidence, receipts, signoffs, dependency impact decisions, and repeatable validation.

Core secret: orchestrate proof, not UI screens. This module turns scattered demos into a release-gated case package with manifest counts, owner receipts, dependency impact paths, validation commands, and exportable reports.

Deterministic core: evidence index, reviewer acceptance, pending receipt review, owner signoff ledger, public dependency datasets, scenario switch, receipt drilldown, scenario comparison, fixture authoring draft, receipt closure simulation, batch fixture variants, adapter replay dry-run, regression score trend, adapter contract replay, external receipt sync mock, replay failure recovery, production handoff diff, adapter owner approval packet, held payload retry ledger, signed receipt sandbox, production adapter smoke harness, rollback receipt verification, credential boundary drill, receipt retention audit, cross-module release drill, adapter failure injection matrix, receipt lineage graph, reviewer packet diff, live adapter readiness simulator, owner approval closeout, mutation replay rehearsal, production adapter cutover checklist, post-cutover receipt monitor, emergency stop drill, private owner receipt bridge, cutover signoff diff, production route shadow replay, production drift audit, owner SLA monitor, release freeze replay, adapter rollback adjudicator, receipt dispute replay, audit export diff, rollout wave planner, incident replay notebook, owner exception ledger, rollback budget simulator, release confidence heatmap, evidence aging policy, release rollback rehearsal, owner quorum simulator, stale evidence auto-refresh queue, release decision board, owner SLA escalation queue, evidence retention purge rehearsal, release evidence compactor, reviewer packet lockfile, production readiness exception closeout, locked packet diff viewer, exception burn-down dashboard, reviewer acceptance replay, accepted packet freeze, exception owner response importer, release readiness replay diff, frozen packet promotion gate, owner response SLA reconciliation, readiness acceptance ledger, promotion rollback preview, SLA exception waiver ledger, candidate packet release note generator, release-note reviewer approval loop, waiver expiry monitor, rollback rehearsal bundle diff, approval evidence seal, waiver renewal simulator, rollback drill incident handoff, sealed approval replay, waiver expiry burn-down, incident closure acceptance packet, closure acceptance replay, waiver owner response importer, incident SLA scoreboard, incident closure diff viewer, waiver SLA reconciliation, release operations acceptance ledger, operations packet signoff diff, release train readiness board, owner escalation closeout, release train replay receipt, owner closeout aging audit, publish rehearsal variance report, release manager daily digest, late owner risk forecast, package acceptance freeze diff, release acceptance waiver summary, freeze exception closure board, publish go/no-go packet, publish decision receipt replay, post-release watch window board, rollback readiness delta, release closeout receipt seal, watch escalation replay, rollback drill closeout packet, closeout acceptance replay, escalation aging board, final release archive packet, archive integrity audit, release memory search, archived packet restore rehearsal, archive retention policy simulator, release memory diff timeline, restore approval packet, archive access review ledger, restore incident drillbook, release memory ownership transfer, restore readiness replay audit, archive permission expiry monitor, release memory audit export bundle, audit bundle reviewer signoff queue, permission renewal replay simulator, restore memory evidence notarization, release memory query replay, restore approval comparison, audit packet retention renewal dashboard, audit query exception ledger, retention owner response importer, restore memory packet handoff, restore packet acceptance replay, handoff owner SLA board, archive restoration drill exporter, restoration drill acceptance ledger, archive drill owner response importer, restore operations readiness digest, restore readiness exception closeout, archive ops SLA escalation queue, restore command rehearsal lock, restore lock reviewer signoff queue, archive command rollback rehearse diff, restore execution redline packet, restore redline owner override simulator, archive execution blackbox recorder, restore abort drill closeout ledger, restore incident replay notarization, archive restore execution variance report, post-abort owner evidence reconciliation, restore acceptance final attestation, archive incident delta aging board, post-restore owner signoff packet, signoff dispute replay, archive acceptance freeze diff, owner closure exception ledger, closure evidence seal, archive terminal package diff, owner reopen guardrail simulator, sealed closure receipt replay, terminal archive retention renewal, owner reopen incident drillbook, receipt replay aging lock, retention exception burn-down, drillbook acceptance ledger, publish decision matrix, evidence manifest, public case package manifest, and JSON export.

AI boundary: AI can generate summaries and reviewer-facing narratives. It cannot mark required evidence present or release a package without deterministic checks.

Key evidence: `../docs/modules/task-orchestrator.md`

## 6. Animation Continuity Lab

Business scenario: animation handoff breaks when Maya, MotionBuilder and Unreal disagree on rig identity, take range, sample rate, root motion, additive layers or channel ownership.

Core secret: treat an animation clip as deterministic facts, not just an FBX file. The module records rig id, skeleton fingerprint, declared take, real keyed animCurves, sub-frame keys, duplicate channel identities, root motion policy and owner-only fixes.

Deterministic core: public synthetic Maya fixture, `mayapy` keyed curve collector, normalized animation-continuity input, rule evaluation, fix preview, and Presenter Pack evidence probe.

AI boundary: AI can explain why a failed take is risky or draft handoff notes. It cannot resample, retarget, delete additive layers or approve owner waivers without deterministic evidence.

Key evidence: `../docs/modules/animation-continuity-lab.md`

## 7. Unreal Animation Bridge

Business scenario: animation clips can pass Maya checks but still drift after Unreal import through skeleton binding, sample-rate, curve, root-motion or compression differences.

Core secret: bridge DCC facts to engine facts. The module reads Maya Animation Continuity L3 evidence, maps each take to expected Unreal AnimSequence / Skeleton facts, and records whether Unreal Python can see the required APIs and assets.

Deterministic core: bridge fixture, Maya L3 source artifact, Unreal Python API probe, expected asset existence probe, evaluation rows, fix preview, and Presenter Pack evidence probe.

AI boundary: AI can explain why a clip is blocked or draft owner handoff notes. It cannot claim an AnimSequence is imported until Unreal runtime facts prove the asset and skeleton exist.

Key evidence: `../docs/modules/unreal-animation-bridge.md`

## 8. Unreal AnimSequence Deep Facts

Business scenario: a clip can import successfully while frame span, runtime curve visibility, root-motion settings or compression settings remain ambiguous.

Core secret: separate asset import success from runtime metadata confidence. R41 reads existing public AnimSequence assets, derives frame spans from play length, and records which curve/root/compression facts Unreal Python can or cannot expose.

Deterministic core: R25 import L3 source artifact, Unreal 5.3.2 read-only collector, duration/frame-span comparison, metadata visibility rows, owner actions, and assetWrites=0 boundary.

AI boundary: AI can explain why a clip is Review or Blocked. It cannot claim curve, root-motion or compression parity when Unreal metadata is not readable.

Key evidence: `../docs/modules/unreal-animation-bridge.md`

## 9. Character Calibration & Intent Transfer Studio

Business scenario: character delivery can pass file checks while topology, joint coverage, face parameters or Control Rig mapping silently break downstream deformation.

Core secret: treat character transfer as facts that survive the DCC-to-engine boundary. The module records topology signature, required joints, TMP leakage, skin influence budget, calibration delta, face parameter coverage and Control Rig mapping.

Deterministic core: public Maya fixture, `mayapy` collector, source rule rows, Maya/AuroraView drilldown panels, owner actions, fix preview, Unreal Control Rig Bridge evidence, fixture authoring receipt, and deformation-link postcheck.

AI boundary: AI can explain why a character is blocked or draft owner notes. It cannot approve topology drift, fake missing joints, or claim Control Rig coverage without runtime facts.

Key evidence: `../docs/modules/character-calibration-studio.md`

## 10. Unreal Control Rig Bridge / Fixture / Face Skeleton / Deformation / Compile Status

Business scenario: approved Maya control mapping still needs Unreal Control Rig API, SkeletalMesh/Skeleton binding, target CR asset coverage, face deformation targets, runtime controls, compile invocation, and diagnostic visibility before it is useful in engine.

Core secret: separate source mapping readiness, engine binding readiness, controlled fixture authoring, runtime hierarchy coverage, Skeleton target coverage, compile invocation and direct diagnostic status. R43 proved that `CR_HeroFace` having five runtime controls is still not enough when the public Skeleton only confirms two deformation target matches. R44 adds a Maya-generated public face Skeleton imported into Unreal and resolves the Eye/Jaw target gap. R45 invokes the public Control Rig compile methods and records the remaining diagnostic-readback boundary without pretending a method call is the same as compile approval.

Deterministic core: Character Calibration Drilldown source artifact, Unreal 5.3.2 Python probe, ControlRig/RigVM API facts, AssetTools authoring harness, hierarchy controller control creation, Maya face Skeleton FBX generation, Unreal skeletal import receipt, read-only deformation-link collector, Skeleton reference-pose facts, shape/offset readability rows, transient compile invocation rows, direct status / diagnostic probe rows, package dirty-state boundary, post-face bridge recheck, evaluation rows, owner actions and public-fixture write boundary.

AI boundary: AI can summarize missing controls, missing deformation targets and owner responsibilities. It cannot approve Control Rig coverage or compile readiness without deterministic engine evidence, hierarchy facts and explicit write boundary.

Key evidence: `../docs/modules/unreal-control-rig-bridge.md`

## 11. Groom Export Inspector

Business scenario: XGen/groom hair can pass ordinary mesh checks while root UVs, strand IDs, guide curves, Alembic payload flags or Unreal importer mode are wrong, making Groom / Binding import unreliable.

Core secret: treat groom export as a non-mesh publish contract. R46 records root UV coverage, stable strand IDs, guide curve coverage, `.abc` payload flags, target Groom / Binding / SkeletalMesh intent and owner actions from Maya runtime facts. R47 checks whether those rows can enter Unreal import readiness through API visibility, target SkeletalMesh presence and zero-write engine boundaries. R48 uses Maya `AbcExport` to write the approved public groom row into a real Alembic cache receipt while holding the TMP row. R49 joins that `.abc` receipt to Unreal runtime post-check readiness: cache sha256 continuity, AssetImportTask dry-run, Alembic factory visibility, target SkeletalMesh presence, missing Groom API and expected Groom / Binding asset gaps. R50 fixes the fixture layer by enabling HairStrands/Alembic hair plugins in the public Unreal project and proving Groom import API readiness under a zero-write commandlet probe. R51 enters a controlled executor: the approved cache imports successfully, but Unreal creates a `StaticMesh` rather than `GroomAsset`; the tool records that boundary, holds BindingAsset creation, and rolls back public fixture writes.

Deterministic core: public Maya scalp/curve fixture, `mayapy` collector, per-strand custom payload, root UV / strand ID / guide evaluation, Alembic contract rows, Maya `AbcExport` cache receipt with bytes/hash, Unreal binding target rows, Unreal 5.3.2 API/asset probe, controlled `AssetImportTask`, class post-check, binding method probe, rollback receipt, owner actions and write boundary.

AI boundary: AI can explain why a groom export is blocked or draft owner notes. It cannot claim a groom cache or import is engine-ready without deterministic root UV, ID, guide, cache receipt, import class, binding and rollback evidence.

Key evidence: `../docs/modules/groom-export-inspector.md`

## 12. Spatial Authoring & Pose Transfer Workbench

Business scenario: sockets, hotspots, pose frames and mirror transfer rules often live as scene conventions and break when assets move from DCC to gameplay.

Core secret: make spatial authoring data explicit: parent joint, local offset, mirror pair, hotspot semantic, owner, pose frame range, local-space consistency and preview locator state.

Deterministic core: public Maya joint/locator fixture, `mayapy` collector, spatial validation rows, drilldown panels, owner actions, fix preview, and Unreal socket import checker evidence.

AI boundary: AI can explain socket risk and propose handoff text. It cannot approve a gameplay socket or pose transfer without source and engine facts.

Key evidence: `../docs/modules/spatial-authoring-workbench.md`

## 13. Unreal Socket Import Checker

Business scenario: a socket can be clean in Maya but still absent or bound to the wrong target in Unreal. Gameplay, VFX, camera and attach logic need engine-side facts, not just DCC locators.

Core secret: compare source spatial intent against actual SkeletalMesh/Skeleton socket readiness. The tool keeps approved rows blocked until expected engine sockets and parent bindings exist.

Deterministic core: Spatial Authoring Drilldown source artifact, Unreal 5.3.2 Python probe, SkeletalMesh/Skeleton/socket API checks, expected socket comparison, owner actions and read-only write boundary.

AI boundary: AI can summarize missing sockets and owner handoff text. It cannot claim socket import success or create gameplay attach points without deterministic Unreal evidence and approval.

Key evidence: `../docs/modules/unreal-socket-import-checker.md`

## 14. Unreal Socket Authoring Executor

Business scenario: an auto-fix button for missing engine sockets is dangerous unless the runtime API can create a named socket, bind it to a bone, post-check it and roll it back.

Core secret: separate the execution gate from the fix promise. R40 selects only the approved rifle row, holds the blocked TMP row, enters Unreal 5.3.2, and records the API limitation that prevents safe socket authoring in commandlet Python.

Deterministic core: R38 source artifact, Unreal commandlet executor, `SkeletalMesh.add_socket` docstring probe, property write attempts for `socket_name` / `bone_name`, no-write boundary and Presenter Pack evidence.

AI boundary: AI can recommend owner actions and explain why the auto-fix is blocked. It cannot claim socket creation when UE exposes add_socket but keeps identity fields read-only.

Key evidence: `../docs/modules/unreal-socket-import-checker.md`

## 15. Platform Variant Forge

Business scenario: PC-to-Mobile asset variants fail when LOD, Nanite, material slots, texture budgets, collision and owner approval are treated as separate chores.

Core secret: model variant work as a gate plus operation contracts. The module joins planned variants to Unreal runtime facts, converts drift into generation operations, executes only public-safe texture work, records rollback receipts for heavier LOD/Nanite/collision steps, and post-checks those receipts against read-only Unreal StaticMesh runtime facts.

Deterministic core: variant fixture, Unreal runtime probes, generation plan, texture runtime collector, public Texture2D payload, controlled executor, executor expansion receipts, StaticMesh post-check and Presenter Pack probes.

AI boundary: AI can explain platform drift and draft operation notes. It cannot mutate production assets or bypass owner approval for high-risk variant generation.

Key evidence: `../docs/modules/platform-variant-forge.md`
