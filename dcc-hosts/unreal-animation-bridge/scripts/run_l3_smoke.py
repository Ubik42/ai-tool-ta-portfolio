from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
PROJECT_PATH = PORTFOLIO_ROOT / "dcc-hosts" / "unreal-handoff-inspector" / "projects" / "AI_Tool_TA_Unreal_L3" / "AI_Tool_TA_Unreal_L3.uproject"
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "probe_animation_runtime.py"


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def _candidate_paths() -> List[Path]:
    return [
        Path(r"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"D:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
    ]


def find_unreal_cli() -> Path | None:
    env_value = os.environ.get("AI_TOOL_TA_UNREAL_CLI")
    if env_value and Path(env_value).exists():
        return Path(env_value)
    for path in _candidate_paths():
        if path.exists():
            return path
    return None


def write_readiness_report(reason: str, unreal_cli: Path | None) -> Path:
    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("unreal-animation-bridge-readiness-%s.json" % stamp)
    report = {
        "reportVersion": "unreal-animation-bridge-readiness@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / Unreal Animation Bridge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-readiness",
        "l3Status": reason,
        "gate": "Blocked",
        "unrealCli": {
            "available": bool(unreal_cli),
            "path": str(unreal_cli) if unreal_cli else None,
        },
        "unrealProject": {
            "available": PROJECT_PATH.exists(),
            "path": public_path(PROJECT_PATH),
        },
        "collector": {
            "script": public_path(UNREAL_SCRIPT),
            "ready": UNREAL_SCRIPT.exists(),
        },
        "boundary": {
            "mutation": "readiness_probe_only",
            "engineWrites": 0,
            "assetWrites": 0,
            "productionWrites": 0,
        },
    }
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> int:
    unreal_cli = find_unreal_cli()
    if not unreal_cli or not PROJECT_PATH.exists():
        reason = "blocked_by_missing_unreal_cli" if not unreal_cli else "blocked_by_missing_unreal_project"
        path = write_readiness_report(reason, unreal_cli)
        print(json.dumps({"ok": False, "path": str(path), "reason": reason}, ensure_ascii=False, indent=2))
        return 1

    artifact_dir = ROOT / "artifacts"
    logs_dir = artifact_dir / "unreal-animation-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("unreal-animation-bridge-readiness-%s.json" % stamp)
    stdout_path = logs_dir / ("unreal-animation-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("unreal-animation-%s.stderr.log" % stamp)

    env = os.environ.copy()
    env["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_UNREAL_CLI"] = str(unreal_cli)
    env["AI_TOOL_TA_UNREAL_PROJECT"] = str(PROJECT_PATH)

    command = [
        str(unreal_cli),
        str(PROJECT_PATH),
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
    report = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() else None
    summary = report.get("evaluation", {}).get("summary") if report else None
    print(
        json.dumps(
            {
                "ok": ok,
                "returnCode": completed.returncode,
                "path": str(output_path) if output_path.exists() else None,
                "stdoutLog": str(stdout_path),
                "stderrLog": str(stderr_path),
                "unrealCli": str(unreal_cli),
                "project": str(PROJECT_PATH),
                "evidenceLevel": report.get("evidenceLevel") if report else None,
                "l3Status": report.get("l3Status") if report else None,
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
