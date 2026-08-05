"""Link spatial sockets and Unreal runtime assets to gameplay attach readiness."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .contract import public_path, resolve_public_path


REPORT_VERSION = "unreal-gameplay-attach-fixture@0.1.0"
MANIFEST_SCHEMA = "synthetic-gameplay-attach-manifest@0.1.0"


def build_gameplay_attach_report(
    socket_artifact_path: str | Path,
    manifest_path: str | Path,
    runtime_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    socket_file = resolve_public_path(socket_artifact_path)
    manifest_file = resolve_public_path(manifest_path)
    socket_report = _read_json(socket_file)
    manifest = _read_json(manifest_file)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError("Unsupported gameplay attach manifest schema: %s" % manifest.get("schema"))
    runtime_snapshot = runtime_snapshot or _empty_runtime_snapshot()
    facts = _build_facts(socket_report, manifest, runtime_snapshot)
    rows = _evaluate(facts, socket_report, runtime_snapshot)
    summary = _summary(facts, rows, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    blocked_reason = runtime.get("blockedReason")
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Import Checker",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-linked" if executed and socket_report.get("evidenceLevel") == "L3" else "Blocked",
        "l3Status": blocked_reason or "unreal_gameplay_attach_fixture_linked",
        "sourceSocketImportChecker": {
            "path": public_path(socket_file),
            "reportVersion": socket_report.get("reportVersion"),
            "evidenceLevel": socket_report.get("evidenceLevel"),
            "l3Status": socket_report.get("l3Status"),
            "gate": socket_report.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "gameplayAttachManifest": {
            "path": public_path(manifest_file),
            "schema": manifest.get("schema"),
            "packageId": manifest.get("packageId"),
            "packageVersion": manifest.get("packageVersion"),
        },
        "unrealRuntime": runtime,
        "facts": facts,
        "evaluation": {
            "schema": "unreal-gameplay-attach-fixture-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "unreal-gameplay-attach-fixture",
            "name": "Unreal Gameplay Attach Fixture",
            "methodSource": "Maya spatial authoring + Unreal socket runtime facts + gameplay attach manifest",
            "protocolCarrier": "socket names, hotspot semantics, attachable asset paths, animation context and attach policy",
            "boundary": {
                "mutation": "read_only_runtime_join",
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "none"),
            },
        },
        "reviewerClaims": _reviewer_claims(summary),
    }


def _build_facts(
    socket_report: Dict[str, Any],
    manifest: Dict[str, Any],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    source_assets = {
        str(row.get("assetId")): row
        for row in socket_report.get("facts", {}).get("assets", [])
    }
    runtime_assets = runtime_snapshot.get("facts", {}).get("assetsByPath", {})
    intents = []
    for intent in manifest.get("intents", []):
        asset_id = str(intent.get("assetId"))
        source_asset = source_assets.get(asset_id, {})
        normalized = source_asset.get("normalized", {})
        source_hotspots = list(source_asset.get("sourceHotspots", []))
        required_sockets = [str(name) for name in intent.get("requiredSocketNames", [])]
        required_semantics = [str(value) for value in intent.get("requiredHotspotSemantics", [])]
        runtime_socket_names = set(str(name) for name in normalized.get("runtime.socketNames", []))
        hotspot_semantics = set(str(row.get("semantic")) for row in source_hotspots if row.get("semantic"))
        animation_paths = [str(path) for path in intent.get("animationAssetPaths", [])]
        attachable_path = str(intent.get("attachablePath") or "")
        intents.append(
            {
                "id": intent.get("id"),
                "assetId": asset_id,
                "assetLabel": source_asset.get("assetLabel"),
                "slotRole": intent.get("slotRole"),
                "ownerState": intent.get("ownerState"),
                "attachablePath": attachable_path,
                "attachableRuntime": runtime_assets.get(attachable_path, {}),
                "animationAssetPaths": animation_paths,
                "animationRuntime": {path: runtime_assets.get(path, {}) for path in animation_paths},
                "requiredSocketNames": required_sockets,
                "requiredHotspotSemantics": required_semantics,
                "sourceStatus": source_asset.get("sourceStatus"),
                "sourceOwnerState": source_asset.get("ownerState"),
                "sourceHotspots": source_hotspots,
                "runtimeSocketNames": sorted(runtime_socket_names),
                "missingRuntimeSockets": sorted(set(required_sockets) - runtime_socket_names),
                "hotspotSemantics": sorted(hotspot_semantics),
                "missingHotspotSemantics": sorted(set(required_semantics) - hotspot_semantics),
                "parentMismatches": list(normalized.get("runtime.parentMismatches", [])),
                "socketApiReady": bool(normalized.get("runtime.socketApiReady")),
                "skeletalTargetPresent": bool(normalized.get("runtime.skeletalMeshExists") and normalized.get("runtime.skeletonExists")),
                "attachPolicy": intent.get("attachPolicy", {}),
            }
        )
    return {
        "schema": "unreal-gameplay-attach-fixture-input@0.1.0",
        "sourceSocketReportVersion": socket_report.get("reportVersion"),
        "sourceSocketEvidenceLevel": socket_report.get("evidenceLevel"),
        "sourceSocketL3Status": socket_report.get("l3Status"),
        "manifestPackageId": manifest.get("packageId"),
        "manifestPackageVersion": manifest.get("packageVersion"),
        "runtimeCollected": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "intents": intents,
    }


def _evaluate(
    facts: Dict[str, Any],
    socket_report: Dict[str, Any],
    runtime_snapshot: Dict[str, Any],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    runtime = runtime_snapshot.get("runtime", {})
    api = runtime.get("api", {})
    for intent in facts.get("intents", []):
        rows.extend(
            [
                _row(intent, "source-socket-l3", socket_report.get("evidenceLevel") == "L3", "error", "source evidence=%s status=%s" % (socket_report.get("evidenceLevel"), socket_report.get("l3Status")), "Run the Unreal Socket Import Checker L3 probe first."),
                _row(intent, "unreal-runtime-probe", bool(runtime.get("executed")), "error", "executed=%s engine=%s" % (runtime.get("executed"), runtime.get("engineVersion")), "Run the gameplay attach fixture through UnrealEditor-Cmd."),
                _row(intent, "gameplay-attach-api-visible", _attach_api_ready(api), "warning", "api=%s" % api.get("classes", {}), "Review Unreal Python attach API visibility before claiming attach execution."),
                _row(intent, "source-spatial-row-approved", intent.get("sourceStatus") == "Ready" and intent.get("sourceOwnerState") == "approved" and intent.get("ownerState") == "approved", "error", "sourceStatus=%s sourceOwner=%s manifestOwner=%s" % (intent.get("sourceStatus"), intent.get("sourceOwnerState"), intent.get("ownerState")), "Resolve source spatial owner actions before gameplay attach readiness."),
                _row(intent, "skeletal-target-present", bool(intent.get("skeletalTargetPresent")), "error", "skeletalTargetPresent=%s" % intent.get("skeletalTargetPresent"), "Import or relink the public SkeletalMesh/Skeleton target."),
                _row(intent, "attachable-asset-present", bool(intent.get("attachableRuntime", {}).get("exists")), "error", "attachable=%s exists=%s class=%s" % (intent.get("attachablePath"), intent.get("attachableRuntime", {}).get("exists"), intent.get("attachableRuntime", {}).get("class")), "Import or relink the gameplay attachable asset before runtime approval."),
                _row(intent, "required-sockets-present", not intent.get("missingRuntimeSockets"), "error", "required=%s runtime=%s missing=%s" % (",".join(intent.get("requiredSocketNames", [])), ",".join(intent.get("runtimeSocketNames", [])), ",".join(intent.get("missingRuntimeSockets", []))), "Create or import required sockets before gameplay attach."),
                _row(intent, "socket-parent-binding-clean", not intent.get("parentMismatches") and not intent.get("missingRuntimeSockets"), "error", "parentMismatches=%s missing=%s" % (intent.get("parentMismatches"), intent.get("missingRuntimeSockets")), "Bind sockets to the expected Skeleton bones before gameplay attach."),
                _row(intent, "required-hotspot-semantics", not intent.get("missingHotspotSemantics"), "warning", "required=%s source=%s missing=%s" % (",".join(intent.get("requiredHotspotSemantics", [])), ",".join(intent.get("hotspotSemantics", [])), ",".join(intent.get("missingHotspotSemantics", []))), "Assign required gameplay/VFX hotspot semantics or add an owner waiver."),
                _row(intent, "animation-context-present", _all_runtime_assets_present(intent.get("animationRuntime", {})), "warning", "animations=%s" % _runtime_asset_evidence(intent.get("animationRuntime", {})), "Import expected animation context or hold attach review."),
                _row(intent, "write-boundary-clean", runtime.get("assetWrites", 0) == 0 and runtime.get("engineWrites", 0) == 0 and runtime.get("productionWrites", 0) == 0, "error", "assetWrites=%s engineWrites=%s productionWrites=%s" % (runtime.get("assetWrites", 0), runtime.get("engineWrites", 0), runtime.get("productionWrites", 0)), "Keep gameplay attach fixture read-only."),
            ]
        )
    return rows


def _summary(
    facts: Dict[str, Any],
    rows: Iterable[Dict[str, Any]],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    row_list = list(rows)
    intents = list(facts.get("intents", []))
    intent_ids = sorted({str(row.get("intentId")) for row in row_list})
    blocked = sorted({str(row.get("intentId")) for row in row_list if row.get("status") == "error"})
    review = sorted({str(row.get("intentId")) for row in row_list if row.get("status") == "warning"} - set(blocked))
    ready = sorted(set(intent_ids) - set(blocked) - set(review))
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "intentCount": len(intent_ids),
        "readyIntents": len(ready),
        "reviewIntents": len(review),
        "blockedIntents": len(blocked),
        "requiredSockets": sum(len(intent.get("requiredSocketNames", [])) for intent in intents),
        "missingRuntimeSockets": sum(len(intent.get("missingRuntimeSockets", [])) for intent in intents),
        "requiredHotspots": sum(len(intent.get("requiredHotspotSemantics", [])) for intent in intents),
        "missingHotspotSemantics": sum(len(intent.get("missingHotspotSemantics", [])) for intent in intents),
        "attachableAssetsPresent": sum(1 for intent in intents if intent.get("attachableRuntime", {}).get("exists")),
        "animationAssetsPresent": sum(
            1
            for intent in intents
            for row in intent.get("animationRuntime", {}).values()
            if row.get("exists")
        ),
        "runtimeCollected": bool(runtime.get("executed")),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "assetWrites": runtime.get("assetWrites", 0),
        "engineWrites": runtime.get("engineWrites", 0),
        "productionWrites": runtime.get("productionWrites", 0),
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    owner_by_rule = {
        "source-socket-l3": "engine-ta",
        "unreal-runtime-probe": "engine-ta",
        "gameplay-attach-api-visible": "engine-ta",
        "source-spatial-row-approved": "spatial-owner",
        "skeletal-target-present": "engine-ta",
        "attachable-asset-present": "content-owner",
        "required-sockets-present": "engine-ta",
        "socket-parent-binding-clean": "technical-animation-owner",
        "required-hotspot-semantics": "gameplay-vfx-owner",
        "animation-context-present": "animation-owner",
        "write-boundary-clean": "tool-ta",
    }
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        actions.append(
            {
                "id": "gameplay-attach-action:%s" % row.get("id"),
                "intentId": row.get("intentId"),
                "assetId": row.get("assetId"),
                "ruleId": row.get("ruleId"),
                "status": row.get("status"),
                "owner": owner_by_rule.get(row.get("ruleId"), "tool-ta"),
                "preview": row.get("fixPreview"),
                "writeBoundary": "preview_only",
            }
        )
    return actions


def _row(
    intent: Dict[str, Any],
    rule_id: str,
    passed: bool,
    fail_status: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (intent.get("id"), rule_id),
        "intentId": intent.get("id"),
        "assetId": intent.get("assetId"),
        "slotRole": intent.get("slotRole"),
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _attach_api_ready(api: Dict[str, Any]) -> bool:
    classes = api.get("classes", {})
    method_count = len(api.get("actorAttachMethods", [])) + len(api.get("sceneComponentAttachMethods", []))
    return bool(classes.get("Actor") and classes.get("SceneComponent") and method_count)


def _all_runtime_assets_present(rows: Dict[str, Dict[str, Any]]) -> bool:
    return bool(rows) and all(row.get("exists") for row in rows.values())


def _runtime_asset_evidence(rows: Dict[str, Dict[str, Any]]) -> str:
    return ",".join("%s:%s" % (path, row.get("exists")) for path, row in rows.items())


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    return [
        "R54 links Maya spatial socket/hotspot authoring to Unreal socket runtime facts and gameplay attach intent rows.",
        "The fixture checks attachable asset presence, required socket coverage, socket parent binding, hotspot semantics and animation context before gameplay attach approval.",
        "The report is read-only: assetWrites, engineWrites and productionWrites remain zero.",
        "Blocked attach rows explain gameplay risk directly: an equip action can fail even when the prop asset exists if the character socket contract is missing.",
    ]


def _empty_runtime_snapshot() -> Dict[str, Any]:
    return {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "blockedReason": "blocked_by_missing_unreal_runtime",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "facts": {"assetsByPath": {}},
    }


def _read_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object: %s" % path)
    return data
