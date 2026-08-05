# Blender Rule Adapter

## 一.业务场景

Cross-DCC Rule Matrix 的关键不是“同一套 UI 支持多个 DCC”，而是同一条发布规则在不同 DCC 里有不同事实来源。Maya 看 custom attr、transform、shadingEngine；Blender 看 object custom properties、collections、material slots、UV layers 和 collision proxy 命名。

本模块把 Blender 侧事实归一化成作品集已有的 Cross-DCC rule input，让同一套门禁可以比较 Maya / Blender / 引擎交付结果。

## 二.核心逻辑

当前 adapter 做 7 件事：

- 从公开 synthetic fixture 建 Blender 背景场景。
- 通过 `bpy` 采集 object custom properties、collections、material slots、UV layers、collision proxy。
- 把 Blender 原始字段映射到 `cross-dcc-rule-input@0.1.0`。
- 对每个资产执行 protocol carrier、collision contract、LOD budget、material/texture sync、UV contract、export root 六类规则。
- 输出 per-asset gate、rule evaluations 和 fix preview。
- 对 blocked public fixture 行执行受控 repair receipt，post-check 到 Ready 后回滚。
- 明确 mutation boundary：只创建临时 public fixture object，不写生产 scene、资产库或引擎内容。

## 三.当前证据

Artifact：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260804-201125.json
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-controlled-repair-20260806-043919.json
```

结果：

| Field | Value |
| --- | --- |
| L2 Report | `blender-rule-adapter-contract@0.1.0` |
| L3 Report | `blender-rule-adapter-bpy-l3@0.1.0` |
| Repair Report | `blender-controlled-repair-executor@0.1.0` |
| Evidence level | L3 |
| L3 status | `bpy_scene_collected` / `blender_controlled_repair_rolled_back` |
| Blender runtime | 5.2.0 LTS background |
| Assets | 2 |
| Ready / Blocked | pre 1 / 1, post-repair 2 / 0 |
| Checks pass / warning / error | 8 / 3 / 1 |
| Gate | Collector `Blocked`; controlled repair `Ready` with rollbackPassed=true |
| Repair operations | 4 / 4 collision proxy, LOD1, UV metrics, material/texture metadata |
| Writes | assetWrites=0, productionWrites=0 |

## 四.展示价值

这条证据说明作品集的“跨 DCC”不是前端 mock：规则层已经有非 Maya 的字段归一化、失败路径、fix preview、真实 Blender runtime 采集和受控修复回滚。当前它被 R57 DCC Presenter Pack 作为 required evidence file 探测。

后续开发重点不是继续证明 Blender 能启动，而是把 transaction receipt 抽成共享中间层，并扩展 UV/vertex color 语义 carrier、平台 variant、真实资产导入前的材质/LOD一致性对比。
