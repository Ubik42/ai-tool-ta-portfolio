# 一.问题反馈

R9.5 已把 Texture Delivery 接入 Maya material / texture inspection。下一轮选择 `Task Orchestrator`，因为作品集需要一个 DCC 内的生产队列入口，把前面几个模块从单点工具串成可解释的批处理状态流。

# 二.⭐回顾分析

Task Orchestrator 的业务秘诀是状态一致性，而不是“按钮集合”：

- 从 Maya scene 发现可处理资产。
- 把每个资产的 protocol、material、texture、visual review、evidence export 变成 task rows。
- dry-run 阶段记录命令、依赖、状态和 evidence，不修改场景。
- per-asset receipt 把任务结果转成 Ready / Review / Blocked 的交付结论。
- 导出 report，作为后续接真实 adapter、蓝盾/工蜂/引擎导入的稳定边界。

# 三.改动解释

Maya host:

- 在 `ai_tool_ta_maya_host/api.py` 新增 `task_orchestrator_create_fixture`、`task_orchestrator_discover_scene`、`task_orchestrator_build_queue`、`task_orchestrator_run_dry_run`、`task_orchestrator_export_report`。
- batch fixture 创建 2 个 assets：ready asset 带 protocol/material/file node，review asset 故意缺 protocol/material/texture。
- scene discovery 采集 mesh、protocol、material、texture node、triangle budget、visible state、review/blocker。
- queue build 为每个 asset 生成 5 类 dry-run tasks：Protocol、Material、Texture、Visual、Export。
- dry-run 输出 task events 和 per-asset receipts，mutation 始终为 false。
- export 输出 `maya-task-orchestrator-dcc-report@1.0.0`。

前端:

- 在 `auroraviewBridge.ts` 注册 5 个 Task Orchestrator Maya API。
- 在 `TaskOrchestratorWorkbench.tsx` 新增 `Maya Batch Queue` 面板，提供 `Create Fixture`、`Discover Scene`、`Build Queue`、`Dry Run`、`Export Report` 五个动作。
- 面板展示 assets、queue tasks、receipts、gate 和 raw JSON。
- 在 `styles.css` 增加面板样式和移动端收敛。

文档:

- 更新根 README 当前 DCC-first 状态。
- 更新 `docs/260803_DCC-first长期开发计划与环境.md`。
- 更新 `dcc-hosts/maya-auroraview-host/README.md`。
- 更新 `docs/modules/task-orchestrator.md`。

# 四.计划&状态

验证结果：

- `npm run build` 通过，仅保留既有 Vite 大 chunk 警告。
- `python -m py_compile ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` smoke 通过：
  - fixture nodes：2
  - discovered assets：2
  - discovery gate：Review
  - task count：10
  - queue gate：Review
  - dry-run gate：Review
  - dry-run events：10
  - receipts：2
  - artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-6-task-orchestrator-smoke-20260803-161017.json
```

下一轮自主推进：

- R9.7 GUI 证据收束：为已完成 DCC 模块准备 Maya 内点击清单、截图/录屏脚本和最终演示路径。
