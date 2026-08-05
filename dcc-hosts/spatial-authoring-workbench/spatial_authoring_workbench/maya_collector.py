"""Maya runtime collector for Spatial Authoring Workbench."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .contract import build_facts_from_assets, evaluate_scene, load_fixture, public_path


L3_REPORT_VERSION = "spatial-authoring-maya-l3@0.1.0"


def build_maya_report(fixture_path: str | Path) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    fixture = load_fixture(fixture_path)
    reset_scene(cmds)
    create_scene_from_fixture(cmds, fixture)
    facts = collect_maya_scene_facts(cmds)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": L3_REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Spatial Authoring Workbench",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3",
        "l3Status": "maya_spatial_authoring_collected",
        "mayaRuntime": {
            "version": _safe(lambda: cmds.about(version=True)),
            "apiVersion": _safe(lambda: cmds.about(apiVersion=True)),
            "batch": bool(_safe(lambda: cmds.about(batch=True), False)),
        },
        "fixture": {
            "path": public_path(fixture_path),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "spatial-authoring",
            "name": "Spatial Authoring & Pose Transfer Workbench",
            "methodSource": "Lightbox socket / hotspot / locator preview / pose transfer authoring",
            "protocolCarrier": "Maya joints, locators and authoring custom attributes",
            "boundary": {
                "mutation": "synthetic_maya_spatial_fixture_only",
                "sceneWrites": "creates temporary public joints, locators and custom attrs in batch scene",
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "Maya runtime collection reads actual joint DAG names and locator transform channels from the batch scene.",
            "Socket, hotspot, pose frame and pose transfer payloads are stored as custom attributes and re-collected before evaluation.",
            "The L3 smoke creates only public synthetic authoring fixtures and does not save production scenes.",
        ],
    }


def reset_scene(cmds: Any) -> None:
    cmds.file(new=True, force=True)
    cmds.currentUnit(linear="cm")


def create_scene_from_fixture(cmds: Any, fixture: Dict[str, Any]) -> None:
    for asset in fixture.get("assets", []):
        namespace = str(asset.get("namespace", ""))
        _ensure_namespace(cmds, namespace)
        root = cmds.createNode("transform", name=_maya_name(namespace, "%s_SPATIAL" % _safe_name(asset.get("id"))))
        _set_string_attr(cmds, root, "aiToolTaSpatialAssetId", str(asset.get("id")))
        _set_string_attr(cmds, root, "aiToolTaSpatialLabel", str(asset.get("label")))
        _set_string_attr(cmds, root, "aiToolTaSpatialProtocol", str(asset.get("protocolSchema")))
        _set_string_attr(cmds, root, "aiToolTaOwnerState", str(asset.get("ownerState")))
        _set_string_attr(cmds, root, "aiToolTaExpectedSkeleton", json.dumps(asset.get("skeleton", {}), ensure_ascii=False, sort_keys=True))
        _set_string_attr(cmds, root, "aiToolTaSpatialConstraints", json.dumps(asset.get("constraints", {}), ensure_ascii=False, sort_keys=True))
        _set_string_attr(cmds, root, "aiToolTaPoseTransfer", json.dumps(asset.get("poseTransfer", {}), ensure_ascii=False, sort_keys=True))

        joints_by_name = _create_joints(cmds, namespace, root, asset.get("skeleton", {}).get("actualJoints", []))
        for socket in asset.get("sockets", []):
            _create_locator(cmds, namespace, root, joints_by_name, socket, "socket")
        for hotspot in asset.get("hotspots", []):
            _create_locator(cmds, namespace, root, joints_by_name, hotspot, "hotspot")
        for pose_frame in asset.get("poseFrames", []):
            _create_locator(cmds, namespace, root, joints_by_name, pose_frame, "poseFrame")


def collect_maya_scene_facts(cmds: Any) -> Dict[str, Any]:
    roots = [
        node
        for node in cmds.ls(type="transform") or []
        if _has_attr(cmds, node, "aiToolTaSpatialProtocol")
    ]
    assets: List[Dict[str, Any]] = []
    for root in sorted(roots):
        skeleton_info = _read_json(_get_string_attr(cmds, root, "aiToolTaExpectedSkeleton"), {})
        descendants = cmds.listRelatives(root, allDescendents=True, type="transform", fullPath=False) or []
        payload_nodes = [node for node in descendants if _has_attr(cmds, node, "aiToolTaSpatialPayload")]
        sockets: List[Dict[str, Any]] = []
        hotspots: List[Dict[str, Any]] = []
        pose_frames: List[Dict[str, Any]] = []
        for node in sorted(payload_nodes):
            payload = _read_json(_get_string_attr(cmds, node, "aiToolTaSpatialPayload"), {})
            kind = payload.get("kind")
            payload["local"] = {
                "translate": _get_triplet_attr(cmds, node, "translate"),
                "rotate": _get_triplet_attr(cmds, node, "rotate"),
                "scale": _get_triplet_attr(cmds, node, "scale"),
            }
            payload.pop("kind", None)
            if kind == "socket":
                sockets.append(payload)
            elif kind == "hotspot":
                hotspots.append(payload)
            elif kind == "poseFrame":
                pose_frames.append(payload)

        joints = [_strip_namespace(node) for node in (cmds.listRelatives(root, allDescendents=True, type="joint") or [])]
        assets.append(
            {
                "id": _get_string_attr(cmds, root, "aiToolTaSpatialAssetId"),
                "label": _get_string_attr(cmds, root, "aiToolTaSpatialLabel"),
                "namespace": _namespace(root),
                "ownerState": _get_string_attr(cmds, root, "aiToolTaOwnerState"),
                "protocolSchema": _get_string_attr(cmds, root, "aiToolTaSpatialProtocol"),
                "rootNode": root,
                "skeleton": {
                    "root": skeleton_info.get("root"),
                    "expectedJoints": skeleton_info.get("expectedJoints", []),
                    "actualJoints": sorted(joints),
                },
                "constraints": _read_json(_get_string_attr(cmds, root, "aiToolTaSpatialConstraints"), {}),
                "sockets": sockets,
                "hotspots": hotspots,
                "poseFrames": pose_frames,
                "poseTransfer": _read_json(_get_string_attr(cmds, root, "aiToolTaPoseTransfer"), {}),
            }
        )

    return build_facts_from_assets(
        scene={
            "sourceDcc": "Maya",
            "unit": "centimeter",
            "upAxis": "Y",
        },
        assets=assets,
        source_dcc="Maya",
        runtime_collected=True,
    )


def _create_joints(cmds: Any, namespace: str, root: str, joint_names: List[str]) -> Dict[str, str]:
    joints: Dict[str, str] = {}
    last_joint = None
    for index, joint_name in enumerate(joint_names):
        clean = str(joint_name)
        joint = cmds.createNode("joint", name=_maya_name(namespace, clean))
        cmds.setAttr("%s.translateY" % joint, float(index) * 0.25)
        if last_joint:
            cmds.parent(joint, last_joint)
        else:
            cmds.parent(joint, root)
        joints[clean] = joint
        last_joint = joint
    return joints


def _create_locator(
    cmds: Any,
    namespace: str,
    root: str,
    joints_by_name: Dict[str, str],
    item: Dict[str, Any],
    kind: str,
) -> str:
    suffix = "%s_%s" % (kind, item.get("frame")) if kind == "poseFrame" else kind
    node_name = _maya_name(namespace, "%s_%s_LOC" % (_safe_name(item.get("name")), suffix))
    locator = cmds.spaceLocator(name=node_name)[0]
    parent_joint = joints_by_name.get(str(item.get("parentJoint")))
    locator = cmds.parent(locator, parent_joint or root)[0]
    local = item.get("local", {})
    _set_triplet_attr(cmds, locator, "translate", local.get("translate", [0.0, 0.0, 0.0]))
    _set_triplet_attr(cmds, locator, "rotate", local.get("rotate", [0.0, 0.0, 0.0]))
    _set_triplet_attr(cmds, locator, "scale", local.get("scale", [1.0, 1.0, 1.0]))
    payload = dict(item)
    payload["kind"] = kind
    _set_string_attr(cmds, locator, "aiToolTaSpatialPayload", json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return locator


def _set_string_attr(cmds: Any, node: str, attr: str, value: str) -> None:
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType="string")
    cmds.setAttr("%s.%s" % (node, attr), value, type="string")


def _get_string_attr(cmds: Any, node: str, attr: str) -> str:
    if not _has_attr(cmds, node, attr):
        return ""
    value = cmds.getAttr("%s.%s" % (node, attr))
    return str(value) if value is not None else ""


def _has_attr(cmds: Any, node: str, attr: str) -> bool:
    try:
        return bool(cmds.attributeQuery(attr, node=node, exists=True))
    except Exception:
        return False


def _set_triplet_attr(cmds: Any, node: str, attr: str, values: Any) -> None:
    triplet = list(values or [0.0, 0.0, 0.0])
    while len(triplet) < 3:
        triplet.append(0.0)
    cmds.setAttr("%s.%s" % (node, attr), float(triplet[0]), float(triplet[1]), float(triplet[2]))


def _get_triplet_attr(cmds: Any, node: str, attr: str) -> List[float]:
    value = cmds.getAttr("%s.%s" % (node, attr))
    if isinstance(value, list):
        value = value[0]
    return [round(float(value[0]), 4), round(float(value[1]), 4), round(float(value[2]), 4)]


def _ensure_namespace(cmds: Any, namespace: str) -> None:
    if namespace and not cmds.namespace(exists=namespace):
        cmds.namespace(add=namespace)


def _maya_name(namespace: str, node: str) -> str:
    return "%s:%s" % (namespace, node) if namespace else node


def _namespace(node: str) -> str:
    return node.rsplit(":", 1)[0] if ":" in node else ""


def _strip_namespace(node: str) -> str:
    return node.rsplit(":", 1)[-1]


def _safe_name(value: Any) -> str:
    return str(value).replace("-", "_")


def _read_json(value: str, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _safe(callback: Any, default: Any = "unknown") -> Any:
    try:
        return callback()
    except Exception:
        return default
