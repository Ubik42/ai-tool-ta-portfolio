from __future__ import annotations

import json
import os
import struct
import sys
import tempfile
import zlib
from pathlib import Path


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_TEXTURE_OUTPUT"])
    plan_path = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_PLAN"])
    runtime_path = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_RUNTIME"])
    inspector_root = Path(os.environ["AI_TOOL_TA_UNREAL_INSPECTOR_ROOT"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from platform_variant_forge.texture_runtime import build_texture_runtime_report

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    asset_writes = _ensure_source_fixture(unreal, inspector_root)
    asset_writes += _ensure_planned_fixture_variants(unreal, plan)
    payload_result = {"assetWrites": 0, "errors": [], "generatedTextureSource": None}
    payload_mode = os.environ.get("AI_TOOL_TA_PLATFORM_VARIANT_TEXTURE_PAYLOAD") == "1"
    if payload_mode:
        payload_result = _ensure_texture_payload_fixture(unreal)
        asset_writes += payload_result.get("assetWrites", 0)
    facts = _collect_texture_facts(unreal, plan)
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _engine_version(unreal),
            "pythonVersion": sys.version,
            "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "assetWrites": asset_writes,
            "payloadMode": "public_texture_payload_fixture" if payload_mode else "dependency_collection_only",
            "texturePayloadWrites": payload_result.get("assetWrites", 0),
            "texturePayloadErrors": payload_result.get("errors", []),
            "generatedTextureSource": payload_result.get("generatedTextureSource"),
            "writeScope": "/Game/AI_Tool_TA public test fixture only",
        },
        "facts": facts,
    }
    report = build_texture_runtime_report(plan_path, runtime_path, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_PLATFORM_VARIANT_TEXTURE_OUTPUT=%s" % output_path)


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


def _ensure_texture_payload_fixture(unreal) -> dict:
    editor_assets = unreal.EditorAssetLibrary
    texture_source = _generated_png_path()
    texture_package_path = "/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor"
    material_path = "/Game/AI_Tool_TA/Materials/M_HeroPanel"
    writes = 0
    errors = []
    _write_png(texture_source, 2048, 2048)

    if not editor_assets.does_asset_exist(texture_package_path):
        try:
            unreal.EditorAssetLibrary.make_directory("/Game/AI_Tool_TA/Textures")
            task = unreal.AssetImportTask()
            task.filename = str(texture_source)
            task.destination_path = "/Game/AI_Tool_TA/Textures"
            task.destination_name = "T_HeroPanel_BaseColor"
            task.automated = True
            task.replace_existing = True
            task.save = True
            unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
            if editor_assets.does_asset_exist(texture_package_path):
                writes += 1
        except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
            errors.append("import_texture:%s" % exc)

    texture = editor_assets.load_asset(texture_package_path)
    material = editor_assets.load_asset(material_path)
    try:
        if texture:
            texture.set_editor_property("srgb", True)
            editor_assets.save_loaded_asset(texture)
    except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
        errors.append("configure_texture:%s" % exc)

    if material and texture and not _material_references_texture(unreal, material_path, texture_package_path):
        try:
            material_editing = getattr(unreal, "MaterialEditingLibrary", None)
            expression_class = getattr(unreal, "MaterialExpressionTextureSample", None)
            material_property = getattr(getattr(unreal, "MaterialProperty", None), "MP_BASE_COLOR", None)
            if not material_editing or not expression_class or material_property is None:
                errors.append("material_editing_api_unavailable")
            else:
                expression = material_editing.create_material_expression(material, expression_class, -320, 0)
                expression.set_editor_property("texture", texture)
                material_editing.connect_material_property(expression, "RGB", material_property)
                material_editing.recompile_material(material)
                editor_assets.save_loaded_asset(material)
                writes += 1
        except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
            errors.append("wire_texture_to_material:%s" % exc)
    _scan_registry(unreal, ["/Game/AI_Tool_TA"])
    return {
        "assetWrites": writes,
        "errors": errors,
        "generatedTextureSource": r"<runtime-temp>\ai_tool_ta_platform_variant\T_HeroPanel_BaseColor_2048.png",
    }


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


def _collect_texture_facts(unreal, plan: dict) -> dict:
    _scan_registry(unreal, ["/Game/AI_Tool_TA"])
    paths = set()
    for asset in plan.get("facts", {}).get("assets", []):
        source_path = asset.get("sourceAsset", {}).get("enginePath")
        if source_path:
            paths.add(source_path)
        for variant in asset.get("variants", []):
            target_path = variant.get("targetEnginePath")
            if target_path:
                paths.add(target_path)
    return {path: _inspect_static_mesh_texture_graph(unreal, path) for path in sorted(paths)}


def _inspect_static_mesh_texture_graph(unreal, asset_path: str) -> dict:
    editor_assets = unreal.EditorAssetLibrary
    exists = bool(editor_assets.does_asset_exist(asset_path))
    asset_data = editor_assets.find_asset_data(asset_path) if exists else None
    static_mesh = editor_assets.load_asset(asset_path) if exists else None
    class_name = _asset_class_name(asset_data) if exists else None
    material = _material_slot_facts(static_mesh)
    dependency_errors = []
    material_rows = []
    texture_rows_by_path = {}
    dependency_query_count = 0

    for material_path in material.get("materialPaths", []):
        row = _inspect_material_textures(unreal, material_path)
        material_rows.append(row)
        dependency_errors.extend(row.get("errors", []))
        if row.get("dependenciesQueried"):
            dependency_query_count += 1
        for texture_row in row.get("textures", []):
            texture_rows_by_path[texture_row["texturePath"]] = texture_row

    texture_rows = [texture_rows_by_path[path] for path in sorted(texture_rows_by_path)]
    max_dimension = max([_int(row.get("maxDimension")) for row in texture_rows] or [0])
    estimated_memory_mb = sum(float(row.get("estimatedMemoryMb") or 0.0) for row in texture_rows)
    readable_rows = [row for row in texture_rows if row.get("settingsReadable")]
    return {
        "assetPath": asset_path,
        "exists": exists,
        "className": class_name,
        "pathMatched": asset_path.startswith("/Game/AI_Tool_TA/"),
        "materialSlotCount": material.get("slotCount", 0),
        "materialPaths": material.get("materialPaths", []),
        "dependencyQueryCount": dependency_query_count,
        "dependencyErrors": dependency_errors,
        "textureDependencyCount": len(texture_rows),
        "maxTextureDimension": max_dimension,
        "estimatedTextureMemoryMb": round(estimated_memory_mb, 3),
        "textureSettingsReadable": len(readable_rows) == len(texture_rows) if texture_rows else False,
        "compressionSettings": sorted({_stringify(row.get("compressionSettings")) for row in texture_rows if row.get("compressionSettings") is not None}),
        "srgbStates": sorted({_stringify(row.get("srgb")) for row in texture_rows if row.get("srgb") is not None}),
        "raw": {
            "materialSlots": material,
            "materials": material_rows,
            "textures": texture_rows,
        },
    }


def _inspect_material_textures(unreal, material_path: str) -> dict:
    editor_assets = unreal.EditorAssetLibrary
    package_path = _package_path(material_path)
    material = _load_asset(editor_assets, material_path)
    asset_data = _find_asset_data(editor_assets, package_path)
    class_name = _asset_class_name(asset_data) if asset_data else None
    errors = []
    dependency_paths = []
    expression_texture_paths = []
    try:
        dependency_paths = _dependency_paths(unreal, package_path)
    except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
        errors.append("asset_registry_dependencies:%s" % exc)
    try:
        expression_texture_paths = _expression_texture_paths(material)
    except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
        errors.append("material_expression_textures:%s" % exc)

    texture_paths = sorted(set(_texture_dependency_paths(unreal, dependency_paths) + expression_texture_paths))
    textures = [_texture_facts(unreal, texture_path, material_path) for texture_path in texture_paths]
    return {
        "materialPath": material_path,
        "packagePath": package_path,
        "exists": bool(material),
        "className": class_name,
        "dependenciesQueried": bool(material) and not any(err.startswith("asset_registry_dependencies:") for err in errors),
        "dependencyPaths": dependency_paths,
        "expressionTexturePaths": expression_texture_paths,
        "texturePaths": texture_paths,
        "textureCount": len(textures),
        "textures": textures,
        "errors": errors,
    }


def _material_references_texture(unreal, material_path: str, texture_path: str) -> bool:
    row = _inspect_material_textures(unreal, material_path)
    return _package_path(texture_path) in set(row.get("texturePaths", []))


def _texture_dependency_paths(unreal, dependency_paths: list) -> list:
    result = []
    editor_assets = unreal.EditorAssetLibrary
    for path in dependency_paths:
        asset_data = _find_asset_data(editor_assets, path)
        class_name = _asset_class_name(asset_data) if asset_data else None
        if class_name and "Texture" in class_name:
            result.append(path)
    return result


def _texture_facts(unreal, texture_path: str, material_path: str) -> dict:
    editor_assets = unreal.EditorAssetLibrary
    texture = _load_asset(editor_assets, texture_path)
    asset_data = _find_asset_data(editor_assets, texture_path)
    width = _first_positive_int(
        _call_method(texture, "blueprint_get_size_x"),
        _call_method(texture, "get_size_x"),
        _editor_property(texture, "size_x"),
    )
    height = _first_positive_int(
        _call_method(texture, "blueprint_get_size_y"),
        _call_method(texture, "get_size_y"),
        _editor_property(texture, "size_y"),
    )
    width = width or 0
    height = height or 0
    compression = _stringify(_editor_property(texture, "compression_settings"))
    srgb = _editor_property(texture, "srgb")
    lod_group = _stringify(_editor_property(texture, "lod_group"))
    max_texture_size = _int(_editor_property(texture, "max_texture_size"))
    source_files = _source_files(texture)
    estimated_mb = (width * height * 4.0) / (1024.0 * 1024.0) if width and height else 0.0
    return {
        "texturePath": _package_path(texture_path),
        "materialPath": material_path,
        "exists": bool(texture),
        "className": _asset_class_name(asset_data) if asset_data else None,
        "width": width,
        "height": height,
        "maxDimension": max(width, height),
        "estimatedMemoryMb": round(estimated_mb, 3),
        "compressionSettings": compression,
        "srgb": bool(srgb) if srgb is not None else None,
        "lodGroup": lod_group,
        "maxTextureSize": max_texture_size,
        "sourceFiles": source_files,
        "settingsReadable": bool(width or height or compression or srgb is not None or lod_group),
    }


def _material_slot_facts(static_mesh) -> dict:
    if not static_mesh:
        return {"slotCount": 0, "materialPaths": [], "rows": []}
    static_materials = _editor_property(static_mesh, "static_materials") or []
    rows = []
    material_paths = []
    for index, slot in enumerate(static_materials):
        slot_name = _stringify(_editor_property(slot, "material_slot_name"))
        material = _editor_property(slot, "material_interface")
        material_path = _object_path(material)
        if material_path:
            material_paths.append(material_path)
        rows.append({"index": index, "slotName": slot_name, "materialPath": material_path})
    return {"slotCount": len(rows), "materialPaths": material_paths, "rows": rows}


def _dependency_paths(unreal, package_path: str) -> list:
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    options_class = getattr(unreal, "AssetRegistryDependencyOptions", None)
    if options_class:
        options = options_class()
        for prop in (
            "include_hard_package_references",
            "include_soft_package_references",
            "include_hard_management_references",
            "include_soft_management_references",
        ):
            try:
                setattr(options, prop, True)
            except Exception:
                pass
        try:
            dependencies = registry.get_dependencies(package_path, options)
        except TypeError:
            dependencies = registry.get_dependencies(package_path)
    else:
        dependencies = registry.get_dependencies(package_path)
    return sorted({_package_path(str(path)) for path in dependencies})


def _expression_texture_paths(material) -> list:
    if not material:
        return []
    rows = []
    expressions = _editor_property(material, "expressions") or []
    for expression in expressions:
        texture = _editor_property(expression, "texture")
        texture_path = _object_path(texture)
        if texture_path:
            rows.append(_package_path(texture_path))
    return sorted(set(rows))


def _source_files(texture) -> list:
    asset_import_data = _editor_property(texture, "asset_import_data")
    if not asset_import_data or not hasattr(asset_import_data, "extract_filenames"):
        return []
    try:
        return [_public_source_path(path) for path in asset_import_data.extract_filenames()]
    except Exception:
        return []


def _generated_png_path() -> Path:
    root = Path(tempfile.gettempdir()) / "ai_tool_ta_platform_variant"
    root.mkdir(parents=True, exist_ok=True)
    return root / "T_HeroPanel_BaseColor_2048.png"


def _write_png(path: Path, width: int, height: int) -> None:
    if path.exists():
        return
    def chunk(chunk_type: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + chunk_type
            + data
            + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
        )

    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            row.extend(((x * 255) // max(1, width - 1), (y * 255) // max(1, height - 1), 180))
        rows.append(bytes(row))
    raw = b"".join(rows)
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 6))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(payload)


def _public_source_path(path: str) -> str:
    value = str(path)
    temp_root = str(Path(tempfile.gettempdir()))
    comparable_value = value.replace("/", "\\")
    comparable_temp_root = temp_root.replace("/", "\\")
    if comparable_value.lower().startswith(comparable_temp_root.lower()):
        suffix = comparable_value[len(comparable_temp_root) :].lstrip("\\/")
        return r"<runtime-temp>\%s" % suffix.replace("/", "\\")
    return value


def _scan_registry(unreal, paths: list) -> None:
    try:
        registry = unreal.AssetRegistryHelpers.get_asset_registry()
        registry.scan_paths_synchronous(paths, force_rescan=True)
    except Exception:
        pass


def _find_asset_data(editor_assets, path: str):
    try:
        data = editor_assets.find_asset_data(_package_path(path))
        if data and data.is_valid():
            return data
    except Exception:
        pass
    return None


def _load_asset(editor_assets, path: str):
    for candidate in (path, _package_path(path)):
        try:
            asset = editor_assets.load_asset(candidate)
            if asset:
                return asset
        except Exception:
            pass
    return None


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


def _engine_version(unreal) -> str:
    try:
        return unreal.SystemLibrary.get_engine_version()
    except Exception:
        return "unknown"


def _package_path(path: str) -> str:
    value = str(path)
    if "." in value:
        left, right = value.rsplit(".", 1)
        if "/" not in right:
            return left
    return value


def _object_path(obj) -> str | None:
    if not obj:
        return None
    try:
        return str(obj.get_path_name())
    except Exception:
        return str(obj)


def _editor_property(target, prop: str):
    if not target:
        return None
    try:
        return target.get_editor_property(prop)
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


def _int(value) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _stringify(value) -> str | None:
    if value is None:
        return None
    return str(value)


_main()
