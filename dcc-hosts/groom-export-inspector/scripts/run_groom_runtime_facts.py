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
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "collect_groom_runtime_facts.py"

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
    logs_dir = artifact_dir / "groom-runtime-facts-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("groom-runtime-facts-%s.json" % stamp)
    stdout_path = logs_dir / ("groom-runtime-facts-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("groom-runtime-facts-%s.stderr.log" % stamp)
    postcheck = _latest_artifact("groom-alembic-import-postcheck-*.json")
    plugin_fixture = _latest_artifact("groom-plugin-api-fixture-*.json")
    controlled_executor = _latest_artifact("groom-controlled-executor-*.json")

    if not unreal_cli:
        return _blocked(output_path, "missing_unreal_cli", None, None, postcheck, plugin_fixture, controlled_executor)
    if not UNREAL_PROJECT.exists():
        return _blocked(output_path, "missing_unreal_project", unreal_cli, None, postcheck, plugin_fixture, controlled_executor)
    if not postcheck:
        return _blocked(output_path, "missing_groom_import_postcheck_artifact", unreal_cli, str(UNREAL_PROJECT), None, plugin_fixture, controlled_executor)
    if not plugin_fixture:
        return _blocked(output_path, "missing_groom_plugin_api_fixture_artifact", unreal_cli, str(UNREAL_PROJECT), postcheck, None, controlled_executor)
    if not controlled_executor:
        return _blocked(output_path, "missing_groom_controlled_executor_artifact", unreal_cli, str(UNREAL_PROJECT), postcheck, plugin_fixture, None)

    env = os.environ.copy()
    env["AI_TOOL_TA_GROOM_EXPORT_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_GROOM_RUNTIME_FACTS_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_GROOM_RUNTIME_FACTS_POSTCHECK"] = str(postcheck)
    env["AI_TOOL_TA_GROOM_RUNTIME_FACTS_PLUGIN_FIXTURE"] = str(plugin_fixture)
    env["AI_TOOL_TA_GROOM_RUNTIME_FACTS_CONTROLLED_EXECUTOR"] = str(controlled_executor)
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
    stdout_path.write_text(completed.stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(completed.stderr, encoding="utf-8", errors="replace")

    ok = output_path.exists()
    result = {
        "ok": ok,
        "returnCode": completed.returncode,
        "path": str(output_path) if output_path.exists() else None,
        "stdoutLog": str(stdout_path),
        "stderrLog": str(stderr_path),
        "unrealCli": str(unreal_cli),
        "project": str(UNREAL_PROJECT),
        "sourceImportPostcheck": str(postcheck),
        "sourcePluginApiFixture": str(plugin_fixture),
        "sourceControlledExecutor": str(controlled_executor),
    }
    if output_path.exists():
        report = json.loads(output_path.read_text(encoding="utf-8"))
        summary = report.get("facts", {}).get("summary", {})
        result.update(
            {
                "reportVersion": report.get("reportVersion"),
                "evidenceLevel": report.get("evidenceLevel"),
                "l3Status": report.get("l3Status"),
                "gate": summary.get("gate"),
                "runtimeAssetsPresent": summary.get("runtimeAssetsPresent"),
                "readableProperties": summary.get("readableProperties"),
                "methodSurface": summary.get("methodSurface"),
                "callResults": summary.get("callResults"),
                "rollbackPassed": summary.get("rollbackPassed"),
                "residualAssetCount": summary.get("residualAssetCount"),
                "assetWrites": summary.get("assetWrites"),
                "pass": summary.get("pass"),
                "warning": summary.get("warning"),
                "error": summary.get("error"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if output_path.exists() else 1


def _latest_artifact(pattern: str) -> Optional[Path]:
    candidates = sorted(ROOT.glob("artifacts/%s" % pattern))
    return candidates[-1] if candidates else None


def _blocked(
    output_path: Path,
    reason: str,
    unreal_cli: Optional[str],
    project: Optional[str],
    postcheck: Optional[Path],
    plugin_fixture: Optional[Path],
    controlled_executor: Optional[Path],
) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from groom_export_inspector.groom_runtime_facts import build_groom_runtime_facts_report

    fallback_postcheck = postcheck or ROOT / "artifacts" / "missing-groom-import-postcheck.json"
    fallback_plugin = plugin_fixture or ROOT / "artifacts" / "missing-groom-plugin-api-fixture.json"
    fallback_controlled = controlled_executor or ROOT / "artifacts" / "missing-groom-controlled-executor.json"
    snapshot = {
        "mode": "blocked",
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
        },
        "selectedOperation": {},
        "apiSurface": {},
        "assetFacts": {},
        "preflight": {},
        "importTask": {},
        "bindingAttempt": {},
        "rollback": {},
        "writeSet": [],
        "rollbackActions": [],
        "errors": [reason],
    }
    report = build_groom_runtime_facts_report(fallback_postcheck, fallback_plugin, fallback_controlled, snapshot)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": False, "reason": reason, "path": str(output_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
