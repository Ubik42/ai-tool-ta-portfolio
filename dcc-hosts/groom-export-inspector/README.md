# Groom Export Inspector

Maya runtime adapter for a public synthetic XGen / groom handoff workflow.

It checks the business facts that make groom export different from mesh export:
root UV, stable strand ID, guide curve coverage, Alembic payload flags and Unreal Groom / Binding intent.

## Commands

```powershell
python dcc-hosts\groom-export-inspector\scripts\run_smoke.py
python dcc-hosts\groom-export-inspector\scripts\run_l3_smoke.py
```

R46 reference artifact:

```text
dcc-hosts\groom-export-inspector\artifacts\groom-export-inspector-maya-l3-20260806-003711.json
```
