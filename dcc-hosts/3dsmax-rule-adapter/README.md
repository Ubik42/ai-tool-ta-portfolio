# 3ds Max Rule Adapter

This host proves another non-Maya Cross-DCC adapter contract for the AI Tool TA portfolio.

Current evidence level is L3 on this machine. The adapter exports a public synthetic scene through real `pymxs` collection, and R58 adds a controlled repair executor that mutates only the public fixture scene, post-checks the repaired state, then rolls back without saving a `.max` file.

## What It Proves

- 3ds Max user properties can carry `asset-protocol@dcc-r9`.
- Layers / export dummies map to export root evidence.
- LOD suffixes, material names, bitmap slots, map channels, texel density, transform state and UCX collision proxies can normalize into the same Cross-DCC rule input used by the Maya and Blender evidence.
- The fixture includes one Ready asset and one intentionally Blocked asset so failure behavior is visible.
- The default smoke performs no production asset mutation.
- The controlled repair path turns blocked UCX collision, LOD, material / texture, UV / map channel, transform and vertex-color rows into explicit receipts, verifies Ready, then restores the preflight fingerprint.

## Run

```powershell
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_smoke.py
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_l3_smoke.py
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_controlled_repair.py 600
```

Latest artifacts are written to:

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts
```

## L3 Runtime Path

Run the runtime collector directly:

```powershell
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_l3_smoke.py --run-runtime
```

The runtime report schema is `max-rule-adapter-pymxs-l3@0.1.0`. It creates a public synthetic scene in 3ds Max batch, collects pymxs facts and evaluates the same Cross-DCC rules as the L2+ contract.

## Controlled Repair Path

```powershell
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_controlled_repair.py 600
```

The repair report schema is `max-controlled-repair-executor@0.1.0`. 3ds Max 2022 batch starts from the blocked hero fixture row, executes five public repair receipts, checks the scene as Ready, then rebuilds the original fixture and verifies rollback. It reports preGate `Blocked`, postGate `Ready`, rollbackPassed=true, selected/executed=5/5, postReadyAssets=2, postBlockedAssets=0, assetWrites=0 and productionWrites=0.
