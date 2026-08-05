from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_GROOM_EXPORT_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_GROOM_ALEMBIC_POSTCHECK_OUTPUT"])
    source_payload = Path(os.environ["AI_TOOL_TA_GROOM_ALEMBIC_POSTCHECK_SOURCE"])
    fixture_path = Path(os.environ["AI_TOOL_TA_GROOM_ALEMBIC_FIXTURE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from groom_export_inspector.alembic_import_postcheck import (
        build_groom_alembic_import_postcheck_report,
        public_path,
        resolve_public_path,
    )

    source = json.loads(source_payload.read_text(encoding="utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture_assets = {str(row.get("id")): row for row in fixture.get("assets", [])}
    api = _api_probe(unreal)
    assets = [
        _probe_operation(unreal, operation, fixture_assets.get(str(operation.get("assetId")), {}), api, resolve_public_path, public_path)
        for operation in source.get("facts", {}).get("operations", [])
    ]
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "read-only Groom Alembic import/post-check probe; no import and no asset save",
        },
        "api": api,
        "assets": assets,
    }
    report = build_groom_alembic_import_postcheck_report(source_payload, fixture_path, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_GROOM_ALEMBIC_POSTCHECK_OUTPUT=%s" % output_path)


def _probe_operation(unreal, operation: Dict[str, Any], fixture_asset: Dict[str, Any], api: Dict[str, Any], resolve_public_path, public_path) -> Dict[str, Any]:
    asset_id = str(operation.get("assetId"))
    source_cache = operation.get("cache", {})
    cache = _cache_facts(source_cache.get("path"), resolve_public_path, public_path)
    unreal_targets = fixture_asset.get("unreal", {})
    target_mesh = str(unreal_targets.get("targetSkeletalMesh") or "")
    expected_groom = str(unreal_targets.get("expectedGroomAsset") or "")
    expected_binding = str(unreal_targets.get("expectedBindingAsset") or "")
    destination = _asset_dir(expected_groom) or "/Game/AI_Tool_TA/Grooms"
    return {
        "assetId": asset_id,
        "assetLabel": operation.get("assetLabel"),
        "cache": cache,
        "targetSkeletalMesh": _asset_probe(unreal, target_mesh),
        "expectedGroomAsset": _asset_probe(unreal, expected_groom),
        "expectedBindingAsset": _asset_probe(unreal, expected_binding),
        "importTaskDryRun": _import_task_dry_run(unreal, cache, destination, api),
        "importExecuted": False,
        "heldReason": "readiness_probe_no_write",
        "assetWrites": 0,
        "engineWrites": 0,
        "productionWrites": 0,
    }


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "AssetImportTask",
        "AssetToolsHelpers",
        "AutomatedAssetImportData",
        "Factory",
        "HairStrandsFactory",
        "AlembicImportFactory",
        "AlembicImportSettings",
        "AlembicImportType",
        "GroomAsset",
        "GroomBindingAsset",
        "GroomCache",
        "GroomCacheImportOptions",
        "GroomImportFactory",
        "GroomImportOptions",
        "EditorAssetLibrary",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    instantiation = {
        "AssetImportTask": _instantiate(unreal, "AssetImportTask"),
        "AlembicImportFactory": _instantiate(unreal, "AlembicImportFactory"),
        "AlembicImportSettings": _instantiate(unreal, "AlembicImportSettings"),
        "GroomImportFactory": _instantiate(unreal, "GroomImportFactory"),
        "GroomImportOptions": _instantiate(unreal, "GroomImportOptions"),
        "GroomCacheImportOptions": _instantiate(unreal, "GroomCacheImportOptions"),
    }
    groom_class_names = _class_names(unreal, ["groom"])
    hair_class_names = _class_names(unreal, ["hair", "strand"])
    alembic_class_names = _class_names(unreal, ["alembic", "abc"])
    plugins = {
        "Groom": _plugin_enabled(unreal, "Groom"),
        "HairStrands": _plugin_enabled(unreal, "HairStrands"),
        "AlembicImporter": _plugin_enabled(unreal, "AlembicImporter"),
    }
    return {
        "classes": classes,
        "instantiation": instantiation,
        "plugins": plugins,
        "groomClassNames": groom_class_names[:160],
        "hairClassNames": hair_class_names[:160],
        "alembicClassNames": alembic_class_names[:160],
        "groomApiVisible": bool(classes.get("GroomAsset") or groom_class_names),
        "groomBindingApiVisible": bool(classes.get("GroomBindingAsset") or any("binding" in name.lower() for name in groom_class_names)),
        "importTaskVisible": bool(classes.get("AssetImportTask")),
        "assetToolsVisible": bool(classes.get("AssetToolsHelpers")),
        "groomImportFactoryVisible": bool(classes.get("GroomImportFactory")),
        "hairStrandsFactoryVisible": bool(classes.get("HairStrandsFactory")),
        "alembicImportFactoryVisible": bool(classes.get("AlembicImportFactory")),
        "groomImportOptionsVisible": bool(classes.get("GroomImportOptions") or classes.get("GroomCacheImportOptions")),
    }


def _import_task_dry_run(unreal, cache: Dict[str, Any], destination: str, api: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "taskConstructed": False,
        "destination": destination,
        "factoryClass": None,
        "propertyRows": [],
        "errors": [],
    }
    if not api.get("importTaskVisible"):
        result["errors"].append("AssetImportTask_missing")
        return result
    try:
        task = unreal.AssetImportTask()
        result["taskConstructed"] = True
    except Exception as exc:
        result["errors"].append("AssetImportTask_construct_failed:%s" % exc)
        return result
    _set_property(task, "filename", str(cache.get("localPath") or ""), result)
    _set_property(task, "destination_path", destination, result)
    _set_property(task, "automated", True, result)
    _set_property(task, "replace_existing", False, result)
    _set_property(task, "save", False, result)
    factory = _build_factory(unreal, api, result)
    if factory is not None:
        _set_property(task, "factory", factory, result)
    return result


def _build_factory(unreal, api: Dict[str, Any], result: Dict[str, Any]):
    for class_name in ("HairStrandsFactory", "GroomImportFactory", "AlembicImportFactory"):
        if not api.get("classes", {}).get(class_name):
            result.setdefault("factoryCandidates", []).append(
                {"className": class_name, "available": False, "constructable": False, "error": "missing"}
            )
            continue
        try:
            factory = getattr(unreal, class_name)()
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


def _asset_probe(unreal, path: str) -> Dict[str, Any]:
    if not path:
        return {"path": path, "exists": False, "assetClass": None, "error": "empty_path"}
    row = {"path": path, "exists": False, "assetClass": None, "error": None}
    try:
        row["exists"] = bool(unreal.EditorAssetLibrary.does_asset_exist(path))
        if row["exists"]:
            row["assetClass"] = _asset_class(unreal, path)
    except Exception as exc:
        row["error"] = str(exc)
    return row


def _asset_class(unreal, path: str) -> Optional[str]:
    try:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(path)
        if not asset_data or not asset_data.is_valid():
            return None
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return None


def _cache_facts(path: Any, resolve_public_path, public_path) -> Dict[str, Any]:
    resolved = resolve_public_path(path)
    exists = resolved.exists()
    size = resolved.stat().st_size if exists else 0
    return {
        "path": public_path(resolved) if str(path or "") else None,
        "localPath": str(resolved),
        "exists": exists,
        "bytes": size,
        "sha256": _sha256(resolved) if exists and size > 0 else None,
    }


def _sha256(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _instantiate(unreal, class_name: str) -> Dict[str, Any]:
    if not hasattr(unreal, class_name):
        return {"available": False, "constructable": False, "error": "missing"}
    try:
        getattr(unreal, class_name)()
        return {"available": True, "constructable": True, "error": None}
    except Exception as exc:
        return {"available": True, "constructable": False, "error": str(exc)}


def _plugin_enabled(unreal, plugin_name: str) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for owner_name, method_name in (
        ("PluginBlueprintLibrary", "is_plugin_enabled"),
        ("Plugins", "is_plugin_enabled"),
    ):
        owner = getattr(unreal, owner_name, None)
        method = getattr(owner, method_name, None) if owner else None
        if not method:
            continue
        row = {"api": "%s.%s" % (owner_name, method_name), "available": True, "enabled": None, "error": None}
        try:
            row["enabled"] = bool(method(plugin_name))
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
        if row["enabled"] is True:
            break
    return {"queried": bool(rows), "enabled": any(row.get("enabled") is True for row in rows), "rows": rows}


def _class_names(unreal, terms: List[str]) -> List[str]:
    names = []
    for name in dir(unreal):
        lowered = name.lower()
        if any(term in lowered for term in terms):
            names.append(name)
    return sorted(names)


def _asset_dir(path: str) -> str:
    if "/" not in path:
        return ""
    return path.rsplit("/", 1)[0]


def _safe(func, fallback):
    try:
        return func()
    except Exception:
        return fallback


_main()
