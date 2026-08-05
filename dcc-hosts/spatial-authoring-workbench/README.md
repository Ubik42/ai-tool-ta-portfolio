# Spatial Authoring & Pose Transfer Workbench

R27 module for public-safe socket, hotspot, pose frame and mirror transfer validation.

## Purpose

This module turns spatial authoring into machine-checkable facts before data moves from DCC to engine:

- socket parent joint coverage and local offset tolerance
- left/right mirror pair presence and symmetry
- VFX / gameplay hotspot semantic and owner accountability
- pose frame coverage, duplicate detection and frame range checks
- transform scale lock, local-space consistency and visible preview locator checks
- pose transfer pair coverage, local-space transfer and owner approval

## Entrypoints

```powershell
python dcc-hosts\spatial-authoring-workbench\scripts\run_smoke.py
python dcc-hosts\spatial-authoring-workbench\scripts\run_l3_smoke.py
```

`run_l3_smoke.py` locates Maya `mayapy`, creates only public synthetic joints and locators, collects runtime facts, and exports `spatial-authoring-maya-l3@0.1.0`.

## Boundary

No production scene, character rig, engine asset or private Lightbox data is included. The blocked row is an intentional synthetic failure case.

