"""Native AnimSequence notify bridge readiness for Unreal.

R67 proved socket-backed gameplay attach still needs explicit animation timing
events. UE 5.3 Python can collect sequence duration/frame facts, but the notify
surface is API-limited for the public fixture. This module turns that limitation
into a concrete C++ / Editor Utility bridge contract and runtime readiness gate.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .contract import public_path, resolve_public_path


REPORT_VERSION = "unreal-animation-notify-native-bridge-readiness@0.1.0"
BRIDGE_SCHEMA = "unreal-animation-notify-native-bridge-contract@dcc-r68"


def build_anim_notify_native_bridge_report(
    source_path: str | Path,
    runtime_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_file = resolve_public_path(source_path)
    source = json.loads(source_file.read_text(encoding="utf-8"))
    runtime_snapshot = runtime_snapshot or _empty_runtime_snapshot()
    facts = _build_facts(source, runtime_snapshot)
    rows = _evaluate(facts, runtime_snapshot)
    summary = _summary(rows, facts, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Animation Native Notify Bridge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-readiness" if executed else "Blocked",
        "l3Status": runtime.get("blockedReason")
        or ("unreal_animation_notify_native_bridge_readiness_collected" if executed else "anim_notify_native_bridge_contract_preflight"),
        "sourceAttachTimingReadiness": {
            "path": public_path(source_file),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "summary": source.get("evaluation", {}).get("summary", {}),
        },
        "unrealRuntime": runtime,
        "facts": facts,
        "evaluation": {
            "schema": "unreal-animation-notify-native-bridge-readiness-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "unreal-animation-notify-native-bridge-readiness",
            "name": "Unreal Animation Notify Native Bridge Readiness",
            "methodSource": "R67 attach timing readiness + Unreal runtime AnimSequence/native module surface probe",
            "protocolCarrier": "attach timing owner actions, public Unreal project native plugin source, Editor commandlet/function library contract",
            "boundary": {
                "mutation": "read_only_unreal_runtime_probe",
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "none"),
            },
        },
        "bridgeContracts": _bridge_contracts(),
        "reviewerClaims": _reviewer_claims(summary),
    }


def _build_facts(source: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    runtime = runtime_snapshot.get("runtime", {})
    project = runtime_snapshot.get("project", {})
    api = runtime.get("api", {})
    classes = api.get("classes", {})
    source_summary = source.get("evaluation", {}).get("summary", {})
    existing_native_files = {_norm_path(item) for item in project.get("animNotifyBridgeFiles", [])}
    missing_native_files = [
        item
        for item in _native_required_files()
        if _norm_path(item) not in existing_native_files
    ]
    source_requires_native = (
        source_summary.get("gate") == "Blocked"
        and int(source_summary.get("notifyReadableIntents") or 0) == 0
        and int(source_summary.get("missingAttachTimingEvents") or 0) > 0
    )
    editor_surface = api.get("classes", {})
    commandlet_visible = bool(api.get("commandletClasses", {}).get("AiToolTaAnimNotifyDiagnosticsCommandlet"))
    return {
        "schema": "unreal-animation-notify-native-bridge-readiness-facts@0.1.0",
        "bridgeSchema": BRIDGE_SCHEMA,
        "source": {
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source_summary.get("gate"),
            "intentCount": source_summary.get("intentCount"),
            "notifyReadableIntents": source_summary.get("notifyReadableIntents"),
            "requiredAttachTimingEvents": source_summary.get("requiredAttachTimingEvents"),
            "missingAttachTimingEvents": source_summary.get("missingAttachTimingEvents"),
            "animationBlueprintLibraryAvailable": source_summary.get("animationBlueprintLibraryAvailable"),
            "animationDataModelAvailable": source_summary.get("animationDataModelAvailable"),
            "requiresNativeNotifyBridge": source_requires_native,
        },
        "project": project,
        "runtimeApi": api,
        "bridgeReadiness": {
            "hasNativeSource": bool(project.get("hasSourceDir") or project.get("hasAnimNotifyBridgeSource")),
            "hasAnimNotifyBridgePlugin": bool(project.get("hasAnimNotifyBridgePlugin")),
            "hasCompiledBridgeBinary": bool(project.get("hasAnimNotifyBridgeBinary")),
            "missingRequiredFiles": missing_native_files,
            "commandletVisible": commandlet_visible,
            "functionLibraryVisible": bool(api.get("functionLibraryClasses", {}).get("AiToolTaAnimNotifyBridgeLibrary")),
            "editorUtilitySurfaceVisible": any(
                bool(editor_surface.get(name))
                for name in (
                    "EditorUtilitySubsystem",
                    "EditorUtilityBlueprint",
                    "EditorUtilityWidgetBlueprint",
                    "AssetToolsHelpers",
                )
            ),
            "animSequenceClassesVisible": bool(
                classes.get("AnimSequence")
                and (classes.get("AnimSequenceBase") or classes.get("AnimationAsset"))
                and classes.get("AnimNotify")
                and classes.get("AnimNotifyState")
            ),
            "animationBlueprintLibraryAvailable": bool(classes.get("AnimationBlueprintLibrary")),
            "animationDataModelAvailable": bool(classes.get("AnimationDataModel")),
        },
        "requiredHandoff": {
            "entrypoint": "UAiToolTaAnimNotifyDiagnosticsCommandlet or Editor Utility wrapper around UAiToolTaAnimNotifyBridgeLibrary",
            "inputReceipt": "R67 attach timing readiness report with gameplay intent animationAssetPaths and missing attach timing events",
            "diagnosticOperations": [
                "Load each public /Game/AI_Tool_TA AnimSequence referenced by gameplay attach intents.",
                "Read UAnimSequenceBase::Notifies through C++ and emit name/class/track/time/duration rows.",
                "Join notify rows back to required timing events such as equip.attach and gear.attach.",
                "Keep diagnostics read-only; only a later guarded authoring commandlet may write notifies.",
            ],
        },
    }


def _evaluate(facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    runtime = runtime_snapshot.get("runtime", {})
    source = facts.get("source", {})
    readiness = facts.get("bridgeReadiness", {})
    project = facts.get("project", {})
    api = facts.get("runtimeApi", {})
    return [
        _row(
            "source-attach-timing-blocked",
            source.get("gate") == "Blocked" and int(source.get("missingAttachTimingEvents") or 0) > 0,
            "error",
            "gate=%s notifyReadableIntents=%s missingAttachTimingEvents=%s"
            % (source.get("gate"), source.get("notifyReadableIntents"), source.get("missingAttachTimingEvents")),
            "Run R67 attach timing readiness first so native notify work is grounded in gameplay timing gaps.",
        ),
        _row(
            "source-native-bridge-required",
            bool(source.get("requiresNativeNotifyBridge")),
            "error",
            "animationBlueprintLibrary=%s animationDataModel=%s notifyReadableIntents=%s"
            % (
                source.get("animationBlueprintLibraryAvailable"),
                source.get("animationDataModelAvailable"),
                source.get("notifyReadableIntents"),
            ),
            "Expose AnimSequence notify data through a native Editor plugin before claiming attach timing approval.",
        ),
        _row(
            "unreal-runtime-entered",
            bool(runtime.get("executed")),
            "error",
            "executed=%s engine=%s" % (runtime.get("executed"), runtime.get("engineVersion")),
            "Run the readiness probe through UnrealEditor-Cmd against the public test project.",
        ),
        _row(
            "animsequence-runtime-classes-visible",
            bool(readiness.get("animSequenceClassesVisible")),
            "error",
            "classes=%s" % api.get("classes", {}),
            "Enable the Unreal animation classes required to inspect AnimSequence notify events.",
        ),
        _row(
            "notify-python-api-limited",
            bool(source.get("requiresNativeNotifyBridge")) and not readiness.get("animationBlueprintLibraryAvailable"),
            "warning",
            "runtimeAnimationBlueprintLibrary=%s sourceAnimationDataModel=%s"
            % (readiness.get("animationBlueprintLibraryAvailable"), source.get("animationDataModelAvailable")),
            "If Python notify APIs become visible, rerun R67 and compare against native diagnostics before adding a write path.",
        ),
        _row(
            "native-module-source-present",
            bool(readiness.get("hasNativeSource") and readiness.get("hasAnimNotifyBridgePlugin"))
            and not readiness.get("missingRequiredFiles"),
            "error",
            "hasSource=%s hasPlugin=%s missing=%s"
            % (
                project.get("hasAnimNotifyBridgeSource"),
                project.get("hasAnimNotifyBridgePlugin"),
                readiness.get("missingRequiredFiles"),
            ),
            "Add the public AI_Tool_TA_AnimNotifyBridge Editor plugin source before claiming native notify diagnostic support.",
        ),
        _row(
            "native-commandlet-entrypoint-visible",
            bool(readiness.get("commandletVisible")),
            "error",
            "commandletVisible=%s commandletClasses=%s"
            % (readiness.get("commandletVisible"), api.get("commandletClasses", {})),
            "Compile and load UAiToolTaAnimNotifyDiagnosticsCommandlet or an equivalent Editor Utility bridge.",
        ),
        _row(
            "compiled-bridge-binary-present",
            bool(readiness.get("hasCompiledBridgeBinary")),
            "error",
            "hasBinary=%s binaries=%s"
            % (project.get("hasAnimNotifyBridgeBinary"), project.get("animNotifyBridgeBinaries", [])),
            "Build the Editor-only bridge module before running AnimSequence notify diagnostics through it.",
        ),
        _row(
            "contract-handoff-complete",
            bool(facts.get("requiredHandoff", {}).get("diagnosticOperations")) and len(_bridge_contracts()) == 2,
            "error",
            "operations=%s contracts=%s"
            % (len(facts.get("requiredHandoff", {}).get("diagnosticOperations", [])), [row["id"] for row in _bridge_contracts()]),
            "Keep both native commandlet and Editor Utility wrapper contracts documented for reviewer handoff.",
        ),
        _row(
            "write-boundary-clean",
            runtime.get("assetWrites", 0) == 0
            and runtime.get("engineWrites", 0) == 0
            and runtime.get("productionWrites", 0) == 0,
            "error",
            "assetWrites=%s engineWrites=%s productionWrites=%s"
            % (runtime.get("assetWrites", 0), runtime.get("engineWrites", 0), runtime.get("productionWrites", 0)),
            "Readiness probes must not save Unreal assets or mutate production content.",
        ),
    ]


def _row(rule_id: str, passed: bool, fail_status: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "native-anim-notify-bridge:%s" % rule_id,
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summary(rows: Iterable[Dict[str, Any]], facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    row_list = list(rows)
    readiness = facts.get("bridgeReadiness", {})
    runtime = runtime_snapshot.get("runtime", {})
    source = facts.get("source", {})
    return {
        "gate": _gate(row_list),
        "checks": len(row_list),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "sourceTimingGate": source.get("gate"),
        "sourceRequiresNativeBridge": bool(source.get("requiresNativeNotifyBridge")),
        "intentCount": source.get("intentCount"),
        "notifyReadableIntents": source.get("notifyReadableIntents"),
        "requiredAttachTimingEvents": source.get("requiredAttachTimingEvents"),
        "missingAttachTimingEvents": source.get("missingAttachTimingEvents"),
        "animationBlueprintLibraryAvailable": bool(readiness.get("animationBlueprintLibraryAvailable")),
        "animationDataModelAvailable": bool(readiness.get("animationDataModelAvailable")),
        "runtimeEntered": bool(runtime.get("executed")),
        "animSequenceClassesVisible": bool(readiness.get("animSequenceClassesVisible")),
        "editorUtilitySurfaceVisible": bool(readiness.get("editorUtilitySurfaceVisible")),
        "hasNativeSource": bool(readiness.get("hasNativeSource")),
        "hasAnimNotifyBridgePlugin": bool(readiness.get("hasAnimNotifyBridgePlugin")),
        "hasCompiledBridgeBinary": bool(readiness.get("hasCompiledBridgeBinary")),
        "commandletVisible": bool(readiness.get("commandletVisible")),
        "functionLibraryVisible": bool(readiness.get("functionLibraryVisible")),
        "missingRequiredNativeFiles": len(readiness.get("missingRequiredFiles", [])),
        "assetWrites": runtime.get("assetWrites", 0),
        "engineWrites": runtime.get("engineWrites", 0),
        "productionWrites": runtime.get("productionWrites", 0),
    }


def _gate(rows: Iterable[Dict[str, Any]]) -> str:
    row_list = list(rows)
    if any(row.get("status") == "error" for row in row_list):
        return "Blocked"
    if any(row.get("status") == "warning" for row in row_list):
        return "Review"
    return "Ready"


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    owner_by_rule = {
        "source-attach-timing-blocked": "animation-ta",
        "source-native-bridge-required": "engine-ta",
        "unreal-runtime-entered": "tool-ta",
        "animsequence-runtime-classes-visible": "engine-ta",
        "notify-python-api-limited": "engine-ta",
        "native-module-source-present": "engine-programmer",
        "native-commandlet-entrypoint-visible": "engine-programmer",
        "compiled-bridge-binary-present": "engine-programmer",
        "contract-handoff-complete": "tool-ta",
        "write-boundary-clean": "tool-ta",
    }
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        actions.append(
            {
                "id": "native-anim-notify-bridge-action:%s" % row.get("ruleId"),
                "ruleId": row.get("ruleId"),
                "status": row.get("status"),
                "owner": owner_by_rule.get(row.get("ruleId"), "tool-ta"),
                "preview": row.get("fixPreview"),
                "writeBoundary": "readiness_only",
            }
        )
    return actions


def _bridge_contracts() -> List[Dict[str, Any]]:
    return [
        {
            "id": "ai-tool-ta-anim-notify-diagnostics-commandlet",
            "kind": "Unreal Editor C++ Commandlet",
            "entrypoint": "UAiToolTaAnimNotifyDiagnosticsCommandlet",
            "requiredFiles": _native_required_files(),
            "receiptInput": "unreal-animation-attach-timing-readiness@0.1.0 intents and animationAssetPaths",
            "successCriteria": [
                "Each referenced public AnimSequence is loaded through native object paths.",
                "Notify name, class, track index, trigger time, end time and duration are emitted from UAnimSequenceBase::Notifies.",
                "Diagnostics remain read-only and report zero production writes.",
            ],
        },
        {
            "id": "ai-tool-ta-anim-notify-editor-utility-wrapper",
            "kind": "Editor Utility / Blueprint callable wrapper",
            "entrypoint": "UAiToolTaAnimNotifyBridgeLibrary::CollectAnimNotifyDiagnostics",
            "requiredFiles": [
                "Plugins/AI_Tool_TA_AnimNotifyBridge/Source/AI_Tool_TA_AnimNotifyBridge/Public/AiToolTaAnimNotifyBridgeLibrary.h",
                "Plugins/AI_Tool_TA_AnimNotifyBridge/Source/AI_Tool_TA_AnimNotifyBridge/Private/AiToolTaAnimNotifyBridgeLibrary.cpp",
            ],
            "receiptInput": "single AnimSequence asset or attach timing operation row",
            "successCriteria": [
                "Editor Utility calls the same native diagnostic implementation as the commandlet.",
                "Required attach timing events can be reviewed against real notify rows.",
                "Any future authoring path requires explicit public fixture scope and rollback guards.",
            ],
        },
    ]


def _native_required_files() -> List[str]:
    return [
        "Plugins/AI_Tool_TA_AnimNotifyBridge/AI_Tool_TA_AnimNotifyBridge.uplugin",
        "Plugins/AI_Tool_TA_AnimNotifyBridge/Source/AI_Tool_TA_AnimNotifyBridge/AI_Tool_TA_AnimNotifyBridge.Build.cs",
        "Plugins/AI_Tool_TA_AnimNotifyBridge/Source/AI_Tool_TA_AnimNotifyBridge/Public/AiToolTaAnimNotifyDiagnosticsCommandlet.h",
        "Plugins/AI_Tool_TA_AnimNotifyBridge/Source/AI_Tool_TA_AnimNotifyBridge/Private/AiToolTaAnimNotifyDiagnosticsCommandlet.cpp",
        "Plugins/AI_Tool_TA_AnimNotifyBridge/Source/AI_Tool_TA_AnimNotifyBridge/Public/AiToolTaAnimNotifyBridgeLibrary.h",
        "Plugins/AI_Tool_TA_AnimNotifyBridge/Source/AI_Tool_TA_AnimNotifyBridge/Private/AiToolTaAnimNotifyBridgeLibrary.cpp",
    ]


def _norm_path(path: Any) -> str:
    return str(path).replace("\\", "/").lower()


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    claims = [
        "R68 keeps R67 honest: socket executor and gameplay attach evidence do not imply animation timing approval.",
        "The attach timing gap is now expressed as a native AnimSequence notify diagnostics bridge contract, not a frontend note.",
        "The readiness probe is read-only and records zero production writes.",
    ]
    if summary.get("hasNativeSource") or summary.get("hasAnimNotifyBridgePlugin"):
        claims.append("The public Unreal project now has the Anim Notify bridge source contract; it remains blocked until the Editor module is built and the commandlet is visible.")
    else:
        claims.append("The public Unreal project is blocked until the Anim Notify bridge source and compiled Editor module exist.")
    return claims


def _empty_runtime_snapshot() -> Dict[str, Any]:
    return {
        "runtime": {
            "executed": False,
            "runtime": "preflight",
            "engineVersion": "not_entered",
            "blockedReason": "not_run",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
            "api": {},
        },
        "project": {},
    }
