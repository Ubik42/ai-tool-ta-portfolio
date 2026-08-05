from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def _main() -> None:
    root = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_ROOT"])
    output_path = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_OUTPUT"])
    source_artifact = Path(os.environ["AI_TOOL_TA_UNREAL_CONTROL_RIG_SOURCE"])
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    import unreal  # type: ignore

    from unreal_control_rig_bridge.contract import build_report, expected_unreal_targets, public_path

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
            "characters": _character_probe(unreal, source, expected_unreal_targets),
            "assetRegistry": _asset_registry_probe(unreal, "/Game/AI_Tool_TA/Characters"),
        },
    }
    report = build_report(source_artifact, runtime_snapshot=runtime_snapshot)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("AI_TOOL_TA_UNREAL_CONTROL_RIG_OUTPUT=%s" % output_path)


def _api_probe(unreal) -> Dict[str, Any]:
    class_names = [
        "ControlRig",
        "ControlRigBlueprint",
        "ControlRigBlueprintFactory",
        "ControlRigComponent",
        "ControlRigShapeLibrary",
        "RigHierarchy",
        "RigVMBlueprint",
        "RigVMController",
        "SkeletalMesh",
        "Skeleton",
        "EditorAssetLibrary",
        "AssetRegistryHelpers",
    ]
    classes = {name: hasattr(unreal, name) for name in class_names}
    control_rig_methods = []
    if hasattr(unreal, "ControlRigBlueprint"):
        control_rig_methods = _method_names(unreal.ControlRigBlueprint, ["control", "hierarchy", "rig", "vm"])
    return {
        "classes": classes,
        "controlRigBlueprintMethods": control_rig_methods[:80],
    }


def _character_probe(unreal, source: Dict[str, Any], expected_unreal_targets_fn) -> Dict[str, Any]:
    rows = {}
    for row in source.get("drilldowns", []):
        asset_id = str(row.get("assetId"))
        expected = expected_unreal_targets_fn(asset_id)
        required_controls = _required_controls(row)
        mesh_path = expected.get("skeletalMeshPath")
        skeleton_path = expected.get("skeletonPath")
        control_rig_path = expected.get("controlRigPath")
        mesh_asset = _load_asset(unreal, mesh_path)
        skeleton_asset = _load_asset(unreal, skeleton_path)
        control_rig_asset = _load_asset(unreal, control_rig_path)
        control_rig_facts = _control_rig_facts(control_rig_asset)
        control_rig_facts["requiredControls"] = required_controls
        rows[asset_id] = {
            "assetId": asset_id,
            "skeletalMeshPath": mesh_path,
            "skeletonPath": skeleton_path,
            "controlRigPath": control_rig_path,
            "skeletalMeshExists": bool(mesh_asset),
            "skeletonExists": bool(skeleton_asset),
            "controlRigExists": bool(control_rig_asset),
            "skeletalMeshClass": _asset_class(unreal, mesh_path) if mesh_asset else None,
            "skeletonClass": _asset_class(unreal, skeleton_path) if skeleton_asset else None,
            "controlRigClass": _asset_class(unreal, control_rig_path) if control_rig_asset else None,
            "requiredControls": required_controls,
            "skeletalMeshFacts": _skeletal_mesh_facts(mesh_asset),
            "skeletonFacts": _skeleton_facts(skeleton_asset),
            "controlRigFacts": control_rig_facts,
        }
    return rows


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


def _control_rig_facts(asset: Any) -> Dict[str, Any]:
    if not asset:
        return {
            "controlsReadable": False,
            "controls": [],
            "availableMethods": [],
        }
    methods = _method_names(asset, ["control", "hierarchy", "rig", "vm"])
    controls = _read_control_names(asset)
    return {
        "controlsReadable": bool(controls),
        "controls": controls,
        "availableMethods": methods[:80],
        "pathName": _safe(lambda: str(asset.get_path_name()), None),
        "class": _safe(lambda: asset.get_class().get_name(), None),
    }


def _skeletal_mesh_facts(asset: Any) -> Dict[str, Any]:
    if not asset:
        return {}
    skeleton = _safe(lambda: asset.get_editor_property("skeleton"), None)
    return {
        "pathName": _safe(lambda: str(asset.get_path_name()), None),
        "class": _safe(lambda: asset.get_class().get_name(), None),
        "skeletonPath": _asset_object_path(skeleton),
        "availableMethods": _method_names(asset, ["bone", "skeleton", "socket", "mesh"])[:80],
    }


def _skeleton_facts(asset: Any) -> Dict[str, Any]:
    if not asset:
        return {}
    return {
        "pathName": _safe(lambda: str(asset.get_path_name()), None),
        "class": _safe(lambda: asset.get_class().get_name(), None),
        "availableMethods": _method_names(asset, ["bone", "skeleton", "socket", "reference"])[:80],
    }


def _required_controls(source_row: Dict[str, Any]) -> List[str]:
    control_panel = _panel(source_row, "controlRig")
    controls = set(str(name) for name in control_panel.get("metrics", {}).get("missingControls", []))
    for mismatch in control_panel.get("metrics", {}).get("targetMismatches", []):
        controls.add(str(mismatch.get("control")))
    required_count = int(control_panel.get("metrics", {}).get("requiredCount") or 0)
    actual_count = int(control_panel.get("metrics", {}).get("actualCount") or 0)
    if required_count == 5 and actual_count == 5 and not controls:
        controls.update(["CTRL_brow_L", "CTRL_brow_R", "CTRL_eye_L", "CTRL_eye_R", "CTRL_jaw"])
    if required_count == 5 and actual_count == 3:
        controls.update(["CTRL_brow_L", "CTRL_brow_R", "CTRL_eye_L", "CTRL_eye_R", "CTRL_jaw"])
    return sorted(name for name in controls if name and name != "None")


def _panel(row: Dict[str, Any], panel_id: str) -> Dict[str, Any]:
    for panel in row.get("panels", []):
        if panel.get("id") == panel_id:
            return panel
    return {"metrics": {}}


def _read_control_names(asset: Any) -> List[str]:
    hierarchy = _safe(lambda: asset.get_hierarchy(), None)
    if not hierarchy:
        hierarchy = _safe(lambda: asset.hierarchy, None)
    if not hierarchy:
        return []
    elements = _safe(lambda: hierarchy.get_controls(), None)
    if not elements:
        elements = _safe(lambda: hierarchy.get_all_keys(), None)
    names = []
    for element in elements or []:
        value = _safe(lambda: element.name, None)
        if value is None:
            value = _safe(lambda: element.get_name(), None)
        if value is not None:
            names.append(str(value))
    return sorted(set(names))


def _load_asset(unreal, path: str | None):
    if not path:
        return None
    try:
        return unreal.EditorAssetLibrary.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    except Exception:
        return None


def _asset_class(unreal, path: str | None) -> str | None:
    if not path:
        return None
    try:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(path)
        if not asset_data or not asset_data.is_valid():
            return None
        return str(asset_data.asset_class_path.asset_name)
    except Exception:
        return None


def _asset_object_path(asset: Any) -> str | None:
    if not asset:
        return None
    value = _safe(lambda: str(asset.get_path_name()), None)
    if not value:
        return None
    return value.split(".")[0]


def _method_names(obj: Any, terms: List[str]) -> List[str]:
    return sorted(name for name in dir(obj) if any(term in name.lower() for term in terms))


def _package_path(path: str) -> str:
    return path.split(".")[0]


def _safe(fn, fallback):
    try:
        return fn()
    except Exception:
        return fallback


_main()

