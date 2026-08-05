# 一.问题反馈

用户要求长期循环开发，不在完成一个闭环后暂停。本轮从 R25 Unreal Animation Bridge import L3 继续推进到角色业务线：Character Calibration & Intent Transfer Studio。

# 二.⭐回顾分析

Lightbox 高价值角色线的关键经验是：角色工具不能只证明“自动生成/迁移成功”，必须先证明 topology、joint coverage、face parameters、Control Rig mapping、calibration delta 等业务语义仍可信。否则 DNA、blendshape、wrap、Control Rig 和引擎侧角色表现都会在后续环节放大错误。

R26 首轮目标选择 Maya `mayapy` L3，而不是先做 UI。原因是当前作品集需要继续补真实 DCC runtime 证据：程序化生成 public synthetic character mesh / joint DAG / custom attrs，再从 Maya 场景采集事实，最后输出机器可审计 artifact。

# 三.改动解释

新增模块：

- `dcc-hosts/character-calibration-studio/fixtures/synthetic_character_calibration_scene.json`
- `dcc-hosts/character-calibration-studio/character_calibration_studio/contract.py`
- `dcc-hosts/character-calibration-studio/character_calibration_studio/maya_collector.py`
- `dcc-hosts/character-calibration-studio/scripts/run_smoke.py`
- `dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py`
- `dcc-hosts/character-calibration-studio/scripts/run_maya_l3.py`

已接入：

- `scripts/validate_loop.ps1` 新增 `character-calibration` 档位。
- Maya Presenter Pack 新增 Character Calibration evidence probe、summary 字段和第 15 步 demo route。
- public manifests / package docs / module docs / AI handoff / 技术报告已同步 R26。

核心证据：

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r26-character-calibration-l3-presentation-pack-20260805-175238.json
```

# 四.计划&状态

R26 当前结果：

- public package：`ai-tool-ta-dcc-first-showcase-r26` / `dcc-first-package@1.23.0`
- Presenter Pack：23 / 23 evidence files present，0 missing required files，15 demo route steps
- Character Calibration：`L3` / `maya_character_calibration_collected`
- Maya runtime：2026
- character rows：2
- assets ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：10 / 2 / 6

已验证：

```powershell
python dcc-hosts\character-calibration-studio\scripts\run_smoke.py
python dcc-hosts\character-calibration-studio\scripts\run_l3_smoke.py
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

下一轮入口：`Spatial Authoring & Pose Transfer Workbench`，先做 socket / hotspot / pose frame / mirror transfer public fixture、Maya collector、rule evaluation 和 Presenter Pack 接入。GUI 截图/录屏继续留到最后人工采集。
