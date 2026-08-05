"""Maya Alembic payload receipt for groom export."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .contract import evaluate_scene, load_fixture, public_path
from .maya_collector import collect_maya_scene_facts, create_scene_from_fixture, reset_scene


REPORT_VERSION = "groom-alembic-payload@0.2.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]
EXPORT_MODE_ASSET_ROOT = "asset_root"
EXPORT_MODE_CURVE_ONLY = "curve_only"


def build_alembic_payload_report(
    fixture_path: str | Path,
    cache_dir: str | Path,
    export_mode: str = EXPORT_MODE_ASSET_ROOT,
) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    normalized_export_mode = _normalize_export_mode(export_mode)
    fixture = load_fixture(fixture_path)
    cache_root = Path(cache_dir)
    cache_root.mkdir(parents=True, exist_ok=True)
    reset_scene(cmds, fixture.get("scene", {}))
    create_scene_from_fixture(cmds, fixture)
    facts = collect_maya_scene_facts(cmds)
    source_evaluation = evaluate_scene(facts)
    plugin = _load_alembic_exporter(cmds)
    operations = _export_operations(cmds, facts, source_evaluation, cache_root, plugin, normalized_export_mode)
    payload = {
        "schema": "groom-alembic-payload-facts@0.1.0",
        "exportMode": normalized_export_mode,
        "unrealHairTranslatorCondition": {
            "source": "UE 5.3 AlembicHairTranslator CanTranslate",
            "acceptedBySchemaProbe": "NumCurves > 0 and bHasGeometry == false",
            "reason": "Groom Alembic import is curve-only; polygon mesh geometry lets the generic Alembic path consume the file as StaticMesh.",
        },
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
        "l3Status": _l3_status(plugin, normalized_export_mode),
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
            "methodSource": _method_source(normalized_export_mode),
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
            "The approved R46 dry-run Alembic intent becomes a real Maya AbcExport receipt for the public groom row.",
            "Blocked/TMP groom rows are held and do not enter the Alembic cache.",
            "The report records cache path, byte size, sha256, source row status and zero production/engine writes.",
            "R52 records a local Alembic schema inspection so UE Groom import eligibility is tied to mesh/curve facts instead of importer guesswork.",
        ],
    }


def _export_operations(
    cmds: Any,
    facts: Dict[str, Any],
    source_evaluation: Dict[str, Any],
    cache_root: Path,
    plugin: Dict[str, Any],
    export_mode: str,
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
        curve_roots = _strand_roots_for_asset(cmds, root) if root else []
        operation = {
            "assetId": asset_id,
            "assetLabel": row.get("assetLabel"),
            "exportMode": export_mode,
            "sourceStatus": "Ready" if source_ready else "Blocked",
            "cacheContractReady": cache_contract_ready,
            "exportSelected": export_selected,
            "heldReason": None if export_selected else _held_reason(source_ready, cache_contract_ready, plugin),
            "rootNode": root,
            "curveRootNodes": curve_roots,
            "frameStart": normalized.get("export.frameStart"),
            "frameEnd": normalized.get("export.frameEnd"),
            "requestedAttrs": [
                "aiToolTaGroomAssetId",
                "aiToolTaGroomLabel",
                "aiToolTaGroomProtocol",
                "aiToolTaGroomExport",
                "aiToolTaGroomUnreal",
                "aiToolTaGroomStrandPayload",
                "groom_root_uv",
                "groom_width",
                "groom_id",
                "groom_guide",
                "groom_group_id",
                "groom_group_name",
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
            "schemaInspection": _empty_schema_inspection(cache_path),
            "writeBoundary": {
                "cacheWrites": 0,
                "engineWrites": 0,
                "productionWrites": 0,
            },
        }
        if export_selected:
            _run_export(cmds, operation, cache_path, export_mode)
        operations.append(operation)
    for operation in operations:
        if operation.get("cache", {}).get("exists"):
            operation["schemaInspection"] = _inspect_alembic_cache(cmds, Path(resolve_local_path(operation["cache"]["path"])))
    return operations


def _run_export(cmds: Any, operation: Dict[str, Any], cache_path: Path, export_mode: str) -> None:
    root = operation.get("rootNode")
    roots = _roots_for_export(operation, export_mode)
    if not root or not roots:
        operation["exportResult"]["attempted"] = True
        operation["exportResult"]["error"] = "missing_export_roots:%s" % export_mode
        return
    frame_start = int(operation.get("frameStart") or 1001)
    frame_end = int(operation.get("frameEnd") or frame_start)
    attrs = " ".join("-attr %s" % attr for attr in operation["requestedAttrs"])
    root_args = " ".join('-root "%s"' % node for node in roots)
    job = '-frameRange %s %s -uvWrite -worldSpace -writeVisibility %s %s -file "%s"' % (
        frame_start,
        frame_end,
        attrs,
        root_args,
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


def resolve_local_path(path: str | Path) -> Path:
    text = str(path or "")
    if text.startswith("<repo>\\"):
        return PORTFOLIO_ROOT / text.replace("<repo>\\", "", 1)
    if text.startswith("<repo>/"):
        return PORTFOLIO_ROOT / text.replace("<repo>/", "", 1)
    return Path(text)


def _empty_schema_inspection(cache_path: Path) -> Dict[str, Any]:
    return {
        "schema": "groom-alembic-schema-inspection@0.1.0",
        "cache": public_path(cache_path),
        "attempted": False,
        "succeeded": False,
        "shapeTypeCounts": {},
        "meshShapeCount": 0,
        "curveShapeCount": 0,
        "transformCount": 0,
        "meshShapePaths": [],
        "curveShapePaths": [],
        "hairTranslatorCompatible": False,
        "ueCondition": "NumCurves > 0 && bHasGeometry == false",
        "error": None,
    }


def _inspect_alembic_cache(cmds: Any, cache_path: Path) -> Dict[str, Any]:
    row = _empty_schema_inspection(cache_path)
    row["attempted"] = True
    try:
        if not cache_path.exists():
            row["error"] = "missing_cache_file"
            return row
        if not bool(cmds.pluginInfo("AbcImport", query=True, loaded=True)):
            cmds.loadPlugin("AbcImport", quiet=True)
        cmds.file(new=True, force=True)
        before = set(cmds.ls(long=True) or [])
        cmds.AbcImport(str(cache_path), mode="import")
        after = set(cmds.ls(long=True) or [])
        new_nodes = sorted(after - before)
        shape_counts: Dict[str, int] = {}
        mesh_shapes: List[str] = []
        curve_shapes: List[str] = []
        transforms = 0
        for node in new_nodes:
            node_type = str(_safe(lambda: cmds.nodeType(node), "unknown"))
            shape_counts[node_type] = shape_counts.get(node_type, 0) + 1
            if node_type == "mesh":
                mesh_shapes.append(node)
            elif node_type == "nurbsCurve":
                curve_shapes.append(node)
            elif node_type == "transform":
                transforms += 1
        row.update(
            {
                "succeeded": True,
                "shapeTypeCounts": shape_counts,
                "meshShapeCount": len(mesh_shapes),
                "curveShapeCount": len(curve_shapes),
                "transformCount": transforms,
                "meshShapePaths": mesh_shapes[:80],
                "curveShapePaths": curve_shapes[:80],
                "hairTranslatorCompatible": len(curve_shapes) > 0 and not mesh_shapes,
            }
        )
    except Exception as exc:
        row["error"] = str(exc)
    return row


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
        "curveOnlyRows": sum(1 for row in rows if row.get("exportMode") == EXPORT_MODE_CURVE_ONLY),
        "schemaInspectedRows": sum(1 for row in rows if row.get("schemaInspection", {}).get("succeeded")),
        "schemaCompatibleRows": sum(1 for row in rows if row.get("schemaInspection", {}).get("hairTranslatorCompatible")),
        "meshShapeRows": sum(1 for row in rows if int(row.get("schemaInspection", {}).get("meshShapeCount") or 0) > 0),
        "curveShapeRows": sum(1 for row in rows if int(row.get("schemaInspection", {}).get("curveShapeCount") or 0) > 0),
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
    schema = row.get("schemaInspection", {})
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
            "unreal-hair-schema-compatible",
            (not selected)
            or bool(
                schema.get("succeeded")
                and schema.get("hairTranslatorCompatible")
                and int(schema.get("meshShapeCount") or 0) == 0
                and int(schema.get("curveShapeCount") or 0) > 0
            ),
            "error",
            "Unreal Hair Alembic Schema",
            "UE Groom Alembic translator accepts curve-only files; polygon mesh geometry can route the cache to StaticMesh import.",
            "meshShapes=%s curveShapes=%s compatible=%s"
            % (schema.get("meshShapeCount"), schema.get("curveShapeCount"), schema.get("hairTranslatorCompatible")),
            "Export only strand/guide curve roots for the Groom cache, and keep scalp mesh for binding metadata instead of the Alembic payload.",
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
    if rule_id in (
        "abc-export-plugin-loaded",
        "export-command-succeeded",
        "cache-file-created",
        "cache-hash-recorded",
        "unreal-hair-schema-compatible",
    ):
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


def _strand_roots_for_asset(cmds: Any, root: str) -> List[str]:
    descendants = cmds.listRelatives(root, allDescendents=True, type="transform", fullPath=True) or []
    return sorted(node for node in descendants if _has_attr(cmds, node, "aiToolTaGroomStrandPayload"))


def _roots_for_export(operation: Dict[str, Any], export_mode: str) -> List[str]:
    if export_mode == EXPORT_MODE_CURVE_ONLY:
        return list(operation.get("curveRootNodes") or [])
    root = operation.get("rootNode")
    return [root] if root else []


def _normalize_export_mode(export_mode: str) -> str:
    value = str(export_mode or EXPORT_MODE_ASSET_ROOT).strip().lower().replace("-", "_")
    if value in {EXPORT_MODE_ASSET_ROOT, "root", "asset"}:
        return EXPORT_MODE_ASSET_ROOT
    if value in {EXPORT_MODE_CURVE_ONLY, "curves", "strands", "strand_only"}:
        return EXPORT_MODE_CURVE_ONLY
    raise ValueError("Unsupported groom Alembic export mode: %s" % export_mode)


def _method_source(export_mode: str) -> str:
    if export_mode == EXPORT_MODE_CURVE_ONLY:
        return "Maya AbcExport over strand/guide curve roots only, excluding scalp mesh from the Groom cache"
    return "Maya AbcExport over public synthetic groom asset root"


def _l3_status(plugin: Dict[str, Any], export_mode: str) -> str:
    if not plugin.get("loadedAfter"):
        return "blocked_by_missing_maya_abc_export"
    if export_mode == EXPORT_MODE_CURVE_ONLY:
        return "maya_groom_curve_only_alembic_payload_exported"
    return "maya_groom_alembic_payload_exported"


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
