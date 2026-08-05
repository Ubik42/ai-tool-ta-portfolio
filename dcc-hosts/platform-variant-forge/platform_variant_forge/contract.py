"""Platform variant planning contract.

The contract turns PC to Mobile asset derivation into auditable facts: budget,
LOD, material, texture, collision, engine path and owner boundaries.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "platform-variant-forge-contract@0.1.0"
NORMALIZED_SCHEMA = "platform-variant-forge-input@0.1.0"
FIXTURE_SCHEMA = "synthetic-platform-variant-plan@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def resolve_public_path(path: str | Path) -> Path:
    text = str(path)
    if text.startswith("<repo>\\"):
        return PORTFOLIO_ROOT / text.replace("<repo>\\", "", 1)
    return Path(path)


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != FIXTURE_SCHEMA:
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def build_report(fixture_path: str | Path, unreal_preset_fact_path: str | Path | None = None) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    source_evidence = _load_source_evidence(fixture, unreal_preset_fact_path)
    facts = build_facts(fixture, source_evidence)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-linked" if source_evidence.get("available") else "L2",
        "l3Status": "platform_variant_plan_joined_to_unreal_facts"
        if source_evidence.get("available")
        else "contract_fixture_collected",
        "fixture": {
            "path": public_path(fixture_path),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "sourceEvidence": source_evidence,
        "adapter": {
            "id": "platform-variant-forge",
            "name": "Platform Variant Forge",
            "methodSource": "Lightbox PC to Mobile asset derivation / LOD material texture collision budget policy",
            "protocolCarrier": "variant plan fixture + engine preset fact comparison artifact",
            "boundary": {
                "mutation": "planning_artifact_only",
                "sceneWrites": 0,
                "engineWrites": 0,
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": _reviewer_claims(),
    }


def build_facts(fixture: Dict[str, Any], source_evidence: Dict[str, Any]) -> Dict[str, Any]:
    policies = {policy["id"]: policy for policy in fixture.get("platformPolicies", [])}
    rows = [
        _build_asset_facts(asset, policies, source_evidence)
        for asset in fixture.get("assets", [])
    ]
    return {
        "schema": NORMALIZED_SCHEMA,
        "sourceEvidenceLevel": source_evidence.get("evidenceLevel"),
        "sourceGate": source_evidence.get("gate"),
        "assets": rows,
    }


def evaluate_scene(facts: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("assets", []):
        for variant in row.get("variants", []):
            evaluations.extend(_evaluate_variant(row, variant))
    return {
        "schema": "platform-variant-forge-evaluation@0.1.0",
        "summary": _summarize(evaluations),
        "evaluations": evaluations,
        "variantActions": _variant_actions(evaluations),
    }


def _load_source_evidence(fixture: Dict[str, Any], override_path: str | Path | None) -> Dict[str, Any]:
    evidence = fixture.get("sourceEvidence", {})
    path_text = str(override_path or evidence.get("unrealPresetFactComparison", ""))
    if not path_text:
        return {"available": False}
    path = resolve_public_path(path_text)
    if not path.exists():
        return {"available": False, "path": public_path(path), "missing": True}
    payload = json.loads(path.read_text(encoding="utf-8"))
    summary = payload.get("summary", {})
    return {
        "available": True,
        "path": public_path(path),
        "reportVersion": payload.get("reportVersion"),
        "evidenceLevel": payload.get("sourceReport", {}).get("evidenceLevel"),
        "l3Status": payload.get("sourceReport", {}).get("l3Status"),
        "gate": summary.get("gate"),
        "factRows": summary.get("factRows"),
        "matched": summary.get("matched"),
        "drift": summary.get("drift"),
        "waived": summary.get("waived"),
        "blocked": summary.get("blocked"),
        "platformSplit": summary.get("platformSplit"),
        "presetSummaries": payload.get("presetSummaries", []),
        "assetComparisons": payload.get("assetComparisons", []),
    }


def _build_asset_facts(
    asset: Dict[str, Any],
    policies: Dict[str, Dict[str, Any]],
    source_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    source = asset.get("sourceAsset", {})
    variants = []
    for plan in asset.get("variantPlans", []):
        policy = policies.get(plan.get("platform"), {})
        expected = plan.get("expected", {})
        variants.append(
            {
                "platform": plan.get("platform"),
                "targetEnginePath": plan.get("targetEnginePath"),
                "requestedActions": plan.get("requestedActions", []),
                "ownerApproval": plan.get("ownerApproval"),
                "expected": expected,
                "policy": policy,
                "normalized": _variant_normalized(asset, source, plan, expected, policy, source_evidence),
            }
        )
    return {
        "assetId": asset.get("id"),
        "assetLabel": asset.get("label"),
        "ownerState": asset.get("ownerState"),
        "sourcePlatform": asset.get("sourcePlatform"),
        "sourceAsset": source,
        "variants": variants,
    }


def _variant_normalized(
    asset: Dict[str, Any],
    source: Dict[str, Any],
    plan: Dict[str, Any],
    expected: Dict[str, Any],
    policy: Dict[str, Any],
    source_evidence: Dict[str, Any],
) -> Dict[str, Any]:
    target_path = str(plan.get("targetEnginePath", ""))
    platform = str(plan.get("platform", ""))
    required_lods = [str(lod) for lod in policy.get("requiredLods", [])]
    actual_lods = [str(lod) for lod in expected.get("lods", [])]
    allowed_features = {str(feature) for feature in policy.get("allowedShaderFeatures", [])}
    actual_features = {str(feature) for feature in expected.get("shaderFeatures", [])}
    collision_policy = policy.get("collision", {})
    path_prefix = "/Game/AI_Tool_TA/Props/%s/" % ("Mobile" if platform == "mobile" else "PC")
    if "vehicle" in str(asset.get("id", "")).lower():
        path_prefix = "/Game/AI_Tool_TA/Vehicles/%s/" % ("Mobile" if platform == "mobile" else "PC")
    return {
        "source.enginePath": source.get("enginePath"),
        "target.enginePath": target_path,
        "target.expectedPrefix": path_prefix,
        "target.pathMatched": target_path.startswith(path_prefix),
        "target.ownerApproval": plan.get("ownerApproval"),
        "target.requestedActions": plan.get("requestedActions", []),
        "target.sourceEvidenceJoined": bool(source_evidence.get("available")),
        "target.unrealPresetGate": source_evidence.get("gate"),
        "budget.triangles": _int(expected.get("triangles")),
        "budget.maxTriangles": _int(policy.get("maxTriangles")),
        "budget.texturePixels": _int(expected.get("textureMaxPixels")),
        "budget.maxTexturePixels": _int(policy.get("maxTexturePixels")),
        "budget.textureMemoryMb": _int(expected.get("textureMemoryMb")),
        "budget.maxTextureMemoryMb": _int(policy.get("maxTextureMemoryMb")),
        "budget.materialSlots": _int(expected.get("materialSlots")),
        "budget.maxMaterialSlots": _int(policy.get("maxMaterialSlots")),
        "budget.drawCalls": _int(expected.get("drawCalls")),
        "budget.maxDrawCalls": _int(policy.get("maxDrawCalls")),
        "lod.required": required_lods,
        "lod.actual": actual_lods,
        "lod.missing": sorted(set(required_lods) - set(actual_lods)),
        "nanite.actual": bool(expected.get("nanite")),
        "nanite.allowed": bool(policy.get("allowNanite")),
        "shader.disallowed": sorted(actual_features - allowed_features),
        "collision.simpleShapes": _int(expected.get("collisionSimpleShapes")),
        "collision.maxSimpleShapes": _int(collision_policy.get("maxSimpleShapes")),
        "collision.complexAsSimple": bool(expected.get("complexAsSimple")),
        "collision.allowComplexAsSimple": bool(collision_policy.get("allowComplexAsSimple")),
    }


def _evaluate_variant(asset: Dict[str, Any], variant: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = asset.get("assetId")
    platform = variant.get("platform")
    n = variant.get("normalized", {})
    prefix = "%s:%s" % (asset_id, platform)
    return [
        _eval(prefix, "source-evidence-join", n.get("target.sourceEvidenceJoined"), "warning", "Source evidence join", "Variant plans should reference existing engine preset fact evidence.", str(n.get("target.unrealPresetGate")), "Regenerate or attach Unreal preset fact comparison evidence."),
        _eval(prefix, "target-path-policy", n.get("target.pathMatched"), "error", "Target path policy", "Platform variants must land in a platform-scoped engine path.", n.get("target.enginePath"), "Move the target asset under the approved platform path prefix."),
        _eval(prefix, "owner-approval", bool(n.get("target.ownerApproval")), "error", "Owner approval", "Platform degradation can change gameplay and visual intent, so an accountable owner must approve the plan.", str(n.get("target.ownerApproval")), "Attach art / tech owner approval before publishing the variant."),
        _eval(prefix, "triangle-budget", _le(n, "budget.triangles", "budget.maxTriangles"), "error", "Triangle budget", "Mobile and PC variants must stay under their target geometry budget.", _budget_text(n, "budget.triangles", "budget.maxTriangles"), "Generate lower LODs or split the asset."),
        _eval(prefix, "texture-budget", _le(n, "budget.texturePixels", "budget.maxTexturePixels") and _le(n, "budget.textureMemoryMb", "budget.maxTextureMemoryMb"), "error", "Texture budget", "Texture size and memory budget must match the target platform.", "pixels=%s/%s memory=%s/%s" % (n.get("budget.texturePixels"), n.get("budget.maxTexturePixels"), n.get("budget.textureMemoryMb"), n.get("budget.maxTextureMemoryMb")), "Downscale or repack textures for the platform variant."),
        _eval(prefix, "material-draw-budget", _le(n, "budget.materialSlots", "budget.maxMaterialSlots") and _le(n, "budget.drawCalls", "budget.maxDrawCalls"), "error", "Material and draw-call budget", "Variant generation must merge materials and reduce draw calls where the platform requires it.", "materials=%s/%s draws=%s/%s" % (n.get("budget.materialSlots"), n.get("budget.maxMaterialSlots"), n.get("budget.drawCalls"), n.get("budget.maxDrawCalls")), "Merge material slots or bake detail into shared textures."),
        _eval(prefix, "lod-coverage", not n.get("lod.missing"), "error", "LOD coverage", "Platform variants need the required LOD chain before runtime import approval.", str(n.get("lod.missing")), "Generate the missing LODs or attach a platform waiver."),
        _eval(prefix, "nanite-policy", n.get("nanite.allowed") or not n.get("nanite.actual"), "error", "Nanite policy", "Mobile variants cannot inherit PC-only Nanite state.", "actual=%s allowed=%s" % (n.get("nanite.actual"), n.get("nanite.allowed")), "Disable Nanite or route the asset to a PC-only package."),
        _eval(prefix, "shader-feature-policy", not n.get("shader.disallowed"), "warning", "Shader feature policy", "Platform variants should not carry expensive shader features that the target policy disallows.", str(n.get("shader.disallowed")), "Bake or replace disallowed material features."),
        _eval(prefix, "collision-policy", _le(n, "collision.simpleShapes", "collision.maxSimpleShapes") and (n.get("collision.allowComplexAsSimple") or not n.get("collision.complexAsSimple")), "error", "Collision policy", "Collision simplification is gameplay-sensitive and must meet target runtime policy.", "simple=%s/%s complexAsSimple=%s" % (n.get("collision.simpleShapes"), n.get("collision.maxSimpleShapes"), n.get("collision.complexAsSimple")), "Simplify collision and remove complex-as-simple before publish."),
    ]


def _eval(row_id: str, rule_id: str, passed: bool, fail_status: str, label: str, reason: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (row_id, rule_id),
        "assetId": row_id.split(":", 1)[0],
        "platform": row_id.split(":", 1)[1] if ":" in row_id else "",
        "ruleId": rule_id,
        "label": label,
        "status": "pass" if passed else fail_status,
        "reason": reason,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summarize(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(evaluations)
    variant_ids = sorted({"%s:%s" % (row["assetId"], row["platform"]) for row in rows})
    blocked = sorted({"%s:%s" % (row["assetId"], row["platform"]) for row in rows if row["status"] == "error"})
    review = sorted({"%s:%s" % (row["assetId"], row["platform"]) for row in rows if row["status"] == "warning"} - set(blocked))
    ready = sorted(set(variant_ids) - set(blocked) - set(review))
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "assetCount": len({row["assetId"] for row in rows}),
        "variantCount": len(variant_ids),
        "readyVariants": len(ready),
        "reviewVariants": len(review),
        "blockedVariants": len(blocked),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "readyVariantIds": ready,
        "reviewVariantIds": review,
        "blockedVariantIds": blocked,
    }


def _variant_actions(evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": "action:%s" % row["id"],
            "assetId": row["assetId"],
            "platform": row["platform"],
            "ruleId": row["ruleId"],
            "status": row["status"],
            "mutationScope": "plan_only_owner_required" if row["status"] == "error" else "plan_only_review",
            "preview": row["fixPreview"],
        }
        for row in evaluations
        if row["status"] != "pass"
    ]


def _le(values: Dict[str, Any], actual_key: str, limit_key: str) -> bool:
    return _int(values.get(actual_key)) <= _int(values.get(limit_key))


def _budget_text(values: Dict[str, Any], actual_key: str, limit_key: str) -> str:
    return "%s/%s" % (values.get(actual_key), values.get(limit_key))


def _int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _reviewer_claims() -> List[str]:
    return [
        "Platform Variant Forge explains PC to Mobile derivation as deterministic budget and policy rows, not as an opaque export button.",
        "The report joins existing Unreal preset fact comparison evidence, so platform split decisions stay connected to engine-side facts.",
        "All outputs are planning artifacts; no Maya scene, Unreal asset, source texture or production package is mutated.",
    ]
