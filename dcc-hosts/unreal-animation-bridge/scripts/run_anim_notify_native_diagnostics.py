from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
LOG_DIR = ARTIFACT_DIR / "unreal-animation-native-notify-diagnostics-logs"
RECEIPT_DIR = ARTIFACT_DIR / "unreal-animation-native-notify-diagnostics-receipts"
PUBLIC_MANIFEST = PORTFOLIO_ROOT / "public-case-package" / "dcc-first-package-manifest.json"
SOURCE_PROJECT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "AI_Tool_TA_Unreal_L3.uproject"
)
TEMP_ROOT = Path(os.environ.get("AI_TOOL_TA_ANIM_NOTIFY_DIAGNOSTICS_ROOT", r"D:\cs\_test\ai_tool_ta_anim_notify_diagnostics"))
REPORT_VERSION = "unreal-animation-notify-native-diagnostics@0.1.0"
PLUGIN_NAME = "AI_Tool_TA_AnimNotifyBridge"
COMMANDLET_NAME = "AiToolTaAnimNotifyDiagnostics"
CONTRACT_LOG = "AI Tool TA Anim Notify Diagnostics Commandlet loaded."
DIAGNOSTICS_STATUS = "diagnostics_completed"

COMMON_UNREAL_CLI = [
    r"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
]


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")

    output_path = ARTIFACT_DIR / ("unreal-animation-notify-native-diagnostics-%s.json" % stamp)
    stdout_path = LOG_DIR / ("unreal-animation-notify-native-diagnostics-%s.stdout.log" % stamp)
    stderr_path = LOG_DIR / ("unreal-animation-notify-native-diagnostics-%s.stderr.log" % stamp)
    input_path = RECEIPT_DIR / ("unreal-animation-notify-native-diagnostics-input-%s.json" % stamp)
    receipt_path = RECEIPT_DIR / ("unreal-animation-notify-native-diagnostics-output-%s.json" % stamp)
    temp_project_dir = TEMP_ROOT / ("aanb-diagnostics-%s" % stamp)
    temp_project = temp_project_dir / "AI_Tool_TA_AnimNotifyDiagnostics.uproject"

    unreal_cli = _find_unreal_cli()
    build_artifact = _resolve_build_artifact()
    plugin_package = _plugin_package_dir(build_artifact)
    attach_timing_path = _resolve_attach_timing_artifact()
    attach_timing_report = _read_json(attach_timing_path) if attach_timing_path else {}
    diagnostic_input = _build_input_receipt(attach_timing_path, attach_timing_report)
    input_path.write_text(json.dumps(diagnostic_input, ensure_ascii=False, indent=2), encoding="utf-8")

    preflight = _preflight(unreal_cli, build_artifact, plugin_package, attach_timing_path, diagnostic_input)
    runtime: Optional[Dict[str, Any]] = None
    if not preflight:
        _prepare_temp_project(temp_project_dir, temp_project, plugin_package)
        runtime = _run_commandlet(unreal_cli, temp_project, input_path, receipt_path, stdout_path, stderr_path)
    else:
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(preflight, encoding="utf-8")

    report = _report(
        stamp=stamp,
        unreal_cli=unreal_cli,
        build_artifact=build_artifact,
        plugin_package=plugin_package,
        attach_timing_path=attach_timing_path,
        input_path=input_path,
        receipt_path=receipt_path,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        temp_project=temp_project,
        diagnostic_input=diagnostic_input,
        preflight_block=preflight,
        runtime=runtime,
    )
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(
        json.dumps(
            {
                "ok": summary["runtimeSucceeded"],
                "path": str(output_path),
                "gate": summary["gate"],
                "returnCode": summary["returnCode"],
                "requested": summary["requestedAnimSequencePaths"],
                "loaded": summary["loadedSequences"],
                "notifyRows": summary["notifyRows"],
                "missingAttachTimingEvents": summary["missingAttachTimingEvents"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _find_unreal_cli() -> Optional[Path]:
    env_path = os.environ.get("AI_TOOL_TA_UNREAL_CLI")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    for name in ("UnrealEditor-Cmd", "UnrealEditor-Cmd.exe", "UnrealEditor", "UnrealEditor.exe"):
        found = shutil.which(name)
        if found:
            return Path(found)
    for candidate in COMMON_UNREAL_CLI:
        path = Path(candidate)
        if path.exists():
            return path
    return None


def _resolve_build_artifact() -> Optional[Path]:
    for env_name in ("AI_TOOL_TA_ANIM_NOTIFY_NATIVE_BUILD_ARTIFACT", "AI_TOOL_TA_ANIM_NOTIFY_BRIDGE_BUILD_ARTIFACT"):
        env_path = os.environ.get(env_name)
        if env_path and Path(env_path).exists():
            return Path(env_path)
    manifest = _read_json(PUBLIC_MANIFEST)
    path = _public_to_path(manifest.get("unrealAnimationNotifyNativeBridgeBuildArtifact"))
    if path and path.exists():
        return path
    candidates = sorted(ARTIFACT_DIR.glob("unreal-animation-notify-native-bridge-build-*.json"), key=lambda item: item.stat().st_mtime)
    for candidate in reversed(candidates):
        try:
            data = _read_json(candidate)
        except Exception:
            continue
        if data.get("summary", {}).get("gate") == "Ready":
            return candidate
    return None


def _resolve_attach_timing_artifact() -> Optional[Path]:
    env_path = os.environ.get("AI_TOOL_TA_ANIM_ATTACH_TIMING_ARTIFACT")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    manifest = _read_json(PUBLIC_MANIFEST)
    path = _public_to_path(manifest.get("unrealAnimationAttachTimingReadinessArtifact"))
    if path and path.exists():
        return path
    candidates = sorted(ARTIFACT_DIR.glob("unreal-animation-attach-timing-readiness-*.json"), key=lambda item: item.stat().st_mtime)
    return candidates[-1] if candidates else None


def _plugin_package_dir(build_artifact: Optional[Path]) -> Optional[Path]:
    if not build_artifact or not build_artifact.exists():
        return None
    data = _read_json(build_artifact)
    path = _public_to_path(data.get("summary", {}).get("packageDir") or data.get("build", {}).get("packageDir"))
    if path and (path / ("%s.uplugin" % PLUGIN_NAME)).exists():
        return path
    return None


def _preflight(
    unreal_cli: Optional[Path],
    build_artifact: Optional[Path],
    plugin_package: Optional[Path],
    attach_timing_path: Optional[Path],
    diagnostic_input: Dict[str, Any],
) -> Optional[str]:
    if not unreal_cli:
        return "blocked_by_missing_unreal_editor_cmd"
    if not build_artifact:
        return "blocked_by_missing_anim_notify_native_build_artifact"
    if not plugin_package:
        return "blocked_by_missing_packaged_anim_notify_bridge_plugin"
    if not SOURCE_PROJECT.exists():
        return "blocked_by_missing_source_unreal_project"
    if not attach_timing_path:
        return "blocked_by_missing_attach_timing_readiness_artifact"
    if not diagnostic_input.get("animationAssetPaths"):
        return "blocked_by_missing_animation_asset_paths"
    return None


def _build_input_receipt(attach_timing_path: Optional[Path], attach_timing_report: Dict[str, Any]) -> Dict[str, Any]:
    intents = attach_timing_report.get("facts", {}).get("intents", [])
    rows: List[Dict[str, Any]] = []
    asset_paths: List[str] = []
    required_events: List[str] = []
    for intent in intents:
        paths = [str(item) for item in intent.get("animationAssetPaths", []) if item]
        for path in paths:
            if path not in asset_paths:
                asset_paths.append(path)
        for event_name in intent.get("requiredAttachTimingEvents", []):
            if event_name not in required_events:
                required_events.append(str(event_name))
        rows.append(
            {
                "id": intent.get("id"),
                "assetId": intent.get("assetId"),
                "slotRole": intent.get("slotRole"),
                "sourceReadinessState": intent.get("sourceReadinessState"),
                "publishRequired": intent.get("publishRequired"),
                "animationAssetPaths": paths,
                "requiredAttachTimingEvents": intent.get("requiredAttachTimingEvents", []),
                "previousMissingAttachTimingEvents": intent.get("missingAttachTimingEvents", []),
            }
        )
    return {
        "schema": "ai-tool-ta-anim-notify-native-diagnostics-input@0.1.0",
        "sourceAttachTimingReadiness": public_path(attach_timing_path) if attach_timing_path else None,
        "sourceReportVersion": attach_timing_report.get("reportVersion"),
        "sourceGate": attach_timing_report.get("evaluation", {}).get("summary", {}).get("gate"),
        "animationAssetPaths": asset_paths,
        "requiredAttachTimingEvents": required_events,
        "intents": rows,
        "writeBoundary": {
            "mutation": "native_read_only_diagnostics",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
        },
    }


def _prepare_temp_project(temp_project_dir: Path, temp_project: Path, plugin_package: Path) -> None:
    if temp_project_dir.exists():
        shutil.rmtree(temp_project_dir)
    (temp_project_dir / "Plugins").mkdir(parents=True, exist_ok=True)
    shutil.copytree(plugin_package, temp_project_dir / "Plugins" / PLUGIN_NAME)
    if (SOURCE_PROJECT.parent / "Config").exists():
        shutil.copytree(SOURCE_PROJECT.parent / "Config", temp_project_dir / "Config")
    if (SOURCE_PROJECT.parent / "Content").exists():
        shutil.copytree(SOURCE_PROJECT.parent / "Content", temp_project_dir / "Content")
    project = json.loads(SOURCE_PROJECT.read_text(encoding="utf-8"))
    plugins = [item for item in project.get("Plugins", []) if item.get("Name") != PLUGIN_NAME]
    plugins.append({"Name": PLUGIN_NAME, "Enabled": True})
    project["Plugins"] = plugins
    project["Description"] = "Temporary AI Tool TA animation notify native diagnostics project."
    temp_project.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_commandlet(
    unreal_cli: Path,
    temp_project: Path,
    input_path: Path,
    receipt_path: Path,
    stdout_path: Path,
    stderr_path: Path,
) -> Dict[str, Any]:
    command = [
        str(unreal_cli),
        str(temp_project),
        "-run=%s" % COMMANDLET_NAME,
        "-Input=%s" % str(input_path),
        "-Output=%s" % str(receipt_path),
        "-unattended",
        "-nop4",
        "-nosplash",
        "-NoAssetRegistryCache",
        "-NoLogTimes",
    ]
    runtime_error = None
    try:
        completed = subprocess.run(
            command,
            cwd=str(temp_project.parent),
            text=False,
            capture_output=True,
            timeout=300,
        )
        stdout = _decode_output(completed.stdout)
        stderr = _decode_output(completed.stderr)
        return_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = _decode_output(exc.stdout)
        stderr = _decode_output(exc.stderr) + "\nCOMMANDLET_TIMEOUT: UnrealEditor-Cmd exceeded 300 seconds."
        return_code = -1
        runtime_error = "timeout"
    except Exception as exc:
        stdout = ""
        stderr = "COMMANDLET_EXCEPTION: %s" % exc
        return_code = -1
        runtime_error = "exception"

    stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
    combined = stdout + "\n" + stderr
    output_payload = _read_json(receipt_path) if receipt_path.exists() else {}
    return {
        "command": command,
        "returnCode": return_code,
        "runtimeError": runtime_error,
        "stdoutLog": public_path(stdout_path),
        "stderrLog": public_path(stderr_path),
        "inputReceipt": public_path(input_path),
        "outputReceipt": public_path(receipt_path) if receipt_path.exists() else None,
        "outputPayload": output_payload,
        "contractLogSeen": CONTRACT_LOG in combined,
        "diagnosticsCompleted": output_payload.get("status") == DIAGNOSTICS_STATUS,
        "commandletName": COMMANDLET_NAME,
        "errors": _error_lines(combined),
    }


def _report(
    stamp: str,
    unreal_cli: Optional[Path],
    build_artifact: Optional[Path],
    plugin_package: Optional[Path],
    attach_timing_path: Optional[Path],
    input_path: Path,
    receipt_path: Path,
    stdout_path: Path,
    stderr_path: Path,
    temp_project: Path,
    diagnostic_input: Dict[str, Any],
    preflight_block: Optional[str],
    runtime: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    runtime = runtime or {}
    output_payload = runtime.get("outputPayload") or {}
    evaluation = _evaluate(diagnostic_input, output_payload)
    summary = _summary(runtime, diagnostic_input, output_payload, evaluation, temp_project)
    if summary["runtimeSucceeded"] and summary["missingAttachTimingEvents"] == 0:
        gate = "Ready"
        l3_status = "unreal_animation_notify_native_diagnostics_timing_ready"
    elif summary["runtimeSucceeded"]:
        gate = "Blocked"
        l3_status = "unreal_animation_notify_native_diagnostics_collected_with_timing_gaps"
    else:
        gate = "Blocked"
        l3_status = preflight_block or "unreal_animation_notify_native_diagnostics_blocked"
    summary["gate"] = gate
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Animation Native Notify Bridge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-runtime-diagnostics" if runtime else "Runtime-readiness",
        "l3Status": l3_status,
        "sourceAttachTimingReadiness": public_path(attach_timing_path) if attach_timing_path else None,
        "sourceBuildArtifact": public_path(build_artifact) if build_artifact else None,
        "pluginPackageDir": public_path(plugin_package) if plugin_package else None,
        "tempProject": str(temp_project),
        "unrealCli": str(unreal_cli) if unreal_cli else None,
        "diagnosticInput": diagnostic_input,
        "runtime": runtime,
        "evaluation": evaluation,
        "summary": summary,
        "artifacts": {
            "inputReceipt": public_path(input_path),
            "outputReceipt": public_path(receipt_path) if receipt_path.exists() else None,
            "stdoutLog": public_path(stdout_path),
            "stderrLog": public_path(stderr_path),
        },
        "reviewerClaims": [
            "The diagnostics harness feeds R67 attach timing animationAssetPaths into the packaged native AI_Tool_TA_AnimNotifyBridge commandlet.",
            "Native runtime loads the referenced public AnimSequence assets and reads UAnimSequence::Notifies through C++ rather than UE Python protected properties.",
            "Commandlet/runtime success is separated from business approval: equip.attach and gear.attach remain blocked when no matching notify rows exist.",
            "The Unreal project is copied to D:\\cs\\_test and diagnostics report zero asset, engine and production writes.",
        ],
    }


def _evaluate(diagnostic_input: Dict[str, Any], output_payload: Dict[str, Any]) -> Dict[str, Any]:
    asset_rows = output_payload.get("assets", []) if isinstance(output_payload.get("assets"), list) else []
    asset_by_path = {_norm_asset_path(row.get("assetPath")): row for row in asset_rows if isinstance(row, dict)}
    rows = []
    intent_results = []
    total_required = 0
    total_matched = 0
    total_missing = 0

    for intent in diagnostic_input.get("intents", []):
        intent_required = [str(item) for item in intent.get("requiredAttachTimingEvents", []) if item]
        found = []
        asset_results = []
        for asset_path in intent.get("animationAssetPaths", []):
            asset_row = asset_by_path.get(_norm_asset_path(asset_path), {})
            notify_names = _notify_names(asset_row)
            for name in notify_names:
                if name not in found:
                    found.append(name)
            asset_results.append(
                {
                    "assetPath": asset_path,
                    "loaded": bool(asset_row.get("loaded")),
                    "collected": bool(asset_row.get("collected")),
                    "notifyCount": int(asset_row.get("notifyCount") or 0),
                    "notifyNames": notify_names,
                    "message": asset_row.get("message"),
                }
            )
        missing = [name for name in intent_required if name not in found]
        matched = [name for name in intent_required if name in found]
        total_required += len(intent_required)
        total_matched += len(matched)
        total_missing += len(missing)
        state = "pass" if not missing and intent_required else "error"
        rows.append(
            {
                "id": "%s:native-required-attach-timing-events" % intent.get("id"),
                "intentId": intent.get("id"),
                "assetId": intent.get("assetId"),
                "slotRole": intent.get("slotRole"),
                "ruleId": "native-required-attach-timing-events",
                "status": state,
                "evidence": "required=%s found=%s missing=%s" % (intent_required, found, missing),
                "fixPreview": "None" if state == "pass" else "Author explicit AnimNotify events for the attach timing contract.",
            }
        )
        intent_results.append(
            {
                "intentId": intent.get("id"),
                "assetId": intent.get("assetId"),
                "slotRole": intent.get("slotRole"),
                "publishRequired": intent.get("publishRequired"),
                "requiredAttachTimingEvents": intent_required,
                "matchedAttachTimingEvents": matched,
                "missingAttachTimingEvents": missing,
                "assetResults": asset_results,
                "readinessState": "TimingReady" if not missing and intent_required else "TimingBlocked",
            }
        )

    loaded = int(output_payload.get("loadedSequences") or 0)
    requested = int(output_payload.get("requestedAnimSequencePaths") or 0)
    rows.append(
        {
            "id": "native-diagnostics:asset-loading",
            "ruleId": "native-animsequence-loading",
            "status": "pass" if requested > 0 and loaded == requested else "error",
            "evidence": "requested=%s loaded=%s" % (requested, loaded),
            "fixPreview": "None" if requested > 0 and loaded == requested else "Fix public AnimSequence paths or temp project content copy.",
        }
    )
    rows.append(
        {
            "id": "native-diagnostics:read-only-boundary",
            "ruleId": "read-only-boundary",
            "status": (
                "pass"
                if int(output_payload.get("assetWrites") or 0) == 0
                and int(output_payload.get("engineWrites") or 0) == 0
                and int(output_payload.get("productionWrites") or 0) == 0
                else "error"
            ),
            "evidence": "assetWrites=%s engineWrites=%s productionWrites=%s"
            % (
                output_payload.get("assetWrites"),
                output_payload.get("engineWrites"),
                output_payload.get("productionWrites"),
            ),
            "fixPreview": "None",
        }
    )

    return {
        "schema": "unreal-animation-notify-native-diagnostics-evaluation@0.1.0",
        "summary": {
            "intentCount": len(diagnostic_input.get("intents", [])),
            "requiredAttachTimingEvents": total_required,
            "matchedAttachTimingEvents": total_matched,
            "missingAttachTimingEvents": total_missing,
            "timingReady": sum(1 for row in intent_results if row.get("readinessState") == "TimingReady"),
            "timingBlocked": sum(1 for row in intent_results if row.get("readinessState") == "TimingBlocked"),
            "pass": sum(1 for row in rows if row.get("status") == "pass"),
            "warning": sum(1 for row in rows if row.get("status") == "warning"),
            "error": sum(1 for row in rows if row.get("status") == "error"),
        },
        "intentResults": intent_results,
        "rows": rows,
        "ownerActions": _owner_actions(rows),
    }


def _summary(
    runtime: Dict[str, Any],
    diagnostic_input: Dict[str, Any],
    output_payload: Dict[str, Any],
    evaluation: Dict[str, Any],
    temp_project: Path,
) -> Dict[str, Any]:
    evaluation_summary = evaluation.get("summary", {})
    runtime_succeeded = (
        int(runtime.get("returnCode", -1)) == 0
        and bool(runtime.get("contractLogSeen"))
        and output_payload.get("status") == DIAGNOSTICS_STATUS
    )
    asset_rows = output_payload.get("assets", []) if isinstance(output_payload.get("assets"), list) else []
    requested = int(output_payload.get("requestedAnimSequencePaths") or len(diagnostic_input.get("animationAssetPaths", [])))
    loaded = int(output_payload.get("loadedSequences") or 0)
    return {
        "gate": "Blocked",
        "runtimeSucceeded": runtime_succeeded,
        "returnCode": runtime.get("returnCode"),
        "commandletName": COMMANDLET_NAME,
        "commandletLoaded": bool(runtime.get("contractLogSeen")),
        "diagnosticsCompleted": output_payload.get("status") == DIAGNOSTICS_STATUS,
        "outputStatus": output_payload.get("status"),
        "inputReceipt": runtime.get("inputReceipt"),
        "outputReceipt": runtime.get("outputReceipt"),
        "requestedAnimSequencePaths": requested,
        "loadedSequences": loaded,
        "missingSequences": max(requested - loaded, 0),
        "assetRows": len(asset_rows),
        "notifyRows": int(output_payload.get("notifyRows") or 0),
        "requiredAttachTimingEvents": evaluation_summary.get("requiredAttachTimingEvents", 0),
        "matchedAttachTimingEvents": evaluation_summary.get("matchedAttachTimingEvents", 0),
        "missingAttachTimingEvents": evaluation_summary.get("missingAttachTimingEvents", 0),
        "timingReady": evaluation_summary.get("timingReady", 0),
        "timingBlocked": evaluation_summary.get("timingBlocked", 0),
        "passChecks": evaluation_summary.get("pass", 0),
        "warningChecks": evaluation_summary.get("warning", 0),
        "errorChecks": evaluation_summary.get("error", 0),
        "errorLines": len(runtime.get("errors", [])),
        "tempProjectWrites": _count_files(temp_project.parent) if temp_project.parent.exists() else 0,
        "assetWrites": int(output_payload.get("assetWrites") or 0),
        "engineWrites": int(output_payload.get("engineWrites") or 0),
        "productionWrites": int(output_payload.get("productionWrites") or 0),
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    owner_by_rule = {
        "native-required-attach-timing-events": "animation-gameplay-owner",
        "native-animsequence-loading": "engine-ta",
        "read-only-boundary": "tool-ta",
    }
    for row in rows:
        if row.get("status") == "pass":
            continue
        actions.append(
            {
                "id": "anim-notify-native-diagnostics-action:%s" % row.get("id"),
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


def _notify_names(asset_row: Dict[str, Any]) -> List[str]:
    names = []
    for item in asset_row.get("notifies", []) if isinstance(asset_row.get("notifies"), list) else []:
        if not isinstance(item, dict):
            continue
        value = str(item.get("notifyName") or "")
        if value and value not in names:
            names.append(value)
    return names


def _public_to_path(value: Any) -> Optional[Path]:
    if not value:
        return None
    text = str(value)
    if text.startswith("<repo>\\") or text.startswith("<repo>/"):
        return PORTFOLIO_ROOT / text[len("<repo>\\") :].replace("/", "\\")
    return Path(text)


def _read_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _decode_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _error_lines(text: str) -> List[str]:
    rows = []
    for line in text.splitlines():
        lower = line.lower()
        if "warningsaserrors" in lower:
            continue
        if "failed to delete old shader autogen file" in lower:
            continue
        if "warning/error summary" in lower:
            continue
        if "error " in lower or ": error" in lower or "failed" in lower or "exception" in lower:
            rows.append(line.strip())
    return rows[:80]


def _count_files(path: Path) -> int:
    try:
        return sum(1 for item in path.rglob("*") if item.is_file())
    except Exception:
        return 0


def _norm_asset_path(value: Any) -> str:
    text = str(value or "")
    if "." in text:
        text = text.split(".", 1)[0]
    return text.lower()


def public_path(path: Optional[Path]) -> Optional[str]:
    if path is None:
        return None
    try:
        return "<repo>\\" + str(path.resolve().relative_to(PORTFOLIO_ROOT.resolve())).replace("/", "\\")
    except Exception:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
