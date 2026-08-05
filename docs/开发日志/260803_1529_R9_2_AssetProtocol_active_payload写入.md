# 一.问题反馈

用户要求进入“循环任务自主推荐开发”。当前最有价值的下一步是 R9.2：把 `Asset Protocol Workbench` 的当前业务 payload 接入 Maya 写入动作，避免 `Maya Bridge` 只写默认样例 payload。

# 二.⭐回顾分析

R9.1 已经证明 Maya AuroraView 宿主可打开，前端也能调用 `MayaPortfolioApi` 的 6 个方法。R9.2 的关键不是继续新增按钮，而是让中央业务模块和右侧 DCC Bridge 共享同一个 live payload。

本轮选择的工程策略：

- custom attr 写入当前 `EncodedProtocol` 加 DCC 追踪外壳，不把完整 report 直接塞进节点。
- 完整 report 仍保留在导出对象里，用于证据包和后续 before/after。
- 建立通用 `DccPayloadContext`，后续 Cross-DCC Rule Matrix、Visual Review、Texture Delivery 都可以复用这个发布机制。

# 三.改动解释

新增：

- `showcases/portfolio-site/src/lib/dccPayloadContext.tsx`

改动：

- `showcases/portfolio-site/src/App.tsx`
  - 用 `DccPayloadProvider` 包裹工具台。
- `showcases/portfolio-site/src/components/AssetProtocolWorkbench.tsx`
  - 发布当前 fixture / editor state / encoded payload / readiness / diff / report。
  - 把关键派生对象改成 `useMemo`，避免 provider 更新导致重复发布循环。
- `showcases/portfolio-site/src/components/MayaBridgePanel.tsx`
  - `Write Attr` 改为写入 active payload。
  - 面板显示 active payload 的模块、label、gate、score、diff、updated。
  - `Export` 报告中带上 active payload。
- `showcases/portfolio-site/src/styles.css`
  - 新增 active payload 信息块样式。

文档更新：

- `docs/260803_DCC-first长期开发计划与环境.md`
- `dcc-hosts/maya-auroraview-host/README.md`
- `README.md`

# 四.计划&状态

已验证：

- `npm run build` 通过。
- Maya host Python `py_compile` 通过。
- Maya 2024 `mayapy` 复杂 active payload smoke 通过：创建 fixture、写入两个节点、inspect 回读 schema、导出 report。

生成 report：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-2-active-payload-smoke-20260803-152936.json
```

下一轮推荐：

1. 在 Maya GUI 里点 `Fixture`、修改 Asset Protocol 字段、点 `Write Attr`、点 `Inspect`，确认 active payload 变化能写入 scene。
2. R9.2 下一段把 Maya `Inspect` 结果回填到 `Asset Protocol Workbench`，展示 scene payload before/after。
3. R9.3 开始把 Cross-DCC Rule Matrix 的 collect / validate / fix preview 接入 Maya scene。
