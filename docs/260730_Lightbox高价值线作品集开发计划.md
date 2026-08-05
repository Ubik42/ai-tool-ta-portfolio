# Lightbox 高价值线作品集开发计划

## 一.定位

这个作品集不展示 Lightbox 外层工程框架，也不展示公司源码。它要展示的是：我能从真实 DCC/游戏资产生产插件里抽出核心业务模型，再把它重制成可运行、可解释、可验证的 AI 工具。

作品集主题：

```text
真实行业插件经验 -> 业务规则抽象 -> AI 辅助工具设计 -> 可运行 demo -> TA 方法沉淀
```

材料来源优先级：

| 来源线 | 代表工程 | 可迁移价值 |
|---|---|---|
| 资产语义编码 | `og2_vehicle_light_tools` | 用 UV / vertex color / custom attr 这类下游稳定通道承载业务语义 |
| Socket / Pose 作者工具 | `og2_vehicle_socket_manager` | 把引擎 socket JSON 生产转成 Maya pose / template authoring |
| 动画确定性导出 | `jk_anim_fbx_exporter`, `maya_pose_force_copy` | 强制求值、bake、清理 namespace/root，把 DCC 不确定状态压平成稳定数据 |
| 命名 / 材质 / 贴图同步 | `maya_naming_material_reference` | 把命名规范变成配置、解析器、预览、Maya graph 和文件操作 |
| 资产协议检查 | `maya_publish_rule_reference`, `maya_rule_adapter_reference` | 用 Collect / Validate / Fix / Extract 把项目规范变成门禁、修复和导出 |
| LOD / UV / 法线规则库 | `maya_rule_adapter_reference` 及后续 CGM 线 | 从命名、材质、目录、LOD 层级推导批量操作和 QC 修复 |

## 二.作品集主线

作品集首屏要让人立刻看到：这不是普通 AI chatbot，而是“AI + TA 业务规则引擎 + DCC 资产数据”的工具能力。

推荐主标题：

```text
AI Tool TA Portfolio: turning DCC production rules into runnable tools
```

首屏展示 4 个核心 demo：

1. Asset Semantic Codec
2. Naming & Material Sync
3. Pyblish Rulebench
4. Animation Export Stabilizer

每个 demo 都必须回答五件事：

| 问题 | 要展示的内容 |
|---|---|
| 业务痛点是什么 | 美术 / TA / 引擎之间哪个交付问题反复出错 |
| 传统插件怎么解决 | 对应 Lightbox 高价值线的核心做法 |
| 我重制了什么 | 使用合成数据和公开 demo 复现业务模型 |
| AI 进入哪里 | AI 做规则解释、配置生成、问题诊断、修复顺序建议，不能替代确定性核心逻辑 |
| TA 能力体现在哪里 | 数据通道选择、规则建模、导出确定性、修复边界、交付证据 |

## 三.核心 demo 设计

### 1. Asset Semantic Codec

灵感来源：`og2_vehicle_light_tools`

要展示的惊艳点：业务语义不一定要放在外挂 JSON 里，能被 FBX/引擎天然保留的数据通道更稳。互斥分类用离散值，可叠加状态用 bitmask。

重制 demo：

- 用一个浏览器 3D 网格或简化面片编辑器模拟“车辆灯光 / 玻璃 / 材质区域标注”。
- 用户选择面片，给它打上 `brake_light`、`head_light`、`glass_red`、`paint_metal` 等业务标签。
- 工具实时把标签编码成 UV3-like 数据：U 轴承载互斥分类，V 轴承载 bitmask 状态。
- 展示编码表、面片热力图、反向解析结果和导出 JSON。
- AI 负责根据业务描述生成编码 schema，并解释为什么某个标签应该是互斥分类或叠加状态。

交付物：

- `showcases/portfolio-site` 中的可交互页面。
- `docs/case-studies/asset-semantic-codec.md`
- 一张“业务语义 -> 数据通道 -> 引擎消费”的流程图。

TA 能力关键词：数据协议设计、bitmask、UV / vertex color 语义承载、资产内事实源。

### 2. Naming & Material Sync

灵感来源：`maya_naming_material_reference`

要展示的惊艳点：命名规范不能只停在文档里。高质量工具要能配置规则、生成名称、反向解析旧资产、同步材质 / 贴图 / Shader 参数，并在操作前给用户预览。

重制 demo：

- 输入一组模型、材质、贴图文件名和规则 schema。
- 工具生成 `SM_...`、`MI_...`、`T_..._D/NRA/MHO/E` 这类规范名。
- 支持从旧模型名反向解析字段，提示缺失字段和冲突。
- 模拟 shader slot 连接：用稳定技术 ID 连接贴图，而不是依赖 UI 展示名。
- AI 负责读取规则文档，生成 schema 草案，解释不合规命名，并给出批量重命名计划。

交付物：

- 规则编辑器 + 批量预览表 + 修改 diff。
- `docs/case-studies/naming-material-sync.md`
- 一份合成资产 fixture。

TA 能力关键词：规范配置化、反向解析、批量 diff、材质图同步、确定性执行。

### 3. Pyblish Rulebench

灵感来源：`maya_publish_rule_reference`, `maya_rule_adapter_reference`

要展示的惊艳点：检查系统的价值不是报错，而是把资产协议变成 Collect / Validate / Fix / Extract 的生产流程。error / warning / info 要区分，可自动修复和需要人判断的规则要分边界。

重制 demo：

- 用 JSON fixture 模拟一组资产：mesh、material、texture、LOD、collision、tags_config、UV density。
- 实现一个轻量规则引擎：
  - Collect：生成结构化 context。
  - Validate：运行命名、LOD、碰撞体、贴图密度、材质 ID 等规则。
  - Fix：只修确定性问题，例如补字段、规范后缀、清理空节点、移动 UV tile。
  - Extract：导出结果 JSON 和报告。
- UI 展示检查列表、严重级别、受影响对象、修复按钮和导出包。
- AI 负责把检查结果翻译成人话，给出修复优先级，并解释哪些问题不能自动修。

交付物：

- 可运行 rulebench 页面。
- `docs/case-studies/pyblish-rulebench.md`
- 一张 Collect / Validate / Fix / Extract 执行图。

TA 能力关键词：资产协议、规则引擎、可解释 QC、修复边界、发布门禁。

### 4. Animation Export Stabilizer

灵感来源：`jk_anim_fbx_exporter`, `maya_pose_force_copy`

要展示的惊艳点：动画导出的核心不是调用 FBXExport，而是把 Maya 当前看起来正确的状态，变成引擎里稳定正确的数据。

重制 demo：

- 用简化的骨骼 / 曲线数据模拟 reference、namespace、动画层、constraint-driven joint、jointOrient、帧范围和 root。
- 展示“直接导出”和“稳定化导出”的差异：
  - merge layers
  - frame-by-frame evaluate
  - bake final rotate
  - normalize root / namespace
  - shift frame range
  - export clean payload
- 加一个 pose copy 子页：展示 world matrix 快照、local transform 回写、依赖顺序和镜像。
- AI 负责诊断导出异常来源，例如“constraint 驱动旋转没有被 bake 成真实 keys”。

交付物：

- 动画曲线 / 骨骼状态可视化页面。
- `docs/case-studies/animation-export-stabilizer.md`
- before / after 数据 diff。

TA 能力关键词：确定性导出、Maya 求值、矩阵 / pose 建模、namespace / root 清理、隔离执行。

## 四.开发节奏

### P0.抽象业务模型

目标：把 Lightbox 高价值线转成公开可讲的业务模型，不依赖公司源码。

任务：

- 为 6 条高价值线各写一张 case card：业务问题、关键数据、核心规则、可公开重制方式、AI 插入点。
- 从现有 Obsidian 深读笔记整理证据索引，只保留方法，不搬内部业务细节。
- 确定首批 4 个 demo 的合成数据格式。

完成标准：

- `docs/case-studies/_case-card-template.md`
- 4 张首批 case card。
- 一份 `docs/lightbox-method-index.md`，记录每条线学到的 TA 方法。

### P1.作品集首页和信息架构

目标：先让作品集像一个真实 AI 工具 TA 展示产品，而不是文档目录。

任务：

- 创建 `showcases/portfolio-site`。
- 首页包含定位、demo 矩阵、Lightbox-inspired method map、案例入口。
- 每个 demo 卡片显示：业务问题、核心逻辑、AI 作用、可运行状态、证据材料。

完成标准：

- 本地可运行。
- 桌面和移动端无文字溢出。
- 访问首页 1 分钟内能理解“我会做 DCC 生产工具，不只是会写 AI prompt”。

### P2.先做 Asset Semantic Codec

目标：先拿最有“核心惊艳”的数据协议案例打穿。

原因：

- 它能直观展示 TA 判断力：业务语义该放哪里、如何编码、如何反查。
- 实现成本可控，不需要真实 Maya。
- 视觉表达强，适合作品集首个 demo。

任务：

- 实现面片选择、标签配置、UV3-like 编码、bitmask 预览、反向解析。
- 加 AI schema assistant：输入业务描述，输出编码 schema 草案。
- 写 case study，明确来自 `og2_vehicle_light_tools` 的方法启发。

完成标准：

- 一个完整可交互 demo。
- 一份流程图。
- 一份 case study。

### P3.做 Naming & Material Sync

目标：展示“规范文档 -> 配置 schema -> 工具执行”的能力。

任务：

- 实现命名 schema、旧名解析、批量重命名 preview、贴图 slot 匹配。
- 加 AI rule parser：把自然语言规范转成字段 schema 和命名模板。
- 展示执行前 diff 和冲突原因。

完成标准：

- 能用合成资产跑完整命名 / 材质 / 贴图同步流程。
- 自动执行和 AI 建议边界清楚。

### P4.做 Pyblish Rulebench

目标：展示“TA 规则工程”和“AI 解释层”的结合。

任务：

- 实现轻量 Collect / Validate / Fix / Extract。
- 规则覆盖 tags_config、LOD、碰撞体、贴图密度、材质 ID。
- UI 区分 error / warning / info，展示修复动作。
- AI 总结检查报告，生成修复优先级。

完成标准：

- 至少 10 条规则。
- 至少 4 个确定性 fix。
- 至少 1 个 extract 输出。

### P5.做 Animation Export Stabilizer

目标：展示动画 / rig / 导出这条更硬核的 TA 线。

任务：

- 先做数据模拟和可视化，不强依赖 Maya。
- 展示直接导出 vs 稳定化导出的 before / after。
- 重点讲清 frame-by-frame evaluate、bake final value、jointOrient、root、namespace 清理。

完成标准：

- 能看到曲线差异和导出 payload 差异。
- case study 讲清“导出工具的核心是确定性”。

### P6.整理成正式作品集

目标：形成可投递、可面试讲、可持续追加案例的作品集。

任务：

- 每个 demo 录 30-60 秒短视频或 GIF。
- 每个 case study 写成统一结构。
- 首页补一页 Method Map：数据协议、规则引擎、确定性导出、AI 解释层。
- README 链到所有 demo 和 case study。

完成标准：

- 4 个 demo 至少 3 个可运行。
- 每个 demo 有截图 / 录屏、case study、合成数据。
- 可以不依赖内部网络独立展示。

## 五.近期执行顺序

1. 先写 `Asset Semantic Codec` case card 和数据 schema。
2. 建 `showcases/portfolio-site`，首页先放静态 demo 矩阵。
3. 实现 `Asset Semantic Codec` 交互原型。
4. 补 `Naming & Material Sync` case card。
5. 再进入 `Pyblish Rulebench`，因为它最能体现规则工程深度。

## 六.边界

- 不复制 Lightbox 公司源码、内部路径、真实项目资产和敏感规则文本。
- demo 使用合成资产和抽象规则，展示的是方法能力。
- AI 只做 schema 草案、解释、诊断和修复建议；真正修改数据的部分必须保持确定性、可预览、可回滚。


