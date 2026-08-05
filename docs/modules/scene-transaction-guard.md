# Scene Transaction Guard

## 核心业务逻辑

Scene Transaction Guard 解决的是 DCC 工具最容易被忽略的风险：工具执行后到底改了什么。专业 TA 工具不能只给成功提示，还要把 scene state 的变化边界、风险行和回滚预案交给 reviewer。

R19 的最小闭环放在 Maya 内完成：

- 执行前捕获 scoped scene state：节点、父子关系、关键 transform / visibility / camera attr、selection、current time。
- 执行一个 synthetic mutation：创建 collision proxy、删除 obsolete proxy、移动并隐藏 hero body、修改 review camera focal length、切换 selection/time。
- 执行后再次捕获 scene state，并计算 before / after fingerprint。
- 输出 created / deleted / modified / context changed 的 diff。
- 把 diff 投影成 risk rows 和 rollback preview，而不是只把 mutation 藏在工具内部。

这条线来自 Lightbox 类工具常见的“确定性、可审计、可回滚”业务经验：DCC 插件越接近批量发布、资产修复和引擎交付，越需要证明工具的写入边界。

## 当前实现

代码入口：

- `dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
- `showcases/portfolio-site/src/components/DccFirstCasePage.tsx`
- `showcases/portfolio-site/src/lib/auroraviewBridge.ts`

Maya API：

- `scene_transaction_create_fixture`
- `scene_transaction_capture_state`
- `scene_transaction_run_guard`
- `scene_transaction_export_receipt`

React 入口：

- `Task Orchestrator` evidence view / `Txn Guard`
- `Scene Transaction Guard` receipt panel
- Presenter Pack summary / `Scene Txn`

## 当前验证

- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py` 通过。
- Maya 2024 `mayapy` scene transaction smoke 通过：
  - report version：`maya-scene-transaction-guard@0.1.0`
  - gate：`Review`
  - before fingerprint：`8d096c2e9a7dccca`
  - after fingerprint：`e048ce005ffd65c3`
  - created / deleted / modified：2 / 2 / 2
  - selection changed：true
  - time changed：true
  - rollback actions：9
  - risk rows：4
- R19 Presenter Pack smoke 通过：
  - evidence files：16 / 16
  - missing required files：0
  - demo route steps：10
  - scene transaction gate：`Review`

## 当前 artifact

Scene Transaction Guard：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-20260804-195730.json
```

R19 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r19-scene-transaction-guard-presentation-pack-20260804-195754.json
```

## 下一步

- 把相同 transaction capture 迁移到 Blender adapter，验证跨 DCC scene mutation receipt。
- 在 Maya GUI 录屏里展示 `Txn Guard` 按钮、risk rows 和 rollback preview，让该能力成为作品集中的可信执行亮点。
