# 一.问题反馈

R46 已经证明 Maya 侧能采集 groom root UV、strand ID、guide curve、Alembic payload 和 Unreal binding intent，但还没有证明这些 groom 行能进入真实 Unreal 导入链路。继续只扩前端或只重复 Maya collector 会偏离 Lightbox 高价值业务点；本轮选择 Groom Unreal Import Readiness，把 R46 的 Maya groom facts 推进到 UE runtime/API 证据。

# 二.⭐回顾分析

Groom 交付的核心风险不是普通 mesh 是否存在，而是 `.abc` cache、GroomAsset、GroomBindingAsset、目标 SkeletalMesh 和 Groom/Alembic import API 是否能在引擎侧对齐。R47 采用 read-only readiness，不导入 Alembic、不保存资产，只证明 Unreal 5.3 public project 是否能看到 AssetImportTask、AlembicImportFactory、GroomAsset / GroomBindingAsset API、目标 `SK_HeroFace` 和预期 Groom / Binding 资产。

# 三.改动解释

新增 `groom_export_inspector/unreal_readiness.py`、`scripts/run_unreal_readiness.py` 和 `scripts/unreal_python/probe_groom_import_readiness.py`。`run_unreal_readiness.py` 复用 UnrealEditor-Cmd 5.3 commandlet 模式，读取 `groom-export-inspector-maya-l3-20260806-003711.json`，进入 public `AI_Tool_TA_Unreal_L3.uproject` 后导出 `groom-unreal-readiness-20260806-010008.json`。

R47 结果为 L3 / `Blocked` / `unreal_groom_import_readiness_collected`：2 groom rows，source Ready / Blocked = 1 / 1，AssetImportTask visible rows = 2，AlembicImportFactory visible rows = 2，target SkeletalMesh present rows = 1，GroomAsset / GroomBindingAsset API visible rows = 0 / 0，expected Groom / Binding assets present = 0 / 0，12 pass / 4 warning / 6 error，10 owner actions，assetWrites=0，productionWrites=0。

Presenter Pack、DCC-first manifest、public package、证据索引、验证索引、模块文档、AI handoff 和技术报告已接入 R47。当前 Presenter Pack 为 `dcc-hosts/maya-auroraview-host/artifacts/r47-groom-unreal-readiness-presentation-pack-20260806-010323.json`，45/45 evidence present，0 missing，36 route steps。

# 四.计划&状态

已完成：真实 Unreal L3 readiness artifact、Maya Presenter Pack 接入、`groom-unreal-readiness` 验证档、public package `ai-tool-ta-dcc-first-showcase-r47` / `dcc-first-package@1.44.0`、public-case-package r8-71 / `public-case-package@3.41.0`。

当前 gate 仍为 `CapturePending`，原因只剩最终 Maya GUI 截图/录屏未采集；R47 的业务 gate `Blocked` 是正确结果，因为 GroomAsset / GroomBindingAsset API 和预期 Groom / Binding 资产缺口不能伪装成已完成。

下一轮入口：优先做 Groom Alembic executor 或 gameplay attach fixture；如果继续 groom 线，应先准备 public-safe `.abc` payload / import receipt / post-check / rollback，不在缺 Groom API 的情况下声称真实资产已导入。
