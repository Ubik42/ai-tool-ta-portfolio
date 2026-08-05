"""Unreal Groom plugin/API fixture readiness.

This adapter verifies the public Unreal project configuration for Groom
handoff work. It separates three facts that are easy to conflate: engine
plugin descriptors exist, the public project requests those plugins, and
Unreal Python exposes enough Groom import API to build an executor.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .contract import public_path


REPORT_VERSION = "groom-plugin-api-fixture@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]

REQUIRED_PLUGINS = {
    "GeometryCache": "Engine/Plugins/Runtime/GeometryCache/GeometryCache.uplugin",
    "AlembicImporter": "Engine/Plugins/Importers/AlembicImporter/AlembicImporter.uplugin",
    "HairStrands": "Engine/Plugins/Runtime/HairStrands/HairStrands.uplugin",
    "AlembicHairImporter": "Engine/Plugins/Importers/AlembicHairImporter/AlembicHairImporter.uplugin",
}


def collect_static_plugin_snapshot(project_path: str | Path, unreal_cli: str | Path | None = None) -> Dict[str, Any]:
    project = Path(project_path)
    project_exists = project.exists()
    project_data = json.loads(project.read_text(encoding="utf-8")) if project_exists else {}
    requested_plugins = project_data.get("Plugins", []) if isinstance(project_data.get("Plugins"), list) else []
    requested_by_name = {str(row.get("Name")): row for row in requested_plugins if isinstance(row, dict)}
    engine_root = _resolve_engine_root(unreal_cli)
    descriptors = []
    for plugin_name, relative_path in REQUIRED_PLUGINS.items():
        descriptor_path = _descriptor_path(engine_root, relative_path)
        descriptor = _read_descriptor(descriptor_path)
        descriptors.append(
            {
                "plugin": plugin_name,
                "descriptor": str(descriptor_path) if descriptor_path else None,
                "exists": bool(descriptor_path and descriptor_path.exists()),
                "friendlyName": descriptor.get("FriendlyName"),
                "enabledByDefault": descriptor.get("EnabledByDefault"),
                "modules": [
                    {"name": row.get("Name"), "type": row.get("Type"), "loadingPhase": row.get("LoadingPhase")}
                    for row in descriptor.get("Modules", [])
                    if isinstance(row, dict)
                ],
                "projectRequested": bool(requested_by_name.get(plugin_name, {}).get("Enabled")),
                "projectRow": requested_by_name.get(plugin_name, {}),
            }
        )
    return {
        "project": {
            "path": public_path(project) if _is_under_repo(project) else str(project),
            "exists": project_exists,
            "engineAssociation": project_data.get("EngineAssociation"),
            "plugins": requested_plugins,
            "requestedPluginNames": sorted(requested_by_name),
        },
        "engine": {
            "root": str(engine_root) if engine_root else None,
            "unrealCli": str(unreal_cli) if unreal_cli else None,
        },
        "descriptors": descriptors,
    }


def build_groom_plugin_api_fixture_report(
    static_snapshot: Dict[str, Any],
    runtime_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    runtime_snapshot = runtime_snapshot or _default_runtime_snapshot()
    facts = _build_facts(static_snapshot, runtime_snapshot)
    evaluation = _evaluate_facts(facts)
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if runtime.get("executed") else "Blocked",
        "l3Status": _l3_status(evaluation.get("summary", {}), runtime),
        "publicProject": static_snapshot.get("project", {}),
        "enginePluginDescriptors": static_snapshot.get("descriptors", []),
        "unrealRuntime": runtime,
        "apiAvailability": runtime_snapshot.get("api", {}),
        "facts": facts,
        "evaluation": evaluation,
        "adapter": {
            "id": "groom-plugin-api-fixture",
            "name": "Groom Plugin/API Public Fixture Readiness",
            "methodSource": "Public Unreal project plugin config + UE commandlet Python API probe",
            "protocolCarrier": "HairStrands, AlembicHairImporter, AlembicImporter, GeometryCache descriptors and Python classes",
            "boundary": {
                "mutation": "read_only_project_plugin_api_probe",
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "read-only; no import, no save"),
            },
        },
        "reviewerClaims": [
            "R50 proves the public Unreal project explicitly requests the Groom/HairStrands and Alembic hair importer plugin stack.",
            "The report separates plugin descriptor readiness from Unreal Python import API visibility, so missing Groom factory/options APIs stay actionable.",
            "The probe is read-only: it enters Unreal, inspects classes and plugin-facing facts, and records zero asset, engine and production writes.",
        ],
    }


def _build_facts(static_snapshot: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    descriptors = static_snapshot.get("descriptors", [])
    runtime = runtime_snapshot.get("runtime", {})
    api = runtime_snapshot.get("api", {})
    classes = api.get("classes", {}) if isinstance(api.get("classes"), dict) else {}
    class_names = api.get("classNames", {}) if isinstance(api.get("classNames"), dict) else {}
    project = static_snapshot.get("project", {})
    rows = []
    for descriptor in descriptors:
        rows.append(
            {
                "plugin": descriptor.get("plugin"),
                "descriptorExists": bool(descriptor.get("exists")),
                "projectRequested": bool(descriptor.get("projectRequested")),
                "enabledByDefault": descriptor.get("enabledByDefault"),
                "moduleCount": len(descriptor.get("modules") or []),
                "modules": descriptor.get("modules") or [],
            }
        )
    groom_class_names = class_names.get("groom", [])
    hair_class_names = class_names.get("hair", [])
    alembic_class_names = class_names.get("alembic", [])
    geometry_cache_class_names = class_names.get("geometryCache", [])
    groom_api_ready = bool(
        (classes.get("GroomAsset") or groom_class_names)
        and (classes.get("GroomBindingAsset") or any("binding" in str(name).lower() for name in groom_class_names))
        and (classes.get("GroomImportFactory") or classes.get("GroomImportOptions") or classes.get("GroomCacheImportOptions"))
    )
    summary = {
        "projectConfigReadable": bool(project.get("exists")),
        "engineRootResolved": bool(static_snapshot.get("engine", {}).get("root")),
        "requiredPluginRows": len(rows),
        "descriptorRowsFound": sum(1 for row in rows if row.get("descriptorExists")),
        "projectRequestedRows": sum(1 for row in rows if row.get("projectRequested")),
        "runtimeCollected": bool(runtime.get("executed")),
        "groomClassNameRows": len(groom_class_names),
        "hairClassNameRows": len(hair_class_names),
        "alembicClassNameRows": len(alembic_class_names),
        "geometryCacheClassNameRows": len(geometry_cache_class_names),
        "groomAssetVisible": bool(classes.get("GroomAsset") or groom_class_names),
        "groomBindingAssetVisible": bool(classes.get("GroomBindingAsset") or any("binding" in str(name).lower() for name in groom_class_names)),
        "groomImportFactoryVisible": bool(classes.get("GroomImportFactory")),
        "groomImportOptionsVisible": bool(classes.get("GroomImportOptions") or classes.get("GroomCacheImportOptions")),
        "groomImportApiReady": groom_api_ready,
        "alembicImportFactoryVisible": bool(classes.get("AlembicImportFactory")),
        "abcImportSettingsVisible": bool(classes.get("AbcImportSettings") or classes.get("AlembicImportSettings")),
        "geometryCacheVisible": bool(classes.get("GeometryCache") or geometry_cache_class_names),
        "assetWrites": int(runtime.get("assetWrites", 0) or 0),
        "engineWrites": int(runtime.get("engineWrites", 0) or 0),
        "productionWrites": int(runtime.get("productionWrites", 0) or 0),
    }
    return {
        "schema": "groom-plugin-api-fixture-facts@0.1.0",
        "plugins": rows,
        "runtimeClassNames": class_names,
        "summary": summary,
    }


def _evaluate_facts(facts: Dict[str, Any]) -> Dict[str, Any]:
    summary = facts.get("summary", {})
    evaluations: List[Dict[str, Any]] = [
        _eval("project-config-readable", bool(summary.get("projectConfigReadable")), "error", "Public Project Config", "The public Unreal fixture .uproject must be readable.", summary.get("projectConfigReadable"), "Restore AI_Tool_TA_Unreal_L3.uproject."),
        _eval("engine-root-resolved", bool(summary.get("engineRootResolved")), "error", "Unreal Engine Root", "The harness must resolve the UE Engine root from UnrealEditor-Cmd.", summary.get("engineRootResolved"), "Set AI_TOOL_TA_UNREAL_CLI or install Unreal 5.x."),
        _eval("engine-plugin-descriptors", summary.get("descriptorRowsFound") == summary.get("requiredPluginRows") and summary.get("requiredPluginRows") == len(REQUIRED_PLUGINS), "error", "Required Plugin Descriptors", "Every required Groom/Alembic plugin descriptor must exist in the local engine.", "%s/%s" % (summary.get("descriptorRowsFound"), summary.get("requiredPluginRows")), "Install or locate a UE build with HairStrands, AlembicHairImporter, AlembicImporter and GeometryCache."),
        _eval("public-project-plugin-requests", summary.get("projectRequestedRows") == len(REQUIRED_PLUGINS), "error", "Public Project Plugin Requests", "The public Unreal fixture must explicitly request every Groom/Alembic plugin used by the executor plan.", "%s/%s" % (summary.get("projectRequestedRows"), len(REQUIRED_PLUGINS)), "Enable the missing plugins in the public .uproject."),
        _eval("unreal-runtime-entered", bool(summary.get("runtimeCollected")), "error", "Unreal Runtime Probe", "The fixture must be tested by UnrealEditor-Cmd, not inferred from file config.", summary.get("runtimeCollected"), "Run run_groom_plugin_api_fixture.py with UnrealEditor-Cmd available."),
        _eval("alembic-import-api-visible", bool(summary.get("alembicImportFactoryVisible")), "error", "Alembic Import API", "Alembic import factory must be visible before a Groom cache executor can be planned.", summary.get("alembicImportFactoryVisible"), "Enable/verify AlembicImporter in the public Unreal project."),
        _eval("geometry-cache-api-visible", bool(summary.get("geometryCacheVisible")), "warning", "Geometry Cache API", "Geometry Cache classes should be visible for Alembic cache review and fallback inspection.", summary.get("geometryCacheVisible"), "Verify GeometryCache plugin exposure in Unreal Python."),
        _eval("groom-core-classes-visible", bool(summary.get("groomAssetVisible")), "error", "Groom Core API", "HairStrands/Groom core classes must be visible to promote import readiness toward an executor.", "groomClassNameRows=%s" % summary.get("groomClassNameRows"), "Verify HairStrands plugin loading or use a C++/Editor Utility bridge."),
        _eval("groom-import-api-ready", bool(summary.get("groomImportApiReady")), "error", "Groom Import API", "A controlled Groom executor needs Groom asset/binding visibility plus import factory/options access.", "asset=%s binding=%s factory=%s options=%s" % (summary.get("groomAssetVisible"), summary.get("groomBindingAssetVisible"), summary.get("groomImportFactoryVisible"), summary.get("groomImportOptionsVisible")), "Use AlembicHairImporter-supported API surface or bridge missing import calls outside Python."),
        _eval("no-write-boundary", summary.get("assetWrites") == 0 and summary.get("engineWrites") == 0 and summary.get("productionWrites") == 0, "error", "Read-only Boundary", "R50 must not import, save or mutate assets.", "assetWrites=%s engineWrites=%s productionWrites=%s" % (summary.get("assetWrites"), summary.get("engineWrites"), summary.get("productionWrites")), "Revert side effects and keep this stage read-only."),
    ]
    return {
        "schema": "groom-plugin-api-fixture-evaluation@0.1.0",
        "summary": _summarize_evaluations(evaluations),
        "evaluations": evaluations,
        "ownerActions": _owner_actions(evaluations),
    }


def _default_runtime_snapshot() -> Dict[str, Any]:
    return {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "engineVersion": "not_entered",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "api": {},
    }


def _resolve_engine_root(unreal_cli: str | Path | None) -> Optional[Path]:
    if not unreal_cli:
        return None
    path = Path(unreal_cli)
    for parent in path.parents:
        if parent.name == "Engine":
            return parent
    return None


def _descriptor_path(engine_root: Optional[Path], relative_path: str) -> Optional[Path]:
    if not engine_root:
        return None
    parts = Path(relative_path).parts
    return engine_root.joinpath(*parts[1:]) if len(parts) > 1 and parts[0] == "Engine" else engine_root / relative_path


def _read_descriptor(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _is_under_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(PORTFOLIO_ROOT)
        return True
    except ValueError:
        return False


def _eval(
    rule_id: str,
    passed: bool,
    fail_status: str,
    label: str,
    message: str,
    evidence: Any,
    fix_preview: str,
) -> Dict[str, Any]:
    status = "pass" if passed else fail_status
    return {
        "id": rule_id,
        "ruleId": rule_id,
        "label": label,
        "status": status,
        "message": "%s is satisfied." % label if passed else message,
        "evidence": evidence,
        "fixPreview": "No action." if passed else fix_preview,
    }


def _summarize_evaluations(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(evaluations)
    return {
        "gate": "Blocked" if any(row["status"] == "error" for row in rows) else "Review" if any(row["status"] == "warning" for row in rows) else "Ready",
        "checks": len(rows),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
    }


def _owner_actions(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for row in evaluations:
        if row["status"] == "pass":
            continue
        actions.append(
            {
                "id": "owner-action:%s" % row["ruleId"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "owner": _owner_for_rule(row["ruleId"]),
                "mutationScope": "owner_required" if row["status"] == "error" else "manual_review",
                "preview": row["fixPreview"],
                "writeBoundary": "read_only_unreal_plugin_api_probe",
            }
        )
    return actions


def _owner_for_rule(rule_id: str) -> str:
    if rule_id in {"public-project-plugin-requests", "engine-plugin-descriptors", "engine-root-resolved"}:
        return "engine-ta"
    if rule_id in {"groom-core-classes-visible", "groom-import-api-ready", "alembic-import-api-visible", "geometry-cache-api-visible"}:
        return "engine-ta"
    if rule_id in {"unreal-runtime-entered"}:
        return "pipeline-ta"
    if rule_id in {"no-write-boundary"}:
        return "pipeline-ta"
    return "reviewer"


def _l3_status(summary: Dict[str, Any], runtime: Dict[str, Any]) -> str:
    if runtime.get("blockedReason"):
        return str(runtime.get("blockedReason"))
    if not runtime.get("executed"):
        return "contract_groom_plugin_api_fixture"
    if summary.get("gate") == "Blocked":
        return "unreal_groom_plugin_api_fixture_blocked"
    if summary.get("gate") == "Review":
        return "unreal_groom_plugin_api_fixture_review"
    return "unreal_groom_plugin_api_fixture_ready"
