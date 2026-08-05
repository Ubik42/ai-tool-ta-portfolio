# Texture Delivery Console

R4 目标：把 `texture_to_engine_reference`、`substance_delivery_reference`、`photoshop_dds_reference`、`spritesheet_reference`、`substance_shader_reference` 这类贴图交付工具的经验，抽象成公开可运行的通道打包与平台交付控制台。

## 方法来源

- `texture_to_engine_reference`
- `substance_delivery_reference`
- `photoshop_dds_reference`
- `spritesheet_reference`
- `substance_shader_reference`

## 核心业务秘诀

贴图工具的价值不是把 PNG 转 DDS，而是把交付约束集中到一个可复盘合同里：

- 命名解析：从 `<asset>_<set>_<role>_<resolution>` 里拿到 asset、texture set、role、resolution。
- 通道打包：ORM / mask / sprite atlas 不是文件列表，而是 channel contract。
- 颜色空间：BaseColor / Emissive 走 sRGB，Normal / mask / Roughness / Metallic / AO 走 linear。
- 平台 profile：PC、mobile、console 的最大尺寸、压缩格式、package budget 和 import root 不一样。
- 长任务队列：pack、compress、manifest、engine sync 都要能记录状态、命令、耗时、失败和重试边界。
- AI 只总结 deterministic risk，不能替代平台预算和通道缺失的硬规则。

## 当前实现

代码入口：

- `showcases/portfolio-site/src/data/textureDelivery.ts`
- `showcases/portfolio-site/src/components/TextureDeliveryConsole.tsx`
- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`

R4.1 已实现：

- 3 个 synthetic texture fixtures：干净 ORM weapon、mobile overbudget vehicle、UI sprite sheet。
- 3 个 packing presets：`UE ORM BC`、`Mobile Mask ASTC`、`Sprite Atlas PNG`。
- 3 个 platform profiles：`PC DX12`、`Mobile ASTC`、`Switch Lite`。
- source naming parser：识别 asset token、texture set、role token、resolution token，并输出 warning。
- channel packing plan：按 preset 生成 BaseColor、Normal、ORM / Mask / Atlas 输出。
- output manifest：输出 format、compression、colorspace、mipmap、texture group、估算大小和 import path。
- risk gate：检查命名、颜色空间、缺失通道、平台尺寸、power-of-two、package budget。
- queue runner mock：`Dry Run`、`Submitted`、`Processing`、`Completed`、`Failed` 五种状态。
- AI risk brief：把 deterministic risk 汇总成 TA / artist 可读说明。
- report JSON：`texture-delivery-report@0.1.0`。

## 当前规则设计

| 规则 | 业务目的 |
| --- | --- |
| Naming parser | 保证贴图能被批量识别、打包和写入 manifest |
| Channel contract | 固定 RGB/A 与 Roughness / Metallic / AO / Opacity 的映射 |
| Colorspace gate | 阻断 Normal sRGB、mask sRGB 这类引擎表现问题 |
| Platform max size | 阻断移动端或低配平台不接受的超大贴图 |
| Power-of-two check | 发现 mipmap 和 block compression 风险 |
| Package budget | 把平台内存预算变成交付门禁 |
| Queue state | 保留长任务的命令、耗时、状态和失败原因 |

## AI 边界

AI 在这个模块里只做风险解释：

- 总结 deterministic risks。
- 把 queue 失败和平台风险转成 TA / artist 可读说明。
- 根据 preset 和 platform 描述交付影响。

AI 不改变 compression，不补 missing channel，不覆盖 package budget。

## R9.5 Maya Texture Inspection

R9.5 把 R4 的前端交付模型接到 Maya 场景上下文里：

- Maya API：`texture_delivery_create_fixture`、`texture_delivery_inspect_scene`、`texture_delivery_validate_scene`、`texture_delivery_export_manifest`。
- React 面板：`Maya Texture Inspection`。
- fixture：创建 synthetic mesh、Lambert material、shadingEngine，以及 BaseColor / Normal / ORM 三个 file texture nodes。
- inspection：读取 mesh、material、shadingEngine、file node、贴图路径、role、resolution、colorSpace。
- validation：执行 Material Binding、Texture Source Paths、Texture Role Naming、Texture Color Space、Texture Platform Budget。
- manifest：导出 `maya-texture-delivery-dcc-report@1.0.0`。

验证结果：

- `npm run build` 通过。
- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` smoke 通过：fixture file nodes 3，inspection sources 3，validation rows 5，gate `Review`。
- smoke artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-5-texture-delivery-smoke-20260803-160419.json
```

## 当前证据

- `assets/texture-delivery-r4-1-console-full.png`
- `assets/texture-delivery-r4-1-mobile-tall.png`
- `assets/texture-delivery-r4-1-exported-report.json`

## 浏览器验证

R4.1 验证目标：

- 打开 `Texture Delivery Console`，默认 `Rifle ORM Pack` 使用 `UE ORM BC` 和 `PC DX12`，gate 为 `Ready`。
- 切到 `Vehicle Mobile Overbudget` 后，gate 变为 `Blocked`，risk 包含平台尺寸和 colorspace 问题。
- 点击 `Processing` 后 queue summary 出现 running task。
- 点击 `Failed` 后 queue summary 出现 failed task。
- 导出 report：`reportVersion=texture-delivery-report@0.1.0`，包含 `packedOutputs`、`risks`、`queueTasks`、`importManifest`。

## R4.7 Public Fixture Approved Delta

R7.3 把 R4 从 adapter dry-run 继续推进到公开可复查的交付 delta：

- 新增 `public_crate_orm` 公开合成贴图 fixture，sourceRoot 和 targetRoot 都在 `<repo>/fixtures/public_texture_crate` 下。
- `texture-delivery-report@0.7.0` 增加 `approvedPackageDelta` 和 `committedManifest`。
- baseline package 为 `approved-public-crate-body-1.0.0`，当前 frozen manifest 与它对比得到 1 个新增、1 个变更、1 个不变文件。
- queue 切到 `Completed` 后，package deterministic gate 为 `Ready`，publish/delta gate 仍为 `Review`，因为新增和变更文件需要 Texture TA 签收。
- committed manifest 状态为 `review_required`，明确只有 manifest 中列出的文件可由外部 adapter 写入；AI 只能总结和路由 receipt。

新增证据：

- `assets/texture-delivery-r4-7-public-fixture-delta-full.png`
- `assets/texture-delivery-r4-7-mobile-tall.png`
- `assets/texture-delivery-r4-7-exported-report.json`
- `assets/texture-delivery-r4-7-committed-manifest.json`

验证结果：

- `npm run build`
- CSS constraint scan
- Playwright desktop/mobile no horizontal overflow
- exported report validation: `fixtureId=public_crate_orm`, `queueMode=completed`, `reportVersion=texture-delivery-report@0.7.0`
- delta validation: added 1, changed 1, unchanged 1, blocked 0, `fixtureScope=portfolio_public_synthetic`
- manifest validation: `texture-committed-manifest@0.1.0`, status `review_required`, fileCount 3

## 下一轮

R7.4 状态：

- R4 `accept-texture-r4` 已在 `owner-signoff-ledger@0.1.0` 中签收。
- 签收范围：public fixture delta、committed manifest 和 external adapter mutation boundary。
- 证据入口：`assets/portfolio-case-study-r7-4-exported-report.json`。

下一轮：

- 进入 R7.5 public case package。
- R8 从扩展线选择一个更复杂的资产依赖 / 发布影响分析工具。

