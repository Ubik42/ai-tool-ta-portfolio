from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
UNREAL_PROJECT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "AI_Tool_TA_Unreal_L3.uproject"
)
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "probe_anim_notify_native_bridge.py"


COMMON_UNREAL_CLI = [
    r"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"D:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
]


def find_unreal_cli() -> Optional[str]:
    env_path = os.environ.get("AI_TOOL_TA_UNREAL_CLI")
    if env_path and Path(env_path).exists():
        return str(Path(env_path))
    for name in ("UnrealEditor-Cmd", "UnrealEditor-Cmd.exe", "UnrealEditor", "UnrealEditor.exe"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in COMMON_UNREAL_CLI:
        if Path(candidate).exists():
            return candidate
    return None


def main() -> int:
    unreal_cli = find_unreal_cli()
    source_artifact = _latest_report(
        ARTIFACT_DIR,
        "unreal-animation-attach-timing-readiness-*.json",
        "unreal-animation-attach-timing-readiness@0.1.0",
    )
    logs_dir = ARTIFACT_DIR / "unreal-animation-native-notify-bridge-logs"
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-animation-notify-native-bridge-readiness-%s.json" % stamp)
    stdout_path = logs_dir / ("unreal-animation-notify-native-bridge-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("unreal-animation-notify-native-bridge-%s.stderr.log" % stamp)

    if not source_artifact:
        print(json.dumps({"ok": False, "reason": "blocked_by_missing_attach_timing_readiness_artifact"}, ensure_ascii=False, indent=2))
        return 1
    if not unreal_cli:
        return _blocked(output_path, source_artifact, "blocked_by_missing_unreal_cli", None, None)
    if not UNREAL_PROJECT.exists():
        return _blocked(output_path, source_artifact, "blocked_by_missing_unreal_project", unreal_cli, None)

    env = os.environ.copy()
    env["AI_TOOL_TA_UNREAL_ANIMATION_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_UNREAL_ANIM_NOTIFY_BRIDGE_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_UNREAL_ANIM_NOTIFY_BRIDGE_SOURCE"] = str(source_artifact)
    env["AI_TOOL_TA_UNREAL_PROJECT"] = str(UNREAL_PROJECT)
    env["AI_TOOL_TA_UNREAL_CLI"] = str(unreal_cli)

    command = [
        str(unreal_cli),
        str(UNREAL_PROJECT),
        "-run=pythonscript",
        "-script=%s" % str(UNREAL_SCRIPT),
        "-unattended",
        "-nop4",
        "-nosplash",
        "-NullRHI",
        "-NoSound",
        "-log",
    ]
    completed = subprocess.run(command, cwd=str(ROOT), env=env, text=True, capture_output=True, timeout=240)
    stdout_path.write_text(completed.stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(completed.stderr, encoding="utf-8", errors="replace")

    ok = completed.returncode == 0 and output_path.exists()
    result = {
        "ok": ok,
        "returnCode": completed.returncode,
        "path": str(output_path) if output_path.exists() else None,
        "stdoutLog": str(stdout_path),
        "stderrLog": str(stderr_path),
        "unrealCli": str(unreal_cli),
        "project": str(UNREAL_PROJECT),
        "source": str(source_artifact),
    }
    if output_path.exists():
        report = json.loads(output_path.read_text(encoding="utf-8"))
        summary = report.get("evaluation", {}).get("summary", {})
        result.update(
            {
                "reportVersion": report.get("reportVersion"),
                "evidenceLevel": report.get("evidenceLevel"),
                "l3Status": report.get("l3Status"),
                "gate": summary.get("gate"),
                "sourceRequiresNativeBridge": summary.get("sourceRequiresNativeBridge"),
                "runtimeEntered": summary.get("runtimeEntered"),
                "animSequenceClassesVisible": summary.get("animSequenceClassesVisible"),
                "hasNativeSource": summary.get("hasNativeSource"),
                "hasAnimNotifyBridgePlugin": summary.get("hasAnimNotifyBridgePlugin"),
                "hasCompiledBridgeBinary": summary.get("hasCompiledBridgeBinary"),
                "commandletVisible": summary.get("commandletVisible"),
                "missingRequiredNativeFiles": summary.get("missingRequiredNativeFiles"),
                "pass": summary.get("pass"),
                "warning": summary.get("warning"),
                "error": summary.get("error"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def _blocked(output_path: Path, source_artifact: Path, reason: str, unreal_cli: Optional[str], project: Optional[str]) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_animation_bridge.native_notify_bridge import build_anim_notify_native_bridge_report

    runtime_snapshot = {
        "runtime": {
            "executed": False,
            "runtime": "preflight",
            "engineVersion": "not_entered",
            "pythonVersion": sys.version,
            "projectPath": project,
            "unrealCli": unreal_cli,
            "blockedReason": reason,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
            "api": {},
        },
        "project": {},
    }
    report = build_anim_notify_native_bridge_report(source_artifact, runtime_snapshot=runtime_snapshot)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": False, "reason": reason, "path": str(output_path)}, ensure_ascii=False, indent=2))
    return 0


def _latest_report(root: Path, pattern: str, report_version: str) -> Optional[Path]:
    matches = []
    for path in sorted(root.glob(pattern), key=lambda item: item.stat().st_mtime):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if report.get("reportVersion") == report_version:
            matches.append(path)
    return matches[-1] if matches else None


if __name__ == "__main__":
    raise SystemExit(main())
