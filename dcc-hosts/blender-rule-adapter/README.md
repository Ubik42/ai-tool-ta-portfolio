# Blender Rule Adapter

This host proves the first non-Maya Cross-DCC adapter contract for the AI Tool TA portfolio.

Current evidence level is L3 on this machine. The adapter exports a public synthetic Blender scene through real `bpy` collection, and R57 adds a controlled repair executor that mutates only the public fixture scene, post-checks the repaired state, then rolls back without saving a `.blend` file.

## What It Proves

- Blender object custom properties can carry `asset-protocol@dcc-r9`.
- Collections map to export root, LOD and collision evidence.
- Material slots, image textures and UV layers can be normalized into the same rule input shape used by Cross-DCC Rule Matrix.
- The fixture includes one Ready asset and one intentionally Blocked asset so failure behavior is visible.
- This pass performs no DCC scene writes and no production asset mutation.
- The L3 path creates only temporary public fixture objects.
- The controlled repair path turns blocked collision, LOD, UV and material / texture sync rows into explicit receipts, verifies Ready, then restores the preflight fingerprint.

## Run

```powershell
python <repo>\dcc-hosts\blender-rule-adapter\scripts\run_smoke.py
```

Run the L3 readiness harness:

```powershell
python <repo>\dcc-hosts\blender-rule-adapter\scripts\run_l3_smoke.py
```

Run the controlled repair executor:

```powershell
python <repo>\dcc-hosts\blender-rule-adapter\scripts\run_controlled_repair.py
```

Latest artifact is written to:

```text
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-contract-20260804-201125.json
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-rule-adapter-l3-20260805-153156.json
<repo>\dcc-hosts\blender-rule-adapter\artifacts\blender-controlled-repair-20260806-043919.json
```

## L3 Runtime Path

When Blender is available, the same launcher will run the `bpy` collector:

```powershell
blender --background --python <repo>\dcc-hosts\blender-rule-adapter\scripts\run_blender_l3.py
```

The runtime report schema is `blender-rule-adapter-bpy-l3@0.1.0`. It creates the public fixture inside Blender, collects object custom properties, collections, material slots, textures and UV layers through `bpy`, then evaluates the same Cross-DCC rules as the L2 contract.

## Controlled Repair Path

The repair report schema is `blender-controlled-repair-executor@0.1.0`. It starts from the blocked mobile fixture row, executes four public repair receipts, checks the repaired scene as Ready, then rebuilds the original fixture and verifies the rollback fingerprint. It does not write production assets or save a Blender file.
