# 一.问题反馈

用户要求循环任务自主推进开发，并强调作品集最终应在 DCC / 引擎内展示工具能力。上一轮 R9.2 已把 Asset Protocol Workbench 接入 Maya custom attr 写入、Inspect 回读和 DCC evidence report，本轮继续推进高价值业务线：把 Cross-DCC Rule Matrix 从浏览器 fixture 展示推进到 Maya scene 内可跑的 collect / validate / fix preview。

# 二.⭐回顾分析

Cross-DCC Rule Matrix 的核心价值不是“展示规则列表”，而是把 Pyblish 类业务拆成稳定四段：

- Collect：DCC adapter 采集 Maya 私有结构，转成共享 rule input。
- Validate：共享 rule 读取标准事实，产出 status / evidence / gate。
- Fix Preview：只预览安全修复和人工动作边界，不直接破坏场景。
- Extract：把事实、规则结果和修复预览导出成 report artifact。

R9.2 只完成了 Asset Protocol 的 payload 写入和回读。R9.3 需要让 Rule Matrix 自己能够读取 Maya selection，而不是依赖前端静态 asset fixture。

# 三.改动解释

Maya host:

- 在 `ai_tool_ta_maya_host/api.py` 新增 `rule_matrix_collect_scene`、`rule_matrix_validate_scene`、`rule_matrix_preview_fixes`、`rule_matrix_export_report`。
- collect 会读取 selection 或 scene mesh transform，采集 transform、mesh shape、triangles/faces、shadingEngine、parent/root、`aiToolTaProtocol`、schema、LOD、collision、budget。
- validate 实现 6 条规则：Protocol Carrier、Collision Contract、LOD Budget、Material / Texture Sync、Export Root Clean、Publish Manifest。
- preview 生成 `safe_auto` / `manual_only` 修复预览，不改场景。
- export 输出 `maya-rule-matrix-dcc-report@1.0.0`。

前端:

- 在 `auroraviewBridge.ts` 注册 4 个 Rule Matrix Maya API。
- 在 `CrossDccRuleMatrix.tsx` 新增 `Maya Scene Rule Run` 面板，提供 `Collect Scene`、`Validate Scene`、`Preview Fixes`、`Export DCC Report` 四个 DCC 动作。
- 面板展示 facts、validation rows、fix preview、summary gate、artifact path 和原始 JSON payload。
- 在 `styles.css` 补充 DCC rule run 的密集产品 UI 和移动端布局收敛。

文档:

- 更新根 README 当前 DCC-first 状态。
- 更新 `docs/260803_DCC-first长期开发计划与环境.md`。
- 更新 `dcc-hosts/maya-auroraview-host/README.md`。
- 更新 `docs/modules/cross-dcc-rule-matrix.md`。

# 四.计划&状态

验证结果：

- `npm run build` 通过，仅保留既有 Vite 大 chunk 警告。
- `python -m py_compile ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` smoke 通过：
  - fixture nodes：`hero_prop_body1`、`hero_prop_socket1`
  - collect count：2
  - validation rows：6
  - validation gate：Blocked
  - fix preview total：3
  - artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-3-rule-matrix-smoke-20260803-155309.json
```

下一轮自主推进：

- R9.4 Visual Review DCC 化：在 Maya 侧创建 review camera / pass manifest / playblast 或 mock capture，把 Visual Review Studio 从浏览器 fixture 推进到 Maya 场景证据。
