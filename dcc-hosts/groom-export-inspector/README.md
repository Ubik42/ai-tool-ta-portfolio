# Groom Export Inspector

Maya runtime adapter for a public synthetic XGen / groom handoff workflow.

It checks the business facts that make groom export different from mesh export:
root UV, stable strand ID, guide curve coverage, Alembic payload flags and Unreal Groom / Binding intent.
R59 also checks group/root projection: curve root CVs must project back to the declared scalp `root_uv` group, guide coverage and Unreal material slot before binding is trusted.

## Commands

```powershell
python dcc-hosts\groom-export-inspector\scripts\run_smoke.py
python dcc-hosts\groom-export-inspector\scripts\run_l3_smoke.py
python dcc-hosts\groom-export-inspector\scripts\run_group_root_projection.py
```

R46 reference artifact:

```text
dcc-hosts\groom-export-inspector\artifacts\groom-export-inspector-maya-l3-20260806-003711.json
```

R59 reference artifact:

```text
dcc-hosts\groom-export-inspector\artifacts\groom-group-root-projection-20260806-051721.json
```
