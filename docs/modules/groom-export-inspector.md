# Groom Export Inspector

R46 目标：把 Lightbox 提炼出的 XGen / groom 到 Unreal 高价值链路从计划推进到 Maya runtime L3 证据，覆盖 root UV、strand ID、guide curve、Alembic payload 和 Unreal Groom / Binding intent。

## 核心业务逻辑

Groom 不是普通 mesh 导出。头发资产出问题时，常见失败不是模型拓扑，而是下游无法稳定绑定和复现：

- 每根 strand 是否有稳定 ID，便于 cache diff 和错误定位。
- root UV 是否存在且在 [0,1] 范围，保证 Unreal Binding 能把毛发根部贴回 scalp。
- guide curve 是否随导出保留，避免插值发束失去作者控制。
- Alembic payload 是否明确包含 root UV / strand ID / guide curve。
- Unreal Groom、Binding、SkeletalMesh、material slot 是否已声明。
- 临时 description / TMP groom 是否被拦截在 owner review。

## 当前实现

代码入口：

- `dcc-hosts/groom-export-inspector/fixtures/synthetic_groom_export_scene.json`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/contract.py`
- `dcc-hosts/groom-export-inspector/groom_export_inspector/maya_collector.py`
- `dcc-hosts/groom-export-inspector/scripts/run_smoke.py`
- `dcc-hosts/groom-export-inspector/scripts/run_l3_smoke.py`
- `dcc-hosts/groom-export-inspector/scripts/run_maya_l3.py`

R46 已完成：

- L2 contract：2 个 public-safe groom rows，1 Ready，1 intentionally Blocked。
- Maya L3：Maya 2026 `mayapy` 创建 synthetic scalp planes 和 curve strands，再从 Maya 场景回读 root UV、strand ID、guide flag、Alembic export payload 和 Unreal binding intent。
- Presenter Pack 接入：R46 Presenter Pack 探测 Groom Export Inspector Maya L3 artifact，并把 demo route 扩到 35 步。
- public manifest 接入：公开包升级到 `ai-tool-ta-dcc-first-showcase-r46` / `dcc-first-package@1.43.0`。

## 证据

当前 Maya L3 artifact：

```text
<repo>\dcc-hosts\groom-export-inspector\artifacts\groom-export-inspector-maya-l3-20260806-003711.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r46-groom-export-inspector-presentation-pack-20260806-004101.json
```

关键结果：

- report version：`groom-export-inspector-maya-l3@0.1.0`
- evidence level：L3
- l3 status：`maya_groom_export_facts_collected`
- Maya runtime：2026
- assets ready / review / blocked：1 / 0 / 1
- strands / guides：11 / 2
- root UV missing / duplicate strand IDs：1 / 1
- checks pass / warning / error：11 / 2 / 7
- owner actions：9
- assetWrites / productionWrites：0 / 0

Gate 为 `Blocked` 是正确状态：`Hero Hair Approved` Ready；`Hero Hair Temporary Groom` 保留 TMP description、缺 root_uv scalp set、duplicate strand ID、missing root UV、guide 缺失、Alembic payload flags 缺失、frame range 错误和 Unreal binding intent 缺失。

## 后续

下一阶段可以继续做：

- Groom Unreal Import Readiness：用 Unreal Python / Editor Utility 检查 Groom 插件、GroomAsset / GroomBindingAsset API 和 public import readiness。
- Groom Alembic Executor：在 public temp/cache 边界内生成 `.abc` payload receipt，再做 import/post-check/rollback。
