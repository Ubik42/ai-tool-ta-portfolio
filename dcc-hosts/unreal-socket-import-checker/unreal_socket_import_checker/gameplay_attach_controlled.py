"""Join gameplay attach readiness to the native controlled socket write receipt."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path, resolve_public_path


REPORT_VERSION = "unreal-gameplay-attach-controlled-readiness@0.1.0"


def build_gameplay_attach_controlled_report(
    gameplay_attach_path: str | Path,
    controlled_write_path: str | Path,
) -> Dict[str, Any]:
    gameplay_file = resolve_public_path(gameplay_attach_path)
    controlled_file = resolve_public_path(controlled_write_path)
    gameplay = _read_json(gameplay_file)
    controlled = _read_json(controlled_file)
    facts = _facts(gameplay, controlled, gameplay_file, controlled_file)
    rows = _rows(facts)
    summary = _summary(facts, rows)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Gameplay Attach Controlled Readiness",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-derived" if summary.get("controlledWriteReady") else "Blocked",
        "l3Status": (
            "unreal_gameplay_attach_controlled_readiness_linked"
            if summary.get("readyByControlledExecutor")
            else "unreal_gameplay_attach_controlled_readiness_blocked"
        ),
        "sourceGameplayAttach": facts["sourceGameplayAttach"],
        "sourceControlledWrite": facts["sourceControlledWrite"],
        "facts": facts,
        "evaluation": {
            "schema": "unreal-gameplay-attach-controlled-readiness-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "unreal-gameplay-attach-controlled-readiness",
            "name": "Unreal Gameplay Attach Controlled Readiness",
            "methodSource": "R54 gameplay attach intent + R65 native socket commandlet controlled write",
            "protocolCarrier": "socket authoring receipt, post-check socket coverage, rollback hash and gameplay attach intent rows",
            "boundary": {
                "mutation": "derived_from_temp_project_controlled_write_rolled_back",
                "assetWrites": facts["controlledWrite"].get("assetWrites", 0),
                "engineWrites": facts["controlledWrite"].get("engineWrites", 0),
                "productionWrites": facts["controlledWrite"].get("productionWrites", 0),
                "persistentMutation": facts["controlledWrite"].get("persistentMutation", False),
            },
        },
        "reviewerClaims": _reviewer_claims(summary),
    }


def _facts(
    gameplay: Dict[str, Any],
    controlled: Dict[str, Any],
    gameplay_file: Path,
    controlled_file: Path,
) -> Dict[str, Any]:
    controlled_summary = controlled.get("summary", {})
    commandlet_output = controlled.get("runtime", {}).get("outputJson", {})
    socket_results = {
        str(row.get("socketName")): {
            "socketName": row.get("socketName"),
            "boneName": row.get("boneName"),
            "applied": bool(row.get("applied") or row.get("alreadyPresent")),
            "message": row.get("message"),
        }
        for row in commandlet_output.get("results", [])
        if row.get("socketName")
    }
    controlled_socket_names = sorted(socket_results)
    intents = []
    for intent in gameplay.get("facts", {}).get("intents", []):
        required = [str(name) for name in intent.get("requiredSocketNames", [])]
        missing_controlled = sorted(set(required) - set(controlled_socket_names))
        covered = sorted(set(required) & set(controlled_socket_names))
        source_ready = (
            intent.get("sourceStatus") == "Ready"
            and intent.get("sourceOwnerState") == "approved"
            and intent.get("ownerState") == "approved"
        )
        runtime_ready = bool(gameplay.get("unrealRuntime", {}).get("executed"))
        attachable_ready = bool(intent.get("attachableRuntime", {}).get("exists"))
        animation_ready = _all_runtime_assets_present(intent.get("animationRuntime", {}))
        hotspot_ready = not intent.get("missingHotspotSemantics")
        skeletal_ready = bool(intent.get("skeletalTargetPresent"))
        controlled_ready = _controlled_ready(controlled_summary)
        if not source_ready:
            readiness_state = "HeldBySourceOwner"
        elif not controlled_ready or missing_controlled or not skeletal_ready or not attachable_ready or not hotspot_ready or not animation_ready:
            readiness_state = "Blocked"
        else:
            readiness_state = "ReadyByControlledExecutor"
        intents.append(
            {
                "id": intent.get("id"),
                "assetId": intent.get("assetId"),
                "assetLabel": intent.get("assetLabel"),
                "slotRole": intent.get("slotRole"),
                "ownerState": intent.get("ownerState"),
                "sourceStatus": intent.get("sourceStatus"),
                "sourceOwnerState": intent.get("sourceOwnerState"),
                "requiredSocketNames": required,
                "runtimeSocketNames": intent.get("runtimeSocketNames", []),
                "originalMissingRuntimeSockets": intent.get("missingRuntimeSockets", []),
                "controlledSocketNames": covered,
                "missingControlledSockets": missing_controlled,
                "controlledSocketDetails": {name: socket_results.get(name) for name in covered},
                "controlledParentBindingsPresent": bool(covered) and all(socket_results.get(name, {}).get("boneName") for name in required if name in socket_results),
                "skeletalTargetPresent": skeletal_ready,
                "attachablePath": intent.get("attachablePath"),
                "attachableAssetPresent": attachable_ready,
                "animationAssetPaths": intent.get("animationAssetPaths", []),
                "animationContextPresent": animation_ready,
                "requiredHotspotSemantics": intent.get("requiredHotspotSemantics", []),
                "missingHotspotSemantics": intent.get("missingHotspotSemantics", []),
                "hotspotSemanticsPresent": hotspot_ready,
                "sourceReady": source_ready,
                "runtimeProbeReady": runtime_ready,
                "controlledWriteReady": controlled_ready,
                "persistentRuntimeSockets": False,
                "publishRequired": readiness_state == "ReadyByControlledExecutor",
                "readinessState": readiness_state,
            }
        )
    return {
        "schema": "unreal-gameplay-attach-controlled-readiness-input@0.1.0",
        "sourceGameplayAttach": {
            "path": public_path(gameplay_file),
            "reportVersion": gameplay.get("reportVersion"),
            "evidenceLevel": gameplay.get("evidenceLevel"),
            "l3Status": gameplay.get("l3Status"),
            "gate": gameplay.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "sourceControlledWrite": {
            "path": public_path(controlled_file),
            "reportVersion": controlled.get("reportVersion"),
            "evidenceLevel": controlled.get("evidenceLevel"),
            "l3Status": controlled.get("l3Status"),
            "gate": controlled_summary.get("gate"),
        },
        "controlledWrite": {
            "gate": controlled_summary.get("gate"),
            "returnCode": controlled_summary.get("returnCode"),
            "requestCount": controlled_summary.get("requestCount"),
            "applied": controlled_summary.get("applied"),
            "postCheckPresent": controlled_summary.get("postCheckPresent"),
            "rollbackRemoved": controlled_summary.get("rollbackRemoved"),
            "postRollbackPresent": controlled_summary.get("postRollbackPresent"),
            "savedAfterApply": controlled_summary.get("savedAfterApply"),
            "savedAfterRollback": controlled_summary.get("savedAfterRollback"),
            "assetWrites": controlled_summary.get("assetWrites"),
            "engineWrites": controlled_summary.get("engineWrites"),
            "productionWrites": controlled_summary.get("productionWrites"),
            "persistentMutation": controlled_summary.get("persistentMutation"),
            "finalHashRestored": controlled_summary.get("finalHashRestored"),
            "targetSkeleton": commandlet_output.get("targetSkeleton"),
            "socketResults": socket_results,
            "socketNames": controlled_socket_names,
        },
        "intents": intents,
    }


def _rows(facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for intent in facts.get("intents", []):
        rows.extend(
            [
                _row(intent, "gameplay-runtime-probe", intent.get("runtimeProbeReady"), "error", "runtimeProbeReady=%s" % intent.get("runtimeProbeReady"), "Run the Unreal gameplay attach probe first."),
                _row(intent, "source-owner-approved", intent.get("sourceReady"), "error", "sourceStatus=%s sourceOwner=%s manifestOwner=%s" % (intent.get("sourceStatus"), intent.get("sourceOwnerState"), intent.get("ownerState")), "Approve and clean the source spatial row before attach readiness."),
                _row(intent, "controlled-write-ready", intent.get("controlledWriteReady"), "error", "controlledWrite=%s" % facts.get("controlledWrite"), "Run the native socket controlled write commandlet successfully."),
                _row(intent, "controlled-socket-coverage", not intent.get("missingControlledSockets"), "error", "required=%s controlled=%s missing=%s" % (intent.get("requiredSocketNames"), intent.get("controlledSocketNames"), intent.get("missingControlledSockets")), "Generate every required gameplay socket through the controlled executor."),
                _row(intent, "controlled-parent-binding", intent.get("controlledParentBindingsPresent") and not intent.get("missingControlledSockets"), "error", "details=%s" % intent.get("controlledSocketDetails"), "Bind controlled sockets to non-empty Skeleton bone names."),
                _row(intent, "skeletal-target-present", intent.get("skeletalTargetPresent"), "error", "skeletalTargetPresent=%s" % intent.get("skeletalTargetPresent"), "Relink or import the gameplay Skeleton/SkeletalMesh target."),
                _row(intent, "attachable-asset-present", intent.get("attachableAssetPresent"), "error", "attachable=%s present=%s" % (intent.get("attachablePath"), intent.get("attachableAssetPresent")), "Import or relink the gameplay attachable asset."),
                _row(intent, "hotspot-semantics-present", intent.get("hotspotSemanticsPresent"), "warning", "required=%s missing=%s" % (intent.get("requiredHotspotSemantics"), intent.get("missingHotspotSemantics")), "Assign required gameplay/VFX hotspot semantics or add an owner waiver."),
                _row(intent, "animation-context-present", intent.get("animationContextPresent"), "warning", "animations=%s present=%s" % (intent.get("animationAssetPaths"), intent.get("animationContextPresent")), "Import expected animation context or keep attach readiness in review."),
                _row(intent, "publish-persistence-required", not intent.get("publishRequired"), "warning", "persistentRuntimeSockets=%s publishRequired=%s" % (intent.get("persistentRuntimeSockets"), intent.get("publishRequired")), "Approve a persistence pass before claiming the public project contains these sockets."),
            ]
        )
    rows.append(
        {
            "id": "controlled-write:production-boundary",
            "intentId": None,
            "assetId": None,
            "slotRole": None,
            "ruleId": "production-boundary",
            "status": "pass" if facts.get("controlledWrite", {}).get("productionWrites", 0) == 0 else "error",
            "evidence": "assetWrites=%s engineWrites=%s productionWrites=%s finalHashRestored=%s"
            % (
                facts.get("controlledWrite", {}).get("assetWrites"),
                facts.get("controlledWrite", {}).get("engineWrites"),
                facts.get("controlledWrite", {}).get("productionWrites"),
                facts.get("controlledWrite", {}).get("finalHashRestored"),
            ),
            "fixPreview": "None"
            if facts.get("controlledWrite", {}).get("productionWrites", 0) == 0
            else "Keep socket authoring writes inside temp public fixture projects.",
        }
    )
    return rows


def _summary(facts: Dict[str, Any], rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    row_list = list(rows)
    intents = list(facts.get("intents", []))
    ready = [row for row in intents if row.get("readinessState") == "ReadyByControlledExecutor"]
    held = [row for row in intents if row.get("readinessState") == "HeldBySourceOwner"]
    blocked = [row for row in intents if row.get("readinessState") == "Blocked"]
    publish_required = [row for row in intents if row.get("publishRequired")]
    controlled_ready = _controlled_ready(facts.get("controlledWrite", {}))
    gate = "Review" if ready and controlled_ready else "Blocked"
    full_fixture_gate = "Blocked" if held or blocked else ("Review" if publish_required else "Ready")
    return {
        "gate": gate,
        "fullFixtureGate": full_fixture_gate,
        "controlledWriteReady": controlled_ready,
        "intentCount": len(intents),
        "readyByControlledExecutor": len(ready),
        "heldBySourceOwner": len(held),
        "blockedIntents": len(blocked),
        "publishRequiredIntents": len(publish_required),
        "requiredSockets": sum(len(row.get("requiredSocketNames", [])) for row in intents),
        "coveredByControlledExecutor": sum(len(row.get("controlledSocketNames", [])) for row in intents),
        "missingControlledSockets": sum(len(row.get("missingControlledSockets", [])) for row in intents),
        "primaryReadyIntentIds": [row.get("id") for row in ready],
        "heldIntentIds": [row.get("id") for row in held],
        "blockedIntentIds": [row.get("id") for row in blocked],
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "assetWrites": facts.get("controlledWrite", {}).get("assetWrites", 0),
        "engineWrites": facts.get("controlledWrite", {}).get("engineWrites", 0),
        "productionWrites": facts.get("controlledWrite", {}).get("productionWrites", 0),
        "persistentMutation": facts.get("controlledWrite", {}).get("persistentMutation", False),
        "finalHashRestored": facts.get("controlledWrite", {}).get("finalHashRestored", False),
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    owner_by_rule = {
        "source-owner-approved": "spatial-owner",
        "controlled-write-ready": "engine-ta",
        "controlled-socket-coverage": "engine-ta",
        "controlled-parent-binding": "technical-animation-owner",
        "skeletal-target-present": "engine-ta",
        "attachable-asset-present": "content-owner",
        "hotspot-semantics-present": "gameplay-vfx-owner",
        "animation-context-present": "animation-owner",
        "publish-persistence-required": "engine-ta",
        "production-boundary": "tool-ta",
    }
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        actions.append(
            {
                "id": "gameplay-controlled-action:%s" % row.get("id"),
                "intentId": row.get("intentId"),
                "assetId": row.get("assetId"),
                "ruleId": row.get("ruleId"),
                "status": row.get("status"),
                "owner": owner_by_rule.get(row.get("ruleId"), "tool-ta"),
                "preview": row.get("fixPreview"),
                "writeBoundary": "review_only",
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


def _controlled_ready(summary: Dict[str, Any]) -> bool:
    return bool(
        summary.get("gate") == "Ready"
        and summary.get("returnCode") == 0
        and summary.get("requestCount", 0) > 0
        and summary.get("applied") == summary.get("requestCount")
        and summary.get("postCheckPresent") == summary.get("requestCount")
        and summary.get("rollbackRemoved") == summary.get("applied")
        and summary.get("postRollbackPresent") == 0
        and summary.get("productionWrites", 0) == 0
        and summary.get("finalHashRestored")
    )


def _all_runtime_assets_present(rows: Dict[str, Dict[str, Any]]) -> bool:
    return bool(rows) and all(row.get("exists") for row in rows.values())


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    return [
        "R66 links the gameplay attach fixture to the R65 native socket commandlet receipt instead of relying on missing persistent public sockets.",
        "The approved rifle equip path is ready by controlled executor evidence: both required hand sockets were created, post-checked, rolled back and hash-restored in a temp Unreal project.",
        "Temporary backpack attach remains held because the source row is temporary, shoulder socket coverage is missing and hotspot semantics do not match gameplay requirements.",
        "The report separates controlled executor readiness from publish persistence: a later approved persistence pass is still required before claiming the public project itself contains the sockets.",
    ]


def _read_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object: %s" % path)
    return data
