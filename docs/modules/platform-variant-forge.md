# Platform Variant Forge

R28 目标：把 PC -> Mobile 平台派生从“规则检查”推进到可交付的 variant plan 证据。

## 核心业务逻辑

平台派生的难点不是改几个数字，而是判断哪些降级可以自动计划，哪些会改变视觉、玩法或引擎地址，必须由 owner 批准：

- 目标路径是否进入平台专属目录。
- Mobile 是否超 triangle、texture memory、material slots、draw calls。
- 需要的 LOD 链是否完整。
- Nanite、clearcoat、parallax、detail normal 这类 PC 特性是否泄漏到 Mobile。
- collision 是否从复杂碰撞变成合规 simple shapes。
- 派生计划是否关联已有 Unreal preset fact comparison，而不是孤立生成。

## 当前实现

代码入口：

- `dcc-hosts/platform-variant-forge/fixtures/synthetic_platform_variant_plan.json`
- `dcc-hosts/platform-variant-forge/platform_variant_forge/contract.py`
- `dcc-hosts/platform-variant-forge/scripts/run_smoke.py`

R28 首版完成：

- 2 个 public-safe source assets，3 个 platform variants。
- 1 个 PC Ready variant、1 个 Mobile Ready variant、1 个 intentionally Blocked Mobile variant。
- 规则覆盖 source evidence join、target path、owner approval、triangle/texture/material/draw budgets、LOD coverage、Nanite policy、shader feature policy、collision policy。
- 报告会读取现有 Unreal preset fact comparison artifact，证据等级为 `L3-linked`，但本轮不新增 Unreal 写入。

## 证据

当前 artifact：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-forge-contract-20260805-183315.json
```

## 后续

下一步可以接 Unreal runtime probe，读取实际 StaticMesh LOD/material/collision/texture import facts，对照 variant plan 生成更强的 L3++ 变体报告。
