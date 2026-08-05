# 3ds Max Rule Adapter

R22 目标：把 Lightbox 里 3ds Max Pyblish 类资产检查经验，抽象成公开可复现的 Cross-DCC Rule Matrix adapter，并通过真实 `pymxs` batch 证明 runtime 采集路径。

## 核心业务逻辑

3ds Max 资产检查的关键不是“跑一堆规则”，而是先把 Max 特有的证据稳定取出来：

- user properties 承载资产协议和平台意图。
- layer / export dummy 表示导出根和资产分组。
- `*_LOD#` suffix 或节点属性表示 LOD sequence。
- material slot 和 bitmap slot 表示材质 / 贴图同步关系。
- map channel / Unwrap_UVW 表示 UV 通道预算、重叠、利用率和 texel density。
- frozen transform、pivot、scale 表示导出前状态是否干净。
- `UCX_*` / proxy node 表示 collision contract。

这些 Max source facts 会被归一化成 `cross-dcc-rule-input@0.1.0`，让共享规则判断 protocol carrier、unit/up axis、export root、LOD、material naming、UV budget、UV quality、transform、collision 和 vertex color boundary。

## 当前实现

代码入口：

- `dcc-hosts/3dsmax-rule-adapter/max_rule_adapter/contract.py`
- `dcc-hosts/3dsmax-rule-adapter/max_rule_adapter/runtime_collector.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_smoke.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_3dsmax_l3.py`
- `dcc-hosts/3dsmax-rule-adapter/fixtures/synthetic_3dsmax_scene.json`

R22 已完成：

- L2+ contract smoke：普通 Python 读取公开 synthetic fixture，输出 normalized facts、evaluation rows 和 fix preview。
- L3 runtime smoke：`3dsmaxbatch.exe` 启动 3ds Max 2022，通过 `pymxs` 创建/采集 public fixture scene。
- Presenter Pack 接入：Maya-hosted R22 package 会探测 Max contract artifact 和 Max runtime L3 artifact。
- Public package 接入：manifest 记录 Max adapter gate、evidence level、asset/check counts、batch availability 和 `pymxs_scene_collected`。

当前 runtime 结果：

- fixture assets：2。
- ready / review / blocked：1 / 0 / 1。
- pass / warning / error：13 / 5 / 2。
- runtime collected：true，object count：4。
- L3 gate：`Blocked`，原因是 public fixture 故意包含一个 blocked asset。
- mutation boundary：只创建临时 public fixture nodes，不写生产 Max scene、资产库或引擎内容。

## 证据

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260805-153232.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r22-blender-max-l3-presentation-pack-20260805-153957.json
```

## 下一轮

下一步不是再跑 readiness，而是扩展 Max 业务面：材质 slot 到贴图交付 manifest 的交叉验证、LOD suffix 和 export root 的批量修复 preview、以及 Max scene transaction recorder。
