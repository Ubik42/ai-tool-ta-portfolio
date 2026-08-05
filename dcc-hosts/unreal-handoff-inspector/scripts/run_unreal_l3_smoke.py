from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_smoke import find_unreal_cli  # noqa: E402


PROJECT_PATH = ROOT / "projects" / "AI_Tool_TA_Unreal_L3" / "AI_Tool_TA_Unreal_L3.uproject"
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "run_l3_inspection.py"


def main() -> int:
    unreal_cli = find_unreal_cli()
    if not unreal_cli:
        print(json.dumps({"ok": False, "reason": "missing_unreal_cli"}, ensure_ascii=False, indent=2))
        return 1
    if not PROJECT_PATH.exists():
        print(json.dumps({"ok": False, "reason": "missing_unreal_project", "project": str(PROJECT_PATH)}, ensure_ascii=False, indent=2))
        return 1

    artifact_dir = ROOT / "artifacts"
    logs_dir = ROOT / "artifacts" / "unreal-l3-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("unreal-handoff-inspector-l3-%s.json" % stamp)
    stdout_path = logs_dir / ("unreal-l3-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("unreal-l3-%s.stderr.log" % stamp)

    env = os.environ.copy()
    env["AI_TOOL_TA_UNREAL_INSPECTOR_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_UNREAL_L3_OUTPUT"] = str(output_path)
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
    summary = None
    evidence_level = None
    l3_status = None
    registry_evidence = None
    engine_fact_evidence = None
    if output_path.exists():
        report = json.loads(output_path.read_text(encoding="utf-8"))
        summary = report["evaluation"]["summary"]
        evidence_level = report.get("evidenceLevel")
        l3_status = report.get("l3Status")
        registry_evidence = report.get("unrealRegistryEvidence")
        engine_fact_evidence = report.get("unrealEngineFactEvidence")

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
                "evidenceLevel": evidence_level,
                "l3Status": l3_status,
                "registryEvidence": registry_evidence,
                "engineFactEvidence": engine_fact_evidence,
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
