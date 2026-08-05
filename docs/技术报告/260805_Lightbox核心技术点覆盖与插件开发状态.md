# Lightbox核心技术点覆盖与插件开发状态

更新时间：2026-08-05  
工程根目录：`<repo>`  
当前发布包：`ai-tool-ta-dcc-first-showcase-r23` / `dcc-first-package@1.20.0`

## 1. 当前结论

当前作品集已经不是纯前端展示。主入口是 Maya 2024 内的 AuroraView 面板，React/TypeScript 只是嵌入式工具界面；证据层由 Maya `mayapy`、Blender `bpy`、3ds Max `pymxs`、Unreal Python 和普通 Python fixture 共同生成。

R23 的硬证据：

- Presenter Pack：`<repo>\dcc-hosts\maya-auroraview-host\artifacts\r23-animation-continuity-l3-presentation-pack-20260805-163040.json`
- Animation Continuity L3：`<repo>\dcc-hosts\animation-continuity-lab\artifacts\animation-continuity-maya-l3-20260805-162744.json`
- Blender L3：`<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json`
- 3ds Max L3：`<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260805-153232.json`
- Presenter Pack 结果：20 / 20 evidence files present，0 missing required files，13 demo route steps。
- Gate 仍是 `CapturePending`，原因只剩 Maya GUI 截图/录屏未采集；Animation/Blender/Max 的 `Blocked` 是 synthetic fixture 中故意放入的失败资产，不是 runtime 缺失。

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
| 动画确定性导出、Take、sub-frame、channel identity | `Animation Continuity Lab` 已通过 Maya `mayapy` 采集 keyed animCurve facts，检查 rig identity、skeleton fingerprint、sample rate、required channel、sub-frame、root motion、active layer | Maya L3 首版 | 扩 MotionBuilder take/story/character mapping 和 Unreal AnimSequence runtime 对照 |
| 角色 DNA、拓扑、joint coverage、面部/肌肉参数迁移 | 已有 topology signature、joint coverage、calibration delta fixture | L2 | 开发 `Character Calibration & Intent Transfer Studio` |
| 空间热点、Socket、Pose Transfer、mirror、locator preview | 已有 spatial authoring fixture | L2 | 开发 `Spatial Authoring & Pose Transfer Workbench` |
| PC -> Mobile 平台派生、LOD/材质/贴图/碰撞生成链 | 当前有规则检查和 engine preset comparison | 局部覆盖 | 开发 `Platform Variant Forge` 或 `LOD Bake Planner` |
| Groom/XGen 到 Unreal | 只有计划提炼 | 未开发 | 开发 `Groom Export Inspector` |

## 3. 计划中的插件线

| # | 插件/工具线 | 大白话说明 | 当前进度 |
| --- | --- | --- | --- |
| 1 | Maya AuroraView Host / Presenter Pack | 在 Maya 里打开作品集工具，并把所有证据打包给 reviewer | 已可运行；R23 Presenter Pack 20/20 evidence present；13 步 demo route；新增 command bridge |
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
| 12 | Animation Continuity Lab | 检查 Maya/MotionBuilder/Unreal 动画传递中的角色身份、Take、时间、通道和曲线差异 | Maya `mayapy` L3 首版完成；MotionBuilder/Unreal 对照未做 |
| 13 | Character Calibration & Intent Transfer Studio | 检查 DNA/拓扑/joint/面部参数/Unreal Control Rig 映射，避免“算法能跑但艺术表现错” | 协议和 headless fixture 完成，插件未开发 |
| 14 | Spatial Authoring & Pose Transfer Workbench | 用热点图、pose frame、locator preview 管 socket、挂点、pose copy、mirror | 协议和 headless fixture 完成，插件未开发 |
| 15 | Platform Variant Forge | 从 PC 资产派生 Mobile 资产，联动命名、LOD、材质、贴图、碰撞、预算 | 只有规则/预检覆盖，生成链未开发 |
| 16 | Character LOD Bake Planner | 给角色部件规划 LOD、贴图烘焙、normal/tangent/vertex color payload | 计划阶段 |
| 17 | Groom Export Inspector | 检查 XGen/groom 到 Unreal 的 root UV、strand ID、guide curve、Alembic payload | 计划阶段 |

## 4. 当前开发进度

| 插件/工具线 | 完成度判断 | 能展示什么 | 不能展示什么 |
| --- | --- | --- | --- |
| Maya Host / Presenter Pack | 88% | Maya 内打开工具、外部 command bridge、13 步 demo route、20 个证据文件探测 | 9 张截图和 1 段录屏未采集 |
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
| Character Calibration Studio | 15% | topology signature、joint coverage、位移阈值 fixture | 没有 Maya mesh/DNA runtime，没有可视化工作台 |
| Spatial Authoring Workbench | 15% | hotspot、pose frame、transform contract fixture | 没有 Maya 热点 UI、locator preview、pose transfer 执行 |
| Platform Variant / LOD Bake / Groom | 5-10% | 方法提炼和计划 | 还没有代码闭环 |

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
   python <repo>\dcc-hosts\maya-auroraview-host\scripts\send_maya_command.py --export-presenter-pack r23-animation-continuity-l3-presentation-pack
   ```

仍需要人工或 GUI 自动化采集的内容：9 张 Maya GUI PNG 和 1 段 MP4，目标目录：

```text
<repo>\assets\dcc-first\r10-7-gui-evidence
```

## 6. 下一步建议

下一轮不要再围绕 Blender/Max readiness 打转，它们已升到 runtime L3。`Animation Continuity Lab` 的 Maya L3 首版已经闭环，下一轮优先做 MotionBuilder / Unreal Animation Bridge：把 Maya 采集到的 rig、take、channel、root motion 事实和 MotionBuilder/Unreal 侧 runtime facts 对齐。它最能体现工具管线 TA 对“业务正确性”的理解，而不是只做资产静态检查。
