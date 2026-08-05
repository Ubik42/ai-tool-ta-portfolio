"""Controlled Unreal Groom import executor.

This adapter is the write-capable layer after the R49 import/post-check and
R50 plugin/API fixture. It may write only under the public `/Game/AI_Tool_TA`
fixture scope, and it must record preflight, import attempt, binding attempt,
post-check and rollback evidence in one report.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path


REPORT_VERSION = "groom-controlled-executor@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_GAME_PREFIX = "/Game/AI_Tool_TA/"


def resolve_public_path(path: str | Path | None) -> Path:
    text = str(path or "")
    if text.startswith("<repo>\\"):
        return PORTFOLIO_ROOT / text.replace("<repo>\\", "", 1)
    if text.startswith("<repo>/"):
        return PORTFOLIO_ROOT / text.replace("<repo>/", "", 1)
    return Path(text)


def build_groom_controlled_executor_report(
    postcheck_path: str | Path,
    plugin_fixture_path: str | Path,
    execution_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    postcheck = _read_json(resolve_public_path(postcheck_path))
    plugin_fixture = _read_json(resolve_public_path(plugin_fixture_path))
    selected = execution_snapshot.get("selectedOperation", {})
    rows = _evaluate_execution_rows(postcheck, plugin_fixture, execution_snapshot)
    summary = _summarize(rows, execution_snapshot)
    runtime = execution_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if executed else "Blocked",
        "l3Status": _l3_status(summary, runtime),
        "sourceImportPostcheck": {
            "path": public_path(resolve_public_path(postcheck_path)),
            "reportVersion": postcheck.get("reportVersion"),
            "evidenceLevel": postcheck.get("evidenceLevel"),
            "l3Status": postcheck.get("l3Status"),
            "gate": postcheck.get("evaluation", {}).get("summary", {}).get("gate"),
            "cacheHashMatchedRows": postcheck.get("facts", {}).get("summary", {}).get("cacheHashMatchedRows"),
            "importCandidateRows": postcheck.get("facts", {}).get("summary", {}).get("importCandidateRows"),
        },
        "sourcePluginApiFixture": {
            "path": public_path(resolve_public_path(plugin_fixture_path)),
            "reportVersion": plugin_fixture.get("reportVersion"),
            "evidenceLevel": plugin_fixture.get("evidenceLevel"),
            "l3Status": plugin_fixture.get("l3Status"),
            "gate": plugin_fixture.get("evaluation", {}).get("summary", {}).get("gate"),
            "groomImportApiReady": plugin_fixture.get("facts", {}).get("summary", {}).get("groomImportApiReady"),
            "alembicImportFactoryVisible": plugin_fixture.get("facts", {}).get("summary", {}).get("alembicImportFactoryVisible"),
        },
        "selectedOperation": selected,
        "unrealRuntime": runtime,
        "transaction": {
            "mode": execution_snapshot.get("mode", "execute_then_rollback"),
            "preflight": execution_snapshot.get("preflight", {}),
            "importTask": execution_snapshot.get("importTask", {}),
            "bindingAttempt": execution_snapshot.get("bindingAttempt", {}),
            "postExecution": execution_snapshot.get("postExecution", {}),
            "rollback": execution_snapshot.get("rollback", {}),
            "writeSet": execution_snapshot.get("writeSet", []),
            "rollbackActions": execution_snapshot.get("rollbackActions", []),
            "errors": execution_snapshot.get("errors", []),
        },
        "facts": {
            "schema": "groom-controlled-executor-facts@0.1.0",
            "summary": summary,
            "selectedAssetId": selected.get("assetId"),
            "expectedGroomAsset": selected.get("expectedGroomAsset"),
            "expectedBindingAsset": selected.get("expectedBindingAsset"),
            "targetSkeletalMesh": selected.get("targetSkeletalMesh"),
            "sourceCache": selected.get("cache"),
        },
        "evaluation": {
            "schema": "groom-controlled-executor-evaluation@0.1.0",
            "summary": {
                "gate": summary.get("gate"),
                "checks": len(rows),
                "pass": summary.get("pass"),
                "warning": summary.get("warning"),
                "error": summary.get("error"),
            },
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "groom-controlled-executor",
            "name": "Groom Controlled Executor",
            "methodSource": "Unreal public fixture AssetImportTask + GroomLibrary binding attempt + rollback receipt",
            "protocolCarrier": "R48 Alembic cache sha256, R49 import candidate, R50 Groom API surface, Unreal post-check assets",
            "boundary": {
                "mutation": "public_fixture_execute_then_rollback",
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public fixture only"),
                "persistentMutation": summary.get("persistentMutation", False),
            },
        },
        "reviewerClaims": [
            "R51 moves Groom from plugin/API readiness into a controlled Unreal executor attempt.",
            "Only the approved public groom cache row may enter execution; TMP/blocked rows stay held.",
            "The report records import task properties, imported object paths, Groom binding method visibility, post-check assets and rollback residue.",
            "A blocked result is still useful: it exposes the exact Unreal Python or Alembic/Groom importer boundary without leaving persistent public fixture mutations.",
        ],
    }


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _evaluate_execution_rows(
    postcheck: Dict[str, Any],
    plugin_fixture: Dict[str, Any],
    snapshot: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime = snapshot.get("runtime", {})
    selected = snapshot.get("selectedOperation", {})
    preflight = snapshot.get("preflight", {})
    import_task = snapshot.get("importTask", {})
    binding = snapshot.get("bindingAttempt", {})
    post = snapshot.get("postExecution", {})
    rollback = snapshot.get("rollback", {})
    write_set = snapshot.get("writeSet", [])
    plugin_summary = plugin_fixture.get("facts", {}).get("summary", {})
    source_summary = postcheck.get("facts", {}).get("summary", {})
    rows = [
        _row(
            "runtime-available",
            bool(runtime.get("executed")),
            "error",
            "executed=%s engine=%s" % (runtime.get("executed"), runtime.get("engineVersion")),
            "Run through UnrealEditor-Cmd before claiming executor evidence.",
        ),
        _row(
            "source-cache-ready",
            bool(selected.get("selected")) and bool(selected.get("cache", {}).get("hashMatches")),
            "error",
            "selected=%s hashMatches=%s R49 candidates=%s"
            % (selected.get("selected"), selected.get("cache", {}).get("hashMatches"), source_summary.get("importCandidateRows")),
            "Use the approved R48/R49 cache row before executing import.",
        ),
        _row(
            "plugin-api-ready",
            bool(plugin_summary.get("groomImportApiReady")) and bool(plugin_summary.get("alembicImportFactoryVisible")),
            "error",
            "groomImportApiReady=%s alembicImportFactoryVisible=%s"
            % (plugin_summary.get("groomImportApiReady"), plugin_summary.get("alembicImportFactoryVisible")),
            "Run R50 plugin/API fixture and keep Groom/Alembic plugins enabled.",
        ),
        _row(
            "public-write-scope",
            bool(write_set) and all(str(path).startswith(PUBLIC_GAME_PREFIX) for path in write_set),
            "error",
            "writeSet=%s" % write_set,
            "Restrict Groom executor writes to /Game/AI_Tool_TA.",
        ),
        _row(
            "preflight-target-mesh",
            bool(preflight.get("targetSkeletalMesh", {}).get("exists")),
            "error",
            "target=%s exists=%s"
            % (selected.get("targetSkeletalMesh"), preflight.get("targetSkeletalMesh", {}).get("exists")),
            "Create or restore the public target SkeletalMesh fixture.",
        ),
        _row(
            "import-task-attempted",
            bool(import_task.get("attempted")),
            "error",
            "attempted=%s factory=%s" % (import_task.get("attempted"), import_task.get("factoryClass")),
            "Construct AssetImportTask and execute import_asset_tasks.",
        ),
        _row(
            "groom-import-created",
            bool(import_task.get("succeeded"))
            and bool(post.get("expectedGroomAsset", {}).get("exists"))
            and post.get("expectedGroomAsset", {}).get("className") == "GroomAsset",
            "error",
            "succeeded=%s imported=%s postGroom=%s class=%s errors=%s"
            % (
                import_task.get("succeeded"),
                import_task.get("importedObjectPaths"),
                post.get("expectedGroomAsset", {}).get("exists"),
                post.get("expectedGroomAsset", {}).get("className"),
                import_task.get("errors"),
            ),
            "Fix Groom/Alembic import settings or switch this step to an Editor Utility/C++ bridge.",
        ),
        _row(
            "binding-method-visible",
            bool(binding.get("methodVisible")),
            "warning",
            "method=%s visible=%s candidates=%s"
            % (binding.get("method"), binding.get("methodVisible"), binding.get("candidateMethods")),
            "Expose GroomLibrary.create_new_groom_binding_asset_with_path or use a bridge.",
        ),
        _row(
            "binding-created",
            bool(binding.get("succeeded")) and bool(post.get("expectedBindingAsset", {}).get("exists")),
            "error",
            "succeeded=%s postBinding=%s error=%s"
            % (binding.get("succeeded"), post.get("expectedBindingAsset", {}).get("exists"), binding.get("error")),
            "Create GroomBindingAsset after GroomAsset import and target mesh validation.",
        ),
        _row(
            "rollback-clean",
            bool(rollback.get("passed")) and int(rollback.get("residualAssetCount") or 0) == 0,
            "error",
            "passed=%s residual=%s deleted=%s"
            % (rollback.get("passed"), rollback.get("residualAssets"), rollback.get("deletedAssets")),
            "Delete any public fixture assets created by the executor before ending the commandlet.",
        ),
        _row(
            "production-boundary",
            _int(runtime.get("engineWrites")) == 0 and _int(runtime.get("productionWrites")) == 0,
            "error",
            "engineWrites=%s productionWrites=%s" % (runtime.get("engineWrites"), runtime.get("productionWrites")),
            "Do not mutate engine or production assets in portfolio executor.",
        ),
    ]
    for error in snapshot.get("errors", []):
        rows.append(_row("runtime-error:%s" % len(rows), False, "error", str(error), "Fix Unreal executor error."))
    return rows


def _row(rule_id: str, passed: bool, fail_status: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "groom-controlled-executor:%s" % rule_id,
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "No action." if passed else fix_preview,
    }


def _summarize(rows: Iterable[Dict[str, Any]], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    row_list = list(rows)
    errors = sum(1 for row in row_list if row["status"] == "error")
    warnings = sum(1 for row in row_list if row["status"] == "warning")
    runtime = snapshot.get("runtime", {})
    import_task = snapshot.get("importTask", {})
    binding = snapshot.get("bindingAttempt", {})
    post = snapshot.get("postExecution", {})
    rollback = snapshot.get("rollback", {})
    operation_applied = bool(import_task.get("succeeded") or binding.get("succeeded"))
    rollback_passed = bool(rollback.get("passed")) and int(rollback.get("residualAssetCount") or 0) == 0
    return {
        "gate": "Blocked" if errors else "Review" if warnings else "Ready",
        "rowCount": len(row_list),
        "pass": sum(1 for row in row_list if row["status"] == "pass"),
        "warning": warnings,
        "error": errors,
        "selectedOperations": 1 if snapshot.get("selectedOperation", {}).get("assetId") else 0,
        "importAttempted": 1 if import_task.get("attempted") else 0,
        "importSucceeded": 1 if import_task.get("succeeded") else 0,
        "importedAssetClass": post.get("expectedGroomAsset", {}).get("className"),
        "wrongImportedClass": bool(
            post.get("expectedGroomAsset", {}).get("exists")
            and post.get("expectedGroomAsset", {}).get("className") != "GroomAsset"
        ),
        "groomPostCheckPassed": 1
        if post.get("expectedGroomAsset", {}).get("exists") and post.get("expectedGroomAsset", {}).get("className") == "GroomAsset"
        else 0,
        "bindingAttempted": 1 if binding.get("attempted") else 0,
        "bindingSucceeded": 1 if binding.get("succeeded") else 0,
        "bindingPostCheckPassed": 1 if post.get("expectedBindingAsset", {}).get("exists") else 0,
        "rollbackPassed": 1 if rollback_passed else 0,
        "residualAssetCount": int(rollback.get("residualAssetCount") or 0),
        "assetWrites": _int(runtime.get("assetWrites")),
        "engineWrites": _int(runtime.get("engineWrites")),
        "productionWrites": _int(runtime.get("productionWrites")),
        "persistentMutation": bool(operation_applied and not rollback_passed),
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for row in rows:
        if row["status"] == "pass":
            continue
        actions.append(
            {
                "id": "owner-action:%s" % row["ruleId"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "owner": _owner_for_rule(row["ruleId"]),
                "mutationScope": "owner_required" if row["status"] == "error" else "manual_review",
                "preview": row["fixPreview"],
                "writeBoundary": "public_fixture_execute_then_rollback",
            }
        )
    return actions


def _owner_for_rule(rule_id: str) -> str:
    if rule_id in {"source-cache-ready", "plugin-api-ready", "import-task-attempted", "groom-import-created", "binding-method-visible", "binding-created"}:
        return "engine-ta"
    if rule_id in {"preflight-target-mesh"}:
        return "content-owner"
    if rule_id in {"rollback-clean", "production-boundary", "public-write-scope", "runtime-available"}:
        return "pipeline-ta"
    return "reviewer"


def _l3_status(summary: Dict[str, Any], runtime: Dict[str, Any]) -> str:
    if runtime.get("blockedReason"):
        return str(runtime.get("blockedReason"))
    if not runtime.get("executed"):
        return "contract_groom_controlled_executor"
    if summary.get("gate") == "Ready":
        return "unreal_groom_executor_import_binding_rolled_back"
    if summary.get("wrongImportedClass") and summary.get("rollbackPassed"):
        return "unreal_groom_executor_wrong_asset_class_rolled_back"
    if summary.get("rollbackPassed"):
        return "unreal_groom_executor_api_limited_rolled_back"
    return "unreal_groom_executor_blocked"


def _int(value: Any) -> int:
    try:
        return int(value or 0)
    except Exception:
        return 0
