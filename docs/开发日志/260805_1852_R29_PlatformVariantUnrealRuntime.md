# 一.问题反馈

继续长期循环开发，优先推进 DCC / 引擎内真实 runtime 证据。R28 已把 PC/Mobile 平台变体规则做成 plan contract，本轮目标是把这个 plan 接到 Unreal runtime，验证计划中的资产是否真实存在、路径是否符合平台策略，以及 LOD / Nanite / collision / material slot 等引擎事实是否满足业务规则。

# 二.⭐回顾分析

Lightbox 高价值点里，平台差异化不是单纯导出两个文件，而是同一业务资产在 PC / Mobile / 临时资产状态下经过 owner、路径、预算、降级策略和引擎实际状态的综合判断。R28 只有 L3-linked 计划证据，本轮补上 UnrealEditor-Cmd + Unreal Python 的运行时采集，让 Presenter Pack 可以展示“计划通过但引擎事实仍需 Review”的真实管线逻辑。

R29 runtime 结果：

```text
artifact: dcc-hosts/platform-variant-forge/artifacts/platform-variant-unreal-runtime-20260805-185026.json
presenter: dcc-hosts/maya-auroraview-host/artifacts/r29-platform-variant-unreal-runtime-presentation-pack-20260805-185113.json
package: ai-tool-ta-dcc-first-showcase-r29 / dcc-first-package@1.26.0
runtime: UnrealEditor-Cmd 5.3 / public test project
summary: 3 variants, 0 Ready, 2 Review, 1 Blocked, 21 pass / 4 warning / 2 error
presenter evidence: 26/26 present, 0 missing required, 18 demo route steps
```

两个 HeroPanel 变体已经在 Unreal runtime 中存在，但因为 runtime LOD 数不足、PC Nanite policy 未满足而进入 Review；Vehicle TMP 变体保持 Blocked，用来展示缺失源资产和目标资产时的业务阻断。

# 三.改动解释

新增 `platform_variant_forge.runtime_contract`，负责读取 R28 plan artifact 与 Unreal runtime JSON，生成 runtime-vs-plan comparison、review actions 和 evidence summary。

新增 `scripts/run_unreal_runtime_probe.py` 与 `scripts/unreal_python/probe_variant_runtime.py`：前者定位 UnrealEditor-Cmd / public project 并启动无 GUI 采集，后者在 Unreal Python 内读取 StaticMesh、material slot、LOD、Nanite 和 collision facts。采集范围限定在 `/Game/AI_Tool_TA` public fixture。

更新 Maya AuroraView Presenter Pack API，把 R29 runtime artifact 接入证据探针、摘要字段、reviewer claims 和 demo route。同步更新 public package manifest、Evidence Index、Validation、AI handoff、module 文档和长期计划文档。

# 四.计划&状态

已验证：

```powershell
.\scripts\validate_loop.ps1 -Tier platform-variant-unreal
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
```

下一轮默认推进 `Platform Variant Auto LOD / Material Bake Planner`：读取 R29 runtime drift，生成 LOD / Nanite / material bake / texture downgrade 的修复计划和 Unreal generation contract，把平台变体从“检测问题”推进到“给出可执行生成策略”。
