# 一.问题反馈

R51 的 controlled executor 已经进入 Unreal 真实导入，但 `.abc` 被 `AlembicImportFactory` 导成 `StaticMesh`，没有形成 `GroomAsset`，因此也无法创建 `GroomBindingAsset`。这说明上一轮证明了执行器边界和 rollback，但还没真正穿透 Groom 业务链路。

# 二.⭐回顾分析

R52 聚焦一个高价值管线判断：毛发工具不能只检查 Maya 曲线数量、Alembic 文件存在、Unreal 插件可见。真正的生产风险在于 Alembic schema 和 Unreal importer mode 是否匹配 HairStrands。资产根节点导出会把头部 mesh 一起带进 `.abc`，UE 容易走 StaticMesh 路径；面向 Groom 的交付必须是 curve-only cache，并且在引擎里验证导入结果 class。

本轮把链路拆成三段证据：Maya 导出 curve-only Alembic 并回读 schema；Unreal post-check 看到 `HairStrandsFactory` 和目标 SkeletalMesh；controlled executor 真导入、创建 binding、检查结果、再 rollback。

# 三.改动解释

- `groom_export_inspector/alembic_payload.py` 升级到 `groom-alembic-payload@0.2.0`，支持 `curve_only` export mode，导出后用 Maya `AbcImport` 回读 schema，记录 `meshShapeRows`、`curveShapeRows`、`schemaCompatibleRows` 和 cache hash。
- `maya_collector.py` 和 `synthetic_groom_export_scene.json` 补齐 Groom 标准属性与头部网格范围，让测试毛发根点、宽度、guide、group 等信息更接近真实交付。
- Unreal post-check 和 controlled executor 增加 `HairStrandsFactory` 探测，优先走 HairStrands/Groom importer 路径。
- controlled executor 修正 binding 调用，把目标 SkeletalMesh 同时作为 transfer source，记录 `GroomAsset`、`GroomBindingAsset`、commandlet log signal、rollback 和残留资产检查。
- Maya AuroraView Presenter Pack、public case package、README、AI_HANDOFF、模块文档、技术报告和验证入口同步到 R52。

# 四.计划&状态

R52 关键 artifact：

- `dcc-hosts/groom-export-inspector/artifacts/groom-alembic-payload-20260806-030023.json`
- `dcc-hosts/groom-export-inspector/artifacts/groom-alembic-import-postcheck-20260806-030028.json`
- `dcc-hosts/groom-export-inspector/artifacts/groom-controlled-executor-20260806-030046.json`
- `dcc-hosts/maya-auroraview-host/artifacts/r52-groom-hair-schema-executor-presentation-pack-20260806-030427.json`

当前包：`ai-tool-ta-dcc-first-showcase-r52` / `dcc-first-package@1.49.0`。Presenter Pack 为 50 / 50 evidence files present，0 missing required files，40 demo route steps，media gate 仍是 `CapturePending`。

R52 结果：Maya payload 为 L3 / `maya_groom_curve_only_alembic_payload_exported`，`exportMode=curve_only`，`schemaCompatibleRows=1`，`meshShapeRows=0`，`curveShapeRows=1`。Unreal executor 为 L3 / `Ready` / `unreal_groom_executor_import_binding_rolled_back`，导入 class=`GroomAsset`，binding 创建成功，rollback 成功，residual assets=0，assetWrites=6，engineWrites=0，productionWrites=0，persistentMutation=false。

已跑验证：`python -m py_compile`、关键 artifact `python -m json.tool`、`git diff --check`、`.\scripts\validate_loop.ps1 -Tier package`。下一轮入口：继续做非手动 runtime 闭环，优先从 Unreal socket authoring executor 或 Control Rig deformation link 里选一个，把当前 Blocked/Review 项推进到可执行 receipt。
