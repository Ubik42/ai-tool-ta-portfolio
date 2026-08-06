# Lightbox核心技术点覆盖与插件开发状态

更新时间：2026-08-06
工程根目录：`<repo>`  
当前发布包：`ai-tool-ta-dcc-first-showcase-r75` / `dcc-first-package@1.72.0`

## 1. 当前结论

当前作品集已经不是纯前端展示。主入口是 Maya 2024 内的 AuroraView 面板，React/TypeScript 只是嵌入式工具界面；证据层由 Maya `mayapy`、Blender `bpy`、3ds Max `pymxs`、Houdini contract / hython readiness、Unreal Python 和普通 Python fixture 共同生成。

R75 的硬证据：

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r75-unreal-control-rig-native-bridge-build-presentation-pack-20260806-101502.json`
- Unreal Control Rig Native Bridge Build：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-native-bridge-build-20260806-100928.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r74-unreal-control-rig-native-bridge-readiness-presentation-pack-20260806-095213.json`
- Unreal Control Rig Native Bridge Readiness：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-native-bridge-readiness-20260806-094558.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r73-unreal-gameplay-attach-timing-controlled-readiness-presentation-pack-20260806-093254.json`
- Unreal Gameplay Attach Timing Controlled Readiness：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-gameplay-attach-timing-controlled-readiness-20260806-092934.json`
- Unreal Animation Notify Native Controlled Write：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-controlled-write-20260806-090946.json`
- Unreal Animation Notify Native Bridge Build：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-bridge-build-20260806-090905.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r71-unreal-animation-notify-native-diagnostics-presentation-pack-20260806-085351.json`
- Unreal Animation Notify Native Diagnostics：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-diagnostics-20260806-085035.json`
- Unreal Animation Notify Native Commandlet Probe：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-commandlet-probe-20260806-083144.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r69-unreal-animation-notify-native-build-presentation-pack-20260806-081958.json`
- Unreal Animation Notify Native Bridge Build：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-bridge-build-20260806-081735.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r68-unreal-animation-notify-native-bridge-presentation-pack-20260806-080752.json`
- Unreal Animation Notify Native Bridge Readiness：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-bridge-readiness-20260806-080502.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r67-unreal-animation-attach-timing-readiness-presentation-pack-20260806-074822.json`
- Unreal Animation Attach Timing Readiness：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-attach-timing-readiness-20260806-074254.json`
- Unreal Gameplay Attach Controlled Readiness：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-gameplay-attach-controlled-readiness-20260806-072642.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r65-unreal-socket-native-controlled-write-presentation-pack-20260806-071240.json`
- Unreal Socket Native Controlled Write：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-controlled-write-20260806-070821.json`
- Unreal Socket Native Bridge Build：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-bridge-build-20260806-070743.json`
- Unreal Socket Native Receipt Dry-run：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-receipt-dryrun-20260806-064842.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r61-unreal-socket-native-source-presentation-pack-20260806-060018.json`
- Unreal Socket Native Bridge Source Readiness：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-bridge-readiness-20260806-055738.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r60-unreal-socket-native-bridge-presentation-pack-20260806-054048.json`
- Unreal Socket Native Bridge Readiness：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-bridge-readiness-20260806-053757.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r59-groom-group-root-projection-presentation-pack-20260806-052010.json`
- Groom Group / Root Projection Inspector：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-group-root-projection-20260806-051721.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r58-max-controlled-repair-presentation-pack-20260806-045801.json`
- 3ds Max Controlled Repair Executor：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-controlled-repair-20260806-045433.json`
- Blender Controlled Repair Executor：`<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-controlled-repair-20260806-043919.json`
- Houdini Rule Adapter：`<repo>\dcc-hosts\houdini-rule-adapter\artifacts\houdini-rule-adapter-contract-20260806-041956.json`
- Houdini hython L3 readiness：`<repo>\dcc-hosts\houdini-rule-adapter\artifacts\houdini-rule-adapter-l3-readiness-20260806-041956.json`
- Groom Runtime Fact Collector：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-runtime-facts-20260806-040118.json`
- Unreal Gameplay Attach Fixture：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-gameplay-attach-fixture-20260806-034615.json`
- 3ds Max Material Texture Manifest Link：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-texture-manifest-link-20260806-032426.json`
- 3ds Max L3：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260806-032411.json`
- Groom Controlled Executor：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-controlled-executor-20260806-030046.json`
- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r50-groom-plugin-api-fixture-presentation-pack-20260806-020447.json`
- Groom Plugin/API Public Fixture：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-plugin-api-fixture-20260806-020048.json`
- Groom Alembic Import/Post-check Readiness：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-alembic-import-postcheck-20260806-030028.json`
- Groom Alembic Payload Receipt：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-alembic-payload-20260806-030023.json`
- Groom Alembic exported cache：`<repo>\dcc-hosts\groom-export-inspector\artifacts\cache\groom-alembic-r52-hair-schema\groom_hero_hair_001.abc`
- Groom Unreal Import Readiness：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-unreal-readiness-20260806-010008.json`
- Groom Export Inspector：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-export-inspector-maya-l3-20260806-003711.json`
- Unreal Control Rig Compile Status Bridge：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-compile-status-20260806-001504.json`
- Unreal Control Rig Face Skeleton Fixture：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-face-skeleton-fixture-20260805-235115.json`
- Unreal Control Rig Deformation Link after face skeleton：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-235154.json`
- Unreal Control Rig Fixture Authoring：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-fixture-authoring-20260805-230323.json`
- Unreal Control Rig Bridge after face skeleton：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-235140.json`
- Unreal AnimSequence Deep Facts：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-deep-facts-20260805-224206.json`
- Unreal Socket Authoring Executor：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-authoring-executor-20260805-222014.json`
- Unreal Socket Native Bridge Readiness：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-bridge-readiness-20260806-053757.json`
- Unreal Socket API docs probe：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-api-docs-20260805-222200.json`
- Unreal Socket Import Checker：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-import-checker-l3-20260805-212131.json`
- Spatial Authoring Drilldown：`<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-drilldown-20260805-203713.json`
- Character Calibration Drilldown：`<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-drilldown-20260805-202259.json`
- Platform Variant Executor Expansion Receipts：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-executor-expansion-20260805-201222.json`
- Platform Variant Controlled Executor：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-controlled-executor-20260805-200810.json`
- Platform Variant Public Texture2D Payload Fixture：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-payload-runtime-20260805-193515.json`
- Platform Variant Texture Runtime Collector：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-runtime-20260805-191529.json`
- Platform Variant Generation Planner：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-generation-plan-20260805-190052.json`
- Platform Variant Forge：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-forge-contract-20260805-183315.json`
- Platform Variant Unreal Runtime Probe：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-unreal-runtime-20260805-185026.json`
- Spatial Authoring Maya L3：`<repo>\dcc-hosts\spatial-authoring-workbench\artifacts\spatial-authoring-maya-l3-20260805-181524.json`
- Unreal Animation Bridge import L3：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-import-l3-20260805-173309.json`
- Character Calibration Maya L3：`<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json`
- Animation Continuity L3：`<repo>\dcc-hosts\animation-continuity-lab\artifacts\animation-continuity-maya-l3-20260805-162744.json`
- Blender L3：`<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json`
- 3ds Max L3：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260806-032411.json`
- Presenter Pack 结果：73 / 73 evidence files present，0 missing required files，63 demo route steps。
- Gate 仍是 `CapturePending`，原因只剩 Maya GUI 截图/录屏未采集；Animation/Unreal Animation/Blender/Max/Houdini/Platform 的 `Blocked` 是 synthetic fixture 中故意保留的业务阻断、runtime drift 或本机缺少 `hython.exe` 的明确 readiness gate。

## 2. Lightbox核心技术点覆盖

| Lightbox提炼点 | 当前覆盖 | 状态 | 后续缺口 |
| --- | --- | --- | --- |
| 业务语义进入资产数据：custom attr / UV / vertex color / sets | `Asset Protocol Workbench` 已在 Maya 写入和回读 `aiToolTaProtocol` custom attr | 已覆盖核心，Maya L3 | UV / vertex color 语义 carrier 可作为后续子功能 |
| Pyblish式 Collect / Validate / Fix / Extract | `Cross-DCC Rule Matrix`、`Asset Handoff Gate`、Blender/Max/Houdini adapter 已实现 collect、validate、fix preview、report export；R57 Blender Controlled Repair 和 R58 Max Controlled Repair 已执行真实 DCC fix/post-check/rollback receipt | 已覆盖，Maya/Blender/Max 有 runtime 证据，Houdini 有 contract/readiness 证据 | 共享 transaction recorder、更多 DCC auto-fix receipt |
| 规则和 DCC adapter 分层 | Maya adapter、Blender `bpy`、3ds Max `pymxs`、Houdini HDA/PDG/bake receipt contract 已归一化到 shared rule input | 已覆盖主要方法 | MotionBuilder、Photoshop/Substance adapter |
| 资产协议作为工作台底座 | `Asset Protocol` 串起 LOD、platform、collision、budget、handoff | 已覆盖 | 扩到 platform variant、character LOD、animation intent |
| 固定相机/固定 pass 的视觉评审 | `Visual Review Studio` 已生成 Maya camera rig、pass manifest、capture preview、report | 部分覆盖 | 真实 Maya playblast/截图和视觉 diff media |
| 贴图/材质交付检查 | `Texture Delivery Console` 已扫描 Maya material / file node / role / colorSpace / path / budget；R53 已把 3ds Max material bitmap slots 与 texture delivery manifest、BC/N/ORM channel 语义、sRGB/linear、平台尺寸预算做 join | 覆盖加深，Maya + Max L3-derived | Substance、Photoshop、DDS、SpriteSheet、真实 UE texture import |
| 任务平台和交付收据 | `Task Orchestrator` 已有 scene discovery、dry-run queue、per-asset receipts | 部分覆盖 | 真实平台 adapter、任务附件、状态同步 |
| 复合资产放行门禁 | `Asset Handoff Gate` 合并协议、规则、贴图、视觉、队列，输出 Ready/Review/Blocked 和 Decision Packet | 已覆盖，Maya L3 | 真实资产案例和 reviewer 录屏 |
| DCC 到引擎 handoff | Maya Engine Preflight + Unreal Handoff Inspector 覆盖 import intent、registry、engine facts、PC/Mobile preset 和 waiver | 覆盖强，Unreal L3++ | 真实 texture/LOD/import preset 扩展 |
| 场景事务、写入边界和 rollback preview | `Scene Transaction Guard` 输出 before/after fingerprint、created/deleted/modified、risk rows、rollback actions | 已覆盖 Maya L3 首版 | 抽成所有 DCC 工具共用的 transaction middleware |
| 动画确定性导出、Take、sub-frame、channel identity、notify timing | `Animation Continuity Lab` 已通过 Maya `mayapy` 采集 keyed animCurve facts；`Unreal Animation Bridge` 已通过 Maya FBX + Unreal Python 导入真实 public AnimSequence/Skeleton facts；R41 已只读采集 AnimSequence duration、derived frame span、frame-rate、curve/root/compression metadata visibility；R67 已把 R66 gameplay attach readiness 接到 AnimSequence notify/timing gate；R68 已把 notify 不可读推进为 public UE C++ commandlet / Editor Utility bridge source/readiness；R69/R72 已通过 RunUAT BuildPlugin 编译 `AI_Tool_TA_AnimNotifyBridge` Win64 Editor DLL；R70 已证明 packaged commandlet 能在 Unreal runtime 加载；R71 已读取 2/2 public AnimSequence 并发现缺 `equip.attach` / `gear.attach`；R72 已在 temp public AnimSequence 中受控写入这两条 notify，保存、post-check、rollback 并恢复 hash；R73 已把 controlled socket readiness、attach timing readiness 和 native notify controlled write 合成 gameplay attach timing gate | Maya L3 + Unreal import L3 + Unreal deep facts L3 + attach timing L3-derived + native bridge L3-readiness/build + commandlet L3-runtime + diagnostics L3-runtime-diagnostics + controlled write L3-runtime-controlled-write + gameplay timing L3-derived | MotionBuilder / Control Rig commandlet probe |
| 角色 DNA、拓扑、joint coverage、面部/肌肉参数迁移 | `Character Calibration Studio` 已通过 Maya `mayapy` 采集 topology / joint / calibration / face params / Control Rig mapping facts；R35 Drilldown 已把 flat rows 转成 topology/skeleton/skin/calibration/face/Control Rig/mirror panels 和 owner actions；R42 已通过 Unreal Python 创建 public `CR_HeroFace`、写入 5 个 runtime controls，并复跑 Control Rig Bridge 让 approved 行 Ready；R43 继续只读检查 control -> deformation target -> Unreal Skeleton link 和 compile API surface；R44 用 Maya FBX + Unreal import 建立 public `SK_HeroFace_Skeleton`，把 `Eye_L` / `Eye_R` / `Jaw` target 缺口 3 / 3 resolved；R45 调用 public `CR_HeroFace` compile 方法，记录 diagnostic/status、dirty-state 和 no-save 边界；R74 已把 direct diagnostics/status 不可读转成 public C++ Editor plugin source 和 Unreal runtime readiness，R75 已通过 RunUAT BuildPlugin 编译 `AI_Tool_TA_ControlRigBridge` Win64 Editor DLL | Maya L3 + L3-derived drilldown + Unreal Control Rig authoring L3 + face skeleton fixture L3 + deformation link L3 + compile status L3 + native bridge L3-readiness/build | commandlet probe、owner waiver |
| 空间热点、Socket、Pose Transfer、mirror、locator preview | `Spatial Authoring Workbench` 已通过 Maya `mayapy` 采集 joint / locator / socket / hotspot / pose frame / mirror / pose transfer facts；R36 Drilldown 已把 flat rows 转成 protocol/parent/socket/mirror/hotspot/pose frame/transform/preview/pose transfer panels 和 owner actions；R38 Unreal Socket Import Checker 已接到 Unreal SkeletalMesh/Skeleton socket API 和 expected socket coverage；R40 Unreal Socket Authoring Executor 已证明 UE 5.3 Python socket identity 字段不可写，能安全阻断自动修复；R60-R65 已完成 native bridge readiness、source package、RunUAT build、commandlet visibility、JSON receipt dry-run、controlled write / save / post-check / rollback；R54 Unreal Gameplay Attach Fixture 已把 socket/hotspot intent、attachable asset、animation context 和 attach API 连成 gameplay equip gate；R66 已把 controlled write 结果接入玩法挂接 readiness，R67 再把玩法挂接接到 animation attach timing gate，R68-R72 把 notify/timing 缺口推进到 native bridge source/readiness/build/commandlet runtime/diagnostics/controlled write，R73 已把 socket + notify executor 证据合并成 gameplay attach timing controlled readiness | Maya L3 + L3-derived drilldown + Unreal L3 + API-limited gate + native controlled executor L3 + gameplay controlled readiness L3-derived + animation timing L3-derived + native notify bridge L3-readiness/build/runtime/controlled-write + gameplay timing L3-derived | 只在需要公开常驻 socket/notify 演示时补 publish/persistence pass |
| PC -> Mobile 平台派生、LOD/材质/贴图/碰撞生成链 | `Platform Variant Forge` 已生成 PC/Mobile variant plan，用 Unreal runtime probe 对照 StaticMesh facts，把 drift 转成 dry-run generation operations，采集材质/贴图 runtime facts，导入 public Texture2D payload 验证预算，执行 public fixture max-size clamp / post-check / rollback，把 LOD/Nanite/collision 后续动作转成 approval / rollback receipts，并通过 R39 StaticMesh post-check 做只读 runtime 验证 | 已覆盖计划层 + Unreal L3 + L3-derived generation plan + texture runtime L3 + Texture2D payload L3 + controlled executor L3 + executor receipts L3-derived + StaticMesh post-check L3 | 更复杂真实风格资产 fixture、LOD/Nanite 受控写入 |
| Houdini 程序化资产、HDA、PDG、bake receipt | `Houdini Rule Adapter` 已把 HDA locked state、detail attributes、`OUT_*` 输出角色、geometry attributes、packed prototypes、PDG wedges 和 frozen bake receipts 归一化到 Cross-DCC Rule Matrix | L2+ contract + hython readiness；collector ready | 安装或定位 `hython.exe` 后升级真实 Houdini L3 |
| Groom/XGen 到 Unreal | `Groom Export Inspector` 已通过 Maya `mayapy` 采集 synthetic scalp / curve strand facts，检查 root UV、strand ID、guide curve、Alembic payload 和 Unreal binding intent；R47 `Groom Unreal Import Readiness` 已通过 Unreal 5.3.2 采集 Groom/Alembic API visibility、target SkeletalMesh presence、expected Groom / Binding assets 和 zero-write boundary；R52 `Groom Alembic Payload Receipt` 已通过 Maya `AbcExport` 写出 approved curve-only public groom `.abc` cache，记录 bytes/hash，并证明 schemaCompatibleRows=1、meshShapeRows=0；R52 `Groom Alembic Import/Post-check Readiness` 已通过 Unreal 5.3.2 读取 `.abc`、验证 sha256 continuity、dry-run AssetImportTask、检查 HairStrandsFactory / Alembic factory / Groom API / target assets / no-write boundary；R50 `Groom Plugin/API Public Fixture` 已显式启用 public Unreal 项目的 HairStrands/Alembic hair stack并证明 Groom import API ready；R52 `Groom Controlled Executor` 已真实执行 approved curve-only `.abc` 的 `HairStrandsFactory` import，产物为 `GroomAsset`，BindingAsset 创建并 post-check=true，rollback clean；R55 `Groom Runtime Fact Collector` 已在资产存在期间回读 3 个 runtime assets、23 个属性、40 个方法面和 11 个 callable facts，再 rollback clean；R59 `Groom Group / Root Projection Inspector` 已在 Maya runtime 中把 curve root CV 投影到 scalp `root_uv`，检查 group definition、guide coverage、UV region、material slot 和 Alembic group payload | Maya L3 + Unreal readiness L3 + Maya curve-only Alembic cache L3 + Unreal post-check readiness L3 + Groom plugin/API fixture L3 Ready + controlled executor L3 Ready rollback proof + runtime facts L3 Ready + group/root projection L3 | 更复杂生产风格 groom fixture；必要时做 Editor Utility / C++ bridge |

## 3. 计划中的插件线

| # | 插件/工具线 | 大白话说明 | 当前进度 |
| --- | --- | --- | --- |
| 1 | Maya AuroraView Host / Presenter Pack | 在 Maya 里打开作品集工具，并把所有证据打包给 reviewer | 已可运行；R75 Presenter Pack 73/73 evidence present；63 步 demo route；新增 Unreal Control Rig Native Bridge Build |
| 2 | Asset Protocol Workbench | 给资产写业务身份证：平台、LOD、碰撞、预算、角色等字段 | Maya custom attr 写入/回读已完成 |
| 3 | Cross-DCC Rule Matrix | 同一套发布规则，分别从 Maya/Blender/Max/Houdini 等 DCC 采集事实后检查 | Maya L3；Blender L3；Blender controlled repair L3；3ds Max L3；Max controlled repair L3；Max texture manifest link L3-derived；Houdini L2+ contract / hython readiness |
| 4 | Visual Review Studio | 自动建固定相机和固定 review pass，让视觉评审可复现 | Maya camera rig/pass manifest 已完成；真实截图/录屏待采集 |
| 5 | Texture Delivery Console | 检查材质球、贴图路径、色彩空间、命名和平台预算 | Maya material/file node inspection 已完成 |
| 6 | Task Orchestrator | 把一批资产变成可 dry-run 的发布任务队列和收据 | Maya scene discovery、queue、receipt 已完成 |
| 7 | Asset Handoff Gate | 把前面 5 个模块合成一个资产能否交付的最终门禁 | Ready/Review/Blocked、repair preview、owner disposition 已完成 |
| 8 | Engine Handoff / Unreal Handoff Inspector | 检查 DCC 交付意图进 Unreal 后是否符合路径、依赖、LOD、碰撞和平台 preset | Unreal L3++ 已完成，PC/Mobile preset fact review 已接回 Maya |
| 9 | Scene Transaction Guard | 记录工具运行前后到底改了场景什么，并给 rollback preview | Maya L3 首版完成 |
| 10 | Blender Rule Adapter | 从 Blender 采集 custom props、collections、material、UV、collision facts | `bpy` L3 完成 |
| 10.1 | Blender Controlled Repair Executor | 把 Blender blocked 行转成可执行修复收据，执行后 post-check，再 rollback | R57 L3 完成；preGate Blocked，postGate Ready，rollbackPassed=true，4/4 operations，0 assetWrites |
| 11 | 3ds Max Rule Adapter | 从 Max 采集 user props、layer/export root、LOD、material、UV、transform、collision facts，并把 material bitmap slot 连接到贴图交付 manifest | `pymxs` L3 完成；R53 Max texture manifest link 完成 |
| 11.1 | 3ds Max Controlled Repair Executor | 把 Max blocked 行转成可执行修复收据，修完 post-check，再 rollback | R58 L3 完成；preGate Blocked，postGate Ready，rollbackPassed=true，5/5 operations，postWarnings=0，postErrors=0，0 assetWrites |
| 12 | Houdini Rule Adapter | 检查 procedural HDA 资产是否有稳定协议、输出角色、packed prototype、PDG wedge 和 frozen bake receipt | R56 L2+ contract 完成；hython L3 readiness 完成但本机缺 `hython.exe` |
| 13 | Animation Continuity Lab | 检查 Maya/MotionBuilder/Unreal 动画传递中的角色身份、Take、时间、通道和曲线差异 | Maya `mayapy` L3 首版完成 |
| 14 | Unreal Animation Bridge / Deep Facts / Attach Timing / Native Notify Bridge | 把 Maya 动画连续性 facts 映射到 Unreal AnimSequence/Skeleton/root motion/curve/compression runtime facts，并继续判断 gameplay attach timing 是否可发布 | Unreal import L3 完成；R41 deep facts 完成；R67 attach timing readiness 完成；R68 native notify bridge source/readiness 完成；R69/R72 native notify bridge build 完成；R70 commandlet probe 完成；R71 native diagnostics 完成；R72 native controlled write 完成；R73 gameplay attach timing controlled readiness 完成，timingReadyByControlledWrite=1，missingAttachTimingEventsAfterControlledWrite=0 |
| 15 | Character Calibration & Intent Transfer Studio | 检查 DNA/拓扑/joint/面部参数/Unreal Control Rig 映射，避免“算法能跑但艺术表现错” | Maya `mayapy` L3 完成；R35 drilldown 完成；R42 Unreal Control Rig Fixture Authoring Ready；R44 Face Skeleton Fixture 已补齐 approved 行 Skeleton targets；R45 compile 方法可调用但 diagnostic/status 仍 Review；R74 native bridge source/runtime readiness 已完成，missingRequiredNativeFiles=0 |
| 16 | Spatial Authoring & Pose Transfer Workbench | 用热点图、pose frame、locator preview 管 socket、挂点、pose copy、mirror | Maya `mayapy` L3 完成；R36 drilldown 完成；R38 Unreal Socket Import Checker L3 完成；R40 Socket Authoring Executor 给出 API-limited gate；R60-R65 native bridge/source/build/commandlet/dry-run/controlled write 完成；R54 Gameplay Attach Fixture、R66 Controlled Readiness、R67 Attach Timing Readiness、R68 Anim Notify Native Bridge Readiness、R69/R72 Anim Notify Native Bridge Build、R70 Anim Notify Commandlet Probe、R71 Native Diagnostics、R72 Native Controlled Write、R73 Gameplay Attach Timing Controlled Readiness 完成 |
| 17 | Platform Variant Forge | 从 PC 资产派生 Mobile 资产，联动命名、LOD、材质、贴图、碰撞、预算 | R28 plan + R29 Unreal runtime + R30 generation plan + R31 texture runtime + R32 public Texture2D payload + R33 controlled executor + R34 executor receipts + R39 StaticMesh post-check 完成 |
| 18 | Unreal Socket Import Checker / Authoring Executor / Native Bridge / Gameplay Attach / Animation Timing | 把 Maya socket / hotspot / pose transfer facts 对照到 Unreal Skeleton / socket runtime facts，并继续判断玩法 equip attach 和动画触发点是否可交付 | R38 runtime checker 完成；R40 controlled executor 证明 UE 5.3 Python socket identity 字段不可写；R60-R65 已完成 native bridge readiness/source/build/commandlet/receipt dry-run/controlled write；R66 gameplay attach controlled readiness 完成；R67 animation attach timing readiness 暴露 notify timing gate；R68 native notify bridge source/readiness 已接入；R69/R72 native notify bridge build 完成；R70 native notify commandlet probe 完成；R71 native diagnostics 完成；R72 native controlled write 完成；R73 socket + notify gameplay timing controlled readiness 完成 |
| 19 | Character LOD Bake Planner | 给角色部件规划 LOD、贴图烘焙、normal/tangent/vertex color payload | 计划阶段 |
| 20 | Groom Export Inspector / Unreal Readiness / Alembic Payload / Import Post-check / Plugin API Fixture / Controlled Executor / Runtime Fact Collector / Group Root Projection | 检查 XGen/groom 到 Unreal 的 root UV、strand ID、guide curve、curve-only Alembic payload、Groom/Alembic API、目标 SkeletalMesh、cache receipt、import/post-check readiness、public plugin/API surface、真实 executor rollback、runtime fact readback、group/root projection 和材质槽路由 | R46 Maya L3 完成；R47 Unreal readiness L3 完成；R52 Maya `AbcExport` curve-only payload receipt 完成；R52 Unreal post-check readiness 完成，cache hash matched，AssetImportTask/HairStrandsFactory/Alembic factory 可 dry-run；R50 Groom Plugin/API Fixture Ready；R52 controlled executor 已真实 import approved `.abc` 为 `GroomAsset`，BindingAsset 创建并回滚 clean；R55 runtime fact collector Ready，3 runtime assets / 23 properties / 40 methods / 11 callable facts；R59 group/root projection L3 完成，approved groom 6/6 root projection matched，3/3 group rows pass |

## 4. 当前开发进度

| 插件/工具线 | 完成度判断 | 能展示什么 | 不能展示什么 |
| --- | --- | --- | --- |
| Maya Host / Presenter Pack | 98% | Maya 内打开工具、外部 command bridge、63 步 demo route、73 个证据文件探测 | 9 张截图和 1 段录屏未采集 |
| Asset Protocol Workbench | 75% | Maya 节点 custom attr 协议写入、inspect、DCC evidence report | UV/vertex color 语义 carrier 未实装 |
| Cross-DCC Rule Matrix | 90% | Maya scene facts、6 条规则、fix preview、Blender/Max runtime adapter、Blender/Max controlled repair rollback、Houdini HDA/PDG/bake receipt contract | Houdini 缺真实 hython L3；规则覆盖仍可加深 |
| Visual Review Studio | 55% | camera rig、pass manifest、capture preview path、review report | 真实 playblast/截图、图片 diff、HTML 视觉报告未进入 DCC-first media |
| Texture Delivery Console | 62% | Maya 材质/贴图节点扫描、色彩空间和路径检查、manifest；R53 从 Max material slot 反查 texture package coverage、BC/N/ORM 语义和 Mobile 预算 | DDS/SP/Photoshop/SpriteSheet/UE texture import |
| Task Orchestrator | 55% | dry-run 队列、per-asset receipts、report export | 真实任务平台 adapter 和附件同步 |
| Asset Handoff Gate | 70% | 合成资产批量 gate、Decision Packet、engine intent、owner held | 真实资产案例和 reviewer 录屏 |
| Unreal Handoff Inspector | 80% | Unreal 5.3 L3++ engine facts、registry fixture、PC/Mobile waiver review | 可继续扩真实 import preset |
| Scene Transaction Guard | 65% | Maya scene diff、risk rows、rollback preview | 还不是所有工具共享的 transaction middleware |
| Blender Rule Adapter | 70% | Blender 5.2 `bpy` L3、custom props/collection/material/UV/collision 采集 | 还缺真实复杂 Blender 资产 fixture |
| Blender Controlled Repair Executor | 72% | Blender 5.2 background 执行 collision proxy、LOD1、UV metric、material/texture metadata 4 条 public repair receipt；post-check Ready；rollback fingerprint matched；0 assetWrites | 还缺真实复杂资产上的 repair 策略、共享 transaction middleware |
| 3ds Max Rule Adapter | 82% | 3ds Max 2022 `pymxs` L3、user props/layer/LOD/material/UV/transform/collision/material texture rows 采集；R53 material slot -> texture manifest link 已完成；R58 controlled repair 已完成 | 还缺真实复杂 Max 资产 fixture、共享 transaction middleware |
| 3ds Max Controlled Repair Executor | 74% | 3ds Max 2022 batch 执行 UCX collision、LOD1、MI 材质/贴图、UV/map channel、transform/vertex-color 5 条 public repair receipt；post-check Ready；rollback fingerprint matched；0 assetWrites | 还缺真实复杂资产上的 repair 策略、共享 transaction middleware |
| Houdini Rule Adapter | 55% | HDA locked state、detail attributes、`OUT_*` 输出角色、geometry attrs、packed prototypes、PDG wedges、frozen bake receipt 已归一到 Cross-DCC Rule Matrix；hython launcher / collector ready | 本机缺 `hython.exe`，真实 Houdini L3 待升级；还缺复杂 HDA fixture |
| Animation Continuity Lab | 45% | Maya `mayapy` L3 keyed animCurve 采集，rig/skeleton/take/sample/channel/sub-frame/root-motion/layer 检查，fix preview 和 Presenter Pack 接入 | 没有 Maya UI drilldown；MotionBuilder 对照未做 |
| Unreal Animation Bridge | 90% | Maya 生成 FBX、Unreal Python 导入 Skeleton/SkeletalMesh/AnimSequence、2/2 sequences present；R41 只读采集 duration、derived frame span、frame-rate、root motion、compression metadata visibility；R67 把 gameplay attach intent 接到 AnimSequence notify/timing gate；R68 已新增 `AI_Tool_TA_AnimNotifyBridge` source/readiness，runtimeEntered=true，missingRequiredNativeFiles=0；R69/R72 已通过 RunUAT BuildPlugin 编译 Win64 Editor DLL；R70 已加载 packaged plugin；R71 已读取 2/2 public AnimSequence；R72 已完成 `equip.attach` / `gear.attach` 受控写入、post-check、rollback、hash restore；R73 已合成 gameplay attach timing controlled readiness | curve names / MotionBuilder 对照仍待后续 |
| Character Calibration Studio | 88% | Maya `mayapy` L3 采集 topology signature、joint coverage、calibration delta、face params、Control Rig mapping；R35 drilldown 输出 14 个 UI-ready panels、8 条 owner actions；R42 创建 public `CR_HeroFace`，写入 5 个 runtime controls；R44 创建 public `SK_HeroFace_Skeleton` 并复跑 deformation-link；R45 调用 compile 方法并证明无 dirty/save 副作用；R74 新增 `AI_Tool_TA_ControlRigBridge` source/readiness；R75 通过 RunUAT BuildPlugin 编译 Win64 Editor DLL | commandlet probe、owner waiver 还可深化 |
| Spatial Authoring Workbench | 97% | Maya `mayapy` L3 采集 socket parent joint、offset、mirror pair、hotspot semantic/owner、pose frame、local space、preview locator、pose transfer approval；R36 drilldown 输出 18 个 UI-ready panels、9 条 owner actions；R38 Unreal Socket Import Checker 输出 SkeletalMesh/Skeleton socket API 和 expected socket coverage；R40 executor 证明 UE 5.3 Python socket authoring API 边界；R60-R65 已完成 native bridge readiness、source/build、commandlet visibility、JSON receipt dry-run、controlled write / post-check / rollback；R54 gameplay attach 把 socket/hotspot intent 接到 attachable/animation/API runtime gate；R66 controlled readiness 把主武器挂接从 pure Blocked 推到 executor-backed Review；R67 再把它接到 animation notify/timing gate；R68-R73 给 notify timing 补了 native source/readiness/build/commandlet runtime/diagnostics/controlled write/gameplay timing readiness | 只在需要公开常驻 socket/notify 演示时补 publish/persistence pass |
| Platform Variant Forge | 90% | PC/Mobile variant plan、Unreal preset fact join、Unreal 5.3 runtime-vs-plan 检查、dry-run generation operation contract、material/texture runtime facts、public 2048 Texture2D payload budget proof、public fixture 受控执行和 rollback、LOD/Nanite/collision approval receipts、StaticMesh post-check | 复杂真实风格资产 fixture、LOD/Nanite 受控写入未做 |
| Groom Export Inspector | 97% | Maya `mayapy` L3 采集 root UV、strand ID、guide curve、Alembic payload、Unreal Groom/Binding intent；Unreal 5.3.2 L3 readiness 采集 AssetImportTask、AlembicImportFactory、target SkeletalMesh、Groom API 和期望 Groom/Binding 资产缺口；R52 Maya `AbcExport` 写出 approved curve-only public `.abc` cache，记录 bytes/hash/schemaCompatibleRows=1/meshShapeRows=0；R52 Unreal 读取 `.abc` 并验证 sha256 continuity、AssetImportTask dry-run、HairStrandsFactory/Alembic factory visibility、target `SK_HeroFace` 和 no-write boundary；R50 public Unreal fixture 已启用 HairStrands/Alembic hair stack 并证明 Groom import API ready；R52 controlled executor 已真实执行 `HairStrandsFactory` import，记录 imported class=`GroomAsset`、BindingAsset post-check=true、rollback clean、residual assets=0；R55 runtime fact collector 已读 3 runtime assets、23 properties、40 methods、11 callable facts；R59 group/root projection 已把 curve root CV、scalp root_uv、group coverage、guide coverage、UV region、material slot 和 Alembic group payload 归到同一个发布门禁 | 更复杂生产风格 groom fixture；必要时走 Editor Utility / C++ bridge |

## 5. 需要手动操作的活

Maya GUI：输入命令只是一种临时启动方式。现在有三种入口：

1. 每个 Maya 会话手动运行一次：

   ```python
   import sys
   host = r"<repo>\dcc-hosts\maya-auroraview-host"
   if host not in sys.path:
       sys.path.insert(0, host)
   from ai_tool_ta_maya_host import show_portfolio
   show_portfolio()
   ```

2. 一次性安装 shelf，以后点 `AI Tool TA`：

   ```python
   exec(open(r"<repo>\dcc-hosts\maya-auroraview-host\shelf\install_shelf_button.py", "r").read())
   ```

3. 每个 Maya 会话启动外部控制 bridge，然后外部 shell 控制：

   ```python
   exec(open(r"<repo>\dcc-hosts\maya-auroraview-host\scripts\start_maya_command_bridge.py", "r").read())
   ```

   ```powershell
   python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --show-portfolio
   python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --export-presenter-pack r61-unreal-socket-native-source-presentation-pack
   ```

仍需要人工或 GUI 自动化采集的内容：9 张 Maya GUI PNG 和 1 段 MP4，目标目录：

```text
<repo>\assets\dcc-first\r10-7-gui-evidence
```

## 6. 下一步建议

下一轮优先做 Control Rig native commandlet probe，把 R75 compiled plugin 证据推进到 Unreal runtime-loaded diagnostics。次优先是 MotionBuilder adapter。Blender/Max readiness、Max texture manifest link、Houdini contract/readiness、Groom group/root projection、socket native bridge、animation notify native bridge、gameplay attach timing controlled readiness 和 R75 Control Rig build 都已经有明确 runtime、build 或 readiness artifact，后续只在新增更高层业务闭环时回到这些线。

## R74 补充 - Unreal Control Rig Native Bridge Readiness

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r74-unreal-control-rig-native-bridge-readiness-presentation-pack-20260806-095213.json`，72/72 evidence files present，0 missing required files，62 demo route steps。
- 新增证据：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-native-bridge-readiness-20260806-094558.json`。
- 结果：L3-readiness / `Blocked` / `unreal_control_rig_native_bridge_readiness_collected`，runtimeEntered=true，Control Rig / RigVM classes visible=true，hasNativeSource=true，hasControlRigBridgePlugin=true，missingRequiredNativeFiles=0，hasCompiledBridgeBinary=false，commandletVisible=false，5 pass / 0 warning / 2 error，assetWrites=0，engineWrites=0，productionWrites=0。

## R75 补充 - Unreal Control Rig Native Bridge Build

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r75-unreal-control-rig-native-bridge-build-presentation-pack-20260806-101502.json`，73/73 evidence files present，0 missing required files，63 demo route steps。
- 新增证据：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-native-bridge-build-20260806-100928.json`。
- 结果：L3-build / `Ready` / `unreal_control_rig_native_bridge_plugin_built`，RunUAT `BuildPlugin` 编译 public `AI_Tool_TA_ControlRigBridge` Editor plugin，returnCode=0，compiledDlls=1，errorLines=0，compilerVersion=14.38.33130，configRestored=true，DLL bytes=151552，sha256=`9930fe41e8c2893f860eb03059539b5cbbf58e318158be3636200b949a5a476b`，assetWrites=0，engineWrites=0，productionWrites=0。


## R39 补充

- Platform Variant StaticMesh Post-check：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-staticmesh-postcheck-20260805-215500.json`
- 结果：L3 / `Review` / `unreal_staticmesh_postcheck_collected`，5 receipts，2 runtime targets，2 no-op matched，3 owner-held，32 pass / 3 warning / 0 error，assetWrites=0，productionWrites=0。

## R40 补充

- Unreal Socket Authoring Executor：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-authoring-executor-20260805-222014.json`
- Unreal Socket API docs probe：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-api-docs-20260805-222200.json`
- 结果：L3 / `Blocked` / `unreal_socket_authoring_executor_api_limited`，selected/held 1 / 1，expected/created sockets 2 / 0，9 pass / 0 warning / 2 error，assetWrites=0，productionWrites=0。

## R41 补充

- Unreal AnimSequence Deep Facts：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-deep-facts-20260805-224206.json`
- 结果：L3 / `Blocked` / `unreal_animsequence_deep_facts_collected`，2 runtime rows，2 / 2 duration frame spans matched，0 Ready / 1 Review / 1 Blocked，15 pass / 2 warning / 1 error，assetWrites=0。

## R42 补充

- Unreal Control Rig Fixture Authoring：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-fixture-authoring-20260805-230323.json`
- Unreal Control Rig Bridge after fixture authoring：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-230343.json`
- 结果：fixture authoring L3 / `Ready`，1 selected / 1 held，created/saved assets 1 / 1，required/runtime/missing controls 5 / 5 / 0，assetWrites=1，productionWrites=0；post-authoring bridge L3 / `Blocked`，approved 行 Ready，TMP 行 Blocked，10 pass / 1 warning / 5 error，assetWrites=0。

## R43 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r43-unreal-control-rig-deformation-link-presentation-pack-20260805-233308.json`，41/41 evidence files present，0 missing required files，32 demo route steps。
- Unreal Control Rig Deformation Link：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-232729.json`
- 结果：L3 / `Blocked` / `unreal_control_rig_deformation_link_collected`，2 character rows，10 control links，5 runtime controls，5 shape/offset-readable controls，2 Skeleton target matches，0 direct compile-status rows，12 pass / 2 warning / 6 error，assetWrites=0，productionWrites=0。核心业务发现：approved 行虽然已经有 `CR_HeroFace` 和 5 个 controls，但 public Skeleton 未确认 `Eye_L`、`Eye_R`、`Jaw`，不能把 controls presence 误判为绑定可交付。

## R44 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r44-unreal-control-rig-face-skeleton-fixture-presentation-pack-20260805-235700.json`，42/42 evidence files present，0 missing required files，33 demo route steps。
- Unreal Control Rig Face Skeleton Fixture：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-face-skeleton-fixture-20260805-235115.json`
- Unreal Control Rig Deformation Link after face skeleton：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-235154.json`
- 结果：Face Skeleton Fixture 为 L3 / `Review`，Maya 2026 `mayapy` 生成 public face Skeleton FBX，Unreal 5.3.2 导入 `SK_HeroFace` / `SK_HeroFace_Skeleton`，required target matches 4 / 4，previous missing resolved 3 / 3，assetWrites=2，productionWrites=0。复跑 deformation-link 后 approved 行从 Blocked 变 Review，runtime controls 5，Skeleton target matches 5，shape/offset-readable controls 5，13 pass / 2 warning / 5 error；剩余缺口是 direct compile status API 不可读。

## R45 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r45-unreal-control-rig-compile-status-presentation-pack-20260806-001919.json`，43/43 evidence files present，0 missing required files，34 demo route steps。
- Unreal Control Rig Compile Status Bridge：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-compile-status-20260806-001504.json`
- 结果：L3 / `Blocked` / `unreal_control_rig_compile_status_collected`，2 character rows，approved 行 Review，TMP 行 Blocked，compile candidate / method visible / invoked / succeeded = 1 / 1 / 1 / 1，direct status / diagnostics / settings = 0 / 0 / 1，dirtyAfter=0，10 pass / 2 warning / 4 error，assetWrites=0，productionWrites=0。核心业务发现：compile 调用可行，但 direct diagnostics 不可读，不能把方法调用包装成 compile approval。

## R46 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r46-groom-export-inspector-presentation-pack-20260806-004101.json`，44/44 evidence files present，0 missing required files，35 demo route steps。
- Groom Export Inspector Maya L3：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-export-inspector-maya-l3-20260806-003711.json`
- 结果：L3 / `Blocked` / `maya_groom_export_facts_collected`，2 groom rows，1 Ready，1 Blocked，11 strands，2 guides，root UV missing / duplicate strand IDs = 1 / 1，11 pass / 2 warning / 7 error，9 owner actions，assetWrites=0，productionWrites=0。核心业务发现：groom 交付必须把 root UV、strand ID、guide curve 和 Alembic payload 当成发布事实。

## R47 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r47-groom-unreal-readiness-presentation-pack-20260806-010323.json`，45/45 evidence files present，0 missing required files，36 demo route steps。
- Groom Unreal Import Readiness：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-unreal-readiness-20260806-010008.json`
- 结果：L3 / `Blocked` / `unreal_groom_import_readiness_collected`，Unreal 5.3.2 runtime 成功，2 groom rows，source Ready / Blocked = 1 / 1，AssetImportTask / AlembicImportFactory visible rows = 2 / 2，target SkeletalMesh present rows = 1，GroomAsset / GroomBindingAsset API visible rows = 0 / 0，expected Groom / Binding assets present = 0 / 0，12 pass / 4 warning / 6 error，10 owner actions，assetWrites=0，productionWrites=0。核心业务发现：可见 Alembic import API 不等于 Groom 资产可发布，Groom plugin/API 与 Binding 目标必须先被 runtime 证明。

## R48 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r48-groom-alembic-payload-presentation-pack-20260806-012304.json`，47/47 evidence files present，0 missing required files，37 demo route steps。
- Groom Alembic Payload Receipt：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-alembic-payload-20260806-030023.json`
- Groom Alembic exported cache：`<repo>\dcc-hosts\groom-export-inspector\artifacts\cache\groom-alembic-r52-hair-schema\groom_hero_hair_001.abc`
- 结果：L3 / `Blocked` / `maya_groom_curve_only_alembic_payload_exported`，Maya 2026 `AbcExport` 写出 approved curve-only public groom `.abc` cache，selected / held = 1 / 1，exportSucceeded=1，cacheFiles=1，cacheBytes=12808，cacheHashes=1，schemaCompatibleRows=1，meshShapeRows=0，16 pass / 0 warning / 2 error，2 owner actions，assetWrites=1 仅限 repo artifact cache，engineWrites=0，productionWrites=0。核心业务发现：可生成 cache 不等于坏行可放行，且 Groom importer 需要 curve-only schema。

## R49 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r49-groom-alembic-import-postcheck-presentation-pack-20260806-014423.json`，48/48 evidence files present，0 missing required files，38 demo route steps。
- Groom Alembic Import/Post-check Readiness：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-alembic-import-postcheck-20260806-030028.json`
- 结果：L3 / `Blocked` / `unreal_groom_alembic_import_postcheck_blocked`，Unreal 5.3.2 runtime 读取 R52 curve-only `.abc`，cache hash matched rows = 1，AssetImportTask dry-run rows = 2，AlembicImportFactory visible rows = 2，Groom API ready rows = 2，target SkeletalMesh present rows = 1，import executed / held = 0 / 2，25 pass / 2 warning / 1 error，3 owner actions，assetWrites=0，engineWrites=0，productionWrites=0。核心业务发现：`.abc` cache receipt 到 UE runtime 可连续追踪，但真实写入必须由 controlled executor 承接。

## R50 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r50-groom-plugin-api-fixture-presentation-pack-20260806-020447.json`，49/49 evidence files present，0 missing required files，39 demo route steps。
- Groom Plugin/API Public Fixture：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-plugin-api-fixture-20260806-020048.json`
- 结果：L3 / `Ready` / `unreal_groom_plugin_api_fixture_ready`，Unreal 5.3.2 runtime 成功，4/4 plugin descriptors found，4/4 project plugin requests，Groom / Hair / Alembic / GeometryCache class rows = 47 / 56 / 14 / 16，Groom import API ready=true，AlembicImportFactory visible=true，10 pass / 0 warning / 0 error，assetWrites=0，engineWrites=0，productionWrites=0。核心业务发现：public fixture 层已解决 Groom API 可见性，下一步应进入受控 GroomAsset / BindingAsset executor、post-check 和 rollback receipt。

## R52 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r52-groom-hair-schema-executor-presentation-pack-20260806-030427.json`，50/50 evidence files present，0 missing required files，40 demo route steps。
- Groom Controlled Executor：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-controlled-executor-20260806-030046.json`
- 结果：L3 / `Ready` / `unreal_groom_executor_import_binding_rolled_back`，Unreal 5.3.2 runtime 成功执行 approved curve-only `.abc` import，selected=1，import attempted/succeeded=true/true，imported asset class=`GroomAsset`，wrongImportedClass=false，GroomAsset post-check=true，BindingAsset 创建并 post-check=true，rollback=true，residual assets=0，11 pass / 0 warning / 0 error，assetWrites=6，engineWrites=0，productionWrites=0，persistentMutation=false。核心业务发现：当前缺口已从 plugin/API 和 cache receipt 推进到完整 GroomAsset / BindingAsset 受控执行闭环。

## R53 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r53-max-texture-manifest-link-presentation-pack-20260806-032705.json`，51/51 evidence files present，0 missing required files，41 demo route steps。
- 3ds Max L3：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260806-032411.json`，新增 `materialTextureRows`，3 条 material bitmap slot facts 来自真实 Max 2022 `pymxs` batch。
- 3ds Max Material Texture Manifest Link：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-texture-manifest-link-20260806-032426.json`
- 结果：L3-derived / `Blocked` / `max_material_texture_manifest_linked`，2 assets，1 Ready / 1 Blocked，slotTextures=4，manifestTextures=4，missingManifestTextures=0，missingRequiredSemantics=2，13 pass / 1 warning / 2 error，assetWrites=0，productionWrites=0。核心业务发现：真实贴图交付判断要把 DCC material slot、交付包 manifest、channel 语义、色彩空间和平台预算放在同一个 gate 里，不能只做路径存在检查。

## R54 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r54-unreal-gameplay-attach-fixture-presentation-pack-20260806-035002.json`，52/52 evidence files present，0 missing required files，42 demo route steps。
- Unreal Gameplay Attach Fixture：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-gameplay-attach-fixture-20260806-034615.json`
- 结果：L3-linked / `Blocked` / `unreal_gameplay_attach_fixture_linked`，2 gameplay intents，0 Ready / 0 Review / 2 Blocked，attachable assets present=2，animation assets present=2，required/missing runtime sockets=4 / 4，required/missing hotspot semantics=2 / 1，15 pass / 1 warning / 6 error，assetWrites=0，productionWrites=0。核心业务发现：道具和动画都在引擎里存在，也不能说明 gameplay equip 可用；角色 socket 合约缺失必须阻断。

## R55 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r55-groom-runtime-facts-presentation-pack-20260806-040806.json`，53/53 evidence files present，0 missing required files，43 demo route steps。
- Groom Runtime Fact Collector：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-runtime-facts-20260806-040118.json`
- 结果：L3 / `Ready` / `unreal_groom_runtime_facts_collected`，Unreal 5.3.2 在 GroomAsset / GroomBindingAsset public fixture 存在期间读取 3 个 runtime assets、23 个属性、40 个方法面、11 个 callable facts，再 rollback clean，residual assets=0，11 pass / 0 warning / 0 error，assetWrites=6，productionWrites=0。核心业务发现：受控执行后还要读取 runtime object surface，证明资产不是只“导入成功”，而是能被引擎侧业务继续校验。

## R56 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r56-houdini-rule-adapter-presentation-pack-20260806-042654.json`，55/55 evidence files present，0 missing required files，45 demo route steps。
- Houdini Rule Adapter：`<repo>\dcc-hosts\houdini-rule-adapter\artifacts\houdini-rule-adapter-contract-20260806-041956.json`
- Houdini hython L3 readiness：`<repo>\dcc-hosts\houdini-rule-adapter\artifacts\houdini-rule-adapter-l3-readiness-20260806-041956.json`
- 结果：L2+ / `Blocked` / `blocked_by_missing_hython`，2 procedural assets，1 Ready / 0 Review / 1 Blocked，11 pass / 2 warning / 5 error，HDA locked state、detail attributes、`OUT_*` role nodes、geometry attrs、packed prototypes、PDG wedges 和 frozen bake receipt 全部进入 `cross-dcc-rule-input@0.1.0`。本机未发现 `hython.exe`，collector ready，sceneWrites / assetWrites / productionWrites 全为 0。核心业务发现：Houdini 程序化资产的交付秘诀不是只看最终 mesh，而是证明 procedural network 可冻结、可复现、可拆 role、可追踪 cook/wedge/bake 收据。

## R57 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r57-blender-controlled-repair-presentation-pack-20260806-044229.json`，56/56 evidence files present，0 missing required files，46 demo route steps。
- Blender Controlled Repair Executor：`<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-controlled-repair-20260806-043919.json`
- 结果：L3 / `Ready` / `blender_controlled_repair_rolled_back`，Blender 5.2 background runtime，preGate=Blocked，postGate=Ready，rollbackPassed=true，selected/executed=4/4，postReadyAssets=2，postBlockedAssets=0，assetWrites=0，productionWrites=0。核心业务发现：Lightbox/Pyblish 的 Fix 不是“自动把资产改好”这么简单，而是 repair receipt、post-check 和 rollback boundary 的三件套。

## R58 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r58-max-controlled-repair-presentation-pack-20260806-045801.json`，57/57 evidence files present，0 missing required files，47 demo route steps。
- 3ds Max Controlled Repair Executor：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-controlled-repair-20260806-045433.json`
- 结果：L3 / `Ready` / `max_controlled_repair_rolled_back`，3ds Max 2022 batch runtime，preGate=Blocked，postGate=Ready，rollbackPassed=true，selected/executed=5/5，postReadyAssets=2，postBlockedAssets=0，postWarnings=0，postErrors=0，assetWrites=0，productionWrites=0。核心业务发现：Max 侧自动修复必须把 UCX collision、LOD、材质贴图、UV/map channel 和 transform/vertex-color 都拆成可审计 receipt，post-check 后再证明 rollback boundary。

## R59 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r59-groom-group-root-projection-presentation-pack-20260806-052010.json`，58/58 evidence files present，0 missing required files，48 demo route steps。
- Groom Group / Root Projection Inspector：`<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-group-root-projection-20260806-051721.json`
- 结果：L3 / `Blocked` / `maya_groom_group_root_projection_collected`，Maya 2026 runtime，2 assets，1 Ready / 0 Review / 1 Blocked，10 strand projection rows，4 group coverage rows，projectionMatchedStrands=6，groupMatchedStrands=7，materialMatchedStrands=8，maxProjectionDrift=0.175，10 pass / 1 warning / 7 error，assetWrites=0，engineWrites=0，productionWrites=0。核心业务发现：Groom/XGen 发布的业务重点不只是导出 `.abc`，还要证明曲线根点能落回正确 scalp UV 区域、group 有 guide 覆盖、发丝 group 和材质槽能映射到 Unreal hair material，TMP 行应在这些任一事实错误时被阻断。

## R60 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r60-unreal-socket-native-bridge-presentation-pack-20260806-054048.json`，59/59 evidence files present，0 missing required files，49 demo route steps。
- Unreal Socket Native Bridge Readiness：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-bridge-readiness-20260806-053757.json`
- 结果：L3-readiness / `Blocked` / `unreal_socket_native_bridge_readiness_collected`，Unreal 5.3.2 runtime，sourceApiLimited=true，expectedSockets=2，createdSocketsViaPython=0，socketClassesVisible=true，editorUtilitySurfaceVisible=true，hasNativeSource=false，hasSocketBridgePlugin=false，hasCompiledBridgeBinary=false，commandletVisible=false，missingRequiredNativeFiles=6，6 pass / 0 warning / 3 error，assetWrites=0，productionWrites=0。核心业务发现：Maya socket authoring 到 Unreal gameplay attach 的真实缺口已经定位到 native bridge 工程面，而不是再尝试 UE Python 反射写 read-only socket identity。

## R61 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r61-unreal-socket-native-source-presentation-pack-20260806-060018.json`，59/59 evidence files present，0 missing required files，49 demo route steps。
- Unreal Socket Native Bridge Source Readiness：`<repo>\dcc-hosts\unreal-socket-import-checker\artifacts\unreal-socket-native-bridge-readiness-20260806-055738.json`
- AI_Tool_TA_SocketBridge source package：`<repo>\dcc-hosts\unreal-handoff-inspector\projects\AI_Tool_TA_Unreal_L3\Plugins\AI_Tool_TA_SocketBridge`
- 结果：L3-readiness / `Blocked` / `unreal_socket_native_bridge_readiness_collected`，Unreal 5.3.2 runtime，hasNativeSource=true，hasSocketBridgePlugin=true，missingRequiredNativeFiles=0，hasCompiledBridgeBinary=false，commandletVisible=false，7 pass / 0 warning / 2 error，assetWrites=0，productionWrites=0。核心业务发现：socket native bridge 已从“没有工程面”推进到“源码 contract 可审查”，下一步是构建加载和受控写入收据。

## R69 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r69-unreal-animation-notify-native-build-presentation-pack-20260806-081958.json`，67/67 evidence files present，0 missing required files，57 demo route steps。
- Unreal Animation Notify Native Bridge Build：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-bridge-build-20260806-081735.json`
- 结果：L3-build / `Ready` / `unreal_animation_notify_native_bridge_plugin_built`，RunUAT `BuildPlugin` 编译 public `AI_Tool_TA_AnimNotifyBridge` Editor plugin，returnCode=0，compiledDlls=1，errorLines=0，compilerVersion=14.38.33130，configRestored=true，DLL bytes=195584，sha256=`1f42afb1a87dae5baa2dae759adb521b96ffde233449a999aaaeea19d67be459`，assetWrites=0，engineWrites=0，productionWrites=0。核心业务发现：AnimSequence notify/timing 缺口已经从 Python API 不可读推进到可编译 native bridge，下一步应证明 packaged plugin commandlet 能在 Unreal runtime 中加载并导出 diagnostics。

## R70 补充

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r70-unreal-animation-notify-native-commandlet-presentation-pack-20260806-083529.json`，68/68 evidence files present，0 missing required files，58 demo route steps。
- Unreal Animation Notify Native Commandlet Probe：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-commandlet-probe-20260806-083144.json`
- 结果：L3-runtime / `Ready` / `unreal_animation_notify_native_commandlet_loaded`，R69 packaged `AI_Tool_TA_AnimNotifyBridge` 在临时 Unreal 5.3 project 中加载成功，`-run=AiToolTaAnimNotifyDiagnostics` returnCode=0，commandletLoaded=true，readinessInvocation=true，outputStatus=`readiness_invocation_only`，requestedAnimSequencePaths=0，errorLines=0，tempProjectWrites=70，assetWrites=0，engineWrites=0，productionWrites=0。核心业务发现：native bridge 已通过 runtime visibility gate，下一步应输入真实 public AnimSequence paths 采集 notify rows。


## R71 补充 - Unreal Animation Notify Native Diagnostics

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r71-unreal-animation-notify-native-diagnostics-presentation-pack-20260806-085351.json`，69/69 evidence files present，0 missing required files，59 demo route steps。
- Unreal Animation Notify Native Diagnostics：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-diagnostics-20260806-085035.json`
- 结论：packaged commandlet 已在 Unreal 5.3 temp project 中读取 R67 的 2 条 AnimSequence 路径，2/2 loaded，outputStatus=`diagnostics_completed`，notifyRows=0，missingAttachTimingEvents=2，productionWrites=0。Blocked 是业务资产缺少 attach timing notify，不是 runtime 失败。

## R72 补充 - Unreal Animation Notify Native Controlled Write

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r72-unreal-animation-notify-native-controlled-write-presentation-pack-20260806-091404.json`，70/70 evidence files present，0 missing required files，60 demo route steps。
- Unreal Animation Notify Native Bridge Build：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-bridge-build-20260806-090905.json`
- Unreal Animation Notify Native Controlled Write：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-notify-native-controlled-write-20260806-090946.json`
- 结论：R72 commandlet 已在 Unreal 5.3 temp project 中把 `equip.attach` 和 `gear.attach` 写入 2 条 public AnimSequence，保存后 post-check 2/2 可见，再 rollback 删除 2/2，并由 harness 恢复 `.uasset` hash。结果为 L3-runtime-controlled-write / Ready，outputStatus=`apply_postcheck_rollback_completed`，assetWrites=4，productionWrites=0，persistentMutation=false，finalHashRestored=true。核心价值是把 Lightbox 式“发现问题/给 owner action”升级为“引擎内受控执行/复查/可回滚”的工具管线能力。

## R73 补充 - Unreal Gameplay Attach Timing Controlled Readiness

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r73-unreal-gameplay-attach-timing-controlled-readiness-presentation-pack-20260806-093254.json`，71/71 evidence files present，0 missing required files，61 demo route steps。
- Unreal Gameplay Attach Timing Controlled Readiness：`<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-gameplay-attach-timing-controlled-readiness-20260806-092934.json`
- 结论：R73 把 R66 gameplay attach controlled readiness、R67 attach timing readiness 和 R72 native notify controlled write 合成一个玩法挂接门禁。结果为 L3-derived / Review，notifyControlledWriteReady=true，timingReadyByControlledWrite=1，heldBySocketOrSource=1，timingBlocked=0，missingAttachTimingEventsAfterControlledWrite=0，productionWrites=0，finalHashRestored=true。approved rifle equip 已经同时有 socket executor 和 notify executor 证据；temporary backpack 继续由 source owner 阻断。
