# 一.问题反馈

用户要求长期循环开发不要停在非手动边界，并强调作品集要继续围绕 Lightbox 高价值业务逻辑推进 DCC / 引擎内可展示工具，而不是堆前端说明。R35 选择角色业务线中已经有 Maya L3 runtime facts 的 Character Calibration，补一层 Maya/AuroraView 可消费的业务 drilldown。

# 二.⭐回顾分析

R26 Character Calibration Maya L3 已能生成并采集 public synthetic character mesh / joint DAG / skin / calibration attrs / face params / Control Rig mapping / mirror pair coverage。已有问题是 evidence 仍偏 flat rule rows，reviewer 需要看到“一个角色为什么被放行/阻断”的分面解释、owner action 和 fix preview。这个缺口适合做 L3-derived artifact：不重复跑重型 Maya，不伪造成新的 runtime 成功，而是把既有 Maya runtime facts 组织成展示层 contract。

# 三.改动解释

新增 `character_calibration_studio/drilldown.py` 和 `scripts/run_drilldown.py`。脚本读取 `character-calibration-maya-l3-20260805-175057.json`，输出 `character-calibration-drilldown@0.1.0` artifact：2 个 character drilldowns、14 个 panels，覆盖 topology、skeleton、skin、calibration、face、Control Rig、mirror；生成 8 条 owner actions，其中 6 条 owner-required、2 条 manual-review，并明确 productionWrites=0。

Maya AuroraView Presenter Pack 新增 Character Calibration Drilldown evidence probe、summary 字段、reviewer claim 和 demo route，public package 升级为 `ai-tool-ta-dcc-first-showcase-r35` / `dcc-first-package@1.32.0`。同步更新 public package、模块文档、AI_HANDOFF、长期循环策略和技术报告。

# 四.计划&状态

R35 artifact：`dcc-hosts/character-calibration-studio/artifacts/character-calibration-drilldown-20260805-202259.json`。R35 Presenter Pack：`dcc-hosts/maya-auroraview-host/artifacts/r35-character-calibration-drilldown-presentation-pack-20260805-202448.json`，32 / 32 evidence present，0 missing，24 demo route steps。验证已完成：R35 drilldown 脚本已直接运行生成 artifact，新增 Python 文件和 Maya host API 已通过 `py_compile`，两个 manifest、R35 drilldown artifact、R35 Presenter Pack 均通过 `python -m json.tool`，`.\scripts\validate_loop.ps1 -Tier quick` 和 `.\scripts\validate_loop.ps1 -Tier package` 均通过。下一轮默认进入 Spatial Authoring Drilldown，把 socket / hotspot / pose transfer Maya L3 rows 投影成 UI-ready panels、owner actions 和 fix previews；Maya GUI 9 张截图和 1 段录屏继续留到最后集中处理。
