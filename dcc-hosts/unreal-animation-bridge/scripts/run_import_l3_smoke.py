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
MAYA_FBX_SCRIPT = ROOT / "scripts" / "generate_maya_fbx_fixture.py"
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "import_animsequence_fixture.py"


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def _mayapy_candidates() -> List[Path]:
    return [
        Path(r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"),
        Path(r"C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe"),
        Path(r"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"),
        Path(r"C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe"),
        Path(r"D:\Program Files\Autodesk\Maya2026\bin\mayapy.exe"),
        Path(r"D:\Program Files\Autodesk\Maya2025\bin\mayapy.exe"),
        Path(r"D:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"),
    ]


def _unreal_candidates() -> List[Path]:
    return [
        Path(r"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
        Path(r"D:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"),
    ]


def find_mayapy() -> Path | None:
    env_value = os.environ.get("AI_TOOL_TA_MAYAPY")
    if env_value and Path(env_value).exists():
        return Path(env_value)
    for path in _mayapy_candidates():
        if path.exists():
            return path
    return None


def find_unreal_cli() -> Path | None:
    env_value = os.environ.get("AI_TOOL_TA_UNREAL_CLI")
    if env_value and Path(env_value).exists():
        return Path(env_value)
    for path in _unreal_candidates():
        if path.exists():
            return path
    return None


def write_blocked_report(reason: str, mayapy: Path | None, unreal_cli: Path | None, output_path: Path) -> Path:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_animation_bridge.contract import build_report

    runtime_snapshot = {
        "executed": True,
        "runtime": "preflight",
        "engineVersion": "not_entered",
        "pythonVersion": sys.version,
        "projectPath": public_path(PROJECT_PATH),
        "api": {},
        "assets": {
            "expectedSequenceCount": 0,
            "presentSequenceCount": 0,
            "missingSequenceCount": 0,
            "allExpectedAssetsPresent": False,
            "rows": {},
        },
        "import": {
            "attempted": True,
            "success": False,
            "method": "preflight",
            "failures": [reason],
            "mayapy": str(mayapy) if mayapy else None,
            "unrealCli": str(unreal_cli) if unreal_cli else None,
            "engineWrites": 0,
            "assetWrites": 0,
            "savePackage": False,
        },
        "mutation": {
            "engineWrites": 0,
            "assetWrites": 0,
            "savePackage": False,
            "writeScope": "none",
        },
    }
    fixture = ROOT / "fixtures" / "synthetic_unreal_animation_bridge.json"
    report = build_report(fixture, runtime_snapshot=runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


def main() -> int:
    mayapy = find_mayapy()
    unreal_cli = find_unreal_cli()
    artifact_dir = ROOT / "artifacts"
    logs_dir = artifact_dir / "unreal-animation-logs"
    temp_dir = PORTFOLIO_ROOT / ".tmp" / "unreal-animation-bridge"
    fbx_dir = temp_dir / "fbx"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("unreal-animation-bridge-import-l3-%s.json" % stamp)
    fbx_manifest = temp_dir / ("maya-fbx-fixture-%s.json" % stamp)

    if not mayapy or not unreal_cli or not PROJECT_PATH.exists():
        reason = (
            "blocked_by_missing_mayapy"
            if not mayapy
            else "blocked_by_missing_unreal_cli"
            if not unreal_cli
            else "blocked_by_missing_unreal_project"
        )
        path = write_blocked_report(reason, mayapy, unreal_cli, output_path)
        print(json.dumps({"ok": False, "path": str(path), "reason": reason}, ensure_ascii=False, indent=2))
        return 0

    maya_stdout = logs_dir / ("unreal-animation-import-maya-%s.stdout.log" % stamp)
    maya_stderr = logs_dir / ("unreal-animation-import-maya-%s.stderr.log" % stamp)
    maya_command = [
        str(mayapy),
        str(MAYA_FBX_SCRIPT),
        "--output-dir",
        str(fbx_dir),
        "--manifest-output",
        str(fbx_manifest),
    ]
    maya_run = subprocess.run(maya_command, cwd=str(ROOT), text=True, capture_output=True, timeout=180)
    maya_stdout.write_text(maya_run.stdout, encoding="utf-8", errors="replace")
    maya_stderr.write_text(maya_run.stderr, encoding="utf-8", errors="replace")
    if maya_run.returncode != 0 or not fbx_manifest.exists():
        path = write_blocked_report("blocked_by_maya_fbx_generation_failed", mayapy, unreal_cli, output_path)
        print(
            json.dumps(
                {
                    "ok": False,
                    "path": str(path),
                    "reason": "blocked_by_maya_fbx_generation_failed",
                    "mayaReturnCode": maya_run.returncode,
                    "mayaStdout": str(maya_stdout),
                    "mayaStderr": str(maya_stderr),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    unreal_stdout = logs_dir / ("unreal-animation-import-%s.stdout.log" % stamp)
    unreal_stderr = logs_dir / ("unreal-animation-import-%s.stderr.log" % stamp)
    env = os.environ.copy()
    env["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_UNREAL_ANIMATION_FBX_MANIFEST"] = str(fbx_manifest)
    env["AI_TOOL_TA_UNREAL_CLI"] = str(unreal_cli)
    env["AI_TOOL_TA_UNREAL_PROJECT"] = str(PROJECT_PATH)

    unreal_command = [
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
    completed = subprocess.run(unreal_command, cwd=str(ROOT), env=env, text=True, capture_output=True, timeout=360)
    unreal_stdout.write_text(completed.stdout, encoding="utf-8", errors="replace")
    unreal_stderr.write_text(completed.stderr, encoding="utf-8", errors="replace")

    ok = output_path.exists()
    report = json.loads(output_path.read_text(encoding="utf-8")) if ok else None
    summary = report.get("evaluation", {}).get("summary") if report else None
    print(
        json.dumps(
            {
                "ok": ok,
                "returnCode": completed.returncode,
                "path": str(output_path) if output_path.exists() else None,
                "mayaFbxManifest": str(fbx_manifest),
                "mayaStdout": str(maya_stdout),
                "mayaStderr": str(maya_stderr),
                "unrealStdout": str(unreal_stdout),
                "unrealStderr": str(unreal_stderr),
                "mayapy": str(mayapy),
                "unrealCli": str(unreal_cli),
                "project": str(PROJECT_PATH),
                "reportVersion": report.get("reportVersion") if report else None,
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
