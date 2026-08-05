# DCC Hosts

这里放作品集的 DCC / 引擎宿主层。React 前端不再是最终主展示载体；它会被嵌入 Maya 等 DCC 中，作为工具 UI 和证据面板。

当前主线：

```text
maya-auroraview-host/
blender-rule-adapter/
3dsmax-rule-adapter/
unreal-handoff-inspector/
animation-continuity-lab/
unreal-animation-bridge/
```

目标是先在 Maya 中用 AuroraView `QtWebView` 加载 portfolio 前端，再逐步把 Asset Protocol、Cross-DCC Rule Matrix、Visual Review 和 Texture Delivery 做成真实 DCC 工具闭环。

`blender-rule-adapter` 是当前第一条非 Maya 证据线：用公开 synthetic fixture 把 Blender 的 object custom properties、collections、material slots、UV 和 collision proxy 归一化为 Cross-DCC Rule Matrix 的规则输入。R22 已通过 Blender 5.2.0 LTS `bpy` L3 runtime smoke，导出 `blender-rule-adapter-bpy-l3@0.1.0`。

`3dsmax-rule-adapter` 是 R21/R22 的非 Maya 证据线：用公开 synthetic fixture 把 3ds Max 的 user properties、layer/export root、LOD suffix、material slot、map channel、transform 和 collision proxy 归一化为 Cross-DCC Rule Matrix 输入。R22 已通过 3ds Max 2022 `pymxs` L3 runtime smoke，导出 `max-rule-adapter-pymxs-l3@0.1.0`。

`unreal-handoff-inspector` 是当前第一条 engine-side 证据线：用公开 synthetic fixture 把 DCC import intent 放到 Unreal Content Registry / AssetImportTask 语义下检查。当前已通过 `UnrealEditor-Cmd.exe -run=pythonscript` 跑通 L3++ smoke，公开 test project 内生成 `SM_HeroPanel_A` StaticMesh 和 `M_HeroPanel` Material，并从 StaticMesh 读取 source import data、material slot、LOD count 和 collision settings 四类 engine facts。R17 继续把这些 facts 接到 PC / Mobile preset policy 和 exception waiver，输出 10 条 matched / drift / waived / blocked 证据行。

`animation-continuity-lab` 是 R23 新增的动画业务证据线：用 public synthetic animation fixture 和 Maya `mayapy` 创建 keyed transforms / animCurves，采集 rig identity、skeleton fingerprint、take range、sample rate、required channel coverage、channel collision、sub-frame keys、root motion、scale drift 和 additive layer facts。当前已导出 `animation-continuity-maya-l3@0.1.0`，后续扩 MotionBuilder / Unreal Animation Bridge。

`unreal-animation-bridge` 是 R24 新增的动画到引擎证据线：读取 R23 Maya Animation Continuity L3 artifact，把 Maya take facts 映射到 Unreal AnimSequence / Skeleton / root motion / curve / compression 预期，并通过 Unreal Python runtime 做只读 readiness probe。当前为 `unreal-animation-bridge-readiness@0.1.0`：Unreal 5.3.2 可见 `AnimSequence`、`AnimSequenceFactory`、`Skeleton`、`SkeletalMesh` API，但公开项目尚未提交 AnimSequence/Skeleton fixture，因此 gate 正确保持 `Blocked`。
