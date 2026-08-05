"""Houdini hou collector for the Cross-DCC rule adapter.

This module is imported by hython. Normal Python can compile it because hou is
imported only inside runtime functions.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

from .contract import build_report, load_fixture


def build_hou_report(fixture_path: str | Path) -> Dict[str, Any]:
    import hou  # type: ignore

    fixture = load_fixture(fixture_path)
    reset_scene(hou)
    create_scene_from_fixture(hou, fixture)
    runtime_fixture = collect_hou_fixture(hou, fixture)
    runtime = {
        "runtimeCollected": True,
        "runtimeNodeCount": _node_count(hou),
        "houdiniVersion": _houdini_version(hou),
    }
    report = build_report(fixture_path, hython_available=True, hython_path="hython.exe", runtime=runtime)
    report["runtimeFixture"] = runtime_fixture
    report["generatedAt"] = time.strftime("%Y-%m-%d %H:%M:%S")
    return report


def reset_scene(hou: Any) -> None:
    try:
        hou.hipFile.clear(suppress_save_prompt=True)
    except TypeError:
        hou.hipFile.clear()


def create_scene_from_fixture(hou: Any, fixture: Dict[str, Any]) -> None:
    obj = hou.node("/obj")
    if obj is None:
        raise RuntimeError("/obj network is unavailable")
    root = obj.createNode("subnet", node_name="AI_TOOL_TA_HOUDINI_FIXTURE")
    root.setUserData("aiToolTaFixtureSchema", str(fixture.get("schema")))
    root.setUserData("aiToolTaFixturePayload", json.dumps(fixture, ensure_ascii=False, sort_keys=True))
    for asset in fixture.get("assets", []):
        node_name = _node_name(asset.get("id"))
        asset_node = root.createNode("subnet", node_name=node_name)
        asset_node.setUserData("aiToolTaAssetId", str(asset.get("id")))
        asset_node.setUserData("aiToolTaAssetPayload", json.dumps(asset, ensure_ascii=False, sort_keys=True))
        for output in asset.get("outputs", []):
            output_node = asset_node.createNode("null", node_name=_node_name(output.get("name")))
            output_node.setUserData("aiToolTaOutputRole", str(output.get("role")))
            output_node.setUserData("aiToolTaOutputPayload", json.dumps(output, ensure_ascii=False, sort_keys=True))
        asset_node.layoutChildren()
    root.layoutChildren()


def collect_hou_fixture(hou: Any, fixture: Dict[str, Any]) -> Dict[str, Any]:
    root = hou.node("/obj/AI_TOOL_TA_HOUDINI_FIXTURE")
    assets = []
    if root is not None:
        for node in root.children():
            payload = _read_json(node.userData("aiToolTaAssetPayload"), {})
            if payload:
                assets.append(payload)
    return {
        "schema": fixture.get("schema"),
        "intent": fixture.get("intent"),
        "scene": fixture.get("scene", {}),
        "assets": assets,
    }


def _node_count(hou: Any) -> int:
    root = hou.node("/obj/AI_TOOL_TA_HOUDINI_FIXTURE")
    if root is None:
        return 0
    return 1 + sum(1 for _ in root.allSubChildren())


def _houdini_version(hou: Any) -> str:
    try:
        return ".".join(str(part) for part in hou.applicationVersion())
    except Exception:
        return "unknown"


def _read_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def _node_name(value: Any) -> str:
    text = str(value or "node")
    return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in text)
