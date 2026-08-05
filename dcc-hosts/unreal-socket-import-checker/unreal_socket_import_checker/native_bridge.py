"""Native socket authoring bridge readiness for Unreal.

R40 proved that Unreal Python can see socket APIs but cannot safely materialize
socket identity for this public fixture. This layer turns that API-limited
result into a concrete C++ / Editor Utility bridge contract and runtime
readiness gate.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .contract import public_path, resolve_public_path


REPORT_VERSION = "unreal-socket-native-bridge-readiness@0.1.0"
BRIDGE_SCHEMA = "unreal-socket-native-bridge-contract@dcc-r60"


def build_native_bridge_report(
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
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Import Checker",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-readiness" if executed else "Blocked",
        "l3Status": runtime.get("blockedReason") or (
            "unreal_socket_native_bridge_readiness_collected" if executed else "native_bridge_contract_preflight"
        ),
        "sourceSocketAuthoringExecutor": {
            "path": public_path(source_file),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "summary": source.get("executor", {}).get("summary", {}),
        },
        "unrealRuntime": runtime,
        "facts": facts,
        "evaluation": {
            "schema": "unreal-socket-native-bridge-readiness-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "unreal-socket-native-bridge-readiness",
            "name": "Unreal Socket Native Bridge Readiness",
            "methodSource": "R40 API-limited socket authoring receipt + Unreal runtime Editor Utility/native module surface probe",
            "protocolCarrier": "source socket receipt, public Unreal project module layout, Editor Utility API surface and native commandlet contract",
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
    source_summary = source.get("executor", {}).get("summary", {})
    source_operations = list(source.get("operations", []))
    expected_sockets = sum(len(row.get("expectedSocketNames", [])) for row in source_operations)
    created_sockets = source_summary.get("createdSockets", 0)
    source_errors = source_summary.get("error", 0)
    missing_native_files = [
        item
        for item in _native_required_files()
        if item not in set(project.get("socketBridgeFiles", []))
    ]
    editor_surface = api.get("classes", {})
    commandlet_visible = bool(api.get("commandletClasses", {}).get("AiToolTaSocketAuthoringCommandlet"))
    return {
        "schema": "unreal-socket-native-bridge-readiness-facts@0.1.0",
        "bridgeSchema": BRIDGE_SCHEMA,
        "source": {
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source_summary.get("gate"),
            "selectedOperations": source_summary.get("selectedOperations"),
            "heldRows": source_summary.get("heldRows"),
            "expectedSockets": expected_sockets,
            "createdSockets": created_sockets,
            "errorChecks": source_errors,
            "apiLimited": source_summary.get("gate") == "Blocked"
            and expected_sockets > 0
            and int(created_sockets or 0) == 0,
        },
        "project": project,
        "runtimeApi": api,
        "bridgeReadiness": {
            "hasNativeSource": bool(project.get("hasSourceDir") or project.get("hasSocketBridgeSource")),
            "hasSocketBridgePlugin": bool(project.get("hasSocketBridgePlugin")),
            "hasCompiledBridgeBinary": bool(project.get("hasSocketBridgeBinary")),
            "missingRequiredFiles": missing_native_files,
            "commandletVisible": commandlet_visible,
            "editorUtilitySurfaceVisible": any(
                bool(editor_surface.get(name))
                for name in (
                    "EditorUtilitySubsystem",
                    "EditorUtilityBlueprint",
                    "EditorUtilityWidgetBlueprint",
                    "AssetToolsHelpers",
                )
            ),
            "socketClassesVisible": bool(
                editor_surface.get("SkeletalMesh")
                and editor_surface.get("Skeleton")
                and editor_surface.get("SkeletalMeshSocket")
            ),
        },
        "requiredHandoff": {
            "entrypoint": "UAiToolTaSocketAuthoringCommandlet or Editor Utility wrapper around the same native function library",
            "inputReceipt": "R38/R40 socket rows with socketName, parentJoint, transform, ownerState and expected target Skeleton path",
            "operations": [
                "Load target USkeleton or USkeletalMesh under /Game/AI_Tool_TA.",
                "Create USkeletalMeshSocket through native object construction.",
                "Set SocketName, BoneName and relative transform through C++ property access.",
                "Post-check socket list and parent binding.",
                "Rollback created sockets or save only inside explicit approved public fixture scope.",
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
            "source-python-api-limited-receipt",
            bool(source.get("apiLimited")),
            "error",
            "gate=%s expectedSockets=%s createdSockets=%s errors=%s"
            % (source.get("gate"), source.get("expectedSockets"), source.get("createdSockets"), source.get("errorChecks")),
            "Run R40 socket authoring executor first so the native bridge is justified by a concrete API-limited receipt.",
        ),
        _row(
            "unreal-runtime-entered",
            bool(runtime.get("executed")),
            "error",
            "executed=%s engine=%s" % (runtime.get("executed"), runtime.get("engineVersion")),
            "Run the readiness probe through UnrealEditor-Cmd against the public test project.",
        ),
        _row(
            "socket-runtime-classes-visible",
            bool(readiness.get("socketClassesVisible")),
            "error",
            "classes=%s" % api.get("classes", {}),
            "Enable the Unreal editor scripting/runtime classes required to inspect Skeleton and SkeletalMesh sockets.",
        ),
        _row(
            "editor-utility-surface-visible",
            bool(readiness.get("editorUtilitySurfaceVisible")),
            "warning",
            "classes=%s" % api.get("classes", {}),
            "Enable EditorScriptingUtilities or expose an equivalent commandlet wrapper for socket authoring.",
        ),
        _row(
            "native-module-source-present",
            bool(readiness.get("hasNativeSource") or readiness.get("hasSocketBridgePlugin")),
            "error",
            "hasSource=%s hasPlugin=%s missing=%s"
            % (project.get("hasSourceDir"), project.get("hasSocketBridgePlugin"), readiness.get("missingRequiredFiles")),
            "Add the public AI_Tool_TA_SocketBridge Editor plugin source before claiming native socket write support.",
        ),
        _row(
            "native-commandlet-entrypoint-visible",
            bool(readiness.get("commandletVisible")),
            "error",
            "commandletVisible=%s commandletClasses=%s"
            % (readiness.get("commandletVisible"), api.get("commandletClasses", {})),
            "Compile and load UAiToolTaSocketAuthoringCommandlet or an equivalent Editor Utility bridge.",
        ),
        _row(
            "compiled-bridge-binary-present",
            bool(readiness.get("hasCompiledBridgeBinary")),
            "error",
            "hasBinary=%s binaries=%s" % (project.get("hasSocketBridgeBinary"), project.get("socketBridgeBinaries", [])),
            "Build the Editor-only bridge module before running socket mutation receipts through it.",
        ),
        _row(
            "contract-handoff-complete",
            bool(facts.get("requiredHandoff", {}).get("operations")) and len(_bridge_contracts()) == 2,
            "error",
            "operations=%s contracts=%s"
            % (len(facts.get("requiredHandoff", {}).get("operations", [])), [row["id"] for row in _bridge_contracts()]),
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
        "id": "native-socket-bridge:%s" % rule_id,
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summary(rows: Iterable[Dict[str, Any]], facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    row_list = list(rows)
    readiness = facts.get("bridgeReadiness", {})
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "gate": _gate(row_list),
        "checks": len(row_list),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "sourceApiLimited": bool(facts.get("source", {}).get("apiLimited")),
        "expectedSockets": facts.get("source", {}).get("expectedSockets"),
        "createdSocketsViaPython": facts.get("source", {}).get("createdSockets"),
        "editorUtilitySurfaceVisible": bool(readiness.get("editorUtilitySurfaceVisible")),
        "socketClassesVisible": bool(readiness.get("socketClassesVisible")),
        "hasNativeSource": bool(readiness.get("hasNativeSource")),
        "hasSocketBridgePlugin": bool(readiness.get("hasSocketBridgePlugin")),
        "hasCompiledBridgeBinary": bool(readiness.get("hasCompiledBridgeBinary")),
        "commandletVisible": bool(readiness.get("commandletVisible")),
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
        "source-python-api-limited-receipt": "engine-ta",
        "unreal-runtime-entered": "tool-ta",
        "socket-runtime-classes-visible": "engine-ta",
        "editor-utility-surface-visible": "engine-ta",
        "native-module-source-present": "engine-ta",
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
                "id": "native-socket-bridge-action:%s" % row.get("ruleId"),
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
            "id": "ai-tool-ta-socket-bridge-commandlet",
            "kind": "Unreal Editor C++ Commandlet",
            "entrypoint": "UAiToolTaSocketAuthoringCommandlet",
            "requiredFiles": _native_required_files(),
            "receiptInput": "unreal-socket-authoring-executor@0.1.0 operations",
            "successCriteria": [
                "SocketName and BoneName are set by native property access.",
                "Post-check proves expected socket names and parent bindings exist.",
                "Rollback removes public fixture sockets or the commandlet exits without saving.",
            ],
        },
        {
            "id": "ai-tool-ta-socket-editor-utility-wrapper",
            "kind": "Editor Utility / Blueprint callable wrapper",
            "entrypoint": "UAiToolTaSocketBridgeLibrary::ApplySocketReceipt",
            "requiredFiles": [
                "Plugins/AI_Tool_TA_SocketBridge/Source/AI_Tool_TA_SocketBridge/Public/AiToolTaSocketBridgeLibrary.h",
                "Plugins/AI_Tool_TA_SocketBridge/Source/AI_Tool_TA_SocketBridge/Private/AiToolTaSocketBridgeLibrary.cpp",
            ],
            "receiptInput": "single approved socket row or JSON receipt",
            "successCriteria": [
                "Editor Utility calls the same native implementation as the commandlet.",
                "No blocked Maya source row can enter the write path.",
                "All writes stay inside /Game/AI_Tool_TA unless an owner-approved production scope is supplied.",
            ],
        },
    ]


def _native_required_files() -> List[str]:
    return [
        "Plugins/AI_Tool_TA_SocketBridge/AI_Tool_TA_SocketBridge.uplugin",
        "Plugins/AI_Tool_TA_SocketBridge/Source/AI_Tool_TA_SocketBridge/AI_Tool_TA_SocketBridge.Build.cs",
        "Plugins/AI_Tool_TA_SocketBridge/Source/AI_Tool_TA_SocketBridge/Public/AiToolTaSocketAuthoringCommandlet.h",
        "Plugins/AI_Tool_TA_SocketBridge/Source/AI_Tool_TA_SocketBridge/Private/AiToolTaSocketAuthoringCommandlet.cpp",
        "Plugins/AI_Tool_TA_SocketBridge/Source/AI_Tool_TA_SocketBridge/Public/AiToolTaSocketBridgeLibrary.h",
        "Plugins/AI_Tool_TA_SocketBridge/Source/AI_Tool_TA_SocketBridge/Private/AiToolTaSocketBridgeLibrary.cpp",
    ]


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    return [
        "R60 keeps the R40 API-limited socket finding honest: Unreal Python did not become the socket write solution.",
        "The readiness artifact names the native commandlet and Editor Utility bridge entrypoints required for safe socket authoring.",
        "The public Unreal project is blocked until the bridge source and compiled Editor module exist; the probe is read-only with zero asset writes.",
    ]


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
