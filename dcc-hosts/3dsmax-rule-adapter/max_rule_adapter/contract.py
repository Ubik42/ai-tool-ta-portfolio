"""Headless 3ds Max adapter contract.

This module runs in normal Python. It captures the rule semantics and normalized
data shape first; a 3ds Max batch pass can replace the fixture loader with
real pymxs collection while keeping the same Cross-DCC schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "max-rule-adapter-contract@0.1.0"
NORMALIZED_SCHEMA = "cross-dcc-rule-input@0.1.0"


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != "synthetic-3dsmax-scene@0.1.0":
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def collect_scene_facts(fixture: Dict[str, Any]) -> Dict[str, Any]:
    scene = fixture.get("scene", {})
    rows: List[Dict[str, Any]] = []

    for asset in fixture.get("assets", []):
        nodes = asset.get("nodes", [])
        render_nodes = [node for node in nodes if node.get("role") != "collision"]
        collision_nodes = [
            node for node in nodes if node.get("role") == "collision" or str(node.get("name", "")).startswith("UCX_")
        ]
        protocol = asset.get("userProperties", {}).get("aiToolTaProtocol", {})
        material_names = sorted({node.get("material", {}).get("name") for node in render_nodes if node.get("material")})
        texture_images = sorted(
            {
                texture
                for node in render_nodes
                for texture in node.get("material", {}).get("textures", [])
            }
        )
        map_channels = [
            channel for node in render_nodes for channel in node.get("mapChannels", []) if channel.get("channel")
        ]
        uv_utilization_values = [
            float(channel.get("utilization", 0.0))
            for channel in map_channels
            if isinstance(channel.get("utilization"), (int, float))
        ]
        uv_overlap_values = [
            float(channel.get("overlapRatio", 0.0))
            for channel in map_channels
            if isinstance(channel.get("overlapRatio"), (int, float))
        ]
        texel_density_values = [
            float(channel.get("texelDensity", 0.0))
            for channel in map_channels
            if isinstance(channel.get("texelDensity"), (int, float))
        ]
        vertex_color_channels = sorted(
            {
                channel
                for node in render_nodes
                for channel in node.get("vertexColorChannels", [])
            }
        )
        lod_values = sorted({node.get("lod") for node in render_nodes if node.get("lod")})
        transform_rows = [node.get("transform", {}) for node in render_nodes]
        transform_clean = all(_transform_is_clean(transform) for transform in transform_rows)

        rows.append(
            {
                "assetId": asset.get("id"),
                "assetLabel": asset.get("label"),
                "sourceDcc": "3ds Max",
                "normalizedSchema": NORMALIZED_SCHEMA,
                "protocolCarrier": "node user properties + layer/export dummy + material + map channels",
                "sourceFields": {
                    "protocol": "asset.userProperties.aiToolTaProtocol or node user props",
                    "collision": "nodes[role=collision] or UCX_*",
                    "lod": "node.lod or *_LOD# suffix",
                    "materialTexture": "node.material.name + material bitmap slots",
                    "uv": "mesh map channels / Unwrap_UVW",
                    "transform": "object transform, pivot and reset/frozen state",
                    "exportRoot": "asset.exportRoot or layer / Dummy hierarchy",
                },
                "normalized": {
                    "asset.protocol.schema": protocol.get("schema"),
                    "asset.delivery.platform": protocol.get("platform"),
                    "asset.delivery.collision": protocol.get("collision", "missing"),
                    "asset.delivery.lodCount": len(lod_values),
                    "asset.render.materialSlots": len(material_names),
                    "asset.render.textureImages": len(texture_images),
                    "asset.render.uvLayerCount": len({channel.get("channel") for channel in map_channels}),
                    "asset.render.minUvUtilization": min(uv_utilization_values) if uv_utilization_values else 0.0,
                    "asset.render.maxUvOverlap": max(uv_overlap_values) if uv_overlap_values else 0.0,
                    "asset.render.minTexelDensity": min(texel_density_values) if texel_density_values else 0.0,
                    "asset.render.vertexColorChannels": len(vertex_color_channels),
                    "asset.transform.clean": transform_clean,
                    "asset.export.root": asset.get("exportRoot"),
                    "asset.export.layer": asset.get("layer"),
                },
                "raw": {
                    "nodes": [node.get("name") for node in nodes],
                    "renderNodes": [node.get("name") for node in render_nodes],
                    "collisionNodes": [node.get("name") for node in collision_nodes],
                    "lodValues": lod_values,
                    "materialNames": material_names,
                    "textureImages": texture_images,
                    "mapChannels": sorted({channel.get("channel") for channel in map_channels}),
                    "vertexColorChannels": vertex_color_channels,
                    "transformRows": transform_rows,
                },
            }
        )

    return {
        "schema": NORMALIZED_SCHEMA,
        "scene": {
            "sourceDcc": "3ds Max",
            "systemUnit": scene.get("systemUnit"),
            "displayUnit": scene.get("displayUnit"),
            "unitScale": scene.get("unitScale"),
            "upAxis": scene.get("upAxis"),
            "assetCount": len(rows),
        },
        "assets": rows,
    }


def evaluate_scene(facts: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    scene = facts.get("scene", {})
    for row in facts.get("assets", []):
        evaluations.extend(_evaluate_asset(row, scene))

    summary = _summarize(evaluations)
    return {
        "schema": "max-rule-adapter-evaluation@0.1.0",
        "summary": summary,
        "evaluations": evaluations,
        "fixPreview": _build_fix_preview(evaluations),
    }


def build_report(
    fixture_path: str | Path,
    max_batch_available: bool = False,
    max_batch_path: str | None = None,
) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    facts = collect_scene_facts(fixture)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / 3ds Max Rule Adapter",
        "evidenceLevel": "L2+",
        "l3Status": "runtime_discovered" if max_batch_available else "blocked_by_missing_3dsmax_batch",
        "maxRuntime": {
            "available": max_batch_available,
            "path": max_batch_path,
            "runner": "3dsmaxbatch.exe",
        },
        "fixture": {
            "path": str(Path(fixture_path)),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "3dsmax",
            "name": "3ds Max Rule Adapter",
            "methodSource": "max_rule_adapter_reference / max_scene_rule_reference / Cross-DCC Rule Matrix",
            "protocolCarrier": "user properties + layer/export dummy + material + map channels",
            "boundary": {
                "mutation": "contract_validation_only",
                "sceneWrites": 0,
                "assetWrites": 0,
                "nextL3Step": "Run scripts/run_l3_smoke.py --run-runtime to collect through pymxs in 3dsmaxbatch.exe.",
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "3ds Max adapter normalizes user properties, layer/export root, LOD suffixes, material names, map channels, transform state and collision proxies into the same Cross-DCC rule input used by Maya and Blender evidence.",
            "The fixture includes one ready static prop and one intentionally blocked hero prop, so UV, collision, transform and material failure paths are visible.",
            "The L2+ contract pass does not launch 3ds Max or mutate production assets; runtime execution is opt-in through 3dsmaxbatch.exe.",
        ],
    }


def _evaluate_asset(row: Dict[str, Any], scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = row.get("assetId")
    normalized = row.get("normalized", {})
    raw = row.get("raw", {})
    material_names = raw.get("materialNames", [])
    vertex_color_channels = int(normalized.get("asset.render.vertexColorChannels") or 0)
    allows_vertex_color = vertex_color_channels == 0
    return [
        _eval(
            asset_id,
            "protocol-carrier",
            normalized.get("asset.protocol.schema") == "asset-protocol@dcc-r9",
            "error",
            "Protocol carrier",
            "3ds Max node user properties must expose asset-protocol@dcc-r9.",
            str(normalized.get("asset.protocol.schema")),
            "Write aiToolTaProtocol into root or render node user properties.",
        ),
        _eval(
            asset_id,
            "unit-up-axis",
            scene.get("unitScale") == 1.0 and scene.get("upAxis") == "Z",
            "warning",
            "Unit / up axis",
            "Max scene should declare centimeter scale and Z-up before engine export.",
            "unitScale=%s upAxis=%s" % (scene.get("unitScale"), scene.get("upAxis")),
            "Normalize system units or document engine conversion in export receipt.",
        ),
        _eval(
            asset_id,
            "export-root-layer",
            bool(normalized.get("asset.export.root")) and bool(normalized.get("asset.export.layer")),
            "error",
            "Export root / layer",
            "Adapter must identify export root and asset layer or dummy hierarchy.",
            "root=%s layer=%s" % (normalized.get("asset.export.root"), normalized.get("asset.export.layer")),
            "Assign EXPORT_* dummy and ASSET_* layer before publish.",
        ),
        _eval(
            asset_id,
            "lod-sequence",
            int(normalized.get("asset.delivery.lodCount") or 0) >= 2 and "LOD0" in raw.get("lodValues", []),
            "warning",
            "LOD sequence",
            "Max static props require LOD0 plus at least one lower LOD for this fixture.",
            "lods=%s" % ",".join(raw.get("lodValues", [])),
            "Create LOD1 or attach platform exception.",
        ),
        _eval(
            asset_id,
            "material-name-policy",
            bool(material_names) and all(str(name).startswith("MI_") for name in material_names),
            "warning",
            "Material naming",
            "Material names should use MI_* so downstream engine slots and texture sync stay deterministic.",
            ",".join(str(name) for name in material_names) or "-",
            "Rename material or export owner-visible material slot waiver.",
        ),
        _eval(
            asset_id,
            "uv-channel-budget",
            1 <= int(normalized.get("asset.render.uvLayerCount") or 0) <= 2,
            "error",
            "UV channel budget",
            "This public Max fixture allows UV1 and optional lightmap UV only.",
            str(normalized.get("asset.render.uvLayerCount")),
            "Remove legacy map channels or move payload into approved custom properties.",
        ),
        _eval(
            asset_id,
            "uv-quality",
            float(normalized.get("asset.render.minUvUtilization") or 0.0) >= 0.70
            and float(normalized.get("asset.render.maxUvOverlap") or 0.0) <= 0.02
            and float(normalized.get("asset.render.minTexelDensity") or 0.0) >= 256,
            "warning",
            "UV quality / texel density",
            "UV utilization, overlap and texel density must stay inside platform handoff limits.",
            "utilization=%s overlap=%s density=%s"
            % (
                normalized.get("asset.render.minUvUtilization"),
                normalized.get("asset.render.maxUvOverlap"),
                normalized.get("asset.render.minTexelDensity"),
            ),
            "Run Unwrap_UVW review and texel density pass before export.",
        ),
        _eval(
            asset_id,
            "transform-clean",
            bool(normalized.get("asset.transform.clean")),
            "warning",
            "Transform clean",
            "Max export nodes need frozen transform and pivot/origin agreement.",
            str(normalized.get("asset.transform.clean")),
            "Reset XForm, collapse stack if approved, and move pivot under owner review.",
        ),
        _eval(
            asset_id,
            "collision-contract",
            normalized.get("asset.delivery.collision") in {"simple", "complex", "proxy"}
            and bool(raw.get("collisionNodes")),
            "error",
            "Collision contract",
            "Collision must be declared and backed by UCX/proxy object evidence.",
            "collision=%s nodes=%s"
            % (normalized.get("asset.delivery.collision"), ",".join(raw.get("collisionNodes", [])) or "-"),
            "Author UCX collision or attach gameplay owner disposition.",
        ),
        _eval(
            asset_id,
            "vertex-color-boundary",
            allows_vertex_color,
            "warning",
            "Vertex color boundary",
            "Unexpected vertex color channels can carry stale bake or mask payloads.",
            str(vertex_color_channels),
            "Remove vertex color data or document the protocol field that consumes it.",
        ),
    ]


def _transform_is_clean(transform: Dict[str, Any]) -> bool:
    return (
        bool(transform.get("frozen"))
        and bool(transform.get("pivotAtOrigin"))
        and _vector_close(transform.get("position", []), [0.0, 0.0, 0.0])
        and _vector_close(transform.get("rotation", []), [0.0, 0.0, 0.0])
        and _vector_close(transform.get("scale", []), [1.0, 1.0, 1.0])
    )


def _vector_close(value: Any, expected: List[float]) -> bool:
    if not isinstance(value, list) or len(value) != len(expected):
        return False
    return all(abs(float(left) - right) <= 0.0001 for left, right in zip(value, expected))


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
                "mutationScope": "owner_required" if row["status"] == "error" else "manual_only",
                "preview": row["fixPreview"],
            }
        )
    return previews

