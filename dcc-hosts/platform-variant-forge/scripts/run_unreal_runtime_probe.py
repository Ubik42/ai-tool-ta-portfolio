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
UNREAL_PROJECT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "AI_Tool_TA_Unreal_L3.uproject"
)
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "probe_variant_runtime.py"
PLAN_ARTIFACT = ROOT / "artifacts" / "platform-variant-forge-contract-20260805-183315.json"


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
    artifact_dir = ROOT / "artifacts"
    logs_dir = artifact_dir / "unreal-variant-runtime-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("platform-variant-unreal-runtime-%s.json" % stamp)
    stdout_path = logs_dir / ("platform-variant-unreal-runtime-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("platform-variant-unreal-runtime-%s.stderr.log" % stamp)

    if not unreal_cli:
        return _blocked(output_path, "missing_unreal_cli", None, None)
    if not UNREAL_PROJECT.exists():
        return _blocked(output_path, "missing_unreal_project", unreal_cli, None)
    if not PLAN_ARTIFACT.exists():
        return _blocked(output_path, "missing_platform_variant_plan", unreal_cli, str(UNREAL_PROJECT))

    env = os.environ.copy()
    env["AI_TOOL_TA_PLATFORM_VARIANT_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_PLATFORM_VARIANT_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_PLATFORM_VARIANT_PLAN"] = str(PLAN_ARTIFACT)
    env["AI_TOOL_TA_UNREAL_PROJECT"] = str(UNREAL_PROJECT)
    env["AI_TOOL_TA_UNREAL_CLI"] = str(unreal_cli)
    env["AI_TOOL_TA_UNREAL_INSPECTOR_ROOT"] = str(PORTFOLIO_ROOT / "dcc-hosts" / "unreal-handoff-inspector")

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
    }
    if output_path.exists():
        report = json.loads(output_path.read_text(encoding="utf-8"))
        result.update(
            {
                "reportVersion": report.get("reportVersion"),
                "evidenceLevel": report.get("evidenceLevel"),
                "l3Status": report.get("l3Status"),
                "summary": report.get("comparison", {}).get("summary"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def _blocked(output_path: Path, reason: str, unreal_cli: str | None, project: str | None) -> int:
    report = {
        "reportVersion": "platform-variant-unreal-runtime@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked",
        "l3Status": reason,
        "unrealRuntime": {
            "executed": False,
            "unrealCli": unreal_cli,
            "project": project,
            "reason": reason,
        },
        "comparison": {
            "summary": {
                "gate": "Blocked",
                "variantCount": 0,
                "readyVariants": 0,
                "reviewVariants": 0,
                "blockedVariants": 0,
                "pass": 0,
                "warning": 0,
                "error": 1,
            },
            "rows": [],
        },
    }
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": False, "reason": reason, "path": str(output_path)}, ensure_ascii=False, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
