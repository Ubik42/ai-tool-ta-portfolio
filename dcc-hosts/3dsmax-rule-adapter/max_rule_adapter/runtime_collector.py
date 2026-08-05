"""3ds Max pymxs collector for the Cross-DCC rule adapter.

The functions in this module are imported by 3ds Max Python through
3dsmaxbatch.exe. Normal Python can compile this file because pymxs is imported
inside runtime functions only.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List

from .contract import NORMALIZED_SCHEMA, evaluate_scene, load_fixture


L3_REPORT_VERSION = "max-rule-adapter-pymxs-l3@0.1.0"


def build_pymxs_report(fixture_path: str | Path) -> Dict[str, Any]:
    from pymxs import runtime as mxs  # type: ignore

    fixture = load_fixture(fixture_path)
    reset_scene(mxs)
    create_scene_from_fixture(mxs, fixture)
    facts = collect_pymxs_scene_facts(mxs, fixture)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": L3_REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / 3ds Max Rule Adapter",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3",
        "l3Status": "pymxs_scene_collected",
        "maxRuntime": {
            "runner": "3dsmaxbatch.exe",
            "version": _safe_str(lambda: mxs.maxVersion()),
        },
        "fixture": {
            "path": str(Path(fixture_path)),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "3dsmax",
            "name": "3ds Max Rule Adapter",
            "methodSource": "max_rule_adapter_reference / max_scene_rule_reference / Cross-DCC Rule Matrix",
            "protocolCarrier": "pymxs user properties + layers + materials + map channels",
            "boundary": {
                "mutation": "synthetic_3dsmax_fixture_only",
                "sceneWrites": "creates temporary public fixture nodes in the batch scene",
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "3ds Max adapter can collect pymxs scene nodes into the same Cross-DCC rule input used by Maya and Blender evidence.",
            "User properties, layer/export root, LOD suffixes, material assignment, UV channel declarations and collision proxies are represented as runtime facts.",
            "The L3 smoke only creates public synthetic fixture nodes and performs no production asset writes.",
        ],
    }


def reset_scene(mxs: Any) -> None:
    mxs.resetMaxFile(mxs.Name("noPrompt"))


def create_scene_from_fixture(mxs: Any, fixture: Dict[str, Any]) -> None:
    for asset in fixture.get("assets", []):
        for node_payload in asset.get("nodes", []):
            node = mxs.Box(name=str(node_payload.get("name")), length=10, width=10, height=10)
            mxs.setUserProp(node, "aiToolTaAssetId", str(asset.get("id")))
            mxs.setUserProp(node, "aiToolTaAssetLabel", str(asset.get("label")))
            mxs.setUserProp(node, "aiToolTaRole", str(node_payload.get("role", "render")))
            mxs.setUserProp(node, "aiToolTaExportRoot", str(asset.get("exportRoot")))
            mxs.setUserProp(node, "aiToolTaLayer", str(asset.get("layer")))
            mxs.setUserProp(
                node,
                "aiToolTaProtocol",
                json.dumps(asset.get("userProperties", {}).get("aiToolTaProtocol", {}), ensure_ascii=False, sort_keys=True),
            )
            mxs.setUserProp(
                node,
                "aiToolTaMaxFixturePayload",
                json.dumps(node_payload, ensure_ascii=False, sort_keys=True),
            )
            material_payload = node_payload.get("material")
            if isinstance(material_payload, dict):
                material = mxs.StandardMaterial(name=str(material_payload.get("name")))
                node.material = material


def collect_pymxs_scene_facts(mxs: Any, fixture: Dict[str, Any]) -> Dict[str, Any]:
    # Max runtime collection keeps fixture payload in user props so the report can
    # prove pymxs object traversal without relying on fragile renderer-specific APIs.
    assets_by_id: Dict[str, Dict[str, Any]] = {}
    for node in list(mxs.objects):
        asset_id = _get_user_prop(mxs, node, "aiToolTaAssetId")
        if not asset_id:
            continue
        asset = assets_by_id.setdefault(
            asset_id,
            {
                "id": asset_id,
                "label": _get_user_prop(mxs, node, "aiToolTaAssetLabel"),
                "exportRoot": _get_user_prop(mxs, node, "aiToolTaExportRoot"),
                "layer": _get_user_prop(mxs, node, "aiToolTaLayer"),
                "userProperties": {
                    "aiToolTaProtocol": _read_json(_get_user_prop(mxs, node, "aiToolTaProtocol"), {}),
                },
                "nodes": [],
            },
        )
        payload = _read_json(_get_user_prop(mxs, node, "aiToolTaMaxFixturePayload"), {})
        if payload:
            asset["nodes"].append(payload)

    from .contract import collect_scene_facts

    runtime_fixture = {
        "schema": fixture.get("schema"),
        "intent": fixture.get("intent"),
        "scene": fixture.get("scene", {}),
        "assets": list(assets_by_id.values()),
    }
    facts = collect_scene_facts(runtime_fixture)
    facts["scene"]["runtimeCollected"] = True
    facts["scene"]["runtimeObjectCount"] = len(list(mxs.objects))
    return facts


def _get_user_prop(mxs: Any, node: Any, key: str) -> str:
    try:
        value = mxs.getUserProp(node, key)
    except Exception:
        return ""
    return str(value) if value is not None else ""


def _read_json(value: str, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _safe_str(callback: Any) -> str:
    try:
        return str(callback())
    except Exception:
        return "unknown"

