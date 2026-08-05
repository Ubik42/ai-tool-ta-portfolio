# Character Calibration & Intent Transfer Studio

Public-safe Maya character calibration evidence module.

R26 scope:

- Generate synthetic character meshes and joint DAGs in Maya `mayapy`.
- Collect topology signature, joint coverage, skin influence budget, calibration deltas, face parameter coverage and Control Rig mappings.
- Export L2 contract and Maya L3 runtime artifacts.

Current intent:

- Prove that character transfer tools should validate business semantics before DNA / blendshape / Control Rig data is trusted.
- Keep one Ready character and one intentionally Blocked temporary sculpt so reviewer can see both release and hold behavior.
- Write no production scenes or assets.
