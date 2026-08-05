# Lightbox核心技术点覆盖与插件开发状态

更新时间：2026-08-05  
工程根目录：`<repo>`  
当前发布包：`ai-tool-ta-dcc-first-showcase-r38` / `dcc-first-package@1.35.0`

## 1. 当前结论

当前作品集已经不是纯前端展示。主入口是 Maya 2024 内的 AuroraView 面板，React/TypeScript 只是嵌入式工具界面；证据层由 Maya `mayapy`、Blender `bpy`、3ds Max `pymxs`、Unreal Python 和普通 Python fixture 共同生成。

R38 的硬证据：

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r39-platform-variant-staticmesh-postcheck-presentation-pack-20260805-215900.json`
- Unreal Control Rig Bridge：`<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-bridge-l3-20260805-205656.json`
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
- Presenter Pack 结果：36 / 36 evidence files present，0 missing required files，28 demo route steps。
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
| 动画确定性导出、Take、sub-frame、channel identity | `Animation Continuity Lab` 已通过 Maya `mayapy` 采集 keyed animCurve facts；`Unreal Animation Bridge` 已通过 Maya FBX + Unreal Python 导入真实 public AnimSequence/Skeleton facts | Maya L3 + Unreal import L3 | 可继续补 sequence length、sample rate、curve metadata、root motion、compression 细节 |
| 角色 DNA、拓扑、joint coverage、面部/肌肉参数迁移 | `Character Calibration Studio` 已通过 Maya `mayapy` 采集 topology / joint / calibration / face params / Control Rig mapping facts；R35 Drilldown 已把 flat rows 转成 topology/skeleton/skin/calibration/face/Control Rig/mirror panels 和 owner actions；R37 Unreal Control Rig Bridge 已把角色 mapping 接到 Unreal Control Rig API、SkeletalMesh/Skeleton binding 和 expected CR asset coverage | Maya L3 + L3-derived drilldown + Unreal L3 | 后续加 public CR asset fixture、runtime hierarchy、deformation target link |
| 空间热点、Socket、Pose Transfer、mirror、locator preview | `Spatial Authoring Workbench` 已通过 Maya `mayapy` 采集 joint / locator / socket / hotspot / pose frame / mirror / pose transfer facts；R36 Drilldown 已把 flat rows 转成 protocol/parent/socket/mirror/hotspot/pose frame/transform/preview/pose transfer panels 和 owner actions；R38 Unreal Socket Import Checker 已接到 Unreal SkeletalMesh/Skeleton socket API 和 expected socket coverage | Maya L3 + L3-derived drilldown + Unreal L3 | 后续加 socket creation / write+rollback fixture |
| PC -> Mobile 平台派生、LOD/材质/贴图/碰撞生成链 | `Platform Variant Forge` 已生成 PC/Mobile variant plan，用 Unreal runtime probe 对照 StaticMesh facts，把 drift 转成 dry-run generation operations，采集材质/贴图 runtime facts，导入 public Texture2D payload 验证预算，执行 public fixture max-size clamp / post-check / rollback，并把 LOD/Nanite/collision 后续动作转成 approval / rollback receipts | 已覆盖计划层 + Unreal L3 + L3-derived generation plan + texture runtime L3 + Texture2D payload L3 + controlled executor L3 + executor receipts L3-derived | 更复杂资产、StaticMesh LOD/Nanite runtime post-check |
| Groom/XGen 到 Unreal | 只有计划提炼 | 未开发 | 开发 `Groom Export Inspector` |

## 3. 计划中的插件线

| # | 插件/工具线 | 大白话说明 | 当前进度 |
| --- | --- | --- | --- |
| 1 | Maya AuroraView Host / Presenter Pack | 在 Maya 里打开作品集工具，并把所有证据打包给 reviewer | 已可运行；R38 Presenter Pack 35/35 evidence present；27 步 demo route；新增 Unreal Socket Import Checker probe |
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
| 13 | Unreal Animation Bridge | 把 Maya 动画连续性 facts 映射到 Unreal AnimSequence/Skeleton/root motion/curve/compression runtime facts | Unreal import L3 完成；2/2 sequences present，4 synthetic assets imported |
| 14 | Character Calibration & Intent Transfer Studio | 检查 DNA/拓扑/joint/面部参数/Unreal Control Rig 映射，避免“算法能跑但艺术表现错” | Maya `mayapy` L3 完成；R35 drilldown 完成；R37 Unreal Control Rig Bridge L3 完成，2 rows / 8 pass / 1 warning / 7 error / assetWrites=0 |
| 15 | Spatial Authoring & Pose Transfer Workbench | 用热点图、pose frame、locator preview 管 socket、挂点、pose copy、mirror | Maya `mayapy` L3 完成；R36 drilldown 完成；R38 Unreal Socket Import Checker L3 完成，2 rows / 9 pass / 2 warning / 9 error / expected-runtime sockets 4/0 / assetWrites=0 |
| 16 | Platform Variant Forge | 从 PC 资产派生 Mobile 资产，联动命名、LOD、材质、贴图、碰撞、预算 | R28 plan + R29 Unreal runtime + R30 generation plan + R31 texture runtime + R32 public Texture2D payload + R33 controlled executor + R34 executor receipts 完成：5 receipts，0 blocked，3 approval/rollback boundaries |
| 17 | Unreal Socket Import Checker | 把 Maya socket / hotspot / pose transfer facts 对照到 Unreal Skeleton / socket runtime facts | R38 完成；Unreal 5.3.2 L3，socket API ready，2 rows 全部按业务门禁 Blocked |
| 18 | Character LOD Bake Planner | 给角色部件规划 LOD、贴图烘焙、normal/tangent/vertex color payload | 计划阶段 |
| 19 | Groom Export Inspector | 检查 XGen/groom 到 Unreal 的 root UV、strand ID、guide curve、Alembic payload | 计划阶段 |

## 4. 当前开发进度

| 插件/工具线 | 完成度判断 | 能展示什么 | 不能展示什么 |
| --- | --- | --- | --- |
| Maya Host / Presenter Pack | 96% | Maya 内打开工具、外部 command bridge、27 步 demo route、35 个证据文件探测 | 9 张截图和 1 段录屏未采集 |
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
| Unreal Animation Bridge | 55% | Maya 生成 FBX、Unreal Python 导入 Skeleton/SkeletalMesh/AnimSequence、2/2 sequences present、Maya L3 source comparison | frame/sample-rate/curve/compression facts 还可继续深化 |
| Character Calibration Studio | 65% | Maya `mayapy` L3 采集 topology signature、joint coverage、calibration delta、face params、Control Rig mapping；R35 drilldown 输出 14 个 UI-ready panels、8 条 owner actions；R37 Unreal Control Rig Bridge 检查 API、SkeletalMesh/Skeleton binding、expected CR asset coverage | public CR asset fixture、runtime hierarchy、deformation target link 还可深化 |
| Spatial Authoring Workbench | 65% | Maya `mayapy` L3 采集 socket parent joint、offset、mirror pair、hotspot semantic/owner、pose frame、local space、preview locator、pose transfer approval；R36 drilldown 输出 18 个 UI-ready panels、9 条 owner actions；R38 Unreal Socket Import Checker 输出 SkeletalMesh/Skeleton socket API 和 expected socket coverage | 还缺 socket creation / write+rollback fixture 和复杂 gameplay attach fixture |
| Platform Variant Forge | 86% | PC/Mobile variant plan、Unreal preset fact join、Unreal 5.3 runtime-vs-plan 检查、dry-run generation operation contract、material/texture runtime facts、public 2048 Texture2D payload budget proof、public fixture 受控执行和 rollback、LOD/Nanite/collision approval receipts | 还缺 StaticMesh LOD/Nanite runtime post-check 和复杂真实风格资产 fixture |
| Character LOD Bake / Groom | 5-10% | 方法提炼和计划 | 还没有代码闭环 |

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
   python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --export-presenter-pack r39-platform-variant-staticmesh-postcheck-presentation-pack
   ```

仍需要人工或 GUI 自动化采集的内容：9 张 Maya GUI PNG 和 1 段 MP4，目标目录：

```text
<repo>\assets\dcc-first\r10-7-gui-evidence
```

## 6. 下一步建议

下一轮不要再围绕 Blender/Max readiness 或 Unreal missing fixture 打转，它们已进入真实 runtime 证据。`Character Calibration Studio` 已有 Maya L3、R35 drilldown 和 R37 Unreal Control Rig Bridge；`Spatial Authoring Workbench` 已有 Maya L3 和 R36 drilldown；`Platform Variant Forge` 已完成 L3-linked plan、Unreal runtime-vs-plan L3、dry-run generation plan、texture runtime collector、public Texture2D payload fixture、controlled executor 和 executor receipts；后续优先把 R37/R38 加深到 public Control Rig / socket asset authoring 的 write+rollback fixture，或把 R34 receipts 转成更细的 StaticMesh LOD/Nanite public runtime post-check。


## R39 补充

- Platform Variant StaticMesh Post-check：`<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-staticmesh-postcheck-20260805-215500.json`
- 结果：L3 / `Review` / `unreal_staticmesh_postcheck_collected`，5 receipts，2 runtime targets，2 no-op matched，3 owner-held，32 pass / 3 warning / 0 error，assetWrites=0，productionWrites=0。
