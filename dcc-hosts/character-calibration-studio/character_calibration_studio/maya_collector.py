"""Maya runtime collector for Character Calibration Studio."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .contract import build_facts_from_characters, evaluate_scene, load_fixture, public_path


L3_REPORT_VERSION = "character-calibration-maya-l3@0.1.0"


def build_maya_report(fixture_path: str | Path) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    fixture = load_fixture(fixture_path)
    reset_scene(cmds)
    create_scene_from_fixture(cmds, fixture)
    facts = collect_maya_scene_facts(cmds)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": L3_REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Character Calibration Studio",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3",
        "l3Status": "maya_character_calibration_collected",
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
            "id": "character-calibration",
            "name": "Character Calibration & Intent Transfer Studio",
            "methodSource": "Lightbox character DNA / topology / joint coverage / Control Rig transfer",
            "protocolCarrier": "Maya mesh topology + joint DAG + calibration custom attrs",
            "boundary": {
                "mutation": "synthetic_maya_character_fixture_only",
                "sceneWrites": "creates temporary public meshes, joints and custom attrs in batch scene",
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "Maya runtime collection reads actual mesh topology and joint DAG names from the batch scene.",
            "Calibration deltas, face parameter payloads and Control Rig mappings are stored as Maya custom attributes and re-collected before evaluation.",
            "The L3 smoke creates only public synthetic character fixtures and does not save production scenes.",
        ],
    }


def reset_scene(cmds: Any) -> None:
    cmds.file(new=True, force=True)
    cmds.currentUnit(linear="cm")


def create_scene_from_fixture(cmds: Any, fixture: Dict[str, Any]) -> None:
    for character in fixture.get("characters", []):
        namespace = str(character.get("namespace", ""))
        _ensure_namespace(cmds, namespace)
        root = cmds.createNode("transform", name=_maya_name(namespace, "%s_CHAR" % _safe_name(character.get("id"))))
        _set_string_attr(cmds, root, "aiToolTaCharacterAssetId", str(character.get("id")))
        _set_string_attr(cmds, root, "aiToolTaCharacterLabel", str(character.get("label")))
        _set_string_attr(cmds, root, "aiToolTaCharacterProtocol", "character-calibration@dcc-r26")
        _set_string_attr(cmds, root, "aiToolTaOwnerState", str(character.get("ownerState")))
        _set_string_attr(cmds, root, "aiToolTaExpectedMesh", json.dumps(character.get("mesh", {}), ensure_ascii=False, sort_keys=True))
        _set_string_attr(cmds, root, "aiToolTaExpectedSkeleton", json.dumps(character.get("skeleton", {}), ensure_ascii=False, sort_keys=True))
        _set_string_attr(cmds, root, "aiToolTaSkin", json.dumps(character.get("skin", {}), ensure_ascii=False, sort_keys=True))
        _set_string_attr(cmds, root, "aiToolTaCalibration", json.dumps(character.get("calibration", {}), ensure_ascii=False, sort_keys=True))
        _set_string_attr(cmds, root, "aiToolTaFaceParams", json.dumps(character.get("faceParams", {}), ensure_ascii=False, sort_keys=True))
        _set_string_attr(cmds, root, "aiToolTaControlRig", json.dumps(character.get("controlRig", {}), ensure_ascii=False, sort_keys=True))

        mesh_info = character.get("mesh", {})
        subdivisions = mesh_info.get("subdivisions", [1, 1, 1])
        mesh, _shape = cmds.polyCube(
            name=_maya_name(namespace, str(mesh_info.get("name", "Character_GEO"))),
            subdivisionsX=int(subdivisions[0]),
            subdivisionsY=int(subdivisions[1]),
            subdivisionsZ=int(subdivisions[2]),
            width=1.0,
            height=1.3,
            depth=0.9,
        )
        cmds.parent(mesh, root)

        last_joint = None
        for index, joint_name in enumerate(character.get("skeleton", {}).get("actualJoints", [])):
            joint = cmds.createNode("joint", name=_maya_name(namespace, str(joint_name)))
            cmds.setAttr("%s.translateY" % joint, float(index) * 0.2)
            if last_joint:
                cmds.parent(joint, last_joint)
            else:
                cmds.parent(joint, root)
            last_joint = joint


def collect_maya_scene_facts(cmds: Any) -> Dict[str, Any]:
    roots = [
        node
        for node in cmds.ls(type="transform") or []
        if _has_attr(cmds, node, "aiToolTaCharacterProtocol")
    ]
    characters: List[Dict[str, Any]] = []
    for root in sorted(roots):
        mesh_info = _read_json(_get_string_attr(cmds, root, "aiToolTaExpectedMesh"), {})
        skeleton_info = _read_json(_get_string_attr(cmds, root, "aiToolTaExpectedSkeleton"), {})
        mesh_transform = _first_mesh_transform(cmds, root)
        vertex_count = int(cmds.polyEvaluate(mesh_transform, vertex=True)) if mesh_transform else 0
        edge_count = int(cmds.polyEvaluate(mesh_transform, edge=True)) if mesh_transform else 0
        face_count = int(cmds.polyEvaluate(mesh_transform, face=True)) if mesh_transform else 0
        mesh_info.update(
            {
                "actualVertexCount": vertex_count,
                "actualEdgeCount": edge_count,
                "actualFaceCount": face_count,
                "topologySignature": "topo:head:v%d:e%d:f%d" % (vertex_count, edge_count, face_count),
            }
        )
        joints = [_strip_namespace(node) for node in (cmds.listRelatives(root, allDescendents=True, type="joint") or [])]
        characters.append(
            {
                "id": _get_string_attr(cmds, root, "aiToolTaCharacterAssetId"),
                "label": _get_string_attr(cmds, root, "aiToolTaCharacterLabel"),
                "namespace": _namespace(root),
                "ownerState": _get_string_attr(cmds, root, "aiToolTaOwnerState"),
                "protocolSchema": _get_string_attr(cmds, root, "aiToolTaCharacterProtocol"),
                "mesh": mesh_info,
                "skeleton": {
                    "root": skeleton_info.get("root"),
                    "expectedJoints": skeleton_info.get("expectedJoints", []),
                    "actualJoints": sorted(joints),
                    "mirrorPairs": skeleton_info.get("mirrorPairs", []),
                },
                "skin": _read_json(_get_string_attr(cmds, root, "aiToolTaSkin"), {}),
                "calibration": _read_json(_get_string_attr(cmds, root, "aiToolTaCalibration"), {}),
                "faceParams": _read_json(_get_string_attr(cmds, root, "aiToolTaFaceParams"), {}),
                "controlRig": _read_json(_get_string_attr(cmds, root, "aiToolTaControlRig"), {}),
            }
        )

    return build_facts_from_characters(
        scene={
            "sourceDcc": "Maya",
            "unit": "centimeter",
            "upAxis": "Y",
        },
        characters=characters,
        source_dcc="Maya",
        runtime_collected=True,
    )


def _first_mesh_transform(cmds: Any, root: str) -> str | None:
    shapes = cmds.listRelatives(root, allDescendents=True, type="mesh", fullPath=False) or []
    if not shapes:
        return None
    parents = cmds.listRelatives(shapes[0], parent=True, fullPath=False) or []
    return parents[0] if parents else None


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
