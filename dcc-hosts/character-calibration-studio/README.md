# Character Calibration & Intent Transfer Studio

Public-safe Maya character calibration evidence module.

R26-R35 scope:

- Generate synthetic character meshes and joint DAGs in Maya `mayapy`.
- Collect topology signature, joint coverage, skin influence budget, calibration deltas, face parameter coverage and Control Rig mappings.
- Export L2 contract and Maya L3 runtime artifacts.
- Convert Maya L3 validation rows into AuroraView-ready topology, skeleton, skin, calibration, face, Control Rig and mirror drilldown panels.

Current intent:

- Prove that character transfer tools should validate business semantics before DNA / blendshape / Control Rig data is trusted.
- Keep one Ready character and one intentionally Blocked temporary sculpt so reviewer can see both release and hold behavior.
- Expose owner actions and fix previews without mutating production character assets.
- Write no production scenes or assets.

Current artifacts:

```text
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-maya-l3-20260805-175057.json
<repo>\dcc-hosts\character-calibration-studio\artifacts\character-calibration-drilldown-20260805-202259.json
```

R35 drilldown result:

- evidence：L3-derived / `Blocked` / `maya_character_calibration_rows_to_drilldown`
- drilldowns / panels：2 / 14
- owner actions：8 total，6 owner-required，2 manual-review
- production writes：0
