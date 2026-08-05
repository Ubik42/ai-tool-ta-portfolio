# 一.问题反馈

当前 Maya / AuroraView 内已经有 5 个 DCC-first 模块和 `DCC Showcase Runbook`，但公开展示入口仍容易被旧 R8 browser evidence ledger 分流。需要把最终作品集入口明确收束到 Maya 内可运行的展示包，并让 reviewer 能看到演示脚本、GUI 点击路径、smoke 结果和 artifact 位置。

# 二.⭐回顾分析

R9.7 已经证明 5 个模块都能通过 Maya host API 跑出 DCC 证据：Asset Protocol、Rule Matrix、Visual Review、Texture Delivery、Task Orchestrator。R10 的价值不在新增业务模块，而在把这些证据组织成可讲、可点、可复查的公开展示包。

核心判断：

- 最终展示入口应该是 Maya Script Editor / shelf 打开 AuroraView 面板。
- 右侧 `DCC Showcase Runbook` 是主演示路径。
- Web build 保留为嵌入 UI 和历史证据浏览，不作为最终主舞台。
- `public-case-package` 需要指向 DCC-first package，而不是只停留在 R8 长链路清单。

# 三.改动解释

- `showcase_runbook_build_plan` 增加 5 步 live demo script 和 6 项 GUI click checklist。
- `showcase_runbook_export_package` 升级为 `maya-dcc-showcase-runbook-package@1.1.0`，输出 presentation、reviewer claims、evidence requirements 和 public case package 指针。
- `DccShowcaseRunbookPanel` 增加 live demo script、GUI click checklist 展示，并把默认导出 label 改为 `r10-dcc-first-showcase-package`。
- 新增 `public-case-package/DCC_FIRST_PACKAGE.md` 和 `public-case-package/dcc-first-package-manifest.json`，作为当前 reviewer 入口和机器可读清单。
- 更新 `public-case-package/README.md`、`package-manifest.json`、`VALIDATION.md`，把当前 DCC-first artifact 挂到公共包入口。
- 更新根 README、长期开发计划、Maya host README 和 runbook 模块文档，把状态从 R9.7/R10 待办推进到 R10 已完成。

# 四.计划&状态

已验证：

- `npm run build` 通过，仅保留 Vite large chunk 警告。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` smoke 通过：5 modules，5 artifacts，3 Ready，2 Review，0 Blocked，live demo script 5 步，GUI checklist 6 项，reviewer claims 4 条。
- 最新 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-dcc-first-showcase-package-20260803-162019.json
```

下一轮：

1. R10.1：按真实 TA 面试/展示顺序压缩模块入口和演示话术。
2. R10.2：补 Maya GUI 截图/录屏证据和公开展示素材清单。
3. R10.3：开始下一条高价值业务工具，优先做 Asset Handoff / Publish Gate 的 DCC 复合闭环。
