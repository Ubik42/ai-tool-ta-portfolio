# 一.问题反馈

R9.4 已把 Visual Review 接入 Maya camera rig / pass manifest。下一轮选择 `Texture Delivery Console`，因为贴图交付是工具管线 TA 非常核心的业务线：它连接 DCC 材质图、文件命名、色彩空间、平台预算和引擎导入 manifest。

# 二.⭐回顾分析

Texture Delivery 的业务秘诀不是格式转换，而是把贴图源和交付规则绑定到场景上下文：

- 从 Maya mesh、shadingEngine、material、file node 还原交付事实。
- 从文件名推导 role 和 resolution。
- 用 role 决定 expected colorSpace。
- 把 missing path、unknown role、colorSpace mismatch、platform max size 变成可复查 gate。
- 导出 manifest，作为后续 engine import adapter 或外部打包器的稳定输入。

# 三.改动解释

Maya host:

- 在 `ai_tool_ta_maya_host/api.py` 新增 `texture_delivery_create_fixture`、`texture_delivery_inspect_scene`、`texture_delivery_validate_scene`、`texture_delivery_export_manifest`。
- fixture 创建 synthetic mesh、Lambert material、shadingEngine、BaseColor / Normal / ORM 三个 file texture nodes。
- inspection 采集 meshes、materials、file texture nodes、路径、role、resolution、colorSpace。
- validation 执行 5 条规则：Material Binding、Texture Source Paths、Texture Role Naming、Texture Color Space、Texture Platform Budget。
- export 输出 `maya-texture-delivery-dcc-report@1.0.0`。

前端:

- 在 `auroraviewBridge.ts` 注册 4 个 Texture Delivery Maya API。
- 在 `TextureDeliveryConsole.tsx` 新增 `Maya Texture Inspection` 面板，提供 `Create Fixture`、`Inspect Textures`、`Validate Scene`、`Export Manifest` 四个动作。
- 面板展示 source rows、validation rows、gate、artifact path 和 raw JSON。
- 在 `styles.css` 增加面板样式和响应式收敛。

文档:

- 更新根 README 当前 DCC-first 状态。
- 更新 `docs/260803_DCC-first长期开发计划与环境.md`。
- 更新 `dcc-hosts/maya-auroraview-host/README.md`。
- 更新 `docs/modules/texture-delivery-console.md`。

# 四.计划&状态

验证结果：

- `npm run build` 通过，仅保留既有 Vite 大 chunk 警告。
- `python -m py_compile ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` smoke 通过：
  - fixture file nodes：3
  - inspection sources：3
  - validation gate：Review
  - validation rows：5
  - artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r9-5-texture-delivery-smoke-20260803-160419.json
```

下一轮自主推进：

- R9.6 Task Orchestrator DCC 化：把模块从前端证据链迁移成 Maya 内批处理队列入口，能发现 scene assets、生成任务、运行 dry-run、输出 batch report。
