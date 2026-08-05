# 一.问题反馈

本轮继续长期开发，不停在 Maya 手动 GUI 采集点。R52 已把 Groom 线推进到 Unreal `HairStrandsFactory` import / BindingAsset / rollback Ready，下一条高价值业务线选择 3ds Max 材质贴图交付检查：把真实 `pymxs` material bitmap slot facts 与交付 manifest、channel 语义、色彩空间和平台预算做 join。

开发中发现 `scripts/validate_loop.ps1 -Tier package` 的 Presenter Pack smoke 仍硬编码 R52 label、50 个证据和 40 步 route。R53 代码本身已返回 51/51 和 41 步，但验证脚本误报失败，需要同步断言。

# 二.⭐回顾分析

Lightbox 高价值点不是“DCC 能跑”，而是把发布事实转成业务 gate：资产在 DCC 里用了哪些材质槽、槽里有哪些贴图、交付包里是否覆盖这些贴图、BC/N/ORM 语义是否齐全、normal/orm 是否 linear、Mobile 预算是否低于 PC。这比单纯扫描文件路径更接近真实管线 TA 的审包逻辑。

R53 的 synthetic fixture 保留一个 Ready 和一个 Blocked：`max-prop-001` 的 BC/N/ORM 全齐且符合 PC 2048 预算；`max-hero-002` 的 Mobile 包只有 BC，缺 normal/orm，且 4096 超过 Mobile 2048 上限。这样 reviewer 能同时看到干净路径和阻断路径。

# 三.改动解释

- `dcc-hosts/3dsmax-rule-adapter/max_rule_adapter/contract.py`：在 Max runtime raw facts 中加入 `materialTextureRows`，记录 node、LOD、materialName 和 slot textures。
- `dcc-hosts/3dsmax-rule-adapter/max_rule_adapter/texture_manifest_link.py`：新增 `max-texture-manifest-link@0.1.0`，把 Max L3 runtime artifact 与 `synthetic_texture_delivery_manifest.json` 做只读 join，输出 asset facts、evaluation rows、owner actions 和 zero-write boundary。
- `dcc-hosts/3dsmax-rule-adapter/scripts/run_texture_manifest_link.py`：新增 CLI，自动选择最新 `max-rule-adapter-pymxs-l3@0.1.0` artifact 并导出 link report。
- `dcc-hosts/3dsmax-rule-adapter/fixtures/synthetic_texture_delivery_manifest.json`：新增 public-safe 贴图交付 manifest fixture。
- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`：Presenter Pack 接入 `maxTextureManifestLinkArtifact`，demo route 增加 Max texture manifest link 步骤，reviewer claims 加入 R53 业务结论。
- `public-case-package/*`、`README.md`、`docs/AI_HANDOFF.md`、`docs/modules/3dsmax-rule-adapter.md`、两份技术报告：同步 R53 当前基线、证据索引、验证结果和后续入口。
- `scripts/validate_loop.ps1`：增加 `max-texture-manifest-link` tier，并把 package Presenter Pack smoke 更新为 R53 label、51 evidence files、41 demo route steps。

# 四.计划&状态

R53 正式证据：
- Max L3 runtime：`dcc-hosts/3dsmax-rule-adapter/artifacts/max-rule-adapter-l3-20260806-032411.json`
- Max texture manifest link：`dcc-hosts/3dsmax-rule-adapter/artifacts/max-texture-manifest-link-20260806-032426.json`
- Presenter Pack：`dcc-hosts/maya-auroraview-host/artifacts/r53-max-texture-manifest-link-presentation-pack-20260806-032705.json`
- Public package：`ai-tool-ta-dcc-first-showcase-r53` / `dcc-first-package@1.50.0`

R53 结果：`max_material_texture_manifest_linked`，L3-derived / `Blocked`，2 assets，1 Ready / 1 Blocked，materialRows=3，slotTextures=4，manifestTextures=4，missingManifestTextures=0，missingRequiredSemantics=2，13 pass / 1 warning / 2 error，assetWrites=0，engineWrites=0，productionWrites=0。

验证已通过：
- `python -m py_compile dcc-hosts\3dsmax-rule-adapter\max_rule_adapter\contract.py dcc-hosts\3dsmax-rule-adapter\max_rule_adapter\texture_manifest_link.py dcc-hosts\3dsmax-rule-adapter\scripts\run_texture_manifest_link.py dcc-hosts\maya-auroraview-host\ai_tool_ta_maya_host\api.py`
- `python -m json.tool`：R53 fixture、Max link artifact、Presenter Pack、两个 public package manifest
- `.\scripts\validate_loop.ps1 -Tier max-texture-manifest-link`
- `.\scripts\validate_loop.ps1 -Tier package`
- `git diff --check`

不提交的临时输出：早期失败/旧源 artifact `max-texture-manifest-link-20260806-032329.json`、`max-texture-manifest-link-20260806-032342.json`，以及验证脚本重复生成的 `max-texture-manifest-link-20260806-033732.json`。下一轮优先进入 gameplay attach fixture、Houdini 非 Maya adapter 或 Control Rig Editor Utility / C++ diagnostic bridge；Maya GUI 截图/录屏仍留到最后集中采集。
