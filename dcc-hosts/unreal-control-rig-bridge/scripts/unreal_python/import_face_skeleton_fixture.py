from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


CHARACTER_DIR = "/Game/AI_Tool_TA/Characters"
TEMP_ROOT = "/Game/AI_Tool_TA/_RuntimeImport/FaceSkeletonFixture"
SKELETAL_MESH_PATH = "/Game/AI_Tool_TA/Characters/SK_HeroFace"
SKELETON_PATH = "/Game/AI_Tool_TA/Characters/SK_HeroFace_Skeleton"


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_FACE_SKELETON_OUTPUT"])
    source_deformation = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_FACE_SKELETON_SOURCE"])
    fbx_manifest_path = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_FACE_SKELETON_FBX_MANIFEST"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_control_rig_bridge.face_skeleton_fixture import build_face_skeleton_fixture_report, public_path

    fbx_manifest = json.loads(fbx_manifest_path.read_text(encoding="utf-8"))
    import_result = _import_face_fixture(unreal, fbx_manifest)
    face_skeleton = _face_skeleton_facts(unreal)
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "assetWrites": import_result.get("assetWrites", 0),
            "engineWrites": import_result.get("engineWrites", 0),
            "productionWrites": 0,
            "writeScope": "/Game/AI_Tool_TA public face Skeleton fixture only",
        },
        "import": import_result,
        "faceSkeleton": face_skeleton,
    }
    report = build_face_skeleton_fixture_report(source_deformation, fbx_manifest_path, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_CONTROL_RIG_FACE_SKELETON_OUTPUT=%s" % output_path)


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "AssetImportTask",
        "AssetToolsHelpers",
        "EditorAssetLibrary",
        "FBXImportType",
        "FbxImportUI",
        "Skeleton",
        "SkeletalMesh",
    ]
    return {
        "classes": {name: hasattr(unreal, name) for name in class_names},
        "fbxImportUIProperties": _method_names(unreal.FbxImportUI(), ["anim", "mesh", "skeleton", "physics"])[:80]
        if hasattr(unreal, "FbxImportUI")
        else [],
        "skeletonMethods": _method_names(unreal.Skeleton, ["bone", "reference", "pose", "skeleton"])[:80]
        if hasattr(unreal, "Skeleton")
        else [],
    }


def _import_face_fixture(unreal, fbx_manifest: Dict[str, Any]) -> Dict[str, Any]:
    exported = fbx_manifest.get("fixture", {}).get("exported", {})
    fbx_path = Path(exported.get("path", ""))
    result: Dict[str, Any] = {
        "attempted": True,
        "success": False,
        "method": "AssetImportTask + FbxImportUI",
        "sourceFbx": str(fbx_path),
        "destination": TEMP_ROOT,
        "targetSkeletalMeshPath": SKELETAL_MESH_PATH,
        "targetSkeletonPath": SKELETON_PATH,
        "importedObjectPaths": [],
        "renamed": {},
        "failures": [],
        "assetWrites": 0,
        "engineWrites": 0,
        "savePackage": False,
    }
    if not fbx_path.exists():
        result["failures"].append("generated_fbx_not_found:%s" % fbx_path)
        return result
    if not all(hasattr(unreal, name) for name in ["AssetToolsHelpers", "AssetImportTask", "FbxImportUI", "EditorAssetLibrary"]):
        result["failures"].append("required_unreal_import_api_missing")
        return result

    editor_assets = unreal.EditorAssetLibrary
    _make_directory(editor_assets, CHARACTER_DIR)
    _delete_directory(editor_assets, TEMP_ROOT)
    _make_directory(editor_assets, TEMP_ROOT)
    _delete_asset(editor_assets, SKELETAL_MESH_PATH)
    _delete_asset(editor_assets, SKELETON_PATH)

    options_report: Dict[str, Any] = {}
    task = _build_import_task(unreal, fbx_path, TEMP_ROOT, options_report)
    imported_paths = _run_import_task(unreal, task, TEMP_ROOT)
    result["importedObjectPaths"] = imported_paths
    result["options"] = options_report
    result["renamed"] = _rename_imported_assets(unreal, imported_paths)
    result["assetWrites"] = _count_present_targets(unreal)
    result["engineWrites"] = result["assetWrites"]
    result["savePackage"] = bool(_save_directory(editor_assets, "/Game/AI_Tool_TA"))
    _delete_directory(editor_assets, TEMP_ROOT)
    _save_directory(editor_assets, "/Game/AI_Tool_TA")
    result["success"] = bool(editor_assets.does_asset_exist(SKELETAL_MESH_PATH) and editor_assets.does_asset_exist(SKELETON_PATH))
    if not result["success"]:
        result["failures"].append("target_assets_missing_after_import")
    return result


def _build_import_task(unreal, fbx_path: Path, destination: str, options_report: Dict[str, Any]):
    task = unreal.AssetImportTask()
    _set_property(task, "filename", str(fbx_path), options_report)
    _set_property(task, "destination_path", destination, options_report)
    _set_property(task, "automated", True, options_report)
    _set_property(task, "replace_existing", True, options_report)
    _set_property(task, "save", False, options_report)

    ui = unreal.FbxImportUI()
    _set_property(ui, "automated_import_should_detect_type", False, options_report)
    if hasattr(unreal, "FBXImportType"):
        _set_property(ui, "mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH, options_report)
    _set_property(ui, "import_mesh", True, options_report)
    _set_property(ui, "import_as_skeletal", True, options_report)
    _set_property(ui, "import_animations", False, options_report)
    _set_property(ui, "create_physics_asset", False, options_report)
    _set_property(task, "options", ui, options_report)
    return task


def _run_import_task(unreal, task, destination: str) -> List[str]:
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported = [_package_path(str(path)) for path in (_get_property(task, "imported_object_paths", []) or [])]
    try:
        scanned = [_package_path(str(path)) for path in unreal.EditorAssetLibrary.list_assets(destination, recursive=True, include_folder=False)]
    except Exception:
        scanned = []
    result = []
    seen = set()
    for path in imported + scanned:
        if path in seen:
            continue
        seen.add(path)
        result.append(path)
    return result


def _rename_imported_assets(unreal, imported_paths: List[str]) -> Dict[str, Any]:
    report: Dict[str, Any] = {"skeletalMeshPath": None, "skeletonPath": None, "rows": []}
    targets = {"SkeletalMesh": SKELETAL_MESH_PATH, "Skeleton": SKELETON_PATH}
    editor_assets = unreal.EditorAssetLibrary
    for source in imported_paths:
        source = _package_path(source)
        class_name = _asset_class(unreal, source)
        target = targets.get(class_name)
        row = {"source": source, "class": class_name, "target": target, "renamed": False}
        if target:
            if editor_assets.does_asset_exist(target):
                editor_assets.delete_asset(target)
            row["renamed"] = target == source or bool(editor_assets.rename_asset(source, target))
            final_path = target if row["renamed"] else source
            if class_name == "SkeletalMesh":
                report["skeletalMeshPath"] = final_path
            elif class_name == "Skeleton":
                report["skeletonPath"] = final_path
        elif class_name == "PhysicsAsset":
            row["deleted"] = _delete_asset(editor_assets, source)
        report["rows"].append(row)
    return report


def _face_skeleton_facts(unreal) -> Dict[str, Any]:
    skeleton = _load_asset(unreal, SKELETON_PATH)
    skeletal_mesh = _load_asset(unreal, SKELETAL_MESH_PATH)
    bone_names, probe = _skeleton_bone_names(skeleton)
    required = ["Head", "Jaw", "Eye_L", "Eye_R"]
    return {
        "skeletalMeshPath": SKELETAL_MESH_PATH,
        "skeletalMeshExists": bool(skeletal_mesh),
        "skeletalMeshClass": _asset_class(unreal, SKELETAL_MESH_PATH) if skeletal_mesh else None,
        "skeletonPath": SKELETON_PATH,
        "exists": bool(skeleton),
        "class": _asset_class(unreal, SKELETON_PATH) if skeleton else None,
        "boneNamesReadable": probe.get("readable"),
        "boneNames": bone_names,
        "boneProbe": probe,
        "requiredTargets": required,
        "targetMatches": {target: target in set(bone_names) for target in required},
    }


def _skeleton_bone_names(asset: Any) -> tuple[List[str], Dict[str, Any]]:
    if not asset:
        return [], {"readable": False, "method": None, "count": 0, "errors": ["skeleton_asset_missing"]}
    errors = []
    pose = _safe(lambda: asset.get_reference_pose(), None)
    if pose is not None:
        names = _names_from_reference_pose(pose)
        if names:
            return sorted(set(names)), {"readable": True, "method": "Skeleton.get_reference_pose", "count": len(set(names)), "errors": []}
        errors.append("get_reference_pose returned no readable bone names")
    else:
        errors.append("get_reference_pose unavailable")
    return [], {
        "readable": False,
        "method": "Skeleton.get_reference_pose",
        "count": 0,
        "errors": errors,
        "availableMethods": _method_names(asset, ["bone", "reference", "skeleton", "pose"])[:80],
        "referencePoseMethods": _method_names(pose, ["bone", "name", "pose", "track"])[:80] if pose else [],
    }


def _names_from_reference_pose(pose: Any) -> List[str]:
    for method_name in ("get_bone_names", "get_all_bone_names", "get_track_names", "get_curve_names"):
        method = getattr(pose, method_name, None)
        if not method:
            continue
        for args in ((), (False,), (True,)):
            try:
                values = method(*args)
                names = [str(value) for value in values or [] if str(value)]
                if names:
                    return names
            except Exception:
                continue
    for count_method, name_method in (("get_num_bones", "get_bone_name"), ("get_bone_count", "get_bone_name")):
        count_fn = getattr(pose, count_method, None)
        name_fn = getattr(pose, name_method, None)
        if not count_fn or not name_fn:
            continue
        try:
            count = int(count_fn())
        except Exception:
            continue
        names = []
        for index in range(count):
            try:
                names.append(str(name_fn(index)))
            except Exception:
                continue
        if names:
            return names
    return []


def _asset_class(unreal, path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    try:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(_package_path(path))
        if not asset_data or not asset_data.is_valid():
            return None
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return None


def _load_asset(unreal, path: Optional[str]):
    if not path:
        return None
    try:
        return unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    except Exception:
        return None


def _count_present_targets(unreal) -> int:
    return sum(
        1
        for path in [SKELETAL_MESH_PATH, SKELETON_PATH]
        if unreal.EditorAssetLibrary.does_asset_exist(path)
    )


def _set_property(obj, name: str, value: Any, report: Dict[str, Any]) -> bool:
    try:
        obj.set_editor_property(name, value)
        report["set:%s.%s" % (obj.__class__.__name__, name)] = True
        return True
    except Exception as exc:
        report["set:%s.%s" % (obj.__class__.__name__, name)] = "failed:%s" % exc
        return False


def _get_property(obj, name: str, fallback: Any) -> Any:
    try:
        return obj.get_editor_property(name)
    except Exception:
        return fallback


def _delete_asset(editor_assets, path: Optional[str]) -> bool:
    if not path:
        return False
    try:
        return bool(editor_assets.does_asset_exist(path) and editor_assets.delete_asset(path))
    except Exception:
        return False


def _make_directory(editor_assets, path: str) -> bool:
    try:
        return bool(editor_assets.make_directory(path))
    except Exception:
        return False


def _delete_directory(editor_assets, path: str) -> bool:
    try:
        return bool(editor_assets.delete_directory(path))
    except Exception:
        return False


def _save_directory(editor_assets, path: str) -> bool:
    try:
        return bool(editor_assets.save_directory(path, only_if_is_dirty=False, recursive=True))
    except Exception:
        try:
            return bool(editor_assets.save_directory(path))
        except Exception:
            return False


def _package_path(path: str) -> str:
    return path.split(".")[0]


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    if not obj:
        return []
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
