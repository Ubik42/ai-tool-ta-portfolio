"""Build approval and rollback receipts for platform variant executor expansion."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path, resolve_public_path


REPORT_VERSION = "platform-variant-executor-expansion@0.1.0"
EXECUTOR_ACTIONS = {
    "apply-runtime-nanite-policy",
    "disable-nanite",
    "generate-lod2",
    "generate-missing-runtime-lods",
    "repair-runtime-collision-policy",
    "simplify-collision",
}


def build_executor_expansion_report(
    generation_plan_path: str | Path,
    controlled_executor_path: str | Path,
) -> Dict[str, Any]:
    generation_path = resolve_public_path(generation_plan_path)
    executor_path = resolve_public_path(controlled_executor_path)
    generation_report = json.loads(generation_path.read_text(encoding="utf-8"))
    executor_report = json.loads(executor_path.read_text(encoding="utf-8"))
    source_operations = [
        operation
        for operation in generation_report.get("operations", [])
        if operation.get("action") in EXECUTOR_ACTIONS or str(operation.get("ruleId", "")).startswith("runtime-lod")
    ]
    receipts = [_receipt(operation, executor_report) for operation in source_operations]
    summary = _summarize(receipts)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-derived",
        "l3Status": "executor_receipts_linked_to_rolled_back_unreal_write",
        "sourceGenerationPlan": {
            "path": public_path(generation_path),
            "reportVersion": generation_report.get("reportVersion"),
            "evidenceLevel": generation_report.get("evidenceLevel"),
            "l3Status": generation_report.get("l3Status"),
            "gate": generation_report.get("summary", {}).get("gate"),
        },
        "sourceControlledExecutor": {
            "path": public_path(executor_path),
            "reportVersion": executor_report.get("reportVersion"),
            "evidenceLevel": executor_report.get("evidenceLevel"),
            "l3Status": executor_report.get("l3Status"),
            "gate": executor_report.get("evaluation", {}).get("summary", {}).get("gate"),
            "postCheckPassed": executor_report.get("evaluation", {}).get("summary", {}).get("postCheckPassed"),
            "rollbackPassed": executor_report.get("evaluation", {}).get("summary", {}).get("rollbackPassed"),
            "persistentMutation": executor_report.get("evaluation", {}).get("summary", {}).get("persistentMutation"),
        },
        "summary": summary,
        "receipts": receipts,
        "adapter": {
            "id": "platform-variant-executor-expansion",
            "name": "Platform Variant Executor Expansion Receipts",
            "methodSource": "R30 generation operations + R33 rolled-back Unreal executor proof",
            "protocolCarrier": "operation contract, owner approval receipt, rollback receipt",
            "boundary": {
                "mutation": "approval_receipts_only",
                "engineWrites": 0,
                "assetWrites": 0,
                "productionWrites": 0,
                "writeScope": "/Game/AI_Tool_TA public fixture or owner-approved project scope",
            },
        },
        "reviewerClaims": [
            "R34 separates safe executor candidates from LOD, Nanite and collision operations that need owner approval.",
            "Every candidate carries deterministic parameters, expected writeSet, approval receipt and rollback receipt.",
            "The receipts are linked to the R33 Unreal write/post-check/rollback proof instead of being free-floating plans.",
            "R34 does not mutate Unreal assets; it prepares the next controlled executor surface.",
        ],
    }


def _receipt(operation: Dict[str, Any], executor_report: Dict[str, Any]) -> Dict[str, Any]:
    category = _category(operation)
    readiness = _readiness(operation, category)
    approval_required = bool(operation.get("approvalRequired"))
    write_set = list(operation.get("transactionPolicy", {}).get("writeSet", []))
    return {
        "id": "executor-expansion:%s" % operation.get("id"),
        "sourceOperationId": operation.get("id"),
        "assetId": operation.get("assetId"),
        "assetLabel": operation.get("assetLabel"),
        "platform": operation.get("platform"),
        "category": category,
        "action": operation.get("action"),
        "sourceStatus": operation.get("status"),
        "receiptStatus": readiness["status"],
        "reason": readiness["reason"],
        "deterministicParams": operation.get("deterministicParams", {}),
        "unrealPythonPreview": operation.get("unrealPythonPreview"),
        "approvalReceipt": {
            "required": approval_required,
            "owner": operation.get("ownerApproval") if approval_required else None,
            "reason": _approval_reason(operation, category) if approval_required else "No owner approval required.",
            "allowedWithoutOwner": not approval_required and operation.get("status") == "Satisfied",
            "publicDemoDecision": "preview-only" if approval_required else "no-op-verified",
        },
        "rollbackReceipt": {
            "requiredBeforeExecution": bool(write_set),
            "preflightFingerprint": operation.get("transactionPolicy", {}).get("preflightFingerprint", "required"),
            "writeSet": write_set,
            "rollback": operation.get("transactionPolicy", {}).get("rollback"),
            "linkedExecutorL3Status": executor_report.get("l3Status"),
            "linkedExecutorRollbackPassed": executor_report.get("evaluation", {}).get("summary", {}).get("rollbackPassed"),
        },
        "riskControls": _risk_controls(operation, category, readiness["status"]),
    }


def _category(operation: Dict[str, Any]) -> str:
    action = str(operation.get("action", ""))
    rule_id = str(operation.get("ruleId", ""))
    if "lod" in action or "lod" in rule_id:
        return "lod"
    if "nanite" in action or "nanite" in rule_id:
        return "nanite"
    if "collision" in action or "collision" in rule_id:
        return "collision"
    return "other"


def _readiness(operation: Dict[str, Any], category: str) -> Dict[str, str]:
    status = operation.get("status")
    if status == "Blocked":
        return {"status": "Blocked", "reason": operation.get("reason", "Operation is blocked.")}
    if status == "Satisfied":
        return {"status": "NoOpVerified", "reason": operation.get("reason", "Runtime already satisfies policy.")}
    if category == "lod" and status == "Review":
        return {
            "status": "ReadinessOnly",
            "reason": "LOD generation needs readable geometry facts and owner approval before execution.",
        }
    if operation.get("approvalRequired"):
        return {
            "status": "ApprovalReady",
            "reason": "Operation has deterministic params and rollback policy, but requires owner approval.",
        }
    return {"status": "ExecutorReady", "reason": "Operation can enter a public-scope controlled executor."}


def _approval_reason(operation: Dict[str, Any], category: str) -> str:
    if category == "lod":
        return "LOD reduction can change silhouette, normal quality and gameplay readability."
    if category == "nanite":
        return "Nanite policy changes platform rendering behavior and memory/runtime tradeoffs."
    if category == "collision":
        return "Collision simplification can change gameplay contact and navigation behavior."
    return str(operation.get("reason") or "Operation changes shipped runtime assets.")


def _risk_controls(operation: Dict[str, Any], category: str, receipt_status: str) -> List[str]:
    controls = [
        "Capture preflight fingerprint before any write.",
        "Limit writeSet to declared public fixture or owner-approved project scope.",
        "Rollback from source control checkout or preflight duplicate.",
    ]
    if category == "lod":
        controls.append("Require geometry fact readability and visual silhouette review before execution.")
    if category == "nanite":
        controls.append("Compare platform preset policy and runtime Nanite flag after execution.")
    if category == "collision":
        controls.append("Compare simple shape count and complex-as-simple state after execution.")
    if receipt_status in ("ReadinessOnly", "ApprovalReady"):
        controls.append("Hold execution until owner approval receipt is attached.")
    if operation.get("status") == "Satisfied":
        controls.append("Keep as no-op proof; no executor write should be scheduled.")
    return controls


def _summarize(receipts: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(receipts)
    counts = {status: sum(1 for row in rows if row.get("receiptStatus") == status) for status in _statuses(rows)}
    blocked = counts.get("Blocked", 0)
    review = counts.get("ReadinessOnly", 0) + counts.get("ApprovalReady", 0)
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "receiptCount": len(rows),
        "categories": sorted({row.get("category") for row in rows}),
        "noOpVerified": counts.get("NoOpVerified", 0),
        "executorReady": counts.get("ExecutorReady", 0),
        "approvalReady": counts.get("ApprovalReady", 0),
        "readinessOnly": counts.get("ReadinessOnly", 0),
        "blocked": blocked,
        "ownerApprovalsRequired": sum(1 for row in rows if row.get("approvalReceipt", {}).get("required")),
        "rollbackReceiptsRequired": sum(1 for row in rows if row.get("rollbackReceipt", {}).get("requiredBeforeExecution")),
        "productionWrites": 0,
    }


def _statuses(rows: Iterable[Dict[str, Any]]) -> List[str]:
    return sorted({str(row.get("receiptStatus")) for row in rows} | {"NoOpVerified", "ExecutorReady", "ApprovalReady", "ReadinessOnly", "Blocked"})
