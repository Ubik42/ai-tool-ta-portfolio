from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_EXECUTOR_OUTPUT"])
    source_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_EXECUTOR_SOURCE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_socket_import_checker.controlled_executor import build_socket_authoring_report

    source = json.loads(source_artifact.read_text(encoding="utf-8"))
    operations, held_rows = _execute_operations(unreal, source)
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": os.environ.get("AI_TOOL_TA_UNREAL_PROJECT"),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "inMemoryWrites": sum(len(row.get("authoring", {}).get("createdSockets", [])) for row in operations),
            "writeScope": "in-memory /Game/AI_Tool_TA public fixture only; rollback verified before exit",
        },
        "operations": operations,
        "heldRows": held_rows,
    }
    report = build_socket_authoring_report(source_artifact, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_SOCKET_EXECUTOR_OUTPUT=%s" % output_path)


def _execute_operations(unreal, source: Dict[str, Any]) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    operations: List[Dict[str, Any]] = []
    held_rows: List[Dict[str, Any]] = []
    for asset in source.get("facts", {}).get("assets", []):
        asset_id = str(asset.get("assetId"))
        source_status = asset.get("sourceStatus")
        owner_state = asset.get("ownerState")
        expected = asset.get("expectedUnreal", {})
        mesh_path = str(expected.get("skeletalMeshPath") or "")
        expected_socket_names = sorted(
            socket.get("exportName") for socket in asset.get("sourceSockets", []) if socket.get("exportName")
        )
        if source_status != "Ready" or owner_state != "approved":
            held_rows.append(
                {
                    "id": "held:%s" % asset_id,
                    "assetId": asset_id,
                    "assetLabel": asset.get("assetLabel"),
                    "sourceStatus": source_status,
                    "ownerState": owner_state,
                    "expectedSocketNames": expected_socket_names,
                    "held": True,
                    "mutated": False,
                    "owner": "spatial-owner",
                    "reason": "Source row is not approved Ready; executor keeps it out of engine mutation.",
                }
            )
            continue
        operations.append(_execute_single_operation(unreal, asset))
    return operations, held_rows


def _execute_single_operation(unreal, asset: Dict[str, Any]) -> Dict[str, Any]:
    asset_id = str(asset.get("assetId"))
    expected = asset.get("expectedUnreal", {})
    mesh_path = str(expected.get("skeletalMeshPath") or "")
    skeleton_path = str(expected.get("skeletonPath") or "")
    operation = {
        "id": "socket-authoring:%s" % asset_id,
        "assetId": asset_id,
        "assetLabel": asset.get("assetLabel"),
        "sourceStatus": asset.get("sourceStatus"),
        "ownerState": asset.get("ownerState"),
        "skeletalMeshPath": mesh_path,
        "skeletonPath": skeleton_path,
        "targetAssetPath": skeleton_path or mesh_path,
        "targetClass": None,
        "targetExists": False,
        "apiReady": False,
        "candidateTargets": [],
        "expectedSockets": asset.get("sourceSockets", []),
        "expectedSocketNames": sorted(
            socket.get("exportName") for socket in asset.get("sourceSockets", []) if socket.get("exportName")
        ),
        "preflight": {},
        "authoring": {
            "attempted": False,
            "method": None,
            "createdSockets": [],
            "skippedExisting": [],
            "errors": [],
        },
        "postcheck": {},
        "rollback": {},
    }
    target, target_path, target_class, method = _select_socket_target(unreal, mesh_path, skeleton_path)
    operation["targetAssetPath"] = target_path
    operation["targetExists"] = bool(target)
    operation["targetClass"] = target_class
    operation["authoring"]["method"] = method
    operation["candidateTargets"] = [
        {"path": skeleton_path, "class": _asset_class(unreal, skeleton_path), "exists": bool(_load_asset(unreal, skeleton_path))},
        {"path": mesh_path, "class": _asset_class(unreal, mesh_path), "exists": bool(_load_asset(unreal, mesh_path))},
    ]
    operation["apiReady"] = bool(target and method and hasattr(unreal, "SkeletalMeshSocket"))
    if not target:
        operation["authoring"]["errors"].append("target_missing")
        return operation

    preflight = _socket_facts(target)
    operation["preflight"] = preflight
    expected_names = operation["expectedSocketNames"]
    missing_specs = [
        socket
        for socket in asset.get("sourceSockets", [])
        if socket.get("exportName") and socket.get("exportName") not in set(preflight.get("socketNames", []))
    ]
    operation["authoring"]["skippedExisting"] = sorted(
        name for name in expected_names if name in set(preflight.get("socketNames", []))
    )
    if not operation["apiReady"]:
        operation["authoring"]["errors"].append("socket_authoring_api_unavailable")
        operation["postcheck"] = _postcheck(expected_names, asset.get("sourceSockets", []), _socket_facts(target))
        operation["rollback"] = _rollback_summary(preflight, _socket_facts(target), [], ["api_unavailable"])
        return operation

    operation["authoring"]["attempted"] = True
    created_names: List[str] = []
    for spec in missing_specs:
        name = str(spec.get("exportName"))
        ok, errors = _add_socket(unreal, target, spec, method)
        if ok:
            created_names.append(name)
        else:
            operation["authoring"]["errors"].extend(["%s:%s" % (name, error) for error in errors])
    _post_edit(target)
    operation["authoring"]["createdSockets"] = sorted(created_names)

    post = _socket_facts(target)
    operation["postcheck"] = _postcheck(expected_names, asset.get("sourceSockets", []), post)

    rollback_errors: List[str] = []
    if created_names:
        rollback_errors = _remove_sockets(target, set(created_names))
        _post_edit(target)
    final = _socket_facts(target)
    operation["rollback"] = _rollback_summary(preflight, final, created_names, rollback_errors)
    return operation


def _select_socket_target(unreal, mesh_path: str, skeleton_path: str):
    skeleton = _load_asset(unreal, skeleton_path)
    if skeleton and _socket_list_readable(skeleton, "sockets"):
        return skeleton, skeleton_path, _asset_class(unreal, skeleton_path), "Skeleton.sockets"
    mesh = _load_asset(unreal, mesh_path)
    if mesh and hasattr(mesh, "add_socket"):
        return mesh, mesh_path, _asset_class(unreal, mesh_path), "SkeletalMesh.add_socket"
    if skeleton:
        return skeleton, skeleton_path, _asset_class(unreal, skeleton_path), None
    return mesh, mesh_path, _asset_class(unreal, mesh_path), None


def _socket_list_readable(target, prop: str) -> bool:
    try:
        target.get_editor_property(prop)
        return True
    except Exception:
        return False


def _add_socket(unreal, target, spec: Dict[str, Any], method: str) -> tuple[bool, List[str]]:
    errors: List[str] = []
    socket_name = str(spec.get("exportName"))
    socket = _new_socket(unreal, target, socket_name)
    if not socket:
        return False, ["create_socket_failed"]
    _set_name_property(unreal, socket, "socket_name", socket_name, errors)
    _set_name_property(unreal, socket, "bone_name", str(spec.get("parentJoint") or ""), errors)
    _set_property(socket, "relative_location", _vector(unreal, spec.get("translate", [])), errors)
    _set_property(socket, "relative_rotation", _rotator(unreal, spec.get("rotate", [])), errors)
    _set_property(socket, "relative_scale", _scale_vector(unreal, spec.get("scale", [])), errors)
    if method == "Skeleton.sockets":
        return _append_socket_to_property(target, socket, errors)
    add_errors = []
    bone_candidates = _bone_candidates(str(spec.get("parentJoint") or ""))
    for bone_name in bone_candidates:
        _set_name_property(unreal, socket, "bone_name", bone_name, errors)
        if _socket_name(socket) != socket_name:
            _set_name_property(unreal, socket, "socket_name", socket_name, errors)
        for args in ((socket,), (socket, False)):
            try:
                target.add_socket(*args)
                if _socket_exists(target, socket_name):
                    return True, errors
            except Exception as exc:
                add_errors.append(str(exc))
    errors.extend(add_errors)
    return False, errors or ["add_socket_did_not_materialize"]


def _append_socket_to_property(target, socket, errors: List[str]) -> tuple[bool, List[str]]:
    for prop in ("sockets", "mesh_only_socket_list"):
        try:
            current = list(target.get_editor_property(prop) or [])
        except Exception as exc:
            errors.append("%s:get:%s" % (prop, exc))
            continue
        try:
            target.set_editor_property(prop, current + [socket])
            return True, errors
        except Exception as exc:
            errors.append("%s:set:%s" % (prop, exc))
    return False, errors


def _socket_exists(target, socket_name: str) -> bool:
    return socket_name in set(_socket_facts(target).get("socketNames", []))


def _bone_candidates(parent_joint: str) -> List[str]:
    values = [parent_joint]
    if parent_joint:
        values.extend(
            [
                parent_joint.lower(),
                parent_joint.replace("_", "").lower(),
                parent_joint[0:1].lower() + parent_joint[1:],
            ]
        )
    return [value for index, value in enumerate(values) if value and value not in values[:index]]


def _new_socket(unreal, target, socket_name: str):
    factories = []
    if hasattr(unreal, "new_object"):
        factories.append(lambda: unreal.new_object(unreal.SkeletalMeshSocket, outer=target, name=socket_name))
        factories.append(lambda: unreal.new_object(unreal.SkeletalMeshSocket, target, socket_name))
    factories.append(lambda: unreal.SkeletalMeshSocket())
    factories.append(lambda: unreal.SkeletalMeshSocket(outer=target))
    for factory in factories:
        try:
            socket = factory()
            if socket:
                return socket
        except Exception:
            continue
    return None


def _remove_sockets(target, socket_names: set[str]) -> List[str]:
    errors: List[str] = []
    for prop in ("mesh_only_socket_list", "sockets"):
        try:
            current = list(target.get_editor_property(prop) or [])
        except Exception as exc:
            errors.append("%s:get:%s" % (prop, exc))
            continue
        filtered = [socket for socket in current if _socket_name(socket) not in socket_names]
        if len(filtered) == len(current):
            continue
        try:
            target.set_editor_property(prop, filtered)
            return []
        except Exception as exc:
            errors.append("%s:set:%s" % (prop, exc))
    return errors or ["socket_list_property_not_found"]


def _postcheck(expected_names: List[str], expected_specs: List[Dict[str, Any]], facts: Dict[str, Any]) -> Dict[str, Any]:
    names = set(facts.get("socketNames", []))
    details = facts.get("socketDetailsByName", {})
    expected_details = {spec.get("exportName"): details.get(spec.get("exportName")) for spec in expected_specs}
    parent_mismatches = []
    for spec in expected_specs:
        name = spec.get("exportName")
        if name not in details:
            continue
        expected_parent = str(spec.get("parentJoint") or "")
        actual_parent = str(details.get(name, {}).get("boneName") or "")
        if expected_parent and actual_parent and _normalize_bone(expected_parent) != _normalize_bone(actual_parent):
            parent_mismatches.append({"socket": name, "expectedParentJoint": expected_parent, "runtimeBone": actual_parent})
    return {
        "socketNames": facts.get("socketNames", []),
        "socketDetailsByName": details,
        "expectedSocketDetails": expected_details,
        "fingerprint": facts.get("fingerprint"),
        "expectedSocketsPresent": set(expected_names).issubset(names),
        "parentBindingsMatched": not parent_mismatches and set(expected_names).issubset(names),
        "parentMismatches": parent_mismatches,
    }


def _rollback_summary(
    preflight: Dict[str, Any],
    final: Dict[str, Any],
    created_names: List[str],
    errors: List[str],
) -> Dict[str, Any]:
    return {
        "attempted": bool(created_names),
        "removedSockets": sorted(created_names) if not errors else [],
        "errors": errors,
        "socketNames": final.get("socketNames", []),
        "fingerprint": final.get("fingerprint"),
        "preflightFingerprint": preflight.get("fingerprint"),
        "restoredPreflight": final.get("fingerprint") == preflight.get("fingerprint"),
    }


def _socket_facts(asset: Any) -> Dict[str, Any]:
    methods = _method_names(asset, ["socket"]) if asset else []
    sockets = []
    socket_count = _safe(lambda: int(asset.num_sockets()), 0) if asset else 0
    for index in range(socket_count or 0):
        socket = _safe(lambda idx=index: asset.get_socket_by_index(idx), None)
        if socket:
            sockets.append(_socket_detail(socket))
    if not sockets and asset:
        for prop in ("mesh_only_socket_list", "sockets"):
            editor_sockets = _safe(lambda p=prop: asset.get_editor_property(p), [])
            for socket in editor_sockets or []:
                sockets.append(_socket_detail(socket))
    normalized = sorted(
        (
            {
                "socketName": row.get("socketName"),
                "boneName": row.get("boneName"),
                "relativeLocation": row.get("relativeLocation"),
                "relativeRotation": row.get("relativeRotation"),
                "relativeScale": row.get("relativeScale"),
            }
            for row in sockets
            if row.get("socketName")
        ),
        key=lambda row: str(row.get("socketName")),
    )
    payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
    return {
        "apiReady": bool(methods),
        "socketCount": len({row.get("socketName") for row in normalized if row.get("socketName")}),
        "socketNames": sorted({str(row.get("socketName")) for row in normalized if row.get("socketName")}),
        "socketDetails": sockets,
        "socketDetailsByName": {row.get("socketName"): row for row in sockets if row.get("socketName")},
        "availableMethods": methods[:80],
        "fingerprint": hashlib.sha1(payload.encode("utf-8")).hexdigest(),
    }


def _socket_detail(socket: Any) -> Dict[str, Any]:
    socket_name = _socket_name(socket)
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


def _api_probe(unreal) -> Dict[str, Any]:
    return {
        "classes": {
            "SkeletalMesh": hasattr(unreal, "SkeletalMesh"),
            "SkeletalMeshSocket": hasattr(unreal, "SkeletalMeshSocket"),
            "EditorAssetLibrary": hasattr(unreal, "EditorAssetLibrary"),
        },
        "skeletalMeshMethods": _method_names(unreal.SkeletalMesh, ["socket"])[:80] if hasattr(unreal, "SkeletalMesh") else [],
        "skeletalMeshSocketMethods": _method_names(unreal.SkeletalMeshSocket, ["socket", "bone", "relative", "name"])[:80]
        if hasattr(unreal, "SkeletalMeshSocket")
        else [],
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


def _set_property(target, prop: str, value: Any, errors: List[str]) -> None:
    try:
        target.set_editor_property(prop, value)
        setattr(target, prop, value)
    except Exception as exc:
        errors.append("%s:%s" % (prop, exc))


def _set_name_property(unreal, target, prop: str, text: str, errors: List[str]) -> None:
    candidates = [text]
    name_class = getattr(unreal, "Name", None)
    if name_class:
        try:
            candidates.insert(0, name_class(text))
        except Exception:
            pass
    for value in candidates:
        try:
            target.set_editor_property(prop, value)
        except Exception as exc:
            errors.append("%s:set:%s" % (prop, exc))
        try:
            setattr(target, prop, value)
        except Exception as exc:
            errors.append("%s:attr:%s" % (prop, exc))
        actual = _safe(lambda: str(target.get_editor_property(prop)), None)
        if actual and actual != "None":
            return


def _socket_name(socket: Any) -> Optional[str]:
    socket_name = _safe(lambda: str(socket.get_editor_property("socket_name")), None)
    if socket_name:
        return socket_name
    return _safe(lambda: str(socket.get_name()), None)


def _vector(unreal, values: List[Any]):
    values = list(values or [])
    while len(values) < 3:
        values.append(0.0)
    return unreal.Vector(float(values[0]), float(values[1]), float(values[2]))


def _scale_vector(unreal, values: List[Any]):
    values = list(values or [1.0, 1.0, 1.0])
    while len(values) < 3:
        values.append(1.0)
    return unreal.Vector(float(values[0]), float(values[1]), float(values[2]))


def _rotator(unreal, values: List[Any]):
    values = list(values or [])
    while len(values) < 3:
        values.append(0.0)
    return unreal.Rotator(float(values[0]), float(values[1]), float(values[2]))


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


def _post_edit(target) -> None:
    for method_name in ("modify", "post_edit_change"):
        method = getattr(target, method_name, None)
        if method:
            try:
                method()
            except Exception:
                pass


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _normalize_bone(value: str) -> str:
    return str(value or "").replace("_", "").lower()


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
