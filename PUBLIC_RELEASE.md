# AI Tool TA Portfolio Public Release

This repository is the public-safe AI Tool TA portfolio workspace.

It demonstrates DCC / engine pipeline tool logic through synthetic fixtures, runtime collectors, JSON evidence, and a Maya-hosted AuroraView interface. It does not require proprietary production scenes or private source repositories.

## Current Showcase

Stable baseline:

```text
ai-tool-ta-dcc-first-showcase-r22 / dcc-first-package@1.19.0
```

Primary delivery artifact:

```text
dcc-hosts/maya-auroraview-host/artifacts/r22-blender-max-l3-presentation-pack-20260805-153957.json
```

Main runtime evidence:

```text
dcc-hosts/blender-rule-adapter/artifacts/blender-rule-adapter-l3-20260805-153156.json
dcc-hosts/3dsmax-rule-adapter/artifacts/max-rule-adapter-l3-20260805-153232.json
dcc-hosts/unreal-handoff-inspector/artifacts/unreal-handoff-inspector-l3-20260803-184208.json
```

## Public Boundary

The public repo intentionally excludes:

- local research extraction notes
- large screenshot/video captures
- installed dependencies
- local DCC binary scenes
- private credentials, endpoints and production assets

All runnable evidence is based on public synthetic fixtures.

## Entry Points

For reviewers:

```text
docs/AI_HANDOFF.md
public-case-package/DCC_FIRST_PACKAGE.md
docs/技术报告/260805_Lightbox核心技术点覆盖与插件开发状态.md
```

For local validation:

```powershell
.\scripts\validate_loop.ps1 -Tier quick
.\scripts\validate_loop.ps1 -Tier package
.\scripts\validate_loop.ps1 -Tier ui
```

For Maya host:

```python
exec(open(r"<repo>\dcc-hosts\maya-auroraview-host\shelf\install_shelf_button.py", "r").read())
```
