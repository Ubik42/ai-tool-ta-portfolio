# 一.问题反馈

本轮继续 AI Tool TA 作品集 DCC-first 长期任务。R20 的 Blender L3 readiness 已完成，但本机没有 `blender.exe`，不能把 Blender contract 冒充成真实 L3 成功。为了继续增加非 Maya 真实行业插件覆盖，本轮转向本机已安装的 3ds Max 方向，提炼 Lightbox 3ds Max Pyblish 类资产检查逻辑，建立新的 Cross-DCC adapter 证据。

# 二.⭐回顾分析

3ds Max 高价值点不在 UI，而在 Max 场景事实如何稳定进入规则系统：user properties、layer/export root、LOD suffix、material slot、map channel、Unwrap/UV 质量、transform reset/frozen state、pivot、collision proxy/UCX 命名和 vertex color boundary。这些都是资产发布前 TA 真正需要管的业务事实。

本机发现 `C:\Program Files\Autodesk\3ds Max 2022\3dsmaxbatch.exe`，但 3ds Max batch 可能触发 license、UI session 或长时进程成本。因此本轮默认不自动启动 Max runtime，而是交付 L2+ contract 和 opt-in L3 readiness。这个状态比假 L3 更有价值，因为它把 runtime 边界、collector readiness 和下一步命令讲清楚。

# 三.改动解释

新增 `dcc-hosts/3dsmax-rule-adapter`：

- `fixtures/synthetic_3dsmax_scene.json`：2 个公开资产，1 个 Ready static prop，1 个 intentionally Blocked hero prop。
- `max_rule_adapter/contract.py`：把 Max source facts 归一化为 `cross-dcc-rule-input@0.1.0`，执行 protocol、unit/up axis、export root、LOD、material naming、UV、transform、collision、vertex color 规则。
- `max_rule_adapter/runtime_collector.py`：提供 `pymxs` collector 路径，构造公开 synthetic scene 并回收 Max runtime facts。
- `scripts/run_smoke.py`：普通 Python L2+ contract smoke。
- `scripts/run_l3_smoke.py`：定位 `3dsmaxbatch.exe` 并导出 readiness；`--run-runtime` 才会启动 Max batch。
- `scripts/run_3dsmax_l3.py`：供 `3dsmaxbatch.exe` 调用的真实 L3 入口。

同步接入：

- Maya `dcc_presentation_build_pack` / `dcc_presentation_export_pack` 默认标签升级到 `r21-3dsmax-rule-adapter-presentation-pack`。
- Presenter Pack 新增 Max contract 和 Max L3 readiness 两个 evidence probe，demo route 从 11 步升级到 12 步。
- DCC-first 页面新增 Max artifact rows、Presenter Pack summary fields 和 Max adapter / Max L3 harness 展示。
- public package 升级到 `ai-tool-ta-dcc-first-showcase-r21` / `dcc-first-package@1.18.0`。
- README、DCC hosts README、public package 文档、Cross-DCC Rule Matrix 文档、长期计划和技术报告同步到 R21。

# 四.计划&状态

本轮验证已完成：

- `python -m py_compile`：Maya API 和 3ds Max adapter 全部通过。
- `python -m json.tool`：DCC manifest、public package manifest、Max contract artifact、Max readiness artifact 通过。
- `npm run build`：通过，仅保留 Vite 大 chunk warning。
- `python dcc-hosts/3dsmax-rule-adapter/scripts/run_smoke.py`：导出 `max-rule-adapter-contract@0.1.0`，2 assets，1 Ready，0 Review，1 Blocked，13 pass，5 warning，2 error。
- `python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py`：导出 `max-rule-adapter-l3-readiness@0.1.0`，gate `Review`，collector ready，`3dsmaxbatch.exe` discovered，runtime not invoked。
- Maya 2024 `mayapy dcc_presentation_export_pack`：导出 R21 Presenter Pack，19 / 19 evidence files present，0 missing required files，12 demo route steps，gate `CapturePending`。

关键 artifact：

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-contract-20260804-220959.json
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts\max-rule-adapter-l3-readiness-20260804-220959.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r21-3dsmax-rule-adapter-presentation-pack-20260804-221449.json
```

下一轮入口：

1. operator 允许时运行 `python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py --run-runtime`，把 Max readiness 升级成 `max-rule-adapter-pymxs-l3@0.1.0`。
2. 如果不启动 Max batch，继续定位 Blender CLI 或采集 Maya GUI 截图/录屏，让 Presenter Pack media gate 从 `CapturePending` 进入可审核。
3. 如果两个 runtime 都暂不动，选择 Houdini / MotionBuilder 建下一条公开 fixture adapter。
