from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_OUTPUT"])
    plan_path = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_PLAN"])
    inspector_root = Path(os.environ["AI_TOOL_TA_UNREAL_INSPECTOR_ROOT"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from platform_variant_forge.runtime_contract import build_runtime_report

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    asset_writes = _ensure_source_fixture(unreal, inspector_root)
    asset_writes += _ensure_planned_fixture_variants(unreal, plan)
    facts = _collect_plan_facts(unreal, plan)
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _engine_version(unreal),
            "pythonVersion": sys.version,
            "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "assetWrites": asset_writes,
            "writeScope": "/Game/AI_Tool_TA public test fixture only",
        },
        "facts": facts,
    }
    report = build_runtime_report(plan_path, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_PLATFORM_VARIANT_OUTPUT=%s" % output_path)


def _ensure_source_fixture(unreal, inspector_root: Path) -> int:
    source_path = inspector_root / "fixtures" / "unreal_sources" / "SM_HeroPanel_A.obj"
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    editor_assets = unreal.EditorAssetLibrary
    writes = 0
    if not editor_assets.does_asset_exist("/Game/AI_Tool_TA/Materials/M_HeroPanel"):
        material = asset_tools.create_asset(
            "M_HeroPanel",
            "/Game/AI_Tool_TA/Materials",
            unreal.Material,
            unreal.MaterialFactoryNew(),
        )
        if material:
            editor_assets.save_loaded_asset(material)
            writes += 1
    if not editor_assets.does_asset_exist("/Game/AI_Tool_TA/Props/SM_HeroPanel_A"):
        task = unreal.AssetImportTask()
        task.filename = str(source_path)
        task.destination_path = "/Game/AI_Tool_TA/Props"
        task.destination_name = "SM_HeroPanel_A"
        task.automated = True
        task.replace_existing = True
        task.save = True
        asset_tools.import_asset_tasks([task])
        if editor_assets.does_asset_exist("/Game/AI_Tool_TA/Props/SM_HeroPanel_A"):
            writes += 1
    source_mesh = editor_assets.load_asset("/Game/AI_Tool_TA/Props/SM_HeroPanel_A")
    material = editor_assets.load_asset("/Game/AI_Tool_TA/Materials/M_HeroPanel")
    if source_mesh and material and hasattr(source_mesh, "set_material"):
        before = _material_slot_facts(source_mesh)
        assigned = any(path and path.startswith("/Game/AI_Tool_TA/Materials/M_HeroPanel") for path in before["materialPaths"])
        if not assigned:
            source_mesh.set_material(0, material)
            editor_assets.save_loaded_asset(source_mesh)
            writes += 1
    return writes


def _ensure_planned_fixture_variants(unreal, plan: dict) -> int:
    editor_assets = unreal.EditorAssetLibrary
    writes = 0
    for asset in plan.get("facts", {}).get("assets", []):
        source_path = asset.get("sourceAsset", {}).get("enginePath")
        if asset.get("assetId") != "variant-hero-panel-001":
            continue
        for variant in asset.get("variants", []):
            target_path = variant.get("targetEnginePath")
            if not source_path or not target_path or editor_assets.does_asset_exist(target_path):
                continue
            target_dir = str(target_path).rsplit("/", 1)[0]
            editor_assets.make_directory(target_dir)
            duplicated = editor_assets.duplicate_asset(source_path, target_path)
            if duplicated:
                editor_assets.save_loaded_asset(duplicated)
                writes += 1
    return writes


def _collect_plan_facts(unreal, plan: dict) -> dict:
    paths = set()
    for asset in plan.get("facts", {}).get("assets", []):
        source_path = asset.get("sourceAsset", {}).get("enginePath")
        if source_path:
            paths.add(source_path)
        for variant in asset.get("variants", []):
            target_path = variant.get("targetEnginePath")
            if target_path:
                paths.add(target_path)
    return {path: _inspect_static_mesh(unreal, path) for path in sorted(paths)}


def _inspect_static_mesh(unreal, asset_path: str) -> dict:
    editor_assets = unreal.EditorAssetLibrary
    exists = bool(editor_assets.does_asset_exist(asset_path))
    asset_data = editor_assets.find_asset_data(asset_path) if exists else None
    static_mesh = editor_assets.load_asset(asset_path) if exists else None
    class_name = None
    if exists:
        try:
            class_name = str(asset_data.asset_class_path.asset_name)
        except Exception:
            class_name = str(asset_data.asset_class)
    lod = _lod_facts(unreal, static_mesh)
    collision = _collision_facts(unreal, static_mesh)
    material = _material_slot_facts(static_mesh)
    return {
        "assetPath": asset_path,
        "exists": exists,
        "className": class_name,
        "pathMatched": asset_path.startswith("/Game/AI_Tool_TA/"),
        "lodCount": lod.get("lodCount"),
        "vertexCount": lod.get("lod0VertexCount"),
        "triangleCount": lod.get("lod0TriangleCount"),
        "materialSlotCount": material.get("slotCount"),
        "materialPaths": material.get("materialPaths"),
        "simpleShapeCount": collision.get("simpleShapeCount"),
        "complexAsSimple": collision.get("complexAsSimple"),
        "collisionTraceFlag": collision.get("collisionTraceFlag"),
        "naniteEnabled": _nanite_enabled(static_mesh),
        "raw": {
            "lod": lod,
            "material": material,
            "collision": collision,
        },
    }


def _lod_facts(unreal, static_mesh) -> dict:
    if not static_mesh:
        return {"lodCount": 0, "lod0VertexCount": 0, "lod0TriangleCount": 0}
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
    return {
        "lodCount": lod_count or 0,
        "lodScreenSizes": _jsonable_list(lod_screen_sizes),
        "sourceModelCount": source_model_count,
        "lod0VertexCount": vertex_count or 0,
        "lod0TriangleCount": triangle_count or 0,
    }


def _collision_facts(unreal, static_mesh) -> dict:
    if not static_mesh:
        return {"simpleShapeCount": 0, "complexAsSimple": False, "collisionTraceFlag": None}
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
    return {
        "simpleShapeCount": simple_shape_count,
        "shapeCounts": shape_counts,
        "collisionTraceFlag": collision_trace_flag,
        "complexAsSimple": "COMPLEX_AS_SIMPLE" in str(collision_trace_flag or "").upper(),
    }


def _material_slot_facts(static_mesh) -> dict:
    if not static_mesh:
        return {"slotCount": 0, "materialPaths": [], "rows": []}
    static_materials = _editor_property(static_mesh, "static_materials") or []
    rows = []
    material_paths = []
    for index, slot in enumerate(static_materials):
        material = _editor_property(slot, "material_interface")
        material_path = _object_path(material)
        if material_path:
            material_paths.append(material_path)
        rows.append({"index": index, "materialPath": material_path})
    return {"slotCount": len(rows), "materialPaths": material_paths, "rows": rows}


def _nanite_enabled(static_mesh):
    if not static_mesh:
        return None
    settings = _editor_property(static_mesh, "nanite_settings")
    enabled = _editor_property(settings, "enabled") if settings else None
    return bool(enabled) if enabled is not None else None


def _engine_version(unreal) -> str:
    try:
        return unreal.SystemLibrary.get_engine_version()
    except Exception:
        return "unknown"


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


_main()
