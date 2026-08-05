"""Headless Blender adapter contract.

This module intentionally runs without Blender. It proves the normalized data
shape and rule boundary first; a later L3 pass can replace the fixture loader
with a real bpy collector while keeping the same report schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "blender-rule-adapter-contract@0.1.0"
NORMALIZED_SCHEMA = "cross-dcc-rule-input@0.1.0"


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != "synthetic-blender-scene@0.1.0":
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def collect_scene_facts(fixture: Dict[str, Any]) -> Dict[str, Any]:
    scene = fixture.get("scene", {})
    assets = fixture.get("assets", [])
    rows: List[Dict[str, Any]] = []

    for asset in assets:
        mesh_objects = [obj for obj in asset.get("objects", []) if obj.get("type") == "MESH"]
        collision_objects = [
            obj
            for obj in asset.get("objects", [])
            if obj.get("role") == "collision" or str(obj.get("name", "")).startswith("UCX_")
        ]
        material_slots = sum(len(obj.get("materialSlots", [])) for obj in mesh_objects)
        texture_images = sorted(
            {
                texture
                for obj in mesh_objects
                for material in obj.get("materials", [])
                for texture in material.get("textures", [])
            }
        )
        uv_layers = sorted({uv.get("name") for obj in mesh_objects for uv in obj.get("uvLayers", []) if uv.get("name")})
        uv_utilization_values = [
            float(uv.get("utilization", 0.0))
            for obj in mesh_objects
            for uv in obj.get("uvLayers", [])
            if isinstance(uv.get("utilization"), (int, float))
        ]
        uv_overlap_values = [
            float(uv.get("overlapRatio", 0.0))
            for obj in mesh_objects
            for uv in obj.get("uvLayers", [])
            if isinstance(uv.get("overlapRatio"), (int, float))
        ]
        custom_properties = asset.get("customProperties", {})
        protocol = custom_properties.get("aiToolTaProtocol", {})
        lod_collections = [name for name in asset.get("collections", []) if str(name).upper().startswith("LOD")]

        rows.append(
            {
                "assetId": asset.get("id"),
                "assetLabel": asset.get("label"),
                "sourceDcc": "Blender",
                "normalizedSchema": NORMALIZED_SCHEMA,
                "protocolCarrier": "object custom properties + collections + material slots",
                "sourceFields": {
                    "protocol": "asset.customProperties.aiToolTaProtocol",
                    "collision": "objects[role=collision] or UCX_*",
                    "lod": "collections[LOD*]",
                    "materialTexture": "mesh.materialSlots + material.textures",
                    "exportRoot": "asset.collections contains EXPORT_*",
                },
                "normalized": {
                    "asset.protocol.schema": protocol.get("schema"),
                    "asset.delivery.platform": protocol.get("platform", asset.get("platform")),
                    "asset.delivery.collision": protocol.get("collision", "missing"),
                    "asset.delivery.lodCount": len(lod_collections),
                    "asset.render.materialSlots": material_slots,
                    "asset.render.textureImages": len(texture_images),
                    "asset.render.uvLayerCount": len(uv_layers),
                    "asset.render.minUvUtilization": min(uv_utilization_values) if uv_utilization_values else 0.0,
                    "asset.render.maxUvOverlap": max(uv_overlap_values) if uv_overlap_values else 0.0,
                    "asset.export.root": asset.get("exportRoot"),
                },
                "raw": {
                    "collections": asset.get("collections", []),
                    "meshObjects": [obj.get("name") for obj in mesh_objects],
                    "collisionObjects": [obj.get("name") for obj in collision_objects],
                    "uvLayers": uv_layers,
                    "textureImages": texture_images,
                },
            }
        )

    return {
        "schema": NORMALIZED_SCHEMA,
        "scene": {
            "sourceDcc": "Blender",
            "unitScale": scene.get("unitScale"),
            "upAxis": scene.get("upAxis"),
            "assetCount": len(rows),
        },
        "assets": rows,
    }


def evaluate_scene(facts: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("assets", []):
        evaluations.extend(_evaluate_asset(row))

    summary = _summarize(evaluations)
    return {
        "schema": "blender-rule-adapter-evaluation@0.1.0",
        "summary": summary,
        "evaluations": evaluations,
        "fixPreview": _build_fix_preview(evaluations),
    }


def build_report(
    fixture_path: str | Path,
    blender_cli_available: bool = False,
    blender_cli_path: str | None = None,
) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    facts = collect_scene_facts(fixture)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Blender Rule Adapter",
        "evidenceLevel": "L3" if blender_cli_available else "L2",
        "l3Status": "available" if blender_cli_available else "blocked_by_missing_blender_cli",
        "blenderCli": {
            "available": blender_cli_available,
            "path": blender_cli_path,
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
            "protocolCarrier": "object custom properties + collections + material slots",
            "boundary": {
                "mutation": "contract_validation_only",
                "sceneWrites": 0,
                "assetWrites": 0,
                "nextL3Step": "Run the same schema through bpy collection in Blender --background.",
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "Blender adapter normalizes object custom properties, collections, material slots, UV data and collision proxies into the same rule input shape used by the portfolio Cross-DCC Rule Matrix.",
            "Fixture includes one ready asset and one intentionally blocked asset, so failure behavior is part of the evidence.",
            "No DCC or production asset mutation is executed in this L2 contract pass.",
        ],
    }


def _evaluate_asset(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = row.get("assetId")
    normalized = row.get("normalized", {})
    return [
        _eval(
            asset_id,
            "protocol-carrier",
            normalized.get("asset.protocol.schema") == "asset-protocol@dcc-r9",
            "error",
            "Protocol carrier",
            "Blender object custom properties must expose asset-protocol@dcc-r9.",
            str(normalized.get("asset.protocol.schema")),
            "Write aiToolTaProtocol custom property on the asset root.",
        ),
        _eval(
            asset_id,
            "collision-contract",
            normalized.get("asset.delivery.collision") in {"simple", "complex", "proxy"},
            "error",
            "Collision contract",
            "Collision must be declared through protocol or UCX/collision object evidence.",
            str(normalized.get("asset.delivery.collision")),
            "Author UCX collision object or add an owner-approved collision waiver.",
        ),
        _eval(
            asset_id,
            "lod-budget",
            int(normalized.get("asset.delivery.lodCount") or 0) >= 2,
            "warning",
            "LOD budget",
            "At least two LOD collections are required for this public Blender fixture.",
            str(normalized.get("asset.delivery.lodCount")),
            "Create LOD1 collection or document platform exception.",
        ),
        _eval(
            asset_id,
            "material-texture-sync",
            abs(int(normalized.get("asset.render.materialSlots") or 0) - int(normalized.get("asset.render.textureImages") or 0))
            <= 1,
            "warning",
            "Material / texture sync",
            "Material slots and texture images should not drift by more than one.",
            "%s material / %s texture"
            % (normalized.get("asset.render.materialSlots"), normalized.get("asset.render.textureImages")),
            "Review material slots and texture image bindings before export.",
        ),
        _eval(
            asset_id,
            "uv-contract",
            int(normalized.get("asset.render.uvLayerCount") or 0) >= 1
            and float(normalized.get("asset.render.minUvUtilization") or 0.0) >= 0.65
            and float(normalized.get("asset.render.maxUvOverlap") or 0.0) <= 0.02,
            "warning",
            "UV contract",
            "UVs require at least one layer, acceptable utilization and low overlap.",
            "layers=%s utilization=%s overlap=%s"
            % (
                normalized.get("asset.render.uvLayerCount"),
                normalized.get("asset.render.minUvUtilization"),
                normalized.get("asset.render.maxUvOverlap"),
            ),
            "Unwrap asset or attach a manual UV exception receipt.",
        ),
        _eval(
            asset_id,
            "export-root",
            bool(normalized.get("asset.export.root")),
            "error",
            "Export root",
            "Adapter must identify the export root collection/object.",
            str(normalized.get("asset.export.root")),
            "Assign EXPORT_* collection or object custom property.",
        ),
    ]


def _eval(
    asset_id: str,
    rule_id: str,
    passed: bool,
    fail_status: str,
    label: str,
    reason: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (asset_id, rule_id),
        "assetId": asset_id,
        "ruleId": rule_id,
        "label": label,
        "status": "pass" if passed else fail_status,
        "reason": reason,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summarize(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(evaluations)
    asset_ids = sorted({row["assetId"] for row in rows})
    blocked_assets = sorted({row["assetId"] for row in rows if row["status"] == "error"})
    review_assets = sorted({row["assetId"] for row in rows if row["status"] == "warning"} - set(blocked_assets))
    ready_assets = sorted(set(asset_ids) - set(blocked_assets) - set(review_assets))
    gate = "Blocked" if blocked_assets else "Review" if review_assets else "Ready"
    return {
        "gate": gate,
        "assetCount": len(asset_ids),
        "readyAssets": len(ready_assets),
        "reviewAssets": len(review_assets),
        "blockedAssets": len(blocked_assets),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "readyAssetIds": ready_assets,
        "reviewAssetIds": review_assets,
        "blockedAssetIds": blocked_assets,
    }


def _build_fix_preview(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    previews = []
    for row in evaluations:
        if row["status"] == "pass":
            continue
        previews.append(
            {
                "id": "fix:%s" % row["id"],
                "assetId": row["assetId"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "mutationScope": "manual_only" if row["status"] == "warning" else "owner_required",
                "preview": row["fixPreview"],
            }
        )
    return previews

