# 一.问题反馈

R42 已经能在 Unreal public project 里创建 `CR_HeroFace`，并写入 5 个 required runtime controls。但这还停在“控件存在”层，不能证明 Control Rig 已经真正能驱动目标 Skeleton，也不能说明 compile status 是否能被当前 Python API 直接读取。

# 二.⭐回顾分析

高价值业务点是角色绑定交付门禁：TA 工具不能只检查 UI 控件名字，要把 Maya `controlRigMappings`、Unreal Control Rig hierarchy、deformation target、Skeleton bone coverage 和 compile API surface 串起来。R43 因此选择 read-only deformation-link collector，不继续做前端卡片。

# 三.改动解释

新增 `unreal_control_rig_bridge.deformation_link`、`scripts/run_deformation_link.py` 和 Unreal Python collector `collect_control_rig_deformation_link.py`。Collector 读取 R42 post-authoring bridge、fixture authoring artifact、`CR_HeroFace`、`SK_Hero_Skeleton` 和 Maya control rig mappings，导出 `<repo>\dcc-hosts\unreal-control-rig-bridge\artifacts\unreal-control-rig-deformation-link-20260805-232729.json`。

Presenter Pack 接入 R43：`r43-unreal-control-rig-deformation-link-presentation-pack-20260805-233308.json`，41/41 evidence files present，0 missing required files，32 demo route steps。Public manifest、DCC_FIRST_PACKAGE、模块文档和工程报告同步到 `ai-tool-ta-dcc-first-showcase-r43` / `dcc-first-package@1.40.0`。

# 四.计划&状态

R43 状态：L3 / `Blocked` / `unreal_control_rig_deformation_link_collected`。结果为 2 character rows，10 control links，5 runtime controls，5 shape/offset-readable controls，2 Skeleton target matches，0 direct compile-status rows，12 pass / 2 warning / 6 error，assetWrites=0，productionWrites=0。

下一轮入口：优先做 Control Rig direct compile status bridge 或 public face skeleton fixture，让 `Eye_L`、`Eye_R`、`Jaw` 这类 deformation target 能在 public Skeleton 上闭环；也可转 gameplay attach fixture 或 Groom Export Inspector。
