# 一.问题反馈

继续执行 DCC-first 作品集循环开发。R10.8 的目标是把 R10.7 的 engine handoff mock 推进到真正可解释的预检层：Ready intent 不能直接等同于引擎可导入，必须经过平台 preset、路径、LOD、预算、协议和 receipt 检查。

# 二.⭐回顾分析

R10.7 已经把 owner / engine decision 纳入主线，但 reviewer 仍只能看到 import intent。真实工具管线里，engine handoff 还需要回答：目标路径是否合法、平台规则是否匹配、预算是否越界、是否有被 owner hold 的资产混进导入包。R10.8 因此新增 preflight packet，只生成 dry-run sidecar，不执行 Unreal 或引擎写入。

# 三.改动解释

- Maya host 新增 `engine_handoff_build_preflight_packet` 和 `engine_handoff_export_preflight_packet`。
- 当前 PC Unreal preset 检查 engine path、platform、LOD、triangle budget、texture budget、protocol carrier 和 receipt state。
- `AssetHandoffGatePanel` 新增 `Engine Preflight` 按钮，展示 preflight rows 和 import sidecar。
- `auroraviewBridge` 已把两个 preflight API 加入方法白名单。
- public package 升级为 `ai-tool-ta-dcc-first-showcase-r10-8` / `dcc-first-package@1.6.0`，并加入 engine preflight artifact。

最新 artifact：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r10-8-engine-handoff-preflight-fixture-20260803-172302.json
```

# 四.计划&状态

已验证：

- `python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py`
- `npm run build`
- Maya 2024 `mayapy` engine preflight smoke：2 preflight rows，1 preflight-ready，1 held，1 import sidecar，8 pass checks，1 hold check，0 engine writes。

下一轮自动推进：

1. R10.9：PC / Mobile engine preflight preset 对比。
2. R10.10：owner disposition drill，展示 owner-required / waiver / held / ready 的业务边界。
3. R10.11：真实 Maya GUI evidence 采集和 media audit 回填。
