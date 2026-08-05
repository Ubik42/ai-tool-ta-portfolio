# 一.问题反馈

用户要求长期循环开发，不在只剩人工 Maya GUI 采集前停下。本轮延续 Lightbox 高价值业务线：角色工具不能只看 Control Rig 控件是否存在，还要证明控件对应的 deformation target 能在引擎 Skeleton 上闭环。

# 二.⭐回顾分析

R43 的 `Unreal Control Rig Deformation Link` 已证明 `CR_HeroFace` 有 5 个 runtime controls，但 approved 行仍缺 `Eye_L`、`Eye_R`、`Jaw` 的 Skeleton target match。这个 blocker 不是 UI 问题，而是角色绑定交付中最容易误判的业务点：控件存在不等于变形链路可交付。

R44 选择 public face Skeleton fixture 作为闭环任务：用 Maya 2026 `mayapy` 生成可公开的 face Skeleton FBX，再让 Unreal 5.3.2 导入 public fixture asset，复跑 bridge 和 deformation-link，确认 R43 的 Eye/Jaw target 缺口是否真实解决。

# 三.改动解释

新增 `unreal_control_rig_bridge/face_skeleton_fixture.py`、`generate_face_skeleton_fbx.py`、`run_face_skeleton_fixture.py` 和 Unreal import 脚本。`contract.py` 的 public expected targets 切到 `/Game/AI_Tool_TA/Characters/SK_HeroFace` / `SK_HeroFace_Skeleton`，`run_deformation_link.py` 改为优先读取最新 bridge artifact。

Presenter Pack 接入 `unreal-control-rig-face-skeleton-fixture` evidence probe，demo route 增至 33 步。`public-case-package` manifest、README、DCC_FIRST_PACKAGE、EVIDENCE_INDEX、VALIDATION、MODULES 和模块文档同步到 `ai-tool-ta-dcc-first-showcase-r44` / `dcc-first-package@1.41.0`。

# 四.计划&状态

R44 结果：Face Skeleton Fixture 为 L3 / `Review`，required target matches 4 / 4，previous R43 missing resolved 3 / 3，assetWrites=2，productionWrites=0。复跑 Deformation Link 后 approved 行从 Blocked 推进到 Review，runtime controls 5，Skeleton target matches 5，shape/offset-readable controls 5，13 pass / 2 warning / 5 error，assetWrites=0。

当前 Presenter Pack：`dcc-hosts/maya-auroraview-host/artifacts/r44-unreal-control-rig-face-skeleton-fixture-presentation-pack-20260805-235700.json`，42/42 evidence files present，0 missing required files，33 demo route steps。下一轮入口：Control Rig direct compile status bridge，或转 gameplay attach fixture / Groom Export Inspector。
