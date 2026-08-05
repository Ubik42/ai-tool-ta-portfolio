# AI 接手说明

## 1. 最终展示效果

目标不是网页作品集，而是 DCC / 引擎内展示的工具管线 TA 能力。

最终 reviewer 应看到：

- Maya 2024 内通过 AuroraView 打开工具面板。
- 面板里有资产协议、规则矩阵、视觉评审、贴图交付、任务编排、资产放行、引擎预检、场景事务保护等模块。
- 每个模块能导出 JSON artifact，说明业务事实、规则判定、fix preview、owner 边界和写入边界。
- 非 Maya 证据已经覆盖 Blender `bpy` L3、3ds Max `pymxs` L3、Unreal Python L3++。
- Presenter Pack 把所有关键证据汇总成 reviewer 可读的发布包。

当前稳定展示包：

```text
public-case-package/DCC_FIRST_PACKAGE.md
public-case-package/dcc-first-package-manifest.json
dcc-hosts/maya-auroraview-host/artifacts/r22-blender-max-l3-presentation-pack-20260805-153957.json
```

## 2. 当前完成度

稳定基线：R22。

已完成：

- Maya AuroraView Host / Presenter Pack
- Asset Protocol Workbench
- Cross-DCC Rule Matrix
- Visual Review Studio
- Texture Delivery Console
- Task Orchestrator
- Asset Handoff Gate
- Unreal Handoff Inspector
- Scene Transaction Guard
- Blender Rule Adapter L3
- 3ds Max Rule Adapter L3
- Maya command bridge
- 轻量验证脚本 `scripts/validate_loop.ps1`

仍缺：

- Maya GUI 9 张 PNG 和 1 段 MP4，留到最后人工采集。
- MotionBuilder / Houdini / Character Calibration / Spatial Authoring 等后续工具线。

## 3. R23 半成品断点

用户暂停时，`Animation Continuity Lab` 已开始建骨架；当前 L2 contract smoke 已通过，但未接入 Presenter Pack。

已新增本地文件：

```text
dcc-hosts/animation-continuity-lab/fixtures/synthetic_animation_scene.json
dcc-hosts/animation-continuity-lab/animation_continuity_lab/contract.py
dcc-hosts/animation-continuity-lab/animation_continuity_lab/maya_collector.py
dcc-hosts/animation-continuity-lab/scripts/run_smoke.py
dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py
dcc-hosts/animation-continuity-lab/scripts/run_maya_l3.py
```

已生成首个 L2 artifact：

```text
dcc-hosts/animation-continuity-lab/artifacts/animation-continuity-contract-20260805-160346.json
```

这条线的最终效果：

- 检查动画交付中的 rig identity、skeleton fingerprint、Take range、sample rate、required channel coverage。
- 检查 sub-frame keys、channel identity collision、root motion policy、scale drift、active additive layers。
- 通过 Maya `mayapy` 生成真实 keyed animCurve runtime evidence。
- 后续再接入 MotionBuilder / Unreal animation import 对照。

继续开发时先做 Maya L3：

```powershell
python dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py
```

通过后再接 Presenter Pack 和 public manifest。

## 4. 长期开发规则

每轮只闭环一个高价值业务任务。

默认验证：

```powershell
.\scripts\validate_loop.ps1 -Tier quick
```

只在对应模块变化时跑对应 runtime 档位；只有发布里程碑跑 `full`。

详细策略：

```text
docs/技术报告/260805_长期循环开发框架与轻量验证策略.md
```

## 5. 公开仓边界

公开仓应包含：

- `dcc-hosts`
- `showcases`
- `public-case-package`
- `fixtures`
- `docs`
- `scripts`
- `README.md`
- `PUBLIC_RELEASE.md`
- `PRODUCT.md`
- `DESIGN.md`

公开仓应排除：

- `lightbox提取`
- `assets` 下的大截图/录屏
- `node_modules`
- `dist`
- `.tmp`
- DCC 二进制场景和本地缓存
