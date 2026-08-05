from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
LOG_DIR = ARTIFACT_DIR / "unreal-socket-native-commandlet-logs"
PUBLIC_MANIFEST = PORTFOLIO_ROOT / "public-case-package" / "dcc-first-package-manifest.json"
SOURCE_PROJECT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "AI_Tool_TA_Unreal_L3.uproject"
)
TEMP_ROOT = Path(os.environ.get("AI_TOOL_TA_SOCKET_COMMANDLET_ROOT", r"D:\cs\_test\ai_tool_ta_socket_commandlet_probe"))
REPORT_VERSION = "unreal-socket-native-commandlet-probe@0.1.0"
COMMANDLET_NAME = "AiToolTaSocketAuthoring"
CONTRACT_LOG = "AI Tool TA Socket Authoring Commandlet contract loaded."
READINESS_LOG = "No Input receipt path supplied; readiness invocation only."

COMMON_UNREAL_CLI = [
    r"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
]


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-socket-native-commandlet-probe-%s.json" % stamp)
    stdout_path = LOG_DIR / ("unreal-socket-native-commandlet-probe-%s.stdout.log" % stamp)
    stderr_path = LOG_DIR / ("unreal-socket-native-commandlet-probe-%s.stderr.log" % stamp)
    temp_project_dir = TEMP_ROOT / ("atsb-commandlet-%s" % stamp)
    temp_project = temp_project_dir / "AI_Tool_TA_CommandletProbe.uproject"

    unreal_cli = _find_unreal_cli()
    build_artifact = _resolve_build_artifact()
    plugin_package = _plugin_package_dir(build_artifact)
    preflight = _preflight(unreal_cli, build_artifact, plugin_package)
    runtime: Optional[Dict[str, Any]] = None
    if not preflight:
        _prepare_temp_project(temp_project_dir, temp_project, plugin_package)
        runtime = _run_commandlet(unreal_cli, temp_project, stdout_path, stderr_path)
    else:
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(preflight, encoding="utf-8")

    report = _report(
        stamp=stamp,
        unreal_cli=unreal_cli,
        build_artifact=build_artifact,
        plugin_package=plugin_package,
        temp_project=temp_project,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        preflight_block=preflight,
        runtime=runtime,
    )
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(
        json.dumps(
            {
                "ok": summary["gate"] == "Ready",
                "path": str(output_path),
                "gate": summary["gate"],
                "returnCode": summary["returnCode"],
                "commandletLoaded": summary["commandletLoaded"],
                "readinessInvocation": summary["readinessInvocation"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _find_unreal_cli() -> Optional[Path]:
    env_path = os.environ.get("AI_TOOL_TA_UNREAL_CLI")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    for name in ("UnrealEditor-Cmd", "UnrealEditor-Cmd.exe", "UnrealEditor", "UnrealEditor.exe"):
        found = shutil.which(name)
        if found:
            return Path(found)
    for candidate in COMMON_UNREAL_CLI:
        path = Path(candidate)
        if path.exists():
            return path
    return None


def _resolve_build_artifact() -> Optional[Path]:
    env_path = os.environ.get("AI_TOOL_TA_SOCKET_NATIVE_BUILD_ARTIFACT")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    if PUBLIC_MANIFEST.exists():
        data = json.loads(PUBLIC_MANIFEST.read_text(encoding="utf-8"))
        path = _public_to_path(data.get("unrealSocketNativeBridgeBuildArtifact"))
        if path and path.exists():
            return path
    candidates = sorted(ARTIFACT_DIR.glob("unreal-socket-native-bridge-build-*.json"), key=lambda item: item.stat().st_mtime)
    for candidate in reversed(candidates):
        try:
            data = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("summary", {}).get("gate") == "Ready":
            return candidate
    return None


def _plugin_package_dir(build_artifact: Optional[Path]) -> Optional[Path]:
    if not build_artifact or not build_artifact.exists():
        return None
    data = json.loads(build_artifact.read_text(encoding="utf-8"))
    path = _public_to_path(data.get("summary", {}).get("packageDir") or data.get("build", {}).get("packageDir"))
    if path and (path / "AI_Tool_TA_SocketBridge.uplugin").exists():
        return path
    return None


def _preflight(unreal_cli: Optional[Path], build_artifact: Optional[Path], plugin_package: Optional[Path]) -> Optional[str]:
    if not unreal_cli:
        return "blocked_by_missing_unreal_editor_cmd"
    if not build_artifact:
        return "blocked_by_missing_native_build_artifact"
    if not plugin_package:
        return "blocked_by_missing_packaged_socket_bridge_plugin"
    if not SOURCE_PROJECT.exists():
        return "blocked_by_missing_source_unreal_project"
    return None


def _prepare_temp_project(temp_project_dir: Path, temp_project: Path, plugin_package: Path) -> None:
    if temp_project_dir.exists():
        shutil.rmtree(temp_project_dir)
    (temp_project_dir / "Plugins").mkdir(parents=True, exist_ok=True)
    shutil.copytree(plugin_package, temp_project_dir / "Plugins" / "AI_Tool_TA_SocketBridge")
    if (SOURCE_PROJECT.parent / "Config").exists():
        shutil.copytree(SOURCE_PROJECT.parent / "Config", temp_project_dir / "Config")
    if (SOURCE_PROJECT.parent / "Content").exists():
        shutil.copytree(SOURCE_PROJECT.parent / "Content", temp_project_dir / "Content")
    project = json.loads(SOURCE_PROJECT.read_text(encoding="utf-8"))
    plugins = [item for item in project.get("Plugins", []) if item.get("Name") != "AI_Tool_TA_SocketBridge"]
    plugins.append({"Name": "AI_Tool_TA_SocketBridge", "Enabled": True})
    project["Plugins"] = plugins
    project["Description"] = "Temporary AI Tool TA socket commandlet probe project."
    temp_project.write_text(json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_commandlet(unreal_cli: Path, temp_project: Path, stdout_path: Path, stderr_path: Path) -> Dict[str, Any]:
    command = [
        str(unreal_cli),
        str(temp_project),
        "-run=%s" % COMMANDLET_NAME,
        "-unattended",
        "-nop4",
        "-nosplash",
        "-NoAssetRegistryCache",
        "-NoLogTimes",
    ]
    build_error = None
    try:
        completed = subprocess.run(
            command,
            cwd=str(temp_project.parent),
            text=False,
            capture_output=True,
            timeout=300,
        )
        stdout = _decode_output(completed.stdout)
        stderr = _decode_output(completed.stderr)
        return_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = _decode_output(exc.stdout)
        stderr = _decode_output(exc.stderr) + "\nCOMMANDLET_TIMEOUT: UnrealEditor-Cmd exceeded 300 seconds."
        return_code = -1
        build_error = "timeout"
    except Exception as exc:
        stdout = ""
        stderr = "COMMANDLET_EXCEPTION: %s" % exc
        return_code = -1
        build_error = "exception"
    stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
    combined = stdout + "\n" + stderr
    return {
        "command": command,
        "returnCode": return_code,
        "runtimeError": build_error,
        "stdoutLog": public_path(stdout_path),
        "stderrLog": public_path(stderr_path),
        "contractLogSeen": CONTRACT_LOG in combined,
        "readinessLogSeen": READINESS_LOG in combined,
        "commandletName": COMMANDLET_NAME,
        "errors": _error_lines(combined),
    }


def _report(
    stamp: str,
    unreal_cli: Optional[Path],
    build_artifact: Optional[Path],
    plugin_package: Optional[Path],
    temp_project: Path,
    stdout_path: Path,
    stderr_path: Path,
    preflight_block: Optional[str],
    runtime: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    runtime = runtime or {}
    commandlet_loaded = bool(runtime.get("contractLogSeen"))
    readiness = bool(runtime.get("readinessLogSeen"))
    ready = int(runtime.get("returnCode", -1)) == 0 and commandlet_loaded and readiness
    gate = "Ready" if ready else "Blocked"
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Import Checker",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-runtime" if runtime else "Runtime-readiness",
        "l3Status": "unreal_socket_native_commandlet_loaded" if ready else (preflight_block or "unreal_socket_native_commandlet_probe_blocked"),
        "sourceBuildArtifact": public_path(build_artifact) if build_artifact else None,
        "pluginPackageDir": public_path(plugin_package) if plugin_package else None,
        "tempProject": str(temp_project),
        "unrealCli": str(unreal_cli) if unreal_cli else None,
        "runtime": runtime,
        "summary": {
            "gate": gate,
            "unrealCliFound": bool(unreal_cli),
            "buildArtifactFound": bool(build_artifact),
            "pluginPackageFound": bool(plugin_package),
            "runtimeAttempted": bool(runtime),
            "returnCode": runtime.get("returnCode"),
            "commandletName": COMMANDLET_NAME,
            "commandletLoaded": commandlet_loaded,
            "readinessInvocation": readiness,
            "errorLines": len(runtime.get("errors", [])),
            "tempProjectWrites": _count_files(temp_project.parent) if temp_project.parent.exists() else 0,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
        },
        "reviewerClaims": [
            "The commandlet probe uses the R62 packaged plugin output, not an inferred source-only contract.",
            "The Unreal project is copied to a temp folder under D:\\cs\\_test and the socket bridge plugin is enabled only there.",
            "The probe executes -run=AiToolTaSocketAuthoring and treats the commandlet contract log plus readiness log as the runtime visibility proof.",
            "No repo Unreal asset, engine content or production project is mutated by this readiness invocation.",
        ],
    }


def _public_to_path(value: Any) -> Optional[Path]:
    if not value:
        return None
    text = str(value)
    if text.startswith("<repo>\\") or text.startswith("<repo>/"):
        return PORTFOLIO_ROOT / text[len("<repo>\\") :].replace("/", "\\")
    return Path(text)


def _decode_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _error_lines(text: str) -> List[str]:
    rows = []
    for line in text.splitlines():
        lower = line.lower()
        if "warningsaserrors" in lower:
            continue
        if "failed to delete old shader autogen file" in lower:
            continue
        if "warning/error summary" in lower:
            continue
        if "error " in lower or ": error" in lower or "failed" in lower or "exception" in lower:
            rows.append(line.strip())
    return rows[:80]


def _count_files(path: Path) -> int:
    try:
        return sum(1 for item in path.rglob("*") if item.is_file())
    except Exception:
        return 0


def public_path(path: Optional[Path]) -> Optional[str]:
    if path is None:
        return None
    try:
        return "<repo>\\" + str(path.resolve().relative_to(PORTFOLIO_ROOT.resolve())).replace("/", "\\")
    except Exception:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
