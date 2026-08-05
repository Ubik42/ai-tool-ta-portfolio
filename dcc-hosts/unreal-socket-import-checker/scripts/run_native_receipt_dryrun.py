from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from run_native_commandlet_probe import (
    COMMANDLET_NAME,
    LOG_DIR,
    ROOT,
    TEMP_ROOT,
    _decode_output,
    _error_lines,
    _find_unreal_cli,
    _plugin_package_dir,
    _prepare_temp_project,
    public_path,
)


ARTIFACT_DIR = ROOT / "artifacts"
PORTFOLIO_ROOT = ROOT.parents[1]
SOURCE_EXECUTOR = ARTIFACT_DIR / "unreal-socket-authoring-executor-20260805-222014.json"
REPORT_VERSION = "unreal-socket-native-receipt-dryrun@0.1.0"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-socket-native-receipt-dryrun-%s.json" % stamp)
    stdout_path = LOG_DIR / ("unreal-socket-native-receipt-dryrun-%s.stdout.log" % stamp)
    stderr_path = LOG_DIR / ("unreal-socket-native-receipt-dryrun-%s.stderr.log" % stamp)
    temp_project_dir = TEMP_ROOT / ("atsb-receipt-dryrun-%s" % stamp)
    temp_project = temp_project_dir / "AI_Tool_TA_ReceiptDryRun.uproject"
    receipt_path = temp_project_dir / "Saved" / "AI_Tool_TA" / "socket-authoring-receipt.json"
    commandlet_output = temp_project_dir / "Saved" / "AI_Tool_TA" / "socket-authoring-dryrun-result.json"

    unreal_cli = _find_unreal_cli()
    build_artifact = _latest_ready_build_artifact()
    plugin_package = _plugin_package_dir(build_artifact)
    source_executor = _read_json(SOURCE_EXECUTOR) if SOURCE_EXECUTOR.exists() else None
    receipt = _build_receipt(source_executor) if source_executor else None
    preflight = _preflight(unreal_cli, build_artifact, plugin_package, receipt)

    runtime: Optional[Dict[str, Any]] = None
    if not preflight:
        _prepare_temp_project(temp_project_dir, temp_project, plugin_package)
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        runtime = _run_dryrun(unreal_cli, temp_project, receipt_path, commandlet_output, stdout_path, stderr_path)
    else:
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(preflight, encoding="utf-8")

    report = _report(
        unreal_cli=unreal_cli,
        build_artifact=build_artifact,
        plugin_package=plugin_package,
        source_executor=SOURCE_EXECUTOR if source_executor else None,
        receipt_path=receipt_path,
        commandlet_output=commandlet_output,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        preflight_block=preflight,
        runtime=runtime,
    )
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(
        json.dumps(
            {
                "ok": summary["gate"] == "Ready",
                "path": str(output_path),
                "gate": summary["gate"],
                "returnCode": summary["returnCode"],
                "targetLoaded": summary["targetLoaded"],
                "requestCount": summary["requestCount"],
                "wouldCreate": summary["wouldCreate"],
                "errorLines": summary["errorLines"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _latest_ready_build_artifact() -> Optional[Path]:
    env_path = os.environ.get("AI_TOOL_TA_SOCKET_NATIVE_BUILD_ARTIFACT")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    candidates = sorted(ARTIFACT_DIR.glob("unreal-socket-native-bridge-build-*.json"), key=lambda item: item.stat().st_mtime)
    for candidate in reversed(candidates):
        try:
            data = _read_json(candidate)
        except Exception:
            continue
        if data.get("summary", {}).get("gate") == "Ready":
            return candidate
    return None


def _build_receipt(source_executor: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    operations = source_executor.get("operations", [])
    selected = None
    for operation in operations:
        if operation.get("sourceStatus") == "Ready" and operation.get("ownerState") == "approved":
            selected = operation
            break
    if not selected:
        return None
    requests = []
    for socket in selected.get("expectedSockets", []):
        requests.append(
            {
                "socketName": socket.get("exportName"),
                "boneName": socket.get("parentJoint"),
                "relativeLocation": socket.get("translate", [0.0, 0.0, 0.0]),
                "relativeRotation": socket.get("rotate", [0.0, 0.0, 0.0]),
                "relativeScale": socket.get("scale", [1.0, 1.0, 1.0]),
                "sourceReceiptId": "%s:%s" % (selected.get("id"), socket.get("exportName")),
            }
        )
    return {
        "schema": "ai-tool-ta-socket-authoring-receipt@0.1.0",
        "mode": "dry-run",
        "sourceExecutorArtifact": public_path(SOURCE_EXECUTOR),
        "sourceOperationId": selected.get("id"),
        "assetId": selected.get("assetId"),
        "targetSkeleton": _object_path(selected.get("skeletonPath")),
        "targetSkeletonPackage": selected.get("skeletonPath"),
        "requests": requests,
    }


def _object_path(package_path: Any) -> str:
    text = str(package_path or "")
    if "." in text.rsplit("/", 1)[-1]:
        return text
    return "%s.%s" % (text, text.rsplit("/", 1)[-1])


def _preflight(
    unreal_cli: Optional[Path],
    build_artifact: Optional[Path],
    plugin_package: Optional[Path],
    receipt: Optional[Dict[str, Any]],
) -> Optional[str]:
    if not unreal_cli:
        return "blocked_by_missing_unreal_editor_cmd"
    if not build_artifact:
        return "blocked_by_missing_native_build_artifact"
    if not plugin_package:
        return "blocked_by_missing_packaged_socket_bridge_plugin"
    if not receipt:
        return "blocked_by_missing_approved_socket_receipt"
    if not receipt.get("requests"):
        return "blocked_by_empty_socket_receipt"
    return None


def _run_dryrun(
    unreal_cli: Path,
    temp_project: Path,
    receipt_path: Path,
    commandlet_output: Path,
    stdout_path: Path,
    stderr_path: Path,
) -> Dict[str, Any]:
    command = [
        str(unreal_cli),
        str(temp_project),
        "-run=%s" % COMMANDLET_NAME,
        "-Input=%s" % str(receipt_path),
        "-Output=%s" % str(commandlet_output),
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
        stderr = _decode_output(exc.stderr) + "\nRECEIPT_DRYRUN_TIMEOUT: UnrealEditor-Cmd exceeded 300 seconds."
        return_code = -1
        runtime_error = "timeout"
    except Exception as exc:
        stdout = ""
        stderr = "RECEIPT_DRYRUN_EXCEPTION: %s" % exc
        return_code = -1
        runtime_error = "exception"
    stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
    output_json = _read_json(commandlet_output) if commandlet_output.exists() else None
    combined = stdout + "\n" + stderr
    return {
        "command": command,
        "returnCode": return_code,
        "runtimeError": runtime_error,
        "stdoutLog": public_path(stdout_path),
        "stderrLog": public_path(stderr_path),
        "commandletOutput": str(commandlet_output),
        "outputJson": output_json,
        "dryRunLogSeen": "Dry-run receipt parsed." in combined,
        "errors": _error_lines(combined),
    }


def _report(
    unreal_cli: Optional[Path],
    build_artifact: Optional[Path],
    plugin_package: Optional[Path],
    source_executor: Optional[Path],
    receipt_path: Path,
    commandlet_output: Path,
    stdout_path: Path,
    stderr_path: Path,
    preflight_block: Optional[str],
    runtime: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    runtime = runtime or {}
    output_json = runtime.get("outputJson") or {}
    request_count = int(output_json.get("requestCount", 0) or 0)
    result_count = int(output_json.get("resultCount", 0) or 0)
    would_create = int(output_json.get("wouldCreate", 0) or 0)
    target_loaded = bool(output_json.get("targetLoaded"))
    ready = (
        int(runtime.get("returnCode", -1)) == 0
        and runtime.get("dryRunLogSeen")
        and output_json.get("status") == "dry_run_completed"
        and target_loaded
        and request_count > 0
        and result_count == request_count
    )
    gate = "Ready" if ready else "Blocked"
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Import Checker",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-runtime-dryrun" if runtime else "Runtime-readiness",
        "l3Status": "unreal_socket_native_receipt_dryrun_completed" if ready else (preflight_block or "unreal_socket_native_receipt_dryrun_blocked"),
        "sourceBuildArtifact": public_path(build_artifact) if build_artifact else None,
        "pluginPackageDir": public_path(plugin_package) if plugin_package else None,
        "sourceExecutorArtifact": public_path(source_executor) if source_executor else None,
        "receiptPath": str(receipt_path),
        "commandletOutput": str(commandlet_output),
        "unrealCli": str(unreal_cli) if unreal_cli else None,
        "runtime": runtime,
        "summary": {
            "gate": gate,
            "returnCode": runtime.get("returnCode"),
            "targetLoaded": target_loaded,
            "requestCount": request_count,
            "resultCount": result_count,
            "wouldCreate": would_create,
            "alreadyPresent": int(output_json.get("alreadyPresent", 0) or 0),
            "dryRunCompleted": output_json.get("status") == "dry_run_completed",
            "dryRunLogSeen": bool(runtime.get("dryRunLogSeen")),
            "errorLines": len(runtime.get("errors", [])),
            "assetWrites": int(output_json.get("assetWrites", 0) or 0),
            "engineWrites": int(output_json.get("engineWrites", 0) or 0),
            "productionWrites": int(output_json.get("productionWrites", 0) or 0),
        },
        "reviewerClaims": [
            "The dry-run receipt is generated from the approved R40 socket authoring executor operation.",
            "The commandlet parses JSON receipt input, loads the target public Skeleton and calls the native socket bridge in dry-run mode.",
            "The output JSON records targetLoaded, requestCount, resultCount, wouldCreate and write counters.",
            "No socket is saved in R64; this is the post-parse dry-run gate before controlled write and rollback.",
        ],
    }


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
