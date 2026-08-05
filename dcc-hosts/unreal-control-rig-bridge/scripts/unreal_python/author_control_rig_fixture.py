from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_FIXTURE_OUTPUT"])
    source_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_FIXTURE_SOURCE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_control_rig_bridge.fixture_authoring import build_fixture_authoring_report, public_path

    source = json.loads(source_artifact.read_text(encoding="utf-8"))
    operations, held_rows = _execute_operations(unreal, source)
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "assetWrites": sum(1 for op in operations if op.get("authoring", {}).get("saved")),
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "/Game/AI_Tool_TA public fixture only; .uasset remains local ignored fixture evidence",
        },
        "operations": operations,
        "heldRows": held_rows,
    }
    report = build_fixture_authoring_report(source_artifact, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_CONTROL_RIG_FIXTURE_OUTPUT=%s" % output_path)


def _execute_operations(unreal, source: Dict[str, Any]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    operations: List[Dict[str, Any]] = []
    held_rows: List[Dict[str, Any]] = []
    for row in source.get("facts", {}).get("characters", []):
        asset_id = str(row.get("assetId"))
        normalized = row.get("normalized", {})
        runtime_row = row.get("runtime", {})
        selected = (
            row.get("sourceStatus") == "Ready"
            and bool(normalized.get("runtime.skeletalMeshExists"))
            and bool(normalized.get("runtime.skeletonExists"))
            and str(row.get("expectedUnreal", {}).get("controlRigPath", "")).startswith("/Game/AI_Tool_TA/")
        )
        if not selected:
            held_rows.append(
                {
                    "id": "held:%s" % asset_id,
                    "assetId": asset_id,
                    "assetLabel": row.get("assetLabel"),
                    "sourceStatus": row.get("sourceStatus"),
                    "skeletalMeshExists": normalized.get("runtime.skeletalMeshExists"),
                    "skeletonExists": normalized.get("runtime.skeletonExists"),
                    "controlRigPath": row.get("expectedUnreal", {}).get("controlRigPath"),
                    "requiredControls": normalized.get("runtime.requiredControls", []),
                    "reason": "Row is not an approved public fixture authoring candidate.",
                    "mutated": False,
                }
            )
            continue
        operations.append(_execute_single_operation(unreal, row, runtime_row))
    return operations, held_rows


def _execute_single_operation(unreal, row: Dict[str, Any], runtime_row: Dict[str, Any]) -> Dict[str, Any]:
    expected = row.get("expectedUnreal", {})
    asset_id = str(row.get("assetId"))
    control_rig_path = str(expected.get("controlRigPath") or "")
    package_path, asset_name = _split_asset_path(control_rig_path)
    required_controls = list(row.get("normalized", {}).get("runtime.requiredControls") or runtime_row.get("requiredControls") or [])
    skeletal_mesh_path = str(expected.get("skeletalMeshPath") or "")
    skeleton_path = str(expected.get("skeletonPath") or "")
    preflight = _asset_facts(unreal, control_rig_path, required_controls)
    operation = {
        "id": "control-rig-fixture:%s" % asset_id,
        "assetId": asset_id,
        "assetLabel": row.get("assetLabel"),
        "selected": True,
        "sourceStatus": row.get("sourceStatus"),
        "skeletalMeshPath": skeletal_mesh_path,
        "skeletonPath": skeleton_path,
        "controlRigPath": control_rig_path,
        "skeletalMeshExists": bool(runtime_row.get("skeletalMeshExists")),
        "skeletonExists": bool(runtime_row.get("skeletonExists")),
        "requiredControls": required_controls,
        "apiReady": _authoring_api_ready(unreal),
        "preflight": preflight,
        "authoring": {
            "attempted": False,
            "created": False,
            "saved": False,
            "method": None,
            "attempts": [],
            "controlAttempts": [],
            "createdControls": [],
            "errors": [],
        },
        "postcheck": preflight,
    }
    asset = _load_asset(unreal, control_rig_path)
    if not asset:
        operation["authoring"]["attempted"] = True
        asset, creation_result = _create_control_rig_asset(unreal, package_path, asset_name, skeletal_mesh_path)
        operation["authoring"]["method"] = creation_result.get("method")
        operation["authoring"]["attempts"] = creation_result.get("attempts", [])
        operation["authoring"]["created"] = bool(asset)
        operation["authoring"]["errors"].extend(creation_result.get("errors", []))

    if asset:
        control_result = _try_add_missing_controls(unreal, asset, required_controls)
        operation["authoring"]["controlAttempts"] = control_result.get("attempts", [])
        operation["authoring"]["createdControls"] = control_result.get("createdControls", [])
        operation["authoring"]["errors"].extend(control_result.get("errors", []))
        if operation["authoring"]["created"] or operation["authoring"]["createdControls"]:
            operation["authoring"]["saved"] = _save_asset(unreal, control_rig_path, operation["authoring"]["errors"])

    operation["postcheck"] = _asset_facts(unreal, control_rig_path, required_controls)
    return operation


def _create_control_rig_asset(unreal, package_path: str, asset_name: str, skeletal_mesh_path: str) -> tuple[Any, Dict[str, Any]]:
    result = {"method": None, "attempts": [], "errors": []}
    skeletal_mesh = _load_asset(unreal, skeletal_mesh_path)
    if hasattr(unreal, "ControlRigBlueprintFactory") and hasattr(unreal, "AssetToolsHelpers") and hasattr(unreal, "ControlRigBlueprint"):
        attempt = {"method": "AssetTools.create_asset(ControlRigBlueprintFactory)", "ok": False, "error": None}
        try:
            factory = unreal.ControlRigBlueprintFactory()
            _try_set_factory_preview_mesh(factory, skeletal_mesh, attempt)
            asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
            asset = asset_tools.create_asset(asset_name, package_path, unreal.ControlRigBlueprint, factory)
            attempt["ok"] = bool(asset)
            result["attempts"].append(attempt)
            if asset:
                result["method"] = attempt["method"]
                return asset, result
        except Exception as exc:
            attempt["error"] = str(exc)
            result["attempts"].append(attempt)
            result["errors"].append("%s:%s" % (attempt["method"], exc))
    if hasattr(unreal, "ControlRigBlueprint") and hasattr(unreal.ControlRigBlueprint, "create_control_rig") and skeletal_mesh:
        attempt = {"method": "ControlRigBlueprint.create_control_rig(skeletal_mesh)", "ok": False, "error": None}
        try:
            asset = unreal.ControlRigBlueprint.create_control_rig(skeletal_mesh)
            attempt["ok"] = bool(asset)
            result["attempts"].append(attempt)
            if asset:
                result["method"] = attempt["method"]
                return asset, result
        except Exception as exc:
            attempt["error"] = str(exc)
            result["attempts"].append(attempt)
            result["errors"].append("%s:%s" % (attempt["method"], exc))
    if not result["attempts"]:
        result["errors"].append("control_rig_authoring_api_unavailable")
    return None, result


def _try_set_factory_preview_mesh(factory: Any, skeletal_mesh: Any, attempt: Dict[str, Any]) -> None:
    attempt["factoryProperties"] = []
    if not skeletal_mesh:
        return
    for prop in ("preview_skeletal_mesh", "target_skeletal_mesh", "skeletal_mesh"):
        try:
            factory.set_editor_property(prop, skeletal_mesh)
            attempt["factoryProperties"].append({"property": prop, "set": True})
            return
        except Exception as exc:
            attempt["factoryProperties"].append({"property": prop, "set": False, "error": str(exc)})


def _try_add_missing_controls(unreal, asset: Any, required_controls: List[str]) -> Dict[str, Any]:
    result = {"attempts": [], "createdControls": [], "errors": []}
    facts = _asset_facts_from_asset(asset, required_controls)
    missing = [name for name in required_controls if name not in set(facts.get("runtimeControls", []))]
    if not missing:
        return result
    controller = _safe(lambda: asset.get_hierarchy_controller(), None)
    if not controller:
        result["errors"].append("hierarchy_controller_unavailable")
        return result
    for name in missing:
        attempt = {"control": name, "method": "RigHierarchyController.add_control", "ok": False, "errors": []}
        ok = _try_add_control(unreal, controller, name, attempt)
        attempt["ok"] = ok
        result["attempts"].append(attempt)
        if ok:
            result["createdControls"].append(name)
        else:
            result["errors"].extend("%s:%s" % (name, error) for error in attempt["errors"])
    _safe(lambda: asset.recompile_vm(), None)
    _safe(lambda: asset.request_auto_vm_recompilation(), None)
    _safe(lambda: asset.post_edit_change(), None)
    return result


def _try_add_control(unreal, controller: Any, name: str, attempt: Dict[str, Any]) -> bool:
    settings = _safe(lambda: unreal.RigControlSettings(), None) if hasattr(unreal, "RigControlSettings") else None
    value = _safe(lambda: unreal.RigControlValue(), None) if hasattr(unreal, "RigControlValue") else None
    parent_key = _empty_rig_key(unreal)
    calls = [
        lambda: controller.add_control(name, parent_key, settings, value, False),
        lambda: controller.add_control(name, parent_key, settings, value),
        lambda: controller.add_control(name, parent_key, settings),
        lambda: controller.add_control(name, parent_key),
        lambda: controller.add_control(name),
    ]
    for index, call in enumerate(calls, start=1):
        try:
            result = call()
            attempt["callIndex"] = index
            attempt["result"] = str(result)
            return True
        except Exception as exc:
            attempt["errors"].append("call%s:%s" % (index, exc))
    return False


def _empty_rig_key(unreal) -> Any:
    if hasattr(unreal, "RigElementKey"):
        for args in ((), ("", getattr(unreal, "RigElementType", object()).NULL)):
            try:
                return unreal.RigElementKey(*args)
            except Exception:
                continue
    return None


def _asset_facts(unreal, asset_path: str, required_controls: List[str]) -> Dict[str, Any]:
    asset = _load_asset(unreal, asset_path)
    if not asset:
        return {
            "exists": False,
            "class": None,
            "pathName": asset_path,
            "hierarchyReadable": False,
            "hierarchyKeyCount": 0,
            "hierarchyKeys": [],
            "runtimeControls": [],
            "missingControls": sorted(required_controls),
            "availableMethods": [],
            "hierarchyMethods": [],
        }
    facts = _asset_facts_from_asset(asset, required_controls)
    facts["exists"] = True
    facts["class"] = _safe(lambda: asset.get_class().get_name(), None)
    facts["pathName"] = _safe(lambda: str(asset.get_path_name()), asset_path)
    return facts


def _asset_facts_from_asset(asset: Any, required_controls: List[str]) -> Dict[str, Any]:
    methods = _method_names(asset, ["control", "hierarchy", "rig", "vm"])
    hierarchy = _safe(lambda: asset.get_hierarchy(), None)
    if not hierarchy:
        hierarchy = _safe(lambda: asset.hierarchy, None)
    hierarchy_methods = _method_names(hierarchy, ["control", "key", "element", "hierarchy"]) if hierarchy else []
    keys = _hierarchy_keys(hierarchy)
    controls = _control_names(hierarchy, keys)
    return {
        "exists": True,
        "class": _safe(lambda: asset.get_class().get_name(), None),
        "pathName": _safe(lambda: str(asset.get_path_name()), None),
        "hierarchyReadable": bool(hierarchy),
        "hierarchyKeyCount": len(keys),
        "hierarchyKeys": keys[:80],
        "runtimeControls": sorted(set(controls)),
        "missingControls": sorted(name for name in required_controls if name not in set(controls)),
        "availableMethods": methods[:80],
        "hierarchyMethods": hierarchy_methods[:80],
    }


def _hierarchy_keys(hierarchy: Any) -> List[Dict[str, Any]]:
    if not hierarchy:
        return []
    raw_keys = _safe(lambda: hierarchy.get_all_keys(), None)
    if raw_keys is None:
        raw_keys = _safe(lambda: hierarchy.get_controls(), None)
    rows = []
    for key in raw_keys or []:
        rows.append(
            {
                "name": _key_name(key),
                "type": _key_type(key),
                "repr": str(key),
            }
        )
    return rows


def _control_names(hierarchy: Any, keys: List[Dict[str, Any]]) -> List[str]:
    names = []
    controls = _safe(lambda: hierarchy.get_controls(), None) if hierarchy else None
    for control in controls or []:
        names.append(_key_name(control))
    for key in keys:
        if "control" in str(key.get("type", "")).lower():
            names.append(str(key.get("name")))
    return sorted({name for name in names if name and name != "None"})


def _key_name(key: Any) -> Optional[str]:
    value = _safe(lambda: key.name, None)
    if value is None:
        value = _safe(lambda: key.get_editor_property("name"), None)
    if value is None:
        value = _safe(lambda: key.get_name(), None)
    return str(value) if value is not None else None


def _key_type(key: Any) -> Optional[str]:
    value = _safe(lambda: key.type, None)
    if value is None:
        value = _safe(lambda: key.get_editor_property("type"), None)
    return str(value) if value is not None else None


def _save_asset(unreal, asset_path: str, errors: List[str]) -> bool:
    try:
        return bool(unreal.EditorAssetLibrary.save_asset(asset_path, only_if_is_dirty=False))
    except Exception as exc:
        errors.append("save_asset:%s" % exc)
        return False


def _split_asset_path(asset_path: str) -> tuple[str, str]:
    package, _, name = asset_path.rpartition("/")
    return package, name


def _authoring_api_ready(unreal) -> bool:
    return bool(
        hasattr(unreal, "ControlRigBlueprint")
        and hasattr(unreal, "ControlRigBlueprintFactory")
        and hasattr(unreal, "AssetToolsHelpers")
        and hasattr(unreal, "EditorAssetLibrary")
    )


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "ControlRig",
        "ControlRigBlueprint",
        "ControlRigBlueprintFactory",
        "RigControlSettings",
        "RigControlValue",
        "RigElementKey",
        "RigElementType",
        "RigHierarchy",
        "RigHierarchyController",
        "AssetToolsHelpers",
        "EditorAssetLibrary",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    return {
        "classes": classes,
        "controlRigBlueprintMethods": _method_names(unreal.ControlRigBlueprint, ["control", "hierarchy", "rig", "vm"])[:80]
        if hasattr(unreal, "ControlRigBlueprint")
        else [],
        "factoryMethods": _method_names(unreal.ControlRigBlueprintFactory, ["control", "rig", "mesh", "skeleton", "factory"])[:80]
        if hasattr(unreal, "ControlRigBlueprintFactory")
        else [],
    }


def _load_asset(unreal, path: Optional[str]):
    if not path:
        return None
    try:
        return unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    except Exception:
        return None


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    if not obj:
        return []
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
