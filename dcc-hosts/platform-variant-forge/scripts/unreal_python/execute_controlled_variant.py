from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_EXECUTOR_OUTPUT"])
    generation_path = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_GENERATION_PLAN"])
    texture_payload_path = Path(os.environ["AI_TOOL_TA_PLATFORM_VARIANT_TEXTURE_PAYLOAD"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from platform_variant_forge.controlled_executor import build_controlled_executor_report

    payload = json.loads(texture_payload_path.read_text(encoding="utf-8"))
    selected = _select_texture_operation(payload)
    texture_path = selected["targetTexturePath"]
    target_max_size = int(selected["targetMaxTextureSize"])
    editor_assets = unreal.EditorAssetLibrary
    errors = []
    asset_writes = 0
    operation_applied = False
    rollback_applied = False

    _scan_registry(unreal, ["/Game/AI_Tool_TA"])
    texture = editor_assets.load_asset(texture_path)
    preflight = _texture_state(unreal, texture_path)
    previous_max_size = preflight.get("maxTextureSize")
    selected["previousMaxTextureSize"] = previous_max_size

    if texture and preflight.get("exists"):
        try:
            texture.set_editor_property("max_texture_size", target_max_size)
            editor_assets.save_loaded_asset(texture)
            asset_writes += 1
            operation_applied = True
        except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
            errors.append("execute_set_max_texture_size:%s" % exc)
    else:
        errors.append("missing_texture:%s" % texture_path)

    post_execution = _texture_state(unreal, texture_path)

    if texture and operation_applied:
        try:
            texture.set_editor_property("max_texture_size", int(previous_max_size or 0))
            editor_assets.save_loaded_asset(texture)
            asset_writes += 1
            rollback_applied = True
        except Exception as exc:  # pragma: no cover - only meaningful inside Unreal
            errors.append("rollback_max_texture_size:%s" % exc)

    rollback = _texture_state(unreal, texture_path)
    snapshot = {
        "mode": "execute_then_rollback",
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _engine_version(unreal),
            "pythonVersion": sys.version,
            "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "engineWrites": 0,
            "assetWrites": asset_writes,
            "productionWrites": 0,
            "writeScope": "/Game/AI_Tool_TA public test fixture only",
        },
        "selectedOperation": selected,
        "operationApplied": operation_applied,
        "rollbackApplied": rollback_applied,
        "writeSet": [texture_path],
        "rollbackActions": [
            {
                "id": "rollback-texture-max-size",
                "kind": "restore_texture_max_size",
                "targetTexturePath": texture_path,
                "restoreValue": previous_max_size,
            }
        ],
        "preflight": preflight,
        "postExecution": post_execution,
        "rollback": rollback,
        "errors": errors,
    }
    report = build_controlled_executor_report(generation_path, texture_payload_path, snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_PLATFORM_VARIANT_EXECUTOR_OUTPUT=%s" % output_path)


def _select_texture_operation(payload: dict) -> dict:
    target_mesh_path = "/Game/AI_Tool_TA/Props/Mobile/SM_HeroPanel_A_M"
    fact = payload.get("textureFacts", {}).get(target_mesh_path, {})
    textures = fact.get("raw", {}).get("textures", [])
    texture_path = textures[0].get("texturePath") if textures else "/Game/AI_Tool_TA/Textures/T_HeroPanel_BaseColor"
    return {
        "id": "variant-hero-panel-001:mobile:apply-texture-max-size-clamp",
        "sourceGenerationOperationId": "variant-hero-panel-001:mobile:downscale-textures",
        "sourceTexturePayloadRowId": "variant-hero-panel-001:mobile:runtime-texture-max-size",
        "assetId": "variant-hero-panel-001",
        "platform": "mobile",
        "targetEnginePath": target_mesh_path,
        "targetTexturePath": _package_path(texture_path),
        "targetMaxTextureSize": int(fact.get("maxTextureDimension") or 2048),
        "action": "apply-texture-max-size-clamp",
        "reason": "R32 payload facts make the Mobile texture budget executable inside the public fixture.",
    }


def _texture_state(unreal, texture_path: str) -> dict:
    editor_assets = unreal.EditorAssetLibrary
    package_path = _package_path(texture_path)
    exists = bool(editor_assets.does_asset_exist(package_path))
    texture = editor_assets.load_asset(package_path) if exists else None
    asset_data = editor_assets.find_asset_data(package_path) if exists else None
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
    row = {
        "texturePath": package_path,
        "exists": exists,
        "className": _asset_class_name(asset_data) if asset_data else None,
        "width": width or 0,
        "height": height or 0,
        "maxDimension": max(width or 0, height or 0),
        "maxTextureSize": _int(_editor_property(texture, "max_texture_size")),
        "srgb": bool(_editor_property(texture, "srgb")) if _editor_property(texture, "srgb") is not None else None,
        "compressionSettings": _stringify(_editor_property(texture, "compression_settings")),
        "lodGroup": _stringify(_editor_property(texture, "lod_group")),
    }
    row["fingerprint"] = _fingerprint(row)
    return row


def _scan_registry(unreal, paths: list) -> None:
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
    value = str(path)
    if "." in value:
        left, right = value.rsplit(".", 1)
        if "/" not in right:
            return left
    return value


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


def _fingerprint(payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


_main()
