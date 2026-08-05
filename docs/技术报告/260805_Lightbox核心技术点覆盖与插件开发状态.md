# Lightbox核心技术点覆盖与插件开发状态

更新时间：2026-08-05  
工程根目录：`<repo>`  
当前发布包：`ai-tool-ta-dcc-first-showcase-r52` / `dcc-first-package@1.49.0`

## 1. 当前结论

当前作品集已经不是纯前端展示。主入口是 Maya 2024 内的 AuroraView 面板，React/TypeScript 只是嵌入式工具界面；证据层由 Maya `mayapy`、Blender `bpy`、3ds Max `pymxs`、Unreal Python 和普通 Python fixture 共同生成。

R52 的硬证据：

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r52-groom-hair-schema-executor-presentation-pack-20260806-030427.json`
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
- 3ds Max L3：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260805-153232.json`
- Presenter Pack 结果：50 / 50 evidence files present，0 missing required files，40 demo route steps。
- Gate 仍是 `CapturePending`，原因只剩 Maya GUI 截图/录屏未采集；Animation/Unreal Animation/Blender/Max/Platform 的 `Blocked` 是 synthetic fixture 中故意保留的业务阻断或 runtime drift，不是 runtime 缺失。

## 2. Lightbox核心技术点覆盖

| Lightbox提炼点 | 当前覆盖 | 状态 | 后续缺口 |
| --- | --- | --- | --- |
| 业务语义进入资产数据：custom attr / UV / vertex color / sets | `Asset Protocol Workbench` 已在 Maya 写入和回读 `aiToolTaProtocol` custom attr | 已覆盖核心，Maya L3 | UV / vertex color 语义 carrier 可作为后续子功能 |
| Pyblish式 Collect / Validate / Fix / Extract | `Cross-DCC Rule Matrix`、`Asset Handoff Gate`、Blender/Max adapter 已实现 collect、validate、fix preview、report export | 已覆盖，Maya/Blender/Max 均有 runtime 证据 | Houdini adapter、共享 transaction recorder |
| 规则和 DCC adapter 分层 | Maya adapter、Blender `bpy`、3ds Max `pymxs` 已归一化到 shared rule input | 已覆盖主要方法 | Houdini、MotionBuilder、Photoshop/Substance adapter |
| 资产协议作为工作台底座 | `Asset Protocol` 串起 LOD、platform、collision、budget、handoff | 已覆盖 | 扩到 platform variant、character LOD、animation intent |
| 固定相机/固定 pass 的视觉评审 | `Visual Review Studio` 已生成 Maya camera rig、pass manifest、capture preview、report | 部分覆盖 | 真实 Maya playblast/截图和视觉 diff media |
| 贴图/材质交付检查 | `Texture Delivery Console` 已扫描 Maya material / file node / role / colorSpace / path / budget | 部分覆盖 | Substance、Photoshop、DDS、SpriteSheet、真实 UE texture import |
| 任务平台和交付收据 | `Task Orchestrator` 已有 scene discovery、dry-run queue、per-asset receipts | 部分覆盖 | 真实平台 adapter、任务附件、状态同步 |
| 复合资产放行门禁 | `Asset Handoff Gate` 合并协议、规则、贴图、视觉、队列，输出 Ready/Review/Blocked 和 Decision Packet | 已覆盖，Maya L3 | 真实资产案例和 reviewer 录屏 |
| DCC 到引擎 handoff | Maya Engine Preflight + Unreal Handoff Inspector 覆盖 import intent、registry、engine facts、PC/Mobile preset 和 waiver | 覆盖强，Unreal L3++ | 真实 texture/LOD/import preset 扩展 |
| 场景事务、写入边界和 rollback preview | `Scene Transaction Guard` 输出 before/after fingerprint、created/deleted/modified、risk rows、rollback actions | 已覆盖 Maya L3 首版 | 抽成所有 DCC 工具共用的 transaction middleware |
| 动画确定性导出、Take、sub-frame、channel identity | `Animation Continuity Lab` 已通过 Maya `mayapy` 采集 keyed animCurve facts；`Unreal Animation Bridge` 已通过 Maya FBX + Unreal Python 导入真实 public AnimSequence/Skeleton facts；R41 已只读采集 AnimSequence duration、derived frame span、frame-rate、curve/root/compression metadata visibility | Maya L3 + Unreal import L3 + Unreal deep facts L3 | curve names 在 UE Python 下仍不可读，后续可走 Animation Blueprint Library / C++ adapter |
| 角色 DNA、拓扑、joint coverage、面部/肌肉参数迁移 | `Character Calibration Studio` 已通过 Maya `mayapy` 采集 topology / joint / calibration / face params / Control Rig mapping facts；R35 Drilldown 已把 flat rows 转成 topology/skeleton/skin/calibration/face/Control Rig/mirror panels 和 owner actions；R42 已通过 Unreal Python 创建 public `CR_HeroFace`、写入 5 个 runtime controls，并复跑 Control Rig Bridge 让 approved 行 Ready；R43 继续只读检查 control -> deformation target -> Unreal Skeleton link 和 compile API surface；R44 用 Maya FBX + Unreal import 建立 public `SK_HeroFace_Skeleton`，把 `Eye_L` / `Eye_R` / `Jaw` target 缺口 3 / 3 resolved；R45 调用 public `CR_HeroFace` compile 方法，记录 diagnostic/status、dirty-state 和 no-save 边界 | Maya L3 + L3-derived drilldown + Unreal Control Rig authoring L3 + face skeleton fixture L3 + deformation link L3 + compile status L3 | direct diagnostic/status Editor Utility / C++ bridge、owner waiver |
| 空间热点、Socket、Pose Transfer、mirror、locator preview | `Spatial Authoring Workbench` 已通过 Maya `mayapy` 采集 joint / locator / socket / hotspot / pose frame / mirror / pose transfer facts；R36 Drilldown 已把 flat rows 转成 protocol/parent/socket/mirror/hotspot/pose frame/transform/preview/pose transfer panels 和 owner actions；R38 Unreal Socket Import Checker 已接到 Unreal SkeletalMesh/Skeleton socket API 和 expected socket coverage；R40 Unreal Socket Authoring Executor 已证明 UE 5.3 Python socket identity 字段不可写，能安全阻断自动修复 | Maya L3 + L3-derived drilldown + Unreal L3 + API-limited executor readiness | 真正 socket 写入需换 Unreal C++ / Editor Utility Blueprint adapter |
| PC -> Mobile 平台派生、LOD/材质/贴图/碰撞生成链 | `Platform Variant Forge` 已生成 PC/Mobile variant plan，用 Unreal runtime probe 对照 StaticMesh facts，把 drift 转成 dry-run generation operations，采集材质/贴图 runtime facts，导入 public Texture2D payload 验证预算，执行 public fixture max-size clamp / post-check / rollback，把 LOD/Nanite/collision 后续动作转成 approval / rollback receipts，并通过 R39 StaticMesh post-check 做只读 runtime 验证 | 已覆盖计划层 + Unreal L3 + L3-derived generation plan + texture runtime L3 + Texture2D payload L3 + controlled executor L3 + executor receipts L3-derived + StaticMesh post-check L3 | 更复杂真实风格资产 fixture、LOD/Nanite 受控写入 |
| Groom/XGen 到 Unreal | `Groom Export Inspector` 已通过 Maya `mayapy` 采集 synthetic scalp / curve strand facts，检查 root UV、strand ID、guide curve、Alembic payload 和 Unreal binding intent；R47 `Groom Unreal Import Readiness` 已通过 Unreal 5.3.2 采集 Groom/Alembic API visibility、target SkeletalMesh presence、expected Groom / Binding assets 和 zero-write boundary；R52 `Groom Alembic Payload Receipt` 已通过 Maya `AbcExport` 写出 approved curve-only public groom `.abc` cache，记录 bytes/hash，并证明 schemaCompatibleRows=1、meshShapeRows=0；R52 `Groom Alembic Import/Post-check Readiness` 已通过 Unreal 5.3.2 读取 `.abc`、验证 sha256 continuity、dry-run AssetImportTask、检查 HairStrandsFactory / Alembic factory / Groom API / target assets / no-write boundary；R50 `Groom Plugin/API Public Fixture` 已显式启用 public Unreal 项目的 HairStrands/Alembic hair stack并证明 Groom import API ready；R52 `Groom Controlled Executor` 已真实执行 approved curve-only `.abc` 的 `HairStrandsFactory` import，产物为 `GroomAsset`，BindingAsset 创建并 post-check=true，rollback clean | Maya L3 + Unreal readiness L3 + Maya curve-only Alembic cache L3 + Unreal post-check readiness L3 + Groom plugin/API fixture L3 Ready + controlled executor L3 Ready rollback proof | 更深 Groom runtime facts：curve count、group count、binding target mesh、root projection stats |

## 3. 计划中的插件线

| # | 插件/工具线 | 大白话说明 | 当前进度 |
| --- | --- | --- | --- |
| 1 | Maya AuroraView Host / Presenter Pack | 在 Maya 里打开作品集工具，并把所有证据打包给 reviewer | 已可运行；R52 Presenter Pack 50/50 evidence present；40 步 demo route；新增 Groom Controlled Executor probe |
| 2 | Asset Protocol Workbench | 给资产写业务身份证：平台、LOD、碰撞、预算、角色等字段 | Maya custom attr 写入/回读已完成 |
| 3 | Cross-DCC Rule Matrix | 同一套发布规则，分别从 Maya/Blender/Max 等 DCC 采集事实后检查 | Maya L3；Blender L3；3ds Max L3 |
| 4 | Visual Review Studio | 自动建固定相机和固定 review pass，让视觉评审可复现 | Maya camera rig/pass manifest 已完成；真实截图/录屏待采集 |
| 5 | Texture Delivery Console | 检查材质球、贴图路径、色彩空间、命名和平台预算 | Maya material/file node inspection 已完成 |
| 6 | Task Orchestrator | 把一批资产变成可 dry-run 的发布任务队列和收据 | Maya scene discovery、queue、receipt 已完成 |
| 7 | Asset Handoff Gate | 把前面 5 个模块合成一个资产能否交付的最终门禁 | Ready/Review/Blocked、repair preview、owner disposition 已完成 |
| 8 | Engine Handoff / Unreal Handoff Inspector | 检查 DCC 交付意图进 Unreal 后是否符合路径、依赖、LOD、碰撞和平台 preset | Unreal L3++ 已完成，PC/Mobile preset fact review 已接回 Maya |
| 9 | Scene Transaction Guard | 记录工具运行前后到底改了场景什么，并给 rollback preview | Maya L3 首版完成 |
| 10 | Blender Rule Adapter | 从 Blender 采集 custom props、collections、material、UV、collision facts | `bpy` L3 完成 |
| 11 | 3ds Max Rule Adapter | 从 Max 采集 user props、layer/export root、LOD、material、UV、transform、collision facts | `pymxs` L3 完成 |
| 12 | Animation Continuity Lab | 检查 Maya/MotionBuilder/Unreal 动画传递中的角色身份、Take、时间、通道和曲线差异 | Maya `mayapy` L3 首版完成 |
| 13 | Unreal Animation Bridge / Deep Facts | 把 Maya 动画连续性 facts 映射到 Unreal AnimSequence/Skeleton/root motion/curve/compression runtime facts | Unreal import L3 完成；R41 deep facts 完成，2 runtime rows，2/2 duration frame spans matched，curve metadata warning 清晰暴露 |
| 14 | Character Calibration & Intent Transfer Studio | 检查 DNA/拓扑/joint/面部参数/Unreal Control Rig 映射，避免“算法能跑但艺术表现错” | Maya `mayapy` L3 完成；R35 drilldown 完成；R42 Unreal Control Rig Fixture Authoring Ready；R44 Face Skeleton Fixture 已补齐 approved 行 Skeleton targets；R45 compile 方法可调用但 diagnostic/status 仍 Review |
| 15 | Spatial Authoring & Pose Transfer Workbench | 用热点图、pose frame、locator preview 管 socket、挂点、pose copy、mirror | Maya `mayapy` L3 完成；R36 drilldown 完成；R38 Unreal Socket Import Checker L3 完成；R40 Socket Authoring Executor 给出 API-limited gate |
| 16 | Platform Variant Forge | 从 PC 资产派生 Mobile 资产，联动命名、LOD、材质、贴图、碰撞、预算 | R28 plan + R29 Unreal runtime + R30 generation plan + R31 texture runtime + R32 public Texture2D payload + R33 controlled executor + R34 executor receipts + R39 StaticMesh post-check 完成 |
| 17 | Unreal Socket Import Checker / Authoring Executor | 把 Maya socket / hotspot / pose transfer facts 对照到 Unreal Skeleton / socket runtime facts，并评估是否能自动补 socket | R38 runtime checker 完成；R40 controlled executor 证明 UE 5.3 Python socket identity 字段不可写，selected/held 1/1，expected/created 2/0，assetWrites=0 |
| 18 | Character LOD Bake Planner | 给角色部件规划 LOD、贴图烘焙、normal/tangent/vertex color payload | 计划阶段 |
| 19 | Groom Export Inspector / Unreal Readiness / Alembic Payload / Import Post-check / Plugin API Fixture / Controlled Executor | 检查 XGen/groom 到 Unreal 的 root UV、strand ID、guide curve、curve-only Alembic payload、Groom/Alembic API、目标 SkeletalMesh、cache receipt、import/post-check readiness、public plugin/API surface 和真实 executor rollback | R46 Maya L3 完成；R47 Unreal readiness L3 完成；R52 Maya `AbcExport` curve-only payload receipt 完成；R52 Unreal post-check readiness 完成，cache hash matched，AssetImportTask/HairStrandsFactory/Alembic factory 可 dry-run；R50 Groom Plugin/API Fixture Ready；R52 controlled executor 已真实 import approved `.abc` 为 `GroomAsset`，BindingAsset 创建并回滚 clean |

## 4. 当前开发进度

| 插件/工具线 | 完成度判断 | 能展示什么 | 不能展示什么 |
| --- | --- | --- | --- |
| Maya Host / Presenter Pack | 98% | Maya 内打开工具、外部 command bridge、40 步 demo route、50 个证据文件探测 | 9 张截图和 1 段录屏未采集 |
| Asset Protocol Workbench | 75% | Maya 节点 custom attr 协议写入、inspect、DCC evidence report | UV/vertex color 语义 carrier 未实装 |
| Cross-DCC Rule Matrix | 80% | Maya scene facts、6 条规则、fix preview、Blender/Max runtime adapter | Houdini adapter 未做；规则覆盖仍可加深 |
| Visual Review Studio | 55% | camera rig、pass manifest、capture preview path、review report | 真实 playblast/截图、图片 diff、HTML 视觉报告未进入 DCC-first media |
| Texture Delivery Console | 55% | Maya 材质/贴图节点扫描、色彩空间和路径检查、manifest | DDS/SP/Photoshop/SpriteSheet/UE texture import |
| Task Orchestrator | 55% | dry-run 队列、per-asset receipts、report export | 真实任务平台 adapter 和附件同步 |
| Asset Handoff Gate | 70% | 合成资产批量 gate、Decision Packet、engine intent、owner held | 真实资产案例和 reviewer 录屏 |
| Unreal Handoff Inspector | 80% | Unreal 5.3 L3++ engine facts、registry fixture、PC/Mobile waiver review | 可继续扩真实 import preset |
| Scene Transaction Guard | 65% | Maya scene diff、risk rows、rollback preview | 还不是所有工具共享的 transaction middleware |
| Blender Rule Adapter | 70% | Blender 5.2 `bpy` L3、custom props/collection/material/UV/collision 采集 | 还缺真实复杂 Blender 资产 fixture |
| 3ds Max Rule Adapter | 70% | 3ds Max 2022 `pymxs` L3、user props/layer/LOD/material/UV/transform/collision 采集 | 还缺真实复杂 Max 资产 fixture |
| Animation Continuity Lab | 45% | Maya `mayapy` L3 keyed animCurve 采集，rig/skeleton/take/sample/channel/sub-frame/root-motion/layer 检查，fix preview 和 Presenter Pack 接入 | 没有 Maya UI drilldown；MotionBuilder/Unreal runtime 对照未做 |
| Unreal Animation Bridge | 62% | Maya 生成 FBX、Unreal Python 导入 Skeleton/SkeletalMesh/AnimSequence、2/2 sequences present；R41 只读采集 duration、derived frame span、frame-rate、root motion、compression metadata visibility，assetWrites=0 | curve names 在 UE Python 下不可读，后续需要 Animation Blueprint Library / C++ adapter |
| Character Calibration Studio | 84% | Maya `mayapy` L3 采集 topology signature、joint coverage、calibration delta、face params、Control Rig mapping；R35 drilldown 输出 14 个 UI-ready panels、8 条 owner actions；R42 创建 public `CR_HeroFace`，写入 5 个 runtime controls；R44 创建 public `SK_HeroFace_Skeleton` 并复跑 deformation-link；R45 调用 compile 方法并证明无 dirty/save 副作用 | direct diagnostic/status bridge、owner waiver 还可深化 |
| Spatial Authoring Workbench | 68% | Maya `mayapy` L3 采集 socket parent joint、offset、mirror pair、hotspot semantic/owner、pose frame、local space、preview locator、pose transfer approval；R36 drilldown 输出 18 个 UI-ready panels、9 条 owner actions；R38 Unreal Socket Import Checker 输出 SkeletalMesh/Skeleton socket API 和 expected socket coverage；R40 executor 证明 UE 5.3 Python socket authoring API 边界 | 真正自动写 socket 要换 Unreal C++ / Editor Utility Blueprint adapter；复杂 gameplay attach fixture 未做 |
| Platform Variant Forge | 90% | PC/Mobile variant plan、Unreal preset fact join、Unreal 5.3 runtime-vs-plan 检查、dry-run generation operation contract、material/texture runtime facts、public 2048 Texture2D payload budget proof、public fixture 受控执行和 rollback、LOD/Nanite/collision approval receipts、StaticMesh post-check | 复杂真实风格资产 fixture、LOD/Nanite 受控写入未做 |
| Groom Export Inspector | 92% | Maya `mayapy` L3 采集 root UV、strand ID、guide curve、Alembic payload、Unreal Groom/Binding intent；Unreal 5.3.2 L3 readiness 采集 AssetImportTask、AlembicImportFactory、target SkeletalMesh、Groom API 和期望 Groom/Binding 资产缺口；R52 Maya `AbcExport` 写出 approved curve-only public `.abc` cache，记录 bytes/hash/schemaCompatibleRows=1/meshShapeRows=0；R52 Unreal 读取 `.abc` 并验证 sha256 continuity、AssetImportTask dry-run、HairStrandsFactory/Alembic factory visibility、target `SK_HeroFace` 和 no-write boundary；R50 public Unreal fixture 已启用 HairStrands/Alembic hair stack 并证明 Groom import API ready；R52 controlled executor 已真实执行 `HairStrandsFactory` import，记录 imported class=`GroomAsset`、BindingAsset post-check=true、rollback clean、residual assets=0 | 可继续补更深 Groom runtime facts、更多 group/guide/root projection fixture |

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
   python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --export-presenter-pack r52-groom-hair-schema-executor-presentation-pack
   ```

仍需要人工或 GUI 自动化采集的内容：9 张 Maya GUI PNG 和 1 段 MP4，目标目录：

```text
<repo>\assets\dcc-first\r10-7-gui-evidence
```

## 6. 下一步建议

下一轮不要再围绕 Blender/Max readiness 或 Groom StaticMesh importer 打转，它们已进入真实 runtime 证据。`Unreal Animation Bridge` 已有 import L3 和 R41 deep facts；`Character Calibration Studio` 已有 Maya L3、R35 drilldown、R42 Control Rig fixture authoring、post-authoring bridge、R43 deformation link、R44 face skeleton fixture 和 R45 compile status bridge；`Groom Export Inspector` 已有 R46 Maya L3、R47 Unreal readiness L3、R52 curve-only Maya Alembic payload receipt、R52 Unreal import/post-check readiness、R50 plugin/API fixture 和 R52 controlled executor Ready rollback proof；`Spatial Authoring Workbench` 已有 Maya L3、R36 drilldown、R38 Unreal Socket Import Checker 和 R40 Socket Authoring Executor API-limited gate；`Platform Variant Forge` 已完成 L3-linked plan、Unreal runtime-vs-plan L3、dry-run generation plan、texture runtime collector、public Texture2D payload fixture、controlled executor、executor receipts 和 StaticMesh post-check。后续优先做 gameplay attach fixture、Houdini 非 Maya adapter 或 Control Rig Editor Utility / C++ diagnostic bridge。


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
