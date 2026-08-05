# Animation Continuity Lab

This adapter turns animation handoff into public-safe, machine-checkable evidence.

It checks:

- rig id and skeleton fingerprint
- take name, range and sample rate
- required channel coverage
- duplicate normalized channel identities
- sub-frame keys
- keys outside take range
- root motion policy
- animated scale leakage
- active additive animation layers without owner attribution

Smoke commands:

```powershell
python <repo>\dcc-hosts\animation-continuity-lab\scripts\run_smoke.py
python <repo>\dcc-hosts\animation-continuity-lab\scripts\run_l3_smoke.py
```
