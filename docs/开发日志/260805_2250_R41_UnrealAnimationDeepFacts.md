# 一.问题反馈

R25 已经证明 Maya FBX 能进入 Unreal 并生成 public Skeleton / SkeletalMesh / AnimSequence，但证据还偏“资产存在”。R41 的任务是补动画交付最容易被忽略的 engine-side metadata：duration、frame span、frame-rate、curve、root motion 和 compression visibility。

# 二.⭐回顾分析

这轮不再重复导入 FBX。高价值点是把“导入成功”拆成“运行时事实是否可审计”：AnimSequence 存在不等于曲线、root motion、compression 都能被工具判断。R41 选择 read-only collector，避免为了演示制造新的 Unreal 写入。

# 三.改动解释

新增 `unreal_animation_bridge/deep_facts.py`、`scripts/run_deep_facts.py` 和 `scripts/unreal_python/collect_animsequence_deep_facts.py`。collector 通过 UnrealEditor-Cmd 打开 public `.uproject`，读取 R25 已存在的两个 AnimSequence，导出 play length、derived frame span、direct frame-rate、curve metadata API、root motion settings、compression settings 和 read-only write boundary。

已接入 Maya Presenter Pack、`scripts/validate_loop.ps1`、public package manifest / README / evidence / validation、AI_HANDOFF、DCC-first case page、Unreal Animation Bridge 模块文档和 Lightbox 覆盖报告。当前 public package 升级到 `ai-tool-ta-dcc-first-showcase-r41` / `dcc-first-package@1.38.0`，Presenter Pack 为 39 / 39 evidence files present、0 missing required files、30 demo route steps。

# 四.计划&状态

R41 artifacts：

```text
dcc-hosts/unreal-animation-bridge/artifacts/unreal-animation-deep-facts-20260805-224206.json
dcc-hosts/maya-auroraview-host/artifacts/r41-unreal-animation-deep-facts-presentation-pack-20260805-224616.json
```

当前结果：L3 / `Blocked` / `unreal_animsequence_deep_facts_collected`，2 runtime rows，2 / 2 duration frame spans matched，0 Ready / 1 Review / 1 Blocked，15 pass / 2 warning / 1 error，assetWrites=0。下一轮优先做 public Control Rig asset fixture / runtime hierarchy。
