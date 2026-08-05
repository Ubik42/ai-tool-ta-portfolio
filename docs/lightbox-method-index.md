# Lightbox 方法索引

这份索引用来把 Lightbox 高价值插件里的业务秘诀，转成作品集 demo 的设计原则。它不是源码摘抄，而是可迁移的 TA 方法库。

## 1. 业务语义要进入资产数据

来源：`og2_vehicle_light_tools`

核心方法：

- 互斥分类用离散值。
- 可叠加状态用 bitmask。
- 优先使用下游能保留的数据通道：UV、vertex color、custom attr、sets、anim keys。
- UI 只做写入和反查，事实源保存在资产数据里。

作品集落点：

- `Asset Semantic Codec`
- 展示“业务标签 -> 数据通道编码 -> 反向解析 -> 引擎可消费 payload”。

## 2. 不让用户直接维护最终交付格式

来源：`og2_vehicle_socket_manager`

核心方法：

- 用户在熟悉的 DCC authoring 环境里工作。
- 工具用模板文件降低新资产接入成本。
- 状态 UI 暴露缺失数据。
- 最终由工具把 DCC pose / frame / namespace 翻译成 JSON。

作品集落点：

- `Socket Pose Authoring` 可作为后续 demo。
- 当前并入 `Animation Export Stabilizer` 的 pose 子页。

## 3. 导出工具的核心是确定性

来源：`jk_anim_fbx_exporter`, `maya_pose_force_copy`

核心方法：

- 不相信“当前看起来对”，要把最终值 bake 成稳定数据。
- 对 constraint / IK / jointOrient / animation layer 这类不确定来源逐帧求值。
- 导出前清理 namespace、root、帧范围、无关节点。
- 复杂场景用临时场景或隔离进程，避免顺序污染。
- pose 工具围绕 world matrix 和最终可见结果建模，而不是只复制局部 channel 值。

作品集落点：

- `Animation Export Stabilizer`
- 展示 direct export vs stabilized export 的 before / after diff。

## 4. 规范要从文档变成 schema 和执行器

来源：`maya_naming_material_reference`

核心方法：

- 命名规范配置化。
- 名字既要能生成，也要能反向解析。
- 执行前必须 preview / diff。
- 材质和贴图连接使用稳定技术 ID，展示名只负责 UI。
- 只有输入齐全时才执行会污染场景的操作。

作品集落点：

- `Naming & Material Sync`
- 展示自然语言规范 -> schema -> rename preview -> material / texture sync。

## 5. 资产检查是协议，不是脚本集合

来源：`maya_publish_rule_reference`, `maya_rule_adapter_reference`

核心方法：

- 先 collect 结构化 context，再让多个 validate / fix / extract 复用。
- error / warning / info 分层，避免把所有问题都阻断。
- 自动修复只做确定性强的动作。
- 需要美术或 TA 判断的问题，用 warning、select、解释和证据定位。
- extract 阶段把 sidecar JSON、贴图、FBX 等交付物整理成可消费包。

作品集落点：

- `Pyblish Rulebench`
- 展示轻量 Collect / Validate / Fix / Extract 和 AI 解释层。

## 6. 从稳定命名和目录推导批量操作

来源：`maya_rule_adapter_reference`

核心方法：

- 命名、材质关键词、LOD 层级、贴图目录是可计算的业务信号。
- 先把信号收敛成 context，再推导 UV tile、LOD 材质、贴图变体、法线修复。
- 自动修复必须有清晰配对规则，例如 Head / Body 接缝、LOD0 / LOD1 / LOD2 序列。

作品集落点：

- `Pyblish Rulebench` 的 LOD / UV / normal 规则组。
- 后续可独立拆成 `LOD & Normal QC Lab`。

## 7. 资产协议是工作台底座

来源：`maya_asset_tool_reference/asset_protocol_editor_reference`

核心方法：

- 用自定义属性把平台、LOD、材质、贴图、碰撞、Nanite、streamable、screen size、cull distance、asset platform 元数据写回资产节点。
- 资产编辑器不是表单，而是资产状态机的编辑器。
- PC / mobile / Nanite / HLOD / collision / LOD 是同一个协议的不同维度。

作品集落点：

- `AI Asset Protocol Workbench`
- 作为后续 QC、LOD、Texture、Review 的数据底座。

## 8. 视觉评审要固定视角和 pass

来源：`maya_visual_review_reference/shelf/tools/visual_compare_reference`

核心方法：

- 固定相机组、固定材质预设、固定输出命名。
- 同时输出 red-blue overlay、white-blue material、solo variant、LOD / detail 拆分。
- 批处理要记录失败原因，导出报告和场景备份。
- 评审工具要保存并恢复用户 viewport 状态。

作品集落点：

- `AI Visual Review Studio`
- 展示 baseline / variant 的多视角、多 pass 视觉回归。

## 9. LOD 是几何、贴图、法线和平台预算联动

来源：`maya_asset_tool_reference/lod_texture_bake_reference`, `lod_wrap_updater`, `tangent_save`, `save_vertex_normal_info`

核心方法：

- LOD 生成要同时考虑 mesh part、UV、贴图烘焙、材质、法线和平台预算。
- 可渲染 payload 可以写入 UV 和 vertex color。
- 形变同步要触发 DCC 求值，再决定是否 bake history。
- 贴图烘焙要明确 source mesh、target mesh、part、resolution、quality 和 merge 输出。

作品集落点：

- `AI Character LOD Bake Planner`
- 展示从 LOD 计划到 bake queue 和 payload 编码。

## 10. 同一业务规则要拆成 rule 和 DCC adapter

来源：`blender_rule_adapter_reference`, `max_rule_adapter_reference`, `max_scene_rule_reference`, `houdini_rule_adapter_reference`

核心方法：

- unit、up axis、LOD、UV、材质、碰撞、texel density 是业务规则。
- Maya / Blender / Max / Houdini 只是采集和修复方式不同。
- 规则启用、severity、fixability 和 selection action 要配置化。

作品集落点：

- `Cross-DCC Rule Matrix`
- 展示统一规则 DSL 与多 DCC adapter mock。

## 11. 贴图交付是通道、压缩、预览和引擎同步

来源：`texture_to_engine_reference`, `photoshop_dds_reference`, `spritesheet_reference`, `substance_shader_reference`

核心方法：

- 贴图工具要控制命名、通道打包、压缩参数、mipmap、预览环境和引擎导入。
- 长任务要有 worker、progress、log、取消和失败原因。
- 与 Photoshop / Substance / Unreal 通信要处理进程、远程执行、临时文件和路径。

作品集落点：

- `AI Texture Delivery Console`
- 展示通道打包、DDS/SpriteSheet/UE import mock 和 AI 风险解释。

## 12. 工具平台要能发现、注册、热更新和统计

来源：`tool_shelf_reference`, `tool_discovery_server_reference`, `task_intake_reference`, `task_manager_backend_reference`

核心方法：

- 工具入口用 shelf 配置表达产品目录。
- 本地服务负责插件发现、端口文件、WebSocket、REST API、持久化和上报。
- 平台任务要通过 adapter 接 AM / task tracker / production tracker / asset platform 等系统。
- 前端插件与本地后端边界清楚：交互在前端，凭证、文件和平台 API 在后端。

作品集落点：

- `AI Production Task Orchestrator`
- 展示任务、资产包、QC、review、publish 的状态流。

## 作品集筛选原则

选择 demo 时优先满足：

1. 能体现真实业务痛点。
2. 有明确数据模型，而不是纯 UI。
3. 能用公开合成数据复现。
4. AI 的作用是增强规则生产、解释和诊断，不破坏确定性执行。
5. 最终能产出截图、视频、数据 diff 或报告。


