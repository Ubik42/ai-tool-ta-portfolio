"""Collect and evaluate Unreal material texture facts for platform variants."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path, resolve_public_path


REPORT_VERSION = "platform-variant-texture-runtime@0.1.0"


def build_texture_runtime_report(
    plan_artifact_path: str | Path,
    runtime_artifact_path: str | Path,
    texture_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    plan_path = resolve_public_path(plan_artifact_path)
    runtime_path = resolve_public_path(runtime_artifact_path)
    plan_report = json.loads(plan_path.read_text(encoding="utf-8"))
    runtime_report = json.loads(runtime_path.read_text(encoding="utf-8")) if runtime_path.exists() else {}
    evaluation = evaluate_texture_runtime(plan_report, texture_snapshot)
    runtime = texture_snapshot.get("runtime", {})
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if runtime.get("executed") else "Blocked",
        "l3Status": "unreal_material_texture_facts_collected"
        if runtime.get("executed")
        else "blocked_by_missing_unreal_runtime",
        "sourcePlan": {
            "path": public_path(plan_path),
            "reportVersion": plan_report.get("reportVersion"),
            "evidenceLevel": plan_report.get("evidenceLevel"),
            "l3Status": plan_report.get("l3Status"),
        },
        "sourceRuntime": {
            "path": public_path(runtime_path),
            "reportVersion": runtime_report.get("reportVersion"),
            "evidenceLevel": runtime_report.get("evidenceLevel"),
            "l3Status": runtime_report.get("l3Status"),
            "engineVersion": runtime_report.get("unrealRuntime", {}).get("engineVersion"),
        },
        "unrealRuntime": runtime,
        "textureFacts": texture_snapshot.get("facts", {}),
        "evaluation": evaluation,
        "adapter": {
            "id": "platform-variant-texture-runtime",
            "name": "Platform Variant Texture Runtime Collector",
            "methodSource": "Unreal StaticMesh material slots to Texture2D budget evidence",
            "protocolCarrier": "variant plan artifact + Unreal Python material dependency facts",
            "boundary": {
                "mutation": "runtime_fact_collection_only",
                "engineWrites": 0,
                "assetWrites": runtime.get("assetWrites", 0),
                "productionWrites": 0,
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public fixture only"),
            },
        },
        "reviewerClaims": [
            "R31 collects material slot, material dependency and Texture2D budget facts from Unreal instead of treating texture bake as an unknown placeholder.",
            "The report separates target asset absence, missing source texture payload and numeric texture budget drift.",
            "Collection is read-only except for public synthetic fixture preparation under /Game/AI_Tool_TA.",
        ],
    }


def evaluate_texture_runtime(plan_report: Dict[str, Any], texture_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    facts = texture_snapshot.get("facts", {})
    for variant_id, plan in sorted(_plan_variant_index(plan_report).items()):
        fact = facts.get(str(plan.get("targetEnginePath")), {})
        rows.extend(_evaluate_variant_texture(plan, fact))
    return {
        "schema": "platform-variant-texture-runtime-evaluation@0.1.0",
        "summary": _summarize(rows),
        "rows": rows,
        "textureBakeActions": _texture_actions(rows),
    }


def _plan_variant_index(plan_report: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    rows: Dict[str, Dict[str, Any]] = {}
    for asset in plan_report.get("facts", {}).get("assets", []):
        source = asset.get("sourceAsset", {})
        for variant in asset.get("variants", []):
            variant_id = "%s:%s" % (asset.get("assetId"), variant.get("platform"))
            rows[variant_id] = {
                "variantId": variant_id,
                "assetId": asset.get("assetId"),
                "assetLabel": asset.get("assetLabel"),
                "platform": variant.get("platform"),
                "sourceEnginePath": source.get("enginePath"),
                "targetEnginePath": variant.get("targetEnginePath"),
                "requestedActions": list(variant.get("requestedActions", [])),
                "expected": variant.get("expected", {}),
                "policy": variant.get("policy", {}),
            }
    return rows


def _evaluate_variant_texture(plan: Dict[str, Any], fact: Dict[str, Any]) -> List[Dict[str, Any]]:
    expected = plan.get("expected", {})
    requested = set(plan.get("requestedActions", []))
    target_exists = bool(fact.get("exists"))
    material_count = _int(fact.get("materialSlotCount"))
    texture_count = _int(fact.get("textureDependencyCount"))
    dependency_queries = _int(fact.get("dependencyQueryCount"))
    max_dimension = _int(fact.get("maxTextureDimension"))
    estimated_mb = _float(fact.get("estimatedTextureMemoryMb"))
    expected_pixels = _int(expected.get("textureMaxPixels"))
    expected_memory = _float(expected.get("textureMemoryMb"))
    downscale_requested = "downscale-textures" in requested
    return [
        _row(
            plan,
            "runtime-target-asset",
            target_exists,
            "error",
            "target=%s exists=%s" % (plan.get("targetEnginePath"), target_exists),
            "Create or duplicate the platform variant before collecting texture facts.",
        ),
        _row(
            plan,
            "runtime-material-chain",
            not target_exists or material_count > 0,
            "warning",
            "materialSlots=%s materialPaths=%s" % (material_count, ",".join(fact.get("materialPaths", []))),
            "Assign platform material slots before texture budget signoff.",
        ),
        _row(
            plan,
            "runtime-texture-dependency-query",
            not target_exists or dependency_queries >= material_count,
            "warning",
            "queries=%s materials=%s errors=%s"
            % (dependency_queries, material_count, ",".join(fact.get("dependencyErrors", []))),
            "Query material dependencies through Unreal Asset Registry or material expressions.",
        ),
        _row(
            plan,
            "runtime-texture-payload",
            not target_exists or texture_count > 0 or not downscale_requested,
            "warning",
            "textures=%s requestedDownscale=%s" % (texture_count, downscale_requested),
            "Attach source Texture2D payload before running a texture downscale or bake executor.",
        ),
        _row(
            plan,
            "runtime-texture-max-size",
            not target_exists or max_dimension == 0 or max_dimension <= expected_pixels,
            "warning",
            "maxDimension=%s expected<=%s" % (max_dimension, expected_pixels),
            "Downscale textures that exceed the platform maximum pixel dimension.",
        ),
        _row(
            plan,
            "runtime-texture-memory-budget",
            not target_exists or texture_count == 0 or estimated_mb <= expected_memory,
            "warning",
            "estimatedMb=%.3f expected<=%.3f textures=%s" % (estimated_mb, expected_memory, texture_count),
            "Repack or downsample texture set to fit the target memory budget.",
        ),
        _row(
            plan,
            "runtime-texture-settings-readable",
            not target_exists or texture_count == 0 or bool(fact.get("textureSettingsReadable")),
            "warning",
            "readable=%s compression=%s srgb=%s"
            % (
                fact.get("textureSettingsReadable"),
                ",".join(fact.get("compressionSettings", [])),
                ",".join(fact.get("srgbStates", [])),
            ),
            "Collect compression, color-space and LOD group settings before executor approval.",
        ),
    ]


def _row(
    plan: Dict[str, Any],
    rule_id: str,
    passed: bool,
    fail_status: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (plan["variantId"], rule_id),
        "assetId": plan.get("assetId"),
        "platform": plan.get("platform"),
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
        "targetEnginePath": plan.get("targetEnginePath"),
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


def _texture_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for row in rows:
        if row["status"] == "pass":
            continue
        actions.append(
            {
                "id": "texture-action:%s" % row["id"],
                "assetId": row["assetId"],
                "platform": row["platform"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "mutationScope": "dry_run_texture_plan_only",
                "preview": row["fixPreview"],
                "targetEnginePath": row["targetEnginePath"],
            }
        )
    return actions


def _int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _float(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0
