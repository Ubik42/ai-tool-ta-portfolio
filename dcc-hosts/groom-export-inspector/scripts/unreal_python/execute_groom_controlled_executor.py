from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_GROOM_EXPORT_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_GROOM_CONTROLLED_EXECUTOR_OUTPUT"])
    postcheck_path = Path(os.environ["AI_TOOL_TA_GROOM_CONTROLLED_EXECUTOR_POSTCHECK"])
    plugin_fixture_path = Path(os.environ["AI_TOOL_TA_GROOM_CONTROLLED_EXECUTOR_PLUGIN_FIXTURE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from groom_export_inspector.controlled_executor import (
        build_groom_controlled_executor_report,
        resolve_public_path,
    )

    postcheck = json.loads(postcheck_path.read_text(encoding="utf-8"))
    plugin_fixture = json.loads(plugin_fixture_path.read_text(encoding="utf-8"))
    editor_assets = unreal.EditorAssetLibrary
    _scan_registry(unreal, ["/Game/AI_Tool_TA"])

    selected = _select_operation(postcheck, plugin_fixture, resolve_public_path)
    expected_groom = selected.get("expectedGroomAsset") or "/Game/AI_Tool_TA/Grooms/G_HeroHair"
    expected_binding = selected.get("expectedBindingAsset") or "/Game/AI_Tool_TA/Grooms/GB_HeroHair_SK_HeroFace"
    target_mesh = selected.get("targetSkeletalMesh") or "/Game/AI_Tool_TA/Characters/SK_HeroFace"
    destination = _asset_dir(expected_groom) or "/Game/AI_Tool_TA/Grooms"
    selected["destinationPath"] = destination

    errors: List[str] = []
    asset_writes = 0
    rollback_actions: List[Dict[str, Any]] = []
    write_set = sorted({expected_groom, expected_binding, destination})

    preflight = {
        "expectedGroomAsset": _asset_probe(unreal, expected_groom),
        "expectedBindingAsset": _asset_probe(unreal, expected_binding),
        "targetSkeletalMesh": _asset_probe(unreal, target_mesh),
        "destinationDirectory": _directory_probe(editor_assets, destination),
    }
    directory_created = False
    if not preflight["destinationDirectory"].get("exists"):
        directory_created = _make_directory(editor_assets, destination, errors)
        if directory_created:
            asset_writes += 1
            rollback_actions.append({"id": "delete-empty-groom-directory", "kind": "delete_directory", "path": destination})

    import_task = _execute_import_task(unreal, selected, expected_groom, destination, errors)
    if import_task.get("succeeded"):
        asset_writes += max(1, len(import_task.get("createdAssets", [])))

    _scan_registry(unreal, ["/Game/AI_Tool_TA"])
    mid_execution = {
        "expectedGroomAsset": _asset_probe(unreal, expected_groom),
        "expectedBindingAsset": _asset_probe(unreal, expected_binding),
        "targetSkeletalMesh": _asset_probe(unreal, target_mesh),
    }
    binding_attempt = _execute_binding(unreal, expected_groom, expected_binding, target_mesh, errors)
    if binding_attempt.get("succeeded"):
        asset_writes += 1

    _scan_registry(unreal, ["/Game/AI_Tool_TA"])
    post_execution = {
        "expectedGroomAsset": _asset_probe(unreal, expected_groom),
        "expectedBindingAsset": _asset_probe(unreal, expected_binding),
        "targetSkeletalMesh": _asset_probe(unreal, target_mesh),
        "importedObjectPaths": import_task.get("importedObjectPaths", []),
        "midExecution": mid_execution,
    }

    created_assets = _created_asset_paths(preflight, post_execution, import_task, expected_groom, expected_binding)
    rollback = _rollback_created_assets(unreal, editor_assets, created_assets, destination, directory_created, errors)
    asset_writes += int(rollback.get("writeCount") or 0)

    snapshot = {
        "mode": "execute_then_rollback",
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _engine_version(unreal),
            "pythonVersion": sys.version,
            "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "assetWrites": asset_writes,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "/Game/AI_Tool_TA public Groom fixture only",
        },
        "selectedOperation": selected,
        "preflight": preflight,
        "importTask": import_task,
        "bindingAttempt": binding_attempt,
        "postExecution": post_execution,
        "rollback": rollback,
        "writeSet": write_set + sorted(set(created_assets) - set(write_set)),
        "rollbackActions": rollback_actions + rollback.get("actions", []),
        "errors": errors,
    }
    report = build_groom_controlled_executor_report(postcheck_path, plugin_fixture_path, snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_GROOM_CONTROLLED_EXECUTOR_OUTPUT=%s" % output_path)


def _select_operation(postcheck: Dict[str, Any], plugin_fixture: Dict[str, Any], resolve_public_path) -> Dict[str, Any]:
    plugin_summary = plugin_fixture.get("facts", {}).get("summary", {})
    operations = postcheck.get("facts", {}).get("operations", [])
    selected_row: Dict[str, Any] = {}
    for row in operations:
        if row.get("sourceExportSelected") and row.get("sourceStatus") == "Ready" and row.get("cache", {}).get("hashMatches"):
            selected_row = row
            break
    cache = selected_row.get("cache", {})
    local_cache = resolve_public_path(cache.get("runtimePath") or cache.get("sourcePath"))
    targets = selected_row.get("unrealTargets", {})
    return {
        "assetId": selected_row.get("assetId"),
        "assetLabel": selected_row.get("assetLabel"),
        "selected": bool(selected_row),
        "sourceImportCandidate": bool(selected_row.get("importPlan", {}).get("candidate")),
        "pluginApiReady": bool(plugin_summary.get("groomImportApiReady")),
        "alembicImportFactoryVisible": bool(plugin_summary.get("alembicImportFactoryVisible")),
        "cache": {
            "path": cache.get("runtimePath") or cache.get("sourcePath"),
            "localPath": str(local_cache),
            "exists": local_cache.exists(),
            "bytes": local_cache.stat().st_size if local_cache.exists() else 0,
            "sourceSha256": cache.get("sourceSha256"),
            "runtimeSha256": cache.get("runtimeSha256"),
            "localSha256": _sha256(local_cache) if local_cache.exists() else None,
            "hashMatches": bool(cache.get("hashMatches")),
        },
        "expectedGroomAsset": targets.get("expectedGroomAsset"),
        "expectedBindingAsset": targets.get("expectedBindingAsset"),
        "targetSkeletalMesh": targets.get("targetSkeletalMesh"),
        "materialSlot": targets.get("materialSlot"),
    }


def _execute_import_task(unreal, selected: Dict[str, Any], expected_groom: str, destination: str, errors: List[str]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "attempted": False,
        "succeeded": False,
        "factoryClass": None,
        "optionsClass": None,
        "destination": destination,
        "destinationName": _asset_name(expected_groom),
        "propertyRows": [],
        "importedObjectPaths": [],
        "createdAssets": [],
        "errors": [],
    }
    cache_path = selected.get("cache", {}).get("localPath")
    if not cache_path or not Path(cache_path).exists():
        result["errors"].append("missing_cache_file:%s" % cache_path)
        errors.extend(result["errors"])
        return result
    task_cls = getattr(unreal, "AssetImportTask", None)
    asset_tools_owner = getattr(unreal, "AssetToolsHelpers", None)
    if task_cls is None or asset_tools_owner is None:
        result["errors"].append("missing_AssetImportTask_or_AssetToolsHelpers")
        errors.extend(result["errors"])
        return result
    try:
        task = task_cls()
        result["attempted"] = True
    except Exception as exc:
        result["errors"].append("AssetImportTask_construct_failed:%s" % exc)
        errors.extend(result["errors"])
        return result
    _set_property(task, "filename", str(cache_path), result)
    _set_property(task, "destination_path", destination, result)
    _set_property(task, "destination_name", _asset_name(expected_groom), result)
    _set_property(task, "automated", True, result)
    _set_property(task, "replace_existing", False, result)
    _set_property(task, "save", True, result)
    factory = _build_factory(unreal, result)
    if factory is not None:
        _set_property(task, "factory", factory, result)
    options = _build_import_options(unreal, result)
    if options is not None:
        _set_property(task, "options", options, result)
    try:
        asset_tools = asset_tools_owner.get_asset_tools()
        before = _asset_probe(unreal, expected_groom)
        asset_tools.import_asset_tasks([task])
        imported = _imported_object_paths(task)
        result["importedObjectPaths"] = imported
        after = _asset_probe(unreal, expected_groom)
        result["createdAssets"] = sorted({path for path in [_package_path(p) for p in imported] if path})
        if after.get("exists") and expected_groom not in result["createdAssets"] and not before.get("exists"):
            result["createdAssets"].append(expected_groom)
        result["succeeded"] = bool(after.get("exists") or result["createdAssets"])
    except Exception as exc:
        result["errors"].append("import_asset_tasks_failed:%s" % exc)
    errors.extend(result["errors"])
    return result


def _build_factory(unreal, result: Dict[str, Any]):
    for class_name in ("HairStrandsFactory", "GroomImportFactory", "AlembicImportFactory"):
        cls = getattr(unreal, class_name, None)
        if cls is None:
            result.setdefault("factoryCandidates", []).append(
                {"className": class_name, "available": False, "constructable": False, "error": "missing"}
            )
            continue
        try:
            factory = cls()
            result.setdefault("factoryCandidates", []).append(
                {"className": class_name, "available": True, "constructable": True, "selected": True, "error": None}
            )
            result["factoryClass"] = class_name
            return factory
        except Exception as exc:
            result.setdefault("factoryCandidates", []).append(
                {"className": class_name, "available": True, "constructable": False, "selected": False, "error": str(exc)}
            )
            result["errors"].append("%s_construct_failed:%s" % (class_name, exc))
    result["errors"].append("no_constructable_hair_groom_or_alembic_factory")
    return None


def _build_import_options(unreal, result: Dict[str, Any]):
    for class_name in ("GroomImportOptions", "GroomCacheImportOptions", "AbcImportSettings"):
        cls = getattr(unreal, class_name, None)
        if cls is None:
            continue
        try:
            options = cls()
            result["optionsClass"] = class_name
            result["optionProperties"] = [name for name in dir(options) if "groom" in name.lower() or "import" in name.lower()][:80]
            return options
        except Exception as exc:
            result["errors"].append("%s_construct_failed:%s" % (class_name, exc))
    result["optionProperties"] = []
    return None


def _execute_binding(unreal, expected_groom: str, expected_binding: str, target_mesh: str, errors: List[str]) -> Dict[str, Any]:
    library = getattr(unreal, "GroomLibrary", None)
    candidate_methods = [name for name in dir(library) if "binding" in name.lower()] if library else []
    result: Dict[str, Any] = {
        "attempted": False,
        "succeeded": False,
        "method": "GroomLibrary.create_new_groom_binding_asset_with_path",
        "methodVisible": False,
        "candidateMethods": candidate_methods,
        "error": None,
        "assetPath": expected_binding,
    }
    method = getattr(library, "create_new_groom_binding_asset_with_path", None) if library else None
    result["methodVisible"] = bool(method)
    if not method:
        return result
    groom_probe = _asset_probe(unreal, expected_groom)
    if groom_probe.get("className") != "GroomAsset":
        result["error"] = "imported_asset_not_GroomAsset:%s" % groom_probe.get("className")
        return result
    groom_asset = unreal.EditorAssetLibrary.load_asset(expected_groom)
    mesh_asset = unreal.EditorAssetLibrary.load_asset(target_mesh)
    if not groom_asset or not mesh_asset:
        result["error"] = "missing_groom_or_target_mesh_for_binding"
        errors.append(result["error"])
        return result
    result["attempted"] = True
    try:
        binding = method(expected_binding, groom_asset, mesh_asset, 100, mesh_asset, 0)
        result["sourceSkeletalMeshForTransfer"] = target_mesh
        result["succeeded"] = bool(binding)
        if binding:
            try:
                unreal.EditorAssetLibrary.save_loaded_asset(binding)
            except Exception as exc:
                result["error"] = "save_binding_failed:%s" % exc
                errors.append(result["error"])
    except Exception as exc:
        result["error"] = str(exc)
        errors.append("create_groom_binding_failed:%s" % exc)
    return result


def _rollback_created_assets(unreal, editor_assets, created_assets: List[str], destination: str, directory_created: bool, errors: List[str]) -> Dict[str, Any]:
    deleted_assets = []
    delete_errors = []
    for path in sorted(set(_package_path(path) for path in created_assets if path), reverse=True):
        if not path.startswith("/Game/AI_Tool_TA/"):
            delete_errors.append("refuse_delete_outside_public_scope:%s" % path)
            continue
        if not editor_assets.does_asset_exist(path):
            continue
        try:
            if editor_assets.delete_asset(path):
                deleted_assets.append(path)
            else:
                delete_errors.append("delete_asset_returned_false:%s" % path)
        except Exception as exc:
            delete_errors.append("delete_asset_failed:%s:%s" % (path, exc))
    directory_deleted = False
    if directory_created:
        try:
            directory_deleted = bool(editor_assets.delete_directory(destination))
        except Exception as exc:
            delete_errors.append("delete_directory_failed:%s:%s" % (destination, exc))
    _scan_registry(unreal, ["/Game/AI_Tool_TA"])
    residual_assets = [path for path in sorted(set(created_assets)) if path and editor_assets.does_asset_exist(_package_path(path))]
    if delete_errors:
        errors.extend(delete_errors)
    return {
        "passed": not residual_assets and not delete_errors,
        "deletedAssets": deleted_assets,
        "directoryCreated": directory_created,
        "directoryDeleted": directory_deleted,
        "residualAssets": residual_assets,
        "residualAssetCount": len(residual_assets),
        "writeCount": len(deleted_assets) + (1 if directory_deleted else 0),
        "errors": delete_errors,
        "actions": [{"id": "delete-created-groom-asset:%s" % _asset_name(path), "kind": "delete_asset", "path": path} for path in deleted_assets],
    }


def _created_asset_paths(preflight: Dict[str, Any], post: Dict[str, Any], import_task: Dict[str, Any], expected_groom: str, expected_binding: str) -> List[str]:
    rows = []
    for path, key in [(expected_groom, "expectedGroomAsset"), (expected_binding, "expectedBindingAsset")]:
        if post.get(key, {}).get("exists") and not preflight.get(key, {}).get("exists"):
            rows.append(path)
    for path in import_task.get("createdAssets", []) + import_task.get("importedObjectPaths", []):
        package_path = _package_path(path)
        if package_path and package_path.startswith("/Game/AI_Tool_TA/"):
            rows.append(package_path)
    return sorted(set(rows))


def _asset_probe(unreal, path: str) -> Dict[str, Any]:
    if not path:
        return {"path": path, "exists": False, "className": None, "fingerprint": None, "error": "empty_path"}
    editor_assets = unreal.EditorAssetLibrary
    package_path = _package_path(path)
    row = {"path": package_path, "exists": False, "className": None, "fingerprint": None, "error": None}
    try:
        row["exists"] = bool(editor_assets.does_asset_exist(package_path))
        if row["exists"]:
            asset_data = editor_assets.find_asset_data(package_path)
            row["className"] = _asset_class_name(asset_data)
            row["fingerprint"] = _fingerprint(row)
    except Exception as exc:
        row["error"] = str(exc)
    return row


def _directory_probe(editor_assets, path: str) -> Dict[str, Any]:
    row = {"path": path, "exists": False, "error": None}
    try:
        row["exists"] = bool(editor_assets.does_directory_exist(path))
    except Exception as exc:
        row["error"] = str(exc)
    return row


def _make_directory(editor_assets, path: str, errors: List[str]) -> bool:
    try:
        return bool(editor_assets.make_directory(path))
    except Exception as exc:
        errors.append("make_directory_failed:%s:%s" % (path, exc))
        return False


def _set_property(obj, name: str, value: Any, result: Dict[str, Any]) -> bool:
    row = {"property": name, "set": False, "error": None}
    try:
        obj.set_editor_property(name, value)
        row["set"] = True
    except Exception as exc:
        row["error"] = str(exc)
        result.setdefault("errors", []).append("set_%s_failed:%s" % (name, exc))
    result.setdefault("propertyRows", []).append(row)
    return bool(row["set"])


def _imported_object_paths(task) -> List[str]:
    for name in ("imported_object_paths", "importedObjectPaths"):
        try:
            value = task.get_editor_property(name)
            if value:
                return [_package_path(str(path)) for path in value]
        except Exception:
            pass
    value = getattr(task, "imported_object_paths", None)
    return [_package_path(str(path)) for path in value] if value else []


def _scan_registry(unreal, paths: List[str]) -> None:
    try:
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(paths, force_rescan=True)
    except Exception:
        pass


def _engine_version(unreal) -> str:
    try:
        return unreal.SystemLibrary.get_engine_version()
    except Exception:
        return "unknown"


def _asset_class_name(asset_data) -> Optional[str]:
    if not asset_data:
        return None
    try:
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        try:
            return str(asset_data.asset_class)
        except Exception:
            return None


def _asset_dir(path: str) -> str:
    package_path = _package_path(path)
    if "/" not in package_path:
        return ""
    return package_path.rsplit("/", 1)[0]


def _asset_name(path: str) -> str:
    package_path = _package_path(path)
    return package_path.rsplit("/", 1)[-1]


def _package_path(path: str) -> str:
    value = str(path or "")
    if "." in value:
        left, right = value.rsplit(".", 1)
        if "/" not in right:
            return left
    return value


def _sha256(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fingerprint(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


_main()
