from __future__ import annotations

import hashlib
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
PLUGIN = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "unreal-handoff-inspector"
    / "projects"
    / "AI_Tool_TA_Unreal_L3"
    / "Plugins"
    / "AI_Tool_TA_SocketBridge"
    / "AI_Tool_TA_SocketBridge.uplugin"
)
ARTIFACT_DIR = ROOT / "artifacts"
LOG_DIR = ARTIFACT_DIR / "unreal-socket-native-build-logs"
BUILD_ROOT = Path(os.environ.get("AI_TOOL_TA_SOCKET_BRIDGE_BUILD_ROOT", r"D:\cs\_test\ai_tool_ta_socket_builds"))
REPORT_VERSION = "unreal-socket-native-bridge-build@0.1.0"
PREFERRED_MSVC_FAMILIES = ("14.38.", "14.37.", "14.36.", "14.35.", "14.34.")


COMMON_UAT = [
    r"C:\Program Files\Epic Games\UE_5.6\Engine\Build\BatchFiles\RunUAT.bat",
    r"C:\Program Files\Epic Games\UE_5.5\Engine\Build\BatchFiles\RunUAT.bat",
    r"C:\Program Files\Epic Games\UE_5.4\Engine\Build\BatchFiles\RunUAT.bat",
    r"C:\Program Files\Epic Games\UE_5.3\Engine\Build\BatchFiles\RunUAT.bat",
    r"C:\Program Files\Epic Games\UE_5.2\Engine\Build\BatchFiles\RunUAT.bat",
]


def main() -> int:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-socket-native-bridge-build-%s.json" % stamp)
    stdout_path = LOG_DIR / ("unreal-socket-native-bridge-build-%s.stdout.log" % stamp)
    stderr_path = LOG_DIR / ("unreal-socket-native-bridge-build-%s.stderr.log" % stamp)
    package_dir = BUILD_ROOT / ("atsb-%s" % stamp)

    uat = _find_uat()
    toolchain = _toolchain_probe()
    preflight = _preflight(uat, toolchain)
    if preflight:
        report = _report(stamp, output_path, stdout_path, stderr_path, package_dir, uat, toolchain, preflight, None)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"ok": False, "path": str(output_path), "reason": preflight}, ensure_ascii=False, indent=2))
        return 0

    build_env = os.environ.copy()
    build_config = _prepare_build_configuration(toolchain, BUILD_ROOT, stamp)
    command = [
        str(uat),
        "BuildPlugin",
        "-Plugin=%s" % str(PLUGIN),
        "-Package=%s" % str(package_dir),
        "-TargetPlatforms=Win64",
        "-Rocket",
        "-NoP4",
    ]
    build_error = None
    try:
        completed = subprocess.run(
            command,
            cwd=str(PORTFOLIO_ROOT),
            env=build_env,
            text=False,
            capture_output=True,
            timeout=900,
        )
        stdout = _decode_output(completed.stdout)
        stderr = _decode_output(completed.stderr)
        return_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = _decode_output(exc.stdout)
        stderr = _decode_output(exc.stderr) + "\nBUILD_TIMEOUT: RunUAT exceeded 900 seconds."
        return_code = -1
        build_error = "timeout"
    except Exception as exc:
        stdout = ""
        stderr = "BUILD_EXCEPTION: %s" % exc
        return_code = -1
        build_error = "exception"
    finally:
        _restore_build_configuration(build_config)
    stdout_path.write_text(stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(stderr, encoding="utf-8", errors="replace")
    build = {
        "command": command,
        "returnCode": return_code,
        "buildError": build_error,
        "stdoutLog": public_path(stdout_path),
        "stderrLog": public_path(stderr_path),
        "packageDir": public_path(package_dir),
        "buildConfiguration": build_config,
        "dlls": _dll_rows(package_dir),
        "errors": _error_lines(stdout + "\n" + stderr),
    }
    report = _report(stamp, output_path, stdout_path, stderr_path, package_dir, uat, toolchain, None, build)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(
        json.dumps(
            {
                "ok": return_code == 0,
                "path": str(output_path),
                "gate": summary["gate"],
                "returnCode": return_code,
                "dlls": summary["compiledDlls"],
                "errors": summary["errorLines"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _find_uat() -> Optional[Path]:
    env_path = os.environ.get("AI_TOOL_TA_RUNUAT")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    found = shutil.which("RunUAT.bat") or shutil.which("RunUAT")
    if found:
        return Path(found)
    for candidate in COMMON_UAT:
        path = Path(candidate)
        if path.exists():
            return path
    return None


def _toolchain_probe() -> Dict[str, Any]:
    roots = [
        Path(r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC"),
        Path(r"C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Tools\MSVC"),
        Path(r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Tools\MSVC"),
        Path(r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC"),
        Path(r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC"),
    ]
    versions = []
    for root in roots:
        if root.exists():
            versions.extend(str(path) for path in sorted(root.iterdir()) if path.is_dir())
    preferred = _preferred_msvc_version(versions)
    return {
        "msvcVersions": versions,
        "preferredCompilerVersion": preferred,
        "preferredCompilerReason": _preferred_msvc_reason(preferred, versions),
        "clOnPath": shutil.which("cl.exe"),
        "dotnetOnPath": shutil.which("dotnet.exe"),
        "msbuildOnPath": shutil.which("MSBuild.exe"),
    }


def _preflight(uat: Optional[Path], toolchain: Dict[str, Any]) -> Optional[str]:
    if not uat:
        return "blocked_by_missing_runuat"
    if not PLUGIN.exists():
        return "blocked_by_missing_socket_bridge_uplugin"
    required = [
        PLUGIN.parent / "Source" / "AI_Tool_TA_SocketBridge" / "AI_Tool_TA_SocketBridge.Build.cs",
        PLUGIN.parent / "Source" / "AI_Tool_TA_SocketBridge" / "Public" / "AiToolTaSocketAuthoringCommandlet.h",
        PLUGIN.parent / "Source" / "AI_Tool_TA_SocketBridge" / "Private" / "AiToolTaSocketAuthoringCommandlet.cpp",
        PLUGIN.parent / "Source" / "AI_Tool_TA_SocketBridge" / "Public" / "AiToolTaSocketBridgeLibrary.h",
        PLUGIN.parent / "Source" / "AI_Tool_TA_SocketBridge" / "Private" / "AiToolTaSocketBridgeLibrary.cpp",
    ]
    if any(not path.exists() for path in required):
        return "blocked_by_missing_required_source_files"
    if not toolchain.get("msvcVersions"):
        return "blocked_by_missing_msvc_toolchain"
    return None


def _preferred_msvc_version(versions: List[str]) -> Optional[str]:
    names = [Path(path).name for path in versions]
    for prefix in PREFERRED_MSVC_FAMILIES:
        matches = sorted(name for name in names if name.startswith(prefix))
        if matches:
            return matches[-1]
    return None


def _preferred_msvc_reason(preferred: Optional[str], versions: List[str]) -> str:
    if preferred:
        return "UE 5.3 installed builds compile reliably with VS 2022 17.4+ MSVC 14.34-14.38; newer 14.44 can trip engine header preprocessor errors."
    if versions:
        return "MSVC is installed, but no preferred UE 5.3 compatible 14.34-14.38 family was found."
    return "No MSVC toolchain directory was found."


def _prepare_build_configuration(toolchain: Dict[str, Any], build_root: Path, stamp: str) -> Dict[str, Any]:
    preferred = toolchain.get("preferredCompilerVersion")
    if not preferred:
        return {
            "enabled": False,
            "reason": "no_preferred_compiler_version",
            "path": None,
            "backupPath": None,
            "compilerVersion": None,
            "restoreAction": "none",
            "restored": None,
        }
    config_path = _global_build_configuration_path()
    backup_path = build_root / "_ubt_config_backup" / ("BuildConfiguration-%s.xml" % stamp)
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    existed = config_path.exists()
    if existed:
        backup_path.write_bytes(config_path.read_bytes())
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        "\n".join(
            [
                '<?xml version="1.0" encoding="utf-8" ?>',
                '<Configuration xmlns="https://www.unrealengine.com/BuildConfiguration">',
                "  <WindowsPlatform>",
                "    <CompilerVersion>%s</CompilerVersion>" % preferred,
                "  </WindowsPlatform>",
                "</Configuration>",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return {
        "enabled": True,
        "reason": toolchain.get("preferredCompilerReason"),
        "mode": "temporary_global_ubt_config",
        "path": str(config_path),
        "backupPath": str(backup_path) if existed else None,
        "compilerVersion": preferred,
        "restoreAction": "restore_backup" if existed else "delete_generated_config",
        "restored": False,
    }


def _restore_build_configuration(build_config: Dict[str, Any]) -> None:
    if not build_config.get("enabled"):
        return
    config_path = Path(build_config["path"])
    backup = build_config.get("backupPath")
    try:
        if backup:
            config_path.write_bytes(Path(backup).read_bytes())
        elif config_path.exists():
            config_path.unlink()
        build_config["restored"] = True
    except Exception as exc:
        build_config["restored"] = False
        build_config["restoreError"] = str(exc)


def _global_build_configuration_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        root = Path(appdata)
    else:
        root = Path.home() / "AppData" / "Roaming"
    return root / "Unreal Engine" / "UnrealBuildTool" / "BuildConfiguration.xml"


def _decode_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _report(
    stamp: str,
    output_path: Path,
    stdout_path: Path,
    stderr_path: Path,
    package_dir: Path,
    uat: Optional[Path],
    toolchain: Dict[str, Any],
    preflight_block: Optional[str],
    build: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    build = build or {}
    dlls = build.get("dlls", [])
    errors = build.get("errors", [])
    succeeded = bool(build) and int(build.get("returnCode", -1)) == 0 and bool(dlls)
    gate = "Ready" if succeeded else "Blocked"
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Import Checker",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-build" if build else "Build-readiness",
        "l3Status": "unreal_socket_native_bridge_plugin_built" if succeeded else (preflight_block or "unreal_socket_native_bridge_build_blocked"),
        "sourcePlugin": public_path(PLUGIN),
        "runUAT": str(uat) if uat else None,
        "toolchain": toolchain,
        "build": build,
        "summary": {
            "gate": gate,
            "runUATFound": bool(uat),
            "msvcFound": bool(toolchain.get("msvcVersions")),
            "buildAttempted": bool(build),
            "returnCode": build.get("returnCode"),
            "compiledDlls": len(dlls),
            "errorLines": len(errors),
            "packageDir": public_path(package_dir),
            "stdoutLog": public_path(stdout_path),
            "stderrLog": public_path(stderr_path),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
        },
        "reviewerClaims": [
            "The socket bridge build harness uses Unreal RunUAT BuildPlugin against the public Editor plugin source.",
            "Build output is local and ignored; the committed evidence is the JSON receipt plus logs and DLL hashes.",
            "The harness temporarily injects and restores UBT BuildConfiguration.xml so UE 5.3 uses a compatible MSVC family.",
            "No Unreal asset or production content is mutated by the build readiness harness.",
        ],
    }


def _dll_rows(package_dir: Path) -> List[Dict[str, Any]]:
    rows = []
    if not package_dir.exists():
        return rows
    for path in sorted(package_dir.glob("**/*.dll")):
        rows.append({"path": public_path(path), "bytes": path.stat().st_size, "sha256": _sha256(path)})
    return rows


def _error_lines(text: str) -> List[str]:
    rows = []
    for line in text.splitlines():
        lower = line.lower()
        if "warningsaserrors" in lower:
            continue
        if "error " in lower or ": error" in lower or "failed" in lower or "exception" in lower:
            rows.append(line.strip())
    return rows[:80]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def public_path(path: Path) -> str:
    try:
        return "<repo>\\" + str(path.resolve().relative_to(PORTFOLIO_ROOT.resolve())).replace("/", "\\")
    except Exception:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
