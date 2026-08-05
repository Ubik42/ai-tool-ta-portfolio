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
SOURCE_GROOM_ARTIFACT_FALLBACK = ROOT / "artifacts" / "groom-export-inspector-maya-l3-20260806-003711.json"
UNREAL_PROJECT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "AI_Tool_TA_Unreal_L3.uproject"
)
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "probe_groom_import_readiness.py"


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


def resolve_source_groom_artifact() -> Path:
    env_path = os.environ.get("AI_TOOL_TA_GROOM_UNREAL_READINESS_SOURCE")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    candidates = sorted((ROOT / "artifacts").glob("groom-export-inspector-maya-l3-*.json"))
    runtime_candidates = [path for path in candidates if "readiness" not in path.name]
    return runtime_candidates[-1] if runtime_candidates else SOURCE_GROOM_ARTIFACT_FALLBACK


def main() -> int:
    unreal_cli = find_unreal_cli()
    source_groom_artifact = resolve_source_groom_artifact()
    artifact_dir = ROOT / "artifacts"
    logs_dir = artifact_dir / "groom-unreal-readiness-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("groom-unreal-readiness-%s.json" % stamp)
    stdout_path = logs_dir / ("groom-unreal-readiness-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("groom-unreal-readiness-%s.stderr.log" % stamp)

    if not unreal_cli:
        return _blocked(output_path, "blocked_by_missing_unreal_cli", None, None, source_groom_artifact)
    if not UNREAL_PROJECT.exists():
        return _blocked(output_path, "blocked_by_missing_unreal_project", unreal_cli, None, source_groom_artifact)
    if not source_groom_artifact.exists():
        return _blocked(output_path, "blocked_by_missing_groom_export_artifact", unreal_cli, str(UNREAL_PROJECT), source_groom_artifact)

    env = os.environ.copy()
    env["AI_TOOL_TA_GROOM_EXPORT_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_GROOM_UNREAL_READINESS_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_GROOM_UNREAL_READINESS_SOURCE"] = str(source_groom_artifact)
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
        "sourceGroom": str(source_groom_artifact),
    }
    if output_path.exists():
        report = json.loads(output_path.read_text(encoding="utf-8"))
        result.update(
            {
                "reportVersion": report.get("reportVersion"),
                "evidenceLevel": report.get("evidenceLevel"),
                "l3Status": report.get("l3Status"),
                "summary": report.get("facts", {}).get("summary"),
                "evaluation": report.get("evaluation", {}).get("summary"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def _blocked(
    output_path: Path,
    reason: str,
    unreal_cli: Optional[str],
    project: Optional[str],
    source_groom_artifact: Path,
) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from groom_export_inspector.unreal_readiness import build_unreal_readiness_report

    runtime_snapshot = {
        "runtime": {
            "executed": False,
            "runtime": "preflight",
            "engineVersion": "not_entered",
            "pythonVersion": sys.version,
            "projectPath": project,
            "unrealCli": unreal_cli,
            "blockedReason": reason,
            "api": {},
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "assets": [],
    }
    report = build_unreal_readiness_report(source_groom_artifact, runtime_snapshot)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": False, "reason": reason, "path": str(output_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
