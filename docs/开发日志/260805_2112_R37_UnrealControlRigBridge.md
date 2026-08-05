# 一.问题反馈

本轮继续长期循环开发，目标不是补前端卡片，而是把 Lightbox 高价值角色业务线继续接到引擎 runtime。R35 已经把 Character Calibration Maya L3 rows 投影成 Maya/AuroraView drilldown，但还缺一层 Unreal 侧 Control Rig / Skeleton / SkeletalMesh 对照，无法证明“DCC 里角色映射通过后，引擎是否真的可接管”。

# 二.⭐回顾分析

选择 `Unreal Control Rig Bridge` 作为 R37 闭环任务。它读取 `character-calibration-drilldown-20260805-202259.json` 和对应 Maya L3 source facts，通过 UnrealEditor-Cmd 进入 public `AI_Tool_TA_Unreal_L3.uproject`，采集 ControlRig / RigVM API、Asset Registry、SkeletalMesh / Skeleton binding 和 expected Control Rig asset path facts。该线覆盖的是工具管线 TA 里的角色 handoff 门禁：source mapping、engine API、engine binding、runtime control coverage 需要分层判定。

# 三.改动解释

新增 `dcc-hosts/unreal-control-rig-bridge` 模块：`contract.py` 负责归一化 Character Drilldown 到 Unreal bridge evaluation，`run_smoke.py` 生成普通 Python contract artifact，`run_l3_smoke.py` 调用 UnrealEditor-Cmd，`probe_control_rig_bridge.py` 在 Unreal Python 内采集 Control Rig API 与资产事实。public Unreal `.uproject` 启用 `ControlRig` plugin。

Maya Presenter Pack 接入 R37：新增 `unreal-control-rig-bridge` evidence probe、summary 字段、reviewer claim 和 demo route 第 12 步；默认导出 label 升为 `r37-unreal-control-rig-bridge-presentation-pack`。public manifests、Evidence Index、Validation、DCC-first package、MODULES、AI_HANDOFF、模块文档和技术报告已同步到 R37。

# 四.计划&状态

R37 已完成。最终 L3 artifact 为 `dcc-hosts/unreal-control-rig-bridge/artifacts/unreal-control-rig-bridge-l3-20260805-205656.json`；Presenter Pack 为 `dcc-hosts/maya-auroraview-host/artifacts/r37-unreal-control-rig-bridge-presentation-pack-20260805-205922.json`。

结果：L3 / `Blocked` / `unreal_control_rig_bridge_facts_collected`；Unreal 5.3.2；Control Rig API ready=true；2 character rows，0 Ready，0 Review，2 Blocked；8 pass，1 warning，7 error；1 个 SkeletalMesh/Skeleton binding，0 个 expected Control Rig asset；assetWrites=0，productionWrites=0。Blocked 是正确业务门禁：approved 行缺 `CR_HeroFace`，TMP 行被 Maya 源头缺陷和 Unreal 目标缺失共同阻断。

验证已通过：R37 Python files 和 Maya Host API 的 `py_compile` 通过；两个 public manifest、R37 L3 artifact、R37 Presenter Pack 和 public `.uproject` 均通过 `python -m json.tool`；`.\scripts\validate_loop.ps1 -Tier quick` 通过；`.\scripts\validate_loop.ps1 -Tier package` 通过并输出 `ai-tool-ta-dcc-first-showcase-r37 dcc-first-package@1.34.0 34 0 26`；`git diff --check` 通过；Unreal public test project `Content` 目录没有非预期改动。下一轮默认进入 `Unreal Socket Import Checker`：读取 Spatial Authoring Drilldown，采集 public Unreal Skeleton / socket facts，输出 socket / hotspot / pose transfer 对照、owner actions 和 Presenter Pack row。
