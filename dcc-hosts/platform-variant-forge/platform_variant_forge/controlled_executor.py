"""Build controlled execution receipts for public platform variant fixtures."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path, resolve_public_path


REPORT_VERSION = "platform-variant-controlled-executor@0.1.0"


def build_controlled_executor_report(
    generation_plan_path: str | Path,
    texture_payload_path: str | Path,
    execution_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    generation_path = resolve_public_path(generation_plan_path)
    payload_path = resolve_public_path(texture_payload_path)
    generation_report = json.loads(generation_path.read_text(encoding="utf-8")) if generation_path.exists() else {}
    payload_report = json.loads(payload_path.read_text(encoding="utf-8")) if payload_path.exists() else {}
    selected = execution_snapshot.get("selectedOperation", {})
    source_generation_operation = _find_generation_operation(generation_report, selected.get("sourceGenerationOperationId"))
    rows = _evaluate_execution_rows(execution_snapshot)
    summary = _summarize(rows, execution_snapshot)
    executed = bool(execution_snapshot.get("runtime", {}).get("executed"))
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if executed else "Blocked",
        "l3Status": _l3_status(summary, executed),
        "sourceGenerationPlan": {
            "path": public_path(generation_path),
            "reportVersion": generation_report.get("reportVersion"),
            "evidenceLevel": generation_report.get("evidenceLevel"),
            "l3Status": generation_report.get("l3Status"),
            "gate": generation_report.get("summary", {}).get("gate"),
        },
        "sourceTexturePayload": {
            "path": public_path(payload_path),
            "reportVersion": payload_report.get("reportVersion"),
            "evidenceLevel": payload_report.get("evidenceLevel"),
            "l3Status": payload_report.get("l3Status"),
            "gate": payload_report.get("evaluation", {}).get("summary", {}).get("gate"),
            "readyVariants": payload_report.get("evaluation", {}).get("summary", {}).get("readyVariants"),
            "blockedVariants": payload_report.get("evaluation", {}).get("summary", {}).get("blockedVariants"),
        },
        "selectedOperation": {
            **selected,
            "sourceGenerationOperation": source_generation_operation,
        },
        "unrealRuntime": execution_snapshot.get("runtime", {}),
        "transaction": {
            "mode": execution_snapshot.get("mode", "execute_then_rollback"),
            "writeSet": execution_snapshot.get("writeSet", []),
            "rollbackActions": execution_snapshot.get("rollbackActions", []),
            "preflight": execution_snapshot.get("preflight", {}),
            "postExecution": execution_snapshot.get("postExecution", {}),
            "rollback": execution_snapshot.get("rollback", {}),
        },
        "evaluation": {
            "schema": "platform-variant-controlled-executor-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
        },
        "adapter": {
            "id": "platform-variant-controlled-executor",
            "name": "Platform Variant Controlled Executor",
            "methodSource": "Unreal public fixture execute/post-check/rollback receipt",
            "protocolCarrier": "R30 generation operation + R32 Texture2D payload facts + Unreal Python transaction",
            "boundary": {
                "mutation": "public_fixture_execute_then_rollback",
                "engineWrites": 0,
                "assetWrites": execution_snapshot.get("runtime", {}).get("assetWrites", 0),
                "productionWrites": 0,
                "writeScope": execution_snapshot.get("runtime", {}).get("writeScope", "/Game/AI_Tool_TA public fixture only"),
                "persistentMutation": summary.get("persistentMutation", False),
            },
        },
        "reviewerClaims": [
            "R33 executes a real Unreal Python property write only inside the public fixture scope.",
            "The executor records preflight, writeSet, post-check and rollback fingerprints instead of treating execution as a success string.",
            "The selected operation is tied back to R30 generation planning and R32 Texture2D payload facts.",
            "The final committed state is rolled back; production writes remain zero.",
        ],
    }


def _find_generation_operation(report: Dict[str, Any], operation_id: Any) -> Dict[str, Any]:
    if not operation_id:
        return {}
    for operation in report.get("operations", []):
        if operation.get("id") == operation_id:
            return operation
    return {}


def _evaluate_execution_rows(snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    runtime = snapshot.get("runtime", {})
    selected = snapshot.get("selectedOperation", {})
    preflight = snapshot.get("preflight", {})
    post = snapshot.get("postExecution", {})
    rollback = snapshot.get("rollback", {})
    write_set = snapshot.get("writeSet", [])
    target_value = selected.get("targetMaxTextureSize")
    previous_value = selected.get("previousMaxTextureSize")
    rows = [
        _row(
            "runtime-available",
            bool(runtime.get("executed")),
            "error",
            "Unreal runtime executed=%s engine=%s" % (runtime.get("executed"), runtime.get("engineVersion")),
            "Run through UnrealEditor-Cmd before claiming controlled execution.",
        ),
        _row(
            "public-scope",
            all(str(path).startswith("/Game/AI_Tool_TA/") for path in write_set),
            "error",
            "writeSet=%s" % write_set,
            "Restrict executor writes to a public fixture or explicitly approved project scope.",
        ),
        _row(
            "preflight-fingerprint",
            bool(preflight.get("exists")) and bool(preflight.get("fingerprint")),
            "error",
            "preflight=%s exists=%s" % (preflight.get("texturePath"), preflight.get("exists")),
            "Capture target asset state before mutation.",
        ),
        _row(
            "execute-write",
            bool(snapshot.get("operationApplied")) and post.get("maxTextureSize") == target_value,
            "error",
            "maxTextureSize before=%s after=%s expected=%s"
            % (previous_value, post.get("maxTextureSize"), target_value),
            "Apply the public texture max-size clamp through Unreal Python.",
        ),
        _row(
            "post-check",
            bool(post.get("fingerprint")) and post.get("fingerprint") != preflight.get("fingerprint"),
            "warning",
            "postFingerprint=%s preflightFingerprint=%s" % (post.get("fingerprint"), preflight.get("fingerprint")),
            "Verify the mutation changed the intended public fixture state.",
        ),
        _row(
            "rollback",
            bool(snapshot.get("rollbackApplied")) and rollback.get("fingerprint") == preflight.get("fingerprint"),
            "error",
            "rollbackFingerprint=%s preflightFingerprint=%s maxTextureSize=%s"
            % (rollback.get("fingerprint"), preflight.get("fingerprint"), rollback.get("maxTextureSize")),
            "Rollback must restore the preflight fingerprint.",
        ),
        _row(
            "production-boundary",
            _int(runtime.get("productionWrites")) == 0 and _int(runtime.get("engineWrites")) == 0,
            "error",
            "engineWrites=%s productionWrites=%s" % (runtime.get("engineWrites"), runtime.get("productionWrites")),
            "Do not mutate production assets in the public portfolio executor.",
        ),
    ]
    for error in snapshot.get("errors", []):
        rows.append(_row("runtime-error:%s" % len(rows), False, "error", str(error), "Fix Unreal executor error."))
    return rows


def _row(rule_id: str, passed: bool, fail_status: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "controlled-executor:%s" % rule_id,
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summarize(rows: Iterable[Dict[str, Any]], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    row_list = list(rows)
    errors = sum(1 for row in row_list if row["status"] == "error")
    warnings = sum(1 for row in row_list if row["status"] == "warning")
    preflight = snapshot.get("preflight", {})
    post = snapshot.get("postExecution", {})
    rollback = snapshot.get("rollback", {})
    preflight_fingerprint = preflight.get("fingerprint")
    post_fingerprint = post.get("fingerprint")
    rollback_fingerprint = rollback.get("fingerprint")
    post_check_passed = bool(post_fingerprint) and post_fingerprint != preflight_fingerprint
    rollback_passed = bool(snapshot.get("rollbackApplied")) and rollback_fingerprint == preflight_fingerprint
    persistent_mutation = bool(snapshot.get("operationApplied")) and not rollback_passed
    return {
        "gate": "Blocked" if errors else "Review" if warnings else "Ready",
        "rowCount": len(row_list),
        "pass": sum(1 for row in row_list if row["status"] == "pass"),
        "warning": warnings,
        "error": errors,
        "executedOperations": 1 if snapshot.get("operationApplied") else 0,
        "postCheckPassed": 1 if post_check_passed else 0,
        "rollbackPassed": 1 if rollback_passed else 0,
        "writeSetCount": len(snapshot.get("writeSet", [])),
        "assetWrites": snapshot.get("runtime", {}).get("assetWrites", 0),
        "persistentMutation": persistent_mutation,
    }


def _l3_status(summary: Dict[str, Any], executed: bool) -> str:
    if not executed:
        return "blocked_by_missing_unreal_runtime"
    if summary.get("gate") == "Ready":
        return "unreal_texture_budget_executor_rolled_back"
    return "unreal_texture_budget_executor_requires_review"


def _int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0
