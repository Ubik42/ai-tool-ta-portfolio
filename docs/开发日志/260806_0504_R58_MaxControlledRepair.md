# 一.问题反馈

长期开发继续围绕 Lightbox 高价值业务逻辑推进。R57 已证明 Blender 侧 Fix / post-check / rollback；本轮选择 3ds Max，把同一类 Pyblish-style 修复闭环落到真实 `3dsmaxbatch.exe` / `pymxs` runtime，避免只停在 collect / validate / preview。

# 二.⭐回顾分析

Max 资产交付的高价值点不是单独检查 LOD、贴图或 transform，而是把 user props、layer/export root、LOD suffix、material bitmap slot、map channel、texel density、transform clean、UCX collision 和 vertex color boundary 归一到同一套发布门禁。自动修复必须拆成 receipt：每条变更说明 rule、writeSet、目标值和 rollback 边界，然后 post-check 证明 gate 从 Blocked 到 Ready。

# 三.改动解释

新增 `max-controlled-repair-executor@0.1.0`：3ds Max 2022 batch 从 blocked hero fixture 行出发，执行 UCX collision proxy、LOD1 render node、MI material/texture semantics、UV/map channel cleanup、transform reset/vertex color clear 五条 repair receipt；post-check 得到 2 Ready / 0 Blocked、20 pass / 0 warning / 0 error；随后重建原 fixture，rollback fingerprint 与 preflight 匹配。Maya Presenter Pack、manifest、public docs、Max 模块页、AI_HANDOFF 和验证脚本同步到 R58。

# 四.计划&状态

当前 R58 Presenter Pack 为 `dcc-first-package@1.55.0`，57 / 57 evidence files present，47 demo route steps，gate 仍为 `CapturePending`，只剩 Maya GUI 截图/录屏。下一轮继续选择真实 DCC / 引擎 runtime 任务，优先 MotionBuilder adapter、Control Rig Editor Utility / C++ diagnostic bridge、socket C++ / Editor Utility adapter 或 Groom group/root projection 细分 fixture。
