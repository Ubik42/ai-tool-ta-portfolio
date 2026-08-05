from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_NATIVE_BRIDGE_OUTPUT"])
    source_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_NATIVE_BRIDGE_SOURCE"])
    project_path = Path(os.environ["AI_TOOL_TA_UNREAL_PROJECT"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_socket_import_checker.native_bridge import build_native_bridge_report

    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": str(project_path),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "read-only public Unreal project readiness probe",
        },
        "project": _project_probe(project_path),
    }
    report = build_native_bridge_report(source_artifact, runtime_snapshot=runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_SOCKET_NATIVE_BRIDGE_OUTPUT=%s" % output_path)


def _api_probe(unreal: Any) -> Dict[str, Any]:
    class_names = [
        "SkeletalMesh",
        "Skeleton",
        "SkeletalMeshSocket",
        "EditorAssetLibrary",
        "EditorUtilitySubsystem",
        "EditorUtilityBlueprint",
        "EditorUtilityWidgetBlueprint",
        "AssetToolsHelpers",
        "BlueprintFunctionLibrary",
        "Commandlet",
        "EditorLoadingAndSavingUtils",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    return {
        "classes": classes,
        "commandletClasses": {
            "Commandlet": classes.get("Commandlet"),
            "AiToolTaSocketAuthoringCommandlet": hasattr(unreal, "AiToolTaSocketAuthoringCommandlet"),
        },
        "skeletalMeshSocketMethods": _method_names(getattr(unreal, "SkeletalMeshSocket", None), ["socket", "bone", "relative", "name"])[:80],
        "skeletonMethods": _method_names(getattr(unreal, "Skeleton", None), ["socket"])[:80],
        "skeletalMeshMethods": _method_names(getattr(unreal, "SkeletalMesh", None), ["socket"])[:80],
        "editorUtilitySubsystemMethods": _method_names(getattr(unreal, "EditorUtilitySubsystem", None), ["utility", "widget", "blueprint"])[:80],
        "assetToolsMethods": _method_names(getattr(unreal, "AssetToolsHelpers", None), ["asset", "factory", "blueprint"])[:80],
    }


def _project_probe(project_path: Path) -> Dict[str, Any]:
    project_dir = project_path.parent
    plugin_dir = project_dir / "Plugins" / "AI_Tool_TA_SocketBridge"
    source_dir = project_dir / "Source"
    bridge_source_dir = plugin_dir / "Source" / "AI_Tool_TA_SocketBridge"
    socket_bridge_files = _relative_existing_files(
        project_dir,
        [
            plugin_dir / "AI_Tool_TA_SocketBridge.uplugin",
            bridge_source_dir / "AI_Tool_TA_SocketBridge.Build.cs",
            bridge_source_dir / "Public" / "AiToolTaSocketAuthoringCommandlet.h",
            bridge_source_dir / "Private" / "AiToolTaSocketAuthoringCommandlet.cpp",
            bridge_source_dir / "Public" / "AiToolTaSocketBridgeLibrary.h",
            bridge_source_dir / "Private" / "AiToolTaSocketBridgeLibrary.cpp",
        ],
    )
    binaries = sorted(str(path.relative_to(project_dir)).replace("/", "\\") for path in plugin_dir.glob("Binaries/**/*.dll")) if plugin_dir.exists() else []
    project_json = _read_project_json(project_path)
    plugins = [
        str(row.get("Name"))
        for row in project_json.get("Plugins", [])
        if isinstance(row, dict) and row.get("Enabled", True)
    ]
    return {
        "projectPath": str(project_path),
        "engineAssociation": project_json.get("EngineAssociation"),
        "enabledPlugins": plugins,
        "hasSourceDir": source_dir.exists(),
        "hasPluginsDir": (project_dir / "Plugins").exists(),
        "hasSocketBridgePlugin": plugin_dir.exists(),
        "hasSocketBridgeSource": bridge_source_dir.exists(),
        "hasSocketBridgeBinary": bool(binaries),
        "socketBridgeFiles": socket_bridge_files,
        "socketBridgeBinaries": binaries,
        "pythonScriptPluginEnabled": "PythonScriptPlugin" in plugins,
        "editorScriptingUtilitiesEnabled": "EditorScriptingUtilities" in plugins,
    }


def _relative_existing_files(root: Path, paths: List[Path]) -> List[str]:
    rows = []
    for path in paths:
        if path.exists():
            rows.append(str(path.relative_to(root)).replace("/", "\\"))
    return sorted(rows)


def _read_project_json(project_path: Path) -> Dict[str, Any]:
    try:
        return json.loads(project_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    if obj is None:
        return []
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _safe(fn: Any, fallback: Any) -> Any:
    try:
        return fn()
    except Exception:
        return fallback


_main()
