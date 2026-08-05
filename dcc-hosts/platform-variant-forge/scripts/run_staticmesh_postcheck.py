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
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "collect_staticmesh_postcheck.py"
RECEIPTS_ARTIFACT = ROOT / "artifacts" / "platform-variant-executor-expansion-20260805-201222.json"


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
    logs_dir = artifact_dir / "unreal-staticmesh-postcheck-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("platform-variant-staticmesh-postcheck-%s.json" % stamp)
    stdout_path = logs_dir / ("platform-variant-staticmesh-postcheck-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("platform-variant-staticmesh-postcheck-%s.stderr.log" % stamp)

    if not unreal_cli:
        return _blocked(output_path, "missing_unreal_cli", None, None)
    if not UNREAL_PROJECT.exists():
        return _blocked(output_path, "missing_unreal_project", unreal_cli, None)
    if not RECEIPTS_ARTIFACT.exists():
        return _blocked(output_path, "missing_platform_variant_executor_receipts", unreal_cli, str(UNREAL_PROJECT))

    env = os.environ.copy()
    env["AI_TOOL_TA_PLATFORM_VARIANT_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_PLATFORM_VARIANT_STATICMESH_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_PLATFORM_VARIANT_RECEIPTS"] = str(RECEIPTS_ARTIFACT)
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
    }
    if output_path.exists():
        report = json.loads(output_path.read_text(encoding="utf-8"))
        result.update(
            {
                "reportVersion": report.get("reportVersion"),
                "evidenceLevel": report.get("evidenceLevel"),
                "l3Status": report.get("l3Status"),
                "summary": report.get("postcheck", {}).get("summary"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def _blocked(output_path: Path, reason: str, unreal_cli: str | None, project: str | None) -> int:
    report = {
        "reportVersion": "platform-variant-staticmesh-postcheck@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / Platform Variant Forge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked",
        "l3Status": reason,
        "sourceExecutorExpansion": {
            "path": str(RECEIPTS_ARTIFACT),
            "reportVersion": None,
            "evidenceLevel": None,
            "l3Status": None,
            "gate": None,
        },
        "unrealRuntime": {
            "executed": False,
            "unrealCli": unreal_cli,
            "project": project,
            "reason": reason,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
        },
        "runtimeFacts": {},
        "apiAvailability": {},
        "postcheck": {
            "summary": {
                "gate": "Blocked",
                "receiptCount": 0,
                "runtimeTargets": 0,
                "targetAssetsPresent": 0,
                "noOpVerified": 0,
                "runtimeNoOpMatched": 0,
                "approvalReady": 0,
                "readinessOnly": 0,
                "executorReady": 0,
                "runtimeSatisfied": 0,
                "runtimeHeld": 0,
                "runtimeDrift": 0,
                "blockedReceipts": 0,
                "ownerActions": 0,
                "pass": 0,
                "warning": 0,
                "error": 1,
                "assetWrites": 0,
                "engineWrites": 0,
                "productionWrites": 0,
            },
            "receipts": [],
            "rows": [],
            "ownerActions": [],
        },
    }
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": False, "reason": reason, "path": str(output_path)}, ensure_ascii=False, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
