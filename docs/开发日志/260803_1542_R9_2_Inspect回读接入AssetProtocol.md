# 一.问题反馈

用户要求设置循环任务自主推进开发。长期目标已登记为 active，当前按 DCC-first 路线自动推进 R9.2 第二段：把 Maya `Inspect` 回读结果接回 `Asset Protocol Workbench`。

# 二.⭐回顾分析

R9.2 第一段已经实现 active payload 写入 Maya custom attr，但回读结果只停留在右侧 `Maya Bridge` 的 JSON 输出区。作为业务工具，Asset Protocol 模块本身需要知道 scene 中实际写了什么，才能形成 before/after 和证据链。

本轮实现重点：

- `Inspect` 结果进入共享上下文。
- Asset Protocol 消费 scene inspection。
- UI 明确标记 `match` / `drift` / `missing` / `stale`，避免把旧 inspect 当作当前 payload。

# 三.改动解释

改动：

- `showcases/portfolio-site/src/lib/dccPayloadContext.tsx`
  - 新增 `DccSceneInspectionSnapshot`、`DccSceneProtocolRow`。
  - 新增 `sceneInspection` 和 `publishSceneInspection()`。
- `showcases/portfolio-site/src/components/MayaBridgePanel.tsx`
  - `Inspect` 成功后解析 rows，并写回 `sceneInspection`。
- `showcases/portfolio-site/src/components/AssetProtocolWorkbench.tsx`
  - 增加 `DCC Scene Payload` 面板。
  - 展示 rows、protocol rows、matched rows、inspect time。
  - 展示每个 Maya 节点的 match / drift / missing。
  - 展示当前 active payload 与第一个 scene payload 的 diff。
- `showcases/portfolio-site/src/styles.css`
  - 增加 scene payload summary、node list、sync chip、diff 区样式。

文档更新：

- `docs/260803_DCC-first长期开发计划与环境.md`
- `dcc-hosts/maya-auroraview-host/README.md`

# 四.计划&状态

已验证：

- `npm run build` 通过。
- Maya host Python `py_compile` 通过。
- Maya 2024 `mayapy` smoke 通过：写入复杂 active payload 后，inspect 回读到 `sourceModule=asset-protocol-workbench` 和 readiness score。

生成 report：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-2-inspect-feedback-smoke-20260803-154209.json
```

下一轮推荐：

1. 把 scene payload diff、validation、inspect rows 合并成一个 `Asset Protocol DCC Evidence Report`。
2. 在 Maya GUI 中按 `Fixture -> Write Attr -> Inspect` 验证 `DCC Scene Payload` 面板。
3. R9.3 开始把 Cross-DCC Rule Matrix 接入 Maya collect / validate / fix preview。
