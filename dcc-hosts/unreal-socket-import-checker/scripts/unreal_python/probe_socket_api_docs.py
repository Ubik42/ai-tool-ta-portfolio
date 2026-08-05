from __future__ import annotations

import inspect
import json
import os
from pathlib import Path


def _main() -> None:
    import unreal  # type: ignore

    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_SOCKET_API_DOCS_OUTPUT"])
    mesh_path = "/Game/AI_Tool_TA/Characters/SK_Hero"
    skeleton_path = "/Game/AI_Tool_TA/Characters/SK_Hero_Skeleton"
    mesh = _load_asset(unreal, mesh_path)
    skeleton = _load_asset(unreal, skeleton_path)
    socket = _new_socket(unreal, mesh)
    report = {
        "reportVersion": "unreal-socket-api-docs@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Import Checker",
        "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
        "classes": {
            "SkeletalMeshSocket": hasattr(unreal, "SkeletalMeshSocket"),
            "Name": hasattr(unreal, "Name"),
            "new_object": hasattr(unreal, "new_object"),
        },
        "mesh": _object_probe(mesh),
        "skeleton": _object_probe(skeleton),
        "socket": _object_probe(socket),
        "constructAttempts": _construct_attempts(unreal, mesh),
        "renameAttempts": _rename_attempts(socket),
        "componentAttempts": _component_attempts(unreal, socket, mesh),
        "docstrings": {
            "SkeletalMesh.add_socket": _doc(_safe(lambda: mesh.add_socket, None)),
            "SkeletalMesh.find_socket": _doc(_safe(lambda: mesh.find_socket, None)),
            "SkeletalMesh.find_socket_and_index": _doc(_safe(lambda: mesh.find_socket_and_index, None)),
            "SkeletalMeshSocket": _doc(getattr(unreal, "SkeletalMeshSocket", None)),
            "SkeletalMeshSocket.initialize_socket_from_location": _doc(
                _safe(lambda: socket.initialize_socket_from_location, None)
            ),
        },
        "signatures": {
            "SkeletalMesh.add_socket": _signature(_safe(lambda: mesh.add_socket, None)),
            "SkeletalMeshSocket": _signature(getattr(unreal, "SkeletalMeshSocket", None)),
            "SkeletalMeshSocket.initialize_socket_from_location": _signature(
                _safe(lambda: socket.initialize_socket_from_location, None)
            ),
        },
        "propertyWriteAttempts": _property_write_attempts(unreal, socket),
        "initializeAttempts": _initialize_attempts(unreal, socket, mesh),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_SOCKET_API_DOCS_OUTPUT=%s" % output_path)


def _object_probe(obj):
    if not obj:
        return None
    return {
        "class": _safe(lambda: obj.get_class().get_name(), None),
        "path": _safe(lambda: obj.get_path_name(), None),
        "methods": sorted(name for name in dir(obj) if any(term in name.lower() for term in ["socket", "bone", "relative", "name"]))[:120],
    }


def _property_write_attempts(unreal, socket):
    rows = []
    if not socket:
        return rows
    values = {
        "socket_name": "SK_Probe",
        "bone_name": "hand_l",
        "relative_location": unreal.Vector(1.0, 2.0, 3.0),
        "relative_rotation": unreal.Rotator(0.0, 0.0, 0.0),
        "relative_scale": unreal.Vector(1.0, 1.0, 1.0),
    }
    for prop, value in values.items():
        row = {"property": prop, "setEditor": None, "setAttr": None, "after": None}
        try:
            socket.set_editor_property(prop, value)
            row["setEditor"] = "ok"
        except Exception as exc:
            row["setEditor"] = str(exc)
        try:
            setattr(socket, prop, value)
            row["setAttr"] = "ok"
        except Exception as exc:
            row["setAttr"] = str(exc)
        row["after"] = _safe(lambda p=prop: str(socket.get_editor_property(p)), None)
        rows.append(row)
    return rows


def _initialize_attempts(unreal, socket, mesh):
    if not socket:
        return []
    attempts = []
    args_rows = [
        ("vector_rotator", (unreal.Vector(1.0, 2.0, 3.0), unreal.Rotator(0.0, 0.0, 0.0))),
        ("mesh_vector_rotator", (mesh, unreal.Vector(1.0, 2.0, 3.0), unreal.Rotator(0.0, 0.0, 0.0))),
        ("mesh_vector", (mesh, unreal.Vector(1.0, 2.0, 3.0))),
    ]
    for label, args in args_rows:
        row = {"label": label, "result": None, "after": {}}
        try:
            result = socket.initialize_socket_from_location(*args)
            row["result"] = str(result)
        except Exception as exc:
            row["result"] = str(exc)
        for prop in ("socket_name", "bone_name", "relative_location", "relative_rotation", "relative_scale"):
            row["after"][prop] = _safe(lambda p=prop: str(socket.get_editor_property(p)), None)
        attempts.append(row)
    return attempts


def _construct_attempts(unreal, outer):
    attempts = []
    factories = [
        ("default", lambda: unreal.SkeletalMeshSocket()),
        ("outer", lambda: unreal.SkeletalMeshSocket(outer=outer)),
        ("name", lambda: unreal.SkeletalMeshSocket(name="SK_Ctor")),
        ("outer_name", lambda: unreal.SkeletalMeshSocket(outer=outer, name="SK_Ctor")),
        ("socket_name_kw", lambda: unreal.SkeletalMeshSocket(socket_name="SK_Ctor", bone_name="hand_l")),
        ("outer_socket_name_kw", lambda: unreal.SkeletalMeshSocket(outer=outer, socket_name="SK_Ctor", bone_name="hand_l")),
    ]
    for label, factory in factories:
        row = {"label": label, "result": None, "probe": None}
        try:
            socket = factory()
            row["result"] = "ok"
            row["probe"] = _object_probe(socket)
            row["properties"] = {
                "socket_name": _safe(lambda: str(socket.get_editor_property("socket_name")), None),
                "bone_name": _safe(lambda: str(socket.get_editor_property("bone_name")), None),
            }
        except Exception as exc:
            row["result"] = str(exc)
        attempts.append(row)
    return attempts


def _rename_attempts(socket):
    attempts = []
    if not socket:
        return attempts
    for args in (("SK_Rename",), ("SK_Rename", None), ("SK_Rename", None, 0)):
        row = {"args": [str(arg) for arg in args], "result": None, "after": {}}
        try:
            result = socket.rename(*args)
            row["result"] = str(result)
        except Exception as exc:
            row["result"] = str(exc)
        row["after"] = {
            "name": _safe(lambda: socket.get_name(), None),
            "socket_name": _safe(lambda: str(socket.get_editor_property("socket_name")), None),
            "bone_name": _safe(lambda: str(socket.get_editor_property("bone_name")), None),
        }
        attempts.append(row)
    return attempts


def _component_attempts(unreal, socket, mesh):
    attempts = []
    if not socket or not mesh or not hasattr(unreal, "SkeletalMeshComponent"):
        return attempts
    component = None
    factories = [
        ("component_default", lambda: unreal.SkeletalMeshComponent()),
        ("component_new_object", lambda: unreal.new_object(unreal.SkeletalMeshComponent) if hasattr(unreal, "new_object") else None),
    ]
    for label, factory in factories:
        row = {"label": label, "create": None, "setMesh": None, "init": None, "after": {}}
        try:
            component = factory()
            row["create"] = "ok" if component else "none"
        except Exception as exc:
            row["create"] = str(exc)
            attempts.append(row)
            continue
        for method_name in ("set_skeletal_mesh", "set_editor_property"):
            try:
                if method_name == "set_skeletal_mesh":
                    component.set_skeletal_mesh(mesh)
                else:
                    component.set_editor_property("skeletal_mesh", mesh)
                row["setMesh"] = method_name
                break
            except Exception as exc:
                row["setMesh"] = str(exc)
        try:
            result = socket.initialize_socket_from_location(
                component,
                unreal.Vector(0.0, 0.0, 0.0),
                unreal.Vector(0.0, 0.0, 1.0),
            )
            row["init"] = str(result)
        except Exception as exc:
            row["init"] = str(exc)
        row["after"] = {
            "socket_name": _safe(lambda: str(socket.get_editor_property("socket_name")), None),
            "bone_name": _safe(lambda: str(socket.get_editor_property("bone_name")), None),
            "relative_location": _safe(lambda: str(socket.get_editor_property("relative_location")), None),
            "relative_rotation": _safe(lambda: str(socket.get_editor_property("relative_rotation")), None),
        }
        attempts.append(row)
    return attempts


def _new_socket(unreal, outer):
    factories = []
    if hasattr(unreal, "new_object"):
        factories.append(lambda: unreal.new_object(unreal.SkeletalMeshSocket, outer=outer, name="SK_Probe"))
        factories.append(lambda: unreal.new_object(unreal.SkeletalMeshSocket, outer, "SK_Probe"))
    factories.append(lambda: unreal.SkeletalMeshSocket())
    factories.append(lambda: unreal.SkeletalMeshSocket(outer=outer))
    for factory in factories:
        try:
            value = factory()
            if value:
                return value
        except Exception:
            continue
    return None


def _load_asset(unreal, path):
    try:
        return unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    except Exception:
        return None


def _doc(obj):
    if not obj:
        return None
    return str(getattr(obj, "__doc__", None))


def _signature(obj):
    if not obj:
        return None
    try:
        return str(inspect.signature(obj))
    except Exception as exc:
        return str(exc)


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
