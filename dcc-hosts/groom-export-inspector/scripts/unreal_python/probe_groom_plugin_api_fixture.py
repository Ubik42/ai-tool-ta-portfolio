from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict

import unreal


def main() -> None:
    output_path = os.environ["AI_TOOL_TA_GROOM_PLUGIN_API_RUNTIME"]
    class_names = dir(unreal)
    classes = {
        name: hasattr(unreal, name)
        for name in [
            "AssetImportTask",
            "AssetToolsHelpers",
            "EditorAssetLibrary",
            "Factory",
            "AbcImportSettings",
            "AlembicImportFactory",
            "AlembicImportSettings",
            "AlembicImportType",
            "GeometryCache",
            "GeometryCacheComponent",
            "GroomAsset",
            "GroomBindingAsset",
            "GroomCache",
            "GroomComponent",
            "GroomCacheImportOptions",
            "GroomImportFactory",
            "GroomImportOptions",
            "HairStrandsComponent",
        ]
    }
    snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": unreal.SystemLibrary.get_engine_version(),
            "pythonVersion": sys.version,
            "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "read-only Groom plugin/API fixture probe; no import and no asset save",
        },
        "api": {
            "classes": classes,
            "instantiation": {
                "AbcImportSettings": _instantiate("AbcImportSettings"),
                "AlembicImportFactory": _instantiate("AlembicImportFactory"),
                "AlembicImportSettings": _instantiate("AlembicImportSettings"),
                "GroomImportFactory": _instantiate("GroomImportFactory"),
                "GroomImportOptions": _instantiate("GroomImportOptions"),
                "GroomCacheImportOptions": _instantiate("GroomCacheImportOptions"),
            },
            "plugins": {
                "GeometryCache": _plugin_enabled("GeometryCache"),
                "AlembicImporter": _plugin_enabled("AlembicImporter"),
                "HairStrands": _plugin_enabled("HairStrands"),
                "AlembicHairImporter": _plugin_enabled("AlembicHairImporter"),
            },
            "classNames": {
                "groom": sorted(name for name in class_names if "Groom" in name),
                "hair": sorted(name for name in class_names if "Hair" in name or "Strand" in name),
                "alembic": sorted(name for name in class_names if "Alembic" in name or name.startswith("Abc")),
                "geometryCache": sorted(name for name in class_names if "GeometryCache" in name),
            },
        },
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2)


def _instantiate(class_name: str) -> Dict[str, Any]:
    cls = getattr(unreal, class_name, None)
    if cls is None:
        return {"available": False, "constructable": False, "error": "missing"}
    try:
        cls()
    except Exception as exc:
        return {"available": True, "constructable": False, "error": str(exc)}
    return {"available": True, "constructable": True, "error": None}


def _plugin_enabled(plugin_name: str) -> Dict[str, Any]:
    rows = []
    for owner_name, method_name in [
        ("PluginBlueprintLibrary", "is_plugin_enabled"),
        ("Plugins", "is_plugin_enabled"),
    ]:
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
    return {"queried": bool(rows), "enabled": any(row.get("enabled") is True for row in rows), "rows": rows}


main()
