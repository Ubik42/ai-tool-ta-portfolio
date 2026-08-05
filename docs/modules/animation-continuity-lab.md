# Animation Continuity Lab

R23 目标：把 Lightbox 里动画导出、MotionBuilder 交接、Unreal 动画导入这类“看起来能播但业务不一定正确”的经验，抽象成公开可复现的动画连续性检查工具，并通过真实 Maya `mayapy` 采集 keyed animCurve 事实。

## 核心业务逻辑

动画交付的难点不是有没有曲线，而是跨软件后语义是否还一致：

- 这条 take 是不是来自批准的 rig id 和 skeleton fingerprint。
- 声明的 start/end/sample rate 是否和场景 FPS、实际 key 范围一致。
- 必须存在的 gameplay channel 有没有丢失。
- 多个 namespace / retarget 源是否合并成同一个 normalized channel identity。
- sub-frame key、range 外 key、root motion、scale drift、active additive layer 是否被显式记录。

工具管线 TA 的关键判断是把这些问题变成机器可读 facts 和 owner boundary。能自动判断的就进规则结果；不能安全修的只给 fix preview 和 owner-held，不把 retarget、resample、layer bake 伪装成一键修复。

## 当前实现

代码入口：

- `dcc-hosts/animation-continuity-lab/fixtures/synthetic_animation_scene.json`
- `dcc-hosts/animation-continuity-lab/animation_continuity_lab/contract.py`
- `dcc-hosts/animation-continuity-lab/animation_continuity_lab/maya_collector.py`
- `dcc-hosts/animation-continuity-lab/scripts/run_smoke.py`
- `dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py`
- `dcc-hosts/animation-continuity-lab/scripts/run_maya_l3.py`

R23 已完成：

- L2 contract smoke：读取 public fixture，输出 animation-continuity input、evaluation、fix preview。
- Maya L3 smoke：自动定位 Maya `mayapy`，在 batch scene 中创建 public synthetic transforms 和 animCurve，采集真实 keyframe facts。
- Presenter Pack 接入：Maya-hosted R23 package 会探测 Animation Continuity L3 artifact，并在 demo route 中加入 `Run animation continuity L3`。
- 公开包接入：`dcc-first-package-manifest.json` 和 `package-manifest.json` 已记录 R23 artifact、summary 和 validation commands。

## 证据

当前 L3 artifact：

```text
<repo>\dcc-hosts\animation-continuity-lab\artifacts\animation-continuity-maya-l3-20260805-162744.json
```

当前 Presenter Pack：

```text
<repo>\dcc-hosts\maya-auroraview-host\artifacts\r23-animation-continuity-l3-presentation-pack-20260805-163040.json
```

关键结果：

- report version：`animation-continuity-maya-l3@0.1.0`
- evidence level：L3
- Maya runtime：2026 batch / API 20260302
- l3 status：`maya_anim_curves_collected`
- assets：2
- ready / review / blocked：1 / 0 / 1
- checks pass / warning / error：11 / 3 / 6
- runtimeCollected：true

Blocked 是 synthetic fixture 中故意放入的失败 take：rig fingerprint 不一致、sample rate 不一致、缺 required channel、channel identity collision、sub-frame key、root motion policy 冲突。它证明规则能抓住业务风险，不表示 runtime 失败。

## 后续

下一阶段把同一份 animation-continuity input 扩到 MotionBuilder / Unreal Animation Bridge：

- MotionBuilder：采集 take list、story clip range、character mapping、plot/bake 状态。
- Unreal：采集 AnimSequence sample rate、root motion、skeleton binding、curve names、compression 后 key range。
- Maya UI：在 AuroraView 面板里增加 animation rows、failure drilldown 和 owner handoff packet。
