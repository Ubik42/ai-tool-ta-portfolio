from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_GAMEPLAY_ATTACH_OUTPUT"])
    socket_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_GAMEPLAY_ATTACH_SOURCE"])
    manifest_path = Path(os.environ["AI_TOOL_TA_UNREAL_GAMEPLAY_ATTACH_MANIFEST"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_socket_import_checker.gameplay_attach import build_gameplay_attach_report
    from unreal_socket_import_checker.contract import public_path

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    asset_paths = _asset_paths_from_manifest(manifest)
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "assetRegistryScanned": True,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "/Game/AI_Tool_TA public fixture only",
        },
        "facts": {
            "assetsByPath": {path: _asset_probe(unreal, path) for path in asset_paths},
            "assetRegistry": _asset_registry_probe(unreal, "/Game/AI_Tool_TA"),
        },
    }
    report = build_gameplay_attach_report(socket_artifact, manifest_path, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_GAMEPLAY_ATTACH_OUTPUT=%s" % output_path)


def _asset_paths_from_manifest(manifest: Dict[str, Any]) -> List[str]:
    paths = []
    for intent in manifest.get("intents", []):
        if intent.get("attachablePath"):
            paths.append(str(intent["attachablePath"]))
        paths.extend(str(path) for path in intent.get("animationAssetPaths", []))
    return sorted(set(paths))


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "Actor",
        "SceneComponent",
        "StaticMesh",
        "StaticMeshActor",
        "SkeletalMeshComponent",
        "EditorAssetLibrary",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    actor_methods = _method_names(unreal.Actor, ["attach"]) if hasattr(unreal, "Actor") else []
    component_methods = _method_names(unreal.SceneComponent, ["attach", "socket"]) if hasattr(unreal, "SceneComponent") else []
    return {
        "classes": classes,
        "actorAttachMethods": actor_methods[:80],
        "sceneComponentAttachMethods": component_methods[:80],
    }


def _asset_probe(unreal, path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return {"path": path, "exists": False}
    exists = _safe(lambda: bool(unreal.EditorAssetLibrary.does_asset_exist(path)), False)
    asset = _safe(lambda: unreal.EditorAssetLibrary.load_asset(path), None) if exists else None
    return {
        "path": path,
        "exists": bool(exists),
        "class": _asset_class(unreal, path) if exists else None,
        "pathName": _safe(lambda: str(asset.get_path_name()), None) if asset else None,
        "package": _safe(lambda: str(asset.get_outermost().get_name()), None) if asset else None,
    }


def _asset_registry_probe(unreal, package_path: str) -> List[Dict[str, Any]]:
    try:
        paths = unreal.EditorAssetLibrary.list_assets(package_path, recursive=True, include_folder=False)
    except Exception:
        return []
    return [
        {
            "path": _package_path(str(path)),
            "class": _asset_class(unreal, _package_path(str(path))),
        }
        for path in paths
    ]


def _asset_class(unreal, path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    try:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(path)
        if not asset_data or not asset_data.is_valid():
            return None
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return None


def _method_names(obj: Any, terms: Iterable[str]) -> List[str]:
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _package_path(path: str) -> str:
    return path.split(".")[0]


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
