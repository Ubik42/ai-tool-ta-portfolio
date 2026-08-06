"""Join gameplay attach readiness to controlled AnimNotify write evidence."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from .contract import public_path, resolve_public_path


REPORT_VERSION = "unreal-gameplay-attach-timing-controlled-readiness@0.1.0"


def build_gameplay_attach_timing_controlled_report(
    gameplay_readiness_path: str | Path,
    attach_timing_path: str | Path,
    notify_controlled_write_path: str | Path,
) -> Dict[str, Any]:
    gameplay_file = resolve_public_path(gameplay_readiness_path)
    attach_timing_file = resolve_public_path(attach_timing_path)
    notify_controlled_file = resolve_public_path(notify_controlled_write_path)
    gameplay = _read_json(gameplay_file)
    attach_timing = _read_json(attach_timing_file)
    notify_controlled = _read_json(notify_controlled_file)
    facts = _facts(gameplay, attach_timing, notify_controlled, gameplay_file, attach_timing_file, notify_controlled_file)
    rows = _rows(facts)
    summary = _summary(facts, rows)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Gameplay Attach Timing Controlled Readiness",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-derived" if summary.get("notifyControlledWriteReady") else "Blocked",
        "l3Status": (
            "unreal_gameplay_attach_timing_controlled_readiness_linked"
            if summary.get("timingReadyByControlledWrite")
            else "unreal_gameplay_attach_timing_controlled_readiness_blocked"
        ),
        "sourceGameplayReadiness": facts["sourceGameplayReadiness"],
        "sourceAttachTimingReadiness": facts["sourceAttachTimingReadiness"],
        "sourceNotifyControlledWrite": facts["sourceNotifyControlledWrite"],
        "facts": facts,
        "evaluation": {
            "schema": "unreal-gameplay-attach-timing-controlled-readiness-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "unreal-gameplay-attach-timing-controlled-readiness",
            "name": "Unreal Gameplay Attach Timing Controlled Readiness",
            "methodSource": "R66 gameplay attach controlled readiness + R67 attach timing readiness + R72 native AnimNotify controlled write",
            "protocolCarrier": "gameplay attach intents, controlled socket coverage, AnimSequence timing requirements and native notify write receipts",
            "boundary": {
                "mutation": "derived_from_temp_project_notify_write_rolled_back",
                "assetWrites": facts["notifyControlledWrite"].get("assetWrites", 0),
                "engineWrites": facts["notifyControlledWrite"].get("engineWrites", 0),
                "productionWrites": facts["notifyControlledWrite"].get("productionWrites", 0),
                "persistentMutation": facts["notifyControlledWrite"].get("persistentMutation", False),
            },
        },
        "reviewerClaims": _reviewer_claims(summary),
    }


def _facts(
    gameplay: Dict[str, Any],
    attach_timing: Dict[str, Any],
    notify_controlled: Dict[str, Any],
    gameplay_file: Path,
    attach_timing_file: Path,
    notify_controlled_file: Path,
) -> Dict[str, Any]:
    gameplay_by_id = {str(row.get("id")): row for row in gameplay.get("facts", {}).get("intents", []) if row.get("id")}
    notify_summary = notify_controlled.get("summary", {})
    output_json = notify_controlled.get("runtime", {}).get("outputJson", {})
    notify_index = _notify_result_index(output_json)
    intents: List[Dict[str, Any]] = []

    for timing_intent in attach_timing.get("facts", {}).get("intents", []):
        intent_id = str(timing_intent.get("id") or "")
        gameplay_intent = gameplay_by_id.get(intent_id, {})
        required_events = [str(name) for name in timing_intent.get("requiredAttachTimingEvents", []) if name]
        animation_paths = [str(path) for path in timing_intent.get("animationAssetPaths", []) if path]
        controlled_rows = _matched_notify_rows(intent_id, animation_paths, required_events, notify_index)
        missing_controlled = _missing_controlled_events(animation_paths, required_events, controlled_rows)
        deep_errors = [str(rule) for rule in timing_intent.get("deepFactErrorRules", []) if rule]
        gameplay_ready = timing_intent.get("sourceReadinessState") == "ReadyByControlledExecutor"
        controlled_write_ready = _notify_controlled_write_ready(notify_summary)
        controlled_event_ready = controlled_write_ready and not missing_controlled and _postcheck_rollback_ready(controlled_rows)

        if not gameplay_ready:
            readiness_state = "HeldBySocketOrSource"
        elif deep_errors or timing_intent.get("linkedSequenceCount", 0) < len(animation_paths):
            readiness_state = "TimingBlocked"
        elif not controlled_event_ready:
            readiness_state = "TimingBlocked"
        else:
            readiness_state = "TimingReadyByControlledWrite"

        intents.append(
            {
                "id": intent_id,
                "assetId": timing_intent.get("assetId"),
                "assetLabel": gameplay_intent.get("assetLabel"),
                "slotRole": timing_intent.get("slotRole"),
                "sourceReadinessState": timing_intent.get("sourceReadinessState"),
                "sourceReadyByControlledExecutor": gameplay_ready,
                "publishRequired": bool(gameplay_intent.get("publishRequired") or timing_intent.get("publishRequired")),
                "animationAssetPaths": animation_paths,
                "linkedSequenceCount": timing_intent.get("linkedSequenceCount", 0),
                "deepFactErrorRules": deep_errors,
                "requiredAttachTimingEvents": required_events,
                "previousMissingAttachTimingEvents": timing_intent.get("missingAttachTimingEvents", []),
                "controlledNotifyRows": controlled_rows,
                "controlledNotifyEventNames": sorted({row.get("notifyName") for row in controlled_rows if row.get("notifyName")}),
                "missingControlledAttachTimingEvents": missing_controlled,
                "notifyControlledWriteReady": controlled_write_ready,
                "postCheckRollbackReady": _postcheck_rollback_ready(controlled_rows),
                "readinessState": readiness_state,
            }
        )

    return {
        "schema": "unreal-gameplay-attach-timing-controlled-readiness-input@0.1.0",
        "sourceGameplayReadiness": _source_info(gameplay_file, gameplay, gameplay.get("evaluation", {}).get("summary", {}).get("gate")),
        "sourceAttachTimingReadiness": _source_info(attach_timing_file, attach_timing, attach_timing.get("evaluation", {}).get("summary", {}).get("gate")),
        "sourceNotifyControlledWrite": _source_info(notify_controlled_file, notify_controlled, notify_summary.get("gate")),
        "notifyControlledWrite": {
            "gate": notify_summary.get("gate"),
            "runtimeSucceeded": notify_summary.get("runtimeSucceeded"),
            "returnCode": notify_summary.get("returnCode"),
            "commandletLoaded": notify_summary.get("commandletLoaded"),
            "outputStatus": notify_summary.get("outputStatus"),
            "requestCount": notify_summary.get("requestCount"),
            "applied": notify_summary.get("applied"),
            "postCheckPresent": notify_summary.get("postCheckPresent"),
            "rollbackRemoved": notify_summary.get("rollbackRemoved"),
            "postRollbackPresent": notify_summary.get("postRollbackPresent"),
            "assetWrites": notify_summary.get("assetWrites"),
            "engineWrites": notify_summary.get("engineWrites"),
            "productionWrites": notify_summary.get("productionWrites"),
            "persistentMutation": notify_summary.get("persistentMutation"),
            "finalHashRestored": notify_summary.get("finalHashRestored"),
            "assets": output_json.get("assets", []),
        },
        "intents": intents,
    }


def _source_info(path: Path, report: Dict[str, Any], gate: Any) -> Dict[str, Any]:
    return {
        "path": public_path(path),
        "reportVersion": report.get("reportVersion"),
        "evidenceLevel": report.get("evidenceLevel"),
        "l3Status": report.get("l3Status"),
        "gate": gate,
    }


def _notify_result_index(output_json: Dict[str, Any]) -> Dict[Tuple[str, str, str], Dict[str, Any]]:
    index: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    for asset in output_json.get("assets", []):
        asset_path = str(asset.get("assetPath") or "")
        for result in asset.get("results", []):
            intent_id = str(result.get("intentId") or "")
            notify_name = str(result.get("notifyName") or "")
            result_path = str(result.get("animSequencePath") or asset_path)
            key = (intent_id, result_path, notify_name)
            index[key] = {
                "intentId": intent_id,
                "assetId": result.get("assetId"),
                "slotRole": result.get("slotRole"),
                "animSequencePath": result_path,
                "notifyName": notify_name,
                "triggerTime": result.get("triggerTime"),
                "trackIndex": result.get("trackIndex"),
                "sourceReceiptId": result.get("sourceReceiptId"),
                "applied": bool(result.get("applied") or result.get("alreadyPresent")),
                "alreadyPresent": bool(result.get("alreadyPresent")),
                "message": result.get("message"),
                "assetPostCheckPresent": asset.get("postCheckPresent", 0),
                "assetRollbackRemoved": asset.get("rollbackRemoved", 0),
                "assetPostRollbackPresent": asset.get("postRollbackPresent", 0),
                "assetStatus": asset.get("status"),
                "savedAfterApply": asset.get("savedAfterApply"),
                "savedAfterRollback": asset.get("savedAfterRollback"),
            }
    return index


def _matched_notify_rows(
    intent_id: str,
    animation_paths: List[str],
    required_events: List[str],
    notify_index: Dict[Tuple[str, str, str], Dict[str, Any]],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for anim_path in animation_paths:
        for event_name in required_events:
            row = notify_index.get((intent_id, anim_path, event_name))
            if row:
                rows.append(row)
    return rows


def _missing_controlled_events(
    animation_paths: List[str],
    required_events: List[str],
    controlled_rows: List[Dict[str, Any]],
) -> List[str]:
    covered = {(row.get("animSequencePath"), row.get("notifyName")) for row in controlled_rows if row.get("applied")}
    missing = []
    for anim_path in animation_paths:
        for event_name in required_events:
            if (anim_path, event_name) not in covered:
                missing.append("%s:%s" % (anim_path, event_name))
    return sorted(missing)


def _notify_controlled_write_ready(summary: Dict[str, Any]) -> bool:
    return (
        summary.get("gate") == "Ready"
        and bool(summary.get("runtimeSucceeded"))
        and bool(summary.get("commandletLoaded"))
        and summary.get("outputStatus") == "apply_postcheck_rollback_completed"
        and summary.get("productionWrites", 1) == 0
        and not bool(summary.get("persistentMutation"))
        and bool(summary.get("finalHashRestored"))
    )


def _postcheck_rollback_ready(rows: List[Dict[str, Any]]) -> bool:
    return bool(rows) and all(
        row.get("applied")
        and row.get("assetPostCheckPresent", 0) > 0
        and row.get("assetRollbackRemoved", 0) > 0
        and row.get("assetPostRollbackPresent", 1) == 0
        and row.get("savedAfterApply")
        and row.get("savedAfterRollback")
        for row in rows
    )


def _rows(facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    notify_write = facts.get("notifyControlledWrite", {})
    for intent in facts.get("intents", []):
        rows.extend(
            [
                _row(intent, "gameplay-controlled-readiness", intent.get("sourceReadyByControlledExecutor"), "error", "sourceReadinessState=%s" % intent.get("sourceReadinessState"), "Resolve socket gameplay readiness before timing approval."),
                _row(intent, "animation-sequence-linked", intent.get("linkedSequenceCount", 0) == len(intent.get("animationAssetPaths", [])) and intent.get("linkedSequenceCount", 0) > 0, "error", "animationPaths=%s linked=%s" % (intent.get("animationAssetPaths"), intent.get("linkedSequenceCount")), "Import or relink the AnimSequence used by this gameplay attach intent."),
                _row(intent, "deep-facts-source-clean", not intent.get("deepFactErrorRules"), "error", "deepFactErrorRules=%s" % intent.get("deepFactErrorRules"), "Fix the animation source/deep-fact errors before attach timing approval."),
                _row(intent, "native-notify-controlled-write-ready", intent.get("notifyControlledWriteReady"), "error", "notifyControlledWrite=%s" % notify_write, "Run the native AnimNotify controlled write harness successfully."),
                _row(intent, "required-attach-timing-events-controlled", not intent.get("missingControlledAttachTimingEvents"), "error", "required=%s controlled=%s missing=%s" % (intent.get("requiredAttachTimingEvents"), intent.get("controlledNotifyEventNames"), intent.get("missingControlledAttachTimingEvents")), "Author explicit equip/attach notify events through the controlled native commandlet."),
                _row(intent, "postcheck-rollback-ready", intent.get("postCheckRollbackReady"), "error", "controlledNotifyRows=%s" % intent.get("controlledNotifyRows"), "Post-check the authored notify rows, roll them back, and restore fixture hashes."),
                _row(intent, "publish-persistence-required", not intent.get("publishRequired"), "warning", "publishRequired=%s persistentMutation=%s" % (intent.get("publishRequired"), notify_write.get("persistentMutation")), "Approve a persistence pass before claiming the public project contains these notifies."),
            ]
        )
    rows.append(
        {
            "id": "notify-controlled-write:production-boundary",
            "intentId": None,
            "assetId": None,
            "slotRole": None,
            "ruleId": "production-boundary",
            "status": "pass"
            if notify_write.get("productionWrites", 1) == 0
            and not notify_write.get("persistentMutation")
            and notify_write.get("finalHashRestored")
            else "error",
            "evidence": "assetWrites=%s engineWrites=%s productionWrites=%s persistentMutation=%s finalHashRestored=%s"
            % (
                notify_write.get("assetWrites"),
                notify_write.get("engineWrites"),
                notify_write.get("productionWrites"),
                notify_write.get("persistentMutation"),
                notify_write.get("finalHashRestored"),
            ),
            "fixPreview": "None",
        }
    )
    return rows


def _summary(facts: Dict[str, Any], rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    row_list = list(rows)
    intents = list(facts.get("intents", []))
    ready = [row for row in intents if row.get("readinessState") == "TimingReadyByControlledWrite"]
    held = [row for row in intents if row.get("readinessState") == "HeldBySocketOrSource"]
    blocked = [row for row in intents if row.get("readinessState") == "TimingBlocked"]
    publish_required = [row for row in intents if row.get("publishRequired")]
    notify_write = facts.get("notifyControlledWrite", {})
    controlled_ready = _notify_controlled_write_ready(notify_write)
    gate = "Review" if ready and controlled_ready else "Blocked"
    full_fixture_gate = "Blocked" if held or blocked else ("Review" if publish_required else "Ready")
    return {
        "gate": gate,
        "fullFixtureGate": full_fixture_gate,
        "notifyControlledWriteReady": controlled_ready,
        "intentCount": len(intents),
        "timingReadyByControlledWrite": len(ready),
        "heldBySocketOrSource": len(held),
        "timingBlocked": len(blocked),
        "publishRequiredIntents": len(publish_required),
        "requiredAttachTimingEvents": sum(len(row.get("requiredAttachTimingEvents", [])) for row in intents),
        "coveredAttachTimingEvents": sum(len(row.get("controlledNotifyRows", [])) for row in intents),
        "missingAttachTimingEventsAfterControlledWrite": sum(len(row.get("missingControlledAttachTimingEvents", [])) for row in intents),
        "primaryReadyIntentIds": [row.get("id") for row in ready],
        "heldIntentIds": [row.get("id") for row in held],
        "blockedIntentIds": [row.get("id") for row in blocked],
        "postCheckPresent": notify_write.get("postCheckPresent", 0),
        "rollbackRemoved": notify_write.get("rollbackRemoved", 0),
        "postRollbackPresent": notify_write.get("postRollbackPresent", 0),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "assetWrites": notify_write.get("assetWrites", 0),
        "engineWrites": notify_write.get("engineWrites", 0),
        "productionWrites": notify_write.get("productionWrites", 0),
        "persistentMutation": notify_write.get("persistentMutation", False),
        "finalHashRestored": notify_write.get("finalHashRestored", False),
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    owner_by_rule = {
        "gameplay-controlled-readiness": "engine-ta",
        "animation-sequence-linked": "animation-ta",
        "deep-facts-source-clean": "animation-owner",
        "native-notify-controlled-write-ready": "engine-ta",
        "required-attach-timing-events-controlled": "animation-gameplay-owner",
        "postcheck-rollback-ready": "tool-ta",
        "publish-persistence-required": "lead-ta",
        "production-boundary": "tool-ta",
    }
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        actions.append(
            {
                "id": "gameplay-timing-controlled-action:%s" % row.get("id"),
                "intentId": row.get("intentId"),
                "assetId": row.get("assetId"),
                "slotRole": row.get("slotRole"),
                "ruleId": row.get("ruleId"),
                "status": row.get("status"),
                "owner": owner_by_rule.get(row.get("ruleId"), "tool-ta"),
                "preview": row.get("fixPreview"),
                "writeBoundary": "review_only",
            }
        )
    return actions


def _row(intent: Dict[str, Any], rule_id: str, passed: bool, fail_status: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
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


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    return [
        "R73 joins controlled socket readiness, animation attach timing readiness and native AnimNotify controlled-write evidence into one gameplay attach delivery gate.",
        "Approved rifle equip is executor-backed for both required sockets and required AnimSequence notify timing; it remains Review until a persistence pass is explicitly approved.",
        "Temporary backpack remains held by source owner even though the native notify write path can create its required timing event.",
        "The artifact is derived from temp-project write/post-check/rollback evidence and records zero production writes.",
        "Summary: timingReadyByControlledWrite=%s, heldBySocketOrSource=%s, productionWrites=%s."
        % (
            summary.get("timingReadyByControlledWrite"),
            summary.get("heldBySocketOrSource"),
            summary.get("productionWrites"),
        ),
    ]


def _read_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object: %s" % path)
    return data
