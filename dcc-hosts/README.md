# DCC Hosts

这里放作品集的 DCC / 引擎宿主层。React 前端不再是最终主展示载体；它会被嵌入 Maya 等 DCC 中，作为工具 UI 和证据面板。

当前主线：

```text
maya-auroraview-host/
blender-rule-adapter/
3dsmax-rule-adapter/
unreal-handoff-inspector/
```

目标是先在 Maya 中用 AuroraView `QtWebView` 加载 portfolio 前端，再逐步把 Asset Protocol、Cross-DCC Rule Matrix、Visual Review 和 Texture Delivery 做成真实 DCC 工具闭环。

`blender-rule-adapter` 是当前第一条非 Maya 证据线：用公开 synthetic fixture 把 Blender 的 object custom properties、collections、material slots、UV 和 collision proxy 归一化为 Cross-DCC Rule Matrix 的规则输入。当前为 L2 contract artifact，本机缺 Blender CLI，后续安装 Blender 后升级为 `blender --background --python` L3 smoke。

`3dsmax-rule-adapter` 是 R21 新增的非 Maya 证据线：用公开 synthetic fixture 把 3ds Max 的 user properties、layer/export root、LOD suffix、material slot、map channel、transform 和 collision proxy 归一化为 Cross-DCC Rule Matrix 输入。本机已发现 `C:\Program Files\Autodesk\3ds Max 2022\3dsmaxbatch.exe`，当前默认只导出 L2+ contract 和 opt-in L3 readiness；真实 `pymxs` batch smoke 需要显式运行 `scripts\run_l3_smoke.py --run-runtime`。

`unreal-handoff-inspector` 是当前第一条 engine-side 证据线：用公开 synthetic fixture 把 DCC import intent 放到 Unreal Content Registry / AssetImportTask 语义下检查。当前已通过 `UnrealEditor-Cmd.exe -run=pythonscript` 跑通 L3++ smoke，公开 test project 内生成 `SM_HeroPanel_A` StaticMesh 和 `M_HeroPanel` Material，并从 StaticMesh 读取 source import data、material slot、LOD count 和 collision settings 四类 engine facts。R17 继续把这些 facts 接到 PC / Mobile preset policy 和 exception waiver，输出 10 条 matched / drift / waived / blocked 证据行。
