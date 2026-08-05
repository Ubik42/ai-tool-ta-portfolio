"""Unreal Groom Alembic import/post-check readiness.

This adapter joins the real Maya Alembic cache receipt from R48 with a
read-only Unreal Python probe. It does not import or save assets; the report
describes exactly which cache rows can enter a controlled Groom import
executor, which Unreal API surfaces are visible, and which post-check targets
are still missing.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .contract import load_fixture, public_path


REPORT_VERSION = "groom-alembic-import-postcheck@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def resolve_public_path(path: str | Path | None) -> Path:
    text = str(path or "")
    if text.startswith("<repo>\\"):
        return PORTFOLIO_ROOT / text.replace("<repo>\\", "", 1)
    return Path(text)


def build_groom_alembic_import_postcheck_report(
    source_payload_path: str | Path,
    fixture_path: str | Path | None = None,
    runtime_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_path = resolve_public_path(source_payload_path)
    source_exists = source_path.exists()
    source_payload = json.loads(source_path.read_text(encoding="utf-8")) if source_exists else {}
    resolved_fixture = _resolve_fixture_path(source_payload, fixture_path)
    fixture_exists = resolved_fixture.exists() if resolved_fixture else False
    fixture = load_fixture(resolved_fixture) if fixture_exists else {"assets": []}
    runtime_snapshot = runtime_snapshot or _default_runtime_snapshot()
    facts = _build_facts(source_payload, source_exists, fixture, fixture_exists, runtime_snapshot)
    evaluation = _evaluate_facts(facts, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if executed else "Blocked",
        "l3Status": _l3_status(evaluation.get("summary", {}), runtime),
        "sourceAlembicPayload": {
            "path": public_path(source_path),
            "exists": source_exists,
            "reportVersion": source_payload.get("reportVersion"),
            "evidenceLevel": source_payload.get("evidenceLevel"),
            "l3Status": source_payload.get("l3Status"),
            "gate": source_payload.get("evaluation", {}).get("summary", {}).get("gate"),
            "cacheFiles": source_payload.get("facts", {}).get("summary", {}).get("cacheFiles"),
            "cacheBytes": source_payload.get("facts", {}).get("summary", {}).get("cacheBytes"),
            "cacheHashes": source_payload.get("facts", {}).get("summary", {}).get("cacheHashes"),
        },
        "sourceFixture": {
            "path": public_path(resolved_fixture) if resolved_fixture else None,
            "exists": fixture_exists,
            "schema": fixture.get("schema"),
        },
        "unrealRuntime": runtime,
        "apiAvailability": runtime_snapshot.get("api", {}),
        "facts": facts,
        "evaluation": evaluation,
        "adapter": {
            "id": "groom-alembic-import-postcheck",
            "name": "Groom Alembic Import/Post-check Readiness",
            "methodSource": "R48 Maya AbcExport cache receipt + Unreal Python read-only import API probe",
            "protocolCarrier": "Alembic cache sha256, expected Groom/Binding paths, target SkeletalMesh and import-task dry run",
            "boundary": {
                "mutation": "read_only_unreal_import_postcheck_probe",
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "read-only; no import, no save"),
            },
        },
        "reviewerClaims": [
            "R49 joins the real R48 Alembic cache file to Unreal-side import API and post-check facts instead of stopping at a Maya cache receipt.",
            "The approved groom row proves cache bytes and sha256 continuity; blocked TMP rows stay held and do not enter the engine executor plan.",
            "The Unreal probe constructs import-task readiness data without importing or saving assets, keeping missing Groom/Binding API and target assets visible as blockers.",
        ],
    }


def _resolve_fixture_path(source_payload: Dict[str, Any], fixture_path: str | Path | None) -> Optional[Path]:
    if fixture_path:
        return resolve_public_path(fixture_path)
    fixture = source_payload.get("sourceArtifact", {}).get("fixture")
    return resolve_public_path(fixture) if fixture else None


def _default_runtime_snapshot() -> Dict[str, Any]:
    return {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "engineVersion": "not_entered",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "api": {},
        "assets": [],
    }


def _build_facts(
    source_payload: Dict[str, Any],
    source_exists: bool,
    fixture: Dict[str, Any],
    fixture_exists: bool,
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    fixture_assets = {str(row.get("id")): row for row in fixture.get("assets", [])}
    runtime_assets = {str(row.get("assetId")): row for row in runtime_snapshot.get("assets", [])}
    api = runtime_snapshot.get("api", {})
    rows = []
    for operation in source_payload.get("facts", {}).get("operations", []):
        asset_id = str(operation.get("assetId"))
        rows.append(_merge_operation(operation, fixture_assets.get(asset_id, {}), runtime_assets.get(asset_id, {}), api))
    return {
        "schema": "groom-alembic-import-postcheck-facts@0.1.0",
        "sourcePayloadReadable": source_exists,
        "fixtureReadable": fixture_exists,
        "runtimeCollected": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "operations": rows,
        "summary": _summarize_facts(rows, source_exists, fixture_exists, runtime_snapshot),
    }


def _merge_operation(
    operation: Dict[str, Any],
    fixture_asset: Dict[str, Any],
    runtime_row: Dict[str, Any],
    api: Dict[str, Any],
) -> Dict[str, Any]:
    asset_id = str(operation.get("assetId"))
    source_cache = operation.get("cache", {})
    runtime_cache = runtime_row.get("cache") or _cache_facts(source_cache.get("path"))
    source_sha = source_cache.get("sha256")
    runtime_sha = runtime_cache.get("sha256")
    selected = bool(operation.get("exportSelected"))
    cache_hash_matches = bool((not selected) or (source_sha and runtime_sha and source_sha == runtime_sha))
    cache_file_present = bool((not selected) or (runtime_cache.get("exists") and int(runtime_cache.get("bytes") or 0) > 0))
    import_candidate = bool(
        selected
        and operation.get("sourceStatus") == "Ready"
        and operation.get("cacheContractReady")
        and operation.get("exportResult", {}).get("succeeded")
        and cache_file_present
        and cache_hash_matches
    )
    unreal_targets = fixture_asset.get("unreal", {})
    target_groom = str(unreal_targets.get("expectedGroomAsset") or "")
    target_binding = str(unreal_targets.get("expectedBindingAsset") or "")
    target_mesh = str(unreal_targets.get("targetSkeletalMesh") or "")
    target_probe = runtime_row.get("targetSkeletalMesh") or {}
    groom_probe = runtime_row.get("expectedGroomAsset") or {}
    binding_probe = runtime_row.get("expectedBindingAsset") or {}
    task_probe = runtime_row.get("importTaskDryRun") or {}
    classes = api.get("classes", {}) if isinstance(api.get("classes"), dict) else {}
    groom_api_ready = bool(
        (api.get("groomApiVisible") or classes.get("GroomAsset"))
        and (api.get("groomBindingApiVisible") or classes.get("GroomBindingAsset"))
        and (api.get("groomImportFactoryVisible") or api.get("groomImportOptionsVisible"))
    )
    import_task_ready = bool(api.get("importTaskVisible") and task_probe.get("taskConstructed"))
    alembic_api_ready = bool(api.get("alembicImportFactoryVisible"))
    held_reason = _held_reason(import_candidate, groom_api_ready, import_task_ready, alembic_api_ready, runtime_row)
    return {
        "assetId": asset_id,
        "assetLabel": operation.get("assetLabel"),
        "sourceStatus": operation.get("sourceStatus"),
        "sourceExportSelected": selected,
        "sourceCacheContractReady": bool(operation.get("cacheContractReady")),
        "sourceExportSucceeded": bool(operation.get("exportResult", {}).get("succeeded")),
        "sourceHeldReason": operation.get("heldReason"),
        "cache": {
            "sourcePath": source_cache.get("path"),
            "runtimePath": runtime_cache.get("path"),
            "exists": bool(runtime_cache.get("exists")),
            "bytes": int(runtime_cache.get("bytes") or 0),
            "sourceSha256": source_sha,
            "runtimeSha256": runtime_sha,
            "hashMatches": cache_hash_matches,
        },
        "unrealTargets": {
            "expectedGroomAsset": target_groom,
            "expectedBindingAsset": target_binding,
            "targetSkeletalMesh": target_mesh,
            "materialSlot": unreal_targets.get("materialSlot"),
        },
        "runtimeTargets": {
            "targetSkeletalMeshExists": bool(target_probe.get("exists")),
            "targetSkeletalMeshClass": target_probe.get("assetClass"),
            "expectedGroomAssetExists": bool(groom_probe.get("exists")),
            "expectedGroomAssetClass": groom_probe.get("assetClass"),
            "expectedBindingAssetExists": bool(binding_probe.get("exists")),
            "expectedBindingAssetClass": binding_probe.get("assetClass"),
        },
        "api": {
            "importTaskVisible": bool(api.get("importTaskVisible")),
            "assetToolsVisible": bool(api.get("assetToolsVisible")),
            "alembicImportFactoryVisible": bool(api.get("alembicImportFactoryVisible")),
            "groomApiVisible": bool(api.get("groomApiVisible")),
            "groomBindingApiVisible": bool(api.get("groomBindingApiVisible")),
            "groomImportFactoryVisible": bool(api.get("groomImportFactoryVisible")),
            "groomImportOptionsVisible": bool(api.get("groomImportOptionsVisible")),
            "groomImportApiReady": groom_api_ready,
            "alembicImportApiReady": alembic_api_ready,
            "importTaskDryRunReady": import_task_ready,
            "classRows": classes,
            "pluginRows": api.get("plugins", {}),
        },
        "importPlan": {
            "candidate": import_candidate,
            "executionMode": "held_readiness_only",
            "executionHeld": True,
            "heldReason": held_reason,
            "expectedDestination": _asset_dir(target_groom),
            "taskDryRun": task_probe,
            "importExecuted": bool(runtime_row.get("importExecuted")),
            "postCheckAssets": 0,
        },
        "writeBoundary": {
            "assetWrites": int(runtime_row.get("assetWrites") or 0),
            "engineWrites": int(runtime_row.get("engineWrites") or 0),
            "productionWrites": int(runtime_row.get("productionWrites") or 0),
        },
    }


def _summarize_facts(
    rows: Iterable[Dict[str, Any]],
    source_exists: bool,
    fixture_exists: bool,
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    row_list = list(rows)
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "sourcePayloadReadable": source_exists,
        "fixtureReadable": fixture_exists,
        "operationRows": len(row_list),
        "selectedRows": sum(1 for row in row_list if row.get("sourceExportSelected")),
        "heldSourceRows": sum(1 for row in row_list if not row.get("sourceExportSelected")),
        "importCandidateRows": sum(1 for row in row_list if row.get("importPlan", {}).get("candidate")),
        "cacheFilesPresent": sum(1 for row in row_list if row.get("cache", {}).get("exists")),
        "cacheHashMatchedRows": sum(1 for row in row_list if row.get("sourceExportSelected") and row.get("cache", {}).get("hashMatches")),
        "runtimeCollected": bool(runtime.get("executed")),
        "assetImportTaskDryRunRows": sum(1 for row in row_list if row.get("api", {}).get("importTaskDryRunReady")),
        "alembicImportFactoryVisibleRows": sum(1 for row in row_list if row.get("api", {}).get("alembicImportFactoryVisible")),
        "groomImportApiReadyRows": sum(1 for row in row_list if row.get("api", {}).get("groomImportApiReady")),
        "targetSkeletalMeshPresentRows": sum(1 for row in row_list if row.get("runtimeTargets", {}).get("targetSkeletalMeshExists")),
        "expectedGroomAssetsPresentRows": sum(1 for row in row_list if row.get("runtimeTargets", {}).get("expectedGroomAssetExists")),
        "expectedBindingAssetsPresentRows": sum(1 for row in row_list if row.get("runtimeTargets", {}).get("expectedBindingAssetExists")),
        "importExecutedRows": sum(1 for row in row_list if row.get("importPlan", {}).get("importExecuted")),
        "importHeldRows": sum(1 for row in row_list if row.get("importPlan", {}).get("executionHeld")),
        "assetWrites": runtime.get("assetWrites", 0),
        "engineWrites": runtime.get("engineWrites", 0),
        "productionWrites": runtime.get("productionWrites", 0),
    }


def _evaluate_facts(facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    if not facts.get("sourcePayloadReadable"):
        evaluations.append(
            _eval(
                "source",
                "source-alembic-payload-readable",
                False,
                "error",
                "Source Alembic Payload",
                "R49 must read the R48 Groom Alembic payload receipt.",
                "missing",
                "Regenerate R48 Groom Alembic Payload Receipt.",
            )
        )
    if not facts.get("fixtureReadable"):
        evaluations.append(
            _eval(
                "fixture",
                "source-fixture-readable",
                False,
                "error",
                "Source Fixture",
                "R49 must join the R48 payload to expected Unreal Groom/Binding target paths.",
                "missing",
                "Restore the public synthetic groom fixture.",
            )
        )
    for row in facts.get("operations", []):
        evaluations.extend(_evaluate_operation(row, runtime_snapshot))
    return {
        "schema": "groom-alembic-import-postcheck-evaluation@0.1.0",
        "summary": _summarize_evaluations(evaluations),
        "evaluations": evaluations,
        "ownerActions": _owner_actions(evaluations),
    }


def _evaluate_operation(row: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    runtime = runtime_snapshot.get("runtime", {})
    candidate = bool(row.get("importPlan", {}).get("candidate"))
    source_selected = bool(row.get("sourceExportSelected"))
    api = row.get("api", {})
    targets = row.get("unrealTargets", {})
    runtime_targets = row.get("runtimeTargets", {})
    writes = row.get("writeBoundary", {})
    return [
        _eval(
            row["assetId"],
            "source-alembic-row-ready",
            row.get("sourceStatus") == "Ready",
            "error",
            "Source Alembic Row",
            "Only R48 Ready/exported groom rows can enter Unreal Alembic import post-check.",
            row.get("sourceStatus"),
            "Resolve upstream groom/cache defects before engine import planning.",
        ),
        _eval(
            row["assetId"],
            "cache-file-present",
            (not source_selected) or bool(row.get("cache", {}).get("exists") and int(row.get("cache", {}).get("bytes") or 0) > 0),
            "error",
            "Alembic Cache File",
            "Selected Groom rows must carry a non-empty .abc file into Unreal readiness.",
            "%s bytes=%s" % (row.get("cache", {}).get("runtimePath"), row.get("cache", {}).get("bytes")),
            "Regenerate the R48 Alembic cache receipt.",
        ),
        _eval(
            row["assetId"],
            "cache-hash-matches",
            (not source_selected) or bool(row.get("cache", {}).get("hashMatches")),
            "error",
            "Alembic Cache Hash",
            "The R49 runtime-visible cache must match the R48 sha256 receipt.",
            "%s == %s" % (row.get("cache", {}).get("sourceSha256"), row.get("cache", {}).get("runtimeSha256")),
            "Re-export the Alembic cache or refresh the payload receipt.",
        ),
        _eval(
            row["assetId"],
            "unreal-python-runtime",
            bool(runtime.get("executed")),
            "error",
            "Unreal Python Runtime",
            "Import post-check facts must be collected inside the public Unreal project.",
            runtime.get("engineVersion"),
            "Run run_alembic_import_postcheck.py with UnrealEditor-Cmd available.",
        ),
        _eval(
            row["assetId"],
            "asset-import-task-dry-run",
            (not candidate) or bool(api.get("importTaskDryRunReady")),
            "error",
            "AssetImportTask Dry Run",
            "A controlled executor needs AssetImportTask to be constructable and property-settable before import.",
            row.get("importPlan", {}).get("taskDryRun"),
            "Fix Unreal Python import-task API access before enabling the executor.",
        ),
        _eval(
            row["assetId"],
            "alembic-import-api-surface",
            (not candidate) or bool(api.get("alembicImportApiReady")),
            "error",
            "Alembic Import API",
            "The engine side must expose an Alembic import factory or equivalent cache import API.",
            "AlembicImportFactory=%s" % api.get("alembicImportFactoryVisible"),
            "Enable/verify the Unreal Alembic importer plugin.",
        ),
        _eval(
            row["assetId"],
            "groom-import-api-surface",
            (not candidate) or bool(api.get("groomImportApiReady")),
            "error",
            "Groom Import API",
            "A Groom executor needs GroomAsset, GroomBindingAsset and Groom import options/factory visibility.",
            "GroomAsset=%s GroomBindingAsset=%s GroomFactory=%s GroomOptions=%s"
            % (
                api.get("groomApiVisible"),
                api.get("groomBindingApiVisible"),
                api.get("groomImportFactoryVisible"),
                api.get("groomImportOptionsVisible"),
            ),
            "Expose Groom plugin Python API or keep the row in owner-held readiness.",
        ),
        _eval(
            row["assetId"],
            "target-skeletal-mesh-exists",
            (not candidate) or bool(runtime_targets.get("targetSkeletalMeshExists")),
            "error",
            "Target SkeletalMesh",
            "Groom Binding post-check needs the target SkeletalMesh to exist in the Unreal fixture project.",
            targets.get("targetSkeletalMesh"),
            "Create or relink the public target SkeletalMesh.",
        ),
        _eval(
            row["assetId"],
            "target-groom-path-declared",
            (not candidate) or bool(targets.get("expectedGroomAsset")),
            "error",
            "Expected Groom Path",
            "The executor plan must declare the GroomAsset path it will create or update.",
            targets.get("expectedGroomAsset"),
            "Declare unreal.expectedGroomAsset in the groom fixture payload.",
        ),
        _eval(
            row["assetId"],
            "target-binding-path-declared",
            (not candidate) or bool(targets.get("expectedBindingAsset")),
            "error",
            "Expected Binding Path",
            "The executor plan must declare the GroomBindingAsset path for post-check.",
            targets.get("expectedBindingAsset"),
            "Declare unreal.expectedBindingAsset in the groom fixture payload.",
        ),
        _eval(
            row["assetId"],
            "import-execution-held",
            bool(row.get("importPlan", {}).get("executionHeld")) and not bool(row.get("importPlan", {}).get("importExecuted")),
            "error",
            "Import Execution Hold",
            "R49 is a readiness/post-check probe and must hold actual import execution.",
            row.get("importPlan", {}).get("heldReason"),
            "Move writes to a controlled executor with rollback receipt.",
        ),
        _eval(
            row["assetId"],
            "expected-groom-postcheck-gap",
            (not candidate) or bool(runtime_targets.get("expectedGroomAssetExists")),
            "warning",
            "Expected Groom Asset Post-check",
            "Missing GroomAsset is expected before executor write, but must stay visible for signoff.",
            targets.get("expectedGroomAsset"),
            "Create/import the GroomAsset in the controlled executor and re-run post-check.",
        ),
        _eval(
            row["assetId"],
            "expected-binding-postcheck-gap",
            (not candidate) or bool(runtime_targets.get("expectedBindingAssetExists")),
            "warning",
            "Expected Binding Asset Post-check",
            "Missing GroomBindingAsset is expected before executor write, but must stay visible for signoff.",
            targets.get("expectedBindingAsset"),
            "Create the GroomBindingAsset after GroomAsset and target mesh validation.",
        ),
        _eval(
            row["assetId"],
            "no-write-boundary",
            int(runtime.get("assetWrites", 0) or 0) == 0
            and int(runtime.get("engineWrites", 0) or 0) == 0
            and int(runtime.get("productionWrites", 0) or 0) == 0
            and int(writes.get("assetWrites", 0) or 0) == 0
            and int(writes.get("productionWrites", 0) or 0) == 0,
            "error",
            "Read-only Boundary",
            "R49 must not import, save, or mutate engine assets.",
            "assetWrites=%s engineWrites=%s productionWrites=%s"
            % (runtime.get("assetWrites", 0), runtime.get("engineWrites", 0), runtime.get("productionWrites", 0)),
            "Revert side effects and keep this stage read-only.",
        ),
    ]


def _summarize_evaluations(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(evaluations)
    asset_ids = sorted({row["assetId"] for row in rows})
    blocked = sorted({row["assetId"] for row in rows if row["status"] == "error"})
    review = sorted({row["assetId"] for row in rows if row["status"] == "warning"} - set(blocked))
    ready = sorted(set(asset_ids) - set(blocked) - set(review))
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "assetCount": len(asset_ids),
        "readyAssets": len(ready),
        "reviewAssets": len(review),
        "blockedAssets": len(blocked),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "readyAssetIds": ready,
        "reviewAssetIds": review,
        "blockedAssetIds": blocked,
    }


def _owner_actions(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for row in evaluations:
        if row["status"] == "pass":
            continue
        actions.append(
            {
                "id": "owner-action:%s" % row["id"],
                "assetId": row["assetId"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "owner": _owner_for_rule(row["ruleId"]),
                "mutationScope": "owner_required" if row["status"] == "error" else "manual_review",
                "preview": row["fixPreview"],
                "writeBoundary": "read_only_unreal_postcheck",
            }
        )
    return actions


def _owner_for_rule(rule_id: str) -> str:
    if rule_id in {"source-alembic-row-ready", "cache-file-present", "cache-hash-matches"}:
        return "groom-ta"
    if rule_id in {"unreal-python-runtime", "asset-import-task-dry-run", "alembic-import-api-surface", "groom-import-api-surface"}:
        return "engine-ta"
    if rule_id in {
        "target-skeletal-mesh-exists",
        "target-groom-path-declared",
        "target-binding-path-declared",
        "expected-groom-postcheck-gap",
        "expected-binding-postcheck-gap",
    }:
        return "content-owner"
    if rule_id in {"import-execution-held", "no-write-boundary"}:
        return "pipeline-ta"
    return "reviewer"


def _held_reason(
    candidate: bool,
    groom_api_ready: bool,
    import_task_ready: bool,
    alembic_api_ready: bool,
    runtime_row: Dict[str, Any],
) -> str:
    if not candidate:
        return runtime_row.get("heldReason") or "source_row_not_import_candidate"
    reasons = ["readiness_probe_no_write"]
    if not import_task_ready:
        reasons.append("asset_import_task_not_dry_run_ready")
    if not alembic_api_ready:
        reasons.append("alembic_import_api_missing")
    if not groom_api_ready:
        reasons.append("groom_import_api_missing")
    reasons.append("owner_approval_required_for_engine_write")
    return ",".join(reasons)


def _cache_facts(path: Any) -> Dict[str, Any]:
    resolved = resolve_public_path(path)
    exists = resolved.exists()
    size = resolved.stat().st_size if exists else 0
    return {
        "path": public_path(resolved) if str(path or "") else None,
        "exists": exists,
        "bytes": size,
        "sha256": _sha256(resolved) if exists and size > 0 else None,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _asset_dir(path: str) -> str:
    if "/" not in path:
        return ""
    return path.rsplit("/", 1)[0]


def _l3_status(summary: Dict[str, Any], runtime: Dict[str, Any]) -> str:
    if runtime.get("blockedReason"):
        return str(runtime.get("blockedReason"))
    if not runtime.get("executed"):
        return "contract_groom_alembic_import_postcheck"
    if summary.get("gate") == "Blocked":
        return "unreal_groom_alembic_import_postcheck_blocked"
    return "unreal_groom_alembic_import_postcheck_collected"


def _eval(
    asset_id: Any,
    rule_id: str,
    passed: bool,
    fail_status: str,
    label: str,
    message: str,
    evidence: Any,
    fix_preview: str,
) -> Dict[str, Any]:
    status = "pass" if passed else fail_status
    return {
        "id": "%s:%s" % (rule_id, asset_id),
        "assetId": str(asset_id),
        "ruleId": rule_id,
        "label": label,
        "status": status,
        "message": "%s is satisfied." % label if passed else message,
        "evidence": evidence,
        "fixPreview": "No action." if passed else fix_preview,
    }
