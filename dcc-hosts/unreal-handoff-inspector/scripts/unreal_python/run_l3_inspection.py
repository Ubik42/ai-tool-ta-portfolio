from __future__ import annotations

import json
import os
import sys
from pathlib import Path


EXPECTED_FIXTURE_ASSETS = [
    {
        "path": "/Game/AI_Tool_TA/Props/SM_HeroPanel_A",
        "class": "StaticMesh",
        "role": "ready_import_target",
    },
    {
        "path": "/Game/AI_Tool_TA/Materials/M_HeroPanel",
        "class": "Material",
        "role": "ready_material_dependency",
    },
]


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_INSPECTOR_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_L3_OUTPUT"])
    fixture_path = root / "fixtures" / "synthetic_unreal_handoff.json"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_handoff_inspector.contract import build_report

    fixture_assets_snapshot = _ensure_fixture_assets(unreal, root)
    engine_facts_snapshot = _inspect_engine_facts(unreal, root)
    asset_registry_snapshot = {
        "queried": False,
        "gameAssetCount": 0,
        "error": None,
    }
    try:
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        assets = registry.get_assets_by_path("/Game", recursive=True)
        asset_registry_snapshot = {
            "queried": True,
            "gameAssetCount": len(assets),
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
        asset_registry_snapshot["error"] = str(exc)

    try:
        engine_version = unreal.SystemLibrary.get_engine_version()
    except Exception:
        engine_version = "unknown"

    runtime_snapshot = {
        "executed": True,
        "runtime": "Unreal Python",
        "engineVersion": engine_version,
        "pythonVersion": sys.version,
        "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
        "assetRegistry": asset_registry_snapshot,
        "fixtureAssets": fixture_assets_snapshot,
        "engineFacts": engine_facts_snapshot,
        "mutation": {
            "engineWrites": 0,
            "assetWrites": fixture_assets_snapshot.get("assetWrites", 0) + engine_facts_snapshot.get("assetWrites", 0),
            "savePackage": fixture_assets_snapshot.get("assetWrites", 0) + engine_facts_snapshot.get("assetWrites", 0) > 0,
            "writeScope": "/Game/AI_Tool_TA public test fixture only",
        },
    }
    report = build_report(
        fixture_path,
        unreal_cli_available=True,
        unreal_cli_path=os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
        unreal_project_path=os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
        unreal_python_executed=True,
        runtime_snapshot=runtime_snapshot,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_L3_OUTPUT=%s" % output_path)


def _ensure_fixture_assets(unreal, root: Path) -> dict:
    source_path = root / "fixtures" / "unreal_sources" / "SM_HeroPanel_A.obj"
    source_files = [str(source_path)]
    asset_writes = 0
    errors = []

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    editor_assets = unreal.EditorAssetLibrary

    if not editor_assets.does_asset_exist("/Game/AI_Tool_TA/Materials/M_HeroPanel"):
        try:
            material = asset_tools.create_asset(
                "M_HeroPanel",
                "/Game/AI_Tool_TA/Materials",
                unreal.Material,
                unreal.MaterialFactoryNew(),
            )
            if material:
                editor_assets.save_loaded_asset(material)
                asset_writes += 1
        except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
            errors.append("create_material:%s" % exc)

    if not editor_assets.does_asset_exist("/Game/AI_Tool_TA/Props/SM_HeroPanel_A"):
        try:
            task = unreal.AssetImportTask()
            task.filename = str(source_path)
            task.destination_path = "/Game/AI_Tool_TA/Props"
            task.destination_name = "SM_HeroPanel_A"
            task.automated = True
            task.replace_existing = True
            task.save = True
            task.imported_object_paths = []
            asset_tools.import_asset_tasks([task])
            if editor_assets.does_asset_exist("/Game/AI_Tool_TA/Props/SM_HeroPanel_A"):
                asset_writes += 1
        except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
            errors.append("import_static_mesh:%s" % exc)

    try:
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(["/Game/AI_Tool_TA"], force_rescan=True)
    except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
        errors.append("scan_registry:%s" % exc)

    rows = [_inspect_expected_asset(unreal, asset) for asset in EXPECTED_FIXTURE_ASSETS]
    matched = [row for row in rows if row["exists"] and row["classMatches"]]
    missing = [row for row in rows if not row["exists"]]
    class_mismatches = [row for row in rows if row["exists"] and not row["classMatches"]]
    return {
        "fixtureRoot": "/Game/AI_Tool_TA",
        "sourceFiles": source_files,
        "assetWrites": asset_writes,
        "expectedAssetCount": len(EXPECTED_FIXTURE_ASSETS),
        "matchedAssetCount": len(matched),
        "missingAssetCount": len(missing),
        "classMismatchCount": len(class_mismatches),
        "matched": len(matched) == len(EXPECTED_FIXTURE_ASSETS),
        "errors": errors,
        "rows": rows,
    }


def _inspect_expected_asset(unreal, expected: dict) -> dict:
    asset_data = unreal.EditorAssetLibrary.find_asset_data(expected["path"])
    exists = bool(asset_data and asset_data.is_valid())
    class_name = None
    package_name = None
    object_path = None
    if exists:
        try:
            class_name = str(asset_data.asset_class_path.asset_name)
        except Exception:
            class_name = str(asset_data.asset_class)
        package_name = str(asset_data.package_name)
        object_name = str(asset_data.asset_name)
        object_path = "%s.%s" % (package_name, object_name)
    return {
        "path": expected["path"],
        "role": expected["role"],
        "expectedClass": expected["class"],
        "exists": exists,
        "className": class_name,
        "classMatches": class_name == expected["class"],
        "packageName": package_name,
        "objectPath": object_path,
    }


def _inspect_engine_facts(unreal, root: Path) -> dict:
    asset_path = "/Game/AI_Tool_TA/Props/SM_HeroPanel_A"
    material_path = "/Game/AI_Tool_TA/Materials/M_HeroPanel"
    source_path = root / "fixtures" / "unreal_sources" / "SM_HeroPanel_A.obj"
    errors = []
    asset_writes = 0
    editor_assets = unreal.EditorAssetLibrary
    static_mesh = editor_assets.load_asset(asset_path)
    material = editor_assets.load_asset(material_path)
    if not static_mesh:
        return {
            "assetPath": asset_path,
            "assetWrites": 0,
            "expectedFactCount": 4,
            "matchedFactCount": 0,
            "missingFactCount": 4,
            "matched": False,
            "facts": {},
            "rows": [
                _fact_row("source-import-data", False, "StaticMesh fixture asset is missing."),
                _fact_row("material-slot", False, "StaticMesh fixture asset is missing."),
                _fact_row("lod-count", False, "StaticMesh fixture asset is missing."),
                _fact_row("collision-settings", False, "StaticMesh fixture asset is missing."),
            ],
            "errors": ["missing_static_mesh_fixture"],
            "apiProbe": _api_probe(unreal),
        }

    material_assignment = _ensure_material_assignment(unreal, static_mesh, material, material_path)
    asset_writes += material_assignment.get("assetWrites", 0)
    errors.extend(material_assignment.get("errors", []))

    facts = {
        "sourceImportData": _source_import_data(static_mesh, source_path),
        "materialSlots": _material_slot_facts(static_mesh, material_path),
        "lod": _lod_facts(unreal, static_mesh),
        "collision": _collision_facts(unreal, static_mesh),
    }
    rows = [
        _fact_row(
            "source-import-data",
            facts["sourceImportData"].get("sourceFileMatched", False),
            "sourceFiles=%s expected=%s" % (",".join(facts["sourceImportData"].get("sourceFiles", [])), source_path),
        ),
        _fact_row(
            "material-slot",
            facts["materialSlots"].get("expectedMaterialAssigned", False),
            "slots=%s assigned=%s" % (
                facts["materialSlots"].get("slotCount"),
                ",".join(facts["materialSlots"].get("materialPaths", [])),
            ),
        ),
        _fact_row(
            "lod-count",
            int(facts["lod"].get("lodCount") or 0) >= 1,
            "lodCount=%s sourceModelCount=%s" % (facts["lod"].get("lodCount"), facts["lod"].get("sourceModelCount")),
        ),
        _fact_row(
            "collision-settings",
            facts["collision"].get("bodySetupPresent", False) and facts["collision"].get("collisionTraceFlag") is not None,
            "bodySetup=%s trace=%s simpleShapes=%s" % (
                facts["collision"].get("bodySetupPresent"),
                facts["collision"].get("collisionTraceFlag"),
                facts["collision"].get("simpleShapeCount"),
            ),
        ),
    ]
    matched = [row for row in rows if row["matched"]]
    return {
        "assetPath": asset_path,
        "assetWrites": asset_writes,
        "expectedFactCount": len(rows),
        "matchedFactCount": len(matched),
        "missingFactCount": len(rows) - len(matched),
        "matched": len(matched) == len(rows),
        "facts": facts,
        "rows": rows,
        "errors": errors,
        "apiProbe": _api_probe(unreal),
    }


def _ensure_material_assignment(unreal, static_mesh, material, material_path: str) -> dict:
    errors = []
    asset_writes = 0
    if not material:
        return {"assetWrites": asset_writes, "errors": ["missing_material_fixture"]}
    before = _material_slot_facts(static_mesh, material_path)
    if before.get("expectedMaterialAssigned"):
        return {"assetWrites": asset_writes, "errors": errors}
    try:
        if hasattr(static_mesh, "set_material"):
            static_mesh.set_material(0, material)
            unreal.EditorAssetLibrary.save_loaded_asset(static_mesh)
            asset_writes += 1
        else:
            errors.append("static_mesh_set_material_unavailable")
    except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
        errors.append("assign_material:%s" % exc)
    return {"assetWrites": asset_writes, "errors": errors}


def _source_import_data(static_mesh, expected_source: Path) -> dict:
    errors = []
    source_files = []
    asset_import_data = _editor_property(static_mesh, "asset_import_data")
    if asset_import_data:
        try:
            if hasattr(asset_import_data, "extract_filenames"):
                source_files = [str(path) for path in asset_import_data.extract_filenames()]
            else:
                errors.append("extract_filenames_unavailable")
        except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
            errors.append("extract_filenames:%s" % exc)
    else:
        errors.append("asset_import_data_missing")
    normalized_expected = _norm_path(str(expected_source))
    matched = any(_norm_path(path).endswith(normalized_expected) or _norm_path(path) == normalized_expected for path in source_files)
    return {
        "assetImportDataPresent": bool(asset_import_data),
        "sourceFiles": source_files,
        "expectedSourceFile": str(expected_source),
        "sourceFileMatched": matched,
        "errors": errors,
    }


def _material_slot_facts(static_mesh, expected_material_path: str) -> dict:
    static_materials = _editor_property(static_mesh, "static_materials") or []
    rows = []
    material_paths = []
    for index, slot in enumerate(static_materials):
        slot_name = _stringify(_editor_property(slot, "material_slot_name"))
        material = _editor_property(slot, "material_interface")
        material_path = _object_path(material)
        if material_path:
            material_paths.append(material_path)
        rows.append(
            {
                "index": index,
                "slotName": slot_name,
                "materialPath": material_path,
            }
        )
    return {
        "slotCount": len(rows),
        "expectedMaterialPath": expected_material_path,
        "expectedMaterialAssigned": any(path and path.startswith(expected_material_path) for path in material_paths),
        "materialPaths": material_paths,
        "rows": rows,
    }


def _lod_facts(unreal, static_mesh) -> dict:
    errors = []
    raw_library_lod_count = _call_static_mesh_library(unreal, "get_lod_count", static_mesh)
    raw_method_lod_count = _call_method(static_mesh, "get_num_lods")
    lod_screen_sizes = _call_static_mesh_library(unreal, "get_lod_screen_sizes", static_mesh)
    lod0_build_settings = _call_static_mesh_library(unreal, "get_lod_build_settings", static_mesh, 0)
    source_models = _editor_property(static_mesh, "source_models")
    source_model_count = len(source_models) if source_models is not None else None
    vertex_count = _call_static_mesh_library(unreal, "get_number_verts", static_mesh, 0)
    triangle_count = _call_static_mesh_library(unreal, "get_number_triangles", static_mesh, 0)
    lod_count = _first_positive_int(
        raw_library_lod_count,
        raw_method_lod_count,
        len(lod_screen_sizes) if lod_screen_sizes is not None else None,
        source_model_count,
        1 if lod0_build_settings is not None else None,
    )
    if lod_count is None:
        errors.append("lod_count_unavailable")
    return {
        "lodCount": lod_count,
        "rawLibraryLodCount": raw_library_lod_count,
        "rawMethodLodCount": raw_method_lod_count,
        "lodScreenSizes": _jsonable_list(lod_screen_sizes),
        "lod0BuildSettingsAvailable": lod0_build_settings is not None,
        "sourceModelCount": source_model_count,
        "lod0VertexCount": vertex_count,
        "lod0TriangleCount": triangle_count,
        "errors": errors,
    }


def _collision_facts(unreal, static_mesh) -> dict:
    errors = []
    body_setup = _editor_property(static_mesh, "body_setup")
    collision_trace_flag = _stringify(_editor_property(body_setup, "collision_trace_flag")) if body_setup else None
    agg_geom = _editor_property(body_setup, "agg_geom") if body_setup else None
    shape_counts = {}
    if agg_geom:
        for prop in ("box_elems", "sphere_elems", "sphyl_elems", "convex_elems", "tapered_capsule_elems"):
            value = _editor_property(agg_geom, prop)
            if value is not None:
                shape_counts[prop] = len(value)
    simple_shape_count = sum(shape_counts.values()) if shape_counts else 0
    complexity = _call_static_mesh_library(unreal, "get_collision_complexity", static_mesh)
    convex_count = _call_static_mesh_library(unreal, "get_convex_collision_count", static_mesh)
    if body_setup and collision_trace_flag is None:
        errors.append("collision_trace_flag_unavailable")
    return {
        "bodySetupPresent": bool(body_setup),
        "collisionTraceFlag": collision_trace_flag,
        "simpleShapeCount": simple_shape_count,
        "shapeCounts": shape_counts,
        "editorStaticMeshLibraryCollisionComplexity": _stringify(complexity),
        "editorStaticMeshLibraryConvexCount": convex_count,
        "errors": errors,
    }


def _fact_row(check_id: str, matched: bool, evidence: str) -> dict:
    return {
        "id": check_id,
        "matched": bool(matched),
        "evidence": evidence,
    }


def _api_probe(unreal) -> dict:
    library = getattr(unreal, "EditorStaticMeshLibrary", None)
    names = []
    if library:
        names = [
            name
            for name in dir(library)
            if "lod" in name.lower()
            or "material" in name.lower()
            or "collision" in name.lower()
            or "triangle" in name.lower()
            or "vert" in name.lower()
        ]
    return {
        "editorStaticMeshLibraryAvailable": bool(library),
        "editorStaticMeshLibraryMethods": sorted(names),
    }


def _call_static_mesh_library(unreal, method_name: str, *args):
    library = getattr(unreal, "EditorStaticMeshLibrary", None)
    if not library or not hasattr(library, method_name):
        return None
    try:
        return getattr(library, method_name)(*args)
    except Exception:
        return None


def _call_method(target, method_name: str):
    if not target or not hasattr(target, method_name):
        return None
    try:
        return getattr(target, method_name)()
    except Exception:
        return None


def _first_positive_int(*values):
    for value in values:
        try:
            number = int(value)
        except (TypeError, ValueError):
            continue
        if number > 0:
            return number
    return None


def _jsonable_list(value):
    if value is None:
        return None
    try:
        return [float(item) for item in value]
    except Exception:
        try:
            return [str(item) for item in value]
        except Exception:
            return str(value)


def _editor_property(target, prop: str):
    if not target:
        return None
    try:
        return target.get_editor_property(prop)
    except Exception:
        return None


def _object_path(obj) -> str | None:
    if not obj:
        return None
    try:
        return str(obj.get_path_name())
    except Exception:
        return str(obj)


def _stringify(value) -> str | None:
    if value is None:
        return None
    return str(value)


def _norm_path(path: str) -> str:
    return path.replace("\\", "/").lower()


_main()
