"""Headless Houdini adapter contract.

The contract runs in normal Python. It captures procedural-asset publishing
semantics first; a hython pass can replace fixture loading with real hou node
collection while keeping the same Cross-DCC schema.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "houdini-rule-adapter-contract@0.1.0"
NORMALIZED_SCHEMA = "cross-dcc-rule-input@0.1.0"


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != "synthetic-houdini-scene@0.1.0":
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def collect_scene_facts(fixture: Dict[str, Any], runtime: Dict[str, Any] | None = None) -> Dict[str, Any]:
    scene = fixture.get("scene", {})
    runtime = runtime or {}
    rows = []
    for asset in fixture.get("assets", []):
        outputs = asset.get("outputs", [])
        render_outputs = [row for row in outputs if row.get("role") == "render"]
        collision_outputs = [row for row in outputs if row.get("role") == "collision"]
        attributes = sorted({attr for output in outputs for attr in output.get("attributes", [])})
        groups = sorted({group for output in outputs for group in output.get("groups", [])})
        material_slots = sorted({slot for output in render_outputs for slot in output.get("materialSlots", [])})
        lods = sorted({output.get("lod") for output in render_outputs if output.get("lod")})
        protocol = asset.get("detailAttributes", {}).get("aiToolTaProtocol", {})
        bake = asset.get("bakeReceipt", {})
        pdg = asset.get("pdg", {})
        prototypes = asset.get("packedInstancePrototypes", [])
        stable_prototypes = [
            proto
            for proto in prototypes
            if proto.get("approved") and proto.get("stableId") and not str(proto.get("stableId")).lower().startswith("tmp")
        ]
        primitive_count = sum(int(output.get("primitives") or 0) for output in render_outputs)
        packed_count = sum(int(output.get("packedPrimitives") or 0) for output in render_outputs)
        hda = asset.get("hda", {})
        rows.append(
            {
                "assetId": asset.get("id"),
                "assetLabel": asset.get("label"),
                "sourceDcc": "Houdini",
                "normalizedSchema": NORMALIZED_SCHEMA,
                "protocolCarrier": "HDA node metadata + detail attributes + SOP output nodes + PDG bake receipt",
                "sourceFields": {
                    "protocol": "detail attribute aiToolTaProtocol",
                    "hda": "hou.Node type / locked state / parms fingerprint",
                    "outputs": "OUT_* SOP nodes and role groups",
                    "attributes": "geometry point/prim/detail attributes",
                    "pdg": "TOP graph wedge result summary",
                    "bake": "frozen bgeo/cache receipt",
                },
                "normalized": {
                    "asset.protocol.schema": protocol.get("schema"),
                    "asset.delivery.platform": protocol.get("platform"),
                    "asset.delivery.collision": protocol.get("collision", "missing"),
                    "asset.delivery.lodCount": len(lods),
                    "asset.render.materialSlots": len(material_slots),
                    "asset.render.hasUv": "uv" in attributes,
                    "asset.render.hasMaterialPath": "shop_materialpath" in attributes,
                    "asset.render.primitives": primitive_count,
                    "asset.render.packedPrimitives": packed_count,
                    "asset.procedural.hdaLocked": bool(hda.get("definitionLocked")),
                    "asset.procedural.nodePath": hda.get("nodePath"),
                    "asset.procedural.typeName": hda.get("typeName"),
                    "asset.procedural.parmFingerprint": hda.get("parmFingerprint"),
                    "asset.procedural.stablePrototypeCount": len(stable_prototypes),
                    "asset.procedural.prototypeCount": len(prototypes),
                    "asset.procedural.pdgWedgeCount": int(pdg.get("wedgeCount") or 0),
                    "asset.procedural.pdgApprovedWedges": int(pdg.get("approvedWedges") or 0),
                    "asset.procedural.pdgFailedWedges": int(pdg.get("failedWedges") or 0),
                    "asset.procedural.bakeFrozen": bool(bake.get("frozen")),
                    "asset.procedural.bakeExists": bool(bake.get("exists")),
                    "asset.procedural.bakeSha256": bake.get("sha256"),
                },
                "raw": {
                    "outputs": [output.get("name") for output in outputs],
                    "renderOutputs": [output.get("name") for output in render_outputs],
                    "collisionOutputs": [output.get("name") for output in collision_outputs],
                    "lods": lods,
                    "groups": groups,
                    "attributes": attributes,
                    "materialSlots": material_slots,
                    "packedInstancePrototypes": prototypes,
                    "pdg": pdg,
                    "bakeReceipt": bake,
                },
            }
        )
    return {
        "schema": NORMALIZED_SCHEMA,
        "scene": {
            "sourceDcc": "Houdini",
            "unitScale": scene.get("unitScale"),
            "upAxis": scene.get("upAxis"),
            "assetCount": len(rows),
            "runtimeCollected": bool(runtime.get("runtimeCollected")),
            "runtimeNodeCount": runtime.get("runtimeNodeCount", 0),
            "houdiniVersion": runtime.get("houdiniVersion"),
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
        "schema": "houdini-rule-adapter-evaluation@0.1.0",
        "summary": summary,
        "evaluations": evaluations,
        "fixPreview": _build_fix_preview(evaluations),
    }


def build_report(
    fixture_path: str | Path,
    hython_available: bool = False,
    hython_path: str | None = None,
    runtime: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    facts = collect_scene_facts(fixture, runtime=runtime)
    evaluation = evaluate_scene(facts)
    runtime_collected = bool(facts.get("scene", {}).get("runtimeCollected"))
    return {
        "reportVersion": "houdini-rule-adapter-hython-l3@0.1.0" if runtime_collected else REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Houdini Rule Adapter",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if runtime_collected else "L2+",
        "l3Status": "hython_node_facts_collected" if runtime_collected else (
            "runtime_discovered" if hython_available else "blocked_by_missing_hython"
        ),
        "houdiniRuntime": {
            "runner": "hython.exe",
            "available": hython_available,
            "path": hython_path,
            "version": facts.get("scene", {}).get("houdiniVersion"),
        },
        "fixture": {
            "path": str(Path(fixture_path)),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "houdini",
            "name": "Houdini Rule Adapter",
            "methodSource": "procedural HDA publish checks / Cross-DCC Rule Matrix",
            "protocolCarrier": "HDA metadata + detail attrs + output SOP groups + PDG bake receipts",
            "boundary": {
                "mutation": "contract_validation_only" if not runtime_collected else "synthetic_houdini_nodes_only",
                "sceneWrites": 0 if not runtime_collected else "creates temporary public fixture nodes in hython",
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "Houdini adapter normalizes HDA state, detail attributes, OUT_* role nodes, packed instance prototypes, PDG wedge results and bake receipts into the same Cross-DCC rule input shape.",
            "The fixture separates a publishable procedural environment asset from a TMP fracture setup blocked by unstable parms, missing collision, missing UV and unfrozen bake receipt.",
            "No production HIP, cache, asset or engine data is mutated by the contract pass.",
        ],
    }


def _evaluate_asset(row: Dict[str, Any], scene: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = row.get("assetId")
    normalized = row.get("normalized", {})
    raw = row.get("raw", {})
    render_prims = int(normalized.get("asset.render.primitives") or 0)
    budget = _triangle_budget(row)
    return [
        _eval(
            asset_id,
            "protocol-carrier",
            normalized.get("asset.protocol.schema") == "asset-protocol@dcc-r9",
            "error",
            "Protocol carrier",
            "Houdini detail attributes must expose asset-protocol@dcc-r9.",
            str(normalized.get("asset.protocol.schema")),
            "Write aiToolTaProtocol as detail attribute on the publish branch.",
        ),
        _eval(
            asset_id,
            "unit-up-axis",
            scene.get("unitScale") == 1.0 and scene.get("upAxis") == "Y",
            "warning",
            "Unit / up axis",
            "Houdini procedural assets should declare meter-scale intent and Y-up conversion boundary for this fixture.",
            "unitScale=%s upAxis=%s" % (scene.get("unitScale"), scene.get("upAxis")),
            "Document export conversion or normalize scene-level metadata.",
        ),
        _eval(
            asset_id,
            "hda-definition-locked",
            bool(normalized.get("asset.procedural.hdaLocked"))
            and "tmp" not in str(normalized.get("asset.procedural.nodePath", "")).lower(),
            "error",
            "HDA locked definition",
            "Publishable procedural assets need a locked HDA definition and non-TMP node path.",
            "locked=%s node=%s type=%s"
            % (
                normalized.get("asset.procedural.hdaLocked"),
                normalized.get("asset.procedural.nodePath"),
                normalized.get("asset.procedural.typeName"),
            ),
            "Lock the HDA definition and move TMP nodes into owner review.",
        ),
        _eval(
            asset_id,
            "output-role-contract",
            bool(raw.get("renderOutputs")) and bool(raw.get("collisionOutputs")),
            "error",
            "Output role contract",
            "Houdini publish branch must expose render and collision outputs.",
            "render=%s collision=%s" % (raw.get("renderOutputs"), raw.get("collisionOutputs")),
            "Create OUT_RENDER_* and OUT_COLLISION SOP nodes or attach a collision waiver.",
        ),
        _eval(
            asset_id,
            "geometry-attribute-contract",
            bool(normalized.get("asset.render.hasUv")) and bool(normalized.get("asset.render.hasMaterialPath")),
            "error",
            "Geometry attributes",
            "Geometry must carry uv and shop_materialpath attributes before handoff.",
            "attrs=%s" % ",".join(raw.get("attributes", [])),
            "Author uv attribute and material path attributes on render outputs.",
        ),
        _eval(
            asset_id,
            "lod-and-variant-contract",
            int(normalized.get("asset.delivery.lodCount") or 0) >= 2
            and int(normalized.get("asset.procedural.pdgFailedWedges") or 0) == 0,
            "warning",
            "LOD / PDG variants",
            "Procedural assets need at least two LOD render outputs and no failed PDG wedges.",
            "lods=%s wedges=%s/%s failed=%s"
            % (
                raw.get("lods"),
                normalized.get("asset.procedural.pdgApprovedWedges"),
                normalized.get("asset.procedural.pdgWedgeCount"),
                normalized.get("asset.procedural.pdgFailedWedges"),
            ),
            "Cook approved wedges and publish LOD1 before export.",
        ),
        _eval(
            asset_id,
            "packed-instance-stability",
            int(normalized.get("asset.procedural.prototypeCount") or 0) == int(normalized.get("asset.procedural.stablePrototypeCount") or 0)
            and int(normalized.get("asset.procedural.prototypeCount") or 0) > 0,
            "error",
            "Packed instance stability",
            "Packed prototypes require stable ids and owner-approved prototype rows.",
            "%s/%s stable"
            % (
                normalized.get("asset.procedural.stablePrototypeCount"),
                normalized.get("asset.procedural.prototypeCount"),
            ),
            "Assign stable prototype ids and remove TMP prototype rows.",
        ),
        _eval(
            asset_id,
            "triangle-budget",
            render_prims <= budget,
            "warning",
            "Triangle budget",
            "Render primitive count must fit the platform budget.",
            "renderPrimitives=%s budget=%s" % (render_prims, budget),
            "Lower scatter density, publish LOD, or request platform waiver.",
        ),
        _eval(
            asset_id,
            "bake-receipt-frozen",
            bool(normalized.get("asset.procedural.bakeFrozen"))
            and bool(normalized.get("asset.procedural.bakeExists"))
            and bool(normalized.get("asset.procedural.bakeSha256")),
            "error",
            "Bake receipt",
            "Procedural outputs must have a frozen cache/bake receipt before engine handoff.",
            "frozen=%s exists=%s sha=%s"
            % (
                normalized.get("asset.procedural.bakeFrozen"),
                normalized.get("asset.procedural.bakeExists"),
                normalized.get("asset.procedural.bakeSha256"),
            ),
            "Freeze cache and write bgeo/USD receipt with sha256.",
        ),
    ]


def _triangle_budget(row: Dict[str, Any]) -> int:
    platform = str(row.get("normalized", {}).get("asset.delivery.platform", "")).lower()
    return 5000 if platform == "mobile" else 20000


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
        "reason": "ok" if passed else reason,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summarize(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    items = list(rows)
    error_assets = {row["assetId"] for row in items if row["status"] == "error"}
    warning_assets = {row["assetId"] for row in items if row["status"] == "warning"}
    assets = sorted({row["assetId"] for row in items})
    ready = [asset for asset in assets if asset not in error_assets and asset not in warning_assets]
    review = [asset for asset in assets if asset not in error_assets and asset in warning_assets]
    blocked = sorted(error_assets)
    return {
        "assets": len(assets),
        "ready": len(ready),
        "review": len(review),
        "blocked": len(blocked),
        "pass": sum(1 for row in items if row["status"] == "pass"),
        "warning": sum(1 for row in items if row["status"] == "warning"),
        "error": sum(1 for row in items if row["status"] == "error"),
        "gate": "Blocked" if blocked else ("Review" if review else "Ready"),
    }


def _build_fix_preview(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "assetId": row["assetId"],
            "ruleId": row["ruleId"],
            "status": row["status"],
            "preview": row["fixPreview"],
            "safeAuto": row["status"] == "warning",
            "ownerRequired": row["status"] == "error",
        }
        for row in rows
        if row["status"] != "pass"
    ]
