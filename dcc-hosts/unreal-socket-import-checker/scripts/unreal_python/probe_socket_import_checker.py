from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_OUTPUT"])
    source_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_SOURCE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_socket_import_checker.contract import build_report, expected_unreal_targets, public_path

    source = json.loads(source_artifact.read_text(encoding="utf-8"))
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
            "engineWrites": 0,
            "assetWrites": 0,
            "writeScope": "/Game/AI_Tool_TA public fixture only",
        },
        "facts": {
            "spatialAssets": _spatial_asset_probe(unreal, source, expected_unreal_targets),
            "assetRegistry": _asset_registry_probe(unreal, "/Game/AI_Tool_TA/Characters"),
        },
    }
    report = build_report(source_artifact, runtime_snapshot=runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_SOCKET_OUTPUT=%s" % output_path)


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "SkeletalMesh",
        "Skeleton",
        "SkeletalMeshSocket",
        "EditorAssetLibrary",
        "AssetRegistryHelpers",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    skeletal_mesh_methods = []
    skeleton_methods = []
    socket_methods = []
    if hasattr(unreal, "SkeletalMesh"):
        skeletal_mesh_methods = _method_names(unreal.SkeletalMesh, ["socket", "skeleton", "bone", "mesh"])
    if hasattr(unreal, "Skeleton"):
        skeleton_methods = _method_names(unreal.Skeleton, ["socket", "skeleton", "bone", "reference"])
    if hasattr(unreal, "SkeletalMeshSocket"):
        socket_methods = _method_names(unreal.SkeletalMeshSocket, ["socket", "bone", "relative", "name"])
    return {
        "classes": classes,
        "skeletalMeshMethods": skeletal_mesh_methods[:80],
        "skeletonMethods": skeleton_methods[:80],
        "skeletalMeshSocketMethods": socket_methods[:80],
    }


def _spatial_asset_probe(unreal, source: Dict[str, Any], expected_unreal_targets_fn) -> Dict[str, Any]:
    rows = {}
    for row in source.get("drilldowns", []):
        asset_id = str(row.get("assetId"))
        expected = expected_unreal_targets_fn(asset_id, row)
        mesh_path = expected.get("skeletalMeshPath")
        skeleton_path = expected.get("skeletonPath")
        mesh_asset = _load_asset(unreal, mesh_path)
        skeleton_asset = _load_asset(unreal, skeleton_path)
        mesh_socket_facts = _socket_facts(mesh_asset)
        skeleton_socket_facts = _socket_facts(skeleton_asset)
        merged_details = {}
        merged_details.update(mesh_socket_facts.get("socketDetailsByName", {}))
        merged_details.update(skeleton_socket_facts.get("socketDetailsByName", {}))
        rows[asset_id] = {
            "assetId": asset_id,
            "skeletalMeshPath": mesh_path,
            "skeletonPath": skeleton_path,
            "skeletalMeshExists": bool(mesh_asset),
            "skeletonExists": bool(skeleton_asset),
            "skeletalMeshClass": _asset_class(unreal, mesh_path) if mesh_asset else None,
            "skeletonClass": _asset_class(unreal, skeleton_path) if skeleton_asset else None,
            "socketApiReady": bool(
                mesh_socket_facts.get("apiReady")
                or skeleton_socket_facts.get("apiReady")
            ),
            "skeletalMeshSocketCount": mesh_socket_facts.get("socketCount", 0),
            "skeletonSocketCount": skeleton_socket_facts.get("socketCount", 0),
            "skeletalMeshSocketNames": mesh_socket_facts.get("socketNames", []),
            "skeletonSocketNames": skeleton_socket_facts.get("socketNames", []),
            "socketDetailsByName": merged_details,
            "skeletalMeshFacts": _asset_facts(mesh_asset, ["socket", "skeleton", "bone", "mesh"]),
            "skeletonFacts": _asset_facts(skeleton_asset, ["socket", "skeleton", "bone", "reference"]),
        }
    return rows


def _socket_facts(asset: Any) -> Dict[str, Any]:
    if not asset:
        return {
            "apiReady": False,
            "socketCount": 0,
            "socketNames": [],
            "socketDetails": [],
            "socketDetailsByName": {},
            "availableMethods": [],
        }
    methods = _method_names(asset, ["socket"])
    sockets = []
    socket_count = _safe(lambda: int(asset.num_sockets()), 0)
    for index in range(socket_count or 0):
        socket = _safe(lambda idx=index: asset.get_socket_by_index(idx), None)
        if socket:
            sockets.append(_socket_detail(socket))
    if not sockets:
        editor_sockets = _safe(lambda: asset.get_editor_property("sockets"), [])
        for socket in editor_sockets or []:
            sockets.append(_socket_detail(socket))
    names = sorted(set(str(row.get("socketName")) for row in sockets if row.get("socketName")))
    return {
        "apiReady": bool(methods),
        "socketCount": len(names),
        "socketNames": names,
        "socketDetails": sockets,
        "socketDetailsByName": {row.get("socketName"): row for row in sockets if row.get("socketName")},
        "availableMethods": methods[:80],
    }


def _socket_detail(socket: Any) -> Dict[str, Any]:
    socket_name = _safe(lambda: str(socket.get_editor_property("socket_name")), None)
    if not socket_name:
        socket_name = _safe(lambda: str(socket.get_name()), None)
    bone_name = _safe(lambda: str(socket.get_editor_property("bone_name")), None)
    relative_location = _safe(lambda: _vector_tuple(socket.get_editor_property("relative_location")), None)
    relative_rotation = _safe(lambda: _rotator_tuple(socket.get_editor_property("relative_rotation")), None)
    relative_scale = _safe(lambda: _vector_tuple(socket.get_editor_property("relative_scale")), None)
    return {
        "socketName": socket_name,
        "boneName": bone_name,
        "relativeLocation": relative_location,
        "relativeRotation": relative_rotation,
        "relativeScale": relative_scale,
        "class": _safe(lambda: socket.get_class().get_name(), None),
    }


def _asset_registry_probe(unreal, package_path: str) -> List[Dict[str, Any]]:
    try:
        asset_paths = unreal.EditorAssetLibrary.list_assets(package_path, recursive=True, include_folder=False)
    except Exception:
        return []
    return [
        {
            "path": _package_path(str(path)),
            "class": _asset_class(unreal, _package_path(str(path))),
        }
        for path in asset_paths
    ]


def _asset_facts(asset: Any, terms: List[str]) -> Dict[str, Any]:
    if not asset:
        return {}
    return {
        "pathName": _safe(lambda: str(asset.get_path_name()), None),
        "class": _safe(lambda: asset.get_class().get_name(), None),
        "availableMethods": _method_names(asset, terms)[:80],
    }


def _load_asset(unreal, path: Optional[str]):
    if not path:
        return None
    try:
        return unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    except Exception:
        return None


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


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _package_path(path: str) -> str:
    return path.split(".")[0]


def _vector_tuple(value: Any) -> List[float]:
    return [
        float(_safe(lambda: value.x, 0.0) or 0.0),
        float(_safe(lambda: value.y, 0.0) or 0.0),
        float(_safe(lambda: value.z, 0.0) or 0.0),
    ]


def _rotator_tuple(value: Any) -> List[float]:
    return [
        float(_safe(lambda: value.roll, 0.0) or 0.0),
        float(_safe(lambda: value.pitch, 0.0) or 0.0),
        float(_safe(lambda: value.yaw, 0.0) or 0.0),
    ]


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
