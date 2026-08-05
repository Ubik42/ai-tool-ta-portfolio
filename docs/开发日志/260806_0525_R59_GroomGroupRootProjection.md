# 一.问题反馈

用户要求长期循环开发作品集，优先推进 Lightbox 高价值业务逻辑，不把 DCC/引擎工具做成纯前端说明。R58 已闭环 Max controlled repair，下一轮需要选择新的业务价值点并继续产出 DCC runtime 证据。

# 二.⭐回顾分析

Groom 线已有 Maya root UV / strand ID / guide / Alembic payload、Unreal readiness、curve-only `.abc`、controlled GroomAsset / BindingAsset executor 和 runtime fact collector。还缺更细的业务门禁：发丝根点是否真的落回 scalp `root_uv`、group 是否覆盖 guide、group 与 UV region / material slot / Alembic payload 是否一致。

这个点是 Groom/XGen 发布的核心风险：`.abc` 文件存在、GroomAsset 能创建，并不代表分组、根点和引擎材质路由正确。

# 三.改动解释

- 新增 `synthetic_groom_group_projection_scene.json`，包含 approved groom 和 TMP blocked groom 两类 public fixture。
- 新增 `groom_export_inspector/group_root_projection.py`，在 Maya runtime 中从 curve root CV 投影到 scalp root UV 平面，输出 strand projection rows、group coverage rows、material routing、Alembic group payload 和 owner boundary。
- 新增 `run_group_root_projection.py` / `run_maya_group_root_projection.py`，支持普通 Python 调 mayapy，也支持 Maya 内采集。
- 更新 groom collector / contract，保留 `groupId`、`groupName`、`materialSlot` 和完整 groom raw payload，保证 downstream checker 能读到真实业务语义。
- 更新 Maya AuroraView Presenter Pack、public manifests、README、模块文档、技术报告和 evidence / validation index。

# 四.计划&状态

R59 artifact：`dcc-hosts/groom-export-inspector/artifacts/groom-group-root-projection-20260806-051721.json`。

R59 Presenter Pack：`dcc-hosts/maya-auroraview-host/artifacts/r59-groom-group-root-projection-presentation-pack-20260806-052010.json`。

结果：L3 / `Blocked` / `maya_groom_group_root_projection_collected`，2 assets，1 Ready / 1 Blocked，10 strand projection rows，4 group coverage rows，projectionMatchedStrands=6，groupMatchedStrands=7，materialMatchedStrands=8，maxProjectionDrift=0.175，assetWrites=0，engineWrites=0，productionWrites=0。

下一轮入口：优先做 Control Rig Editor Utility / C++ diagnostic bridge、socket C++ / Editor Utility adapter、MotionBuilder adapter 或 Animation Blueprint Library / C++ adapter；Maya GUI 截图/录屏留到最后集中采集。
