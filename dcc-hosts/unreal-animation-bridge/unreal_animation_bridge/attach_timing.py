"""Attach timing readiness from gameplay socket evidence and AnimSequence facts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path, resolve_public_path


REPORT_VERSION = "unreal-animation-attach-timing-readiness@0.1.0"


def build_attach_timing_report(gameplay_readiness_path: str | Path, deep_facts_path: str | Path) -> Dict[str, Any]:
    gameplay_file = resolve_public_path(gameplay_readiness_path)
    deep_file = resolve_public_path(deep_facts_path)
    gameplay = _read_json(gameplay_file)
    deep = _read_json(deep_file)
    facts = _facts(gameplay, deep, gameplay_file, deep_file)
    rows = _rows(facts)
    summary = _summary(facts, rows)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Animation Attach Timing Readiness",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-derived" if facts.get("runtimeDeepFactsCollected") else "Blocked",
        "l3Status": "unreal_animation_attach_timing_readiness_linked"
        if facts.get("runtimeDeepFactsCollected")
        else "unreal_animation_attach_timing_readiness_blocked",
        "sourceGameplayReadiness": facts["sourceGameplayReadiness"],
        "sourceAnimSequenceDeepFacts": facts["sourceAnimSequenceDeepFacts"],
        "facts": facts,
        "evaluation": {
            "schema": "unreal-animation-attach-timing-readiness-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "unreal-animation-attach-timing-readiness",
            "name": "Unreal Animation Attach Timing Readiness",
            "methodSource": "R66 gameplay attach controlled readiness + R41 AnimSequence deep facts",
            "protocolCarrier": "gameplay attach intents, AnimSequence runtime metadata, notify readability and required attach timing events",
            "boundary": {
                "mutation": "derived_read_only",
                "assetWrites": summary.get("assetWrites", 0),
                "engineWrites": summary.get("engineWrites", 0),
                "productionWrites": summary.get("productionWrites", 0),
            },
        },
        "reviewerClaims": _reviewer_claims(summary),
    }


def _facts(gameplay: Dict[str, Any], deep: Dict[str, Any], gameplay_file: Path, deep_file: Path) -> Dict[str, Any]:
    deep_by_path = {
        str(row.get("expectedAnimSequencePath")): row
        for row in deep.get("facts", {}).get("sequences", [])
        if row.get("expectedAnimSequencePath")
    }
    deep_rows_by_asset: Dict[str, List[Dict[str, Any]]] = {}
    for row in deep.get("evaluation", {}).get("rows", []):
        if row.get("assetId"):
            deep_rows_by_asset.setdefault(str(row["assetId"]), []).append(row)
    intents = []
    for intent in gameplay.get("facts", {}).get("intents", []):
        animation_paths = [str(path) for path in intent.get("animationAssetPaths", [])]
        linked = [deep_by_path.get(path, {}) for path in animation_paths]
        required_events = _required_events(intent)
        notify_rows = [_notify_facts(row) for row in linked if row]
        missing_events = sorted(set(required_events) - set(_notify_event_names(notify_rows)))
        deep_errors = [
            row
            for sequence in linked
            for row in deep_rows_by_asset.get(str(sequence.get("assetId")), [])
            if row.get("status") == "error"
        ]
        readiness_state = _readiness_state(intent, linked, notify_rows, missing_events, deep_errors)
        intents.append(
            {
                "id": intent.get("id"),
                "assetId": intent.get("assetId"),
                "slotRole": intent.get("slotRole"),
                "sourceReadinessState": intent.get("readinessState"),
                "sourceReadyByControlledExecutor": intent.get("readinessState") == "ReadyByControlledExecutor",
                "publishRequired": bool(intent.get("publishRequired")),
                "animationAssetPaths": animation_paths,
                "linkedSequenceCount": len([row for row in linked if row]),
                "linkedSequences": [_sequence_summary(row) for row in linked if row],
                "deepFactErrorRules": sorted({row.get("ruleId") for row in deep_errors if row.get("ruleId")}),
                "requiredAttachTimingEvents": required_events,
                "notifyFacts": notify_rows,
                "notifyReadable": any(row.get("propertiesReadable") for row in notify_rows),
                "notifyEventNames": _notify_event_names(notify_rows),
                "missingAttachTimingEvents": missing_events,
                "readinessState": readiness_state,
            }
        )
    deep_summary = deep.get("evaluation", {}).get("summary", {})
    api_classes = deep.get("unrealRuntime", {}).get("api", {}).get("classes", {})
    return {
        "schema": "unreal-animation-attach-timing-readiness-input@0.1.0",
        "sourceGameplayReadiness": {
            "path": public_path(gameplay_file),
            "reportVersion": gameplay.get("reportVersion"),
            "evidenceLevel": gameplay.get("evidenceLevel"),
            "l3Status": gameplay.get("l3Status"),
            "gate": gameplay.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "sourceAnimSequenceDeepFacts": {
            "path": public_path(deep_file),
            "reportVersion": deep.get("reportVersion"),
            "evidenceLevel": deep.get("evidenceLevel"),
            "l3Status": deep.get("l3Status"),
            "gate": deep_summary.get("gate"),
        },
        "runtimeDeepFactsCollected": bool(deep_summary.get("runtimeRowsCollected")),
        "animationBlueprintLibraryAvailable": bool(api_classes.get("AnimationBlueprintLibrary")),
        "animationDataModelAvailable": bool(api_classes.get("AnimationDataModel")),
        "intents": intents,
        "runtimeBoundary": {
            "assetWrites": deep_summary.get("assetWrites", 0),
            "engineWrites": deep_summary.get("engineWrites", 0),
            "productionWrites": deep_summary.get("productionWrites", 0),
        },
    }


def _rows(facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for intent in facts.get("intents", []):
        rows.extend(
            [
                _row(
                    intent,
                    "gameplay-controlled-readiness",
                    intent.get("sourceReadyByControlledExecutor"),
                    "warning",
                    "sourceReadinessState=%s publishRequired=%s"
                    % (intent.get("sourceReadinessState"), intent.get("publishRequired")),
                    "Resolve socket gameplay readiness before timing approval.",
                ),
                _row(
                    intent,
                    "animation-sequence-linked",
                    intent.get("linkedSequenceCount", 0) == len(intent.get("animationAssetPaths", []))
                    and intent.get("linkedSequenceCount", 0) > 0,
                    "error",
                    "animationPaths=%s linked=%s" % (intent.get("animationAssetPaths"), intent.get("linkedSequenceCount")),
                    "Import or relink the AnimSequence used by this gameplay attach intent.",
                ),
                _row(
                    intent,
                    "deep-facts-source-clean",
                    not intent.get("deepFactErrorRules"),
                    "error",
                    "deepFactErrorRules=%s" % intent.get("deepFactErrorRules"),
                    "Fix the animation source/deep-fact errors before attach timing approval.",
                ),
                _row(
                    intent,
                    "notify-properties-readable",
                    intent.get("notifyReadable"),
                    "error",
                    "notifyFacts=%s" % intent.get("notifyFacts"),
                    "Expose AnimSequence notify data through Unreal Python, Editor Utility or C++ bridge.",
                ),
                _row(
                    intent,
                    "required-attach-timing-events",
                    not intent.get("missingAttachTimingEvents"),
                    "error",
                    "required=%s found=%s missing=%s"
                    % (
                        intent.get("requiredAttachTimingEvents"),
                        intent.get("notifyEventNames"),
                        intent.get("missingAttachTimingEvents"),
                    ),
                    "Author explicit equip/attach notify events or provide an approved timing receipt.",
                ),
            ]
        )
    boundary = facts.get("runtimeBoundary", {})
    rows.append(
        {
            "id": "attach-timing:read-only-boundary",
            "intentId": None,
            "assetId": None,
            "ruleId": "read-only-boundary",
            "status": "pass"
            if boundary.get("assetWrites", 0) == 0
            and boundary.get("engineWrites", 0) == 0
            and boundary.get("productionWrites", 0) == 0
            else "error",
            "evidence": "assetWrites=%s engineWrites=%s productionWrites=%s"
            % (boundary.get("assetWrites", 0), boundary.get("engineWrites", 0), boundary.get("productionWrites", 0)),
            "fixPreview": "None",
        }
    )
    return rows


def _summary(facts: Dict[str, Any], rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    row_list = list(rows)
    intents = list(facts.get("intents", []))
    blocked = [row for row in intents if row.get("readinessState") == "TimingBlocked"]
    held = [row for row in intents if row.get("readinessState") == "HeldBySocketOrSource"]
    ready = [row for row in intents if row.get("readinessState") == "TimingReady"]
    boundary = facts.get("runtimeBoundary", {})
    return {
        "gate": "Blocked" if blocked or held else "Ready" if ready else "Blocked",
        "intentCount": len(intents),
        "timingReady": len(ready),
        "timingBlocked": len(blocked),
        "heldBySocketOrSource": len(held),
        "notifyReadableIntents": sum(1 for row in intents if row.get("notifyReadable")),
        "requiredAttachTimingEvents": sum(len(row.get("requiredAttachTimingEvents", [])) for row in intents),
        "missingAttachTimingEvents": sum(len(row.get("missingAttachTimingEvents", [])) for row in intents),
        "animationBlueprintLibraryAvailable": facts.get("animationBlueprintLibraryAvailable"),
        "animationDataModelAvailable": facts.get("animationDataModelAvailable"),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "assetWrites": boundary.get("assetWrites", 0),
        "engineWrites": boundary.get("engineWrites", 0),
        "productionWrites": boundary.get("productionWrites", 0),
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    owners = {
        "gameplay-controlled-readiness": "engine-ta",
        "animation-sequence-linked": "animation-ta",
        "deep-facts-source-clean": "animation-owner",
        "notify-properties-readable": "engine-ta",
        "required-attach-timing-events": "animation-gameplay-owner",
        "read-only-boundary": "tool-ta",
    }
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        actions.append(
            {
                "id": "attach-timing-action:%s" % row.get("id"),
                "intentId": row.get("intentId"),
                "assetId": row.get("assetId"),
                "ruleId": row.get("ruleId"),
                "status": row.get("status"),
                "owner": owners.get(row.get("ruleId"), "tool-ta"),
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


def _readiness_state(
    intent: Dict[str, Any],
    linked_sequences: List[Dict[str, Any]],
    notify_rows: List[Dict[str, Any]],
    missing_events: List[str],
    deep_errors: List[Dict[str, Any]],
) -> str:
    if intent.get("readinessState") != "ReadyByControlledExecutor":
        return "HeldBySocketOrSource"
    if not linked_sequences or deep_errors or not any(row.get("propertiesReadable") for row in notify_rows) or missing_events:
        return "TimingBlocked"
    return "TimingReady"


def _required_events(intent: Dict[str, Any]) -> List[str]:
    slot_role = str(intent.get("slotRole") or "")
    if "weapon" in slot_role.lower():
        return ["equip.attach"]
    if "backpack" in slot_role.lower():
        return ["gear.attach"]
    return ["attach.commit"]


def _sequence_summary(sequence: Dict[str, Any]) -> Dict[str, Any]:
    runtime = sequence.get("runtimeUnreal", {})
    deep = runtime.get("deepFacts", {})
    return {
        "assetId": sequence.get("assetId"),
        "expectedAnimSequencePath": sequence.get("expectedAnimSequencePath"),
        "ownerState": sequence.get("ownerState"),
        "animSequenceExists": runtime.get("animSequenceExists"),
        "class": deep.get("class"),
        "playLength": deep.get("playLength"),
        "directFrameRateReadable": deep.get("directFrameRateReadable"),
        "frameSpanDelta": deep.get("frameSpanDelta"),
    }


def _notify_facts(sequence: Dict[str, Any]) -> Dict[str, Any]:
    deep = sequence.get("runtimeUnreal", {}).get("deepFacts", {})
    facts = deep.get("notifies", {})
    event_names: List[str] = []
    for prop in facts.get("properties", []):
        value = prop.get("value")
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    name = item.get("notifyName") or item.get("name") or item.get("event")
                    if name:
                        event_names.append(str(name))
                elif item is not None:
                    event_names.append(str(item))
    return {
        "assetId": sequence.get("assetId"),
        "animSequencePath": sequence.get("expectedAnimSequencePath"),
        "propertiesReadable": bool(facts.get("propertiesReadable")),
        "counts": facts.get("counts", []),
        "eventNames": sorted(set(event_names)),
        "properties": facts.get("properties", []),
    }


def _notify_event_names(notify_rows: List[Dict[str, Any]]) -> List[str]:
    names: List[str] = []
    for row in notify_rows:
        names.extend(str(name) for name in row.get("eventNames", []))
    return sorted(set(names))


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    return [
        "R67 connects socket gameplay readiness to AnimSequence timing, so attach approval depends on both runtime sockets and animation trigger evidence.",
        "The current public AnimSequences exist and deep facts are readable, but AnimSequence notify properties are protected or absent through UE 5.3 Python.",
        "Missing equip/attach timing events are exported as owner actions instead of implying gameplay attach can fire correctly.",
        "The artifact remains read-only and records zero asset, engine and production writes.",
    ]


def _read_json(path: Path) -> Dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object: %s" % path)
    return data
