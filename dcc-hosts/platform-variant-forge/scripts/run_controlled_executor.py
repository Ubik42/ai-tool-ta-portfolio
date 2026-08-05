from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "execute_controlled_variant.py"
GENERATION_ARTIFACT = ROOT / "artifacts" / "platform-variant-generation-plan-20260805-190052.json"

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from run_texture_runtime_probe import UNREAL_PROJECT, find_unreal_cli  # noqa: E402


def main() -> int:
    unreal_cli = find_unreal_cli()
    artifact_dir = ROOT / "artifacts"
    logs_dir = artifact_dir / "unreal-controlled-executor-logs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("platform-variant-controlled-executor-%s.json" % stamp)
    stdout_path = logs_dir / ("platform-variant-controlled-executor-%s.stdout.log" % stamp)
    stderr_path = logs_dir / ("platform-variant-controlled-executor-%s.stderr.log" % stamp)
    texture_payload = _latest_texture_payload_artifact()

    if not unreal_cli:
        return _blocked(output_path, "missing_unreal_cli", None, None, texture_payload)
    if not UNREAL_PROJECT.exists():
        return _blocked(output_path, "missing_unreal_project", unreal_cli, None, texture_payload)
    if not GENERATION_ARTIFACT.exists():
        return _blocked(output_path, "missing_generation_plan", unreal_cli, str(UNREAL_PROJECT), texture_payload)
    if not texture_payload:
        return _blocked(output_path, "missing_texture_payload_artifact", unreal_cli, str(UNREAL_PROJECT), None)

    env = os.environ.copy()
    env["AI_TOOL_TA_PLATFORM_VARIANT_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_PLATFORM_VARIANT_EXECUTOR_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_PLATFORM_VARIANT_GENERATION_PLAN"] = str(GENERATION_ARTIFACT)
    env["AI_TOOL_TA_PLATFORM_VARIANT_TEXTURE_PAYLOAD"] = str(texture_payload)
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
        "sourceTexturePayload": str(texture_payload),
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


def _latest_texture_payload_artifact() -> Optional[Path]:
    candidates = sorted(ROOT.glob("artifacts/platform-variant-texture-payload-runtime-*.json"))
    return candidates[-1] if candidates else None


def _blocked(
    output_path: Path,
    reason: str,
    unreal_cli: str | None,
    project: str | None,
    texture_payload: Path | None,
) -> int:
    from platform_variant_forge.controlled_executor import build_controlled_executor_report

    snapshot = {
        "mode": "blocked",
        "runtime": {
            "executed": False,
            "unrealCli": unreal_cli,
            "project": project,
            "reason": reason,
            "engineWrites": 0,
            "assetWrites": 0,
            "productionWrites": 0,
        },
        "selectedOperation": {},
        "writeSet": [],
        "rollbackActions": [],
        "preflight": {},
        "postExecution": {},
        "rollback": {},
        "errors": [reason],
    }
    payload = texture_payload or ROOT / "artifacts" / "missing-texture-payload.json"
    report = build_controlled_executor_report(GENERATION_ARTIFACT, payload, snapshot)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"ok": False, "reason": reason, "path": str(output_path)}, ensure_ascii=False, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
