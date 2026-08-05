# 一.问题反馈

本轮继续长期循环开发，目标是把作品集从 Maya-first 展示推进到跨 DCC / 引擎证据。上一轮的风险是 Presenter Pack 已经能在 Maya 内展示，但非 Maya 证据仍停在概念和前端 mock，容易被理解成“只有 Maya 工具”。

# 二.⭐回顾分析

Lightbox 高价值提炼里，跨 DCC 规则适配比继续追加 owner drill 更有展示价值。真正值得学习的是不同 DCC 的场景事实来源不同，但最终要归一成同一套发布规则输入：Maya 看 custom attr / shadingEngine / transform，Blender 看 object custom properties / collections / material slots / UV / collision proxy。

本机没有 Blender CLI，所以本轮不冒进声明 L3；先完成 L2 adapter contract、fixture、artifact、Presenter Pack 接入，后续安装 Blender 后再补 `blender --background --python`。

# 三.改动解释

新增 `dcc-hosts/blender-rule-adapter`：包含 synthetic Blender scene fixture、`blender_rule_adapter.contract`、`scripts/run_smoke.py` 和 artifact 输出。当前 artifact 为：

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260803-180736.json
```

更新 Maya Presenter Pack API：加入 `blender-rule-adapter` evidence probe、Blender adapter summary、7 步 demo route 和 reviewer claim；默认导出 label 改为 `r12-cross-dcc-presentation-pack`。

更新前端 `DccFirstCasePage`：Maya 内页面显示 R12 Cross-DCC Presenter Pack，按钮导出 R12 label，并在 Presenter Pack 结果里展示 Blender adapter 的 L2 / gate 状态。

更新 public package 和文档：`dcc-first-package-manifest.json` 升级到 `ai-tool-ta-dcc-first-showcase-r12` / `dcc-first-package@1.9.0`，`DCC_FIRST_PACKAGE.md`、`VALIDATION.md`、root README、dcc-hosts README、长期计划和技术报告都已指向 R12。新增模块文档：

```text
<repo>\docs\modules\blender-rule-adapter.md
```

# 四.计划&状态

已完成验证：

- `python -m py_compile`：Maya host API、Blender adapter contract、Blender smoke 脚本通过。
- `python dcc-hosts/blender-rule-adapter/scripts/run_smoke.py`：2 assets，1 Ready，1 Blocked，8 pass，3 warning，1 error，L3 status 为 `blocked_by_missing_blender_cli`。
- `Maya 2024 mayapy dcc_presentation_export_pack(label="r12-cross-dcc-presentation-pack")`：生成 R12 Presenter Pack，12 / 12 evidence files present，0 missing required files，7 demo route steps。
- `npm run build`：前端生产构建通过，仅保留既有 Vite 大 chunk 警告。
- manifest / artifact consistency check：通过。

当前完成度：DCC-first 展示链约 75%。Maya 内工具闭环和公开 JSON 证据已经成型；跨 DCC 已有第一条 L2 证据；真实 GUI 截图/录屏、Blender L3、Unreal-side inspection 仍未完成。

下一轮建议：优先做 Unreal-side inspection，把 Engine Preflight / Preset Compare 从 dry-run sidecar 推进到引擎侧可验证 artifact；如果先安装 Blender，则把 `blender-rule-adapter` 升级为 L3。
