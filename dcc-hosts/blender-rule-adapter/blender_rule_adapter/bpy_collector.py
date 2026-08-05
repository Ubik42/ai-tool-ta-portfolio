"""Blender bpy collector for the Cross-DCC rule adapter.

The functions in this module are imported by Blender's Python runtime. They
create a public synthetic scene, collect real bpy objects/materials/UV layers,
and emit the same normalized schema as the L2 contract.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .contract import NORMALIZED_SCHEMA, evaluate_scene, load_fixture


L3_REPORT_VERSION = "blender-rule-adapter-bpy-l3@0.1.0"


def build_bpy_report(fixture_path: str | Path) -> Dict[str, Any]:
    import bpy  # type: ignore

    fixture = load_fixture(fixture_path)
    reset_scene(bpy)
    create_scene_from_fixture(bpy, fixture)
    facts = collect_bpy_scene_facts(bpy)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": L3_REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Blender Rule Adapter",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3",
        "l3Status": "bpy_scene_collected",
        "blenderRuntime": {
            "version": ".".join(str(part) for part in bpy.app.version),
            "versionString": bpy.app.version_string,
            "background": bool(bpy.app.background),
        },
        "fixture": {
            "path": str(Path(fixture_path)),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "blender",
            "name": "Blender Rule Adapter",
            "methodSource": "blender_rule_adapter_reference / Cross-DCC Rule Matrix",
            "protocolCarrier": "bpy object custom properties + collections + material slots + UV layers",
            "boundary": {
                "mutation": "synthetic_blender_fixture_only",
                "sceneWrites": "creates temporary public fixture objects in background scene",
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "The Blender adapter can collect a real bpy scene into the same Cross-DCC rule input used by Maya evidence.",
            "Protocol, LOD, collision, material, texture and UV facts are read through Blender runtime APIs.",
            "The L3 smoke only creates synthetic public fixture objects and performs no production asset writes.",
        ],
    }


def reset_scene(bpy: Any) -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for datablock_group in (
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.images,
    ):
        for datablock in list(datablock_group):
            if datablock.users == 0:
                datablock_group.remove(datablock)
    for collection in list(bpy.data.collections):
        if collection.users == 0 and collection.name.startswith(("ASSET_", "EXPORT_", "LOD", "Collision")):
            bpy.data.collections.remove(collection)


def create_scene_from_fixture(bpy: Any, fixture: Dict[str, Any]) -> None:
    scene = bpy.context.scene
    scene.unit_settings.scale_length = float(fixture.get("scene", {}).get("unitScale", 1.0))
    scene["aiToolTaSourceDcc"] = "Blender"
    scene["aiToolTaFixtureSchema"] = fixture.get("schema")

    for asset in fixture.get("assets", []):
        _create_asset_root(bpy, asset)
        for obj_payload in asset.get("objects", []):
            _create_mesh_object(bpy, asset, obj_payload)


def collect_bpy_scene_facts(bpy: Any) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    roots = [
        obj
        for obj in bpy.data.objects
        if obj.type == "EMPTY" and obj.get("aiToolTaAssetId") and obj.get("aiToolTaProtocol")
    ]

    for root in sorted(roots, key=lambda obj: str(obj.get("aiToolTaAssetId"))):
        asset_id = str(root.get("aiToolTaAssetId"))
        objects = [obj for obj in bpy.data.objects if obj.get("aiToolTaAssetId") == asset_id and obj != root]
        mesh_objects = [obj for obj in objects if obj.type == "MESH" and obj.get("aiToolTaRole") != "collision"]
        collision_objects = [
            obj
            for obj in objects
            if obj.get("aiToolTaRole") == "collision" or str(obj.name).startswith("UCX_")
        ]
        material_slots = sum(len(obj.material_slots) for obj in mesh_objects)
        texture_images = sorted(
            {
                texture
                for obj in mesh_objects
                for material in _materials_for_object(obj)
                for texture in _material_textures(material)
            }
        )
        uv_layers = sorted({uv.name for obj in mesh_objects for uv in obj.data.uv_layers})
        uv_metrics = [_uv_metric(metric) for obj in mesh_objects for metric in _object_uv_metrics(obj).values()]
        uv_utilization_values = [metric["utilization"] for metric in uv_metrics]
        uv_overlap_values = [metric["overlapRatio"] for metric in uv_metrics]
        protocol = _read_json_prop(root, "aiToolTaProtocol", {})
        collections = _read_json_prop(root, "aiToolTaCollections", [])
        lod_collections = [name for name in collections if str(name).upper().startswith("LOD")]

        rows.append(
            {
                "assetId": asset_id,
                "assetLabel": root.get("aiToolTaAssetLabel"),
                "sourceDcc": "Blender",
                "normalizedSchema": NORMALIZED_SCHEMA,
                "protocolCarrier": "bpy object custom properties + collections + material slots",
                "sourceFields": {
                    "protocol": "root['aiToolTaProtocol']",
                    "collision": "objects[aiToolTaRole=collision] or UCX_*",
                    "lod": "root['aiToolTaCollections'][LOD*]",
                    "materialTexture": "obj.material_slots + material['aiToolTaTextures']",
                    "exportRoot": "root['aiToolTaExportRoot']",
                },
                "normalized": {
                    "asset.protocol.schema": protocol.get("schema"),
                    "asset.delivery.platform": protocol.get("platform"),
                    "asset.delivery.collision": protocol.get("collision", "missing"),
                    "asset.delivery.lodCount": len(lod_collections),
                    "asset.render.materialSlots": material_slots,
                    "asset.render.textureImages": len(texture_images),
                    "asset.render.uvLayerCount": len(uv_layers),
                    "asset.render.minUvUtilization": min(uv_utilization_values) if uv_utilization_values else 0.0,
                    "asset.render.maxUvOverlap": max(uv_overlap_values) if uv_overlap_values else 0.0,
                    "asset.export.root": root.get("aiToolTaExportRoot"),
                },
                "raw": {
                    "collections": collections,
                    "meshObjects": [obj.name for obj in mesh_objects],
                    "collisionObjects": [obj.name for obj in collision_objects],
                    "uvLayers": uv_layers,
                    "textureImages": texture_images,
                },
            }
        )

    return {
        "schema": NORMALIZED_SCHEMA,
        "scene": {
            "sourceDcc": "Blender",
            "unitScale": bpy.context.scene.unit_settings.scale_length,
            "upAxis": "Z",
            "assetCount": len(rows),
        },
        "assets": rows,
    }


def _create_asset_root(bpy: Any, asset: Dict[str, Any]) -> None:
    root = bpy.data.objects.new("%s_ROOT" % asset.get("id"), None)
    root.empty_display_type = "CUBE"
    root.empty_display_size = 0.5
    root["aiToolTaAssetId"] = asset.get("id")
    root["aiToolTaAssetLabel"] = asset.get("label")
    root["aiToolTaExportRoot"] = asset.get("exportRoot")
    root["aiToolTaCollections"] = json.dumps(asset.get("collections", []), ensure_ascii=False, sort_keys=True)
    root["aiToolTaProtocol"] = json.dumps(
        asset.get("customProperties", {}).get("aiToolTaProtocol", {}),
        ensure_ascii=False,
        sort_keys=True,
    )
    bpy.context.scene.collection.objects.link(root)

    for collection_name in asset.get("collections", []):
        _ensure_collection(bpy, str(collection_name))


def _create_mesh_object(bpy: Any, asset: Dict[str, Any], payload: Dict[str, Any]) -> None:
    mesh = bpy.data.meshes.new("%sMesh" % payload.get("name"))
    mesh.from_pydata(
        [(-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0)],
        [],
        [(0, 1, 2, 3)],
    )
    mesh.update()
    obj = bpy.data.objects.new(str(payload.get("name")), mesh)
    obj["aiToolTaAssetId"] = asset.get("id")
    obj["aiToolTaRole"] = payload.get("role")
    obj["aiToolTaUvMetrics"] = json.dumps(
        {
            uv.get("name", "UVMap"): {
                "utilization": uv.get("utilization", 0.0),
                "overlapRatio": uv.get("overlapRatio", 0.0),
            }
            for uv in payload.get("uvLayers", [])
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    for material_payload in payload.get("materials", []):
        material = bpy.data.materials.new(str(material_payload.get("name")))
        material["aiToolTaTextures"] = json.dumps(
            material_payload.get("textures", []),
            ensure_ascii=False,
            sort_keys=True,
        )
        obj.data.materials.append(material)

    for slot_name in payload.get("materialSlots", []):
        if not any(slot.material and slot.material.name == slot_name for slot in obj.material_slots):
            material = bpy.data.materials.new(str(slot_name))
            material["aiToolTaTextures"] = json.dumps([], ensure_ascii=False)
            obj.data.materials.append(material)

    for uv_payload in payload.get("uvLayers", []):
        uv_name = str(uv_payload.get("name", "UVMap"))
        if not obj.data.uv_layers.get(uv_name):
            obj.data.uv_layers.new(name=uv_name)

    target_collection = _ensure_collection(bpy, _select_collection_name(asset, payload))
    target_collection.objects.link(obj)
    if bpy.context.scene.collection.objects.get(obj.name):
        bpy.context.scene.collection.objects.unlink(obj)


def _select_collection_name(asset: Dict[str, Any], payload: Dict[str, Any]) -> str:
    collections = [str(name) for name in asset.get("collections", [])]
    if payload.get("role") == "collision" and "Collision" in collections:
        return "Collision"
    for collection_name in collections:
        if collection_name.upper().startswith("LOD") and collection_name in str(payload.get("name", "")):
            return collection_name
    return str(asset.get("exportRoot") or collections[0])


def _ensure_collection(bpy: Any, name: str) -> Any:
    existing = bpy.data.collections.get(name)
    if existing:
        return existing
    collection = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(collection)
    return collection


def _materials_for_object(obj: Any) -> List[Any]:
    return [slot.material for slot in obj.material_slots if slot.material]


def _material_textures(material: Any) -> List[str]:
    textures = _read_json_prop(material, "aiToolTaTextures", [])
    if textures:
        return [str(texture) for texture in textures]
    return []


def _object_uv_metrics(obj: Any) -> Dict[str, Dict[str, float]]:
    return _read_json_prop(obj, "aiToolTaUvMetrics", {})


def _uv_metric(payload: Dict[str, Any]) -> Dict[str, float]:
    return {
        "utilization": float(payload.get("utilization", 0.0)),
        "overlapRatio": float(payload.get("overlapRatio", 0.0)),
    }


def _read_json_prop(owner: Any, key: str, default: Any) -> Any:
    value = owner.get(key)
    if not value:
        return default
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default
    return value

