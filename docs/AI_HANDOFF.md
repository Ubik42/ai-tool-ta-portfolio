# AI 接手说明

## 1. 最终展示效果

目标不是网页作品集，而是 DCC / 引擎内展示的工具管线 TA 能力。

最终 reviewer 应看到：

- Maya 2024 内通过 AuroraView 打开工具面板。
- 面板里有资产协议、规则矩阵、视觉评审、贴图交付、任务编排、资产放行、引擎预检、场景事务保护、动画连续性、角色校准等模块。
- 每个模块能导出 JSON artifact，说明业务事实、规则判定、fix preview、owner 边界和写入边界。
- 非 Maya 证据已经覆盖 Blender `bpy` L3、3ds Max `pymxs` L3、Unreal Python L3++；动画线已有 Maya `mayapy` L3 keyed animCurve 证据和 Unreal Animation Bridge import L3；角色线已有 Character Calibration Maya L3。
- Presenter Pack 把所有关键证据汇总成 reviewer 可读的发布包。

当前稳定展示包：

```text
public-case-package/DCC_FIRST_PACKAGE.md
public-case-package/dcc-first-package-manifest.json
dcc-hosts/maya-auroraview-host/artifacts/r26-character-calibration-l3-presentation-pack-20260805-175238.json
```

## 2. 当前完成度

稳定基线：R26。

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
- Animation Continuity Lab Maya L3
- Unreal Animation Bridge import L3
- Character Calibration Studio Maya L3
- Blender Rule Adapter L3
- 3ds Max Rule Adapter L3
- Maya command bridge
- 轻量验证脚本 `scripts/validate_loop.ps1`

仍缺：

- Maya GUI 9 张 PNG 和 1 段 MP4，留到最后人工采集。
- MotionBuilder、Houdini、Spatial Authoring、Unreal animation fact deepening、Character Calibration UI drilldown 等后续工具线。

## 3. R26 当前断点

`Animation Continuity Lab` 已完成首轮闭环：L2 contract smoke、Maya `mayapy` L3 keyed animCurve collector、Presenter Pack 接入、public manifest 接入和模块文档。

`Unreal Animation Bridge` 已完成 import L3 闭环：读取 R23 Maya L3 artifact，生成 public Maya FBX clips，通过 UnrealEditor-Cmd 进入公开 test `.uproject`，导入并采集 Skeleton / SkeletalMesh / AnimSequence runtime facts。

`Character Calibration Studio` 已完成 Maya L3 闭环：生成 public synthetic character mesh / joint DAG / calibration attrs，采集 topology signature、joint coverage、skin influence budget、calibration delta、face params、Control Rig mapping 和 mirror pair coverage。

核心文件：

```text
dcc-hosts/animation-continuity-lab/fixtures/synthetic_animation_scene.json
dcc-hosts/animation-continuity-lab/animation_continuity_lab/contract.py
dcc-hosts/animation-continuity-lab/animation_continuity_lab/maya_collector.py
dcc-hosts/animation-continuity-lab/scripts/run_smoke.py
dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py
dcc-hosts/animation-continuity-lab/scripts/run_maya_l3.py
dcc-hosts/unreal-animation-bridge/fixtures/synthetic_unreal_animation_bridge.json
dcc-hosts/unreal-animation-bridge/unreal_animation_bridge/contract.py
dcc-hosts/unreal-animation-bridge/scripts/run_smoke.py
dcc-hosts/unreal-animation-bridge/scripts/run_l3_smoke.py
dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py
dcc-hosts/unreal-animation-bridge/scripts/generate_maya_fbx_fixture.py
dcc-hosts/unreal-animation-bridge/scripts/unreal_python/probe_animation_runtime.py
dcc-hosts/unreal-animation-bridge/scripts/unreal_python/import_animsequence_fixture.py
dcc-hosts/character-calibration-studio/fixtures/synthetic_character_calibration_scene.json
dcc-hosts/character-calibration-studio/character_calibration_studio/contract.py
dcc-hosts/character-calibration-studio/character_calibration_studio/maya_collector.py
dcc-hosts/character-calibration-studio/scripts/run_smoke.py
dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py
dcc-hosts/character-calibration-studio/scripts/run_maya_l3.py
```

已生成首个 L2 artifact：

```text
dcc-hosts/animation-continuity-lab/artifacts/animation-continuity-contract-20260805-160346.json
```

当前 L3 artifact：

```text
dcc-hosts/animation-continuity-lab/artifacts/animation-continuity-maya-l3-20260805-162744.json
```

当前 R23 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r23-animation-continuity-l3-presentation-pack-20260805-163040.json
```

当前 Unreal Animation Bridge import L3：

```text
dcc-hosts/unreal-animation-bridge/artifacts/unreal-animation-bridge-import-l3-20260805-173309.json
```

当前 Character Calibration Maya L3：

```text
dcc-hosts/character-calibration-studio/artifacts/character-calibration-maya-l3-20260805-175057.json
```

当前 R26 Presenter Pack：

```text
dcc-hosts/maya-auroraview-host/artifacts/r26-character-calibration-l3-presentation-pack-20260805-175238.json
```

这条线的最终效果：

- 检查动画交付中的 rig identity、skeleton fingerprint、Take range、sample rate、required channel coverage。
- 检查 sub-frame keys、channel identity collision、root motion policy、scale drift、active additive layers。
- 通过 Maya `mayapy` 生成真实 keyed animCurve runtime evidence。
- Unreal 侧已接入 import L3；后续可继续补 MotionBuilder 或更细的 Unreal curve/compression facts。

继续开发时优先做 Spatial Authoring & Pose Transfer Workbench，或深化 Character Calibration UI drilldown。如果只验证当前 R26，运行：

```powershell
python dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py
python dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py
python dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py
```

当前 R26 public package 为 `ai-tool-ta-dcc-first-showcase-r26` / `dcc-first-package@1.23.0`，Presenter Pack 23 / 23 evidence files present，0 missing required files，15 demo route steps；Character Calibration 已到 `L3` / `maya_character_calibration_collected`，1 Ready / 1 Blocked。gate 仍为 `CapturePending`，只因为 Maya GUI media 还没采集。

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
