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
LOG_DIR = ARTIFACT_DIR / "unreal-control-rig-native-bridge-readiness-logs"
UNREAL_PROJECT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "AI_Tool_TA_Unreal_L3.uproject"
)
PLUGIN_DIR = UNREAL_PROJECT.parent / "Plugins" / "AI_Tool_TA_ControlRigBridge"
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "probe_control_rig_native_bridge.py"
REPORT_VERSION = "unreal-control-rig-native-bridge-readiness@0.1.0"

COMMON_UNREAL_CLI = [
    r"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"D:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
]


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-control-rig-native-bridge-readiness-%s.json" % stamp)
    stdout_path = LOG_DIR / ("unreal-control-rig-native-bridge-readiness-%s.stdout.log" % stamp)
    stderr_path = LOG_DIR / ("unreal-control-rig-native-bridge-readiness-%s.stderr.log" % stamp)
    unreal_cli = _find_unreal_cli()
    compile_status_path = _latest_report("unreal-control-rig-compile-status-*.json", "unreal-control-rig-compile-status@0.1.0")

    if not unreal_cli:
        return _blocked(output_path, "blocked_by_missing_unreal_cli", None, compile_status_path)
    if not UNREAL_PROJECT.exists():
        return _blocked(output_path, "blocked_by_missing_unreal_project", str(unreal_cli), compile_status_path)
    if not compile_status_path:
        return _blocked(output_path, "blocked_by_missing_compile_status_artifact", str(unreal_cli), compile_status_path)

    env = os.environ.copy()
    env["AI_TOOL_TA_UNREAL_CONTROL_RIG_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_UNREAL_CONTROL_RIG_NATIVE_BRIDGE_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_UNREAL_CONTROL_RIG_COMPILE_STATUS_SOURCE"] = str(compile_status_path)
    env["AI_TOOL_TA_UNREAL_CONTROL_RIG_NATIVE_BRIDGE_PLUGIN"] = str(PLUGIN_DIR)
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
        "sourceCompileStatus": str(compile_status_path),
    }
    if output_path.exists():
        report = json.loads(output_path.read_text(encoding="utf-8"))
        result.update(
            {
                "reportVersion": report.get("reportVersion"),
                "evidenceLevel": report.get("evidenceLevel"),
                "l3Status": report.get("l3Status"),
                "summary": report.get("evaluation", {}).get("summary"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


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


def _latest_report(pattern: str, report_version: str) -> Optional[Path]:
    matches = []
    for path in sorted(ARTIFACT_DIR.glob(pattern), key=lambda item: item.stat().st_mtime):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if report.get("reportVersion") == report_version:
            matches.append(path)
    return matches[-1] if matches else None


def _blocked(output_path: Path, reason: str, unreal_cli: Optional[str], compile_status_path: Optional[Path]) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_control_rig_bridge.control_rig_native_bridge import build_control_rig_native_bridge_report

    source_path = compile_status_path or ARTIFACT_DIR / "unreal-control-rig-compile-status-20260806-001504.json"
    runtime_snapshot = {
        "runtime": {
            "executed": False,
            "runtime": "preflight",
            "blockedReason": reason,
            "unrealCli": unreal_cli,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
        }
    }
    report = build_control_rig_native_bridge_report(source_path, runtime_snapshot)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": False, "reason": reason, "path": str(output_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
