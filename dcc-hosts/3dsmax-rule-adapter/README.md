# 3ds Max Rule Adapter

This host proves another non-Maya Cross-DCC adapter contract for the AI Tool TA portfolio.

Current evidence level is L2+ by default. The machine has 3ds Max 2022 batch tooling, but the heartbeat launcher does not start `3dsmaxbatch.exe` automatically because it can depend on license, UI and desktop session state. The adapter still exports a machine-checkable contract artifact and a readiness artifact with the exact opt-in L3 command.

## What It Proves

- 3ds Max user properties can carry `asset-protocol@dcc-r9`.
- Layers / export dummies map to export root evidence.
- LOD suffixes, material names, bitmap slots, map channels, texel density, transform state and UCX collision proxies can normalize into the same Cross-DCC rule input used by the Maya and Blender evidence.
- The fixture includes one Ready asset and one intentionally Blocked asset so failure behavior is visible.
- The default smoke performs no 3ds Max scene writes and no production asset mutation.

## Run

```powershell
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_smoke.py
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_l3_smoke.py
```

Latest artifacts are written to:

```text
<repo>\dcc-hosts\3dsmax-rule-adapter\artifacts
```

## L3 Runtime Path

When operator-run 3ds Max batch validation is acceptable:

```powershell
python <repo>\dcc-hosts\3dsmax-rule-adapter\scripts\run_l3_smoke.py --run-runtime
```

The runtime report schema is `max-rule-adapter-pymxs-l3@0.1.0`. It creates a public synthetic scene in 3ds Max batch, collects pymxs facts and evaluates the same Cross-DCC rules as the L2+ contract.
