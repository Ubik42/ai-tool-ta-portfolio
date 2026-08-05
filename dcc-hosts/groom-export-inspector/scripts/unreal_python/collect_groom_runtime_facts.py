from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_GROOM_EXPORT_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_GROOM_RUNTIME_FACTS_OUTPUT"])
    postcheck_path = Path(os.environ["AI_TOOL_TA_GROOM_RUNTIME_FACTS_POSTCHECK"])
    plugin_fixture_path = Path(os.environ["AI_TOOL_TA_GROOM_RUNTIME_FACTS_PLUGIN_FIXTURE"])
    controlled_executor_path = Path(os.environ["AI_TOOL_TA_GROOM_RUNTIME_FACTS_CONTROLLED_EXECUTOR"])
    scripts_dir = root / "scripts" / "unreal_python"
    for path in (root, scripts_dir):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))

    import unreal  # type: ignore

    import execute_groom_controlled_executor as executor
    from groom_export_inspector.groom_runtime_facts import build_groom_runtime_facts_report, resolve_public_path

    postcheck = json.loads(postcheck_path.read_text(encoding="utf-8"))
    plugin_fixture = json.loads(plugin_fixture_path.read_text(encoding="utf-8"))
    editor_assets = unreal.EditorAssetLibrary
    executor._scan_registry(unreal, ["/Game/AI_Tool_TA"])

    selected = executor._select_operation(postcheck, plugin_fixture, resolve_public_path)
    expected_groom = selected.get("expectedGroomAsset") or "/Game/AI_Tool_TA/Grooms/G_HeroHair"
    expected_binding = selected.get("expectedBindingAsset") or "/Game/AI_Tool_TA/Grooms/GB_HeroHair_SK_HeroFace"
    target_mesh = selected.get("targetSkeletalMesh") or "/Game/AI_Tool_TA/Characters/SK_HeroFace"
    destination = executor._asset_dir(expected_groom) or "/Game/AI_Tool_TA/Grooms"
    selected["destinationPath"] = destination

    errors: List[str] = []
    asset_writes = 0
    rollback_actions: List[Dict[str, Any]] = []
    write_set = sorted({expected_groom, expected_binding, destination})

    preflight = {
        "expectedGroomAsset": executor._asset_probe(unreal, expected_groom),
        "expectedBindingAsset": executor._asset_probe(unreal, expected_binding),
        "targetSkeletalMesh": executor._asset_probe(unreal, target_mesh),
        "destinationDirectory": executor._directory_probe(editor_assets, destination),
    }
    directory_created = False
    if not preflight["destinationDirectory"].get("exists"):
        directory_created = executor._make_directory(editor_assets, destination, errors)
        if directory_created:
            asset_writes += 1
            rollback_actions.append({"id": "delete-empty-groom-runtime-directory", "kind": "delete_directory", "path": destination})

    import_task = executor._execute_import_task(unreal, selected, expected_groom, destination, errors)
    if import_task.get("succeeded"):
        asset_writes += max(1, len(import_task.get("createdAssets", [])))

    executor._scan_registry(unreal, ["/Game/AI_Tool_TA"])
    binding_attempt = executor._execute_binding(unreal, expected_groom, expected_binding, target_mesh, errors)
    if binding_attempt.get("succeeded"):
        asset_writes += 1

    executor._scan_registry(unreal, ["/Game/AI_Tool_TA"])
    asset_facts = {
        "groomAsset": _collect_asset_runtime_fact(unreal, expected_groom, "groom"),
        "bindingAsset": _collect_asset_runtime_fact(unreal, expected_binding, "binding"),
        "targetSkeletalMesh": _collect_asset_runtime_fact(unreal, target_mesh, "skeletalMesh"),
    }
    post_execution = {
        "expectedGroomAsset": executor._asset_probe(unreal, expected_groom),
        "expectedBindingAsset": executor._asset_probe(unreal, expected_binding),
        "targetSkeletalMesh": executor._asset_probe(unreal, target_mesh),
        "importedObjectPaths": import_task.get("importedObjectPaths", []),
    }
    created_assets = executor._created_asset_paths(preflight, post_execution, import_task, expected_groom, expected_binding)
    rollback = executor._rollback_created_assets(unreal, editor_assets, created_assets, destination, directory_created, errors)
    asset_writes += int(rollback.get("writeCount") or 0)

    snapshot = {
        "mode": "execute_collect_then_rollback",
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": executor._engine_version(unreal),
            "pythonVersion": sys.version,
            "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "assetWrites": asset_writes,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "/Game/AI_Tool_TA public Groom fixture only",
        },
        "selectedOperation": selected,
        "apiSurface": _collect_api_surface(unreal),
        "assetFacts": asset_facts,
        "preflight": preflight,
        "importTask": import_task,
        "bindingAttempt": binding_attempt,
        "rollback": rollback,
        "writeSet": write_set + sorted(set(created_assets) - set(write_set)),
        "rollbackActions": rollback_actions + rollback.get("actions", []),
        "errors": errors,
    }
    report = build_groom_runtime_facts_report(postcheck_path, plugin_fixture_path, controlled_executor_path, snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_GROOM_RUNTIME_FACTS_OUTPUT=%s" % output_path)


def _collect_api_surface(unreal) -> Dict[str, Any]:
    class_names = [
        "GroomAsset",
        "GroomBindingAsset",
        "GroomLibrary",
        "HairStrandsFactory",
        "GroomImportOptions",
        "AlembicImportFactory",
        "AssetImportTask",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    methods = {}
    for name in class_names:
        cls = getattr(unreal, name, None)
        methods[name] = _relevant_names(dir(cls), limit=80) if cls else []
    return {"classes": classes, "methods": methods}


def _collect_asset_runtime_fact(unreal, path: str, role: str) -> Dict[str, Any]:
    package_path = _package_path(path)
    base = _asset_probe(unreal, package_path)
    row: Dict[str, Any] = {
        "role": role,
        "path": package_path,
        "exists": base.get("exists"),
        "className": base.get("className"),
        "fingerprint": base.get("fingerprint"),
        "objectClass": None,
        "pathName": None,
        "packageName": None,
        "packageDirty": None,
        "methodNames": [],
        "methodCount": 0,
        "propertyRows": [],
        "readablePropertyCount": 0,
        "callResultRows": [],
        "callResultCount": 0,
        "errors": [],
    }
    if not row["exists"]:
        return row
    asset = None
    try:
        asset = unreal.EditorAssetLibrary.load_asset(package_path)
    except Exception as exc:
        row["errors"].append("load_asset_failed:%s" % exc)
        return row
    if asset is None:
        row["errors"].append("load_asset_returned_none")
        return row
    row["objectClass"] = type(asset).__name__
    row["pathName"] = _safe_call(lambda: asset.get_path_name())
    row["packageName"] = _safe_call(lambda: asset.get_outermost().get_name())
    row["packageDirty"] = _safe_call(lambda: bool(asset.get_outermost().is_dirty()))
    base_fields = [
        {"name": "pathName", "readable": row["pathName"] is not None, "value": row["pathName"], "source": "object"},
        {"name": "packageName", "readable": row["packageName"] is not None, "value": row["packageName"], "source": "object"},
        {"name": "packageDirty", "readable": row["packageDirty"] is not None, "value": row["packageDirty"], "source": "object"},
    ]
    row["propertyRows"].extend(base_fields)
    for name in _candidate_properties(role):
        entry = {"name": name, "readable": False, "value": None, "source": "editor_property", "error": None}
        try:
            value = asset.get_editor_property(name)
            entry["value"] = _safe_value(value)
            entry["readable"] = True
        except Exception as exc:
            entry["error"] = str(exc)
        row["propertyRows"].append(entry)
    method_names = _relevant_names(dir(asset), limit=120)
    row["methodNames"] = method_names
    row["methodCount"] = len(method_names)
    for name in _callable_fact_methods(asset, method_names):
        entry = {"name": name, "called": False, "value": None, "error": None}
        try:
            value = getattr(asset, name)()
            entry["called"] = True
            entry["value"] = _safe_value(value)
        except Exception as exc:
            entry["error"] = str(exc)
        row["callResultRows"].append(entry)
    row["readablePropertyCount"] = sum(1 for item in row["propertyRows"] if item.get("readable"))
    row["callResultCount"] = sum(1 for item in row["callResultRows"] if item.get("called"))
    return row


def _asset_probe(unreal, path: str) -> Dict[str, Any]:
    package_path = _package_path(path)
    result = {"path": package_path, "exists": False, "className": None, "fingerprint": None, "error": None}
    try:
        result["exists"] = bool(unreal.EditorAssetLibrary.does_asset_exist(package_path))
        if result["exists"]:
            asset_data = unreal.EditorAssetLibrary.find_asset_data(package_path)
            result["className"] = _asset_class_name(asset_data)
            result["fingerprint"] = "%s:%s" % (result["path"], result["className"])
    except Exception as exc:
        result["error"] = str(exc)
    return result


def _candidate_properties(role: str) -> List[str]:
    common = ["asset_import_data", "thumbnail_info"]
    if role == "groom":
        return common + [
            "hair_groups_info",
            "hair_groups_cards",
            "hair_groups_meshes",
            "enable_global_interpolation",
            "interpolation_settings",
            "lod_settings",
        ]
    if role == "binding":
        return common + [
            "groom",
            "target_skeletal_mesh",
            "source_skeletal_mesh",
            "num_interpolation_points",
            "matching_section",
            "group_infos",
        ]
    return common + ["skeleton", "materials", "lod_info", "imported_bounds", "physics_asset"]


def _relevant_names(names, limit: int) -> List[str]:
    tokens = (
        "groom",
        "hair",
        "strand",
        "group",
        "binding",
        "mesh",
        "skeleton",
        "lod",
        "guide",
        "interpolation",
        "material",
        "bounds",
        "asset",
        "package",
    )
    blocked = ("delete", "save", "set_", "rename", "reimport", "import_", "build", "create", "make_", "factory")
    rows = []
    for name in names:
        lower = str(name).lower()
        if lower.startswith("_") or any(part in lower for part in blocked):
            continue
        if any(token in lower for token in tokens):
            rows.append(str(name))
    return sorted(set(rows))[:limit]


def _callable_fact_methods(asset, method_names: List[str]) -> List[str]:
    candidates = []
    for name in method_names:
        lower = name.lower()
        if not lower.startswith(("get_", "is_", "has_")):
            continue
        value = getattr(asset, name, None)
        if callable(value):
            candidates.append(name)
    return candidates[:20]


def _asset_class_name(asset_data) -> str | None:
    if not asset_data:
        return None
    try:
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        try:
            return str(asset_data.asset_class)
        except Exception:
            return None


def _package_path(path: str) -> str:
    value = str(path or "")
    if "." in value:
        left, right = value.rsplit(".", 1)
        if "/" not in right:
            return left
    return value


def _safe_call(func):
    try:
        return _safe_value(func())
    except Exception:
        return None


def _safe_value(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_value(item) for item in list(value)[:12]]
    if isinstance(value, dict):
        return {str(key): _safe_value(item) for key, item in list(value.items())[:12]}
    for attr in ("get_path_name", "get_name"):
        method = getattr(value, attr, None)
        if callable(method):
            try:
                return method()
            except Exception:
                pass
    return str(value)[:240]


if __name__ == "__main__":
    _main()
