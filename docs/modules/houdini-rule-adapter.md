# Houdini Rule Adapter

R56 目标：把 Houdini procedural / HDA publish 里的核心交付判断，接到 Cross-DCC Rule Matrix。它不是展示“会打开 Houdini”，而是把程序化资产的业务事实稳定抽出来：HDA 状态、detail attributes、`OUT_*` 输出角色、packed prototypes、PDG wedges 和 frozen bake receipt。

## 核心业务逻辑

Houdini 资产交付的风险点和 Maya / Max 不一样。它的核心不是单个 mesh 节点是否规范，而是 procedural network 是否能被下游复现、冻结、拆分和追责：

- HDA definition 是否 locked，参数 fingerprint 是否稳定。
- detail attr 是否承载公开资产协议和平台意图。
- `OUT_RENDER_*`、`OUT_COLLISION` 等输出节点是否把 render / collision / LOD role 显式暴露出来。
- 几何 attributes 是否包含 `P`、`N`、`uv`、`shop_materialpath`、`name`、LOD / variant / collision 语义。
- packed instance prototype 是否有 stable id，避免 scatter 每次 cook 产生不可追踪结果。
- PDG wedge 是否有 approved / failed 摘要，不能只看最后产物存在。
- bgeo / cache receipt 是否 frozen、存在并带 hash，避免把可变 procedural 状态直接交给引擎。

这些 Houdini source facts 被归一化成 `cross-dcc-rule-input@0.1.0`，和 Blender / 3ds Max adapter 使用同一组 pass / warning / error rows。

## 当前实现

代码入口：

- `dcc-hosts/houdini-rule-adapter/fixtures/synthetic_houdini_scene.json`
- `dcc-hosts/houdini-rule-adapter/houdini_rule_adapter/contract.py`
- `dcc-hosts/houdini-rule-adapter/houdini_rule_adapter/hou_collector.py`
- `dcc-hosts/houdini-rule-adapter/scripts/run_smoke.py`
- `dcc-hosts/houdini-rule-adapter/scripts/run_houdini_l3.py`
- `dcc-hosts/houdini-rule-adapter/scripts/run_l3_smoke.py`

R56 已完成：

- L2+ contract smoke：普通 Python 读取公开 synthetic fixture，输出 normalized facts、rule rows、gate 和 mutation boundary。
- hython readiness harness：自动查找 `AI_TOOL_TA_HYTHON`、PATH `hython` 和常见 SideFX 安装路径。
- `hou` collector：在真实 hython 可用时创建 public subnet fixture，把 fixture payload 写入 Houdini node userData，再通过 `hou` 遍历回收 facts。
- Presenter Pack 接入：Maya-hosted R56 package 探测 Houdini contract artifact 和 hython readiness artifact。
- Public package 接入：manifest 记录 Houdini adapter gate、evidence level、asset/check counts、hython availability 和 collector readiness。

当前结果：

- report version：`houdini-rule-adapter-contract@0.1.0`
- evidence level：L2+
- L3 status：`blocked_by_missing_hython`
- gate：`Blocked`
- fixture assets：2
- ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：11 / 2 / 5
- hython available：false
- L3 harness collector ready：true
- mutation boundary：sceneWrites / assetWrites / productionWrites 全为 0

关键结论：Houdini 程序化资产不能只看导出文件是否存在。必须把 HDA 锁定状态、输出 role、geometry attributes、packed prototype stability、PDG wedge 和 frozen bake receipt 作为同一份发布证据。当前机器没有 `hython.exe`，所以 R56 正确输出 readiness blocked gate；等 Houdini runtime 可用后，同一入口会升级为 `houdini-rule-adapter-hython-l3@0.1.0`。

## 证据

```text
<repo>\dcc-hosts\houdini-rule-adapter\artifacts\houdini-rule-adapter-contract-20260806-041956.json
<repo>\dcc-hosts\houdini-rule-adapter\artifacts\houdini-rule-adapter-l3-readiness-20260806-041956.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r56-houdini-rule-adapter-presentation-pack-20260806-042654.json
```

## 下一轮

如果本机后续安装 Houdini 或能定位 `hython.exe`，直接运行：

```powershell
python dcc-hosts/houdini-rule-adapter/scripts/run_l3_smoke.py
```

否则继续补 MotionBuilder / Unreal Editor Utility / socket C++ adapter / Groom group-root projection 等其他业务线，不在 runtime 缺失处空转。
