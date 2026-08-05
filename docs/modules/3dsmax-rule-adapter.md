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
- `dcc-hosts/3dsmax-rule-adapter/max_rule_adapter/controlled_repair.py`
- `dcc-hosts/3dsmax-rule-adapter/max_rule_adapter/texture_manifest_link.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_smoke.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_3dsmax_l3.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_controlled_repair.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_3dsmax_controlled_repair.py`
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_texture_manifest_link.py`
- `dcc-hosts/3dsmax-rule-adapter/fixtures/synthetic_3dsmax_scene.json`
- `dcc-hosts/3dsmax-rule-adapter/fixtures/synthetic_texture_delivery_manifest.json`

R22 已完成：

- L2+ contract smoke：普通 Python 读取公开 synthetic fixture，输出 normalized facts、evaluation rows 和 fix preview。
- L3 runtime smoke：`3dsmaxbatch.exe` 启动 3ds Max 2022，通过 `pymxs` 创建/采集 public fixture scene。
- Presenter Pack 接入：Maya-hosted R22 package 会探测 Max contract artifact 和 Max runtime L3 artifact。
- Public package 接入：manifest 记录 Max adapter gate、evidence level、asset/check counts、batch availability 和 `pymxs_scene_collected`。
- R53 texture manifest link：读取真实 Max L3 material bitmap slot facts，和 texture delivery manifest 对账，检查 package coverage、required channel semantics、sRGB/linear policy、PC/Mobile resolution budget 和 owner action。
- R58 controlled repair：通过 `3dsmaxbatch.exe` 对 blocked hero fixture 执行 UCX collision、LOD1、MI 材质/贴图、UV/map channel、transform / vertex color 五条 repair receipt，post-check Ready 后 rollback。

当前 runtime 结果：

- fixture assets：2。
- ready / review / blocked：1 / 0 / 1。
- pass / warning / error：13 / 5 / 2。
- runtime collected：true，object count：4。
- L3 gate：`Blocked`，原因是 public fixture 故意包含一个 blocked asset。
- mutation boundary：只创建临时 public fixture nodes，不写生产 Max scene、资产库或引擎内容。

R53 结果：

- report version：`max-texture-manifest-link@0.1.0`
- evidence level：L3-derived
- gate：`Blocked`
- assets ready / review / blocked：1 / 0 / 1
- material rows / slot textures / manifest textures：3 / 4 / 4
- missing manifest textures：0
- missing required semantics：2
- checks pass / warning / error：13 / 1 / 2
- boundary：read-only artifact join，sceneWrites / assetWrites / engineWrites / productionWrites 全为 0

关键结论：Max 里看到了贴图节点，不等于贴图包可交付。必须把 DCC material slot、交付 manifest、通道语义、颜色空间和平台尺寸预算连起来判定。`max-prop-001` 可通过；`max-hero-002` 被 normal / orm 缺失和 mobile 4096 贴图预算阻断。

R58 controlled repair 结果：

- report version：`max-controlled-repair-executor@0.1.0`
- evidence level：L3
- gate：`Ready`
- preGate / postGate：`Blocked` / `Ready`
- selected / executed operations：5 / 5
- post ready / blocked：2 / 0
- post warnings / errors：0 / 0
- rollbackPassed：true
- boundary：只改 public fixture batch scene，sceneWrites=5，assetWrites / productionWrites 全为 0，不保存 `.max` 文件

关键结论：Max 修复不是“直接把场景改好”，而是把 collision、LOD、材质贴图、UV 和 transform 的每个变更都做成可审计 receipt，修完后重新跑门禁，再证明回滚边界。

## 证据

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-20260806-032411.json
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-texture-manifest-link-20260806-032426.json
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-controlled-repair-20260806-045433.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r53-max-texture-manifest-link-presentation-pack-20260806-032705.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r58-max-controlled-repair-presentation-pack-20260806-045801.json
```

## 下一轮

下一步可以继续扩展 Max 业务面：把 R58 repair receipt 抽到共享 transaction middleware，或把 R53 manifest link 接到 Texture Delivery Console 的统一包验收视图。
