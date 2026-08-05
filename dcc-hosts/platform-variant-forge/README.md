# Platform Variant Forge

R28 module for public-safe PC to Mobile asset variant planning.

## Purpose

This module turns platform derivation into reviewable facts:

- target engine path policy
- owner approval boundary
- triangle, texture memory, material slot and draw-call budgets
- required LOD coverage
- Nanite and shader feature policy
- collision simplification policy
- source join to existing Unreal preset fact comparison evidence

## Entrypoint

```powershell
python dcc-hosts\platform-variant-forge\scripts\run_smoke.py
```

The smoke exports `platform-variant-forge-contract@0.1.0`. It does not mutate scenes, textures, meshes or Unreal assets.

## R39 StaticMesh post-check

```powershell
python dcc-hosts\platform-variant-forge\scripts\run_staticmesh_postcheck.py
```

This read-only Unreal probe validates LOD / Nanite / collision executor receipts against current StaticMesh runtime facts and exports `platform-variant-staticmesh-postcheck@0.1.0`.
