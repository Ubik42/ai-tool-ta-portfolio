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
MANIFEST = ROOT / "fixtures" / "synthetic_gameplay_attach_manifest.json"
UNREAL_PROJECT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "AI_Tool_TA_Unreal_L3.uproject"
)
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "probe_gameplay_attach_runtime.py"


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
    artifact_dir = ARTIFACT_DIR
    logs_dir = artifact_dir / "unreal-gameplay-attach-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("unreal-gameplay-attach-fixture-%s.json" % stamp)
    stdout_path = logs_dir / ("unreal-gameplay-attach-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("unreal-gameplay-attach-%s.stderr.log" % stamp)
    source_artifact = _latest_socket_l3_artifact()

    if not unreal_cli:
        return _blocked(output_path, "blocked_by_missing_unreal_cli", None, None, source_artifact)
    if not UNREAL_PROJECT.exists():
        return _blocked(output_path, "blocked_by_missing_unreal_project", unreal_cli, None, source_artifact)
    if not source_artifact.exists():
        return _blocked(output_path, "blocked_by_missing_unreal_socket_l3_artifact", unreal_cli, str(UNREAL_PROJECT), source_artifact)
    if not MANIFEST.exists():
        raise FileNotFoundError(MANIFEST)

    env = os.environ.copy()
    env["AI_TOOL_TA_UNREAL_SOCKET_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_UNREAL_GAMEPLAY_ATTACH_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_UNREAL_GAMEPLAY_ATTACH_SOURCE"] = str(source_artifact)
    env["AI_TOOL_TA_UNREAL_GAMEPLAY_ATTACH_MANIFEST"] = str(MANIFEST)
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
                "intentCount": summary.get("intentCount"),
                "readyIntents": summary.get("readyIntents"),
                "reviewIntents": summary.get("reviewIntents"),
                "blockedIntents": summary.get("blockedIntents"),
                "missingRuntimeSockets": summary.get("missingRuntimeSockets"),
                "attachableAssetsPresent": summary.get("attachableAssetsPresent"),
                "pass": summary.get("pass"),
                "warning": summary.get("warning"),
                "error": summary.get("error"),
            }
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def _latest_socket_l3_artifact() -> Path:
    candidates = sorted(ARTIFACT_DIR.glob("unreal-socket-import-checker-l3-*.json"))
    reports = []
    for path in candidates:
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if report.get("reportVersion") == "unreal-socket-import-checker@0.1.0" and report.get("evidenceLevel") == "L3":
            reports.append(path)
    if reports:
        return reports[-1]
    return ARTIFACT_DIR / "unreal-socket-import-checker-l3-20260805-212131.json"


def _blocked(output_path: Path, reason: str, unreal_cli: Optional[str], project: Optional[str], source_artifact: Path) -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_socket_import_checker.gameplay_attach import build_gameplay_attach_report

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
        },
        "facts": {"assetsByPath": {}},
    }
    report = build_gameplay_attach_report(source_artifact, MANIFEST, runtime_snapshot)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": False, "reason": reason, "path": str(output_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
