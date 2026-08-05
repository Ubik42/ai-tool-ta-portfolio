# Asset Protocol Workbench

R1 目标：把 Lightbox 资产协议类经验转成公开可运行工具雏形。

## 方法来源

- `maya_asset_tool_reference/asset_protocol_editor_reference`
- `og2_vehicle_light_tools`
- `maya_asset_tool_reference/lod_texture_bake_reference`
- `tangent_save`
- `save_vertex_normal_info`

## 核心业务秘诀

资产协议不是 UI 表单，而是资产状态机。

协议字段必须同时满足：

- 能被美术/TA 在工具里读写。
- 能被自动检查规则消费。
- 能被导出阶段打包成 manifest。
- 能被下游引擎或工具链稳定保留。
- 能反查回业务含义。

这就是 Lightbox 里 UV、vertex color、custom attr、LOD 字段、平台字段、collision 字段、Nanite/streamable 字段有价值的原因。它们不是“附加信息”，而是资产生产协议的可计算入口。

## 当前实现

代码入口：

- `showcases/portfolio-site/src/data/assetProtocol.ts`
- `showcases/portfolio-site/src/App.tsx`

R1 已实现：

- 3 个 synthetic asset fixtures。
- asset protocol encode manifest。
- 6 条确定性 validation rules。
- publish readiness score。
- fixture 切换 UI。
- protocol facts、rule result、encoded payload 预览。
- schema version：`lb_asset_protocol@1.1.0`。
- 协议字段编辑器。
- before / after protocol diff。
- auto-fix preview，区分 safe fix 和 manual action。
- AI risk brief，根据 rule engine 输出生成风险摘要，不参与资产修改。
- before / after encoded payload diff。
- safe fix payload diff。
- safe-fix audit trail。
- edit presets：mobile cleanup、LOD prep、material sync。
- report JSON 预览和导出动作。
- case-study card。
- staged preset 交互证据。
- report JSON 下载落盘校验。

## 当前规则

| Rule | 目的 |
| --- | --- |
| Semantic carrier | 检查业务语义是否写入 UV3 / vertex color / custom attr |
| Mobile Nanite gate | 阻断 mobile 资产错误开启 Nanite |
| LOD budget | 提醒 LOD 数不足会影响平台预算 |
| Collision protocol | 阻断缺失 collision 的可交付资产 |
| Texture budget | 提醒 mobile texture set 过量 |
| Material / texture sync | 检查材质槽和贴图集数量漂移 |

## AI 边界

AI 在这个模块里只做三件事：

- 从需求草拟协议字段。
- 解释规则失败原因和平台风险。
- 把 validation result 整理成 publish readiness summary。

AI 不直接修改资产，也不覆盖 rule engine 的阻断结果。

## Auto-fix 边界

当前只把确定性强、不会发明资产内容的动作标记为 safe fix：

- Mobile asset 开启 Nanite 时，自动改为 off。

其余动作只进入 manual action：

- 缺 collision：需要生成或手工 author collision。
- LOD 不足：需要 queue LOD generation。
- mobile texture set 超预算：需要 texture merge preview。
- material slot / texture set 漂移：需要审查 shader binding。

这个边界来自真实 TA 工具经验：能确定的字段可以自动改，涉及几何、材质绑定和资产质量判断的改动必须先给证据和预览。

## R1.5 验证

浏览器自动化验证了真实交互链路：

- 点击 `Stage Preset` 后，`mobile cleanup` preset 把 `Mobile Crate / risky` 从 blocked 推到 ready。
- report 下载文件：`assets/asset-protocol-r1-5-exported-report.json`。
- 关键校验结果：readiness `100 / Ready`、protocol diff `6`、audit event `6`、first audit kind `preset`。
- 截图证据：`assets/asset-protocol-r1-5-staged-preset-full.png`。

这个验证说明当前模块已经不只是静态面板，而是具备“规则判断 -> staged edit -> payload diff -> audit -> report export”的完整工具链闭环。

## 下一轮

R1 封口和 R2 启动继续补：

- 把当前 rule engine 抽成 Cross-DCC Rule Matrix 可复用接口。
- R1.5 小结和进入 R2 的 adapter 设计。

