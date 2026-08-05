"""Build dry-run generation plans from platform variant runtime drift."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path, resolve_public_path


REPORT_VERSION = "platform-variant-generation-plan@0.1.0"


def build_generation_report(runtime_artifact_path: str | Path) -> Dict[str, Any]:
    runtime_path = resolve_public_path(runtime_artifact_path)
    runtime_report = json.loads(runtime_path.read_text(encoding="utf-8"))
    plan_path = resolve_public_path(runtime_report.get("sourcePlan", {}).get("path", ""))
    plan_report = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else {}
    operations = build_operations(runtime_report, plan_report)
    summary = _summarize(operations)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-derived" if runtime_report.get("evidenceLevel") == "L3" else "L2",
        "l3Status": "runtime_drift_to_generation_plan"
        if runtime_report.get("evidenceLevel") == "L3"
        else "contract_generation_plan_only",
        "sourceRuntime": {
            "path": public_path(runtime_path),
            "reportVersion": runtime_report.get("reportVersion"),
            "evidenceLevel": runtime_report.get("evidenceLevel"),
            "l3Status": runtime_report.get("l3Status"),
            "engineVersion": runtime_report.get("unrealRuntime", {}).get("engineVersion"),
        },
        "sourcePlan": {
            "path": public_path(plan_path),
            "reportVersion": plan_report.get("reportVersion"),
            "evidenceLevel": plan_report.get("evidenceLevel"),
            "l3Status": plan_report.get("l3Status"),
        },
        "summary": summary,
        "operations": operations,
        "executorContract": _executor_contract(summary),
        "adapter": {
            "id": "platform-variant-generation-planner",
            "name": "Platform Variant Auto LOD / Material Bake Planner",
            "methodSource": "Platform variant runtime drift to dry-run generation plan",
            "protocolCarrier": "R28 variant plan + R29 Unreal runtime facts",
            "boundary": {
                "mutation": "dry_run_generation_plan_only",
                "sceneWrites": 0,
                "engineWrites": 0,
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "reviewerClaims": [
            "R30 turns runtime drift rows into explicit generation operations instead of leaving them as generic warnings.",
            "Each operation carries its owner approval, transaction boundary, deterministic parameters and rollback preview.",
            "The artifact stays dry-run: it explains what an Unreal executor would do without mutating production assets.",
        ],
    }


def build_operations(runtime_report: Dict[str, Any], plan_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    runtime_rows = runtime_report.get("comparison", {}).get("rows", [])
    runtime_facts = runtime_report.get("runtimeFacts", {})
    row_index = _row_index(runtime_rows)
    plan_variants = _plan_variant_index(plan_report)
    operations: List[Dict[str, Any]] = []
    for variant_id in sorted(plan_variants):
        plan = plan_variants[variant_id]
        target_path = str(plan.get("targetEnginePath"))
        source_path = str(plan.get("sourceEnginePath"))
        target_fact = runtime_facts.get(target_path, {})
        source_fact = runtime_facts.get(source_path, {})
        operations.extend(_precondition_operations(plan, source_fact, target_fact, row_index))
        if _exists(source_fact) and _exists(target_fact):
            operations.extend(_requested_action_operations(plan, target_fact, row_index))
            operations.extend(_runtime_drift_operations(plan, target_fact, row_index))
    return _dedupe_operations(operations)


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
                "ownerState": asset.get("ownerState"),
                "ownerApproval": variant.get("ownerApproval"),
                "sourceEnginePath": source.get("enginePath"),
                "targetEnginePath": variant.get("targetEnginePath"),
                "requestedActions": list(variant.get("requestedActions", [])),
                "expected": variant.get("expected", {}),
                "policy": variant.get("policy", {}),
                "normalized": variant.get("normalized", {}),
            }
    return rows


def _precondition_operations(
    plan: Dict[str, Any],
    source_fact: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    operations = []
    if not _exists(source_fact):
        operations.append(
            _operation(
                plan,
                "create-or-import-source",
                "Blocked",
                "runtime-source-asset",
                row_index,
                "Source StaticMesh is absent in Unreal runtime.",
                "Import source StaticMesh before platform derivation.",
                {"sourceEnginePath": plan.get("sourceEnginePath")},
                "asset_tools.import_asset_tasks([source_import_task])",
                approval_required=True,
            )
        )
    if not _exists(target_fact):
        operations.append(
            _operation(
                plan,
                "create-target-variant",
                "Blocked",
                "runtime-target-asset",
                row_index,
                "Target platform variant asset is absent in Unreal runtime.",
                "Create the platform target asset under the planned path.",
                {
                    "sourceEnginePath": plan.get("sourceEnginePath"),
                    "targetEnginePath": plan.get("targetEnginePath"),
                },
                "EditorAssetLibrary.duplicate_asset(source_path, target_path)",
                approval_required=True,
            )
        )
    return operations


def _requested_action_operations(
    plan: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    operations = []
    for action in plan.get("requestedActions", []):
        if action == "generate-lod2":
            operations.append(_lod_operation(plan, target_fact, row_index, action))
        elif action == "disable-nanite":
            operations.append(_nanite_operation(plan, target_fact, row_index, action, expected=False))
        elif action == "merge-materials":
            operations.append(_material_operation(plan, target_fact, row_index, action))
        elif action == "downscale-textures":
            operations.append(_texture_operation(plan, target_fact, row_index, action))
        elif action == "simplify-collision":
            operations.append(_collision_operation(plan, target_fact, row_index, action))
        elif action in ("rename-path", "preserve-master"):
            operations.append(_path_operation(plan, target_fact, row_index, action))
    return operations


def _runtime_drift_operations(
    plan: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    operations = []
    requested = set(plan.get("requestedActions", []))
    if _row_status(plan, row_index, "runtime-lod-count") == "warning" and not _has_requested_lod_action(requested):
        operations.append(_lod_operation(plan, target_fact, row_index, "generate-missing-runtime-lods"))
    if _row_status(plan, row_index, "runtime-nanite-policy") == "warning":
        operations.append(
            _nanite_operation(
                plan,
                target_fact,
                row_index,
                "apply-runtime-nanite-policy",
                expected=bool(plan.get("expected", {}).get("nanite")),
            )
        )
    if _row_status(plan, row_index, "runtime-material-budget") == "warning":
        operations.append(_material_operation(plan, target_fact, row_index, "repair-runtime-material-budget"))
    if _row_status(plan, row_index, "runtime-collision-policy") == "warning":
        operations.append(_collision_operation(plan, target_fact, row_index, "repair-runtime-collision-policy"))
    return operations


def _has_requested_lod_action(requested: Iterable[str]) -> bool:
    return any(str(action).startswith("generate-lod") for action in requested)


def _lod_operation(
    plan: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
    action: str,
) -> Dict[str, Any]:
    expected_lods = list(plan.get("expected", {}).get("lods", []))
    actual_lods = _int(target_fact.get("lodCount"))
    missing = expected_lods[actual_lods:] if actual_lods < len(expected_lods) else []
    has_geometry = _int(target_fact.get("triangleCount")) > 0 or _int(target_fact.get("vertexCount")) > 0
    status = "Satisfied" if not missing else "Ready" if has_geometry else "Review"
    reason = "LOD chain already satisfies the platform plan."
    if missing and has_geometry:
        reason = "Runtime StaticMesh needs deterministic LOD generation."
    elif missing:
        reason = "Runtime mesh exists but geometry counts are not readable in the synthetic fixture; keep as executor readiness."
    return _operation(
        plan,
        action,
        status,
        "runtime-lod-count",
        row_index,
        reason,
        "Generate missing LODs %s with platform reduction settings." % missing,
        {
            "targetEnginePath": plan.get("targetEnginePath"),
            "actualLodCount": actual_lods,
            "expectedLods": expected_lods,
            "missingLods": missing,
            "screenSizePolicy": _screen_size_policy(plan.get("platform"), len(expected_lods)),
            "reductionSettings": _reduction_policy(plan.get("platform"), missing),
        },
        "StaticMeshEditorSubsystem.set_lods(target_mesh, lod_settings)",
        approval_required=bool(missing),
    )


def _nanite_operation(
    plan: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
    action: str,
    expected: bool,
) -> Dict[str, Any]:
    actual = target_fact.get("naniteEnabled")
    status = "Satisfied" if actual is not None and bool(actual) == bool(expected) else "Ready"
    return _operation(
        plan,
        action,
        status,
        "runtime-nanite-policy",
        row_index,
        "Runtime Nanite flag matches policy." if status == "Satisfied" else "Runtime Nanite flag differs from platform policy.",
        "Set Nanite enabled=%s on the target StaticMesh." % bool(expected),
        {
            "targetEnginePath": plan.get("targetEnginePath"),
            "actualNanite": actual,
            "expectedNanite": bool(expected),
        },
        "target_mesh.get_editor_property('nanite_settings').enabled = expected_nanite",
        approval_required=status != "Satisfied",
    )


def _material_operation(
    plan: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
    action: str,
) -> Dict[str, Any]:
    actual_slots = _int(target_fact.get("materialSlotCount"))
    expected_slots = _int(plan.get("expected", {}).get("materialSlots"))
    status = "Satisfied" if actual_slots <= expected_slots else "Ready"
    return _operation(
        plan,
        action,
        status,
        "runtime-material-budget",
        row_index,
        "Material slot budget already matches runtime target." if status == "Satisfied" else "Runtime material slots exceed platform budget.",
        "Bake detail materials into shared textures and remap material slots.",
        {
            "targetEnginePath": plan.get("targetEnginePath"),
            "actualMaterialSlots": actual_slots,
            "expectedMaterialSlots": expected_slots,
            "materialPaths": target_fact.get("materialPaths", []),
        },
        "MaterialEditingLibrary.reassign_material_slots(target_mesh, baked_material)",
        approval_required=status != "Satisfied",
    )


def _texture_operation(
    plan: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
    action: str,
) -> Dict[str, Any]:
    expected = plan.get("expected", {})
    return _operation(
        plan,
        action,
        "Review",
        "runtime-texture-budget",
        row_index,
        "Runtime texture source facts are not collected yet; planner can only emit the bake contract.",
        "Downscale texture set and repack platform material payload.",
        {
            "targetEnginePath": plan.get("targetEnginePath"),
            "expectedTextureMaxPixels": expected.get("textureMaxPixels"),
            "expectedTextureMemoryMb": expected.get("textureMemoryMb"),
            "materialPaths": target_fact.get("materialPaths", []),
            "missingRuntimeTextureFacts": True,
        },
        "Texture pipeline adapter exports resized maps before Unreal material reassignment.",
        approval_required=True,
    )


def _collision_operation(
    plan: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
    action: str,
) -> Dict[str, Any]:
    actual_shapes = _int(target_fact.get("simpleShapeCount"))
    expected_shapes = _int(plan.get("expected", {}).get("collisionSimpleShapes"))
    complex_as_simple = bool(target_fact.get("complexAsSimple"))
    status = "Satisfied" if actual_shapes <= expected_shapes and not complex_as_simple else "Ready"
    return _operation(
        plan,
        action,
        status,
        "runtime-collision-policy",
        row_index,
        "Collision policy already matches runtime target." if status == "Satisfied" else "Runtime collision differs from platform policy.",
        "Regenerate simplified collision shapes for platform runtime.",
        {
            "targetEnginePath": plan.get("targetEnginePath"),
            "actualSimpleShapes": actual_shapes,
            "expectedSimpleShapes": expected_shapes,
            "complexAsSimple": complex_as_simple,
        },
        "EditorStaticMeshLibrary.remove_collisions(target_mesh); add_simple_collisions(target_mesh)",
        approval_required=status != "Satisfied",
    )


def _path_operation(
    plan: Dict[str, Any],
    target_fact: Dict[str, Any],
    row_index: Dict[str, Dict[str, Any]],
    action: str,
) -> Dict[str, Any]:
    status = "Satisfied" if bool(target_fact.get("pathMatched")) else "Blocked"
    return _operation(
        plan,
        action,
        status,
        "runtime-path-policy",
        row_index,
        "Runtime target path already matches platform scope." if status == "Satisfied" else "Runtime target path is outside platform scope.",
        "Move or duplicate the asset under the platform-scoped path.",
        {
            "targetEnginePath": plan.get("targetEnginePath"),
            "expectedPrefix": plan.get("normalized", {}).get("target.expectedPrefix"),
            "pathMatched": bool(target_fact.get("pathMatched")),
        },
        "EditorAssetLibrary.rename_asset(source_path, platform_scoped_path)",
        approval_required=status != "Satisfied",
    )


def _operation(
    plan: Dict[str, Any],
    action: str,
    status: str,
    rule_id: str,
    row_index: Dict[str, Dict[str, Any]],
    reason: str,
    preview: str,
    params: Dict[str, Any],
    unreal_preview: str,
    approval_required: bool,
) -> Dict[str, Any]:
    runtime_row = row_index.get("%s:%s" % (plan["variantId"], rule_id), {})
    return {
        "id": "%s:%s" % (plan["variantId"], action),
        "assetId": plan.get("assetId"),
        "assetLabel": plan.get("assetLabel"),
        "platform": plan.get("platform"),
        "action": action,
        "ruleId": rule_id,
        "status": status,
        "reason": reason,
        "runtimeEvidence": runtime_row.get("evidence"),
        "sourceRuntimeStatus": runtime_row.get("status"),
        "preview": "None" if status == "Satisfied" else preview,
        "ownerApproval": plan.get("ownerApproval"),
        "approvalRequired": bool(approval_required),
        "mutationScope": "dry_run_plan_only",
        "targetEnginePath": plan.get("targetEnginePath"),
        "deterministicParams": params,
        "unrealPythonPreview": unreal_preview,
        "transactionPolicy": {
            "preflightFingerprint": "required",
            "writeSet": [plan.get("targetEnginePath")] if status in ("Ready", "Review") else [],
            "rollback": "restore asset from preflight duplicate or source control checkout",
            "productionWrite": False,
        },
    }


def _row_index(rows: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(row.get("id")): row for row in rows}


def _row_status(plan: Dict[str, Any], row_index: Dict[str, Dict[str, Any]], rule_id: str) -> str:
    return str(row_index.get("%s:%s" % (plan["variantId"], rule_id), {}).get("status", ""))


def _dedupe_operations(operations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: Dict[str, Dict[str, Any]] = {}
    severity = {"Blocked": 4, "Review": 3, "Ready": 2, "Satisfied": 1}
    for operation in operations:
        key = "%s:%s:%s" % (operation["assetId"], operation["platform"], operation["action"])
        existing = rows.get(key)
        if not existing or severity[operation["status"]] > severity[existing["status"]]:
            rows[key] = operation
    return sorted(rows.values(), key=lambda row: (row["assetId"], row["platform"], row["action"]))


def _summarize(operations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(operations)
    blocked = [row for row in rows if row["status"] == "Blocked"]
    review = [row for row in rows if row["status"] == "Review"]
    ready = [row for row in rows if row["status"] == "Ready"]
    satisfied = [row for row in rows if row["status"] == "Satisfied"]
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "operationCount": len(rows),
        "readyOperations": len(ready),
        "reviewOperations": len(review),
        "blockedOperations": len(blocked),
        "satisfiedOperations": len(satisfied),
        "variantCount": len({"%s:%s" % (row["assetId"], row["platform"]) for row in rows}),
        "executorReadyOperations": len(ready),
        "ownerApprovalRequired": sum(1 for row in rows if row.get("approvalRequired")),
        "operationTypes": sorted({row["action"] for row in rows}),
    }


def _executor_contract(summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": "platform-variant-generation-executor-contract@0.1.0",
        "mode": "dry-run",
        "canExecuteWithoutHuman": summary.get("blockedOperations") == 0 and summary.get("reviewOperations") == 0,
        "requiredRuntime": "Unreal Python",
        "expectedBoundary": "/Game/AI_Tool_TA public fixture or user-approved project scope",
        "blockedUntil": [
            "source and target assets exist",
            "geometry facts are readable for destructive LOD generation",
            "texture facts are collected before texture bake execution",
            "owner approval exists for visual or gameplay-affecting changes",
        ],
    }


def _screen_size_policy(platform: str, lod_count: int) -> List[float]:
    if lod_count <= 0:
        return []
    if platform == "mobile":
        defaults = [1.0, 0.45, 0.18, 0.06]
    else:
        defaults = [1.0, 0.55, 0.25, 0.1]
    return defaults[:lod_count]


def _reduction_policy(platform: str, missing: Iterable[str]) -> Dict[str, Any]:
    missing_rows = list(missing)
    target = 0.35 if platform == "mobile" else 0.55
    return {
        "method": "percent_triangles",
        "targetPercentByMissingLod": {lod: max(0.08, target / (index + 1)) for index, lod in enumerate(missing_rows)},
        "recomputeNormals": True,
        "preserveUVs": True,
        "preserveVertexColors": True,
    }


def _exists(fact: Dict[str, Any]) -> bool:
    return bool(fact.get("exists"))


def _int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0
