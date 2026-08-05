"""Maya Alembic payload receipt for groom export."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .contract import evaluate_scene, load_fixture, public_path
from .maya_collector import collect_maya_scene_facts, create_scene_from_fixture, reset_scene


REPORT_VERSION = "groom-alembic-payload@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def build_alembic_payload_report(
    fixture_path: str | Path,
    cache_dir: str | Path,
) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    fixture = load_fixture(fixture_path)
    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    reset_scene(cmds, fixture.get("scene", {}))
    create_scene_from_fixture(cmds, fixture)
    facts = collect_maya_scene_facts(cmds)
    source_evaluation = evaluate_scene(facts)
    plugin = _load_alembic_exporter(cmds)
    operations = _export_operations(cmds, facts, source_evaluation, cache_root, plugin)
    payload = {
        "schema": "groom-alembic-payload-facts@0.1.0",
        "sourceAssets": len(facts.get("assets", [])),
        "operations": operations,
        "summary": _summarize_operations(operations, plugin),
    }
    evaluation = _evaluate_payload(payload, plugin)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if plugin.get("loadedAfter") else "Blocked",
        "l3Status": "maya_groom_alembic_payload_exported" if plugin.get("loadedAfter") else "blocked_by_missing_maya_abc_export",
        "mayaRuntime": {
            "version": _safe(lambda: cmds.about(version=True)),
            "apiVersion": _safe(lambda: cmds.about(apiVersion=True)),
            "batch": bool(_safe(lambda: cmds.about(batch=True), False)),
        },
        "sourceArtifact": {
            "fixture": public_path(fixture_path),
            "sourceFactsSchema": facts.get("schema"),
            "sourceEvaluationGate": source_evaluation.get("summary", {}).get("gate"),
        },
        "alembicPlugin": plugin,
        "facts": payload,
        "evaluation": evaluation,
        "adapter": {
            "id": "groom-alembic-payload",
            "name": "Groom Alembic Payload Receipt",
            "methodSource": "Maya AbcExport over public synthetic groom curves",
            "protocolCarrier": "Approved R46 groom rows + Maya curve roots + Alembic cache receipt",
            "boundary": {
                "mutation": "public_synthetic_alembic_cache_write",
                "cacheRoot": public_path(cache_root),
                "assetWrites": payload["summary"]["cacheFiles"],
                "engineWrites": 0,
                "productionWrites": payload["summary"]["productionWrites"],
                "writeScope": "public repo artifacts/cache only",
            },
        },
        "reviewerClaims": [
            "R48 turns the R46 dry-run Alembic intent into a real Maya AbcExport receipt for the approved public groom row.",
            "Blocked/TMP groom rows are held and do not enter the Alembic cache.",
            "The report records cache path, byte size, sha256, source row status and zero production/engine writes.",
        ],
    }


def _export_operations(
    cmds: Any,
    facts: Dict[str, Any],
    source_evaluation: Dict[str, Any],
    cache_root: Path,
    plugin: Dict[str, Any],
) -> List[Dict[str, Any]]:
    operations = []
    ready_ids = set(source_evaluation.get("summary", {}).get("readyAssetIds", []))
    for row in facts.get("assets", []):
        asset_id = str(row.get("assetId"))
        normalized = row.get("normalized", {})
        source_ready = asset_id in ready_ids
        cache_contract_ready = _cache_contract_ready(normalized)
        export_selected = source_ready and cache_contract_ready and bool(plugin.get("loadedAfter"))
        root = _root_for_asset(cmds, asset_id)
        cache_path = cache_root / ("%s.abc" % asset_id.replace("-", "_"))
        operation = {
            "assetId": asset_id,
            "assetLabel": row.get("assetLabel"),
            "sourceStatus": "Ready" if source_ready else "Blocked",
            "cacheContractReady": cache_contract_ready,
            "exportSelected": export_selected,
            "heldReason": None if export_selected else _held_reason(source_ready, cache_contract_ready, plugin),
            "rootNode": root,
            "frameStart": normalized.get("export.frameStart"),
            "frameEnd": normalized.get("export.frameEnd"),
            "requestedAttrs": [
                "aiToolTaGroomAssetId",
                "aiToolTaGroomLabel",
                "aiToolTaGroomProtocol",
                "aiToolTaGroomExport",
                "aiToolTaGroomUnreal",
                "aiToolTaGroomStrandPayload",
            ],
            "commandPreview": None,
            "cache": {
                "path": public_path(cache_path),
                "exists": False,
                "bytes": 0,
                "sha256": None,
            },
            "exportResult": {
                "attempted": False,
                "succeeded": False,
                "error": None,
            },
            "writeBoundary": {
                "cacheWrites": 0,
                "engineWrites": 0,
                "productionWrites": 0,
            },
        }
        if export_selected:
            _run_export(cmds, operation, cache_path)
        operations.append(operation)
    return operations


def _run_export(cmds: Any, operation: Dict[str, Any], cache_path: Path) -> None:
    root = operation.get("rootNode")
    if not root:
        operation["exportResult"]["attempted"] = True
        operation["exportResult"]["error"] = "missing_root_node"
        return
    frame_start = int(operation.get("frameStart") or 1001)
    frame_end = int(operation.get("frameEnd") or frame_start)
    attrs = " ".join("-attr %s" % attr for attr in operation["requestedAttrs"])
    job = '-frameRange %s %s -uvWrite -worldSpace -writeVisibility %s -root "%s" -file "%s"' % (
        frame_start,
        frame_end,
        attrs,
        root,
        cache_path.as_posix(),
    )
    operation["commandPreview"] = "AbcExport -j %s" % job
    operation["exportResult"]["attempted"] = True
    try:
        if cache_path.exists():
            cache_path.unlink()
        cmds.AbcExport(j=job)
        exists = cache_path.exists()
        size = cache_path.stat().st_size if exists else 0
        operation["cache"].update(
            {
                "exists": exists,
                "bytes": size,
                "sha256": _sha256(cache_path) if exists and size > 0 else None,
            }
        )
        operation["exportResult"]["succeeded"] = bool(exists and size > 0)
        operation["writeBoundary"]["cacheWrites"] = 1 if operation["exportResult"]["succeeded"] else 0
    except Exception as exc:
        operation["exportResult"]["error"] = str(exc)


def _load_alembic_exporter(cmds: Any) -> Dict[str, Any]:
    row = {
        "plugin": "AbcExport",
        "loadedBefore": False,
        "loadedAfter": False,
        "path": None,
        "versionBanner": "Maya AbcExport plugin",
        "error": None,
    }
    try:
        row["loadedBefore"] = bool(cmds.pluginInfo("AbcExport", query=True, loaded=True))
        if not row["loadedBefore"]:
            cmds.loadPlugin("AbcExport", quiet=True)
        row["loadedAfter"] = bool(cmds.pluginInfo("AbcExport", query=True, loaded=True))
        row["path"] = cmds.pluginInfo("AbcExport", query=True, path=True)
    except Exception as exc:
        row["error"] = str(exc)
    return row


def _summarize_operations(operations: Iterable[Dict[str, Any]], plugin: Dict[str, Any]) -> Dict[str, Any]:
    rows = list(operations)
    return {
        "assetRows": len(rows),
        "pluginLoaded": bool(plugin.get("loadedAfter")),
        "selectedRows": sum(1 for row in rows if row.get("exportSelected")),
        "heldRows": sum(1 for row in rows if not row.get("exportSelected")),
        "exportAttempted": sum(1 for row in rows if row.get("exportResult", {}).get("attempted")),
        "exportSucceeded": sum(1 for row in rows if row.get("exportResult", {}).get("succeeded")),
        "cacheFiles": sum(1 for row in rows if row.get("cache", {}).get("exists")),
        "cacheBytes": sum(int(row.get("cache", {}).get("bytes") or 0) for row in rows),
        "cacheHashes": sum(1 for row in rows if row.get("cache", {}).get("sha256")),
        "sourceReadyRows": sum(1 for row in rows if row.get("sourceStatus") == "Ready"),
        "sourceBlockedRows": sum(1 for row in rows if row.get("sourceStatus") == "Blocked"),
        "productionWrites": sum(int(row.get("writeBoundary", {}).get("productionWrites") or 0) for row in rows),
        "engineWrites": sum(int(row.get("writeBoundary", {}).get("engineWrites") or 0) for row in rows),
    }


def _evaluate_payload(payload: Dict[str, Any], plugin: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in payload.get("operations", []):
        evaluations.extend(_evaluate_operation(row, plugin))
    return {
        "schema": "groom-alembic-payload-evaluation@0.1.0",
        "summary": _summarize_evaluations(evaluations),
        "evaluations": evaluations,
        "ownerActions": _owner_actions(evaluations),
    }


def _evaluate_operation(row: Dict[str, Any], plugin: Dict[str, Any]) -> List[Dict[str, Any]]:
    selected = bool(row.get("exportSelected"))
    result = row.get("exportResult", {})
    cache = row.get("cache", {})
    return [
        _eval(
            row["assetId"],
            "source-groom-row-ready",
            row.get("sourceStatus") == "Ready",
            "error",
            "Source Groom Row",
            "Only R46 Ready groom rows can be exported to Alembic.",
            row.get("sourceStatus"),
            "Resolve source groom owner actions before cache export.",
        ),
        _eval(
            row["assetId"],
            "cache-payload-contract",
            bool(row.get("cacheContractReady")),
            "error",
            "Alembic Payload Contract",
            "Selected cache exports must include .abc extension, root UV, strand IDs, guide curves and a valid frame range.",
            "cacheContractReady=%s" % row.get("cacheContractReady"),
            "Fix the Maya groom export payload before Alembic export.",
        ),
        _eval(
            row["assetId"],
            "abc-export-plugin-loaded",
            bool(plugin.get("loadedAfter")),
            "error",
            "Maya AbcExport Plugin",
            "The Maya Alembic exporter must be available before cache receipt generation.",
            plugin.get("path") or plugin.get("error"),
            "Install or load the Maya AbcExport plugin.",
        ),
        _eval(
            row["assetId"],
            "blocked-row-held",
            selected or bool(row.get("heldReason")),
            "error",
            "Blocked Row Hold",
            "Rows that are not export-selected must carry a hold reason.",
            row.get("heldReason"),
            "Record why the row did not enter Alembic export.",
        ),
        _eval(
            row["assetId"],
            "export-command-succeeded",
            not selected or bool(result.get("succeeded")),
            "error",
            "Alembic Export Command",
            "Selected groom rows must produce a successful AbcExport command receipt.",
            result.get("error") or result.get("succeeded"),
            "Rerun the Maya Alembic payload export and inspect AbcExport errors.",
        ),
        _eval(
            row["assetId"],
            "cache-file-created",
            not selected or bool(cache.get("exists") and int(cache.get("bytes") or 0) > 0),
            "error",
            "Alembic Cache File",
            "Selected groom rows must create a non-empty Alembic file.",
            "%s bytes=%s" % (cache.get("path"), cache.get("bytes")),
            "Regenerate the public Alembic cache receipt.",
        ),
        _eval(
            row["assetId"],
            "cache-hash-recorded",
            not selected or bool(cache.get("sha256")),
            "error",
            "Alembic Cache Hash",
            "Export receipts must include sha256 so the cache can be compared later.",
            cache.get("sha256"),
            "Record the exported cache hash.",
        ),
        _eval(
            row["assetId"],
            "no-production-write",
            int(row.get("writeBoundary", {}).get("productionWrites") or 0) == 0
            and int(row.get("writeBoundary", {}).get("engineWrites") or 0) == 0,
            "error",
            "Write Boundary",
            "R48 may write public synthetic cache artifacts only.",
            row.get("writeBoundary"),
            "Move any production or engine write out of the payload receipt stage.",
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
                "mutationScope": "owner_required",
                "preview": row["fixPreview"],
                "writeBoundary": "public_synthetic_cache_only",
            }
        )
    return actions


def _owner_for_rule(rule_id: str) -> str:
    if rule_id in ("source-groom-row-ready", "cache-payload-contract", "blocked-row-held"):
        return "groom-ta"
    if rule_id in ("abc-export-plugin-loaded", "export-command-succeeded", "cache-file-created", "cache-hash-recorded"):
        return "pipeline-ta"
    if rule_id == "no-production-write":
        return "release-ta"
    return "reviewer"


def _root_for_asset(cmds: Any, asset_id: str) -> Optional[str]:
    for node in cmds.ls(type="transform", long=True) or []:
        if not _has_attr(cmds, node, "aiToolTaGroomAssetId"):
            continue
        value = cmds.getAttr("%s.aiToolTaGroomAssetId" % node)
        if str(value) == asset_id:
            return node
    return None


def _cache_contract_ready(normalized: Dict[str, Any]) -> bool:
    frame_start = normalized.get("export.frameStart")
    frame_end = normalized.get("export.frameEnd")
    try:
        frame_range_valid = frame_start is not None and frame_end is not None and int(frame_start) <= int(frame_end)
    except Exception:
        frame_range_valid = False
    return bool(
        normalized.get("export.extensionMatched")
        and normalized.get("export.includeRootUV")
        and normalized.get("export.includeStrandIds")
        and normalized.get("export.includeGuideCurves")
        and frame_range_valid
    )


def _held_reason(source_ready: bool, cache_contract_ready: bool, plugin: Dict[str, Any]) -> str:
    reasons = []
    if not source_ready:
        reasons.append("source_groom_row_not_ready")
    if not cache_contract_ready:
        reasons.append("cache_contract_not_ready")
    if not plugin.get("loadedAfter"):
        reasons.append("abc_export_plugin_missing")
    return ",".join(reasons) or "not_selected"


def _has_attr(cmds: Any, node: str, attr: str) -> bool:
    try:
        return bool(cmds.attributeQuery(attr, node=node, exists=True))
    except Exception:
        return False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _safe(callback: Any, default: Any = "unknown") -> Any:
    try:
        return callback()
    except Exception:
        return default
