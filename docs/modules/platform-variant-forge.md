# Platform Variant Forge

R28-R33 目标：把 PC -> Mobile 平台派生从“规则检查”推进到可交付的 variant plan 证据，用 Unreal runtime facts 验证计划是否真的落进引擎，把 runtime drift 转成 dry-run generation operations，并补上材质贴图链路、真实 public Texture2D payload 和受控执行 / 回滚 evidence。

## 核心业务逻辑

平台派生的难点不是改几个数字，而是判断哪些降级可以自动计划，哪些会改变视觉、玩法或引擎地址，必须由 owner 批准：

- 目标路径是否进入平台专属目录。
- Mobile 是否超 triangle、texture memory、material slots、draw calls。
- 需要的 LOD 链是否完整。
- Nanite、clearcoat、parallax、detail normal 这类 PC 特性是否泄漏到 Mobile。
- collision 是否从复杂碰撞变成合规 simple shapes。
- 派生计划是否关联已有 Unreal preset fact comparison，而不是孤立生成。
- Unreal 里实际生成/复制出来的 StaticMesh variant 是否符合计划，而不是只在 JSON 里“看起来通过”。
- 检测到 drift 后，哪些操作可自动执行，哪些因为缺源资产、缺几何/贴图事实或 owner approval 必须停住。
- 材质槽是否真的能追到 Unreal material dependency / Texture2D payload，而不是只在计划里写了 texture budget。

## 当前实现

代码入口：

- `dcc-hosts/platform-variant-forge/fixtures/synthetic_platform_variant_plan.json`
- `dcc-hosts/platform-variant-forge/platform_variant_forge/contract.py`
- `dcc-hosts/platform-variant-forge/platform_variant_forge/runtime_contract.py`
- `dcc-hosts/platform-variant-forge/platform_variant_forge/generation_plan.py`
- `dcc-hosts/platform-variant-forge/platform_variant_forge/texture_runtime.py`
- `dcc-hosts/platform-variant-forge/platform_variant_forge/controlled_executor.py`
- `dcc-hosts/platform-variant-forge/scripts/run_smoke.py`
- `dcc-hosts/platform-variant-forge/scripts/run_unreal_runtime_probe.py`
- `dcc-hosts/platform-variant-forge/scripts/run_generation_plan.py`
- `dcc-hosts/platform-variant-forge/scripts/run_texture_runtime_probe.py`
- `dcc-hosts/platform-variant-forge/scripts/run_texture_payload_probe.py`
- `dcc-hosts/platform-variant-forge/scripts/run_controlled_executor.py`
- `dcc-hosts/platform-variant-forge/scripts/unreal_python/probe_variant_runtime.py`
- `dcc-hosts/platform-variant-forge/scripts/unreal_python/collect_texture_runtime.py`
- `dcc-hosts/platform-variant-forge/scripts/unreal_python/execute_controlled_variant.py`

R28 首版完成：

- 2 个 public-safe source assets，3 个 platform variants。
- 1 个 PC Ready variant、1 个 Mobile Ready variant、1 个 intentionally Blocked Mobile variant。
- 规则覆盖 source evidence join、target path、owner approval、triangle/texture/material/draw budgets、LOD coverage、Nanite policy、shader feature policy、collision policy。
- 报告会读取现有 Unreal preset fact comparison artifact，证据等级为 `L3-linked`，但本轮不新增 Unreal 写入。

R29 runtime probe 完成：

- 通过 `UnrealEditor-Cmd.exe` 进入公开 test `.uproject`。
- 在 `/Game/AI_Tool_TA` 公开 fixture 范围内确认/生成计划中的 PC / Mobile StaticMesh runtime assets。
- 采集 runtime path、LOD count、material slot、Nanite state、collision simple shape 等事实。
- 对照 R28 variant plan 输出 3 variants：0 Ready，2 Review，1 intentionally Blocked。
- 规则结果为 21 pass / 4 warning / 2 error；Blocked 来自临时车辆样本，Review 来自 hero panel runtime LOD/Nanite drift。

R30 generation planner 完成：

- 读取 R29 runtime drift 和 R28 plan，生成 dry-run generation contract。
- 操作覆盖 missing LOD、Nanite policy、material merge、texture downscale、collision simplification、source import 和 target variant creation。
- 输出 11 operations：1 Ready、3 Review、2 Blocked、5 Satisfied。
- 每个 operation 带 owner approval、deterministic params、Unreal Python preview、writeSet、rollback preview 和 productionWrite=false。
- Gate 仍为 `Blocked`，原因是 synthetic vehicle source/target 缺失；HeroPanel LOD / texture bake 留在 Review，因为当前 public runtime fixture 的几何/贴图 facts 不足以执行 destructive bake。

R31 texture runtime collector 完成：

- 通过 `UnrealEditor-Cmd.exe` 进入同一个公开 test `.uproject`。
- 对计划里的 source / PC target / Mobile target StaticMesh 采集 material slots、material paths、Asset Registry dependency query、material expression texture references、Texture2D 尺寸/估算内存/压缩/sRGB/readability。
- 输出 3 variants：1 Ready，1 Review，1 intentionally Blocked。
- 规则结果为 19 pass / 1 warning / 1 error；Mobile HeroPanel 的 warning 现在明确是“材质链已采集，但 synthetic material 没有真实 Texture2D payload”，不再是 collector 缺失。
- assetWrites=0；本轮没有新增 Unreal 资产写入。

R32 public Texture2D payload fixture 完成：

- 通过 `run_texture_payload_probe.py` 打开同一个公开 Unreal test project。
- 运行时生成 public 2048 PNG，导入为 `/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor`，并挂到 `M_HeroPanel`。
- 重新采集 StaticMesh -> material -> Texture2D facts，Mobile HeroPanel 的 texture downscale 从 Review 进入可计算预算对照。
- 输出 3 variants：2 Ready，0 Review，1 intentionally Blocked；规则结果为 20 pass / 0 warning / 1 error。
- 最终提交的幂等 rerun 为 assetWrites=0；fixture 缺失时的写入范围也只限 `/Game/AI_Tool_TA` public fixture，不写生产工程资产。

R33 controlled executor 完成：

- 读取 R30 generation plan 和 R32 texture payload artifact。
- 选择 HeroPanel Mobile texture downscale 中可在 public fixture 内执行的 max texture size clamp。
- 记录 preflight fingerprint，执行 maxTextureSize `0 -> 2048`，保存 public Texture2D，采集 post-state。
- 立刻 rollback 到 `0`，确认最终 fingerprint 回到 `2502b08c541495a4`。
- 输出 gate `Ready`，1 executed operation，1 post-check pass，1 rollback pass，7 pass / 0 warning / 0 error，persistentMutation=false。

## 证据

当前 artifact：

```text
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-forge-contract-20260805-183315.json
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-unreal-runtime-20260805-185026.json
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-generation-plan-20260805-190052.json
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-runtime-20260805-191529.json
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-texture-payload-runtime-20260805-193515.json
<repo>\dcc-hosts\platform-variant-forge\artifacts\platform-variant-controlled-executor-20260805-200810.json
```

## 后续

下一步可以把 executor 扩到 LOD / Nanite / collision 的 approval receipts，或转向 Character Calibration / Spatial Authoring 的 Maya UI drilldown 与 Unreal 对照。
