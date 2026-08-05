"""Unreal Groom runtime fact collector.

This layer runs after the controlled executor path. It imports the approved
public curve-only groom cache, reads GroomAsset / GroomBindingAsset runtime
facts while the assets exist, then rolls back public fixture writes.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path


REPORT_VERSION = "groom-runtime-facts@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]
PUBLIC_GAME_PREFIX = "/Game/AI_Tool_TA/"


def resolve_public_path(path: str | Path | None) -> Path:
    text = str(path or "")
    if text.startswith("<repo>\\"):
        return PORTFOLIO_ROOT / text.replace("<repo>\\", "", 1)
    if text.startswith("<repo>/"):
        return PORTFOLIO_ROOT / text.replace("<repo>/", "", 1)
    return Path(text)


def build_groom_runtime_facts_report(
    postcheck_path: str | Path,
    plugin_fixture_path: str | Path,
    controlled_executor_path: str | Path | None,
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    postcheck = _read_json(resolve_public_path(postcheck_path))
    plugin_fixture = _read_json(resolve_public_path(plugin_fixture_path))
    controlled_executor = _read_json(resolve_public_path(controlled_executor_path)) if controlled_executor_path else {}
    rows = _evaluate_rows(postcheck, plugin_fixture, controlled_executor, runtime_snapshot)
    summary = _summarize(rows, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if runtime.get("executed") else "Blocked",
        "l3Status": _l3_status(summary, runtime),
        "sourceImportPostcheck": _source_record(postcheck_path, postcheck),
        "sourcePluginApiFixture": _source_record(plugin_fixture_path, plugin_fixture),
        "sourceControlledExecutor": _source_record(controlled_executor_path, controlled_executor),
        "selectedOperation": runtime_snapshot.get("selectedOperation", {}),
        "unrealRuntime": runtime,
        "facts": {
            "schema": "groom-runtime-facts-input@0.1.0",
            "summary": summary,
            "assetFacts": runtime_snapshot.get("assetFacts", {}),
            "apiSurface": runtime_snapshot.get("apiSurface", {}),
            "sourceCache": runtime_snapshot.get("selectedOperation", {}).get("cache", {}),
        },
        "transaction": {
            "mode": runtime_snapshot.get("mode", "execute_collect_then_rollback"),
            "preflight": runtime_snapshot.get("preflight", {}),
            "importTask": runtime_snapshot.get("importTask", {}),
            "bindingAttempt": runtime_snapshot.get("bindingAttempt", {}),
            "rollback": runtime_snapshot.get("rollback", {}),
            "writeSet": runtime_snapshot.get("writeSet", []),
            "rollbackActions": runtime_snapshot.get("rollbackActions", []),
            "errors": runtime_snapshot.get("errors", []),
        },
        "evaluation": {
            "schema": "groom-runtime-facts-evaluation@0.1.0",
            "summary": {
                "gate": summary["gate"],
                "checks": len(rows),
                "pass": summary["pass"],
                "warning": summary["warning"],
                "error": summary["error"],
            },
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "groom-runtime-facts",
            "name": "Groom Runtime Fact Collector",
            "methodSource": "Unreal HairStrandsFactory import + GroomLibrary binding + runtime fact readback + rollback",
            "protocolCarrier": "GroomAsset, GroomBindingAsset, target SkeletalMesh, API method surface, readable runtime fields",
            "boundary": {
                "mutation": "public_fixture_execute_collect_then_rollback",
                "assetWrites": summary["assetWrites"],
                "engineWrites": summary["engineWrites"],
                "productionWrites": summary["productionWrites"],
                "persistentMutation": summary["persistentMutation"],
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public Groom fixture only"),
            },
        },
        "reviewerClaims": [
            "R55 reads GroomAsset and GroomBindingAsset facts while the controlled public fixture assets exist, then rolls them back.",
            "The collector separates import success from runtime fact readability: a GroomAsset must expose enough package, method and property surface to be reviewable.",
            "The report keeps all writes inside /Game/AI_Tool_TA and requires rollback residue to be zero before a Ready gate.",
        ],
    }


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path and path.exists() else {}


def _source_record(path: str | Path | None, payload: Dict[str, Any]) -> Dict[str, Any]:
    if not path:
        return {"path": None, "reportVersion": None, "evidenceLevel": None, "l3Status": None, "gate": None}
    resolved = resolve_public_path(path)
    return {
        "path": public_path(resolved),
        "reportVersion": payload.get("reportVersion"),
        "evidenceLevel": payload.get("evidenceLevel"),
        "l3Status": payload.get("l3Status"),
        "gate": payload.get("evaluation", {}).get("summary", {}).get("gate"),
    }


def _evaluate_rows(
    postcheck: Dict[str, Any],
    plugin_fixture: Dict[str, Any],
    controlled_executor: Dict[str, Any],
    snapshot: Dict[str, Any],
) -> List[Dict[str, Any]]:
    runtime = snapshot.get("runtime", {})
    selected = snapshot.get("selectedOperation", {})
    facts = snapshot.get("assetFacts", {})
    api = snapshot.get("apiSurface", {})
    rollback = snapshot.get("rollback", {})
    write_set = snapshot.get("writeSet", [])
    source_summary = postcheck.get("facts", {}).get("summary", {})
    plugin_summary = plugin_fixture.get("facts", {}).get("summary", {})
    controlled_summary = controlled_executor.get("facts", {}).get("summary", {})
    groom_fact = facts.get("groomAsset", {})
    binding_fact = facts.get("bindingAsset", {})
    target_fact = facts.get("targetSkeletalMesh", {})
    return [
        _row(
            "runtime-entered",
            bool(runtime.get("executed")),
            "error",
            "executed=%s engine=%s" % (runtime.get("executed"), runtime.get("engineVersion")),
            "Run through UnrealEditor-Cmd before claiming runtime facts.",
        ),
        _row(
            "source-cache-linked",
            bool(selected.get("cache", {}).get("hashMatches")) and bool(source_summary.get("cacheHashMatchedRows")),
            "error",
            "hashMatches=%s sourceHashRows=%s"
            % (selected.get("cache", {}).get("hashMatches"), source_summary.get("cacheHashMatchedRows")),
            "Use the approved curve-only Alembic cache receipt.",
        ),
        _row(
            "plugin-api-ready",
            bool(plugin_summary.get("groomImportApiReady")) and bool(api.get("classes", {}).get("GroomAsset")),
            "error",
            "groomImportApiReady=%s GroomAssetClass=%s"
            % (plugin_summary.get("groomImportApiReady"), api.get("classes", {}).get("GroomAsset")),
            "Keep HairStrands/Alembic plugins enabled in the public project.",
        ),
        _row(
            "controlled-executor-ready-source",
            controlled_executor.get("l3Status") == "unreal_groom_executor_import_binding_rolled_back",
            "warning",
            "sourceStatus=%s sourceGate=%s selected=%s"
            % (
                controlled_executor.get("l3Status"),
                controlled_executor.get("evaluation", {}).get("summary", {}).get("gate"),
                controlled_summary.get("selectedOperations"),
            ),
            "Run the controlled executor before using it as a runtime-fact source.",
        ),
        _row(
            "groom-asset-created",
            groom_fact.get("exists") and groom_fact.get("className") == "GroomAsset",
            "error",
            "exists=%s class=%s path=%s"
            % (groom_fact.get("exists"), groom_fact.get("className"), groom_fact.get("path")),
            "Import the curve-only Alembic as a GroomAsset before reading runtime facts.",
        ),
        _row(
            "binding-asset-created",
            binding_fact.get("exists") and binding_fact.get("className") == "GroomBindingAsset",
            "error",
            "exists=%s class=%s path=%s"
            % (binding_fact.get("exists"), binding_fact.get("className"), binding_fact.get("path")),
            "Create the GroomBindingAsset against the target SkeletalMesh before approval.",
        ),
        _row(
            "target-skeletalmesh-present",
            target_fact.get("exists") and target_fact.get("className") == "SkeletalMesh",
            "error",
            "exists=%s class=%s path=%s"
            % (target_fact.get("exists"), target_fact.get("className"), target_fact.get("path")),
            "Restore the public SK_HeroFace target mesh.",
        ),
        _row(
            "groom-runtime-readable",
            int(groom_fact.get("readablePropertyCount") or 0) > 0 or int(groom_fact.get("callResultCount") or 0) > 0,
            "warning",
            "properties=%s methods=%s calls=%s"
            % (
                groom_fact.get("readablePropertyCount"),
                groom_fact.get("methodCount"),
                groom_fact.get("callResultCount"),
            ),
            "Expose deeper GroomAsset stats through an Editor Utility/C++ bridge if Python surface is too shallow.",
        ),
        _row(
            "binding-runtime-readable",
            int(binding_fact.get("readablePropertyCount") or 0) > 0 or int(binding_fact.get("callResultCount") or 0) > 0,
            "warning",
            "properties=%s methods=%s calls=%s"
            % (
                binding_fact.get("readablePropertyCount"),
                binding_fact.get("methodCount"),
                binding_fact.get("callResultCount"),
            ),
            "Expose deeper GroomBindingAsset stats through an Editor Utility/C++ bridge if Python surface is too shallow.",
        ),
        _row(
            "public-write-scope",
            bool(write_set) and all(str(path).startswith(PUBLIC_GAME_PREFIX) for path in write_set),
            "error",
            "writeSet=%s" % write_set,
            "Restrict runtime fact fixture writes to /Game/AI_Tool_TA.",
        ),
        _row(
            "rollback-clean",
            bool(rollback.get("passed")) and int(rollback.get("residualAssetCount") or 0) == 0,
            "error",
            "passed=%s residual=%s deleted=%s"
            % (rollback.get("passed"), rollback.get("residualAssetCount"), rollback.get("deletedAssets")),
            "Delete all public fixture assets created for runtime fact collection.",
        ),
    ]


def _summarize(rows: List[Dict[str, Any]], snapshot: Dict[str, Any]) -> Dict[str, Any]:
    runtime = snapshot.get("runtime", {})
    facts = snapshot.get("assetFacts", {})
    rollback = snapshot.get("rollback", {})
    errors = snapshot.get("errors", [])
    error_count = sum(1 for row in rows if row["status"] == "error")
    warning_count = sum(1 for row in rows if row["status"] == "warning")
    gate = "Blocked" if error_count else ("Review" if warning_count else "Ready")
    asset_rows = [facts.get("groomAsset", {}), facts.get("bindingAsset", {}), facts.get("targetSkeletalMesh", {})]
    return {
        "gate": gate,
        "assetFacts": len([row for row in asset_rows if row]),
        "runtimeAssetsPresent": sum(1 for row in asset_rows if row.get("exists")),
        "groomAssetClass": facts.get("groomAsset", {}).get("className"),
        "bindingAssetClass": facts.get("bindingAsset", {}).get("className"),
        "targetMeshClass": facts.get("targetSkeletalMesh", {}).get("className"),
        "readableProperties": sum(int(row.get("readablePropertyCount") or 0) for row in asset_rows),
        "methodSurface": sum(int(row.get("methodCount") or 0) for row in asset_rows),
        "callResults": sum(int(row.get("callResultCount") or 0) for row in asset_rows),
        "rollbackPassed": bool(rollback.get("passed")),
        "residualAssetCount": int(rollback.get("residualAssetCount") or 0),
        "assetWrites": int(runtime.get("assetWrites") or 0),
        "engineWrites": int(runtime.get("engineWrites") or 0),
        "productionWrites": int(runtime.get("productionWrites") or 0),
        "persistentMutation": bool(rollback.get("residualAssetCount")),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": warning_count,
        "error": error_count,
        "runtimeErrors": len(errors),
    }


def _l3_status(summary: Dict[str, Any], runtime: Dict[str, Any]) -> str:
    if not runtime.get("executed"):
        return "unreal_groom_runtime_facts_not_entered"
    if summary.get("gate") == "Ready":
        return "unreal_groom_runtime_facts_collected"
    if summary.get("rollbackPassed"):
        return "unreal_groom_runtime_facts_collected_with_review"
    return "unreal_groom_runtime_facts_blocked"


def _row(rule_id: str, passed: bool, failure_status: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "groom-runtime-facts:%s" % rule_id,
        "ruleId": rule_id,
        "status": "pass" if passed else failure_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    owners = {
        "source-cache-linked": "groom-export-owner",
        "plugin-api-ready": "engine-ta",
        "controlled-executor-ready-source": "engine-ta",
        "groom-asset-created": "engine-ta",
        "binding-asset-created": "character-tech-art",
        "target-skeletalmesh-present": "character-tech-art",
        "groom-runtime-readable": "engine-ta",
        "binding-runtime-readable": "engine-ta",
        "public-write-scope": "tool-ta",
        "rollback-clean": "tool-ta",
    }
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        rule_id = row.get("ruleId")
        actions.append(
            {
                "id": "groom-runtime-action:%s" % rule_id,
                "ruleId": rule_id,
                "status": row.get("status"),
                "owner": owners.get(rule_id, "tool-ta"),
                "preview": row.get("fixPreview"),
                "writeBoundary": "preview_only",
            }
        )
    return actions
