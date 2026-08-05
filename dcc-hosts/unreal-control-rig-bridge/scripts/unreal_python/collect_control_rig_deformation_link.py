from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_DEFORMATION_OUTPUT"])
    bridge_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_DEFORMATION_SOURCE"])
    fixture_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_FIXTURE_AUTHORING_SOURCE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_control_rig_bridge.deformation_link import build_deformation_link_report, public_path, resolve_public_path

    bridge = json.loads(bridge_artifact.read_text(encoding="utf-8"))
    source_l3 = _load_source_l3(bridge, resolve_public_path)
    characters = _character_rows(unreal, bridge, source_l3)
    runtime_snapshot = {
        "runtime": {
            "executed": True,
            "runtime": "Unreal Python",
            "engineVersion": _safe(lambda: unreal.SystemLibrary.get_engine_version(), "unknown"),
            "pythonVersion": sys.version,
            "projectPath": public_path(os.environ.get("AI_TOOL_TA_UNREAL_PROJECT", "")),
            "unrealCli": os.environ.get("AI_TOOL_TA_UNREAL_CLI"),
            "api": _api_probe(unreal),
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "read-only /Game/AI_Tool_TA Control Rig deformation link probe",
        },
        "characters": characters,
    }
    report = build_deformation_link_report(bridge_artifact, fixture_artifact, runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_CONTROL_RIG_DEFORMATION_OUTPUT=%s" % output_path)


def _load_source_l3(bridge: Dict[str, Any], resolve_public_path_fn) -> Dict[str, Any]:
    drilldown_path = bridge.get("sourceArtifact", {}).get("path")
    if not drilldown_path:
        return {}
    drilldown_resolved = resolve_public_path_fn(drilldown_path)
    if not drilldown_resolved.exists():
        return {}
    drilldown = json.loads(drilldown_resolved.read_text(encoding="utf-8"))
    l3_path = drilldown.get("sourceArtifact", {}).get("path")
    if not l3_path:
        return {}
    l3_resolved = resolve_public_path_fn(l3_path)
    if not l3_resolved.exists():
        return {}
    return json.loads(l3_resolved.read_text(encoding="utf-8"))


def _character_rows(unreal, bridge: Dict[str, Any], source_l3: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    source_l3_by_id = {str(row.get("assetId")): row for row in source_l3.get("facts", {}).get("characters", [])}
    for row in bridge.get("facts", {}).get("characters", []):
        asset_id = str(row.get("assetId"))
        expected = row.get("expectedUnreal", {})
        runtime = row.get("runtime", {})
        source_raw = source_l3_by_id.get(asset_id, {}).get("raw", {})
        mappings = _source_mappings(row, source_raw)
        required_controls = sorted(set(row.get("normalized", {}).get("runtime.requiredControls") or mappings.keys()))
        control_rig_path = str(expected.get("controlRigPath") or runtime.get("controlRigPath") or "")
        skeleton_path = str(expected.get("skeletonPath") or runtime.get("skeletonPath") or "")
        skeletal_mesh_path = str(expected.get("skeletalMeshPath") or runtime.get("skeletalMeshPath") or "")
        control_rig = _load_asset(unreal, control_rig_path)
        skeleton = _load_asset(unreal, skeleton_path)
        skeletal_mesh = _load_asset(unreal, skeletal_mesh_path)
        hierarchy = _control_rig_hierarchy(control_rig)
        hierarchy_keys = _hierarchy_keys(hierarchy)
        runtime_controls = _control_names(hierarchy, hierarchy_keys)
        skeleton_bones, skeleton_bone_probe = _skeleton_bone_names(skeleton)
        control_details = {
            control: _control_detail(unreal, hierarchy, control)
            for control in required_controls
        }
        control_links = [
            _control_link_row(
                control,
                mappings.get(control),
                runtime_controls,
                skeleton_bones,
                skeleton_bone_probe,
                control_details.get(control, {}),
            )
            for control in required_controls
        ]
        return_row = {
            "assetId": asset_id,
            "assetLabel": row.get("assetLabel"),
            "sourceStatus": row.get("sourceStatus"),
            "sourceControlRigPanelStatus": row.get("sourceControlRig", {}).get("panelStatus"),
            "sourceSkeletonPanelStatus": row.get("sourceSkeleton", {}).get("panelStatus"),
            "sourceMissingJoints": row.get("sourceSkeleton", {}).get("missing", []),
            "sourceTemporaryJoints": row.get("sourceSkeleton", {}).get("temporary", []),
            "sourceTargetMismatches": row.get("sourceControlRig", {}).get("targetMismatches", []),
            "sourceUnresolvedTargets": row.get("sourceControlRig", {}).get("unresolvedTargets", []),
            "sourceExpectedJoints": source_raw.get("expectedJoints", []),
            "sourceActualJoints": source_raw.get("actualJoints", []),
            "sourceMappings": mappings,
            "expectedUnreal": expected,
            "skeletalMeshPath": skeletal_mesh_path,
            "skeletalMeshExists": bool(skeletal_mesh),
            "skeletonPath": skeleton_path,
            "skeletonExists": bool(skeleton),
            "skeletonClass": _asset_class(unreal, skeleton_path) if skeleton else None,
            "skeletonBoneNamesReadable": skeleton_bone_probe.get("readable"),
            "skeletonBoneNames": skeleton_bones,
            "skeletonBoneProbe": skeleton_bone_probe,
            "controlRigPath": control_rig_path,
            "controlRigExists": bool(control_rig),
            "controlRigClass": _asset_class(unreal, control_rig_path) if control_rig else None,
            "requiredControls": required_controls,
            "hierarchyReadable": bool(hierarchy),
            "hierarchyKeyCount": len(hierarchy_keys),
            "hierarchyKeys": hierarchy_keys[:80],
            "runtimeControls": runtime_controls,
            "missingControls": sorted(name for name in required_controls if name not in set(runtime_controls)),
            "controlLinks": control_links,
            "compileProbe": _compile_probe(control_rig),
        }
        rows.append(return_row)
    return rows


def _source_mappings(bridge_row: Dict[str, Any], source_raw: Dict[str, Any]) -> Dict[str, str]:
    mappings = {str(control): str(target) for control, target in source_raw.get("controlRigMappings", {}).items()}
    for mismatch in bridge_row.get("sourceControlRig", {}).get("targetMismatches", []):
        control = mismatch.get("control")
        expected = mismatch.get("expected")
        if control and expected:
            mappings[str(control)] = str(expected)
    for missing in bridge_row.get("sourceControlRig", {}).get("missingControls", []):
        mappings.setdefault(str(missing), "")
    return mappings


def _control_link_row(
    control: str,
    deformation_target: Optional[str],
    runtime_controls: List[str],
    skeleton_bones: List[str],
    skeleton_probe: Dict[str, Any],
    detail: Dict[str, Any],
) -> Dict[str, Any]:
    runtime_exists = control in set(runtime_controls)
    target_status: Any = "unknown"
    if skeleton_probe.get("readable"):
        target_status = bool(deformation_target and deformation_target in set(skeleton_bones))
    shape_readable = any(call.get("ok") for call in detail.get("shapeCalls", []))
    offset_readable = any(call.get("ok") for call in detail.get("offsetCalls", []))
    return {
        "control": control,
        "deformationTarget": deformation_target,
        "runtimeControlExists": runtime_exists,
        "targetInUnrealSkeleton": target_status,
        "shapeReadable": shape_readable,
        "offsetReadable": offset_readable,
        "valueReadable": any(call.get("ok") for call in detail.get("valueCalls", [])),
        "detail": detail,
    }


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "ControlRig",
        "ControlRigBlueprint",
        "RigElementKey",
        "RigElementType",
        "RigHierarchy",
        "Skeleton",
        "SkeletalMesh",
        "EditorAssetLibrary",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    return {
        "classes": classes,
        "controlRigBlueprintMethods": _method_names(unreal.ControlRigBlueprint, ["compile", "control", "hierarchy", "rig", "vm"])[:100]
        if hasattr(unreal, "ControlRigBlueprint")
        else [],
        "rigHierarchyMethods": _method_names(unreal.RigHierarchy, ["control", "shape", "offset", "transform", "value", "key"])[:120]
        if hasattr(unreal, "RigHierarchy")
        else [],
        "skeletonMethods": _method_names(unreal.Skeleton, ["bone", "reference", "skeleton", "pose"])[:80]
        if hasattr(unreal, "Skeleton")
        else [],
    }


def _control_rig_hierarchy(asset: Any) -> Any:
    if not asset:
        return None
    hierarchy = _safe(lambda: asset.get_hierarchy(), None)
    if not hierarchy:
        hierarchy = _safe(lambda: asset.hierarchy, None)
    return hierarchy


def _hierarchy_keys(hierarchy: Any) -> List[Dict[str, Any]]:
    if not hierarchy:
        return []
    raw_keys = _safe(lambda: hierarchy.get_all_keys(), None)
    if raw_keys is None:
        raw_keys = _safe(lambda: hierarchy.get_controls(), None)
    rows = []
    for key in raw_keys or []:
        rows.append({"name": _key_name(key), "type": _key_type(key), "repr": str(key)})
    return rows


def _control_names(hierarchy: Any, keys: List[Dict[str, Any]]) -> List[str]:
    names = []
    controls = _safe(lambda: hierarchy.get_controls(), None) if hierarchy else None
    for control in controls or []:
        names.append(_key_name(control))
    for key in keys:
        if "control" in str(key.get("type", "")).lower():
            names.append(str(key.get("name")))
    return sorted({name for name in names if name and name != "None"})


def _control_detail(unreal, hierarchy: Any, control: str) -> Dict[str, Any]:
    if not hierarchy:
        return {"control": control, "key": None, "valueCalls": [], "shapeCalls": [], "offsetCalls": [], "metadataCalls": []}
    key = _rig_control_key(unreal, control)
    value_calls = _call_variants(hierarchy, "get_control_value", [(key,), (control,)]) + _call_variants(
        hierarchy, "get_control_value_by_index", [(_control_index(hierarchy, control),)]
    )
    shape_calls = []
    for method_name in ("get_local_control_shape_transform", "get_global_control_shape_transform"):
        shape_calls.extend(_call_variants(hierarchy, method_name, [(key,), (control,)]))
    for method_name in ("get_local_control_shape_transform_by_index", "get_global_control_shape_transform_by_index"):
        shape_calls.extend(_call_variants(hierarchy, method_name, [(_control_index(hierarchy, control),)]))
    offset_calls = []
    for method_name in ("get_global_control_offset_transform",):
        offset_calls.extend(_call_variants(hierarchy, method_name, [(key,), (control,)]))
    offset_calls.extend(_call_variants(hierarchy, "get_global_control_offset_transform_by_index", [(_control_index(hierarchy, control),)]))
    metadata_calls = _call_variants(hierarchy, "get_rig_element_key_metadata", [(key, "aiToolTA"), (key, "")])
    return {
        "control": control,
        "key": str(key) if key else None,
        "valueCalls": value_calls,
        "shapeCalls": shape_calls,
        "offsetCalls": offset_calls,
        "metadataCalls": metadata_calls,
    }


def _rig_control_key(unreal, control: str) -> Any:
    if not hasattr(unreal, "RigElementKey") or not hasattr(unreal, "RigElementType"):
        return None
    control_type = getattr(unreal.RigElementType, "CONTROL", None)
    candidates = [
        (control, control_type),
        (control_type, control),
        (),
    ]
    for args in candidates:
        try:
            key = unreal.RigElementKey(*args)
            if args == ():
                _safe(lambda: key.set_editor_property("name", control), None)
                _safe(lambda: key.set_editor_property("type", control_type), None)
            if control in str(key):
                return key
        except Exception:
            continue
    return None


def _control_index(hierarchy: Any, control: str) -> int:
    controls = _safe(lambda: hierarchy.get_controls(), None) if hierarchy else None
    for index, key in enumerate(controls or []):
        if _key_name(key) == control:
            return index
    return -1


def _call_variants(obj: Any, method_name: str, arg_variants: List[tuple]) -> List[Dict[str, Any]]:
    method = getattr(obj, method_name, None)
    if not method:
        return []
    rows = []
    for args in arg_variants:
        if any(arg is None or arg == -1 for arg in args):
            continue
        row = {"method": method_name, "args": [str(arg) for arg in args], "ok": False, "value": None, "error": None}
        try:
            value = method(*args)
            row["ok"] = True
            row["value"] = _short_repr(value)
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)
        if row["ok"]:
            break
    return rows


def _compile_probe(asset: Any) -> Dict[str, Any]:
    if not asset:
        return {
            "compileApiVisible": False,
            "directCompileStatusReadable": False,
            "directCompileStatus": None,
            "compileMethods": [],
            "classRows": [],
            "settingsRows": [],
        }
    methods = _method_names(asset, ["compile", "recompile", "vm", "rig"])
    class_rows = []
    for method_name in ("get_control_rig_class", "get_rig_vm_host_class"):
        class_rows.extend(_call_variants(asset, method_name, [()]))
    settings_rows = []
    for attr in ("vm_compile_settings", "compile_status", "last_compile_status", "status"):
        settings_rows.append({"attribute": attr, "ok": False, "value": None, "error": None})
        try:
            value = asset.get_editor_property(attr)
            settings_rows[-1]["ok"] = True
            settings_rows[-1]["value"] = _short_repr(value)
        except Exception as exc:
            settings_rows[-1]["error"] = str(exc)
    direct_rows = [row for row in settings_rows if row["ok"] and "status" in row["attribute"]]
    return {
        "compileApiVisible": any("compile" in name.lower() or "vm" in name.lower() for name in methods),
        "directCompileStatusReadable": bool(direct_rows),
        "directCompileStatus": direct_rows[0]["value"] if direct_rows else None,
        "compileMethods": methods[:100],
        "classRows": class_rows,
        "settingsRows": settings_rows,
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

    for count_method, name_method in (
        ("get_num_bones", "get_bone_name"),
        ("get_bone_count", "get_bone_name"),
        ("num_bones", "get_bone_name"),
    ):
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

    rows = []
    try:
        iterator = iter(pose)
    except Exception:
        iterator = iter([])
    for item in iterator:
        name = _safe(lambda: item.name, None)
        if name is None:
            name = _safe(lambda: item.get_editor_property("name"), None)
        if name is None:
            name = _safe(lambda: item.bone_name, None)
        if name is None:
            text = str(item)
            marker = "name="
            if marker in text:
                name = text.split(marker, 1)[1].split(",", 1)[0].strip("'\"{} ")
        if name is not None:
            rows.append(str(name))
    return rows


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


def _key_name(key: Any) -> Optional[str]:
    value = _safe(lambda: key.name, None)
    if value is None:
        value = _safe(lambda: key.get_editor_property("name"), None)
    if value is None:
        value = _safe(lambda: key.get_name(), None)
    return str(value) if value is not None else None


def _key_type(key: Any) -> Optional[str]:
    value = _safe(lambda: key.type, None)
    if value is None:
        value = _safe(lambda: key.get_editor_property("type"), None)
    return str(value) if value is not None else None


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    if not obj:
        return []
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _short_repr(value: Any) -> str:
    text = str(value)
    return text if len(text) <= 240 else text[:237] + "..."


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()
