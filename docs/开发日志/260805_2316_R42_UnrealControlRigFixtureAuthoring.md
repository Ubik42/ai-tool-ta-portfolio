# 一.问题反馈

用户要求长期循环开发不能停在计划或前端展示，必须继续推进 DCC / 引擎内可证明的工具管线能力。R41 后最有价值缺口是 Character Calibration 角色线的 Unreal Control Rig public asset fixture / runtime hierarchy。

# 二.⭐回顾分析

R37 已经证明 Unreal 5.3.2 Python 能进入 public `.uproject`，ControlRig / RigVM API 可见，`SK_Hero` 和 Skeleton binding 存在，但 `/Game/AI_Tool_TA/Characters/CR_HeroFace` 缺失，approved 角色行因此被 Blocked。R42 的价值不是继续写 readiness 说明，而是尝试受控创建 CR fixture，并用 post-authoring bridge 证明业务状态变化。

# 三.改动解释

新增 `unreal_control_rig_bridge/fixture_authoring.py`、`scripts/run_fixture_authoring.py` 和 `scripts/unreal_python/author_control_rig_fixture.py`。Unreal harness 只选择 approved public 角色行，通过 `ControlRigBlueprintFactory` / `AssetTools` 创建 `CR_HeroFace`，用 `RigHierarchyController.add_control` 写入 `CTRL_brow_L`、`CTRL_brow_R`、`CTRL_eye_L`、`CTRL_eye_R`、`CTRL_jaw`，保存 1 个 public fixture asset，并保持 productionWrites=0。

复跑 `run_l3_smoke.py` 后，approved `char-hero-head-001` 从 R37 的 missing CR asset 变成 Ready；TMP 行继续 Blocked。已接入 Maya Presenter Pack、`scripts/validate_loop.ps1`、public package manifest / README / evidence / validation、AI_HANDOFF、DCC-first case page、Control Rig 模块文档和 Lightbox 覆盖报告。当前 public package 升级到 `ai-tool-ta-dcc-first-showcase-r42` / `dcc-first-package@1.39.0`，Presenter Pack 为 40 / 40 evidence files present、0 missing required files、31 demo route steps。

# 四.计划&状态

R42 artifacts：

```text
dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-fixture-authoring-20260805-230323.json
dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-bridge-l3-20260805-230343.json
dcc-hosts/maya-auroraview-host/artifacts/r42-unreal-control-rig-fixture-authoring-presentation-pack-20260805-230853.json
```

当前结果：fixture authoring L3 / `Ready` / `unreal_control_rig_fixture_authoring_collected`，1 selected / 1 held，created/saved assets 1 / 1，required/runtime/missing controls 5 / 5 / 0，assetWrites=1，productionWrites=0；post-authoring bridge L3 / `Blocked`，approved 行 Ready，TMP 行 Blocked，10 pass / 1 warning / 5 error，assetWrites=0。下一轮优先做 Control Rig deformation target link / compile status，或转向 gameplay attach fixture / Groom Export Inspector。
