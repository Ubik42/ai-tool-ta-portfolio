"""Compare platform variant plans against Unreal runtime facts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import PORTFOLIO_ROOT, public_path, resolve_public_path


REPORT_VERSION = "platform-variant-unreal-runtime@0.1.0"


def build_runtime_report(plan_artifact_path: str | Path, runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    plan_path = resolve_public_path(plan_artifact_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    comparison = compare_runtime_to_plan(plan, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if runtime.get("executed") else "Blocked",
        "l3Status": "unreal_variant_runtime_assets_collected" if runtime.get("executed") else "blocked_by_missing_unreal_runtime",
        "sourcePlan": {
            "path": public_path(plan_path),
            "reportVersion": plan.get("reportVersion"),
            "evidenceLevel": plan.get("evidenceLevel"),
            "l3Status": plan.get("l3Status"),
        },
        "unrealRuntime": runtime,
        "runtimeFacts": runtime_snapshot.get("facts", {}),
        "comparison": comparison,
        "adapter": {
            "id": "platform-variant-unreal-runtime-probe",
            "name": "Platform Variant Unreal Runtime Probe",
            "methodSource": "Platform Variant Forge runtime-vs-plan verification",
            "protocolCarrier": "variant plan artifact + Unreal Python StaticMesh facts",
            "boundary": {
                "mutation": "public_test_project_fixture_write",
                "engineWrites": 0,
                "assetWrites": runtime.get("assetWrites", 0),
                "productionWrites": 0,
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public fixture only"),
            },
        },
        "reviewerClaims": [
            "R29 verifies the R28 PC/Mobile variant plan against actual Unreal StaticMesh runtime facts.",
            "The probe separates plan-ready rows from runtime drift, so reviewer can see whether a generated variant is truly engine-ready.",
            "Any writes are limited to synthetic public Unreal fixture assets under /Game/AI_Tool_TA.",
        ],
    }


def compare_runtime_to_plan(plan: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    runtime_facts = runtime_snapshot.get("facts", {})
    rows: List[Dict[str, Any]] = []
    for asset in plan.get("facts", {}).get("assets", []):
        source = asset.get("sourceAsset", {})
        for variant in asset.get("variants", []):
            rows.extend(_compare_variant(asset, source, variant, runtime_facts))
    return {
        "schema": "platform-variant-unreal-runtime-comparison@0.1.0",
        "summary": _summarize(rows),
        "rows": rows,
        "runtimeActions": _runtime_actions(rows),
    }


def _compare_variant(
    asset: Dict[str, Any],
    source: Dict[str, Any],
    variant: Dict[str, Any],
    runtime_facts: Dict[str, Any],
) -> List[Dict[str, Any]]:
    asset_id = asset.get("assetId")
    platform = variant.get("platform")
    target_path = variant.get("targetEnginePath")
    expected = variant.get("expected", {})
    normalized = variant.get("normalized", {})
    source_fact = runtime_facts.get(str(source.get("enginePath")), {})
    target_fact = runtime_facts.get(str(target_path), {})
    prefix = "%s:%s" % (asset_id, platform)
    expected_lod_count = len(expected.get("lods", []))
    expected_material_slots = _int(expected.get("materialSlots"))
    expected_collision_shapes = _int(expected.get("collisionSimpleShapes"))
    expected_triangles = _int(expected.get("triangles"))
    return [
        _row(prefix, "runtime-source-asset", bool(source_fact.get("exists")), "error", source.get("enginePath"), "Create or import the source Unreal asset before deriving variants."),
        _row(prefix, "runtime-target-asset", bool(target_fact.get("exists")), "error", target_path, "Create the planned platform variant asset under the target path."),
        _row(prefix, "runtime-path-policy", bool(target_fact.get("pathMatched")), "error", target_path, "Move runtime asset under the platform-scoped path from the variant plan."),
        _row(prefix, "runtime-lod-count", _int(target_fact.get("lodCount")) >= expected_lod_count, "warning", "actual=%s expected>=%s" % (target_fact.get("lodCount"), expected_lod_count), "Generate missing runtime LODs before platform signoff."),
        _row(prefix, "runtime-triangle-budget", _int(target_fact.get("triangleCount")) <= expected_triangles or _int(target_fact.get("triangleCount")) == 0, "warning", "actual=%s expected<=%s" % (target_fact.get("triangleCount"), expected_triangles), "Rebuild or decimate the runtime variant mesh."),
        _row(prefix, "runtime-material-budget", _int(target_fact.get("materialSlotCount")) <= expected_material_slots, "warning", "actual=%s expected<=%s" % (target_fact.get("materialSlotCount"), expected_material_slots), "Merge material slots or bake detail textures for the target platform."),
        _row(prefix, "runtime-nanite-policy", _nanite_matches(target_fact, expected), "warning", "actual=%s expected=%s" % (target_fact.get("naniteEnabled"), expected.get("nanite")), "Apply the platform Nanite policy to the runtime StaticMesh asset."),
        _row(prefix, "runtime-collision-policy", _collision_matches(target_fact, expected_collision_shapes), "warning", "simple=%s expected<=%s complexAsSimple=%s" % (target_fact.get("simpleShapeCount"), expected_collision_shapes, target_fact.get("complexAsSimple")), "Regenerate simplified collision for the runtime platform variant."),
        _row(prefix, "plan-source-evidence", bool(normalized.get("target.sourceEvidenceJoined")), "warning", normalized.get("target.unrealPresetGate"), "Attach or regenerate Unreal preset fact comparison before approving runtime variants."),
    ]


def _row(row_id: str, rule_id: str, passed: bool, fail_status: str, evidence: Any, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (row_id, rule_id),
        "assetId": row_id.split(":", 1)[0],
        "platform": row_id.split(":", 1)[1] if ":" in row_id else "",
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": str(evidence),
        "fixPreview": "None" if passed else fix_preview,
    }


def _summarize(rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    row_list = list(rows)
    variant_ids = sorted({"%s:%s" % (row["assetId"], row["platform"]) for row in row_list})
    blocked = sorted({"%s:%s" % (row["assetId"], row["platform"]) for row in row_list if row["status"] == "error"})
    review = sorted({"%s:%s" % (row["assetId"], row["platform"]) for row in row_list if row["status"] == "warning"} - set(blocked))
    ready = sorted(set(variant_ids) - set(blocked) - set(review))
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "variantCount": len(variant_ids),
        "readyVariants": len(ready),
        "reviewVariants": len(review),
        "blockedVariants": len(blocked),
        "pass": sum(1 for row in row_list if row["status"] == "pass"),
        "warning": sum(1 for row in row_list if row["status"] == "warning"),
        "error": sum(1 for row in row_list if row["status"] == "error"),
        "readyVariantIds": ready,
        "reviewVariantIds": review,
        "blockedVariantIds": blocked,
    }


def _runtime_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": "runtime-action:%s" % row["id"],
            "assetId": row["assetId"],
            "platform": row["platform"],
            "ruleId": row["ruleId"],
            "status": row["status"],
            "preview": row["fixPreview"],
        }
        for row in rows
        if row["status"] != "pass"
    ]


def _nanite_matches(target_fact: Dict[str, Any], expected: Dict[str, Any]) -> bool:
    actual = target_fact.get("naniteEnabled")
    if actual is None:
        return True
    return bool(actual) == bool(expected.get("nanite"))


def _collision_matches(target_fact: Dict[str, Any], expected_simple_shapes: int) -> bool:
    simple_shapes = _int(target_fact.get("simpleShapeCount"))
    complex_as_simple = bool(target_fact.get("complexAsSimple"))
    return simple_shapes <= expected_simple_shapes and not complex_as_simple


def _int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0
