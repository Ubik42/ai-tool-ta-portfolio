from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_GROOM_EXPORT_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_GROOM_UNREAL_READINESS_OUTPUT"])
    source_groom = Path(os.environ["AI_TOOL_TA_GROOM_UNREAL_READINESS_SOURCE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from groom_export_inspector.unreal_readiness import build_unreal_readiness_report, public_path

    source = json.loads(source_groom.read_text(encoding="utf-8"))
    api = _api_probe(unreal)
    assets = [_probe_asset_row(unreal, row) for row in source.get("facts", {}).get("assets", [])]
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": api,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "read-only Groom import readiness probe; no import and no asset save",
        },
        "assets": assets,
    }
    report = build_unreal_readiness_report(source_groom, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_GROOM_UNREAL_READINESS_OUTPUT=%s" % output_path)


def _probe_asset_row(unreal, source_row: Dict[str, Any]) -> Dict[str, Any]:
    normalized = source_row.get("normalized", {})
    target_mesh = str(normalized.get("unreal.targetSkeletalMesh") or "")
    expected_groom = str(normalized.get("unreal.expectedGroomAsset") or "")
    expected_binding = str(normalized.get("unreal.expectedBindingAsset") or "")
    target_probe = _asset_probe(unreal, target_mesh)
    groom_probe = _asset_probe(unreal, expected_groom)
    binding_probe = _asset_probe(unreal, expected_binding)
    errors = []
    for probe in (target_probe, groom_probe, binding_probe):
        if probe.get("error"):
            errors.append({"path": probe.get("path"), "error": probe.get("error")})
    return {
        "assetId": source_row.get("assetId"),
        "assetLabel": source_row.get("assetLabel"),
        "targetSkeletalMesh": target_mesh,
        "targetSkeletalMeshExists": target_probe.get("exists"),
        "targetSkeletalMeshClass": target_probe.get("assetClass"),
        "expectedGroomAsset": expected_groom,
        "expectedGroomAssetExists": groom_probe.get("exists"),
        "expectedGroomAssetClass": groom_probe.get("assetClass"),
        "expectedBindingAsset": expected_binding,
        "expectedBindingAssetExists": binding_probe.get("exists"),
        "expectedBindingAssetClass": binding_probe.get("assetClass"),
        "assetProbeErrors": errors,
    }


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "AssetImportTask",
        "AssetToolsHelpers",
        "AutomatedAssetImportData",
        "AlembicImportFactory",
        "AlembicImportSettings",
        "GroomAsset",
        "GroomBindingAsset",
        "GroomCache",
        "GroomCacheImportOptions",
        "GroomImportFactory",
        "GroomImportOptions",
        "EditorAssetLibrary",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
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
        "plugins": plugins,
        "groomClassNames": groom_class_names[:160],
        "hairClassNames": hair_class_names[:160],
        "alembicClassNames": alembic_class_names[:160],
        "groomApiVisible": bool(classes.get("GroomAsset") or groom_class_names),
        "groomBindingApiVisible": bool(classes.get("GroomBindingAsset") or any("binding" in name.lower() for name in groom_class_names)),
        "importTaskVisible": bool(classes.get("AssetImportTask")),
        "groomImportFactoryVisible": bool(classes.get("GroomImportFactory")),
        "alembicImportFactoryVisible": bool(classes.get("AlembicImportFactory")),
        "groomImportOptionsVisible": bool(classes.get("GroomImportOptions") or classes.get("GroomCacheImportOptions")),
        "assetToolsVisible": bool(classes.get("AssetToolsHelpers")),
    }


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


def _safe(func, fallback):
    try:
        return func()
    except Exception:
        return fallback


_main()
