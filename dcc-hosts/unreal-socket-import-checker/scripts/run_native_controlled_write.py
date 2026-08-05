from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Optional

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
from run_native_receipt_dryrun import (
    SOURCE_EXECUTOR,
    _build_receipt,
    _latest_ready_build_artifact,
    _read_json,
)


ARTIFACT_DIR = ROOT / "artifacts"
REPORT_VERSION = "unreal-socket-native-controlled-write@0.1.0"
CONTROLLED_LOG = "Apply/post-check/rollback completed."


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-socket-native-controlled-write-%s.json" % stamp)
    stdout_path = LOG_DIR / ("unreal-socket-native-controlled-write-%s.stdout.log" % stamp)
    stderr_path = LOG_DIR / ("unreal-socket-native-controlled-write-%s.stderr.log" % stamp)
    temp_project_dir = TEMP_ROOT / ("atsb-controlled-write-%s" % stamp)
    temp_project = temp_project_dir / "AI_Tool_TA_ControlledWrite.uproject"
    receipt_path = temp_project_dir / "Saved" / "AI_Tool_TA" / "socket-authoring-receipt.json"
    commandlet_output = temp_project_dir / "Saved" / "AI_Tool_TA" / "socket-authoring-controlled-write-result.json"

    unreal_cli = _find_unreal_cli()
    build_artifact = _latest_ready_build_artifact()
    plugin_package = _plugin_package_dir(build_artifact)
    source_executor = _read_json(SOURCE_EXECUTOR) if SOURCE_EXECUTOR.exists() else None
    receipt = _build_receipt(source_executor) if source_executor else None
    preflight = _preflight(unreal_cli, build_artifact, plugin_package, receipt)

    runtime: Optional[Dict[str, Any]] = None
    target_uasset: Optional[Path] = None
    backup_uasset: Optional[Path] = None
    pre_hash: Optional[str] = None
    final_hash: Optional[str] = None
    restored_hash: Optional[str] = None
    restored_by_harness = False

    if not preflight:
        _prepare_temp_project(temp_project_dir, temp_project, plugin_package)
        target_uasset = _target_uasset(temp_project_dir, receipt)
        if not target_uasset.exists():
            preflight = "blocked_by_missing_temp_target_skeleton_uasset"
            stdout_path.write_text("", encoding="utf-8")
            stderr_path.write_text(preflight, encoding="utf-8")
        else:
            backup_uasset = target_uasset.with_suffix(target_uasset.suffix + ".pre_r65_backup")
            shutil.copy2(target_uasset, backup_uasset)
            pre_hash = _sha1(target_uasset)
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
            runtime = _run_controlled_write(unreal_cli, temp_project, receipt_path, commandlet_output, stdout_path, stderr_path)
            final_hash = _sha1(target_uasset) if target_uasset.exists() else None
            if backup_uasset.exists() and target_uasset.exists() and final_hash != pre_hash:
                shutil.copy2(backup_uasset, target_uasset)
                restored_by_harness = True
                restored_hash = _sha1(target_uasset)
            else:
                restored_hash = final_hash
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
        target_uasset=target_uasset,
        backup_uasset=backup_uasset,
        pre_hash=pre_hash,
        final_hash=final_hash,
        restored_hash=restored_hash,
        restored_by_harness=restored_by_harness,
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
                "applied": summary["applied"],
                "rollbackRemoved": summary["rollbackRemoved"],
                "finalHashRestored": summary["finalHashRestored"],
                "productionWrites": summary["productionWrites"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


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
    target = str(receipt.get("targetSkeletonPackage") or "")
    if not target.startswith("/Game/AI_Tool_TA/"):
        return "blocked_by_non_public_fixture_target"
    return None


def _target_uasset(temp_project_dir: Path, receipt: Dict[str, Any]) -> Path:
    package_path = str(receipt.get("targetSkeletonPackage") or receipt.get("targetSkeleton") or "")
    if "." in package_path.rsplit("/", 1)[-1]:
        package_path = package_path.split(".", 1)[0]
    relative = package_path.replace("/Game/", "Content/").replace("/", "\\") + ".uasset"
    return temp_project_dir / relative


def _run_controlled_write(
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
        "-Apply",
        "-Rollback",
        "-AllowPublicFixtureWrite",
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
        stderr = _decode_output(exc.stderr) + "\nCONTROLLED_WRITE_TIMEOUT: UnrealEditor-Cmd exceeded 300 seconds."
        return_code = -1
        runtime_error = "timeout"
    except Exception as exc:
        stdout = ""
        stderr = "CONTROLLED_WRITE_EXCEPTION: %s" % exc
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
        "controlledWriteLogSeen": CONTROLLED_LOG in combined,
        "errors": _error_lines(combined),
    }


def _report(
    unreal_cli: Optional[Path],
    build_artifact: Optional[Path],
    plugin_package: Optional[Path],
    source_executor: Optional[Path],
    receipt_path: Path,
    commandlet_output: Path,
    target_uasset: Optional[Path],
    backup_uasset: Optional[Path],
    pre_hash: Optional[str],
    final_hash: Optional[str],
    restored_hash: Optional[str],
    restored_by_harness: bool,
    stdout_path: Path,
    stderr_path: Path,
    preflight_block: Optional[str],
    runtime: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    runtime = runtime or {}
    output_json = runtime.get("outputJson") or {}
    return_code = int(runtime.get("returnCode", -1))
    request_count = int(output_json.get("requestCount", 0) or 0)
    applied = int(output_json.get("applied", 0) or 0)
    post_check_present = int(output_json.get("postCheckPresent", 0) or 0)
    rollback_removed = int(output_json.get("rollbackRemoved", 0) or 0)
    post_rollback_present = int(output_json.get("postRollbackPresent", 0) or 0)
    asset_writes = int(output_json.get("assetWrites", 0) or 0)
    production_writes = int(output_json.get("productionWrites", 0) or 0)
    final_hash_restored = bool(pre_hash and restored_hash and pre_hash == restored_hash)
    ready = (
        return_code == 0
        and runtime.get("controlledWriteLogSeen")
        and output_json.get("status") == "apply_postcheck_rollback_completed"
        and output_json.get("targetLoaded") is True
        and request_count > 0
        and applied == request_count
        and post_check_present >= request_count
        and rollback_removed == applied
        and post_rollback_present == 0
        and asset_writes >= 2
        and production_writes == 0
        and final_hash_restored
    )
    gate = "Ready" if ready else "Blocked"
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Import Checker",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-runtime-controlled-write" if runtime else "Runtime-readiness",
        "l3Status": "unreal_socket_native_controlled_write_rolled_back" if ready else (preflight_block or "unreal_socket_native_controlled_write_blocked"),
        "sourceBuildArtifact": public_path(build_artifact) if build_artifact else None,
        "pluginPackageDir": public_path(plugin_package) if plugin_package else None,
        "sourceExecutorArtifact": public_path(source_executor) if source_executor else None,
        "receiptPath": str(receipt_path),
        "commandletOutput": str(commandlet_output),
        "targetUasset": str(target_uasset) if target_uasset else None,
        "backupUasset": str(backup_uasset) if backup_uasset else None,
        "unrealCli": str(unreal_cli) if unreal_cli else None,
        "runtime": runtime,
        "hashes": {
            "preflight": pre_hash,
            "afterCommandlet": final_hash,
            "restored": restored_hash,
            "restoredByHarness": restored_by_harness,
        },
        "summary": {
            "gate": gate,
            "returnCode": runtime.get("returnCode"),
            "targetLoaded": bool(output_json.get("targetLoaded")),
            "requestCount": request_count,
            "applied": applied,
            "postCheckPresent": post_check_present,
            "rollbackRemoved": rollback_removed,
            "postRollbackPresent": post_rollback_present,
            "savedAfterApply": bool(output_json.get("savedAfterApply")),
            "savedAfterRollback": bool(output_json.get("savedAfterRollback")),
            "assetWrites": asset_writes,
            "engineWrites": int(output_json.get("engineWrites", 0) or 0),
            "productionWrites": production_writes,
            "persistentMutation": bool(output_json.get("persistentMutation")),
            "finalHashRestored": final_hash_restored,
            "restoredByHarness": restored_by_harness,
            "controlledWriteLogSeen": bool(runtime.get("controlledWriteLogSeen")),
            "errorLines": len(runtime.get("errors", [])),
        },
        "reviewerClaims": [
            "The commandlet requires -Apply, -Rollback and -AllowPublicFixtureWrite before mutating a Skeleton.",
            "The target Skeleton is copied into a temp Unreal project and must live under /Game/AI_Tool_TA.",
            "The commandlet creates the requested sockets, saves the public fixture package, post-checks runtime presence, removes the created sockets, saves rollback and reports write counters.",
            "The harness restores the target uasset bytes to the preflight hash after commandlet rollback, leaving no persistent temp fixture mutation.",
        ],
    }


def _sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
