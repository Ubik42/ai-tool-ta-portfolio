from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


CHARACTER_DIR = "/Game/AI_Tool_TA/Characters"
ANIMATION_DIR = "/Game/AI_Tool_TA/Animations"
TEMP_ROOT = "/Game/AI_Tool_TA/_RuntimeImport"


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_OUTPUT"])
    fbx_manifest_path = Path(os.environ["AI_TOOL_TA_UNREAL_ANIMATION_FBX_MANIFEST"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_animation_bridge.contract import build_report, public_path

    fixture_path = root / "fixtures" / "synthetic_unreal_animation_bridge.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fbx_manifest = json.loads(fbx_manifest_path.read_text(encoding="utf-8"))

    import_result = _import_fixture(unreal, fixture, fbx_manifest)
    runtime_snapshot = {
        "executed": True,
        "runtime": "Unreal Python",
        "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
        "pythonVersion": sys.version,
        "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
        "api": _api_probe(unreal),
        "assets": _asset_probe(unreal, fixture),
        "import": import_result,
        "mutation": {
            "engineWrites": import_result.get("engineWrites", 0),
            "assetWrites": import_result.get("assetWrites", 0),
            "savePackage": import_result.get("savePackage", False),
            "writeScope": "public synthetic Unreal test project only",
        },
    }
    report = build_report(fixture_path, runtime_snapshot=runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_ANIMATION_BRIDGE_OUTPUT=%s" % output_path)


def _api_probe(unreal) -> dict:
    class_names = [
        "AnimSequence",
        "AnimSequenceFactory",
        "AnimationBlueprintLibrary",
        "Skeleton",
        "SkeletalMesh",
        "EditorAssetLibrary",
        "AssetRegistryHelpers",
        "AssetToolsHelpers",
        "AssetImportTask",
        "FbxImportUI",
        "FbxSkeletalMeshImportData",
        "FbxAnimSequenceImportData",
        "FBXImportType",
        "FBXAnimationLengthImportType",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    import_ui_properties = []
    if hasattr(unreal, "FbxImportUI"):
        try:
            import_ui_properties = sorted(
                name
                for name in dir(unreal.FbxImportUI())
                if "anim" in name.lower()
                or "mesh" in name.lower()
                or "skeleton" in name.lower()
                or "physics" in name.lower()
            )
        except Exception:
            import_ui_properties = []
    return {
        "classes": classes,
        "fbxImportUIProperties": import_ui_properties[:80],
    }


def _import_fixture(unreal, fixture: Dict[str, Any], fbx_manifest: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "attempted": True,
        "success": False,
        "method": "AssetImportTask + FbxImportUI",
        "fbxManifest": {
            "reportVersion": fbx_manifest.get("reportVersion"),
            "clipCount": fbx_manifest.get("fixture", {}).get("clipCount"),
        },
        "clipImports": [],
        "failures": [],
        "engineWrites": 0,
        "assetWrites": 0,
        "savePackage": False,
    }
    if not all(hasattr(unreal, name) for name in ["AssetToolsHelpers", "AssetImportTask", "FbxImportUI", "EditorAssetLibrary"]):
        result["failures"].append("required_unreal_import_api_missing")
        return result

    editor_assets = unreal.EditorAssetLibrary
    _make_directory(editor_assets, CHARACTER_DIR)
    _make_directory(editor_assets, ANIMATION_DIR)
    _delete_directory(editor_assets, TEMP_ROOT)
    _make_directory(editor_assets, TEMP_ROOT)

    for sequence in fixture.get("animationSequences", []):
        _delete_asset(editor_assets, sequence.get("expectedAnimSequencePath"))
    first = (fixture.get("animationSequences") or [None])[0]
    if first:
        _delete_asset(editor_assets, first.get("expectedSkeletalMeshPath"))
        _delete_asset(editor_assets, first.get("expectedSkeletonPath"))

    clips = {
        item.get("sourceFbxClipName"): item
        for item in fbx_manifest.get("fixture", {}).get("clips", [])
        if isinstance(item, dict)
    }
    skeleton_path = first.get("expectedSkeletonPath") if first else None

    for index, sequence in enumerate(fixture.get("animationSequences", [])):
        clip_name = sequence.get("sourceFbxClipName")
        clip = clips.get(clip_name)
        if not clip:
            failure = "missing_generated_fbx:%s" % clip_name
            result["failures"].append(failure)
            result["clipImports"].append({"assetId": sequence.get("assetId"), "success": False, "failure": failure})
            continue
        fbx_path = Path(clip.get("path", ""))
        if not fbx_path.exists():
            failure = "generated_fbx_not_found:%s" % fbx_path
            result["failures"].append(failure)
            result["clipImports"].append({"assetId": sequence.get("assetId"), "success": False, "failure": failure})
            continue

        destination = "%s/%s" % (TEMP_ROOT, sequence.get("assetId"))
        _delete_directory(editor_assets, destination)
        _make_directory(editor_assets, destination)
        existing_skeleton = editor_assets.load_asset(skeleton_path) if skeleton_path and editor_assets.does_asset_exist(skeleton_path) else None
        import_mesh = index == 0 or existing_skeleton is None
        options_report: Dict[str, Any] = {}
        task = _build_import_task(
            unreal,
            fbx_path,
            destination,
            import_mesh=import_mesh,
            import_animations=True,
            skeleton=existing_skeleton,
            options_report=options_report,
        )
        imported_paths = _run_import_task(unreal, task, destination)
        rename_report = _rename_imported_assets(
            unreal,
            imported_paths,
            sequence,
            rename_skeleton=index == 0,
            rename_mesh=index == 0,
        )
        clip_success = bool(rename_report.get("animSequencePath")) and (
            index > 0
            or bool(rename_report.get("skeletonPath") and rename_report.get("skeletalMeshPath"))
        )
        if not clip_success:
            result["failures"].append("clip_import_incomplete:%s" % sequence.get("assetId"))
        result["clipImports"].append(
            {
                "assetId": sequence.get("assetId"),
                "sourceFbx": str(fbx_path),
                "destination": destination,
                "importMesh": import_mesh,
                "success": clip_success,
                "importedObjectPaths": imported_paths,
                "options": options_report,
                "renamed": rename_report,
            }
        )

    result["assetWrites"] = _count_present_targets(unreal, fixture)
    result["engineWrites"] = result["assetWrites"]
    result["savePackage"] = bool(_save_directory(editor_assets, "/Game/AI_Tool_TA"))
    _delete_directory(editor_assets, TEMP_ROOT)
    _save_directory(editor_assets, "/Game/AI_Tool_TA")
    result["importedAssetCount"] = result["assetWrites"]
    result["success"] = _all_expected_targets_present(unreal, fixture)
    return result


def _build_import_task(
    unreal,
    fbx_path: Path,
    destination: str,
    import_mesh: bool,
    import_animations: bool,
    skeleton: Any,
    options_report: Dict[str, Any],
):
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
    _set_property(ui, "import_mesh", import_mesh, options_report)
    _set_property(ui, "import_as_skeletal", True, options_report)
    _set_property(ui, "import_animations", import_animations, options_report)
    _set_property(ui, "create_physics_asset", False, options_report)
    if skeleton:
        _set_property(ui, "skeleton", skeleton, options_report)
    if hasattr(unreal, "FbxAnimSequenceImportData"):
        anim_data = unreal.FbxAnimSequenceImportData()
        _set_property(anim_data, "import_custom_attribute", True, options_report)
        _set_property(anim_data, "remove_redundant_keys", False, options_report)
        if hasattr(unreal, "FBXAnimationLengthImportType"):
            _set_property(
                anim_data,
                "animation_length",
                unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME,
                options_report,
            )
        _set_property(ui, "anim_sequence_import_data", anim_data, options_report)
    _set_property(task, "options", ui, options_report)
    return task


def _run_import_task(unreal, task, destination: str) -> List[str]:
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.import_asset_tasks([task])
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


def _rename_imported_assets(
    unreal,
    imported_paths: List[str],
    sequence: Dict[str, Any],
    rename_skeleton: bool,
    rename_mesh: bool,
) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "animSequencePath": None,
        "skeletonPath": None,
        "skeletalMeshPath": None,
        "rows": [],
    }
    targets = {
        "AnimSequence": sequence.get("expectedAnimSequencePath"),
        "Skeleton": sequence.get("expectedSkeletonPath") if rename_skeleton else None,
        "SkeletalMesh": sequence.get("expectedSkeletalMeshPath") if rename_mesh else None,
    }
    editor_assets = unreal.EditorAssetLibrary
    for source in imported_paths:
        source = _package_path(source)
        class_name = _asset_class(unreal, source)
        target = targets.get(class_name)
        row = {"source": source, "class": class_name, "target": target, "renamed": False}
        if target:
            if target != source and editor_assets.does_asset_exist(target):
                editor_assets.delete_asset(target)
            row["renamed"] = target == source or bool(editor_assets.rename_asset(source, target))
            final_path = target if row["renamed"] else source
            if class_name == "AnimSequence":
                report["animSequencePath"] = final_path
            elif class_name == "Skeleton":
                report["skeletonPath"] = final_path
            elif class_name == "SkeletalMesh":
                report["skeletalMeshPath"] = final_path
        report["rows"].append(row)
    return report


def _asset_probe(unreal, fixture: dict) -> dict:
    editor_assets = unreal.EditorAssetLibrary
    rows = {}
    missing = []
    present = []
    for sequence in fixture.get("animationSequences", []):
        anim_path = sequence.get("expectedAnimSequencePath")
        skeleton_path = sequence.get("expectedSkeletonPath")
        mesh_path = sequence.get("expectedSkeletalMeshPath")
        anim_exists = bool(editor_assets.does_asset_exist(anim_path))
        skeleton_exists = bool(editor_assets.does_asset_exist(skeleton_path))
        mesh_exists = bool(editor_assets.does_asset_exist(mesh_path)) if mesh_path else False
        anim_asset = editor_assets.load_asset(anim_path) if anim_exists else None
        row = {
            "assetId": sequence.get("assetId"),
            "animSequencePath": anim_path,
            "skeletonPath": skeleton_path,
            "skeletalMeshPath": mesh_path,
            "animSequenceExists": anim_exists,
            "skeletonExists": skeleton_exists,
            "skeletalMeshExists": mesh_exists,
            "animSequenceClass": _asset_class(unreal, anim_path) if anim_exists else None,
            "skeletonClass": _asset_class(unreal, skeleton_path) if skeleton_exists else None,
            "skeletalMeshClass": _asset_class(unreal, mesh_path) if mesh_exists else None,
            "animSequenceFacts": _anim_sequence_facts(anim_asset) if anim_asset else {},
            "runtimeImported": True,
        }
        rows[anim_path] = row
        if anim_exists and skeleton_exists:
            present.append(anim_path)
        else:
            missing.append(anim_path)
    return {
        "expectedSequenceCount": len(rows),
        "presentSequenceCount": len(present),
        "missingSequenceCount": len(missing),
        "allExpectedAssetsPresent": len(rows) > 0 and not missing,
        "present": present,
        "missing": missing,
        "rows": rows,
    }


def _anim_sequence_facts(asset) -> Dict[str, Any]:
    if not asset:
        return {}
    skeleton = _safe(lambda: asset.get_editor_property("skeleton"), None)
    return {
        "class": _safe(lambda: asset.get_class().get_name(), None),
        "pathName": _safe(lambda: str(asset.get_path_name()), None),
        "skeletonPath": _asset_object_path(skeleton),
        "playLength": _safe(lambda: float(asset.get_play_length()), None),
        "numberOfFrames": _safe(lambda: int(asset.get_number_of_frames()), None),
        "numberOfSampledKeys": _safe(lambda: int(asset.get_number_of_sampled_keys()), None),
        "samplingFrameRate": str(_safe(lambda: asset.get_editor_property("sampling_frame_rate"), "")),
        "availableMethods": sorted(
            name
            for name in dir(asset)
            if "curve" in name.lower()
            or "frame" in name.lower()
            or "length" in name.lower()
            or "skeleton" in name.lower()
            or "rate" in name.lower()
        )[:80],
    }


def _asset_class(unreal, path: str | None) -> str | None:
    if not path:
        return None
    path = _package_path(path)
    asset_data = unreal.EditorAssetLibrary.find_asset_data(path)
    if not asset_data or not asset_data.is_valid():
        return None
    try:
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return str(asset_data.asset_class)


def _all_expected_targets_present(unreal, fixture: Dict[str, Any]) -> bool:
    editor_assets = unreal.EditorAssetLibrary
    rows = fixture.get("animationSequences", [])
    if not rows:
        return False
    for sequence in rows:
        if not editor_assets.does_asset_exist(sequence.get("expectedAnimSequencePath")):
            return False
        if not editor_assets.does_asset_exist(sequence.get("expectedSkeletonPath")):
            return False
    return True


def _count_present_targets(unreal, fixture: Dict[str, Any]) -> int:
    editor_assets = unreal.EditorAssetLibrary
    targets = set()
    for sequence in fixture.get("animationSequences", []):
        for key in ["expectedAnimSequencePath", "expectedSkeletonPath", "expectedSkeletalMeshPath"]:
            value = sequence.get(key)
            if value:
                targets.add(value)
    return sum(1 for target in targets if editor_assets.does_asset_exist(target))


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


def _delete_asset(editor_assets, path: str | None) -> bool:
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


def _asset_object_path(asset: Any) -> str | None:
    if not asset:
        return None
    value = _safe(lambda: str(asset.get_path_name()), None)
    if not value:
        return None
    return value.split(".")[0]


def _package_path(path: str) -> str:
    return path.split(".")[0]


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
