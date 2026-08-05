from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
SOURCE_DEFORMATION_ARTIFACT = ROOT / "artifacts" / "unreal-control-rig-deformation-link-20260805-232729.json"
MAYA_FBX_SCRIPT = ROOT / "scripts" / "generate_face_skeleton_fbx.py"
UNREAL_PROJECT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "AI_Tool_TA_Unreal_L3.uproject"
)
UNREAL_SCRIPT = ROOT / "scripts" / "unreal_python" / "import_face_skeleton_fixture.py"


COMMON_MAYAPY = [
    r"C:\Program Files\Autodesk\Maya2026\bin\mayapy.exe",
    r"C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe",
    r"C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe",
    r"C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe",
    r"D:\Program Files\Autodesk\Maya2026\bin\mayapy.exe",
    r"D:\Program Files\Autodesk\Maya2025\bin\mayapy.exe",
    r"D:\Program Files\Autodesk\Maya2024\bin\mayapy.exe",
]
COMMON_UNREAL_CLI = [
    r"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"D:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def find_mayapy() -> Optional[str]:
    env_path = os.environ.get("AI_TOOL_TA_MAYAPY")
    if env_path and Path(env_path).exists():
        return str(Path(env_path))
    for name in ("mayapy", "mayapy.exe"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in COMMON_MAYAPY:
        if Path(candidate).exists():
            return candidate
    return None


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
    mayapy = find_mayapy()
    unreal_cli = find_unreal_cli()
    source_deformation = Path(os.environ.get("AI_TOOL_TA_UNREAL_CONTROL_RIG_FACE_SKELETON_SOURCE", SOURCE_DEFORMATION_ARTIFACT))
    artifact_dir = ROOT / "artifacts"
    logs_dir = artifact_dir / "unreal-control-rig-face-skeleton-fixture-logs"
    temp_dir = PORTFOLIO_ROOT / ".tmp" / "unreal-control-rig-face-skeleton-fixture"
    fbx_dir = temp_dir / "fbx"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("unreal-control-rig-face-skeleton-fixture-%s.json" % stamp)
    fbx_manifest = temp_dir / ("face-skeleton-fbx-fixture-%s.json" % stamp)

    if not mayapy or not unreal_cli or not UNREAL_PROJECT.exists() or not source_deformation.exists():
        reason = (
            "blocked_by_missing_mayapy"
            if not mayapy
            else "blocked_by_missing_unreal_cli"
            if not unreal_cli
            else "blocked_by_missing_unreal_project"
            if not UNREAL_PROJECT.exists()
            else "blocked_by_missing_source_deformation_artifact"
        )
        path = _blocked(output_path, reason, source_deformation, fbx_manifest, mayapy, unreal_cli)
        print(json.dumps({"ok": False, "path": str(path), "reason": reason}, ensure_ascii=False, indent=2))
        return 0

    maya_stdout = logs_dir / ("face-skeleton-maya-%s.stdout.log" % stamp)
    maya_stderr = logs_dir / ("face-skeleton-maya-%s.stderr.log" % stamp)
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
        path = _blocked(output_path, "blocked_by_maya_face_skeleton_fbx_generation_failed", source_deformation, fbx_manifest, mayapy, unreal_cli)
        print(
            json.dumps(
                {
                    "ok": False,
                    "path": str(path),
                    "reason": "blocked_by_maya_face_skeleton_fbx_generation_failed",
                    "mayaReturnCode": maya_run.returncode,
                    "mayaStdout": str(maya_stdout),
                    "mayaStderr": str(maya_stderr),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    unreal_stdout = logs_dir / ("face-skeleton-unreal-%s.stdout.log" % stamp)
    unreal_stderr = logs_dir / ("face-skeleton-unreal-%s.stderr.log" % stamp)
    env = os.environ.copy()
    env["AI_TOOL_TA_UNREAL_CONTROL_RIG_ROOT"] = str(ROOT)
    env["AI_TOOL_TA_UNREAL_CONTROL_RIG_FACE_SKELETON_OUTPUT"] = str(output_path)
    env["AI_TOOL_TA_UNREAL_CONTROL_RIG_FACE_SKELETON_SOURCE"] = str(source_deformation)
    env["AI_TOOL_TA_UNREAL_CONTROL_RIG_FACE_SKELETON_FBX_MANIFEST"] = str(fbx_manifest)
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
    completed = subprocess.run(command, cwd=str(ROOT), env=env, text=True, capture_output=True, timeout=360)
    unreal_stdout.write_text(completed.stdout, encoding="utf-8", errors="replace")
    unreal_stderr.write_text(completed.stderr, encoding="utf-8", errors="replace")

    ok = completed.returncode == 0 and output_path.exists()
    report = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() else None
    print(
        json.dumps(
            {
                "ok": ok,
                "returnCode": completed.returncode,
                "path": str(output_path) if output_path.exists() else None,
                "fbxManifest": str(fbx_manifest),
                "mayaStdout": str(maya_stdout),
                "mayaStderr": str(maya_stderr),
                "unrealStdout": str(unreal_stdout),
                "unrealStderr": str(unreal_stderr),
                "mayapy": str(mayapy),
                "unrealCli": str(unreal_cli),
                "project": str(UNREAL_PROJECT),
                "reportVersion": report.get("reportVersion") if report else None,
                "evidenceLevel": report.get("evidenceLevel") if report else None,
                "l3Status": report.get("l3Status") if report else None,
                "summary": report.get("facts", {}).get("summary") if report else None,
                "evaluation": report.get("evaluation", {}).get("summary") if report else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if ok else 1


def _blocked(
    output_path: Path,
    reason: str,
    source_deformation: Path,
    fbx_manifest: Path,
    mayapy: Optional[str],
    unreal_cli: Optional[str],
) -> Path:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_control_rig_bridge.face_skeleton_fixture import build_face_skeleton_fixture_report

    runtime_snapshot = {
        "runtime": {
            "executed": False,
            "runtime": "preflight",
            "engineVersion": "not_entered",
            "pythonVersion": sys.version,
            "projectPath": public_path(UNREAL_PROJECT),
            "unrealCli": unreal_cli,
            "mayapy": mayapy,
            "blockedReason": reason,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "import": {"attempted": False, "success": False, "failures": [reason]},
        "faceSkeleton": {},
    }
    report = build_face_skeleton_fixture_report(source_deformation, fbx_manifest if fbx_manifest.exists() else None, runtime_snapshot)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    raise SystemExit(main())
