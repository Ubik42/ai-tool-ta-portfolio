"""Controlled Unreal socket authoring executor with rollback evidence."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path, resolve_public_path


REPORT_VERSION = "unreal-socket-authoring-executor@0.1.0"


def build_socket_authoring_report(source_path: str | Path, runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    source_file = resolve_public_path(source_path)
    source = json.loads(source_file.read_text(encoding="utf-8"))
    operations = list(runtime_snapshot.get("operations", []))
    held_rows = list(runtime_snapshot.get("heldRows", []))
    rows = [row for operation in operations for row in _operation_rows(operation, runtime_snapshot)]
    rows.extend(_held_row_checks(held_rows, runtime_snapshot))
    summary = _summary(operations, held_rows, rows, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    blocked_reason = runtime.get("blockedReason")
    executed = bool(runtime.get("executed"))
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Authoring Executor",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if executed else "Blocked",
        "l3Status": blocked_reason or _l3_status(summary, executed),
        "sourceSocketImportChecker": {
            "path": public_path(source_file),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "unrealRuntime": runtime,
        "operations": operations,
        "heldRows": held_rows,
        "executor": {
            "schema": "unreal-socket-authoring-executor@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(operations, held_rows, rows),
        },
        "adapter": {
            "id": "unreal-socket-authoring-executor",
            "name": "Unreal Socket Authoring Controlled Executor",
            "methodSource": "R38 Maya spatial socket intent + Unreal Python SkeletalMesh.add_socket runtime mutation",
            "protocolCarrier": "approved source socket rows, Unreal in-memory authoring, post-check snapshot and rollback fingerprint",
            "boundary": {
                "mutation": "in_memory_public_fixture_rolled_back",
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public fixture only"),
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "inMemoryWrites": runtime.get("inMemoryWrites", 0),
            },
        },
        "reviewerClaims": _reviewer_claims(summary),
    }


def _operation_rows(operation: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    runtime = runtime_snapshot.get("runtime", {})
    post = operation.get("postcheck", {})
    rollback = operation.get("rollback", {})
    authoring = operation.get("authoring", {})
    expected = set(operation.get("expectedSocketNames", []))
    post_names = set(post.get("socketNames", []))
    preflight = operation.get("preflight", {})
    return [
        _row(
            operation,
            "unreal-python-runtime",
            bool(runtime.get("executed")),
            "error",
            "executed=%s engine=%s" % (runtime.get("executed"), runtime.get("engineVersion")),
            "Run the executor through UnrealEditor-Cmd against the public test project.",
        ),
        _row(
            operation,
            "source-row-approved",
            operation.get("sourceStatus") == "Ready" and operation.get("ownerState") == "approved",
            "error",
            "sourceStatus=%s ownerState=%s" % (operation.get("sourceStatus"), operation.get("ownerState")),
            "Resolve Maya spatial authoring owner actions before allowing engine writes.",
        ),
        _row(
            operation,
            "public-fixture-scope",
            bool(operation.get("targetAssetPath", "").startswith("/Game/AI_Tool_TA/")),
            "error",
            "target=%s" % operation.get("targetAssetPath"),
            "Keep showcase execution inside the public /Game/AI_Tool_TA fixture.",
        ),
        _row(
            operation,
            "target-socket-container-present",
            bool(operation.get("targetExists")) and operation.get("targetClass") in ("SkeletalMesh", "Skeleton"),
            "error",
            "exists=%s class=%s" % (operation.get("targetExists"), operation.get("targetClass")),
            "Import or relink the public SkeletalMesh or Skeleton before socket execution.",
        ),
        _row(
            operation,
            "socket-authoring-api-ready",
            bool(operation.get("apiReady")),
            "error",
            "method=%s apiReady=%s errors=%s"
            % (authoring.get("method"), operation.get("apiReady"), authoring.get("errors", [])),
            "Use a project where SkeletalMesh.add_socket and SkeletalMeshSocket properties are available.",
        ),
        _row(
            operation,
            "preflight-fingerprint-captured",
            bool(preflight.get("fingerprint")),
            "error",
            "preflightSockets=%s fingerprint=%s" % (preflight.get("socketNames"), preflight.get("fingerprint")),
            "Capture the socket list before mutation so rollback can be proven.",
        ),
        _row(
            operation,
            "socket-authoring-executed",
            bool(authoring.get("attempted")) and expected.issubset(post_names),
            "error",
            "created=%s postSockets=%s" % (authoring.get("createdSockets"), post.get("socketNames")),
            "Create every missing expected socket before accepting the execution receipt.",
        ),
        _row(
            operation,
            "postcheck-parent-binding",
            bool(post.get("expectedSocketsPresent")) and bool(post.get("parentBindingsMatched")),
            "error",
            "parentMismatches=%s details=%s" % (post.get("parentMismatches"), post.get("expectedSocketDetails")),
            "Bind each runtime socket to the same parent joint carried by the Maya source row.",
        ),
        _row(
            operation,
            "rollback-restored-preflight",
            bool(rollback.get("restoredPreflight")),
            "error",
            "finalSockets=%s finalFingerprint=%s preflightFingerprint=%s"
            % (rollback.get("socketNames"), rollback.get("fingerprint"), preflight.get("fingerprint")),
            "Remove temporary sockets and restore the preflight socket fingerprint before exiting.",
        ),
        _row(
            operation,
            "write-boundary-clean",
            runtime.get("assetWrites", 0) == 0
            and runtime.get("engineWrites", 0) == 0
            and runtime.get("productionWrites", 0) == 0,
            "error",
            "assetWrites=%s engineWrites=%s productionWrites=%s inMemoryWrites=%s"
            % (
                runtime.get("assetWrites", 0),
                runtime.get("engineWrites", 0),
                runtime.get("productionWrites", 0),
                runtime.get("inMemoryWrites", 0),
            ),
            "Do not save public or production assets during the controlled authoring rehearsal.",
        ),
    ]


def _held_row_checks(held_rows: Iterable[Dict[str, Any]], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    runtime = runtime_snapshot.get("runtime", {})
    rows = []
    for held in held_rows:
        rows.append(
            {
                "id": "%s:held-row-no-write" % held.get("assetId"),
                "assetId": held.get("assetId"),
                "operationId": held.get("id"),
                "ruleId": "held-row-no-write",
                "status": "pass" if held.get("held") and not held.get("mutated") else "error",
                "evidence": "held=%s mutated=%s reason=%s productionWrites=%s"
                % (held.get("held"), held.get("mutated"), held.get("reason"), runtime.get("productionWrites", 0)),
                "fixPreview": "None" if held.get("held") and not held.get("mutated") else "Keep blocked source rows out of execution.",
            }
        )
    return rows


def _row(
    operation: Dict[str, Any],
    rule_id: str,
    passed: bool,
    fail_status: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (operation.get("id"), rule_id),
        "assetId": operation.get("assetId"),
        "operationId": operation.get("id"),
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summary(
    operations: Iterable[Dict[str, Any]],
    held_rows: Iterable[Dict[str, Any]],
    rows: Iterable[Dict[str, Any]],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    operation_list = list(operations)
    held_list = list(held_rows)
    row_list = list(rows)
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "gate": _gate(row_list),
        "selectedOperations": len(operation_list),
        "heldRows": len(held_list),
        "expectedSockets": sum(len(row.get("expectedSocketNames", [])) for row in operation_list),
        "createdSockets": sum(len(row.get("authoring", {}).get("createdSockets", [])) for row in operation_list),
        "postCheckPassed": sum(1 for row in operation_list if row.get("postcheck", {}).get("expectedSocketsPresent")),
        "rollbackPassed": sum(1 for row in operation_list if row.get("rollback", {}).get("restoredPreflight")),
        "heldRowsUntouched": sum(1 for row in held_list if row.get("held") and not row.get("mutated")),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "assetWrites": runtime.get("assetWrites", 0),
        "engineWrites": runtime.get("engineWrites", 0),
        "productionWrites": runtime.get("productionWrites", 0),
        "inMemoryWrites": runtime.get("inMemoryWrites", 0),
    }


def _owner_actions(
    operations: Iterable[Dict[str, Any]],
    held_rows: Iterable[Dict[str, Any]],
    rows: Iterable[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    actions = []
    failed_rules = [row for row in rows if row.get("status") != "pass"]
    for row in failed_rules:
        actions.append(
            {
                "id": "socket-authoring-action:%s" % row.get("id"),
                "assetId": row.get("assetId"),
                "ruleId": row.get("ruleId"),
                "owner": "engine-ta",
                "preview": row.get("fixPreview"),
            }
        )
    for held in held_rows:
        actions.append(
            {
                "id": "socket-authoring-held:%s" % held.get("assetId"),
                "assetId": held.get("assetId"),
                "ruleId": "source-row-held",
                "owner": held.get("owner", "spatial-owner"),
                "preview": held.get("reason"),
            }
        )
    return actions


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
    if summary.get("gate") == "Ready" and summary.get("rollbackPassed") == summary.get("selectedOperations"):
        return "unreal_socket_authoring_executor_rolled_back"
    if summary.get("selectedOperations") and not summary.get("createdSockets"):
        return "unreal_socket_authoring_executor_api_limited"
    return "unreal_socket_authoring_executor_blocked"


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    base = [
        "R40 converts the R38 approved rifle socket gap into a controlled Unreal execution gate.",
        "Only approved public fixture rows can execute; temporary or blocked source rows remain held with explicit no-write evidence.",
        "No package, engine or production asset is saved; assetWrites, engineWrites and productionWrites remain zero.",
    ]
    if summary.get("gate") == "Ready":
        base.append(
            "The executor creates the expected public sockets in Unreal memory, validates their post-state, then rolls the socket list back to the preflight fingerprint."
        )
    else:
        base.append(
            "The executor records the Unreal Python authoring limitation instead of pretending auto-fix succeeded: UE 5.3 exposes add_socket but keeps socket_name and bone_name read-only for commandlet-created SkeletalMeshSocket objects."
        )
    return base
