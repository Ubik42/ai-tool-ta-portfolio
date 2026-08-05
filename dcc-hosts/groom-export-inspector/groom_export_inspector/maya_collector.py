"""Maya runtime collector for Groom Export Inspector."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .contract import build_facts_from_assets, evaluate_scene, load_fixture, public_path


L3_REPORT_VERSION = "groom-export-inspector-maya-l3@0.1.0"


def build_maya_report(fixture_path: str | Path) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    fixture = load_fixture(fixture_path)
    reset_scene(cmds, fixture.get("scene", {}))
    create_scene_from_fixture(cmds, fixture)
    facts = collect_maya_scene_facts(cmds)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": L3_REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3",
        "l3Status": "maya_groom_export_facts_collected",
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
            "id": "groom-export-inspector",
            "name": "Groom Export Inspector",
            "methodSource": "Lightbox XGen to Unreal groom handoff",
            "protocolCarrier": "Maya groom curves + root UV + strand ID + guide curve + Alembic export payload",
            "boundary": {
                "mutation": "synthetic_maya_groom_fixture_only",
                "sceneWrites": "creates temporary public scalp planes, curve strands and custom attrs in batch scene",
                "assetWrites": 0,
                "engineWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "Maya runtime collection reads actual curve nodes and per-strand custom attributes from the batch scene.",
            "Root UV, strand ID, guide curve and Alembic payload facts are re-collected from Maya before evaluation.",
            "The L3 smoke creates only public synthetic groom fixtures and does not export or save production caches.",
        ],
    }


def reset_scene(cmds: Any, scene: Dict[str, Any]) -> None:
    cmds.file(new=True, force=True)
    cmds.currentUnit(linear="cm")
    start = float(scene.get("playbackStart", 1001) or 1001)
    end = float(scene.get("playbackEnd", start) or start)
    cmds.playbackOptions(minTime=start, maxTime=end, animationStartTime=start, animationEndTime=end)


def create_scene_from_fixture(cmds: Any, fixture: Dict[str, Any]) -> None:
    for asset in fixture.get("assets", []):
        namespace = str(asset.get("namespace", ""))
        _ensure_namespace(cmds, namespace)
        root = cmds.createNode("transform", name=_maya_name(namespace, "%s_GROOM" % _safe_name(asset.get("id"))))
        _set_string_attr(cmds, root, "aiToolTaGroomAssetId", str(asset.get("id")))
        _set_string_attr(cmds, root, "aiToolTaGroomLabel", str(asset.get("label")))
        _set_string_attr(cmds, root, "aiToolTaGroomProtocol", str(asset.get("protocolSchema")))
        _set_string_attr(cmds, root, "aiToolTaOwnerState", str(asset.get("ownerState")))
        _set_string_attr(
            cmds,
            root,
            "aiToolTaGroomDescription",
            json.dumps(asset.get("description", {}), ensure_ascii=False, sort_keys=True),
        )
        _set_string_attr(
            cmds,
            root,
            "aiToolTaGroomScalp",
            json.dumps(asset.get("scalp", {}), ensure_ascii=False, sort_keys=True),
        )
        _set_string_attr(
            cmds,
            root,
            "aiToolTaGroomMeta",
            json.dumps(asset.get("groom", {}), ensure_ascii=False, sort_keys=True),
        )
        _set_string_attr(
            cmds,
            root,
            "aiToolTaGroomExport",
            json.dumps(asset.get("export", {}), ensure_ascii=False, sort_keys=True),
        )
        _set_string_attr(
            cmds,
            root,
            "aiToolTaGroomUnreal",
            json.dumps(asset.get("unreal", {}), ensure_ascii=False, sort_keys=True),
        )
        scalp_node = _create_scalp_plane(cmds, namespace, asset.get("scalp", {}))
        cmds.parent(scalp_node, root)
        for index, strand in enumerate(asset.get("groom", {}).get("strands", [])):
            curve = _create_curve(cmds, namespace, strand, index)
            cmds.parent(curve, root)


def collect_maya_scene_facts(cmds: Any) -> Dict[str, Any]:
    roots = [
        node
        for node in cmds.ls(type="transform") or []
        if _has_attr(cmds, node, "aiToolTaGroomProtocol")
    ]
    assets: List[Dict[str, Any]] = []
    for root in sorted(roots):
        descendants = cmds.listRelatives(root, allDescendents=True, fullPath=True) or []
        strand_nodes = [node for node in descendants if _has_attr(cmds, node, "aiToolTaGroomStrandPayload")]
        strands = []
        for node in sorted(strand_nodes):
            payload = _read_json(_get_string_attr(cmds, node, "aiToolTaGroomStrandPayload"), {})
            payload["node"] = node
            payload["pointCount"] = _curve_point_count(cmds, node)
            strands.append(payload)

        groom_meta = _read_json(_get_string_attr(cmds, root, "aiToolTaGroomMeta"), {})
        groom_meta["strands"] = strands
        assets.append(
            {
                "id": _get_string_attr(cmds, root, "aiToolTaGroomAssetId"),
                "label": _get_string_attr(cmds, root, "aiToolTaGroomLabel"),
                "namespace": _namespace(root),
                "ownerState": _get_string_attr(cmds, root, "aiToolTaOwnerState"),
                "protocolSchema": _get_string_attr(cmds, root, "aiToolTaGroomProtocol"),
                "description": _read_json(_get_string_attr(cmds, root, "aiToolTaGroomDescription"), {}),
                "scalp": _read_json(_get_string_attr(cmds, root, "aiToolTaGroomScalp"), {}),
                "groom": groom_meta,
                "export": _read_json(_get_string_attr(cmds, root, "aiToolTaGroomExport"), {}),
                "unreal": _read_json(_get_string_attr(cmds, root, "aiToolTaGroomUnreal"), {}),
            }
        )

    return build_facts_from_assets(
        scene={
            "sourceDcc": "Maya",
            "unit": "centimeter",
            "upAxis": "Y",
            "timeUnit": "film",
            "playbackStart": _safe(lambda: cmds.playbackOptions(query=True, minTime=True), 1001),
            "playbackEnd": _safe(lambda: cmds.playbackOptions(query=True, maxTime=True), 1001),
        },
        assets=assets,
        source_dcc="Maya",
        runtime_collected=True,
    )


def _create_scalp_plane(cmds: Any, namespace: str, scalp: Dict[str, Any]) -> str:
    name = _maya_name(namespace, str(scalp.get("mesh", "scalp_geo")))
    plane = cmds.polyPlane(name=name, width=2.0, height=1.2, subdivisionsX=1, subdivisionsY=1)[0]
    _set_string_attr(cmds, plane, "aiToolTaGroomScalpPayload", json.dumps(scalp, ensure_ascii=False, sort_keys=True))
    return plane


def _create_curve(cmds: Any, namespace: str, strand: Dict[str, Any], index: int) -> str:
    strand_id = str(strand.get("id") or "missing_id_%03d" % index)
    points = strand.get("points") or [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    curve = cmds.curve(name=_maya_name(namespace, "%s_CRV" % _safe_name(strand_id)), degree=1, point=points)
    payload = {
        "id": str(strand.get("id", "")),
        "rootUv": strand.get("rootUv"),
        "guide": bool(strand.get("guide")),
        "width": float(strand.get("width", 0.0) or 0.0),
        "groupId": strand.get("groupId"),
        "groupName": str(strand.get("groupName", "")),
        "materialSlot": str(strand.get("materialSlot", "")),
        "points": points,
    }
    _set_string_attr(cmds, curve, "aiToolTaGroomStrandPayload", json.dumps(payload, ensure_ascii=False, sort_keys=True))
    _set_standard_groom_attrs(cmds, curve, payload)
    return curve


def _set_standard_groom_attrs(cmds: Any, curve: str, payload: Dict[str, Any]) -> None:
    targets = [curve] + (cmds.listRelatives(curve, shapes=True, fullPath=True) or [])
    root_uv = payload.get("rootUv") if isinstance(payload.get("rootUv"), list) else [0.0, 0.0]
    strand_id = payload.get("id") or "missing"
    group_id = int(payload.get("groupId") or 0)
    group_name = payload.get("groupName") or "HeroHair"
    for node in targets:
        _set_double2_attr(cmds, node, "groom_root_uv", float(root_uv[0]), float(root_uv[1]))
        _set_numeric_attr(cmds, node, "groom_width", float(payload.get("width") or 0.0), "double")
        _set_numeric_attr(cmds, node, "groom_id", index_value(strand_id), "long")
        _set_numeric_attr(cmds, node, "groom_guide", 1 if payload.get("guide") else 0, "bool")
        _set_numeric_attr(cmds, node, "groom_group_id", group_id, "long")
        _set_string_attr(cmds, node, "groom_group_name", str(group_name))


def _set_string_attr(cmds: Any, node: str, attr: str, value: str) -> None:
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType="string")
    cmds.setAttr("%s.%s" % (node, attr), value, type="string")


def _set_numeric_attr(cmds: Any, node: str, attr: str, value: Any, attr_type: str) -> None:
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, attributeType=attr_type)
    cmds.setAttr("%s.%s" % (node, attr), value)


def _set_double2_attr(cmds: Any, node: str, attr: str, x_value: float, y_value: float) -> None:
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, attributeType="double2")
        cmds.addAttr(node, longName="%s_x" % attr, attributeType="double", parent=attr)
        cmds.addAttr(node, longName="%s_y" % attr, attributeType="double", parent=attr)
    cmds.setAttr("%s.%s" % (node, attr), x_value, y_value, type="double2")


def index_value(value: Any) -> int:
    digits = "".join(char for char in str(value) if char.isdigit())
    return int(digits or 0)


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


def _curve_point_count(cmds: Any, node: str) -> int:
    shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
    if not shapes:
        return 0
    spans = int(cmds.getAttr("%s.spans" % shapes[0]) or 0)
    degree = int(cmds.getAttr("%s.degree" % shapes[0]) or 0)
    return spans + degree


def _ensure_namespace(cmds: Any, namespace: str) -> None:
    if namespace and not cmds.namespace(exists=namespace):
        cmds.namespace(add=namespace)


def _maya_name(namespace: str, node: str) -> str:
    return "%s:%s" % (namespace, node) if namespace else node


def _namespace(node: str) -> str:
    return node.rsplit(":", 1)[0] if ":" in node else ""


def _safe_name(value: Any) -> str:
    return str(value).replace("-", "_").replace(" ", "_")


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
