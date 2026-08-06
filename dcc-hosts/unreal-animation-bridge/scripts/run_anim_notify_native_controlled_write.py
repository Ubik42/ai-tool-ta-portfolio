from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from run_anim_notify_native_diagnostics import (
    COMMANDLET_NAME,
    PLUGIN_NAME,
    PUBLIC_MANIFEST,
    SOURCE_PROJECT,
    _decode_output,
    _error_lines,
    _find_unreal_cli,
    _plugin_package_dir,
    _prepare_temp_project,
    _public_to_path,
    _read_json,
    public_path,
)


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
LOG_DIR = ARTIFACT_DIR / "unreal-animation-native-notify-controlled-write-logs"
RECEIPT_DIR = ARTIFACT_DIR / "unreal-animation-native-notify-controlled-write-receipts"
TEMP_ROOT = Path(
    os.environ.get(
        "AI_TOOL_TA_ANIM_NOTIFY_CONTROLLED_WRITE_ROOT",
        r"D:\cs\_test\ai_tool_ta_anim_notify_controlled_write",
    )
)
REPORT_VERSION = "unreal-animation-notify-native-controlled-write@0.1.0"
CONTROLLED_LOG = "Anim notify apply/post-check/rollback completed."
CONTROLLED_STATUS = "apply_postcheck_rollback_completed"


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")

    output_path = ARTIFACT_DIR / ("unreal-animation-notify-native-controlled-write-%s.json" % stamp)
    stdout_path = LOG_DIR / ("unreal-animation-notify-native-controlled-write-%s.stdout.log" % stamp)
    stderr_path = LOG_DIR / ("unreal-animation-notify-native-controlled-write-%s.stderr.log" % stamp)
    input_path = RECEIPT_DIR / ("unreal-animation-notify-native-controlled-write-input-%s.json" % stamp)
    receipt_path = RECEIPT_DIR / ("unreal-animation-notify-native-controlled-write-output-%s.json" % stamp)
    temp_project_dir = TEMP_ROOT / ("aanb-controlled-write-%s" % stamp)
    temp_project = temp_project_dir / "AI_Tool_TA_AnimNotifyControlledWrite.uproject"

    unreal_cli = _find_unreal_cli()
    build_artifact = _resolve_latest_build_artifact()
    plugin_package = _plugin_package_dir(build_artifact)
    attach_timing_path = _resolve_attach_timing_artifact()
    attach_timing_report = _read_json(attach_timing_path) if attach_timing_path else {}
    input_receipt = _build_input_receipt(attach_timing_path, attach_timing_report)
    input_path.write_text(json.dumps(input_receipt, ensure_ascii=False, indent=2), encoding="utf-8")

    preflight = _preflight(unreal_cli, build_artifact, plugin_package, attach_timing_path, input_receipt)
    runtime: Optional[Dict[str, Any]] = None
    target_hashes: List[Dict[str, Any]] = []
    restored_by_harness = False

    if not preflight:
        _prepare_temp_project(temp_project_dir, temp_project, plugin_package)
        target_hashes = _prepare_target_hashes(temp_project_dir, input_receipt)
        missing_targets = [row for row in target_hashes if not row.get("exists")]
        if missing_targets:
            preflight = "blocked_by_missing_temp_animsequence_uasset"
            stdout_path.write_text("", encoding="utf-8")
            stderr_path.write_text(preflight, encoding="utf-8")
        else:
            runtime = _run_controlled_write(unreal_cli, temp_project, input_path, receipt_path, stdout_path, stderr_path)
            restored_by_harness = _restore_target_hashes(target_hashes)
    else:
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(preflight, encoding="utf-8")

    report = _report(
        unreal_cli=unreal_cli,
        build_artifact=build_artifact,
        plugin_package=plugin_package,
        attach_timing_path=attach_timing_path,
        input_path=input_path,
        receipt_path=receipt_path,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        temp_project=temp_project,
        input_receipt=input_receipt,
        target_hashes=target_hashes,
        restored_by_harness=restored_by_harness,
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
                "requests": summary["requestCount"],
                "applied": summary["applied"],
                "postCheckPresent": summary["postCheckPresent"],
                "rollbackRemoved": summary["rollbackRemoved"],
                "finalHashRestored": summary["finalHashRestored"],
                "productionWrites": summary["productionWrites"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _resolve_latest_build_artifact() -> Optional[Path]:
    for env_name in ("AI_TOOL_TA_ANIM_NOTIFY_NATIVE_BUILD_ARTIFACT", "AI_TOOL_TA_ANIM_NOTIFY_BRIDGE_BUILD_ARTIFACT"):
        env_path = os.environ.get(env_name)
        if env_path and Path(env_path).exists():
            return Path(env_path)
    candidates = sorted(ARTIFACT_DIR.glob("unreal-animation-notify-native-bridge-build-*.json"), key=lambda item: item.stat().st_mtime)
    for candidate in reversed(candidates):
        data = _read_json(candidate)
        if data.get("summary", {}).get("gate") == "Ready":
            return candidate
    manifest = _read_json(PUBLIC_MANIFEST)
    path = _public_to_path(manifest.get("unrealAnimationNotifyNativeBridgeBuildArtifact"))
    if path and path.exists():
        return path
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


def _preflight(
    unreal_cli: Optional[Path],
    build_artifact: Optional[Path],
    plugin_package: Optional[Path],
    attach_timing_path: Optional[Path],
    input_receipt: Dict[str, Any],
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
    requests = input_receipt.get("requests", [])
    if not requests:
        return "blocked_by_missing_notify_authoring_requests"
    if any(not str(row.get("animSequencePath") or "").startswith("/Game/AI_Tool_TA/") for row in requests):
        return "blocked_by_non_public_fixture_request"
    return None


def _build_input_receipt(attach_timing_path: Optional[Path], attach_timing_report: Dict[str, Any]) -> Dict[str, Any]:
    requests: List[Dict[str, Any]] = []
    intent_rows: List[Dict[str, Any]] = []
    for intent in attach_timing_report.get("facts", {}).get("intents", []):
        linked_by_path = {
            str(row.get("expectedAnimSequencePath")): row
            for row in intent.get("linkedSequences", [])
            if row.get("expectedAnimSequencePath")
        }
        animation_paths = [str(path) for path in intent.get("animationAssetPaths", []) if path]
        required_events = [str(name) for name in intent.get("requiredAttachTimingEvents", []) if name]
        for event_name in required_events:
            for anim_path in animation_paths:
                sequence = linked_by_path.get(anim_path, {})
                trigger_time = _default_trigger_time(event_name, sequence.get("playLength"))
                requests.append(
                    {
                        "sourceReceiptId": "%s:%s:%s" % (intent.get("id"), anim_path, event_name),
                        "intentId": intent.get("id"),
                        "assetId": intent.get("assetId"),
                        "slotRole": intent.get("slotRole"),
                        "animSequencePath": anim_path,
                        "notifyName": event_name,
                        "triggerTime": trigger_time,
                        "trackIndex": 0,
                        "sourceReadinessState": intent.get("readinessState"),
                        "publishRequired": intent.get("publishRequired"),
                    }
                )
        intent_rows.append(
            {
                "id": intent.get("id"),
                "assetId": intent.get("assetId"),
                "slotRole": intent.get("slotRole"),
                "sourceReadinessState": intent.get("readinessState"),
                "animationAssetPaths": animation_paths,
                "requiredAttachTimingEvents": required_events,
                "requestCount": sum(1 for row in requests if row.get("intentId") == intent.get("id")),
            }
        )

    return {
        "schema": "ai-tool-ta-anim-notify-native-controlled-write-input@0.1.0",
        "sourceAttachTimingReadiness": public_path(attach_timing_path) if attach_timing_path else None,
        "sourceReportVersion": attach_timing_report.get("reportVersion"),
        "sourceGate": attach_timing_report.get("evaluation", {}).get("summary", {}).get("gate"),
        "requests": requests,
        "intents": intent_rows,
        "writeBoundary": {
            "mutation": "public_fixture_apply_postcheck_rollback",
            "requiresApplyFlag": True,
            "requiresRollbackFlag": True,
            "requiresPublicFixtureGuard": True,
            "productionWrites": 0,
        },
    }


def _default_trigger_time(event_name: str, play_length: Any) -> float:
    base = 0.25
    lower = event_name.lower()
    if "equip" in lower:
        base = 0.35
    elif "gear" in lower:
        base = 0.48
    elif "attach" in lower:
        base = 0.30
    try:
        length = float(play_length)
    except Exception:
        length = 1.0
    return round(max(0.0, min(base, max(length - 0.01, 0.0))), 4)


def _prepare_target_hashes(temp_project_dir: Path, input_receipt: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    seen = set()
    for request in input_receipt.get("requests", []):
        asset_path = str(request.get("animSequencePath") or "")
        if not asset_path or asset_path in seen:
            continue
        seen.add(asset_path)
        target = _target_uasset(temp_project_dir, asset_path)
        backup = target.with_suffix(target.suffix + ".pre_r72_backup")
        exists = target.exists()
        row = {
            "assetPath": asset_path,
            "targetUasset": str(target),
            "backupUasset": str(backup),
            "exists": exists,
            "preHash": _sha1(target) if exists else None,
            "afterCommandletHash": None,
            "restoredHash": None,
            "finalHashRestored": False,
        }
        if exists:
            shutil.copy2(target, backup)
        rows.append(row)
    return rows


def _restore_target_hashes(rows: List[Dict[str, Any]]) -> bool:
    restored_by_harness = False
    for row in rows:
        target = Path(str(row.get("targetUasset") or ""))
        backup = Path(str(row.get("backupUasset") or ""))
        row["afterCommandletHash"] = _sha1(target) if target.exists() else None
        if backup.exists() and target.exists() and row.get("afterCommandletHash") != row.get("preHash"):
            shutil.copy2(backup, target)
            restored_by_harness = True
        row["restoredHash"] = _sha1(target) if target.exists() else None
        row["finalHashRestored"] = bool(row.get("preHash") and row.get("restoredHash") == row.get("preHash"))
    return restored_by_harness


def _run_controlled_write(
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
    output_json = _read_json(receipt_path) if receipt_path.exists() else {}
    combined = stdout + "\n" + stderr
    return {
        "command": command,
        "returnCode": return_code,
        "runtimeError": runtime_error,
        "stdoutLog": public_path(stdout_path),
        "stderrLog": public_path(stderr_path),
        "inputReceipt": public_path(input_path),
        "outputReceipt": public_path(receipt_path) if receipt_path.exists() else None,
        "outputJson": output_json,
        "commandletLoaded": "AI Tool TA Anim Notify Diagnostics Commandlet loaded." in combined,
        "controlledWriteLogSeen": CONTROLLED_LOG in combined,
        "errors": _error_lines(combined),
    }


def _report(
    unreal_cli: Optional[Path],
    build_artifact: Optional[Path],
    plugin_package: Optional[Path],
    attach_timing_path: Optional[Path],
    input_path: Path,
    receipt_path: Path,
    stdout_path: Path,
    stderr_path: Path,
    temp_project: Path,
    input_receipt: Dict[str, Any],
    target_hashes: List[Dict[str, Any]],
    restored_by_harness: bool,
    preflight_block: Optional[str],
    runtime: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    runtime = runtime or {}
    output_json = runtime.get("outputJson") or {}
    summary = _summary(runtime, output_json, input_receipt, target_hashes, restored_by_harness, temp_project)
    ready = summary["runtimeSucceeded"] and summary["requestCount"] > 0
    ready = ready and summary["applied"] == summary["requestCount"]
    ready = ready and summary["postCheckPresent"] >= summary["requestCount"]
    ready = ready and summary["rollbackRemoved"] == summary["applied"]
    ready = ready and summary["postRollbackPresent"] == 0
    ready = ready and summary["assetWrites"] >= 2
    ready = ready and summary["productionWrites"] == 0
    ready = ready and summary["finalHashRestored"]
    ready = ready and summary["errorLines"] == 0
    summary["gate"] = "Ready" if ready else "Blocked"
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Animation Native Notify Bridge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-runtime-controlled-write" if runtime else "Runtime-readiness",
        "l3Status": "unreal_animation_notify_native_controlled_write_rolled_back"
        if ready
        else (preflight_block or "unreal_animation_notify_native_controlled_write_blocked"),
        "sourceAttachTimingReadiness": public_path(attach_timing_path) if attach_timing_path else None,
        "sourceBuildArtifact": public_path(build_artifact) if build_artifact else None,
        "pluginPackageDir": public_path(plugin_package) if plugin_package else None,
        "tempProject": str(temp_project),
        "unrealCli": str(unreal_cli) if unreal_cli else None,
        "inputReceipt": public_path(input_path),
        "outputReceipt": public_path(receipt_path) if receipt_path.exists() else None,
        "runtime": runtime,
        "targetHashes": target_hashes,
        "summary": summary,
        "evaluation": _evaluation(summary, input_receipt, output_json),
        "artifacts": {
            "inputReceipt": public_path(input_path),
            "outputReceipt": public_path(receipt_path) if receipt_path.exists() else None,
            "stdoutLog": public_path(stdout_path),
            "stderrLog": public_path(stderr_path),
        },
        "reviewerClaims": [
            "The authoring harness converts R67 missing attach timing events into explicit native AnimNotify write requests.",
            "The commandlet requires -Apply, -Rollback and -AllowPublicFixtureWrite before mutating public fixture AnimSequences.",
            "The Unreal project is copied to D:\\cs\\_test; source project assets are not edited.",
            "Native runtime writes named notify events, post-checks that equip.attach / gear.attach are readable through UAnimSequence::Notifies, removes the created rows and saves rollback.",
            "The harness restores target AnimSequence uasset bytes to their preflight hashes after commandlet rollback.",
        ],
    }


def _summary(
    runtime: Dict[str, Any],
    output_json: Dict[str, Any],
    input_receipt: Dict[str, Any],
    target_hashes: List[Dict[str, Any]],
    restored_by_harness: bool,
    temp_project: Path,
) -> Dict[str, Any]:
    runtime_succeeded = (
        int(runtime.get("returnCode", -1)) == 0
        and bool(runtime.get("commandletLoaded"))
        and bool(runtime.get("controlledWriteLogSeen"))
        and output_json.get("status") == CONTROLLED_STATUS
    )
    request_count = int(output_json.get("requestCount") or len(input_receipt.get("requests", [])))
    loaded = int(output_json.get("loadedSequences") or 0)
    asset_count = int(output_json.get("assetCount") or len({row.get("animSequencePath") for row in input_receipt.get("requests", [])}))
    return {
        "gate": "Blocked",
        "runtimeSucceeded": runtime_succeeded,
        "returnCode": runtime.get("returnCode"),
        "commandletName": COMMANDLET_NAME,
        "commandletLoaded": bool(runtime.get("commandletLoaded")),
        "controlledWriteLogSeen": bool(runtime.get("controlledWriteLogSeen")),
        "outputStatus": output_json.get("status"),
        "inputReceipt": runtime.get("inputReceipt"),
        "outputReceipt": runtime.get("outputReceipt"),
        "requestCount": request_count,
        "assetCount": asset_count,
        "loadedSequences": loaded,
        "missingSequences": max(asset_count - loaded, 0),
        "alreadyPresent": int(output_json.get("alreadyPresent") or 0),
        "wouldCreate": int(output_json.get("wouldCreate") or 0),
        "applied": int(output_json.get("applied") or 0),
        "postCheckPresent": int(output_json.get("postCheckPresent") or 0),
        "rollbackRemoved": int(output_json.get("rollbackRemoved") or 0),
        "postRollbackPresent": int(output_json.get("postRollbackPresent") or 0),
        "savedAfterApply": bool(output_json.get("savedAfterApply")),
        "savedAfterRollback": bool(output_json.get("savedAfterRollback")),
        "assetWrites": int(output_json.get("assetWrites") or 0),
        "engineWrites": int(output_json.get("engineWrites") or 0),
        "productionWrites": int(output_json.get("productionWrites") or 0),
        "persistentMutation": bool(output_json.get("persistentMutation")),
        "targetHashRows": len(target_hashes),
        "finalHashRestored": bool(target_hashes) and all(bool(row.get("finalHashRestored")) for row in target_hashes),
        "restoredByHarness": restored_by_harness,
        "errorLines": len(runtime.get("errors", [])),
        "tempProjectWrites": _count_files(temp_project.parent) if temp_project.parent.exists() else 0,
    }


def _evaluation(summary: Dict[str, Any], input_receipt: Dict[str, Any], output_json: Dict[str, Any]) -> Dict[str, Any]:
    rows = [
        _row(
            "authoring-requests-parsed",
            summary.get("requestCount", 0) == len(input_receipt.get("requests", [])) and summary.get("requestCount", 0) > 0,
            "requestCount=%s sourceRequests=%s" % (summary.get("requestCount"), len(input_receipt.get("requests", []))),
            "Generate explicit AnimNotify write requests from R67 missing attach timing events.",
        ),
        _row(
            "public-fixture-targets-only",
            all(str(row.get("animSequencePath") or "").startswith("/Game/AI_Tool_TA/") for row in input_receipt.get("requests", [])),
            "targets=%s" % sorted({row.get("animSequencePath") for row in input_receipt.get("requests", [])}),
            "Limit controlled writes to public fixture assets.",
        ),
        _row(
            "native-apply-postcheck",
            summary.get("applied") == summary.get("requestCount") and summary.get("postCheckPresent", 0) >= summary.get("requestCount", 0),
            "applied=%s postCheckPresent=%s requestCount=%s"
            % (summary.get("applied"), summary.get("postCheckPresent"), summary.get("requestCount")),
            "Fix native commandlet authoring or AnimSequence notify matching.",
        ),
        _row(
            "native-rollback-clean",
            summary.get("rollbackRemoved") == summary.get("applied") and summary.get("postRollbackPresent") == 0,
            "rollbackRemoved=%s postRollbackPresent=%s" % (summary.get("rollbackRemoved"), summary.get("postRollbackPresent")),
            "Rollback every notify created by this receipt before leaving the temp project.",
        ),
        _row(
            "hash-restored",
            bool(summary.get("finalHashRestored")),
            "targetHashRows=%s restoredByHarness=%s" % (summary.get("targetHashRows"), summary.get("restoredByHarness")),
            "Restore target uasset bytes to the preflight hash after commandlet rollback.",
        ),
        _row(
            "write-boundary-clean",
            summary.get("productionWrites") == 0 and not summary.get("persistentMutation"),
            "assetWrites=%s engineWrites=%s productionWrites=%s persistentMutation=%s"
            % (
                summary.get("assetWrites"),
                summary.get("engineWrites"),
                summary.get("productionWrites"),
                summary.get("persistentMutation"),
            ),
            "Keep writes scoped to the temp public fixture project and verify no persistent mutation remains.",
        ),
    ]
    return {
        "schema": "unreal-animation-notify-native-controlled-write-evaluation@0.1.0",
        "summary": {
            "pass": sum(1 for row in rows if row["status"] == "pass"),
            "warning": sum(1 for row in rows if row["status"] == "warning"),
            "error": sum(1 for row in rows if row["status"] == "error"),
            "gate": summary.get("gate"),
        },
        "rows": rows,
        "outputAssets": output_json.get("assets", []),
    }


def _row(rule_id: str, passed: bool, evidence: str, fix_preview: str) -> Dict[str, Any]:
    return {
        "id": "anim-notify-controlled-write:%s" % rule_id,
        "ruleId": rule_id,
        "status": "pass" if passed else "error",
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _target_uasset(temp_project_dir: Path, asset_path: str) -> Path:
    package_path = asset_path.split(".", 1)[0]
    relative = package_path.replace("/Game/", "Content/").replace("/", "\\") + ".uasset"
    return temp_project_dir / relative


def _sha1(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _count_files(path: Path) -> int:
    try:
        return sum(1 for item in path.rglob("*") if item.is_file())
    except Exception:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
