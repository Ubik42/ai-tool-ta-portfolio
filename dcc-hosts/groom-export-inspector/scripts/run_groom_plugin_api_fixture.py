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
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "probe_groom_plugin_api_fixture.py"

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
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from groom_export_inspector.plugin_api_fixture import (
        build_groom_plugin_api_fixture_report,
        collect_static_plugin_snapshot,
    )

    unreal_cli = find_unreal_cli()
    artifact_dir = ROOT / "artifacts"
    logs_dir = artifact_dir / "groom-plugin-api-fixture-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("groom-plugin-api-fixture-%s.json" % stamp)
    runtime_path = logs_dir / ("groom-plugin-api-fixture-%s.runtime.json" % stamp)
    stdout_path = logs_dir / ("groom-plugin-api-fixture-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("groom-plugin-api-fixture-%s.stderr.log" % stamp)

    static_snapshot = collect_static_plugin_snapshot(UNREAL_PROJECT, unreal_cli)
    runtime_snapshot = _blocked_runtime("blocked_by_missing_unreal_cli", unreal_cli)
    return_code: Optional[int] = None

    if not unreal_cli:
        runtime_snapshot = _blocked_runtime("blocked_by_missing_unreal_cli", unreal_cli)
    elif not UNREAL_PROJECT.exists():
        runtime_snapshot = _blocked_runtime("blocked_by_missing_unreal_project", unreal_cli)
    elif not UNREAL_SCRIPT.exists():
        runtime_snapshot = _blocked_runtime("blocked_by_missing_unreal_probe", unreal_cli)
    else:
        env = os.environ.copy()
        env["AI_TOOL_TA_GROOM_EXPORT_ROOT"] = str(ROOT)
        env["AI_TOOL_TA_GROOM_PLUGIN_API_RUNTIME"] = str(runtime_path)
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
        completed = subprocess.run(command, cwd=str(ROOT), env=env, text=True, capture_output=True, timeout=300)
        return_code = completed.returncode
        stdout_path.write_text(completed.stdout, encoding="utf-8", errors="replace")
        stderr_path.write_text(completed.stderr, encoding="utf-8", errors="replace")
        if completed.returncode == 0 and runtime_path.exists():
            runtime_snapshot = json.loads(runtime_path.read_text(encoding="utf-8"))
            runtime_snapshot.setdefault("runtime", {})["returnCode"] = completed.returncode
            runtime_snapshot["runtime"]["stdoutLog"] = str(stdout_path)
            runtime_snapshot["runtime"]["stderrLog"] = str(stderr_path)
        else:
            runtime_snapshot = _blocked_runtime("blocked_by_unreal_probe_failure", unreal_cli)
            runtime_snapshot.setdefault("runtime", {})["returnCode"] = completed.returncode
            runtime_snapshot["runtime"]["stdoutLog"] = str(stdout_path)
            runtime_snapshot["runtime"]["stderrLog"] = str(stderr_path)

    report = build_groom_plugin_api_fixture_report(static_snapshot, runtime_snapshot)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report.get("facts", {}).get("summary", {})
    result = {
        "ok": bool(runtime_snapshot.get("runtime", {}).get("executed")) and output_path.exists(),
        "returnCode": return_code,
        "path": str(output_path),
        "reportVersion": report.get("reportVersion"),
        "evidenceLevel": report.get("evidenceLevel"),
        "l3Status": report.get("l3Status"),
        "gate": report.get("evaluation", {}).get("summary", {}).get("gate"),
        "summary": {
            "projectRequestedRows": summary.get("projectRequestedRows"),
            "descriptorRowsFound": summary.get("descriptorRowsFound"),
            "runtimeCollected": summary.get("runtimeCollected"),
            "groomClassNameRows": summary.get("groomClassNameRows"),
            "hairClassNameRows": summary.get("hairClassNameRows"),
            "alembicClassNameRows": summary.get("alembicClassNameRows"),
            "geometryCacheClassNameRows": summary.get("geometryCacheClassNameRows"),
            "groomImportApiReady": summary.get("groomImportApiReady"),
            "alembicImportFactoryVisible": summary.get("alembicImportFactoryVisible"),
            "assetWrites": summary.get("assetWrites"),
            "engineWrites": summary.get("engineWrites"),
            "productionWrites": summary.get("productionWrites"),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if output_path.exists() else 1


def _blocked_runtime(reason: str, unreal_cli: Optional[str]) -> dict:
    return {
        "runtime": {
            "executed": False,
            "runtime": "preflight",
            "engineVersion": "not_entered",
            "pythonVersion": sys.version,
            "projectPath": str(UNREAL_PROJECT) if UNREAL_PROJECT.exists() else None,
            "unrealCli": unreal_cli,
            "blockedReason": reason,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "api": {},
    }


if __name__ == "__main__":
    raise SystemExit(main())
