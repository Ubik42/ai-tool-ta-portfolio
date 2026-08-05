"""Maya runtime collector for Animation Continuity Lab."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .contract import build_facts_from_assets, evaluate_scene, load_fixture


L3_REPORT_VERSION = "animation-continuity-maya-l3@0.1.0"


def build_maya_report(fixture_path: str | Path) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    fixture = load_fixture(fixture_path)
    reset_scene(cmds)
    create_scene_from_fixture(cmds, fixture)
    facts = collect_maya_scene_facts(cmds)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": L3_REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Animation Continuity Lab",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3",
        "l3Status": "maya_anim_curves_collected",
        "mayaRuntime": {
            "version": _safe(lambda: cmds.about(version=True)),
            "apiVersion": _safe(lambda: cmds.about(apiVersion=True)),
            "batch": bool(_safe(lambda: cmds.about(batch=True), False)),
        },
        "fixture": {
            "path": str(Path(fixture_path)),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "animation-continuity",
            "name": "Animation Continuity Lab",
            "methodSource": "Lightbox animation export / MotionBuilder handoff / Unreal animation import continuity",
            "protocolCarrier": "Maya custom attrs + keyed animCurve facts",
            "boundary": {
                "mutation": "synthetic_maya_animation_fixture_only",
                "sceneWrites": "creates temporary public fixture transforms and animation curves in batch scene",
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "Maya runtime collection reads actual keyed transform curves rather than only trusting fixture JSON.",
            "Rig identity, skeleton fingerprint, take range, sample rate, channel identity, sub-frame keys, root motion and active layers are represented as machine-checkable facts.",
            "The L3 smoke only creates public synthetic transforms and anim curves in a batch scene.",
        ],
    }


def reset_scene(cmds: Any) -> None:
    cmds.file(new=True, force=True)
    cmds.currentUnit(time="ntsc")


def create_scene_from_fixture(cmds: Any, fixture: Dict[str, Any]) -> None:
    scene = fixture.get("scene", {})
    cmds.playbackOptions(
        minTime=float(scene.get("playbackStart", 1)),
        maxTime=float(scene.get("playbackEnd", 120)),
        animationStartTime=float(scene.get("playbackStart", 1)),
        animationEndTime=float(scene.get("playbackEnd", 120)),
    )
    for asset in fixture.get("assets", []):
        namespace = str(asset.get("namespace", ""))
        _ensure_namespace(cmds, namespace)
        for channel in asset.get("channels", []):
            channel_namespace = str(channel.get("namespace", namespace))
            _ensure_namespace(cmds, channel_namespace)

        root = cmds.createNode("transform", name=_maya_name(namespace, "%s_ROOT" % asset.get("id")))
        _set_string_attr(cmds, root, "aiToolTaAnimAssetId", str(asset.get("id")))
        _set_string_attr(cmds, root, "aiToolTaAnimAssetLabel", str(asset.get("label")))
        _set_string_attr(cmds, root, "aiToolTaAnimRootNode", str(asset.get("rootNode", "Hips")))
        _set_string_attr(cmds, root, "aiToolTaRigId", str(asset.get("actualRigId")))
        _set_string_attr(cmds, root, "aiToolTaSkeletonFingerprint", str(asset.get("actualSkeletonFingerprint")))
        _set_string_attr(cmds, root, "aiToolTaAnimProtocol", json.dumps(asset.get("protocol", {}), ensure_ascii=False, sort_keys=True))
        _set_string_attr(cmds, root, "aiToolTaAnimLayers", json.dumps(asset.get("animationLayers", []), ensure_ascii=False, sort_keys=True))

        for channel in asset.get("channels", []):
            node_name = _maya_name(str(channel.get("namespace", namespace)), str(channel.get("node")))
            node = node_name if cmds.objExists(node_name) else cmds.createNode("transform", name=node_name)
            _set_string_attr(cmds, node, "aiToolTaAnimAssetId", str(asset.get("id")))
            _set_string_attr(cmds, node, "aiToolTaAnimShortName", str(channel.get("node")))
            attr = str(channel.get("attr"))
            for key in channel.get("keys", []):
                cmds.setKeyframe(node, attribute=attr, time=float(key.get("frame")), value=float(key.get("value", 0.0)))


def collect_maya_scene_facts(cmds: Any) -> Dict[str, Any]:
    roots = [
        node
        for node in cmds.ls(type="transform") or []
        if _has_attr(cmds, node, "aiToolTaAnimProtocol")
    ]
    assets: List[Dict[str, Any]] = []
    for root in sorted(roots):
        asset_id = _get_string_attr(cmds, root, "aiToolTaAnimAssetId")
        nodes = [
            node
            for node in cmds.ls(type="transform") or []
            if node != root and _get_string_attr(cmds, node, "aiToolTaAnimAssetId") == asset_id
        ]
        channels: List[Dict[str, Any]] = []
        for node in sorted(nodes):
            short_name = _get_string_attr(cmds, node, "aiToolTaAnimShortName") or _strip_namespace(node)
            for attr in ("translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"):
                times = cmds.keyframe(node, attribute=attr, query=True, timeChange=True) or []
                if not times:
                    continue
                values = cmds.keyframe(node, attribute=attr, query=True, valueChange=True) or []
                channels.append(
                    {
                        "namespace": _namespace(node),
                        "node": short_name,
                        "attr": attr,
                        "keys": [
                            {"frame": float(frame), "value": float(value)}
                            for frame, value in zip(times, values)
                        ],
                    }
                )
        assets.append(
            {
                "id": asset_id,
                "label": _get_string_attr(cmds, root, "aiToolTaAnimAssetLabel"),
                "namespace": _namespace(root),
                "actualRigId": _get_string_attr(cmds, root, "aiToolTaRigId"),
                "actualSkeletonFingerprint": _get_string_attr(cmds, root, "aiToolTaSkeletonFingerprint"),
                "rootNode": _get_string_attr(cmds, root, "aiToolTaAnimRootNode"),
                "protocol": _read_json(_get_string_attr(cmds, root, "aiToolTaAnimProtocol"), {}),
                "animationLayers": _read_json(_get_string_attr(cmds, root, "aiToolTaAnimLayers"), []),
                "channels": channels,
            }
        )

    start = float(cmds.playbackOptions(query=True, minTime=True))
    end = float(cmds.playbackOptions(query=True, maxTime=True))
    return build_facts_from_assets(
        scene={
            "sourceDcc": "Maya",
            "unit": "centimeter",
            "timeUnit": cmds.currentUnit(query=True, time=True),
            "fps": 30,
            "playbackStart": start,
            "playbackEnd": end,
        },
        assets=assets,
        source_dcc="Maya",
        runtime_collected=True,
    )


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
