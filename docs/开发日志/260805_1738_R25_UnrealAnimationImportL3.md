# 一.问题反馈

用户要求长期循环开发，不在每个闭环后暂停；本轮继续推进 Lightbox 高价值动画交付线，把 R24 的 Unreal Animation Bridge 从 L3-readiness 升级到真实 import L3。

# 二.⭐回顾分析

R24 只证明 Unreal Python 能进入 public test project 并探测 AnimSequence / Skeleton API，但当时没有 public skeletal animation fixture。R25 的关键业务价值是补上 DCC -> engine 的真实链路：Maya keyed animCurve evidence 不停在 DCC 侧，而是生成 public FBX，通过 Unreal commandlet 导入 Skeleton / SkeletalMesh / AnimSequence，再用 runtime facts 反查是否真的进了引擎。

当前 `Blocked` gate 不是导入失败。`RunStart` 已 Ready；`Attack_A` 继续保留 rig fingerprint、sample rate、frame range、curve coverage、sub-frame、root motion 等业务故障，作为 reviewer 能看到的阻断样本。

# 三.改动解释

新增 Unreal Animation Bridge import L3 harness：

- `dcc-hosts/unreal-animation-bridge/scripts/generate_maya_fbx_fixture.py`：Maya 2026 `mayapy` + `fbxmaya` 现场生成两段 public synthetic FBX。
- `dcc-hosts/unreal-animation-bridge/scripts/unreal_python/import_animsequence_fixture.py`：Unreal Python 使用 `AssetImportTask` + `FbxImportUI` 导入，并把临时目录里的 `SkeletalMesh`、`Skeleton`、`AnimSequence` 重命名到 fixture 期望路径。
- `dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py`：自动找 `mayapy` 和 `UnrealEditor-Cmd.exe`，串起 FBX 生成、Unreal 导入、日志和 JSON artifact。
- `unreal_animation_bridge/contract.py`：新增 `unreal-animation-bridge-import-l3@0.1.0` 证据层级，区分 L2 contract、L3-readiness、L3 import success / attempt。
- Presenter Pack / public manifests / public package docs / module docs 已升级到 R25。

核心证据：

```text
<repo>\dcc-hosts\unreal-animation-bridge\artifacts\unreal-animation-bridge-import-l3-20260805-173309.json
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r25-unreal-animation-import-l3-presentation-pack-20260805-173624.json
```

# 四.计划&状态

R25 当前结果：

- public package：`ai-tool-ta-dcc-first-showcase-r25` / `dcc-first-package@1.22.0`
- Presenter Pack：22 / 22 evidence files present，0 missing required files，14 demo route steps
- Unreal Animation Bridge：`L3` / `unreal_animsequence_assets_imported`
- Unreal runtime：5.3.2 / Python 3.9.7
- expected sequences：2 / 2 present
- imported assets：4 synthetic assets
- assets ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：12 / 1 / 5

已验证：

```powershell
python -m py_compile dcc-hosts\unreal-animation-bridge\unreal_animation_bridge\contract.py dcc-hosts\unreal-animation-bridge\scripts\generate_maya_fbx_fixture.py dcc-hosts\unreal-animation-bridge\scripts\run_import_l3_smoke.py dcc-hosts\unreal-animation-bridge\scripts\unreal_python\import_animsequence_fixture.py
python dcc-hosts\unreal-animation-bridge\scripts\run_import_l3_smoke.py
python dcc-hosts\unreal-animation-bridge\scripts\run_smoke.py
python dcc-hosts\unreal-animation-bridge\scripts\run_l3_smoke.py
Maya mayapy dcc_presentation_export_pack(label="r25-unreal-animation-import-l3-presentation-pack")
```

下一轮入口：`Character Calibration & Intent Transfer Studio`，先做 topology / joint coverage / calibration delta 的 public fixture、Maya collector、rule evaluation 和 Presenter Pack 接入。GUI 截图/录屏继续留到最后人工采集。
