# 一.问题反馈

继续长期循环开发，目标是把作品集从 Maya-first 推进到跨 DCC / 引擎可展示。R12 已完成 Blender adapter L2，但引擎线仍主要停在 Maya 侧 Engine Preflight / PC-Mobile preset compare，缺少 engine-side inspection 证据。

# 二.⭐回顾分析

本轮检查到本机存在：

```text
C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe
```

但本地没有可复用公开 `.uproject`，也没有配置 `AI_TOOL_TA_UNREAL_PROJECT`。因此本轮不声明 Unreal L3，而是先完成 L2 inspector contract：证明 DCC import intent 进入 Unreal 前还要过 Content Registry / AssetImportTask 语义检查。

这条线的业务价值比继续扩 UI 或 owner drill 更高：很多资产问题不是 Maya 里看不出来，而是进入引擎后才暴露为路径、覆盖、依赖、平台 preset、LOD/collision、owner hold 混入导入包等问题。

# 三.改动解释

新增 `dcc-hosts/unreal-handoff-inspector`：

- `fixtures/synthetic_unreal_handoff.json`：公开 synthetic Unreal handoff fixture。
- `unreal_handoff_inspector/contract.py`：纯 Python inspector contract。
- `scripts/run_smoke.py`：检测 Unreal CLI / project env，导出 artifact。
- `README.md`：说明 L2/L3 边界。

当前 artifact：

```text
<repo>\dcc-hosts\unreal-handoff-inspector\artifacts\unreal-handoff-inspector-contract-20260803-181658.json
```

更新 Maya Presenter Pack API：新增 Unreal Handoff Inspector evidence probe、summary 字段、demo route step 和 reviewer claim；默认导出 label 改为 `r13-engine-presentation-pack`。

更新前端 `DccFirstCasePage`：Maya 内入口文案改为 `R13 Cross-DCC / Engine Presenter Pack`，导出 label 改为 R13，并在 Presenter Pack 结果里显示 Unreal inspector 的 L2 / gate 状态。

更新 public package：`dcc-first-package-manifest.json` 升级到 `ai-tool-ta-dcc-first-showcase-r13` / `dcc-first-package@1.10.0`，新增 Unreal inspector required artifact，并把 Presenter Pack 指向：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r13-engine-presentation-pack-20260803-181814.json
```

新增模块文档：

```text
<repo>\docs\modules\unreal-handoff-inspector.md
```

# 四.计划&状态

已完成验证：

- `python -m py_compile`：Maya host API、Blender adapter、Unreal inspector 通过。
- `python dcc-hosts/unreal-handoff-inspector/scripts/run_smoke.py`：2 import intents，1 import-ready，1 Blocked，1 dry-run import command，14 pass，2 review，4 blocked。
- `Maya 2024 mayapy dcc_presentation_export_pack(label="r13-engine-presentation-pack")`：13 / 13 evidence files present，0 missing required files，8 demo route steps。
- `npm run build`：前端生产构建通过，仅保留既有 Vite 大 chunk 警告。
- manifest / artifact consistency check：通过。

当前完成度：DCC-first 展示链约 80%。Maya L3、Blender L2、Unreal inspector L2 都已纳入同一个 Presenter Pack。剩余关键项是 Unreal test `.uproject` L3、Blender CLI L3、真实 Maya GUI 截图/录屏。

下一轮建议：准备公开 Unreal test `.uproject`，把 Unreal Handoff Inspector 从 L2 contract 升级为 `UnrealEditor-Cmd.exe -run=pythonscript` L3 smoke。
