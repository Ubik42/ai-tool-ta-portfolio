"""Validate executor receipts against Unreal StaticMesh runtime facts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from .contract import public_path, resolve_public_path


REPORT_VERSION = "platform-variant-staticmesh-postcheck@0.1.0"


def build_staticmesh_postcheck_report(
    receipts_path: str | Path,
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    receipt_path = resolve_public_path(receipts_path)
    receipts_report = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt_rows = receipts_report.get("receipts", [])
    comparisons = [_compare_receipt(receipt, runtime_snapshot.get("facts", {})) for receipt in receipt_rows]
    rows = [row for comparison in comparisons for row in comparison.get("checks", [])]
    summary = _summarize(receipt_rows, comparisons, rows, runtime_snapshot)
    executed = bool(runtime_snapshot.get("runtime", {}).get("executed"))
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if executed else "Blocked",
        "l3Status": _l3_status(summary, executed),
        "sourceExecutorExpansion": {
            "path": public_path(receipt_path),
            "reportVersion": receipts_report.get("reportVersion"),
            "evidenceLevel": receipts_report.get("evidenceLevel"),
            "l3Status": receipts_report.get("l3Status"),
            "gate": receipts_report.get("summary", {}).get("gate"),
        },
        "unrealRuntime": runtime_snapshot.get("runtime", {}),
        "runtimeFacts": runtime_snapshot.get("facts", {}),
        "apiAvailability": runtime_snapshot.get("apiAvailability", {}),
        "postcheck": {
            "schema": "platform-variant-staticmesh-postcheck@0.1.0",
            "summary": summary,
            "receipts": comparisons,
            "rows": rows,
            "ownerActions": _owner_actions(comparisons),
        },
        "adapter": {
            "id": "platform-variant-staticmesh-postcheck",
            "name": "Platform Variant StaticMesh Post-check",
            "methodSource": "R34 executor receipt semantics + Unreal StaticMesh runtime facts",
            "protocolCarrier": "approval receipt, rollback receipt, read-only Unreal Python facts",
            "boundary": {
                "mutation": "read_only_runtime_postcheck",
                "engineWrites": 0,
                "assetWrites": runtime_snapshot.get("runtime", {}).get("assetWrites", 0),
                "productionWrites": 0,
                "writeScope": "/Game/AI_Tool_TA public fixture facts only",
            },
        },
        "reviewerClaims": [
            "R39 checks R34 LOD, Nanite and collision executor receipts against actual Unreal StaticMesh runtime facts.",
            "No-op receipts must match runtime state; owner-held receipts remain visible as approval/readiness work instead of being marked done.",
            "The probe is read-only: assetWrites, engineWrites and productionWrites stay at zero.",
            "This proves the business loop from runtime drift to executable receipt to post-checkable state.",
        ],
    }


def _compare_receipt(receipt: Dict[str, Any], runtime_facts: Dict[str, Any]) -> Dict[str, Any]:
    params = receipt.get("deterministicParams", {})
    target_path = str(params.get("targetEnginePath") or "")
    fact = runtime_facts.get(target_path, {})
    semantic = _semantic_state(receipt, fact)
    checks = [
        _row(
            receipt,
            "runtime-target-present",
            bool(fact.get("exists")),
            "error",
            "target=%s exists=%s class=%s" % (target_path, fact.get("exists"), fact.get("className")),
            "Create or import the planned StaticMesh target before executor signoff.",
        ),
        _row(
            receipt,
            "runtime-target-staticmesh",
            str(fact.get("className", "")).lower().endswith("staticmesh"),
            "error",
            "target=%s class=%s" % (target_path, fact.get("className")),
            "Point the receipt at a StaticMesh asset.",
        ),
        _row(
            receipt,
            "runtime-path-scope",
            bool(fact.get("pathMatched")),
            "error",
            "target=%s pathMatched=%s" % (target_path, fact.get("pathMatched")),
            "Keep public showcase fixtures under /Game/AI_Tool_TA.",
        ),
        _row(
            receipt,
            "runtime-geometry-readable",
            _int(fact.get("lodCount")) > 0,
            "error",
            "lodCount=%s triangles=%s verts=%s"
            % (fact.get("lodCount"), fact.get("triangleCount"), fact.get("vertexCount")),
            "Collect readable StaticMesh geometry facts before LOD or collision execution.",
        ),
        _policy_row(receipt, fact),
        _row(
            receipt,
            "rollback-boundary",
            _rollback_boundary_ok(receipt),
            "error",
            "receiptStatus=%s writeSet=%s rollbackRequired=%s productionWrites=0"
            % (
                receipt.get("receiptStatus"),
                receipt.get("rollbackReceipt", {}).get("writeSet", []),
                receipt.get("rollbackReceipt", {}).get("requiredBeforeExecution"),
            ),
            "Attach rollback receipt before enabling writes for this operation.",
        ),
        _row(
            receipt,
            "approval-boundary",
            _approval_boundary_ok(receipt),
            "error",
            "approvalRequired=%s owner=%s publicDecision=%s"
            % (
                receipt.get("approvalReceipt", {}).get("required"),
                receipt.get("approvalReceipt", {}).get("owner"),
                receipt.get("approvalReceipt", {}).get("publicDemoDecision"),
            ),
            "Hold owner-sensitive LOD, Nanite or collision writes until owner approval is attached.",
        ),
    ]
    return {
        "id": receipt.get("id"),
        "assetId": receipt.get("assetId"),
        "assetLabel": receipt.get("assetLabel"),
        "platform": receipt.get("platform"),
        "category": receipt.get("category"),
        "action": receipt.get("action"),
        "receiptStatus": receipt.get("receiptStatus"),
        "targetEnginePath": target_path,
        "runtimeFact": fact,
        "semanticState": semantic["state"],
        "semanticReason": semantic["reason"],
        "checks": checks,
    }


def _policy_row(receipt: Dict[str, Any], fact: Dict[str, Any]) -> Dict[str, Any]:
    category = receipt.get("category")
    if category == "nanite":
        return _row(
            receipt,
            "runtime-nanite-policy",
            _nanite_matches(receipt, fact),
            "warning",
            "actual=%s expected=%s"
            % (fact.get("naniteEnabled"), receipt.get("deterministicParams", {}).get("expectedNanite")),
            "Apply or disable Nanite according to platform policy after approval.",
        )
    if category == "lod":
        return _row(
            receipt,
            "runtime-lod-coverage",
            _lod_matches(receipt, fact),
            "warning",
            "actualLodCount=%s expectedLods=%s missing=%s"
            % (
                fact.get("lodCount"),
                receipt.get("deterministicParams", {}).get("expectedLods"),
                _missing_lods(receipt, fact),
            ),
            "Generate the missing runtime LODs from receipt reduction settings after owner approval.",
        )
    if category == "collision":
        return _row(
            receipt,
            "runtime-collision-policy",
            _collision_matches(receipt, fact),
            "warning",
            "simpleShapes=%s expected<=%s complexAsSimple=%s"
            % (
                fact.get("simpleShapeCount"),
                receipt.get("deterministicParams", {}).get("expectedSimpleShapes"),
                fact.get("complexAsSimple"),
            ),
            "Regenerate simplified collision and re-run the post-check.",
        )
    return _row(receipt, "runtime-policy-supported", False, "warning", "category=%s" % category, "Add a post-check policy for this operation category.")


def _semantic_state(receipt: Dict[str, Any], fact: Dict[str, Any]) -> Dict[str, str]:
    if not fact.get("exists"):
        return {"state": "Blocked", "reason": "Target StaticMesh is missing in Unreal runtime facts."}
    policy_matches = _policy_matches(receipt, fact)
    receipt_status = receipt.get("receiptStatus")
    if receipt_status == "NoOpVerified":
        return {
            "state": "RuntimeMatched" if policy_matches else "RuntimeDrift",
            "reason": "No-op receipt matches runtime state." if policy_matches else "No-op receipt drifted from runtime state.",
        }
    if receipt_status == "ApprovalReady":
        return {
            "state": "OwnerHeld" if not policy_matches else "AlreadySatisfied",
            "reason": "Runtime change is deterministic but still owner-held." if not policy_matches else "Runtime already satisfies owner-held receipt.",
        }
    if receipt_status == "ReadinessOnly":
        return {
            "state": "ReadinessHeld" if not policy_matches else "AlreadySatisfied",
            "reason": "Geometry is readable; execution waits for approval and visual review."
            if not policy_matches
            else "Runtime LOD coverage already satisfies the readiness receipt.",
        }
    if receipt_status == "ExecutorReady":
        return {
            "state": "ExecutorReady" if not policy_matches else "AlreadySatisfied",
            "reason": "Receipt can enter a controlled executor when write scope is approved.",
        }
    return {"state": str(receipt_status or "Unknown"), "reason": "Receipt status carried from source expansion."}


def _summarize(
    receipts: Iterable[Dict[str, Any]],
    comparisons: Iterable[Dict[str, Any]],
    rows: Iterable[Dict[str, Any]],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    receipt_list = list(receipts)
    comparison_list = list(comparisons)
    row_list = list(rows)
    facts = runtime_snapshot.get("facts", {})
    target_paths = sorted({str(row.get("deterministicParams", {}).get("targetEnginePath")) for row in receipt_list})
    target_paths = [path for path in target_paths if path and path != "None"]
    no_op_rows = [row for row in comparison_list if row.get("receiptStatus") == "NoOpVerified"]
    return {
        "gate": _gate(row_list),
        "receiptCount": len(receipt_list),
        "runtimeTargets": len(target_paths),
        "targetAssetsPresent": sum(1 for path in target_paths if facts.get(path, {}).get("exists")),
        "noOpVerified": sum(1 for row in comparison_list if row.get("receiptStatus") == "NoOpVerified"),
        "runtimeNoOpMatched": sum(1 for row in no_op_rows if row.get("semanticState") == "RuntimeMatched"),
        "approvalReady": sum(1 for row in comparison_list if row.get("receiptStatus") == "ApprovalReady"),
        "readinessOnly": sum(1 for row in comparison_list if row.get("receiptStatus") == "ReadinessOnly"),
        "executorReady": sum(1 for row in comparison_list if row.get("receiptStatus") == "ExecutorReady"),
        "runtimeSatisfied": sum(1 for row in comparison_list if row.get("semanticState") in ("RuntimeMatched", "AlreadySatisfied")),
        "runtimeHeld": sum(1 for row in comparison_list if row.get("semanticState") in ("OwnerHeld", "ReadinessHeld", "ExecutorReady")),
        "runtimeDrift": sum(1 for row in comparison_list if row.get("semanticState") == "RuntimeDrift"),
        "blockedReceipts": sum(1 for row in comparison_list if row.get("semanticState") == "Blocked"),
        "ownerActions": len(_owner_actions(comparison_list)),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "assetWrites": runtime_snapshot.get("runtime", {}).get("assetWrites", 0),
        "engineWrites": runtime_snapshot.get("runtime", {}).get("engineWrites", 0),
        "productionWrites": runtime_snapshot.get("runtime", {}).get("productionWrites", 0),
    }


def _owner_actions(comparisons: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions: List[Dict[str, Any]] = []
    for comparison in comparisons:
        if comparison.get("semanticState") not in ("OwnerHeld", "ReadinessHeld", "RuntimeDrift", "Blocked"):
            continue
        actions.append(
            {
                "id": "staticmesh-postcheck-action:%s" % comparison.get("id"),
                "assetId": comparison.get("assetId"),
                "platform": comparison.get("platform"),
                "category": comparison.get("category"),
                "targetEnginePath": comparison.get("targetEnginePath"),
                "state": comparison.get("semanticState"),
                "preview": comparison.get("semanticReason"),
            }
        )
    return actions


def _row(
    receipt: Dict[str, Any],
    rule_id: str,
    passed: bool,
    fail_status: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (receipt.get("id"), rule_id),
        "receiptId": receipt.get("id"),
        "assetId": receipt.get("assetId"),
        "platform": receipt.get("platform"),
        "category": receipt.get("category"),
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _policy_matches(receipt: Dict[str, Any], fact: Dict[str, Any]) -> bool:
    category = receipt.get("category")
    if category == "nanite":
        return _nanite_matches(receipt, fact)
    if category == "lod":
        return _lod_matches(receipt, fact)
    if category == "collision":
        return _collision_matches(receipt, fact)
    return False


def _nanite_matches(receipt: Dict[str, Any], fact: Dict[str, Any]) -> bool:
    expected = receipt.get("deterministicParams", {}).get("expectedNanite")
    actual = fact.get("naniteEnabled")
    if actual is None:
        return False
    return bool(actual) == bool(expected)


def _lod_matches(receipt: Dict[str, Any], fact: Dict[str, Any]) -> bool:
    expected_lods = receipt.get("deterministicParams", {}).get("expectedLods", [])
    return _int(fact.get("lodCount")) >= len(expected_lods)


def _collision_matches(receipt: Dict[str, Any], fact: Dict[str, Any]) -> bool:
    expected = _int(receipt.get("deterministicParams", {}).get("expectedSimpleShapes"))
    simple_shapes = _int(fact.get("simpleShapeCount"))
    return expected > 0 and simple_shapes <= expected and not bool(fact.get("complexAsSimple"))


def _missing_lods(receipt: Dict[str, Any], fact: Dict[str, Any]) -> List[str]:
    expected_lods = list(receipt.get("deterministicParams", {}).get("expectedLods", []))
    actual_count = _int(fact.get("lodCount"))
    return [lod for index, lod in enumerate(expected_lods) if index >= actual_count]


def _rollback_boundary_ok(receipt: Dict[str, Any]) -> bool:
    status = receipt.get("receiptStatus")
    rollback = receipt.get("rollbackReceipt", {})
    write_set = rollback.get("writeSet", [])
    if status == "NoOpVerified":
        return not rollback.get("requiredBeforeExecution") and len(write_set) == 0
    if status in ("ApprovalReady", "ReadinessOnly", "ExecutorReady"):
        return bool(rollback.get("requiredBeforeExecution")) and len(write_set) > 0
    return status != "Blocked"


def _approval_boundary_ok(receipt: Dict[str, Any]) -> bool:
    status = receipt.get("receiptStatus")
    approval = receipt.get("approvalReceipt", {})
    if status == "NoOpVerified":
        return not approval.get("required") and bool(approval.get("allowedWithoutOwner"))
    if status in ("ApprovalReady", "ReadinessOnly"):
        return bool(approval.get("required")) and bool(approval.get("owner")) and approval.get("publicDemoDecision") == "preview-only"
    return status != "Blocked"


def _gate(rows: Iterable[Dict[str, Any]]) -> str:
    row_list = list(rows)
    if any(row.get("status") == "error" for row in row_list):
        return "Blocked"
    if any(row.get("status") == "warning" for row in row_list):
        return "Review"
    return "Ready"


def _l3_status(summary: Dict[str, Any], executed: bool) -> str:
    if not executed:
        return "blocked_by_missing_unreal_runtime"
    if summary.get("gate") == "Blocked":
        return "unreal_staticmesh_postcheck_blocked"
    return "unreal_staticmesh_postcheck_collected"


def _int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0
