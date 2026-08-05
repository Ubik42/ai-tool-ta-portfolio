# Lightbox 中高价值扩展线与复杂工具计划

## 一.当前结论

还没有把本地所有 Lightbox 仓库逐函数看完。上一轮深读覆盖的是最高价值、最适合立刻转成作品集 demo 的 Maya 线：车辆语义编码、socket pose、动画导出、pose copy、命名材质同步、Pyblish 资产协议。

这轮放宽阈值后，新增看到的中高价值内容更多，尤其集中在：

- CGM 工业化角色 / 场景资产制作链。
- CDV 武器视觉回归和动画工具。
- Blender / 3ds Max / Houdini / Unreal 的跨 DCC Pyblish。
- Photoshop / Substance Painter / SpriteSheet 的贴图交付链。
- Figma / AM / pipeline task platform 的任务平台集成。

这些内容适合把作品集从 4 个单点 demo 升级成一个复杂产品：`AI Production Asset Command Center`。

```text
任务平台 -> 资产协议 -> DCC 规则矩阵 -> LOD/材质/贴图处理 -> 视觉评审 -> 导出报告
```

## 二.新增中高价值线

### 1. CGM 工业化资产工作台

代表来源：

- `maya_asset_tool_reference`
- `asset_protocol_editor_reference`
- `lod_texture_bake_reference`
- `speed_poly`
- `autouv`
- `tangent_save`
- `save_vertex_normal_info`
- `lod_wrap_updater`
- `weapon_checker_toolkit`
- `role_model_bake`
- `role_hunyuan_export`

核心价值：

这不是一堆 Maya 小按钮，而是一套资产状态机。`asset_protocol_editor_reference` 给模型写入大量 `CG_Tag_*` 自定义属性，把平台、LOD、材质、贴图、碰撞、Nanite、streamable、asset platform 元数据、screen size、cull distance、stage 等信息写回 Maya 节点。后面的检查、导出、平台分叉都依赖这些资产内标签。

最值得学习的做法：

- 把“资产是什么”写进资产节点，不只写在外部表格。
- PC / mobile / Nanite / HLOD / collision / streamable 是同一个资产协议的不同维度。
- 资产编辑器不只是 UI，它是数据协议编辑器。
- LOD、贴图、材质、碰撞、平台预算要放在同一个工作台里联动。

可做作品集：

`AI Asset Protocol Workbench`

- 合成一个资产包：mesh、LOD、materials、textures、collision、platform budgets。
- UI 展示资产协议标签表。
- AI 从需求描述生成标签建议，例如“移动端远景可 streamable，LOD3 去透明材质，PC 保留 Nanite”。
- 确定性规则检查标签冲突：Nanite 与移动端 LOD、collision preset、材质数量、贴图密度、screen size。
- 输出 sidecar JSON 和 QA 报告。

### 2. 角色 LOD / 贴图烘焙 / 形变同步链

代表来源：

- `lod_texture_bake_reference`
- `metahuman_head`
- `role_model_bake`
- `lod_wrap_updater`
- `tangent_save`
- `save_vertex_normal_info`

核心价值：

这条线把角色资产的几件难事连起来：Metahuman DNA 生成 LOD、属性传递、LOD4 贴图烘焙、basecolor / normal 合并、Wrap + BlendShape 同步 LOD 形变、切线存到 3U 和顶点色、锁定法线记录到自定义属性。

最值得学习的做法：

- LOD 不是单独减面，而是几何、UV、贴图、法线、材质、平台预算的联动结果。
- 一些渲染必需数据可以被编码到 UV 和 vertex color。
- 形变同步要考虑 Maya 惰性求值，必要时用 bounding box 触发计算后再 bake history。
- 烘焙流程要明确 source mesh、target mesh、texture part、resolution、quality、merge 输出。

可做作品集：

`AI Character LOD Bake Planner`

- 用合成角色部件：head / teeth / eyes / hair。
- 生成 LOD 计划：LOD2 / LOD3 / LOD4 目标、面数预算、贴图输出、烘焙通道。
- 可视化 texture bake queue 和 part merge。
- 展示 tangent / normal / vertex color payload。
- AI 负责生成 LOD/bake 计划和风险解释；具体 bake graph 和 payload 由确定性逻辑生成。

### 3. 武器视觉回归与评审自动化

代表来源：

- `maya_visual_review_reference/shelf/tools/visual_compare_reference`
- `camera_capture.py`
- `batch_runner.py`
- `report_html.py`
- `wecom_notify.py`

核心价值：

这个工具不是简单截图。它把武器 A/B 对比变成批量视觉评审流程：自动找或创建 basic/detail 相机，多预设材质显示，LOD0 / DT / solo 多组合截图，按 camera + LOD + kind 命名，导出场景备份，生成报告，并能通知。

最值得学习的做法：

- 视觉评审要固定相机、固定材质、固定命名和固定输出结构，否则对比没有意义。
- 多 preset 截图比单视角截图更能定位问题：红蓝透明叠加、白蓝材质、solo B、LOD / DT 分开。
- 工具要保护用户现场，保存和恢复 model panel 状态。
- 批处理必须把失败原因写进结果，而不是静默跳过。

可做作品集：

`AI Visual Review Studio`

- 输入 baseline / variant 的合成模型或渲染图。
- 生成固定相机序列和多种 review pass。
- 输出差异热力图、截图表、HTML report。
- AI 总结“可能的差异原因”：轮廓偏移、LOD 版本混乱、材质错配、少件、多件。
- 结果可作为任务评审附件。

### 4. Cross-DCC Rule Matrix

代表来源：

- `blender_rule_adapter_reference`
- `blender_rule_adapter_reference`
- `max_rule_adapter_reference`
- `max_scene_rule_reference`
- `houdini_rule_adapter_reference`
- `mpj_unreal_pyblish_plugins`

核心价值：

不同 DCC 在做同一类资产协议：单位、up axis、LOD group、UV 数量、UV overlap、UV utilization、texel density、材质数量、碰撞体、开放边、非流形、面数预算、导出层级。差别在于 API 和数据模型，不在于业务规则本身。

最值得学习的做法：

- 规则要拆成“业务语义”和“DCC adapter”两层。
- 同一条规则可以有 Maya / Blender / Max / Houdini 的不同采集实现。
- 配置决定哪些规则启用，规则输出要统一成 error / warning / info。
- 选中错误对象、导出报告、自动修复是 Pyblish 工具的关键体验。

可做作品集：

`Cross-DCC Rule Matrix`

- 设计统一 rule DSL：`rule_id`, `target`, `severity`, `dcc_adapters`, `fixability`。
- 用合成场景 JSON 模拟 Maya / Blender / Max / Houdini 的不同数据。
- 同一 UI 展示不同 DCC 下的规则覆盖、缺口和结果。
- AI 根据规则说明生成 adapter TODO 和风险评估。
- 输出“项目资产协议覆盖矩阵”。

### 5. 贴图 / 材质交付链

代表来源：

- `texture_to_engine_reference`
- `substance_delivery_reference`
- `substance_shader_reference`
- `photoshop_dds_reference`
- `photoshop_tool_reference`
- `spritesheet_reference`
- `badge_pattern_generator`

核心价值：

这里的重点是把贴图从 DCC/绘制工具变成引擎可消费资产：Substance Painter export preset、通道打包、FFMTable 输出、同步 UE texture asset、Photoshop DDS 转换、nvcompress 参数、SpriteSheet 合并 / 拆分 / 智能精简、SP 自定义 shader 和 HDR lookdev。

最值得学习的做法：

- 贴图工具不是“转换格式”，而是保证通道、命名、压缩、mipmap、预览环境和引擎导入一致。
- 长任务必须有 worker、progress、log、取消和失败原因。
- 与 Photoshop / Substance / Unreal 通信时，要处理已有进程、远程执行、临时文件、路径和异步状态。
- SpriteSheet 的“智能合并”已经出现了视觉特征比较思路，可以扩展成 AI 辅助图像归并。

可做作品集：

`AI Texture Delivery Console`

- 支持合成贴图输入：D / N / MRA / E / alpha。
- 规则化通道打包和命名。
- 模拟 DDS / SpriteSheet / UE import 输出。
- 显示压缩参数、mipmap、目标平台、失败原因。
- AI 解释贴图命名问题、通道错配和导入风险。

### 6. 平台任务中枢与 Figma 工具平台

代表来源：

- `task_intake_reference`
- `task_manager_backend_reference`
- `asset_platform_sync_reference`
- `tool_shelf_reference`
- `tool_discovery_server_reference`
- `common_figma_shelf_config`

核心价值：

这条线说明工具不只在 DCC 内部。真实生产需要把 AM / production tracker / task tracker / asset platform / pipeline task platform / Figma 工具入口连起来。`tool_discovery_server_reference` 的插件发现、本地端口文件、WebSocket、REST API、SQLite 持久化、插件 entry point 自动注册，都是“工具平台化”的经验。

最值得学习的做法：

- 工具入口需要可发现、可配置、可热更新、可统计。
- 任务不是 UI 列表，背后要接平台 adapter、凭证、状态同步、附件 / 交付物、发布动作。
- 前端插件和本地 FastAPI 后端的边界要清楚：Figma 负责交互，本地服务负责平台 API、文件和敏感凭证。
- shelves 配置是产品目录，不是简单 launcher。

可做作品集：

`AI Production Task Orchestrator`

- 合成一批任务：需求、资产类型、负责人、状态、交付物、检查结果。
- 支持任务 -> 资产包 -> QC -> review -> publish 的状态流。
- AI 生成任务摘要、风险提醒、下一步动作。
- 后端用本地 API 模拟平台 adapter。
- 前端展示 task board、deliverables、QC badges、review report。

### 7. 头发 / Groom / Lookdev 导出

代表来源：

- `maya_visual_review_reference/shelf/tools/xgen2ue`
- `texture_to_engine_reference`
- `substance_shader_reference`

核心价值：

XGen 到 Unreal 的链路会处理 description、guide curve、root UV、ID attr、Alembic export；SP lookdev 负责 HDR 环境和材质预览一致性。它代表“非标准 mesh 资产”的交付方法。

最值得学习的做法：

- groom 资产要额外生成 root UV、ID、guide curve 和 Alembic payload。
- 预览环境要固定，否则美术判断不稳定。
- 导出过程需要把 DCC 特有数据转成引擎认识的字段。

可做作品集：

`Groom Export Inspector`

- 合成发束曲线数据。
- 展示 root UV、strand ID、guide curve、cache path。
- 检查缺失属性和导出风险。
- AI 解释 groom 导出失败原因。

## 三.复杂作品集总产品

建议把后续作品集主工程升级为：

```text
AI Production Asset Command Center
```

它不是单个工具，而是一个可展示的生产工具平台，包含 6 个模块：

| 模块 | 对应 Lightbox 经验 | 展示能力 |
|---|---|---|
| Task Orchestrator | Figma AM / pipeline task platform / asset platform | 任务、状态、交付物、平台 adapter |
| Asset Protocol Workbench | CGM AssetEditor / Raid tags_config | 资产标签、平台预算、LOD、碰撞、材质协议 |
| Cross-DCC Rule Matrix | Blender / Max / Houdini / Maya Pyblish | 统一规则 DSL + DCC adapter |
| LOD Bake Planner | CGM LOD / bake / tangent / normal 工具 | LOD 计划、贴图烘焙、payload 编码 |
| Visual Review Studio | CDV Weapon Compare | 固定相机、多 pass 截图、diff report |
| Texture Delivery Console | SP2UE / Img2DDS / SpriteSheet | 通道打包、压缩、SpriteSheet、UE import |

## 四.开发计划

### P0.扩展 case card

目标：把新增中高价值线变成可执行设计卡。

交付：

- `docs/case-studies/ai-asset-protocol-workbench.md`
- `docs/case-studies/ai-visual-review-studio.md`
- `docs/case-studies/cross-dcc-rule-matrix.md`
- `docs/case-studies/ai-texture-delivery-console.md`
- `docs/case-studies/ai-production-task-orchestrator.md`

完成标准：

- 每张 card 有：业务问题、Lightbox 方法源、核心数据、AI 进入点、确定性边界、demo 证据计划。

### P1.搭建统一作品集站点

目标：创建 `showcases/portfolio-site`，先做复杂产品的信息架构。

页面：

- Overview：展示总产品定位。
- Method Map：Lightbox 方法源到 demo 模块的映射。
- Module Matrix：6 个模块状态。
- Case Detail：每个模块的业务问题和核心逻辑。

完成标准：

- 本地可运行。
- 首页能清楚表达“我做的是生产资产工具平台，不是单点 AI 小玩具”。

### P2.Asset Protocol Workbench

优先级最高。

原因：

- 它连接了上一轮的 Asset Semantic Codec、Raid tags_config、CGM AssetEditor。
- 它是后续 QC、LOD、Texture、Review 的数据底座。

功能：

- 合成资产包编辑器。
- `CG_Tag_*` 风格字段：platform、lod_count、nanite、collision、material、texture、streamable、screen_size、cull_distance。
- 冲突检查：平台与 LOD、Nanite 与 mobile、collision preset、材质数量、贴图密度。
- AI schema assistant：从自然语言需求生成资产协议建议。
- sidecar JSON 导出。

完成标准：

- 一个资产包能从“未标注”变成“可检查 / 可导出”。
- 有 before / after JSON diff。

### P3.Cross-DCC Rule Matrix

功能：

- 规则 DSL。
- DCC adapter mock：Maya / Blender / Max / Houdini。
- 规则覆盖：unit、up axis、LOD group、UV number、UV overlap、UV utilization、texel density、collision、material count。
- 结果统一为 error / warning / info。
- AI 解释某条规则如何移植到另一个 DCC。

完成标准：

- 至少 20 条规则。
- 至少 4 个 DCC adapter mock。
- 一张覆盖矩阵和一份检查报告。

### P4.Visual Review Studio

功能：

- baseline / variant 资产对比。
- 固定相机组：basic / detail。
- review pass：red-blue overlay、white-blue material、solo variant、LOD / detail split。
- HTML report。
- AI 总结差异和可能原因。

完成标准：

- 能用合成图片或简单 3D 数据生成评审报告。
- 有截图墙、差异说明、失败原因。

### P5.Texture Delivery Console

功能：

- 贴图输入：D / N / MRA / E / alpha。
- 通道打包规则。
- DDS / SpriteSheet / UE import mock。
- 长任务状态：queue、progress、log、error。
- AI 解释命名、通道和压缩风险。

完成标准：

- 一组贴图能产出打包计划、输出文件清单、导入报告。
- 有失败样例，例如缺 normal、MRA 通道错位、命名冲突。

### P6.LOD Bake Planner

功能：

- LOD 目标规划。
- 部件级 bake queue。
- texture merge 输出。
- tangent / vertex color payload 可视化。
- wrap / blendShape 形变同步流程图。

完成标准：

- 能从角色合成数据生成 LOD2-LOD4 计划。
- 能解释每个 LOD 为什么这样降级。

### P7.Task Orchestrator

功能：

- 任务看板。
- 资产包绑定任务。
- QC / review / texture / export 状态汇总。
- 交付物列表。
- AI 生成每日风险、待办、交付说明。

完成标准：

- 一个任务能走完：需求 -> 资产协议 -> QC -> 视觉评审 -> 贴图交付 -> 发布报告。

## 五.实现策略

技术建议：

- 前端：React / Vite / TypeScript。
- 数据：本地 JSON fixture，不依赖内部服务。
- AI 能力：先做 mock assistant 和 prompt templates；后续再接真实 API。
- 规则引擎：TypeScript 实现，规则 DSL 和 adapter 分离。
- 可视化：先用 2D / 表格 / SVG / canvas；需要 3D 再引入 Three.js。
- 报告：HTML + JSON 双输出。

目录建议：

```text
showcases/portfolio-site/
├── src/
│   ├── modules/
│   │   ├── task-orchestrator/
│   │   ├── asset-protocol/
│   │   ├── rule-matrix/
│   │   ├── visual-review/
│   │   ├── texture-delivery/
│   │   └── lod-bake-planner/
│   ├── rules/
│   ├── fixtures/
│   └── reports/
└── README.md
```

## 六.优先级

推荐顺序：

1. `Asset Protocol Workbench`
2. `Cross-DCC Rule Matrix`
3. `Visual Review Studio`
4. `Texture Delivery Console`
5. `LOD Bake Planner`
6. `Task Orchestrator`

理由：

- 资产协议是底座。
- 规则矩阵最能体现 TA 工程能力。
- 视觉评审最容易形成展示冲击。
- 贴图和 LOD 是复杂度扩展。
- 任务中枢最后做，避免先搭平台壳子。

## 七.边界

- 使用合成数据，不使用公司资产、内部路径、内部服务真实数据。
- 可以提炼方法，不复制业务敏感配置。
- AI 负责解释、建议、schema 草案和报告总结。
- 真正修改数据、生成导出清单、判定规则结果必须由确定性代码完成。

