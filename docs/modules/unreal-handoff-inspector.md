# Unreal Handoff Inspector

## 一.业务场景

DCC 侧 `Engine Preflight` 只能证明“这个资产准备生成 import intent”。真实工具管线还要在引擎侧继续判断：Content Browser 目标路径是否合法、现有资产是否冲突、source fingerprint 是否和 sidecar 一致、材质贴图依赖是否存在、LOD/collision 是否满足平台 preset、owner-held 资产是否被错误导入。

本模块把 Maya 的 engine handoff intent 推进一步，变成 Unreal-side import inspection contract。

## 二.核心逻辑

当前 inspector 做 10 件事：

- 读取公开 synthetic Unreal handoff fixture。
- 读取 synthetic Content Registry / import intent，并在 Unreal test project 里生成真实 registry fixture。
- 检查 mount root、platform preset、asset class、source fingerprint、content conflict、material dependencies、LOD policy、collision policy、owner state、Python plugin readiness。
- 对 import-ready 资产生成 Unreal `AssetImportTask` dry-run command preview。
- 对 blocked 资产输出具体 blocked/review reason 和 fix preview。
- 记录本机 Unreal CLI 是否存在。
- 在 Unreal Python 内导出 runtime snapshot，证明 headless engine smoke 真实执行。
- 在 `/Game/AI_Tool_TA` 下验证 `SM_HeroPanel_A` StaticMesh 和 `M_HeroPanel` Material 两条 Asset Registry path/class row。
- 从 `SM_HeroPanel_A` StaticMesh 读取 source import data、material slot assignment、LOD count 和 collision settings。
- 把 Unreal runtime facts 与 PC / Mobile preset policy、exception waiver rows 做对比，输出 matched / drift / waived / blocked。
- 把 preset comparison 投影到 Maya/AuroraView reviewer queue，显示 blocked、drift、waived 和 matched row 的 owner action。

## 三.当前证据

Artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-l3-20260803-184208.json
```

Preset fact comparison artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-preset-fact-comparison-20260803-185302.json
```

Preset fact review artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r18-unreal-preset-fact-review-20260803-190519.json
```

结果：

| Field | Value |
| --- | --- |
| Report | `unreal-handoff-inspector-contract@0.4.0` |
| Evidence level | L3++ |
| L3 status | `unreal_engine_facts_matched` |
| Unreal runtime | 5.3.2 / Python 3.9.7 |
| Asset Registry | queried, 2 / 2 fixture rows matched |
| Engine facts | source import, material slot, LOD, collision all matched |
| Preset fact report | `unreal-preset-fact-comparison@0.1.0` |
| Preset fact review | `maya-unreal-preset-fact-review@0.1.0` |
| Preset fact gate | `Blocked` |
| Preset fact rows | 10 |
| Matched / Drift / Waived / Blocked | 7 / 1 / 1 / 1 |
| Review queue / blocked / waivers | 3 / 1 / 1 |
| Platform split / approved waiver | 1 / 1 |
| Import intents | 2 |
| Import ready / Blocked | 1 / 1 |
| Dry-run import commands | 1 |
| Checks pass / review / blocked | 14 / 2 / 4 |

## 四.展示价值

这条证据补的是 DCC 工具常见断点：很多工具只在 Maya 里生成“可导入”的判断，但真正事故经常发生在引擎路径、覆盖冲突、依赖缺失、平台 preset 和 owner-held 资产混入导入包。R18 Presenter Pack 已把它作为 required evidence file，并且 evidence level 已从 L2/L3/L3+ 升级到 L3++，再追加了 preset fact comparison 和 Maya-hosted preset fact review。

R17 的业务点是 waiver 边界：PC 的 public fixture 单 LOD 被 owner-scoped waiver 收进 Review，Mobile 仍因路径和 LOD policy 保持 blocked。这比单纯“读到引擎事实”更接近真实 TA 的放行/阻断决策。

R18 把这层判断投影回 Maya/AuroraView：`Preset Facts` 按钮不让 reviewer 打开 JSON，而是直接显示 preset summary、asset platform split 和 fact row queue。当前队列 3 条：Mobile engine path blocked、Mobile LOD drift、PC LOD approved waiver。这个面板展示的是工具管线 TA 最有价值的判断逻辑：规则不是只报错，而是区分可放行、需 owner 决策、已批准例外和必须阻断。
