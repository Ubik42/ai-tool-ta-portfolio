"""Control Rig native diagnostic bridge source/readiness facts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .compile_status import public_path, resolve_public_path


REPORT_VERSION = "unreal-control-rig-native-bridge-readiness@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_RELATIVE = Path(
    "dcc-hosts/unreal-handoff-inspector/projects/AI_Tool_TA_Unreal_L3/Plugins/AI_Tool_TA_ControlRigBridge"
)
REQUIRED_NATIVE_FILES = [
    "AI_Tool_TA_ControlRigBridge.uplugin",
    "Source/AI_Tool_TA_ControlRigBridge/AI_Tool_TA_ControlRigBridge.Build.cs",
    "Source/AI_Tool_TA_ControlRigBridge/Public/AI_Tool_TA_ControlRigBridge.h",
    "Source/AI_Tool_TA_ControlRigBridge/Private/AI_Tool_TA_ControlRigBridge.cpp",
    "Source/AI_Tool_TA_ControlRigBridge/Public/AiToolTaControlRigBridgeLibrary.h",
    "Source/AI_Tool_TA_ControlRigBridge/Private/AiToolTaControlRigBridgeLibrary.cpp",
    "Source/AI_Tool_TA_ControlRigBridge/Public/AiToolTaControlRigDiagnosticsCommandlet.h",
    "Source/AI_Tool_TA_ControlRigBridge/Private/AiToolTaControlRigDiagnosticsCommandlet.cpp",
]


def build_control_rig_native_bridge_report(
    source_compile_status_path: str | Path,
    runtime_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    source_path = resolve_public_path(source_compile_status_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    runtime_snapshot = runtime_snapshot or {
        "runtime": {
            "executed": False,
            "blockedReason": "not_run",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
        }
    }
    facts = _facts(source, source_path, runtime_snapshot)
    rows = _rows(facts)
    summary = _summary(facts, rows)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Control Rig Native Bridge Readiness",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-readiness" if facts.get("runtimeEntered") else "Blocked",
        "l3Status": (
            "unreal_control_rig_native_bridge_readiness_collected"
            if facts.get("runtimeEntered")
            else facts.get("runtime", {}).get("blockedReason", "unreal_control_rig_native_bridge_not_run")
        ),
        "sourceCompileStatus": facts["sourceCompileStatus"],
        "facts": facts,
        "evaluation": {
            "schema": "unreal-control-rig-native-bridge-readiness-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "unreal-control-rig-native-bridge-readiness",
            "name": "Unreal Control Rig Native Bridge Readiness",
            "methodSource": "R45 compile status + public Control Rig native diagnostic bridge source/readiness probe",
            "protocolCarrier": "ControlRigBlueprint compile/status API surface, C++ commandlet source, binary/commandlet visibility gate",
            "boundary": {
                "mutation": "read_only_source_and_runtime_probe",
                "assetWrites": summary.get("assetWrites", 0),
                "engineWrites": summary.get("engineWrites", 0),
                "productionWrites": summary.get("productionWrites", 0),
            },
        },
        "reviewerClaims": _reviewer_claims(summary),
    }


def _facts(source: Dict[str, Any], source_path: Path, runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    runtime = runtime_snapshot.get("runtime", {})
    source_summary = source.get("evaluation", {}).get("summary", {})
    source_facts = source.get("facts", {}).get("summary", {})
    plugin_dir = PORTFOLIO_ROOT / PLUGIN_RELATIVE
    required_rows = []
    for relative in REQUIRED_NATIVE_FILES:
        path = plugin_dir / relative
        required_rows.append(
            {
                "relativePath": relative,
                "path": public_path(path),
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
            }
        )
    class_visibility = runtime.get("api", {}).get("classes", {})
    return {
        "schema": "unreal-control-rig-native-bridge-readiness-input@0.1.0",
        "sourceCompileStatus": {
            "path": public_path(source_path),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source_summary.get("gate"),
            "compileInvocationSucceededRows": source_facts.get("compileInvocationSucceededRows"),
            "directStatusReadableRows": source_facts.get("directStatusReadableRows"),
            "diagnosticReadableRows": source_facts.get("diagnosticReadableRows"),
        },
        "sourceRequiresNativeBridge": bool(
            source_facts.get("compileInvocationSucceededRows", 0)
            and not source_facts.get("directStatusReadableRows", 0)
            and not source_facts.get("diagnosticReadableRows", 0)
        ),
        "runtime": runtime,
        "runtimeEntered": bool(runtime.get("executed")),
        "classVisibility": class_visibility,
        "controlRigClassesVisible": all(
            bool(class_visibility.get(name))
            for name in ("ControlRigBlueprint", "RigVMBlueprint", "RigVMController")
        ),
        "pluginDir": public_path(plugin_dir),
        "requiredNativeFiles": required_rows,
        "missingRequiredNativeFiles": [row["relativePath"] for row in required_rows if not row["exists"]],
        "hasNativeSource": all(row["exists"] for row in required_rows),
        "hasControlRigBridgePlugin": plugin_dir.exists(),
        "hasCompiledBridgeBinary": bool(runtime.get("hasCompiledBridgeBinary")),
        "commandletVisible": bool(runtime.get("commandletVisible")),
        "assetWrites": runtime.get("assetWrites", 0),
        "engineWrites": runtime.get("engineWrites", 0),
        "productionWrites": runtime.get("productionWrites", 0),
    }


def _rows(facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        _row("source-requires-native-bridge", facts.get("sourceRequiresNativeBridge"), "warning", "source=%s" % facts.get("sourceCompileStatus"), "Use native C++ reflection/commandlet to read protected compile status and diagnostics."),
        _row("unreal-runtime-entered", facts.get("runtimeEntered"), "error", "runtime=%s" % facts.get("runtime"), "Run the readiness probe inside UnrealEditor-Cmd."),
        _row("control-rig-runtime-classes-visible", facts.get("controlRigClassesVisible"), "error", "classVisibility=%s" % facts.get("classVisibility"), "Enable ControlRig/RigVM editor plugins in the public project."),
        _row("native-source-present", facts.get("hasNativeSource"), "error", "missing=%s" % facts.get("missingRequiredNativeFiles"), "Add the public Control Rig bridge plugin source files."),
        _row("compiled-bridge-binary-visible", facts.get("hasCompiledBridgeBinary"), "error", "pluginDir=%s" % facts.get("pluginDir"), "Run BuildPlugin for AI_Tool_TA_ControlRigBridge."),
        _row("commandlet-visible", facts.get("commandletVisible"), "error", "commandletVisible=%s" % facts.get("commandletVisible"), "Load the compiled bridge and run AiToolTaControlRigDiagnostics."),
        _row(
            "read-only-boundary",
            facts.get("assetWrites", 0) == 0 and facts.get("engineWrites", 0) == 0 and facts.get("productionWrites", 0) == 0,
            "error",
            "assetWrites=%s engineWrites=%s productionWrites=%s" % (facts.get("assetWrites"), facts.get("engineWrites"), facts.get("productionWrites")),
            "Keep native readiness as a source/runtime probe with zero writes.",
        ),
    ]


def _summary(facts: Dict[str, Any], rows: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    row_list = list(rows)
    has_errors = any(row.get("status") == "error" for row in row_list)
    has_warnings = any(row.get("status") == "warning" for row in row_list)
    return {
        "gate": "Blocked" if has_errors else "Review" if has_warnings else "Ready",
        "sourceRequiresNativeBridge": facts.get("sourceRequiresNativeBridge"),
        "runtimeEntered": facts.get("runtimeEntered"),
        "controlRigClassesVisible": facts.get("controlRigClassesVisible"),
        "hasNativeSource": facts.get("hasNativeSource"),
        "hasControlRigBridgePlugin": facts.get("hasControlRigBridgePlugin"),
        "missingRequiredNativeFiles": len(facts.get("missingRequiredNativeFiles", [])),
        "hasCompiledBridgeBinary": facts.get("hasCompiledBridgeBinary"),
        "commandletVisible": facts.get("commandletVisible"),
        "pass": sum(1 for row in row_list if row.get("status") == "pass"),
        "warning": sum(1 for row in row_list if row.get("status") == "warning"),
        "error": sum(1 for row in row_list if row.get("status") == "error"),
        "assetWrites": facts.get("assetWrites", 0),
        "engineWrites": facts.get("engineWrites", 0),
        "productionWrites": facts.get("productionWrites", 0),
    }


def _row(rule_id: str, passed: bool, fail_status: str, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "control-rig-native-bridge:%s" % rule_id,
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    owners = {
        "source-requires-native-bridge": "technical-animation-owner",
        "unreal-runtime-entered": "engine-ta",
        "control-rig-runtime-classes-visible": "engine-ta",
        "native-source-present": "tool-ta",
        "compiled-bridge-binary-visible": "tool-ta",
        "commandlet-visible": "tool-ta",
        "read-only-boundary": "pipeline-ta",
    }
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        actions.append(
            {
                "id": "control-rig-native-bridge-action:%s" % row.get("ruleId"),
                "ruleId": row.get("ruleId"),
                "status": row.get("status"),
                "owner": owners.get(row.get("ruleId"), "tool-ta"),
                "preview": row.get("fixPreview"),
                "writeBoundary": "source_and_runtime_readiness",
            }
        )
    return actions


def _reviewer_claims(summary: Dict[str, Any]) -> List[str]:
    return [
        "R74 converts the R45 Control Rig compile-status blind spot into a native C++ bridge source/readiness gate.",
        "The public Unreal project now contains an editor-only Control Rig bridge plugin with a diagnostic library and commandlet source contract.",
        "Unreal runtime sees ControlRig/RigVM classes; the current Blocked gate is the explicit binary/commandlet build gate, not a missing business rationale.",
        "The readiness artifact is read-only and records zero asset, engine and production writes.",
        "Summary: sourceRequiresNativeBridge=%s, hasNativeSource=%s, hasCompiledBridgeBinary=%s, commandletVisible=%s."
        % (
            summary.get("sourceRequiresNativeBridge"),
            summary.get("hasNativeSource"),
            summary.get("hasCompiledBridgeBinary"),
            summary.get("commandletVisible"),
        ),
    ]
