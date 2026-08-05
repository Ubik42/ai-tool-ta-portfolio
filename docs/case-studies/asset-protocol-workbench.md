# Case Study: Asset Protocol Workbench

## 业务问题

资产交付失败往往不是因为一个脚本没跑，而是因为协议信息分散：一部分在命名里，一部分在 Maya 节点属性里，一部分写进 UV / vertex color，一部分只存在 TA 和美术的口头约定里。

这种状态下，publish 前最难判断的是：

- 资产到底面向哪个平台预算。
- LOD / collision / Nanite / streamable 是否互相冲突。
- 材质槽和贴图集是否匹配。
- 下游能不能稳定读到业务语义。
- 哪些问题能自动修，哪些必须人工审查。

## 方法来源

抽象自 Lightbox 中这几类高价值插件经验：

- `maya_asset_tool_reference/asset_protocol_editor_reference`：资产协议字段写回 DCC 节点，驱动平台、LOD、collision、Nanite、streamable 等状态。
- `og2_vehicle_light_tools`：用 UV / bitmask 承载车辆灯光、玻璃、材质等业务语义。
- `tangent_save` / `save_vertex_normal_info`：把下游需要的渲染 payload 写进稳定载体。
- `lod_texture_bake_reference`：LOD、贴图、法线、平台预算不是独立问题。

## 核心设计

这个 demo 把资产协议拆成 5 层：

1. Synthetic fixture：公开合成资产，不泄漏内部项目。
2. Protocol schema：统一声明字段、版本和 carrier。
3. Rule engine：确定性判断 pass / warning / error。
4. Edit preset：把常见 TA 操作做成可预览的 staged edit。
5. Report JSON：把规则、diff、fix、audit 和 payload 变成证据。

## AI 的位置

AI 不执行资产修改，也不覆盖规则阻断。

当前 AI 角色只做解释层：

- 把 rule result 归纳成 risk brief。
- 说明 safe fix 和 manual action 的边界。
- 为作品集 case-study 提供业务口径。

## 当前可运行能力

前端入口：

```powershell
cd <repo>\showcases\portfolio-site
npm run dev -- --host 127.0.0.1 --port 5181
```

当前功能：

- 3 个 synthetic asset fixture。
- 可编辑协议字段。
- schema version：`lb_asset_protocol@1.1.0`。
- validation rules。
- publish readiness。
- AI risk brief。
- before / after protocol diff。
- encoded payload diff。
- edit presets：mobile cleanup、LOD prep、material sync。
- safe/manual fix preview。
- action audit trail。
- report JSON export。

## 作为作品集的价值

这个模块展示的不是“会写检查脚本”，而是更核心的 TA 能力：

- 把资产规范变成可计算协议。
- 把 DCC 数据载体当成业务通道设计。
- 把自动修复和人工审查边界说清楚。
- 把工具结果包装成可复盘证据。

后续接 `Cross-DCC Rule Matrix` 时，这个模块可以作为 asset context 输入。

