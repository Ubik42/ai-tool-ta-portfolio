"""Groom export contract.

The module models a Lightbox-style XGen/groom handoff check before hair data is
converted into Unreal Groom / Binding assets.
"""

from __future__ import annotations

import json
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "groom-export-inspector-contract@0.1.0"
NORMALIZED_SCHEMA = "groom-export-input@0.1.0"
FIXTURE_SCHEMA = "synthetic-groom-export-scene@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != FIXTURE_SCHEMA:
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def collect_scene_facts(fixture: Dict[str, Any]) -> Dict[str, Any]:
    return build_facts_from_assets(
        scene=fixture.get("scene", {}),
        assets=fixture.get("assets", []),
        source_dcc="Fixture",
        runtime_collected=False,
    )


def build_facts_from_assets(
    scene: Dict[str, Any],
    assets: List[Dict[str, Any]],
    source_dcc: str,
    runtime_collected: bool,
) -> Dict[str, Any]:
    rows = [_build_asset_facts(asset, scene, source_dcc) for asset in assets]
    return {
        "schema": NORMALIZED_SCHEMA,
        "scene": {
            "sourceDcc": source_dcc,
            "unit": scene.get("unit"),
            "upAxis": scene.get("upAxis"),
            "timeUnit": scene.get("timeUnit"),
            "fps": scene.get("fps"),
            "playbackStart": scene.get("playbackStart"),
            "playbackEnd": scene.get("playbackEnd"),
            "assetCount": len(rows),
            "runtimeCollected": runtime_collected,
        },
        "assets": rows,
    }


def evaluate_scene(facts: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("assets", []):
        evaluations.extend(_evaluate_asset(row))
    return {
        "schema": "groom-export-evaluation@0.1.0",
        "summary": _summarize(evaluations),
        "evaluations": evaluations,
        "ownerActions": _build_owner_actions(evaluations),
    }


def build_report(fixture_path: str | Path) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    facts = collect_scene_facts(fixture)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2",
        "l3Status": "contract_fixture_collected",
        "fixture": {
            "path": public_path(fixture_path),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "groom-export-inspector",
            "name": "Groom Export Inspector",
            "methodSource": "Lightbox XGen to Unreal groom handoff",
            "protocolCarrier": "Maya groom curves + root UV + strand ID + guide curve + Alembic export payload",
            "boundary": {
                "mutation": "contract_validation_only",
                "sceneWrites": 0,
                "assetWrites": 0,
                "engineWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": _reviewer_claims(),
    }


def _build_asset_facts(asset: Dict[str, Any], scene: Dict[str, Any], source_dcc: str) -> Dict[str, Any]:
    description = asset.get("description", {})
    scalp = asset.get("scalp", {})
    groom = asset.get("groom", {})
    export = asset.get("export", {})
    unreal = asset.get("unreal", {})
    strands = [_strand_fact(strand) for strand in groom.get("strands", [])]
    strand_ids = [row["id"] for row in strands if row["id"]]
    id_counts = Counter(strand_ids)
    duplicate_ids = sorted(strand_id for strand_id, count in id_counts.items() if count > 1)
    missing_id_rows = [index for index, row in enumerate(strands) if not row["id"]]
    missing_root_uv = [row["id"] or "row_%03d" % index for index, row in enumerate(strands) if row["rootUv"] is None]
    invalid_root_uv = [
        {"strandId": row["id"] or "row_%03d" % index, "rootUv": row["rootUv"]}
        for index, row in enumerate(strands)
        if row["rootUv"] is not None and not _uv_in_range(row["rootUv"])
    ]
    guide_ids = sorted(row["id"] for row in strands if row["id"] and row["guide"])
    required_guide_ids = sorted(str(value) for value in groom.get("requiredGuideIds", []))
    actual_uv_sets = [str(value) for value in scalp.get("actualUVSets", [])]
    expected_uv_set = str(scalp.get("expectedUVSet", "root_uv"))
    cache_path = str(export.get("cachePath", ""))
    frame_range = list(export.get("frameRange", [scene.get("playbackStart"), scene.get("playbackEnd")]))
    return {
        "assetId": asset.get("id"),
        "assetLabel": asset.get("label"),
        "sourceDcc": source_dcc,
        "normalizedSchema": NORMALIZED_SCHEMA,
        "protocolCarrier": "groom curves + root UV + strand ID + guide curve + Alembic payload",
        "sourceFields": {
            "description": "root.aiToolTaGroomDescription",
            "scalp": "root.aiToolTaGroomScalp + Maya mesh UV set evidence",
            "strands": "curve aiToolTaGroomStrandPayload custom attrs",
            "export": "root.aiToolTaGroomExport",
            "unreal": "root.aiToolTaGroomUnreal",
        },
        "normalized": {
            "groom.protocol.schema": asset.get("protocolSchema"),
            "groom.ownerState": asset.get("ownerState"),
            "description.name": description.get("name"),
            "description.type": description.get("type"),
            "description.collection": description.get("collection"),
            "description.tmpToken": "TMP" in str(description.get("name", "")).upper(),
            "scalp.mesh": scalp.get("mesh"),
            "scalp.expectedUVSet": expected_uv_set,
            "scalp.actualUVSets": actual_uv_sets,
            "scalp.rootUVSetPresent": expected_uv_set in actual_uv_sets,
            "strands.count": len(strands),
            "strands.budget": int(groom.get("strandBudget", 0) or 0),
            "strands.missingIds": missing_id_rows,
            "strands.duplicateIds": duplicate_ids,
            "rootUV.missing": missing_root_uv,
            "rootUV.invalid": invalid_root_uv,
            "guides.count": len(guide_ids),
            "guides.minimum": int(groom.get("minGuideCount", 0) or 0),
            "guides.required": required_guide_ids,
            "guides.actual": guide_ids,
            "guides.missingRequired": sorted(set(required_guide_ids) - set(guide_ids)),
            "export.cachePath": cache_path,
            "export.expectedExtension": export.get("expectedExtension", ".abc"),
            "export.extensionMatched": cache_path.lower().endswith(str(export.get("expectedExtension", ".abc")).lower()),
            "export.frameStart": int(frame_range[0]) if frame_range else None,
            "export.frameEnd": int(frame_range[1]) if len(frame_range) > 1 else None,
            "export.includeRootUV": bool(export.get("includeRootUV")),
            "export.includeStrandIds": bool(export.get("includeStrandIds")),
            "export.includeGuideCurves": bool(export.get("includeGuideCurves")),
            "export.writeMode": export.get("writeMode"),
            "unreal.expectedGroomAsset": unreal.get("expectedGroomAsset"),
            "unreal.expectedBindingAsset": unreal.get("expectedBindingAsset"),
            "unreal.targetSkeletalMesh": unreal.get("targetSkeletalMesh"),
            "unreal.materialSlot": unreal.get("materialSlot"),
        },
        "raw": {
            "namespace": asset.get("namespace"),
            "description": description,
            "scalp": scalp,
            "groom": groom,
            "strands": strands,
            "export": export,
            "unreal": unreal,
        },
    }


def _strand_fact(strand: Dict[str, Any]) -> Dict[str, Any]:
    root_uv = strand.get("rootUv")
    return {
        "id": str(strand.get("id", "")),
        "rootUv": [float(root_uv[0]), float(root_uv[1])] if isinstance(root_uv, list) and len(root_uv) >= 2 else None,
        "guide": bool(strand.get("guide")),
        "width": float(strand.get("width", 0.0) or 0.0),
        "groupId": strand.get("groupId"),
        "groupName": str(strand.get("groupName", "")),
        "materialSlot": str(strand.get("materialSlot", "")),
        "node": strand.get("node"),
        "pointCount": strand.get("pointCount"),
        "points": [
            [float(point[0]), float(point[1]), float(point[2])]
            for point in strand.get("points", [])
            if isinstance(point, list) and len(point) >= 3
        ],
    }


def _evaluate_asset(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = row.get("assetId")
    n = row.get("normalized", {})
    export_start = n.get("export.frameStart")
    export_end = n.get("export.frameEnd")
    return [
        _eval(
            asset_id,
            "protocol-carrier",
            n.get("groom.protocol.schema") == "groom-export@dcc-r46",
            "error",
            "Groom protocol carrier",
            "Groom export needs a typed protocol before guide/root data can be trusted.",
            str(n.get("groom.protocol.schema")),
            "Write groom-export@dcc-r46 on the groom root.",
        ),
        _eval(
            asset_id,
            "description-boundary",
            bool(n.get("description.name")) and not n.get("description.tmpToken"),
            "warning",
            "Description boundary",
            "Temporary XGen descriptions should not silently enter engine groom export.",
            str(n.get("description.name")),
            "Rename the description or route the temporary groom to owner review.",
        ),
        _eval(
            asset_id,
            "scalp-root-uv-set",
            bool(n.get("scalp.rootUVSetPresent")),
            "error",
            "Scalp root UV set",
            "Unreal groom binding needs a stable root UV set on the scalp mesh.",
            "expected=%s actual=%s" % (n.get("scalp.expectedUVSet"), n.get("scalp.actualUVSets")),
            "Generate or remap the root_uv set before Alembic export.",
        ),
        _eval(
            asset_id,
            "strand-id-coverage",
            not n.get("strands.missingIds") and not n.get("strands.duplicateIds"),
            "error",
            "Strand ID coverage",
            "Strand IDs must be present and unique so downstream cache diffs and binding errors are traceable.",
            "missingRows=%s duplicateIds=%s" % (n.get("strands.missingIds"), n.get("strands.duplicateIds")),
            "Regenerate stable strand IDs on the groom curves.",
        ),
        _eval(
            asset_id,
            "root-uv-coverage",
            not n.get("rootUV.missing") and not n.get("rootUV.invalid"),
            "error",
            "Root UV coverage",
            "Every strand must carry a valid [0,1] root UV before export to Unreal.",
            "missing=%s invalid=%s" % (n.get("rootUV.missing"), n.get("rootUV.invalid")),
            "Bake root UV from scalp attachment and reject out-of-range samples.",
        ),
        _eval(
            asset_id,
            "guide-curve-coverage",
            int(n.get("guides.count") or 0) >= int(n.get("guides.minimum") or 0)
            and not n.get("guides.missingRequired"),
            "error",
            "Guide curve coverage",
            "Guide curves are the authored controls for interpolated groom strands and must survive handoff.",
            "actual=%s minimum=%s missing=%s"
            % (n.get("guides.actual"), n.get("guides.minimum"), n.get("guides.missingRequired")),
            "Restore required guide curves or lower the guide requirement with owner approval.",
        ),
        _eval(
            asset_id,
            "alembic-payload-contract",
            bool(n.get("export.extensionMatched"))
            and bool(n.get("export.includeRootUV"))
            and bool(n.get("export.includeStrandIds"))
            and bool(n.get("export.includeGuideCurves")),
            "error",
            "Alembic payload contract",
            "The Alembic handoff must carry root UV, strand ID and guide curves with a .abc cache path.",
            "path=%s rootUV=%s strandIds=%s guides=%s"
            % (
                n.get("export.cachePath"),
                n.get("export.includeRootUV"),
                n.get("export.includeStrandIds"),
                n.get("export.includeGuideCurves"),
            ),
            "Export .abc with root UV, strand ID and guide curve payload enabled.",
        ),
        _eval(
            asset_id,
            "frame-range",
            export_start is not None and export_end is not None and int(export_start) <= int(export_end),
            "error",
            "Frame range",
            "Groom caches need a valid frame range even for single-frame static hair export.",
            "%s-%s" % (export_start, export_end),
            "Fix the cache frame range before publishing the Alembic receipt.",
        ),
        _eval(
            asset_id,
            "strand-budget",
            int(n.get("strands.budget") or 0) <= 0 or int(n.get("strands.count") or 0) <= int(n.get("strands.budget") or 0),
            "warning",
            "Strand budget",
            "Platform groom budgets must be explicit before the asset can be handed to runtime.",
            "count=%s budget=%s" % (n.get("strands.count"), n.get("strands.budget")),
            "Reduce generated strand count or move the groom into a higher-cost platform bucket.",
        ),
        _eval(
            asset_id,
            "unreal-binding-target",
            bool(n.get("unreal.expectedGroomAsset"))
            and bool(n.get("unreal.expectedBindingAsset"))
            and bool(n.get("unreal.targetSkeletalMesh"))
            and bool(n.get("unreal.materialSlot")),
            "error",
            "Unreal binding target",
            "Groom export is incomplete without target Groom, Binding, SkeletalMesh and material-slot intent.",
            "groom=%s binding=%s mesh=%s material=%s"
            % (
                n.get("unreal.expectedGroomAsset"),
                n.get("unreal.expectedBindingAsset"),
                n.get("unreal.targetSkeletalMesh"),
                n.get("unreal.materialSlot"),
            ),
            "Declare target Unreal groom, binding and material slot before engine import.",
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
    return {
        "gate": "Blocked" if blocked_assets else "Review" if review_assets else "Ready",
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


def _build_owner_actions(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    for row in evaluations:
        if row["status"] == "pass":
            continue
        actions.append(
            {
                "id": "owner-action:%s" % row["id"],
                "assetId": row["assetId"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "mutationScope": "owner_required" if row["status"] == "error" else "manual_review",
                "owner": _owner_for_rule(row["ruleId"]),
                "preview": row["fixPreview"],
            }
        )
    return actions


def _owner_for_rule(rule_id: str) -> str:
    if rule_id in {"alembic-payload-contract", "frame-range", "unreal-binding-target"}:
        return "engine-ta"
    if rule_id in {"strand-budget"}:
        return "platform-ta"
    return "groom-owner"


def _uv_in_range(value: List[float]) -> bool:
    return 0.0 <= float(value[0]) <= 1.0 and 0.0 <= float(value[1]) <= 1.0


def _reviewer_claims() -> List[str]:
    return [
        "Groom Export Inspector treats hair as a non-mesh handoff with root UV, strand ID, guide curve and Alembic payload requirements.",
        "The fixture includes one approved groom and one intentionally blocked temporary groom, so guide/ID/cache failures are visible in the package.",
        "Contract mode performs no scene, asset or engine writes; Maya L3 mode creates only public synthetic curves and custom attributes.",
    ]
