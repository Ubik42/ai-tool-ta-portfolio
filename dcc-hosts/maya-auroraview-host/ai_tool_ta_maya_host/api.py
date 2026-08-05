"""Maya API surface exposed to the AuroraView frontend."""

from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import PORTFOLIO_ROOT, display_path, ensure_artifacts_dir, paths_report


PROTOCOL_ATTR = "aiToolTaProtocol"
SCENE_TRANSACTION_ATTR = "aiToolTaTransactionRole"
EXPECTED_PROTOCOL_SCHEMA = "asset-protocol@dcc-r9"
VISUAL_CAMERA_ATTR = "aiToolTaReviewCamera"
VISUAL_CAMERA_GROUPS = {
    "basic": [
        ("Camera_Front", (0.0, 0.0, 8.0), (0.0, 0.0, 0.0)),
        ("Camera_Back", (0.0, 0.0, -8.0), (0.0, 180.0, 0.0)),
        ("Camera_Left", (-8.0, 0.0, 0.0), (0.0, -90.0, 0.0)),
        ("Camera_Right", (8.0, 0.0, 0.0), (0.0, 90.0, 0.0)),
        ("Camera_Top", (0.0, 8.0, 0.0), (-90.0, 0.0, 0.0)),
        ("Camera_Bottom", (0.0, -8.0, 0.0), (90.0, 0.0, 0.0)),
    ],
    "detail": [
        ("Camera_01", (4.5, 3.0, 5.0), (-25.0, 38.0, 0.0)),
        ("Camera_02", (-4.5, 2.8, 5.0), (-23.0, -38.0, 0.0)),
        ("Camera_03", (4.5, 2.8, -5.0), (-23.0, 140.0, 0.0)),
        ("Camera_04", (-4.5, 2.8, -5.0), (-23.0, -140.0, 0.0)),
    ],
}
VISUAL_PASS_PRESETS = [
    {
        "id": "rb_lod0",
        "label": "Red / Blue LOD0",
        "required_bucket": "LOD0",
        "material_contract": "A red 45% transparent, B cyan 45% transparent",
    },
    {
        "id": "wb_lod0",
        "label": "White / Blue LOD0",
        "required_bucket": "LOD0",
        "material_contract": "A lambert white, B cyan",
    },
    {
        "id": "rb_dt",
        "label": "Red / Blue DT",
        "required_bucket": "DT",
        "material_contract": "A red 45% transparent, B cyan 45% transparent",
    },
    {
        "id": "wb_dt",
        "label": "White / Blue DT",
        "required_bucket": "DT",
        "material_contract": "A lambert white, B cyan",
    },
    {
        "id": "solo_b",
        "label": "Variant Dual LOD",
        "required_bucket": "variant_lod0_or_dt",
        "material_contract": "B LOD0 dark grey, B DT light grey, A hidden",
    },
]
TEXTURE_ROLE_EXPECTED_COLOR_SPACE = {
    "baseColor": "sRGB",
    "emissive": "sRGB",
    "normal": "Raw",
    "roughness": "Raw",
    "metallic": "Raw",
    "ao": "Raw",
    "opacity": "Raw",
    "height": "Raw",
}


def _read_json_dict(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _resolve_package_path(path_value: Any, base_dir: Path) -> Optional[Path]:
    if isinstance(path_value, Path):
        return path_value
    if not isinstance(path_value, str) or not path_value:
        return None
    if path_value.startswith("<repo>"):
        suffix = path_value[len("<repo>") :].lstrip("\\/")
        return PORTFOLIO_ROOT / suffix
    path = Path(path_value)
    return path if path.is_absolute() else base_dir / path


def _probe_file(
    file_id: str,
    label: str,
    kind: str,
    path_value: Any,
    required: bool = True,
    base_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    base = base_dir or PORTFOLIO_ROOT
    resolved = _resolve_package_path(path_value, base)
    exists = bool(resolved and resolved.exists())
    bytes_size = resolved.stat().st_size if exists and resolved else 0
    return {
        "id": file_id,
        "label": label,
        "kind": kind,
        "path": display_path(resolved) if resolved else None,
        "required": required,
        "exists": exists,
        "bytes": bytes_size,
        "state": "Present" if exists else "RequiredMissing" if required else "OptionalMissing",
    }


def _dict_list(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _preset_fact_reviewer_action(status: str, has_waiver: bool) -> str:
    if status == "matched":
        return "accept"
    if status == "waived" or has_waiver:
        return "verify waiver owner and expiry"
    if status == "drift":
        return "send to owner for preset policy decision"
    if status == "blocked":
        return "hold engine import until policy is fixed"
    return "manual review"


def _maya_cmds():
    try:
        import maya.cmds as cmds  # type: ignore
    except Exception as exc:  # pragma: no cover - only meaningful inside Maya
        raise RuntimeError("This API must run inside Autodesk Maya") from exc

    if not hasattr(cmds, "ls"):
        try:
            import maya.standalone as standalone  # type: ignore

            standalone.initialize(name="python")
            import maya.cmds as cmds  # type: ignore  # noqa: PLC0415
        except Exception:
            pass

    return cmds


def _safe_attr_exists(cmds: Any, node: str, attr: str) -> bool:
    return bool(cmds.objExists(node) and cmds.attributeQuery(attr, node=node, exists=True))


def _get_top_parent(cmds: Any, node: str) -> Optional[str]:
    parents = cmds.listRelatives(node, parent=True, fullPath=False) or []
    current = parents[0] if parents else None
    top_parent = current

    while current:
        next_parents = cmds.listRelatives(current, parent=True, fullPath=False) or []
        if not next_parents:
            break
        top_parent = next_parents[0]
        current = next_parents[0]

    return top_parent


def _unique_existing(nodes: List[str], cmds: Any) -> List[str]:
    result: List[str] = []
    seen = set()
    for node in nodes:
        if node in seen or not cmds.objExists(node):
            continue
        seen.add(node)
        result.append(node)
    return result


def _resolve_rule_matrix_targets(
    cmds: Any,
    names: Optional[List[str]] = None,
    include_all: bool = False,
) -> List[str]:
    if names:
        return _unique_existing(names, cmds)

    targets = [] if include_all else (cmds.ls(selection=True, long=False) or [])
    if targets:
        return _unique_existing(targets, cmds)

    mesh_shapes = cmds.ls(type="mesh", long=False) or []
    parents = cmds.listRelatives(mesh_shapes, parent=True, fullPath=False) or []
    return _unique_existing(parents, cmds)


def _read_protocol_payload(cmds: Any, node: str, shapes: List[str]) -> Dict[str, Any]:
    carriers = [node] + shapes
    for carrier in carriers:
        if not _safe_attr_exists(cmds, carrier, PROTOCOL_ATTR):
            continue

        raw = cmds.getAttr(carrier + "." + PROTOCOL_ATTR)
        try:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("Protocol payload must be a JSON object.")
            return {
                "carrier": carrier,
                "has_protocol": True,
                "payload": payload,
                "raw": raw,
                "payload_valid": True,
            }
        except Exception:
            return {
                "carrier": carrier,
                "has_protocol": True,
                "payload": {},
                "raw": raw,
                "payload_valid": False,
                "payload_error": "Invalid JSON payload",
            }

    return {
        "carrier": None,
        "has_protocol": False,
        "payload": {},
        "raw": None,
        "payload_valid": False,
    }


def _collect_rule_matrix_facts(
    cmds: Any,
    names: Optional[List[str]] = None,
    include_all: bool = False,
) -> List[Dict[str, Any]]:
    facts: List[Dict[str, Any]] = []
    targets = _resolve_rule_matrix_targets(cmds, names=names, include_all=include_all)

    for target in targets:
        node = target
        node_type = cmds.nodeType(target)
        if node_type == "mesh":
            parents = cmds.listRelatives(target, parent=True, fullPath=False) or []
            if parents:
                node = parents[0]

        shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=False) or []
        mesh_shapes = [shape for shape in shapes if cmds.nodeType(shape) == "mesh"]
        protocol = _read_protocol_payload(cmds, node, mesh_shapes)
        shading_engines: List[str] = []

        for shape in mesh_shapes:
            shading_engines.extend(cmds.listConnections(shape, type="shadingEngine") or [])

        material_sets = sorted(set(shading_engines))
        payload = protocol["payload"]
        payload_budget = payload.get("budget", {}) if isinstance(payload.get("budget"), dict) else {}

        try:
            triangles = int(cmds.polyEvaluate(node, triangle=True)) if mesh_shapes else 0
        except Exception:
            triangles = 0

        try:
            faces = int(cmds.polyEvaluate(node, face=True)) if mesh_shapes else 0
        except Exception:
            faces = 0

        try:
            visible = bool(cmds.getAttr(node + ".visibility"))
        except Exception:
            visible = True

        parent = (cmds.listRelatives(node, parent=True, fullPath=False) or [None])[0]
        top_parent = _get_top_parent(cmds, node)
        collision_value = payload.get("collision") or payload.get("collisionType") or payload.get("physics")
        collision_from_name = "collision" in node.lower() or "_col" in node.lower()

        facts.append(
            {
                "node": node,
                "node_type": cmds.nodeType(node),
                "shapes": mesh_shapes,
                "mesh_shape_count": len(mesh_shapes),
                "triangles": triangles,
                "faces": faces,
                "materials": material_sets,
                "material_count": len(material_sets),
                "visible": visible,
                "parent": parent,
                "top_parent": top_parent,
                "has_export_root": bool(top_parent),
                "protocol_attr": PROTOCOL_ATTR,
                "protocol_carrier": protocol["carrier"],
                "has_protocol": protocol["has_protocol"],
                "payload_valid": protocol["payload_valid"],
                "payload_error": protocol.get("payload_error"),
                "schema": payload.get("schema"),
                "role": payload.get("role"),
                "platform": payload.get("platform"),
                "lod": payload.get("lod"),
                "budget_triangles": payload_budget.get("triangles"),
                "budget_textures": payload_budget.get("textures"),
                "collision": collision_value,
                "collision_from_name": collision_from_name,
            }
        )

    return facts


def _gate_from_results(results: List[Dict[str, Any]]) -> str:
    if any(result["status"] == "error" for result in results):
        return "Blocked"
    if any(result["status"] in ("warning", "skipped") for result in results):
        return "Review"
    return "Ready"


def _summarize_rule_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    pass_count = sum(1 for result in results if result["status"] == "pass")
    warning_count = sum(1 for result in results if result["status"] == "warning")
    error_count = sum(1 for result in results if result["status"] == "error")
    skipped_count = sum(1 for result in results if result["status"] == "skipped")
    score = max(0, 100 - error_count * 32 - warning_count * 12 - skipped_count * 8)
    return {
        "score": score,
        "pass": pass_count,
        "warning": warning_count,
        "error": error_count,
        "skipped": skipped_count,
        "gate": _gate_from_results(results),
    }


def _rule_result(
    rule_id: str,
    name: str,
    stage: str,
    severity: str,
    status: str,
    message: str,
    evidence: str,
    nodes: List[str],
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "rule_id": rule_id,
        "name": name,
        "stage": stage,
        "severity": severity,
        "status": status,
        "message": message,
        "evidence": evidence,
        "nodes": nodes,
        "fix_preview": fix_preview,
    }


def _validate_rule_matrix_facts(facts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not facts:
        return [
            _rule_result(
                "scene-has-targets",
                "Scene Targets",
                "Collect",
                "blocker",
                "error",
                "No mesh targets were found for rule matrix collection.",
                "selection=0, meshTransforms=0",
                [],
                "Create or select a publishable mesh asset before validation.",
            )
        ]

    nodes = [fact["node"] for fact in facts]
    missing_protocol = [fact["node"] for fact in facts if not fact["has_protocol"]]
    invalid_payload = [fact["node"] for fact in facts if fact["has_protocol"] and not fact["payload_valid"]]
    stale_schema = [
        fact["node"]
        for fact in facts
        if fact["has_protocol"] and fact["payload_valid"] and fact.get("schema") != EXPECTED_PROTOCOL_SCHEMA
    ]
    missing_collision = [fact["node"] for fact in facts if not (fact.get("collision") or fact["collision_from_name"])]
    missing_lod = [fact["node"] for fact in facts if not fact.get("lod")]
    missing_mesh = [fact["node"] for fact in facts if fact["mesh_shape_count"] == 0]
    missing_material = [fact["node"] for fact in facts if fact["mesh_shape_count"] > 0 and fact["material_count"] == 0]
    no_export_root = [fact["node"] for fact in facts if not fact["has_export_root"]]

    results = [
        _rule_result(
            "protocol-carrier",
            "Protocol Carrier",
            "Collect",
            "blocker",
            "error" if missing_protocol or invalid_payload else "warning" if stale_schema else "pass",
            (
                "Protocol custom attr is missing or unreadable."
                if missing_protocol or invalid_payload
                else "Protocol schema should be upgraded before extract."
                if stale_schema
                else "All collected nodes carry a valid asset protocol payload."
            ),
            (
                "missing=%s invalid=%s"
                % (",".join(missing_protocol) or "-", ",".join(invalid_payload) or "-")
                if missing_protocol or invalid_payload
                else "schema=%s nodes=%s" % (EXPECTED_PROTOCOL_SCHEMA if not stale_schema else ",".join(stale_schema), len(nodes))
            ),
            missing_protocol + invalid_payload + stale_schema,
            (
                "Safe preview: add or rewrite aiToolTaProtocol with the active payload."
                if missing_protocol or invalid_payload or stale_schema
                else "No fix needed."
            ),
        ),
        _rule_result(
            "collision-contract",
            "Collision Contract",
            "Validate",
            "blocker",
            "error" if missing_collision else "pass",
            (
                "Collision declaration is missing on collected publish nodes."
                if missing_collision
                else "Collision contract is declared in payload or node naming."
            ),
            "missing=%s" % (",".join(missing_collision) or "-"),
            missing_collision,
            (
                "Manual preview: author collision geometry, set collision payload, or attach owner waiver."
                if missing_collision
                else "No fix needed."
            ),
        ),
        _rule_result(
            "lod-budget",
            "LOD Budget",
            "Validate",
            "major",
            "warning" if missing_lod else "pass",
            (
                "LOD declaration is absent; platform budget cannot be checked."
                if missing_lod
                else "LOD declaration is present for collected nodes."
            ),
            "missing=%s" % (",".join(missing_lod) or "-"),
            missing_lod,
            "Manual preview: queue LOD budget review." if missing_lod else "No fix needed.",
        ),
        _rule_result(
            "material-texture-sync",
            "Material / Texture Sync",
            "Validate",
            "major",
            "warning" if missing_mesh or missing_material else "pass",
            (
                "Mesh or material binding evidence needs TA review."
                if missing_mesh or missing_material
                else "Mesh shapes and shadingEngine bindings are present."
            ),
            "missingMesh=%s missingMaterial=%s"
            % (",".join(missing_mesh) or "-", ",".join(missing_material) or "-"),
            missing_mesh + missing_material,
            (
                "Manual preview: inspect mesh exportability or material binding before extract."
                if missing_mesh or missing_material
                else "No fix needed."
            ),
        ),
        _rule_result(
            "export-root-clean",
            "Export Root Clean",
            "Fix",
            "major",
            "warning" if no_export_root else "pass",
            (
                "Some publish nodes are not grouped under an export root."
                if no_export_root
                else "Collected nodes are under an export root or fixture root."
            ),
            "noRoot=%s" % (",".join(no_export_root) or "-"),
            no_export_root,
            (
                "Safe preview: create or tag an export root and parent publish nodes."
                if no_export_root
                else "No fix needed."
            ),
        ),
    ]

    manifest_status = _gate_from_results(results)
    results.append(
        _rule_result(
            "publish-manifest",
            "Publish Manifest",
            "Extract",
            "minor",
            "error" if manifest_status == "Blocked" else "warning" if manifest_status == "Review" else "pass",
            (
                "Manifest should include blockers before the asset can publish."
                if manifest_status == "Blocked"
                else "Manifest should include review notes and staged fixes."
                if manifest_status == "Review"
                else "Manifest can be exported from collected scene facts."
            ),
            "upstreamGate=%s, facts=%s" % (manifest_status, len(facts)),
            nodes,
            "Safe preview: export validation report JSON as the publish sidecar.",
        )
    )
    return results


def _preview_rule_matrix_fixes(
    facts: List[Dict[str, Any]],
    validation: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    previews: List[Dict[str, Any]] = []
    missing_protocol_nodes = [
        fact["node"]
        for fact in facts
        if not fact["has_protocol"] or not fact["payload_valid"] or fact.get("schema") != EXPECTED_PROTOCOL_SCHEMA
    ]
    missing_collision_nodes = [
        fact["node"] for fact in facts if not (fact.get("collision") or fact["collision_from_name"])
    ]
    missing_lod_nodes = [fact["node"] for fact in facts if not fact.get("lod")]
    missing_material_nodes = [
        fact["node"] for fact in facts if fact["mesh_shape_count"] > 0 and fact["material_count"] == 0
    ]
    no_export_root_nodes = [fact["node"] for fact in facts if not fact["has_export_root"]]

    for node in missing_protocol_nodes:
        previews.append(
            {
                "id": "fix-%s-protocol-carrier" % node,
                "node": node,
                "rule_id": "protocol-carrier",
                "kind": "safe_auto",
                "owner": "Tool",
                "mutation": "write_string_attr",
                "target": node + "." + PROTOCOL_ATTR,
                "before": "missing_or_invalid",
                "after": EXPECTED_PROTOCOL_SCHEMA,
                "preview": "Add or rewrite aiToolTaProtocol using the active workbench payload.",
            }
        )

    for node in missing_collision_nodes:
        previews.append(
            {
                "id": "fix-%s-collision-contract" % node,
                "node": node,
                "rule_id": "collision-contract",
                "kind": "manual_only",
                "owner": "TA",
                "mutation": "owner_disposition_required",
                "target": node,
                "before": "collision=missing",
                "after": "collision=simple|complex|proxy or waiver",
                "preview": "Do not auto-generate gameplay-affecting collision without owner approval.",
            }
        )

    for node in missing_lod_nodes:
        previews.append(
            {
                "id": "fix-%s-lod-budget" % node,
                "node": node,
                "rule_id": "lod-budget",
                "kind": "manual_only",
                "owner": "TA",
                "mutation": "budget_review_required",
                "target": node,
                "before": "lod=missing",
                "after": "lod declaration or owner exception",
                "preview": "Queue LOD review before extract.",
            }
        )

    for node in missing_material_nodes:
        previews.append(
            {
                "id": "fix-%s-material-texture-sync" % node,
                "node": node,
                "rule_id": "material-texture-sync",
                "kind": "manual_only",
                "owner": "TA",
                "mutation": "material_binding_review",
                "target": node,
                "before": "material binding missing",
                "after": "shadingEngine binding verified",
                "preview": "Inspect material binding before publish.",
            }
        )

    for node in no_export_root_nodes:
        previews.append(
            {
                "id": "fix-%s-export-root-clean" % node,
                "node": node,
                "rule_id": "export-root-clean",
                "kind": "safe_auto",
                "owner": "Tool",
                "mutation": "create_or_tag_export_root",
                "target": node,
                "before": "root=missing",
                "after": "root=asset_export_root",
                "preview": "Create or tag an export root before extract.",
            }
        )

    if validation:
        previews.append(
            {
                "id": "fix-publish-manifest",
                "node": "<scene>",
                "rule_id": "publish-manifest",
                "kind": "safe_auto",
                "owner": "Tool",
                "mutation": "export_report_json",
                "target": "maya-auroraview-host/artifacts",
                "before": "transient validation result",
                "after": "versioned report artifact",
                "preview": "Export collected facts, validation rows, and staged fixes as JSON evidence.",
            }
        )

    return previews


def _ensure_string_attr(cmds: Any, node: str, attr: str, value: str) -> None:
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType="string")
    cmds.setAttr(node + "." + attr, value, type="string")


def _json_fingerprint(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _round_number(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 5)
    return value


def _safe_get_attr_value(cmds: Any, node: str, attr: str) -> Any:
    plug = node + "." + attr
    try:
        value = cmds.getAttr(plug)
    except Exception:
        return None
    if isinstance(value, list):
        return [[_round_number(item) for item in row] if isinstance(row, tuple) else row for row in value]
    if isinstance(value, tuple):
        return [_round_number(item) for item in value]
    return _round_number(value)


def _capture_transaction_scope(cmds: Any, names: Optional[List[str]] = None, include_all: bool = False) -> List[str]:
    if names:
        roots = _unique_existing(names, cmds)
    else:
        roots = _unique_existing(cmds.ls(selection=True, long=False) or [], cmds)

    if not roots and include_all:
        roots = _unique_existing(cmds.ls(type="transform", long=False) or [], cmds)

    scoped: List[str] = []
    seen = set()
    for root in roots:
        candidates = [root] + (cmds.listRelatives(root, allDescendents=True, fullPath=False) or [])
        for node in candidates:
            if node in seen or not cmds.objExists(node):
                continue
            seen.add(node)
            scoped.append(node)
    return scoped


def _capture_transaction_state(
    cmds: Any,
    names: Optional[List[str]] = None,
    include_all: bool = False,
) -> Dict[str, Any]:
    scoped = _capture_transaction_scope(cmds, names=names, include_all=include_all)
    nodes: Dict[str, Any] = {}
    for node in scoped:
        node_type = cmds.nodeType(node)
        parents = cmds.listRelatives(node, parent=True, fullPath=False) or []
        children = cmds.listRelatives(node, children=True, fullPath=False) or []
        attrs: Dict[str, Any] = {}
        for attr in ("translate", "rotate", "scale", "visibility"):
            if node_type == "transform" and cmds.attributeQuery(attr, node=node, exists=True):
                attrs[attr] = _safe_get_attr_value(cmds, node, attr)
        if node_type == "camera":
            for attr in ("focalLength", "nearClipPlane", "farClipPlane"):
                if cmds.attributeQuery(attr, node=node, exists=True):
                    attrs[attr] = _safe_get_attr_value(cmds, node, attr)
        for attr in cmds.listAttr(node, userDefined=True) or []:
            attrs[attr] = _safe_get_attr_value(cmds, node, attr)
        nodes[node] = {
            "type": node_type,
            "parent": parents[0] if parents else None,
            "children": children,
            "attrs": attrs,
        }

    state = {
        "schema": "maya-scene-transaction-state@0.1.0",
        "captured_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "scope": scoped,
        "node_count": len(nodes),
        "selection": cmds.ls(selection=True, long=False) or [],
        "time": _round_number(cmds.currentTime(query=True)),
        "playback": {
            "min": _round_number(cmds.playbackOptions(query=True, min=True)),
            "max": _round_number(cmds.playbackOptions(query=True, max=True)),
        },
        "nodes": nodes,
    }
    state["fingerprint"] = _json_fingerprint({"nodes": nodes, "selection": state["selection"], "time": state["time"]})
    return state


def _diff_transaction_states(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    before_nodes = before.get("nodes", {}) if isinstance(before.get("nodes"), dict) else {}
    after_nodes = after.get("nodes", {}) if isinstance(after.get("nodes"), dict) else {}
    before_names = set(before_nodes)
    after_names = set(after_nodes)

    created = sorted(after_names - before_names)
    deleted = sorted(before_names - after_names)
    modified: List[Dict[str, Any]] = []

    for node in sorted(before_names & after_names):
        before_node = before_nodes[node]
        after_node = after_nodes[node]
        deltas: List[Dict[str, Any]] = []
        if before_node.get("parent") != after_node.get("parent"):
            deltas.append({"field": "parent", "before": before_node.get("parent"), "after": after_node.get("parent")})
        before_attrs = before_node.get("attrs", {}) if isinstance(before_node.get("attrs"), dict) else {}
        after_attrs = after_node.get("attrs", {}) if isinstance(after_node.get("attrs"), dict) else {}
        for attr in sorted(set(before_attrs) | set(after_attrs)):
            if before_attrs.get(attr) != after_attrs.get(attr):
                deltas.append({"field": "attrs.%s" % attr, "before": before_attrs.get(attr), "after": after_attrs.get(attr)})
        if deltas:
            modified.append({"node": node, "type": after_node.get("type"), "deltas": deltas})

    selection_changed = before.get("selection") != after.get("selection")
    time_changed = before.get("time") != after.get("time")
    rollback_actions: List[Dict[str, Any]] = []
    for node in created:
        rollback_actions.append({"id": "rollback-delete-%s" % node, "kind": "delete_created_node", "node": node})
    for node in deleted:
        rollback_actions.append({"id": "rollback-restore-%s" % node, "kind": "restore_deleted_node_from_snapshot", "node": node})
    for item in modified:
        for delta in item["deltas"]:
            rollback_actions.append(
                {
                    "id": "rollback-set-%s-%s" % (item["node"], delta["field"].replace(".", "-")),
                    "kind": "set_previous_value",
                    "node": item["node"],
                    "field": delta["field"],
                    "value": delta["before"],
                }
            )
    if selection_changed:
        rollback_actions.append({"id": "rollback-selection", "kind": "restore_selection", "value": before.get("selection", [])})
    if time_changed:
        rollback_actions.append({"id": "rollback-time", "kind": "restore_current_time", "value": before.get("time")})

    summary = {
        "created": len(created),
        "deleted": len(deleted),
        "modified": len(modified),
        "selectionChanged": selection_changed,
        "timeChanged": time_changed,
        "rollbackActions": len(rollback_actions),
        "gate": "Review" if created or deleted or modified or selection_changed or time_changed else "Ready",
    }
    return {
        "schema": "maya-scene-transaction-diff@0.1.0",
        "summary": summary,
        "created": created,
        "deleted": deleted,
        "modified": modified,
        "selection_changed": {
            "changed": selection_changed,
            "before": before.get("selection", []),
            "after": after.get("selection", []),
        },
        "time_changed": {"changed": time_changed, "before": before.get("time"), "after": after.get("time")},
        "rollback_preview": rollback_actions,
    }


def _classify_visual_bucket(node: str) -> str:
    upper = node.upper()
    if "LOD0" in upper:
        return "LOD0"
    if "_DT" in upper or ":DT" in upper or upper.endswith("DT"):
        return "DT"
    return "other"


def _collect_visual_meshes(
    cmds: Any,
    names: Optional[List[str]] = None,
    include_all: bool = False,
) -> Dict[str, Any]:
    targets = _resolve_rule_matrix_targets(cmds, names=names, include_all=include_all)
    meshes: List[Dict[str, Any]] = []

    for target in targets:
        node = target
        if cmds.nodeType(target) == "mesh":
            parents = cmds.listRelatives(target, parent=True, fullPath=False) or []
            node = parents[0] if parents else target
        shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=False) or []
        mesh_shapes = [shape for shape in shapes if cmds.nodeType(shape) == "mesh"]
        if not mesh_shapes:
            continue
        meshes.append(
            {
                "node": node,
                "shapes": mesh_shapes,
                "bucket": _classify_visual_bucket(node),
                "slot": "B" if "B" in node.upper() or "VARIANT" in node.upper() else "A",
                "parent": (cmds.listRelatives(node, parent=True, fullPath=False) or [None])[0],
            }
        )

    buckets = {
        "LOD0": [mesh["node"] for mesh in meshes if mesh["bucket"] == "LOD0"],
        "DT": [mesh["node"] for mesh in meshes if mesh["bucket"] == "DT"],
        "other": [mesh["node"] for mesh in meshes if mesh["bucket"] == "other"],
    }
    return {"meshes": meshes, "buckets": buckets}


def _collect_visual_cameras(cmds: Any, camera_groups: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    allowed_groups = set(camera_groups or ["basic", "detail"])
    camera_shapes = cmds.ls(type="camera", long=False) or []
    cameras: List[Dict[str, Any]] = []

    for shape in camera_shapes:
        parents = cmds.listRelatives(shape, parent=True, fullPath=False) or []
        camera = parents[0] if parents else shape
        if camera in ("persp", "top", "front", "side"):
            continue
        group = "detail" if camera.startswith("Camera_0") or camera.startswith("wp_cam") else "basic"
        if group not in allowed_groups:
            continue
        tagged = _safe_attr_exists(cmds, camera, VISUAL_CAMERA_ATTR)
        name_matches = camera.startswith("Camera_") or camera.startswith("cam_") or camera.startswith("wp_cam")
        if not tagged and not name_matches:
            continue
        cameras.append(
            {
                "name": camera,
                "shape": shape,
                "group": group,
                "tagged": tagged,
                "focal_length": cmds.getAttr(shape + ".focalLength") if cmds.objExists(shape + ".focalLength") else None,
            }
        )

    return cameras


def _build_visual_pass_manifest(
    cmds: Any,
    names: Optional[List[str]] = None,
    include_all: bool = False,
    camera_groups: Optional[List[str]] = None,
    width: int = 1024,
    height: int = 1024,
) -> Dict[str, Any]:
    mesh_result = _collect_visual_meshes(cmds, names=names, include_all=include_all)
    cameras = _collect_visual_cameras(cmds, camera_groups=camera_groups)
    buckets = mesh_result["buckets"]
    passes: List[Dict[str, Any]] = []

    for preset in VISUAL_PASS_PRESETS:
        required_bucket = preset["required_bucket"]
        if not cameras:
            status = "skipped"
            reason = "No review cameras were discovered."
        elif required_bucket == "variant_lod0_or_dt":
            status = "run" if buckets["LOD0"] or buckets["DT"] else "skipped"
            reason = "Variant has at least one visible LOD bucket." if status == "run" else "No LOD0 or DT meshes found."
        else:
            bucket_nodes = buckets[required_bucket]
            status = "run" if bucket_nodes else "skipped"
            reason = "%s mesh bucket has %s node(s)." % (required_bucket, len(bucket_nodes))

        shots = [
            {
                "camera": camera["name"],
                "output": "%s_%s.png" % (camera["name"], preset["id"]),
                "width": width,
                "height": height,
            }
            for camera in cameras
        ] if status == "run" else []

        passes.append(
            {
                "id": preset["id"],
                "label": preset["label"],
                "status": status,
                "reason": reason,
                "required_bucket": required_bucket,
                "material_contract": preset["material_contract"],
                "camera_count": len(cameras),
                "image_count": len(shots),
                "shots": shots,
            }
        )

    return {
        "schema": "maya-visual-review-pass-manifest@1.0.0",
        "resolution": {"width": width, "height": height},
        "camera_groups": camera_groups or ["basic", "detail"],
        "cameras": cameras,
        "mesh_summary": {
            "total": len(mesh_result["meshes"]),
            "lod0": len(buckets["LOD0"]),
            "dt": len(buckets["DT"]),
            "other": len(buckets["other"]),
        },
        "meshes": mesh_result["meshes"],
        "passes": passes,
        "summary": {
            "run": sum(1 for item in passes if item["status"] == "run"),
            "skipped": sum(1 for item in passes if item["status"] == "skipped"),
            "image_count": sum(int(item["image_count"]) for item in passes),
            "gate": "Review" if any(item["status"] == "skipped" for item in passes) else "Ready",
        },
    }


def _infer_texture_role(name: str) -> str:
    normalized = name.lower()
    role_tokens = [
        ("baseColor", ["basecolor", "base_color", "_bc", "_d", "diffuse", "albedo"]),
        ("normal", ["normal", "_n", "_nor"]),
        ("roughness", ["roughness", "_rgh", "_rough", "_orm"]),
        ("metallic", ["metallic", "_metal", "_m"]),
        ("ao", ["_ao", "ambient"]),
        ("emissive", ["emissive", "_e"]),
        ("opacity", ["opacity", "_a", "alpha"]),
        ("height", ["height", "_h"]),
    ]
    for role, tokens in role_tokens:
        if any(token in normalized for token in tokens):
            return role
    return "unknown"


def _infer_texture_resolution(path_or_name: str) -> Optional[int]:
    match = re.search(r"(?:^|[_-])(512|1024|2048|4096|8192)(?:[_\-.]|$)", path_or_name)
    if not match:
        return None
    try:
        return int(match.group(1))
    except Exception:
        return None


def _collect_texture_scene(cmds: Any, include_all: bool = True) -> Dict[str, Any]:
    mesh_result = _collect_visual_meshes(cmds, include_all=include_all)
    shading_engines = sorted(set(cmds.ls(type="shadingEngine") or []))
    materials: List[Dict[str, Any]] = []
    file_nodes: List[Dict[str, Any]] = []

    for shading_engine in shading_engines:
        surface_nodes = cmds.listConnections(shading_engine + ".surfaceShader", source=True, destination=False) or []
        for material in surface_nodes:
            if material in ("lambert1", "particleCloud1"):
                continue
            material_files = sorted(set(cmds.listConnections(material, type="file") or []))
            materials.append(
                {
                    "name": material,
                    "shading_engine": shading_engine,
                    "file_nodes": material_files,
                }
            )

    for file_node in sorted(set(cmds.ls(type="file") or [])):
        try:
            texture_path = cmds.getAttr(file_node + ".fileTextureName") or ""
        except Exception:
            texture_path = ""
        try:
            color_space = cmds.getAttr(file_node + ".colorSpace") or ""
        except Exception:
            color_space = ""

        file_name = Path(texture_path).name if texture_path else file_node
        role = _infer_texture_role(file_name)
        expected_color_space = TEXTURE_ROLE_EXPECTED_COLOR_SPACE.get(role)
        exists = bool(texture_path and Path(texture_path).exists())
        file_nodes.append(
            {
                "node": file_node,
                "file_name": file_name,
                "path": texture_path,
                "exists": exists,
                "role": role,
                "color_space": color_space,
                "expected_color_space": expected_color_space,
                "resolution": _infer_texture_resolution(file_name),
                "materials": sorted(set(cmds.listConnections(file_node, type="lambert") or [])),
            }
        )

    return {
        "schema": "maya-texture-delivery-inspection@1.0.0",
        "mesh_summary": mesh_result["buckets"] | {"total": len(mesh_result["meshes"])},
        "meshes": mesh_result["meshes"],
        "materials": materials,
        "file_nodes": file_nodes,
    }


def _validate_texture_scene(inspection: Dict[str, Any]) -> Dict[str, Any]:
    file_nodes = inspection["file_nodes"]
    materials = inspection["materials"]
    results: List[Dict[str, Any]] = []

    def add_result(rule_id: str, label: str, status: str, evidence: str, fix_preview: str) -> None:
        results.append(
            {
                "rule_id": rule_id,
                "label": label,
                "status": status,
                "evidence": evidence,
                "fix_preview": fix_preview,
            }
        )

    unknown_roles = [node["node"] for node in file_nodes if node["role"] == "unknown"]
    missing_paths = [node["node"] for node in file_nodes if not node["path"] or not node["exists"]]
    color_mismatches = [
        node["node"]
        for node in file_nodes
        if node["expected_color_space"] and node["color_space"] and node["color_space"] != node["expected_color_space"]
    ]
    high_res = [
        node["node"]
        for node in file_nodes
        if isinstance(node["resolution"], int) and int(node["resolution"]) > 4096
    ]

    add_result(
        "material-binding",
        "Material Binding",
        "error" if not materials else "pass",
        "materials=%s fileNodes=%s" % (len(materials), len(file_nodes)),
        "Assign materials and connect file nodes before building a delivery manifest." if not materials else "No fix needed.",
    )
    add_result(
        "texture-source-paths",
        "Texture Source Paths",
        "warning" if missing_paths else "pass",
        "missing=%s" % (",".join(missing_paths) or "-"),
        "Relink missing sourceimages paths before launching external packers." if missing_paths else "No fix needed.",
    )
    add_result(
        "texture-role-naming",
        "Texture Role Naming",
        "warning" if unknown_roles else "pass",
        "unknown=%s" % (",".join(unknown_roles) or "-"),
        "Rename or map unknown texture roles before channel packing." if unknown_roles else "No fix needed.",
    )
    add_result(
        "texture-color-space",
        "Texture Color Space",
        "error" if color_mismatches else "pass",
        "mismatch=%s" % (",".join(color_mismatches) or "-"),
        "Correct file node colorSpace tags before packing." if color_mismatches else "No fix needed.",
    )
    add_result(
        "texture-platform-budget",
        "Texture Platform Budget",
        "warning" if high_res else "pass",
        "over4096=%s" % (",".join(high_res) or "-"),
        "Downscale or request platform owner approval for oversized textures." if high_res else "No fix needed.",
    )

    gate = "Blocked" if any(result["status"] == "error" for result in results) else "Review" if any(result["status"] == "warning" for result in results) else "Ready"
    return {
        "schema": "maya-texture-delivery-validation@1.0.0",
        "summary": {
            "gate": gate,
            "pass": sum(1 for result in results if result["status"] == "pass"),
            "warning": sum(1 for result in results if result["status"] == "warning"),
            "error": sum(1 for result in results if result["status"] == "error"),
            "source_count": len(file_nodes),
            "material_count": len(materials),
        },
        "results": results,
    }


def _collect_task_assets(
    cmds: Any,
    names: Optional[List[str]] = None,
    include_all: bool = True,
) -> Dict[str, Any]:
    targets = _resolve_rule_matrix_targets(cmds, names=names, include_all=include_all)
    assets: List[Dict[str, Any]] = []

    for target in targets:
        node = target
        if cmds.nodeType(target) == "mesh":
            parents = cmds.listRelatives(target, parent=True, fullPath=False) or []
            node = parents[0] if parents else target

        shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True, fullPath=False) or []
        mesh_shapes = [shape for shape in shapes if cmds.nodeType(shape) == "mesh"]
        if not mesh_shapes:
            continue

        protocol = _read_protocol_payload(cmds, node, mesh_shapes)
        payload = protocol["payload"]
        payload_budget = payload.get("budget", {}) if isinstance(payload.get("budget"), dict) else {}
        shading_engines: List[str] = []
        materials: List[str] = []
        file_nodes: List[str] = []

        for shape in mesh_shapes:
            shading_engines.extend(cmds.listConnections(shape, type="shadingEngine") or [])

        for shading_engine in sorted(set(shading_engines)):
            surface_nodes = cmds.listConnections(shading_engine + ".surfaceShader", source=True, destination=False) or []
            for material in surface_nodes:
                if material in ("lambert1", "particleCloud1"):
                    continue
                materials.append(material)
                file_nodes.extend(cmds.listConnections(material, type="file") or [])

        try:
            triangles = int(cmds.polyEvaluate(node, triangle=True))
        except Exception:
            triangles = 0

        try:
            visible = bool(cmds.getAttr(node + ".visibility"))
        except Exception:
            visible = True

        budget_triangles = payload_budget.get("triangles")
        budget_over = (
            isinstance(budget_triangles, (int, float))
            and budget_triangles > 0
            and triangles > int(budget_triangles)
        )
        blockers: List[str] = []
        review: List[str] = []

        if protocol["has_protocol"] and not protocol["payload_valid"]:
            blockers.append("invalid protocol JSON")
        if not protocol["has_protocol"]:
            review.append("missing aiToolTaProtocol")
        if not materials:
            review.append("missing material binding")
        if not file_nodes:
            review.append("no texture file nodes")
        if budget_over:
            review.append("triangle budget exceeded")
        if not visible:
            review.append("asset hidden in scene")

        gate = "Blocked" if blockers else "Review" if review else "Ready"
        assets.append(
            {
                "id": "asset-%03d" % (len(assets) + 1),
                "node": node,
                "shapes": mesh_shapes,
                "top_parent": _get_top_parent(cmds, node),
                "lod": payload.get("lod") or _classify_visual_bucket(node),
                "role": payload.get("role") or "unknown",
                "platform": payload.get("platform") or "unknown",
                "triangles": triangles,
                "budget_triangles": budget_triangles,
                "material_count": len(set(materials)),
                "texture_count": len(set(file_nodes)),
                "shading_engines": sorted(set(shading_engines)),
                "materials": sorted(set(materials)),
                "file_nodes": sorted(set(file_nodes)),
                "has_protocol": protocol["has_protocol"],
                "payload_valid": protocol["payload_valid"],
                "protocol_carrier": protocol["carrier"],
                "visible": visible,
                "gate": gate,
                "blockers": blockers,
                "review": review,
            }
        )

    summary = {
        "asset_count": len(assets),
        "ready": sum(1 for asset in assets if asset["gate"] == "Ready"),
        "review": sum(1 for asset in assets if asset["gate"] == "Review"),
        "blocked": sum(1 for asset in assets if asset["gate"] == "Blocked"),
    }
    summary["gate"] = "Blocked" if summary["blocked"] else "Review" if summary["review"] or not assets else "Ready"
    return {
        "schema": "maya-task-orchestrator-discovery@1.0.0",
        "assets": assets,
        "summary": summary,
    }


def _build_task_queue_from_discovery(discovery: Dict[str, Any]) -> Dict[str, Any]:
    tasks: List[Dict[str, Any]] = []

    def add_task(
        asset: Dict[str, Any],
        suffix: str,
        label: str,
        phase: str,
        status: str,
        command: str,
        evidence: str,
        depends_on: Optional[List[str]] = None,
    ) -> None:
        task_id = "%s:%s" % (suffix, asset["node"])
        tasks.append(
            {
                "id": task_id,
                "asset_id": asset["id"],
                "asset": asset["node"],
                "label": label,
                "phase": phase,
                "status": status,
                "command": command,
                "evidence": evidence,
                "depends_on": depends_on or [],
                "mutation_allowed": False,
            }
        )

    for asset in discovery["assets"]:
        protocol_status = "blocked" if asset["has_protocol"] and not asset["payload_valid"] else (
            "done" if asset["has_protocol"] else "review"
        )
        material_status = "done" if asset["material_count"] > 0 else "review"
        texture_status = "done" if asset["texture_count"] > 0 else "review"
        visual_status = "done" if asset["shapes"] and asset["visible"] else "review"
        publish_status = "queued" if asset["gate"] == "Ready" else "review" if asset["gate"] == "Review" else "blocked"

        add_task(
            asset,
            "protocol",
            "Collect Protocol Payload",
            "collect",
            protocol_status,
            "api.asset_inspect_protocol(names=[%s])" % asset["node"],
            "protocol carrier=%s" % (asset["protocol_carrier"] or "-"),
        )
        add_task(
            asset,
            "material",
            "Validate Material Binding",
            "validate",
            material_status,
            "api.rule_matrix_validate_scene(names=[%s])" % asset["node"],
            "materials=%s shadingEngines=%s" % (asset["material_count"], len(asset["shading_engines"])),
            depends_on=["protocol:%s" % asset["node"]],
        )
        add_task(
            asset,
            "texture",
            "Validate Texture Delivery",
            "validate",
            texture_status,
            "api.texture_delivery_validate_scene(include_all=True)",
            "fileNodes=%s" % asset["texture_count"],
            depends_on=["material:%s" % asset["node"]],
        )
        add_task(
            asset,
            "visual",
            "Build Visual Review Manifest",
            "review",
            visual_status,
            "api.visual_review_build_pass_manifest(names=[%s])" % asset["node"],
            "visible=%s shapes=%s" % (asset["visible"], len(asset["shapes"])),
            depends_on=["material:%s" % asset["node"]],
        )
        add_task(
            asset,
            "publish",
            "Export Evidence Packet",
            "extract",
            publish_status,
            "api.task_orchestrator_export_report(names=[%s])" % asset["node"],
            "assetGate=%s review=%s blockers=%s" % (
                asset["gate"],
                ",".join(asset["review"]) or "-",
                ",".join(asset["blockers"]) or "-",
            ),
            depends_on=[
                "protocol:%s" % asset["node"],
                "material:%s" % asset["node"],
                "texture:%s" % asset["node"],
                "visual:%s" % asset["node"],
            ],
        )

    summary = {
        "total": len(tasks),
        "done": sum(1 for task in tasks if task["status"] == "done"),
        "queued": sum(1 for task in tasks if task["status"] == "queued"),
        "review": sum(1 for task in tasks if task["status"] == "review"),
        "blocked": sum(1 for task in tasks if task["status"] == "blocked"),
    }
    summary["gate"] = "Blocked" if summary["blocked"] else "Review" if summary["review"] else "Ready"
    return {
        "schema": "maya-task-orchestrator-queue@1.0.0",
        "summary": summary,
        "tasks": tasks,
    }


def _dry_run_task_queue(queue: Dict[str, Any], discovery: Dict[str, Any]) -> Dict[str, Any]:
    events: List[Dict[str, Any]] = []
    receipts: List[Dict[str, Any]] = []

    for index, task in enumerate(queue["tasks"], start=1):
        result_status = {
            "done": "done",
            "queued": "done",
            "review": "review",
            "blocked": "blocked",
        }.get(task["status"], "review")
        events.append(
            {
                "id": "event-%03d" % index,
                "task_id": task["id"],
                "asset": task["asset"],
                "phase": task["phase"],
                "status": result_status,
                "duration_ms": 12 + index * 3,
                "evidence": task["evidence"],
                "command": task["command"],
                "mutation_allowed": False,
            }
        )

    for asset in discovery["assets"]:
        asset_events = [event for event in events if event["asset"] == asset["node"]]
        state = "blocked" if any(event["status"] == "blocked" for event in asset_events) else (
            "held_for_review" if any(event["status"] == "review" for event in asset_events) else "accepted"
        )
        receipts.append(
            {
                "id": "receipt:%s" % asset["node"],
                "asset": asset["node"],
                "state": state,
                "gate": "Blocked" if state == "blocked" else "Review" if state == "held_for_review" else "Ready",
                "evidence_count": len(asset_events),
                "next_action": (
                    "Fix blocked task before publish."
                    if state == "blocked"
                    else "TA review required before publish."
                    if state == "held_for_review"
                    else "Eligible for evidence packet export."
                ),
            }
        )

    summary = {
        "events": len(events),
        "done": sum(1 for event in events if event["status"] == "done"),
        "review": sum(1 for event in events if event["status"] == "review"),
        "blocked": sum(1 for event in events if event["status"] == "blocked"),
    }
    summary["gate"] = "Blocked" if summary["blocked"] else "Review" if summary["review"] else "Ready"
    return {
        "schema": "maya-task-orchestrator-dry-run@1.0.0",
        "summary": summary,
        "events": events,
        "receipts": receipts,
    }


class MayaPortfolioApi:
    """Methods exposed to JavaScript as auroraview.api.*."""

    def environment_status(self) -> Dict[str, Any]:
        status: Dict[str, Any] = {
            "ok": True,
            "paths": paths_report(),
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        try:
            import auroraview  # type: ignore

            status["auroraview_version"] = getattr(auroraview, "__version__", "unknown")
            status["auroraview_has_qt"] = getattr(auroraview, "_HAS_QT", None)
            status["auroraview_core_error"] = getattr(auroraview, "_CORE_IMPORT_ERROR", None)
        except Exception as exc:
            status["auroraview_error"] = str(exc)

        try:
            cmds = _maya_cmds()
            status["maya"] = {
                "version": cmds.about(version=True),
                "api_version": cmds.about(apiVersion=True),
                "scene": cmds.file(q=True, sceneName=True) or "Untitled",
                "modified": cmds.file(q=True, modified=True),
            }
        except Exception as exc:
            status["maya_error"] = str(exc)

        return status

    def scene_get_selection(self) -> Dict[str, Any]:
        cmds = _maya_cmds()
        selection = cmds.ls(selection=True, long=False) or []
        return {"ok": True, "selection": selection, "count": len(selection)}

    def scene_create_protocol_fixture(self, name: str = "ai_tool_ta_fixture") -> Dict[str, Any]:
        cmds = _maya_cmds()
        root = cmds.group(empty=True, name=name + "#")
        nodes: List[str] = []

        cube = cmds.polyCube(name="hero_prop_body#")[0]
        cmds.parent(cube, root)
        cmds.setAttr(cube + ".translateX", -1.5)
        nodes.append(cube)

        sphere = cmds.polySphere(name="hero_prop_socket#")[0]
        cmds.parent(sphere, root)
        cmds.setAttr(sphere + ".translateX", 1.5)
        nodes.append(sphere)

        payload = {
            "schema": "asset-protocol@dcc-r9",
            "role": "synthetic_fixture",
            "platform": "pc",
            "lod": "lod0",
            "budget": {"triangles": 12000, "textures": 4},
        }
        self.asset_apply_protocol_payload(payload=payload, names=nodes)
        cmds.select(nodes, replace=True)

        return {"ok": True, "root": root, "nodes": nodes, "payload": payload}

    def asset_apply_protocol_payload(
        self,
        payload: Optional[Dict[str, Any]] = None,
        names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        payload = payload or {
            "schema": "asset-protocol@dcc-r9",
            "role": "selected_asset",
            "platform": "pc",
            "lod": "lod0",
        }
        targets = names or cmds.ls(selection=True, long=False) or []
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        changed: List[Dict[str, str]] = []

        for node in targets:
            if not cmds.objExists(node):
                continue
            if not cmds.attributeQuery(PROTOCOL_ATTR, node=node, exists=True):
                cmds.addAttr(node, longName=PROTOCOL_ATTR, dataType="string")
            cmds.setAttr(node + "." + PROTOCOL_ATTR, encoded, type="string")
            changed.append({"node": node, "attr": PROTOCOL_ATTR})

        return {"ok": True, "changed": changed, "payload": payload}

    def asset_inspect_protocol(self, names: Optional[List[str]] = None) -> Dict[str, Any]:
        cmds = _maya_cmds()
        targets = names or cmds.ls(selection=True, long=False) or []
        rows: List[Dict[str, Any]] = []

        for node in targets:
            row: Dict[str, Any] = {"node": node, "has_protocol": False}
            if cmds.objExists(node) and cmds.attributeQuery(PROTOCOL_ATTR, node=node, exists=True):
                raw = cmds.getAttr(node + "." + PROTOCOL_ATTR)
                row["has_protocol"] = True
                row["raw"] = raw
                try:
                    row["payload"] = json.loads(raw)
                except Exception:
                    row["payload_error"] = "Invalid JSON payload"
            rows.append(row)

        return {"ok": True, "rows": rows, "count": len(rows)}

    def report_export_json(
        self,
        label: str = "maya-bridge-report",
        report: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        artifacts_dir = ensure_artifacts_dir()
        safe_label = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in label)
        path = artifacts_dir / ("%s-%s.json" % (safe_label, time.strftime("%Y%m%d-%H%M%S")))
        payload = report or {
            "environment": self.environment_status(),
            "selection": self.scene_get_selection(),
            "protocol": self.asset_inspect_protocol(),
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "path": str(path), "bytes": Path(path).stat().st_size}

    def scene_transaction_create_fixture(self, name: str = "r19_scene_transaction_guard") -> Dict[str, Any]:
        cmds = _maya_cmds()
        root = cmds.group(empty=True, name=name + "#")
        body = cmds.polyCube(name=name + "_hero_body#")[0]
        obsolete = cmds.spaceLocator(name=name + "_obsolete_proxy#")[0]
        camera, camera_shape = cmds.camera(name=name + "_review_cam#")
        cmds.parent([body, obsolete, camera], root)
        cmds.setAttr(body + ".translateX", -1.25)
        cmds.setAttr(obsolete + ".translateX", 1.25)
        cmds.setAttr(camera + ".translate", 0.0, 3.0, 7.0, type="double3")
        cmds.setAttr(camera + ".rotate", -23.0, 0.0, 0.0, type="double3")
        cmds.setAttr(camera_shape + ".focalLength", 50)
        _ensure_string_attr(cmds, root, SCENE_TRANSACTION_ATTR, "scope_root")
        _ensure_string_attr(cmds, body, SCENE_TRANSACTION_ATTR, "hero_asset")
        _ensure_string_attr(cmds, obsolete, SCENE_TRANSACTION_ATTR, "obsolete_proxy")
        _ensure_string_attr(cmds, camera, SCENE_TRANSACTION_ATTR, "review_camera")
        cmds.currentTime(12)
        cmds.select([body, obsolete], replace=True)
        return {
            "ok": True,
            "schema": "maya-scene-transaction-fixture@0.1.0",
            "root": root,
            "nodes": {
                "body": body,
                "obsolete": obsolete,
                "camera": camera,
                "cameraShape": camera_shape,
            },
            "scope": [root],
        }

    def scene_transaction_capture_state(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = False,
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        state = _capture_transaction_state(cmds, names=names, include_all=include_all)
        return {"ok": True, "state": state}

    def scene_transaction_run_guard(
        self,
        name: str = "r19_scene_transaction_guard",
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        fixture = self.scene_transaction_create_fixture(name=name)
        root = fixture["root"]
        body = fixture["nodes"]["body"]
        obsolete = fixture["nodes"]["obsolete"]
        camera_shape = fixture["nodes"]["cameraShape"]
        before = _capture_transaction_state(cmds, names=[root])

        collision_proxy = cmds.polyCube(name=name + "_collision_proxy#")[0]
        cmds.parent(collision_proxy, root)
        cmds.setAttr(collision_proxy + ".translate", 0.65, 0.0, 0.0, type="double3")
        cmds.setAttr(collision_proxy + ".scale", 0.3, 0.3, 0.3, type="double3")
        _ensure_string_attr(cmds, collision_proxy, SCENE_TRANSACTION_ATTR, "created_collision_proxy")
        cmds.setAttr(body + ".translateX", -0.55)
        cmds.setAttr(body + ".visibility", False)
        cmds.setAttr(camera_shape + ".focalLength", 85)
        cmds.delete(obsolete)
        cmds.currentTime(24)
        cmds.select([body, collision_proxy], replace=True)

        after = _capture_transaction_state(cmds, names=[root])
        diff = _diff_transaction_states(before, after)
        risk_rows = [
            {
                "id": "created-node-risk",
                "severity": "review",
                "count": diff["summary"]["created"],
                "reason": "New scene nodes should be intentional and named before publish.",
            },
            {
                "id": "deleted-node-risk",
                "severity": "review",
                "count": diff["summary"]["deleted"],
                "reason": "Deleted nodes need rollback evidence or owner approval.",
            },
            {
                "id": "modified-node-risk",
                "severity": "review",
                "count": diff["summary"]["modified"],
                "reason": "Attribute changes are grouped as a rollback preview instead of being hidden in tool execution.",
            },
            {
                "id": "context-risk",
                "severity": "review" if diff["summary"]["selectionChanged"] or diff["summary"]["timeChanged"] else "pass",
                "count": int(diff["summary"]["selectionChanged"]) + int(diff["summary"]["timeChanged"]),
                "reason": "Selection and timeline context are part of DCC tool state and must be restored or documented.",
            },
        ]
        receipt = {
            "ok": True,
            "schema": "maya-scene-transaction-guard@0.1.0",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "fixture": fixture,
            "summary": {
                "gate": diff["summary"]["gate"],
                "beforeFingerprint": before["fingerprint"],
                "afterFingerprint": after["fingerprint"],
                "created": diff["summary"]["created"],
                "deleted": diff["summary"]["deleted"],
                "modified": diff["summary"]["modified"],
                "selectionChanged": diff["summary"]["selectionChanged"],
                "timeChanged": diff["summary"]["timeChanged"],
                "rollbackActions": diff["summary"]["rollbackActions"],
                "riskRows": len(risk_rows),
            },
            "before": before,
            "after": after,
            "diff": diff,
            "risk_rows": risk_rows,
            "reviewer_claims": [
                "The transaction guard captures scene state before and after a DCC tool mutation.",
                "Created, deleted, modified, selection and timeline changes are visible as evidence rows.",
                "Rollback is exported as a preview receipt; no production restore or engine write is executed.",
            ],
            "boundary": {
                "mutation": "synthetic_maya_fixture_only",
                "sceneWrites": "public fixture nodes only",
                "engineWrites": 0,
                "externalWrites": 0,
            },
        }
        return receipt

    def scene_transaction_export_receipt(
        self,
        label: str = "r19-scene-transaction-guard",
    ) -> Dict[str, Any]:
        receipt = self.scene_transaction_run_guard(name=label.replace("-", "_"))
        report = {
            "reportVersion": "maya-scene-transaction-guard@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "transactionGuard": receipt,
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def unreal_preset_fact_review_load(
        self,
        label: str = "r18-unreal-preset-fact-review",
    ) -> Dict[str, Any]:
        public_package_dir = PORTFOLIO_ROOT / "public-case-package"
        manifest_path = public_package_dir / "dcc-first-package-manifest.json"
        manifest = _read_json_dict(manifest_path)
        manifest_summary = manifest.get("summary", {}) if isinstance(manifest.get("summary"), dict) else {}
        source_value = manifest_summary.get("unrealPresetFactComparisonArtifact") or manifest.get(
            "unrealPresetFactComparisonArtifact"
        )
        source_path = _resolve_package_path(source_value, PORTFOLIO_ROOT)
        if not source_path or not source_path.exists():
            raise FileNotFoundError("Unreal preset fact comparison artifact is missing from the public package manifest.")

        source_report = _read_json_dict(source_path)
        if not source_report:
            raise ValueError("Unreal preset fact comparison artifact is empty or invalid JSON.")

        source_summary = source_report.get("summary", {}) if isinstance(source_report.get("summary"), dict) else {}
        source_fact_rows = _dict_list(source_report.get("factRows"))
        source_waiver_rows = _dict_list(source_report.get("waiverRows"))
        review_rows: List[Dict[str, Any]] = []
        status_counts: Dict[str, int] = {"matched": 0, "drift": 0, "waived": 0, "blocked": 0}

        for row in source_fact_rows:
            status = str(row.get("status") or "unknown")
            waiver = row.get("waiver") if isinstance(row.get("waiver"), dict) else None
            if status in status_counts:
                status_counts[status] += 1
            review_rows.append(
                {
                    "id": row.get("id"),
                    "asset_id": row.get("assetId"),
                    "preset": row.get("preset"),
                    "fact_id": row.get("factId"),
                    "status": status,
                    "matched": bool(row.get("matched")),
                    "actual": row.get("actual"),
                    "expected": row.get("expected"),
                    "fix_preview": row.get("fixPreview"),
                    "waiver_id": waiver.get("id") if waiver else None,
                    "waiver_owner": waiver.get("owner") if waiver else None,
                    "waiver_expires_on": waiver.get("expiresOn") if waiver else None,
                    "reviewer_action": _preset_fact_reviewer_action(status, bool(waiver)),
                }
            )

        review_rows.sort(
            key=lambda item: (
                {"blocked": 0, "drift": 1, "waived": 2, "matched": 3}.get(str(item["status"]), 9),
                str(item.get("preset") or ""),
                str(item.get("asset_id") or ""),
                str(item.get("fact_id") or ""),
            )
        )
        attention_rows = [row for row in review_rows if row["status"] != "matched"]
        source_claims = source_report.get("reviewerClaims")
        reviewer_claims = source_claims if isinstance(source_claims, list) else []

        return {
            "ok": True,
            "schema": "maya-unreal-preset-fact-review@0.1.0",
            "label": label,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "manifest_path": str(manifest_path),
            "source_artifact": str(source_path),
            "summary": {
                "gate": source_summary.get("gate", "Review"),
                "source_report_version": source_report.get("reportVersion"),
                "source_evidence_level": source_summary.get("sourceEvidenceLevel"),
                "source_l3_status": source_summary.get("sourceL3Status"),
                "preset_count": source_summary.get("presetCount", len(_dict_list(source_report.get("presetSummaries")))),
                "asset_count": source_summary.get("assetCount", len(_dict_list(source_report.get("assetComparisons")))),
                "fact_rows": source_summary.get("factRows", len(review_rows)),
                "matched": status_counts["matched"],
                "drift": status_counts["drift"],
                "waived": status_counts["waived"],
                "blocked": status_counts["blocked"],
                "attention_rows": len(attention_rows),
                "approved_waivers": source_summary.get("approvedWaivers", len(source_waiver_rows)),
                "platform_split": source_summary.get("platformSplit"),
                "review_queue": len(attention_rows),
            },
            "preset_summaries": _dict_list(source_report.get("presetSummaries")),
            "asset_comparisons": _dict_list(source_report.get("assetComparisons")),
            "fact_rows": review_rows,
            "review_queue": attention_rows,
            "waiver_rows": source_waiver_rows,
            "reviewer_claims": reviewer_claims,
            "boundary": {
                "mutation": "read_only_review_projection",
                "sceneWrites": "none",
                "engineWrites": 0,
                "source": "public Unreal fixture artifact",
            },
        }

    def unreal_preset_fact_review_export(
        self,
        label: str = "r18-unreal-preset-fact-review",
    ) -> Dict[str, Any]:
        review = self.unreal_preset_fact_review_load(label=label)
        report = {
            "reportVersion": "maya-unreal-preset-fact-review@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "review": review,
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def rule_matrix_collect_scene(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = False,
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        facts = _collect_rule_matrix_facts(cmds, names=names, include_all=include_all)
        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-rule-matrix-facts@1.0.0",
            "count": len(facts),
            "facts": facts,
        }

    def rule_matrix_validate_scene(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = False,
    ) -> Dict[str, Any]:
        collect = self.rule_matrix_collect_scene(names=names, include_all=include_all)
        facts = collect["facts"]
        results = _validate_rule_matrix_facts(facts)
        summary = _summarize_rule_results(results)
        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-rule-matrix-validation@1.0.0",
            "facts": facts,
            "results": results,
            "summary": summary,
        }

    def rule_matrix_preview_fixes(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = False,
    ) -> Dict[str, Any]:
        validation = self.rule_matrix_validate_scene(names=names, include_all=include_all)
        previews = _preview_rule_matrix_fixes(validation["facts"], validation["results"])
        blocked = [item for item in previews if item["kind"] == "manual_only"]
        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-rule-matrix-fix-preview@1.0.0",
            "summary": {
                "total": len(previews),
                "safe_auto": sum(1 for item in previews if item["kind"] == "safe_auto"),
                "manual_only": len(blocked),
                "gate": "Review" if blocked else validation["summary"]["gate"],
            },
            "facts": validation["facts"],
            "validation": validation["results"],
            "previews": previews,
        }

    def rule_matrix_export_report(
        self,
        label: str = "rule-matrix-dcc-report",
        names: Optional[List[str]] = None,
        include_all: bool = False,
    ) -> Dict[str, Any]:
        validation = self.rule_matrix_validate_scene(names=names, include_all=include_all)
        fixes = _preview_rule_matrix_fixes(validation["facts"], validation["results"])
        report = {
            "reportVersion": "maya-rule-matrix-dcc-report@1.0.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "collect": {
                "schema": "maya-rule-matrix-facts@1.0.0",
                "count": len(validation["facts"]),
                "facts": validation["facts"],
            },
            "validation": {
                "schema": validation["schema"],
                "summary": validation["summary"],
                "results": validation["results"],
            },
            "fixPreview": {
                "schema": "maya-rule-matrix-fix-preview@1.0.0",
                "summary": {
                    "total": len(fixes),
                    "safe_auto": sum(1 for item in fixes if item["kind"] == "safe_auto"),
                    "manual_only": sum(1 for item in fixes if item["kind"] == "manual_only"),
                },
                "previews": fixes,
            },
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def visual_review_create_camera_rig(
        self,
        name: str = "ai_tool_ta_review_rig",
        camera_groups: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        allowed_groups = camera_groups or ["basic", "detail"]
        root = cmds.group(empty=True, name=name + "#")
        created: List[Dict[str, Any]] = []

        for group_name in allowed_groups:
            for camera_name, translate, rotate in VISUAL_CAMERA_GROUPS.get(group_name, []):
                transform, shape = cmds.camera(name=camera_name + "#")
                cmds.parent(transform, root)
                cmds.setAttr(transform + ".translate", *translate, type="double3")
                cmds.setAttr(transform + ".rotate", *rotate, type="double3")
                cmds.setAttr(shape + ".focalLength", 70 if group_name == "detail" else 50)
                _ensure_string_attr(cmds, transform, VISUAL_CAMERA_ATTR, group_name)
                created.append(
                    {
                        "name": transform,
                        "shape": shape,
                        "group": group_name,
                        "translate": translate,
                        "rotate": rotate,
                    }
                )

        if created:
            cmds.select([item["name"] for item in created], replace=True)
        return {
            "ok": True,
            "schema": "maya-visual-review-camera-rig@1.0.0",
            "root": root,
            "created": created,
            "count": len(created),
        }

    def visual_review_build_pass_manifest(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = False,
        camera_groups: Optional[List[str]] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        manifest = _build_visual_pass_manifest(
            cmds,
            names=names,
            include_all=include_all,
            camera_groups=camera_groups,
            width=width,
            height=height,
        )
        return {"ok": True, "adapter": "maya", "manifest": manifest}

    def visual_review_preview_capture(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = False,
        camera_groups: Optional[List[str]] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        manifest = _build_visual_pass_manifest(
            cmds,
            names=names,
            include_all=include_all,
            camera_groups=camera_groups,
            width=width,
            height=height,
        )
        output_dir = ensure_artifacts_dir() / ("visual-review-capture-%s" % time.strftime("%Y%m%d-%H%M%S"))
        capture_rows: List[Dict[str, Any]] = []

        for run in manifest["passes"]:
            for shot in run["shots"]:
                capture_rows.append(
                    {
                        "pass_id": run["id"],
                        "camera": shot["camera"],
                        "status": "planned",
                        "output": str(output_dir / shot["output"]),
                        "note": "Preview only; GUI playblast can write this path in the next R9.4 step.",
                    }
                )

        return {
            "ok": True,
            "schema": "maya-visual-review-capture-preview@1.0.0",
            "output_dir": str(output_dir),
            "manifest": manifest,
            "captures": capture_rows,
            "summary": {
                "planned": len(capture_rows),
                "passes_run": manifest["summary"]["run"],
                "passes_skipped": manifest["summary"]["skipped"],
                "gate": manifest["summary"]["gate"],
            },
        }

    def visual_review_export_report(
        self,
        label: str = "visual-review-dcc-report",
        names: Optional[List[str]] = None,
        include_all: bool = False,
        camera_groups: Optional[List[str]] = None,
        width: int = 1024,
        height: int = 1024,
    ) -> Dict[str, Any]:
        preview = self.visual_review_preview_capture(
            names=names,
            include_all=include_all,
            camera_groups=camera_groups,
            width=width,
            height=height,
        )
        report = {
            "reportVersion": "maya-visual-review-dcc-report@1.0.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "manifest": preview["manifest"],
            "capturePreview": {
                "schema": preview["schema"],
                "outputDir": preview["output_dir"],
                "summary": preview["summary"],
                "captures": preview["captures"],
            },
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def texture_delivery_create_fixture(
        self,
        name: str = "ai_tool_ta_texture_fixture",
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        root = cmds.group(empty=True, name=name + "#")
        mesh = cmds.polyCube(name="WPN_Rifle_LOD0_texture_body#")[0]
        cmds.parent(mesh, root)
        material = cmds.shadingNode("lambert", asShader=True, name="M_AI_Texture_Body#")
        shading_engine = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="SG_AI_Texture_Body#")
        cmds.connectAttr(material + ".outColor", shading_engine + ".surfaceShader", force=True)
        cmds.sets(mesh, edit=True, forceElement=shading_engine)

        source_root = PORTFOLIO_ROOT / "fixtures" / "public_texture_crate" / "sourceimages"
        textures = [
            ("T_Rifle_Body_BC_2048.png", "sRGB", ".color"),
            ("T_Rifle_Body_N_2048.tga", "Raw", ".normalCamera"),
            ("T_Rifle_Body_ORM_2048.tga", "Raw", ".ambientColor"),
        ]
        file_nodes: List[Dict[str, Any]] = []
        for file_name, color_space, target_attr in textures:
            file_node = cmds.shadingNode("file", asTexture=True, name=file_name.replace(".", "_") + "#")
            texture_path = str(source_root / file_name)
            cmds.setAttr(file_node + ".fileTextureName", texture_path, type="string")
            if cmds.objExists(file_node + ".colorSpace"):
                cmds.setAttr(file_node + ".colorSpace", color_space, type="string")
            try:
                cmds.connectAttr(file_node + ".outColor", material + target_attr, force=True)
            except Exception:
                pass
            file_nodes.append({"node": file_node, "file_name": file_name, "color_space": color_space, "path": texture_path})

        cmds.select(mesh, replace=True)
        return {
            "ok": True,
            "schema": "maya-texture-delivery-fixture@1.0.0",
            "root": root,
            "mesh": mesh,
            "material": material,
            "shading_engine": shading_engine,
            "file_nodes": file_nodes,
        }

    def texture_delivery_inspect_scene(self, include_all: bool = True) -> Dict[str, Any]:
        cmds = _maya_cmds()
        inspection = _collect_texture_scene(cmds, include_all=include_all)
        return {"ok": True, "adapter": "maya", "inspection": inspection}

    def texture_delivery_validate_scene(self, include_all: bool = True) -> Dict[str, Any]:
        inspection = self.texture_delivery_inspect_scene(include_all=include_all)["inspection"]
        validation = _validate_texture_scene(inspection)
        return {"ok": True, "adapter": "maya", "inspection": inspection, "validation": validation}

    def texture_delivery_export_manifest(
        self,
        label: str = "texture-delivery-dcc-report",
        include_all: bool = True,
    ) -> Dict[str, Any]:
        validated = self.texture_delivery_validate_scene(include_all=include_all)
        inspection = validated["inspection"]
        validation = validated["validation"]
        manifest_items = [
            {
                "textureName": node["file_name"],
                "sourcePath": node["path"],
                "role": node["role"],
                "colorSpace": node["color_space"],
                "expectedColorSpace": node["expected_color_space"],
                "exists": node["exists"],
                "resolution": node["resolution"],
            }
            for node in inspection["file_nodes"]
        ]
        report = {
            "reportVersion": "maya-texture-delivery-dcc-report@1.0.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "inspection": inspection,
            "validation": validation,
            "manifest": {
                "schema": "maya-texture-delivery-manifest@1.0.0",
                "items": manifest_items,
                "gate": validation["summary"]["gate"],
            },
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def task_orchestrator_create_fixture(
        self,
        name: str = "ai_tool_ta_task_batch",
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        root = cmds.group(empty=True, name=name + "#")
        ready_mesh = cmds.polyCube(name="BATCH_Crate_LOD0_ready#")[0]
        review_mesh = cmds.polySphere(name="BATCH_Vehicle_DT_review#")[0]
        cmds.parent(ready_mesh, root)
        cmds.parent(review_mesh, root)
        cmds.setAttr(ready_mesh + ".translateX", -1.4)
        cmds.setAttr(review_mesh + ".translateX", 1.4)

        material = cmds.shadingNode("lambert", asShader=True, name="M_Batch_Crate_Body#")
        shading_engine = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="SG_Batch_Crate_Body#")
        cmds.connectAttr(material + ".outColor", shading_engine + ".surfaceShader", force=True)
        cmds.sets(ready_mesh, edit=True, forceElement=shading_engine)
        file_node = cmds.shadingNode("file", asTexture=True, name="T_Batch_Crate_BC_2048_png#")
        texture_path = str(
            PORTFOLIO_ROOT / "fixtures" / "public_texture_crate" / "sourceimages" / "T_Batch_Crate_BC_2048.png"
        )
        cmds.setAttr(file_node + ".fileTextureName", texture_path, type="string")
        if cmds.objExists(file_node + ".colorSpace"):
            cmds.setAttr(file_node + ".colorSpace", "sRGB", type="string")
        try:
            cmds.connectAttr(file_node + ".outColor", material + ".color", force=True)
        except Exception:
            pass

        ready_payload = {
            "schema": EXPECTED_PROTOCOL_SCHEMA,
            "role": "batch_ready_asset",
            "platform": "pc",
            "lod": "lod0",
            "budget": {"triangles": 12000, "textures": 4},
        }
        self.asset_apply_protocol_payload(payload=ready_payload, names=[ready_mesh])
        cmds.select([ready_mesh, review_mesh], replace=True)

        return {
            "ok": True,
            "schema": "maya-task-orchestrator-fixture@1.0.0",
            "root": root,
            "nodes": [ready_mesh, review_mesh],
            "ready_payload": ready_payload,
            "material": material,
            "shading_engine": shading_engine,
            "file_node": file_node,
            "texture_path": texture_path,
            "notes": [
                "ready mesh has protocol, material and file node",
                "review mesh intentionally lacks protocol, material and texture binding",
            ],
        }

    def task_orchestrator_discover_scene(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        discovery = _collect_task_assets(cmds, names=names, include_all=include_all)
        return {"ok": True, "adapter": "maya", "discovery": discovery}

    def task_orchestrator_build_queue(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        discovery = self.task_orchestrator_discover_scene(names=names, include_all=include_all)["discovery"]
        queue = _build_task_queue_from_discovery(discovery)
        return {"ok": True, "adapter": "maya", "discovery": discovery, "queue": queue}

    def task_orchestrator_run_dry_run(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        built = self.task_orchestrator_build_queue(names=names, include_all=include_all)
        dry_run = _dry_run_task_queue(built["queue"], built["discovery"])
        return {
            "ok": True,
            "adapter": "maya",
            "discovery": built["discovery"],
            "queue": built["queue"],
            "dry_run": dry_run,
        }

    def task_orchestrator_export_report(
        self,
        label: str = "task-orchestrator-dcc-report",
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        dry_run = self.task_orchestrator_run_dry_run(names=names, include_all=include_all)
        report = {
            "reportVersion": "maya-task-orchestrator-dcc-report@1.0.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "discovery": dry_run["discovery"],
            "queue": dry_run["queue"],
            "dryRun": dry_run["dry_run"],
            "boundary": {
                "mutation": "dry_run_only",
                "sceneWrites": 0,
                "nextIntegration": "replace dry-run command strings with real module adapters",
            },
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def asset_handoff_create_fixture(
        self,
        name: str = "ai_tool_ta_asset_handoff",
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        root = cmds.group(empty=True, name=name + "#")
        ready_mesh = cmds.polyCube(name="AH_Crate_LOD0_publish_ready#")[0]
        review_mesh = cmds.polySphere(name="AH_Vehicle_DT_needs_texture_review#")[0]
        cmds.parent(ready_mesh, root)
        cmds.parent(review_mesh, root)
        cmds.setAttr(ready_mesh + ".translateX", -1.6)
        cmds.setAttr(review_mesh + ".translateX", 1.6)

        material = cmds.shadingNode("lambert", asShader=True, name="M_AH_Crate_Body#")
        shading_engine = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="SG_AH_Crate_Body#")
        cmds.connectAttr(material + ".outColor", shading_engine + ".surfaceShader", force=True)
        cmds.sets(ready_mesh, edit=True, forceElement=shading_engine)

        file_node = cmds.shadingNode("file", asTexture=True, name="T_AH_Crate_BC_2048_png#")
        texture_path = str(
            PORTFOLIO_ROOT / "fixtures" / "public_texture_crate" / "sourceimages" / "T_AH_Crate_BC_2048.png"
        )
        cmds.setAttr(file_node + ".fileTextureName", texture_path, type="string")
        if cmds.objExists(file_node + ".colorSpace"):
            cmds.setAttr(file_node + ".colorSpace", "sRGB", type="string")
        try:
            cmds.connectAttr(file_node + ".outColor", material + ".color", force=True)
        except Exception:
            pass

        ready_payload = {
            "schema": EXPECTED_PROTOCOL_SCHEMA,
            "role": "handoff_publish_ready",
            "platform": "pc",
            "lod": "lod0",
            "collision": "simple",
            "budget": {"triangles": 12000, "textures": 4},
            "evidence": {"source": "r10.3 asset handoff gate"},
        }
        review_payload = {
            "schema": EXPECTED_PROTOCOL_SCHEMA,
            "role": "handoff_review_asset",
            "platform": "pc",
            "lod": "dt",
            "collision": "simple",
            "budget": {"triangles": 8000, "textures": 2},
            "evidence": {"source": "r10.3 asset handoff gate", "reviewReason": "material and texture binding intentionally absent"},
        }
        self.asset_apply_protocol_payload(payload=ready_payload, names=[ready_mesh])
        self.asset_apply_protocol_payload(payload=review_payload, names=[review_mesh])
        camera_rig = self.visual_review_create_camera_rig(name=name + "_review_rig")
        cmds.select([ready_mesh, review_mesh], replace=True)

        return {
            "ok": True,
            "schema": "maya-asset-handoff-fixture@0.1.0",
            "root": root,
            "nodes": [ready_mesh, review_mesh],
            "ready_node": ready_mesh,
            "review_node": review_mesh,
            "material": material,
            "shading_engine": shading_engine,
            "file_node": file_node,
            "texture_path": texture_path,
            "camera_rig": {"root": camera_rig.get("root"), "count": camera_rig.get("count")},
            "notes": [
                "ready node has protocol, material, file node, collision and LOD evidence",
                "review node has valid protocol but intentionally lacks material and texture evidence",
            ],
        }

    def asset_handoff_collect(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        cmds = _maya_cmds()
        discovery = self.task_orchestrator_discover_scene(names=names, include_all=include_all)["discovery"]
        asset_nodes = [asset["node"] for asset in discovery["assets"]]

        if asset_nodes:
            rule_validation = self.rule_matrix_validate_scene(names=asset_nodes, include_all=False)
            rule_fixes = self.rule_matrix_preview_fixes(names=asset_nodes, include_all=False)
            visual_manifest = self.visual_review_build_pass_manifest(names=asset_nodes, include_all=False)["manifest"]
        else:
            rule_results = _validate_rule_matrix_facts([])
            rule_validation = {
                "ok": True,
                "adapter": "maya",
                "schema": "maya-rule-matrix-validation@1.0.0",
                "facts": [],
                "results": rule_results,
                "summary": _summarize_rule_results(rule_results),
            }
            rule_fixes = {
                "ok": True,
                "adapter": "maya",
                "schema": "maya-rule-matrix-fix-preview@1.0.0",
                "summary": {"total": 0, "safe_auto": 0, "manual_only": 0, "gate": "Blocked"},
                "facts": [],
                "validation": rule_results,
                "previews": [],
            }
            visual_manifest = _build_visual_pass_manifest(cmds, names=["__missing_asset__"], include_all=False)

        texture_validation = self.texture_delivery_validate_scene(include_all=True)
        queue = _build_task_queue_from_discovery(discovery)
        dry_run = _dry_run_task_queue(queue, discovery)

        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-asset-handoff-collect@0.1.0",
            "assets": discovery["assets"],
            "discovery": discovery,
            "protocol": self.asset_inspect_protocol(names=asset_nodes),
            "ruleMatrix": {
                "summary": rule_validation["summary"],
                "results": rule_validation["results"],
                "fixPreview": rule_fixes["summary"],
                "previews": rule_fixes["previews"],
            },
            "textureDelivery": {
                "inspection": texture_validation["inspection"],
                "validation": texture_validation["validation"],
            },
            "visualReview": {
                "manifest": visual_manifest,
                "summary": visual_manifest["summary"],
            },
            "taskQueue": {
                "queue": queue,
                "dryRun": dry_run,
            },
            "summary": {
                "asset_count": discovery["summary"]["asset_count"],
                "ready": discovery["summary"]["ready"],
                "review": discovery["summary"]["review"],
                "blocked": discovery["summary"]["blocked"],
                "rule_gate": rule_validation["summary"]["gate"],
                "texture_gate": texture_validation["validation"]["summary"]["gate"],
                "visual_gate": visual_manifest["summary"]["gate"],
                "queue_gate": queue["summary"]["gate"],
            },
        }

    def asset_handoff_evaluate_gate(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        collected = self.asset_handoff_collect(names=names, include_all=include_all)
        rule_results = collected["ruleMatrix"]["results"]
        queue_tasks = collected["taskQueue"]["queue"]["tasks"]
        receipts = collected["taskQueue"]["dryRun"]["receipts"]
        asset_rows: List[Dict[str, Any]] = []

        for asset in collected["assets"]:
            node = asset["node"]
            node_rule_results = [result for result in rule_results if node in result.get("nodes", [])]
            node_tasks = [task for task in queue_tasks if task["asset"] == node]
            receipt = next((item for item in receipts if item["asset"] == node), None)
            blockers = list(asset["blockers"])
            review = list(asset["review"])

            for result in node_rule_results:
                if result["status"] == "error":
                    blockers.append(result["message"])
                elif result["status"] in ("warning", "skipped"):
                    review.append(result["message"])

            blockers = sorted(set(blockers))
            review = sorted(set(review))
            gate = "Blocked" if blockers else "Review" if review else "Ready"
            asset_rows.append(
                {
                    "asset_id": asset["id"],
                    "node": node,
                    "gate": gate,
                    "role": asset["role"],
                    "lod": asset["lod"],
                    "platform": asset["platform"],
                    "triangles": asset["triangles"],
                    "protocol": {
                        "has_protocol": asset["has_protocol"],
                        "payload_valid": asset["payload_valid"],
                        "carrier": asset["protocol_carrier"],
                    },
                    "materials": asset["material_count"],
                    "textures": asset["texture_count"],
                    "rule_results": len(node_rule_results),
                    "queue_tasks": len(node_tasks),
                    "receipt_state": receipt.get("state") if receipt else None,
                    "blockers": blockers,
                    "review": review,
                    "evidence": [
                        "protocol" if asset["has_protocol"] else "protocol_missing",
                        "rule_matrix:%s" % len(node_rule_results),
                        "material:%s" % asset["material_count"],
                        "texture:%s" % asset["texture_count"],
                        "queue:%s" % len(node_tasks),
                    ],
                }
            )

        summary = {
            "asset_count": len(asset_rows),
            "ready": sum(1 for asset in asset_rows if asset["gate"] == "Ready"),
            "review": sum(1 for asset in asset_rows if asset["gate"] == "Review"),
            "blocked": sum(1 for asset in asset_rows if asset["gate"] == "Blocked"),
        }
        summary["gate"] = "Blocked" if summary["blocked"] else "Review" if summary["review"] or not asset_rows else "Ready"

        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-asset-handoff-gate-evaluation@0.1.0",
            "summary": summary,
            "assets": asset_rows,
            "collect": collected,
            "policy": {
                "ready": "protocol + material + texture + rule + queue evidence are present",
                "review": "deterministic checks found missing handoff evidence but no invalid payload blocker",
                "blocked": "invalid protocol JSON or blocker rule prevents handoff packet promotion",
            },
        }

    def asset_handoff_preview_actions(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        evaluation = self.asset_handoff_evaluate_gate(names=names, include_all=include_all)
        actions: List[Dict[str, Any]] = []

        for asset in evaluation["assets"]:
            if asset["gate"] == "Ready":
                actions.append(
                    {
                        "id": "handoff-%s-export" % asset["asset_id"],
                        "asset": asset["node"],
                        "kind": "safe_auto",
                        "label": "Export handoff sidecar",
                        "phase": "extract",
                        "preview": "Write protocol, rule, texture, visual, queue evidence into the handoff packet.",
                    }
                )
                continue

            for reason in asset["blockers"] or asset["review"]:
                actions.append(
                    {
                        "id": "handoff-%s-%03d" % (asset["asset_id"], len(actions) + 1),
                        "asset": asset["node"],
                        "kind": "manual_only" if asset["gate"] == "Review" else "blocked",
                        "label": "Resolve handoff evidence",
                        "phase": "validate",
                        "preview": reason,
                    }
                )

        actions.append(
            {
                "id": "handoff-packet-export",
                "asset": "<batch>",
                "kind": "safe_auto",
                "label": "Export batch handoff packet",
                "phase": "extract",
                "preview": "Export all asset gates, evidence summaries, actions, receipts and residual risk as JSON.",
            }
        )

        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-asset-handoff-action-preview@0.1.0",
            "summary": {
                "total": len(actions),
                "safe_auto": sum(1 for item in actions if item["kind"] == "safe_auto"),
                "manual_only": sum(1 for item in actions if item["kind"] == "manual_only"),
                "blocked": sum(1 for item in actions if item["kind"] == "blocked"),
                "gate": evaluation["summary"]["gate"],
            },
            "evaluation": evaluation,
            "actions": actions,
        }

    def asset_handoff_build_decision_packet(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        preview = self.asset_handoff_preview_actions(names=names, include_all=include_all)
        evaluation = preview["evaluation"]
        repair_preview: List[Dict[str, Any]] = []
        owner_dispositions: List[Dict[str, Any]] = []
        engine_handoff: List[Dict[str, Any]] = []

        def classify_repair(reason: str) -> Dict[str, str]:
            lower = reason.lower()
            if "texture" in lower or "file node" in lower:
                return {
                    "repair_type": "texture_binding",
                    "preview_command": "Attach validated file texture nodes or add an owner waiver before engine import.",
                }
            if "material" in lower or "shading" in lower:
                return {
                    "repair_type": "material_binding",
                    "preview_command": "Bind an approved material/shadingEngine and rerun handoff evaluation.",
                }
            if "collision" in lower:
                return {
                    "repair_type": "collision_contract",
                    "preview_command": "Author collision geometry or attach gameplay owner approval.",
                }
            if "protocol" in lower or "payload" in lower:
                return {
                    "repair_type": "protocol_payload",
                    "preview_command": "Rewrite aiToolTaProtocol with the expected schema and required fields.",
                }
            return {
                "repair_type": "handoff_review",
                "preview_command": "Route the asset to TA review with this evidence attached.",
            }

        for asset in evaluation["assets"]:
            reasons = list(asset["blockers"]) + list(asset["review"])
            gate = asset["gate"]
            owner = "TA"
            if any("texture" in reason.lower() or "material" in reason.lower() for reason in reasons):
                owner = "Material Owner"
            elif any("collision" in reason.lower() for reason in reasons):
                owner = "Gameplay Owner"

            if gate == "Ready":
                repair_preview.append(
                    {
                        "id": "repair-%s-export-sidecar" % asset["asset_id"],
                        "asset": asset["node"],
                        "kind": "safe_auto",
                        "repair_type": "sidecar_export",
                        "mutation_allowed": False,
                        "preview_command": "Export engine handoff sidecar from validated DCC evidence.",
                        "risk": "No repair required.",
                    }
                )
                owner_dispositions.append(
                    {
                        "id": "disposition-%s" % asset["asset_id"],
                        "asset": asset["node"],
                        "owner": owner,
                        "state": "accepted",
                        "requires_owner": False,
                        "decision": "promote_to_engine_handoff",
                        "reason": "All required protocol, rule, texture, visual and queue evidence is present.",
                    }
                )
                engine_handoff.append(
                    {
                        "id": "engine-%s" % asset["asset_id"],
                        "asset": asset["node"],
                        "state": "ready_for_import",
                        "intent": "create_engine_import_manifest",
                        "engine_path": "/Game/AI_Tool_TA/%s" % asset["asset_id"],
                        "payload_preview": {
                            "asset_id": asset["asset_id"],
                            "role": asset["role"],
                            "lod": asset["lod"],
                            "platform": asset["platform"],
                            "protocol_carrier": asset["protocol"]["carrier"],
                            "source_gate": gate,
                        },
                    }
                )
                continue

            disposition_state = "owner_required" if gate == "Review" else "blocked"
            owner_dispositions.append(
                {
                    "id": "disposition-%s" % asset["asset_id"],
                    "asset": asset["node"],
                    "owner": owner,
                    "state": disposition_state,
                    "requires_owner": True,
                    "decision": "hold_engine_handoff",
                    "reason": reasons[0] if reasons else "No promotable handoff evidence.",
                }
            )

            for index, reason in enumerate(reasons or ["Unresolved handoff evidence"], start=1):
                repair = classify_repair(reason)
                repair_preview.append(
                    {
                        "id": "repair-%s-%02d" % (asset["asset_id"], index),
                        "asset": asset["node"],
                        "kind": "manual_only" if gate == "Review" else "blocked",
                        "repair_type": repair["repair_type"],
                        "mutation_allowed": False,
                        "preview_command": repair["preview_command"],
                        "risk": reason,
                    }
                )

            engine_handoff.append(
                {
                    "id": "engine-%s" % asset["asset_id"],
                    "asset": asset["node"],
                    "state": "held_for_review" if gate == "Review" else "blocked",
                    "intent": "skip_engine_import_until_disposition",
                    "engine_path": None,
                    "payload_preview": {
                        "asset_id": asset["asset_id"],
                        "role": asset["role"],
                        "lod": asset["lod"],
                        "platform": asset["platform"],
                        "source_gate": gate,
                        "hold_reason": reasons[0] if reasons else "No promotable handoff evidence.",
                    },
                }
            )

        summary = {
            "gate": evaluation["summary"]["gate"],
            "asset_count": evaluation["summary"]["asset_count"],
            "ready": evaluation["summary"]["ready"],
            "review": evaluation["summary"]["review"],
            "blocked": evaluation["summary"]["blocked"],
            "repair_action_count": len(repair_preview),
            "safe_auto": sum(1 for item in repair_preview if item["kind"] == "safe_auto"),
            "manual_only": sum(1 for item in repair_preview if item["kind"] == "manual_only"),
            "blocked_actions": sum(1 for item in repair_preview if item["kind"] == "blocked"),
            "owner_dispositions": len(owner_dispositions),
            "owner_required": sum(1 for item in owner_dispositions if item["requires_owner"]),
            "engine_ready": sum(1 for item in engine_handoff if item["state"] == "ready_for_import"),
            "engine_held": sum(1 for item in engine_handoff if item["state"] != "ready_for_import"),
        }

        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-asset-handoff-decision-packet@0.1.0",
            "summary": summary,
            "evaluation": evaluation,
            "repairPreview": repair_preview,
            "ownerDispositions": owner_dispositions,
            "engineHandoff": engine_handoff,
            "policy": {
                "scene_mutation": "none",
                "owner_authority": "Review and blocked rows need explicit owner disposition before engine handoff.",
                "engine_boundary": "Engine handoff rows are import intents only; no Unreal or engine write is executed.",
            },
        }

    def asset_handoff_export_decision_packet(
        self,
        label: str = "asset-handoff-decision-packet",
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        source_packet = self.asset_handoff_export_packet(
            label=label + "-source",
            names=names,
            include_all=include_all,
        )
        decision_packet = self.asset_handoff_build_decision_packet(
            names=names,
            include_all=include_all,
        )
        report = {
            "reportVersion": "maya-asset-handoff-decision-packet@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "summary": decision_packet["summary"],
            "sourcePacket": {
                "path": source_packet["path"],
                "bytes": source_packet["bytes"],
                "reportVersion": source_packet["report"]["reportVersion"],
                "summary": source_packet["report"]["summary"],
            },
            "decisionPacket": decision_packet,
            "boundary": {
                "mutation": "preview_and_packet_export_only",
                "sceneWrites": "source fixture creation only when caller asks for fixture",
                "engineWrites": 0,
                "ownerAuthority": "Owner disposition is represented as evidence, not auto-approval.",
            },
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def engine_handoff_build_preflight_packet(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
        platform_preset: str = "pc",
    ) -> Dict[str, Any]:
        decision_packet = self.asset_handoff_build_decision_packet(names=names, include_all=include_all)
        preset_key = (platform_preset or "pc").strip().lower()
        presets = {
            "pc": {
                "id": "pc",
                "label": "PC Unreal Import",
                "engine": "Unreal",
                "path_prefix": "/Game/AI_Tool_TA/",
                "platform": "pc",
                "allowed_lods": ["lod0"],
                "max_triangles": 12000,
                "min_textures": 1,
                "max_textures": 4,
                "requires_receipt": "accepted",
            },
            "mobile": {
                "id": "mobile",
                "label": "Mobile Preview Import",
                "engine": "Unreal",
                "path_prefix": "/Game/AI_Tool_TA/Mobile/",
                "platform": "mobile",
                "allowed_lods": ["lod0", "dt"],
                "max_triangles": 8000,
                "min_textures": 1,
                "max_textures": 2,
                "requires_receipt": "accepted",
            },
        }
        preset = presets.get(preset_key, presets["pc"])
        assets_by_node = {asset["node"]: asset for asset in decision_packet["evaluation"]["assets"]}
        assets_by_id = {asset["asset_id"]: asset for asset in decision_packet["evaluation"]["assets"]}
        preflight_rows: List[Dict[str, Any]] = []
        import_sidecars: List[Dict[str, Any]] = []

        def check_row(check_id: str, label: str, ok: bool, evidence: str, fail_status: str = "blocked") -> Dict[str, str]:
            return {
                "id": check_id,
                "label": label,
                "status": "pass" if ok else fail_status,
                "evidence": evidence,
            }

        for intent in decision_packet["engineHandoff"]:
            payload = intent.get("payload_preview", {})
            asset = assets_by_node.get(intent["asset"]) or assets_by_id.get(payload.get("asset_id"))
            asset_id = payload.get("asset_id") or (asset["asset_id"] if asset else intent["id"].replace("engine-", ""))
            checks: List[Dict[str, str]] = []

            if intent["state"] != "ready_for_import" or not asset:
                checks.append(
                    {
                        "id": "decision-state",
                        "label": "Decision State",
                        "status": "hold",
                        "evidence": "%s / %s" % (intent["state"], payload.get("hold_reason", "owner disposition required")),
                    }
                )
                preflight_rows.append(
                    {
                        "id": "preflight-%s" % asset_id,
                        "asset": intent["asset"],
                        "asset_id": asset_id,
                        "state": "held_for_owner_disposition",
                        "preset": preset["id"],
                        "engine_path": intent["engine_path"],
                        "checks": checks,
                        "import_preview": None,
                        "disposition": "hold_engine_import",
                    }
                )
                continue

            engine_path = intent["engine_path"] or ""
            checks.extend(
                [
                    check_row(
                        "decision-state",
                        "Decision State",
                        intent["state"] == "ready_for_import" and asset["gate"] == "Ready",
                        "intent=%s sourceGate=%s" % (intent["state"], asset["gate"]),
                    ),
                    check_row(
                        "engine-path",
                        "Engine Path",
                        engine_path.startswith(preset["path_prefix"]),
                        "path=%s prefix=%s" % (engine_path or "-", preset["path_prefix"]),
                    ),
                    check_row(
                        "platform-preset",
                        "Platform Preset",
                        asset["platform"] == preset["platform"],
                        "assetPlatform=%s preset=%s" % (asset["platform"], preset["platform"]),
                        fail_status="review",
                    ),
                    check_row(
                        "lod-policy",
                        "LOD Policy",
                        asset["lod"] in preset["allowed_lods"],
                        "lod=%s allowed=%s" % (asset["lod"], ",".join(preset["allowed_lods"])),
                    ),
                    check_row(
                        "triangle-budget",
                        "Triangle Budget",
                        asset["triangles"] <= preset["max_triangles"],
                        "triangles=%s max=%s" % (asset["triangles"], preset["max_triangles"]),
                    ),
                    check_row(
                        "texture-budget",
                        "Texture Budget",
                        preset["min_textures"] <= asset["textures"] <= preset["max_textures"],
                        "textures=%s range=%s-%s" % (asset["textures"], preset["min_textures"], preset["max_textures"]),
                    ),
                    check_row(
                        "protocol-carrier",
                        "Protocol Carrier",
                        bool(asset["protocol"]["payload_valid"]),
                        "carrier=%s" % asset["protocol"]["carrier"],
                    ),
                    check_row(
                        "receipt-state",
                        "Receipt State",
                        asset["receipt_state"] == preset["requires_receipt"],
                        "receipt=%s required=%s" % (asset["receipt_state"], preset["requires_receipt"]),
                        fail_status="review",
                    ),
                ]
            )

            blocked_checks = [item for item in checks if item["status"] == "blocked"]
            review_checks = [item for item in checks if item["status"] == "review"]
            state = "blocked" if blocked_checks else "review" if review_checks else "preflight_ready"
            sidecar = None
            if state == "preflight_ready":
                sidecar = {
                    "id": "engine-sidecar-%s-%s" % (asset_id, preset["id"]),
                    "asset": asset["node"],
                    "engine_path": engine_path,
                    "platform_preset": preset["id"],
                    "mutation_allowed": False,
                    "preview_command": "Create %s import sidecar for %s." % (preset["engine"], engine_path),
                    "payload": {
                        "asset_id": asset_id,
                        "source_node": asset["node"],
                        "role": asset["role"],
                        "lod": asset["lod"],
                        "platform": asset["platform"],
                        "triangles": asset["triangles"],
                        "textures": asset["textures"],
                        "source_gate": asset["gate"],
                        "engine_path": engine_path,
                        "dry_run_only": True,
                    },
                }
                import_sidecars.append(sidecar)

            preflight_rows.append(
                {
                    "id": "preflight-%s" % asset_id,
                    "asset": asset["node"],
                    "asset_id": asset_id,
                    "state": state,
                    "preset": preset["id"],
                    "engine_path": engine_path,
                    "checks": checks,
                    "import_preview": sidecar,
                    "disposition": "create_import_sidecar" if state == "preflight_ready" else "hold_engine_import",
                }
            )

        check_statuses = [check["status"] for row in preflight_rows for check in row["checks"]]
        blocked = sum(1 for row in preflight_rows if row["state"] == "blocked")
        held = sum(1 for row in preflight_rows if row["state"] == "held_for_owner_disposition")
        review = sum(1 for row in preflight_rows if row["state"] == "review")
        ready = sum(1 for row in preflight_rows if row["state"] == "preflight_ready")
        summary = {
            "gate": "Blocked" if blocked else "Review" if held or review else "Ready",
            "asset_count": len(preflight_rows),
            "preflight_ready": ready,
            "held": held,
            "review": review,
            "blocked": blocked,
            "import_sidecars": len(import_sidecars),
            "pass_checks": check_statuses.count("pass"),
            "review_checks": check_statuses.count("review"),
            "hold_checks": check_statuses.count("hold"),
            "blocked_checks": check_statuses.count("blocked"),
            "platform_preset": preset["id"],
        }

        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-engine-handoff-preflight@0.1.0",
            "summary": summary,
            "platformPreset": preset,
            "decisionSummary": decision_packet["summary"],
            "preflightRows": preflight_rows,
            "importSidecars": import_sidecars,
            "policy": {
                "scene_mutation": "none",
                "engine_writes": 0,
                "ready_rule": "Only decision-ready rows with passing preset checks produce import sidecars.",
                "held_rule": "Review or owner-required rows stay visible as held preflight rows.",
            },
        }

    def engine_handoff_export_preflight_packet(
        self,
        label: str = "engine-handoff-preflight",
        names: Optional[List[str]] = None,
        include_all: bool = True,
        platform_preset: str = "pc",
    ) -> Dict[str, Any]:
        source_decision = self.asset_handoff_export_decision_packet(
            label=label + "-decision-source",
            names=names,
            include_all=include_all,
        )
        preflight_packet = self.engine_handoff_build_preflight_packet(
            names=names,
            include_all=include_all,
            platform_preset=platform_preset,
        )
        report = {
            "reportVersion": "maya-engine-handoff-preflight@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "summary": preflight_packet["summary"],
            "sourceDecisionPacket": {
                "path": source_decision["path"],
                "bytes": source_decision["bytes"],
                "reportVersion": source_decision["report"]["reportVersion"],
                "summary": source_decision["report"]["summary"],
            },
            "preflightPacket": preflight_packet,
            "boundary": {
                "mutation": "preflight_and_packet_export_only",
                "sceneWrites": "source fixture creation only when caller asks for fixture",
                "engineWrites": 0,
                "ownerAuthority": "Held rows require owner disposition before engine import sidecar creation.",
            },
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def engine_handoff_build_preset_comparison(
        self,
        names: Optional[List[str]] = None,
        include_all: bool = True,
        platform_presets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        preset_ids = platform_presets or ["pc", "mobile"]
        preflight_packets: List[Dict[str, Any]] = []
        for preset_id in preset_ids:
            preflight_packets.append(
                self.engine_handoff_build_preflight_packet(
                    names=names,
                    include_all=include_all,
                    platform_preset=preset_id,
                )
            )

        rows_by_asset: Dict[str, Dict[str, Any]] = {}
        preset_summaries: List[Dict[str, Any]] = []

        for packet in preflight_packets:
            summary = packet["summary"]
            preset_id = summary["platform_preset"]
            preset_summaries.append(
                {
                    "preset": preset_id,
                    "label": packet["platformPreset"]["label"],
                    "gate": summary["gate"],
                    "preflight_ready": summary["preflight_ready"],
                    "held": summary["held"],
                    "review": summary["review"],
                    "blocked": summary["blocked"],
                    "import_sidecars": summary["import_sidecars"],
                    "pass_checks": summary["pass_checks"],
                    "review_checks": summary["review_checks"],
                    "hold_checks": summary["hold_checks"],
                    "blocked_checks": summary["blocked_checks"],
                }
            )

            for row in packet["preflightRows"]:
                asset_id = row["asset_id"]
                comparison = rows_by_asset.setdefault(
                    asset_id,
                    {
                        "asset_id": asset_id,
                        "asset": row["asset"],
                        "presetStates": {},
                        "presetDispositions": {},
                        "blockingReasons": {},
                    },
                )
                comparison["presetStates"][preset_id] = row["state"]
                comparison["presetDispositions"][preset_id] = row["disposition"]
                failed_checks = [check for check in row["checks"] if check["status"] != "pass"]
                comparison["blockingReasons"][preset_id] = [
                    "%s:%s:%s" % (check["label"], check["status"], check["evidence"]) for check in failed_checks
                ]

        comparison_rows: List[Dict[str, Any]] = []
        for row in rows_by_asset.values():
            states = list(row["presetStates"].values())
            unique_states = sorted(set(states))
            if unique_states == ["held_for_owner_disposition"]:
                disposition = "held_across_presets"
            elif len(unique_states) == 1:
                disposition = "same_state"
            elif "preflight_ready" in unique_states and any(state != "preflight_ready" for state in unique_states):
                disposition = "platform_split"
            else:
                disposition = "held_across_presets"
            row["delta"] = disposition
            comparison_rows.append(row)

        comparison_rows.sort(key=lambda item: item["asset_id"])
        preset_gates = [summary["gate"] for summary in preset_summaries]
        summary = {
            "gate": "Review" if comparison_rows else "Ready",
            "preset_count": len(preset_summaries),
            "asset_count": len(comparison_rows),
            "platform_split": sum(1 for row in comparison_rows if row["delta"] == "platform_split"),
            "same_state": sum(1 for row in comparison_rows if row["delta"] == "same_state"),
            "held_across_presets": sum(1 for row in comparison_rows if row["delta"] == "held_across_presets"),
            "ready_sidecars": sum(item["import_sidecars"] for item in preset_summaries),
            "blocked_presets": sum(1 for gate in preset_gates if gate == "Blocked"),
            "review_presets": sum(1 for gate in preset_gates if gate == "Review"),
            "presets": [summary["preset"] for summary in preset_summaries],
        }

        return {
            "ok": True,
            "adapter": "maya",
            "schema": "maya-engine-handoff-preset-comparison@0.1.0",
            "summary": summary,
            "presetSummaries": preset_summaries,
            "comparisonRows": comparison_rows,
            "preflightPackets": preflight_packets,
            "policy": {
                "scene_mutation": "none",
                "engine_writes": 0,
                "comparison_rule": "Preset comparison explains why the same DCC decision can produce different engine handoff outcomes per platform.",
                "owner_rule": "Owner-held rows remain held across every preset until explicit disposition changes.",
            },
        }

    def engine_handoff_export_preset_comparison(
        self,
        label: str = "engine-handoff-preset-comparison",
        names: Optional[List[str]] = None,
        include_all: bool = True,
        platform_presets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        source_decision = self.asset_handoff_export_decision_packet(
            label=label + "-decision-source",
            names=names,
            include_all=include_all,
        )
        comparison = self.engine_handoff_build_preset_comparison(
            names=names,
            include_all=include_all,
            platform_presets=platform_presets,
        )
        report = {
            "reportVersion": "maya-engine-handoff-preset-comparison@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "summary": comparison["summary"],
            "sourceDecisionPacket": {
                "path": source_decision["path"],
                "bytes": source_decision["bytes"],
                "reportVersion": source_decision["report"]["reportVersion"],
                "summary": source_decision["report"]["summary"],
            },
            "comparisonPacket": comparison,
            "boundary": {
                "mutation": "comparison_and_packet_export_only",
                "sceneWrites": "source fixture creation only when caller asks for fixture",
                "engineWrites": 0,
                "ownerAuthority": "Preset comparison cannot approve owner-held rows.",
            },
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def asset_handoff_export_packet(
        self,
        label: str = "asset-handoff-gate",
        names: Optional[List[str]] = None,
        include_all: bool = True,
    ) -> Dict[str, Any]:
        preview = self.asset_handoff_preview_actions(names=names, include_all=include_all)
        evaluation = preview["evaluation"]
        report = {
            "reportVersion": "maya-asset-handoff-gate@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "summary": evaluation["summary"],
            "assets": evaluation["assets"],
            "collect": evaluation["collect"],
            "actions": preview["actions"],
            "boundary": {
                "mutation": "preview_and_packet_export_only",
                "sceneWrites": "fixture creation writes synthetic demo assets only",
                "ownerAuthority": "Review rows require TA/owner disposition before promotion",
            },
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def showcase_runbook_build_plan(self) -> Dict[str, Any]:
        modules = [
            {
                "id": "asset-protocol",
                "label": "Asset Protocol Workbench",
                "gui_entry": "Right rail Maya Bridge plus Asset Protocol Workbench DCC Evidence",
                "primary_method": "asset_inspect_protocol",
                "proof": "custom attr payload written to Maya nodes and recovered as scene evidence",
            },
            {
                "id": "rule-matrix",
                "label": "Cross-DCC Rule Matrix",
                "gui_entry": "Cross-DCC Rule Matrix / Maya Scene Rule Run",
                "primary_method": "rule_matrix_export_report",
                "proof": "scene facts, validation rows, fix preview and JSON artifact",
            },
            {
                "id": "visual-review",
                "label": "Visual Review Studio",
                "gui_entry": "Visual Review Studio / Maya Capture Setup",
                "primary_method": "visual_review_export_report",
                "proof": "camera rig, pass manifest, capture preview and JSON artifact",
            },
            {
                "id": "texture-delivery",
                "label": "Texture Delivery Console",
                "gui_entry": "Texture Delivery Console / Maya Texture Inspection",
                "primary_method": "texture_delivery_export_manifest",
                "proof": "material/file node inspection, color-space validation and manifest artifact",
            },
            {
                "id": "task-orchestrator",
                "label": "Task Orchestrator",
                "gui_entry": "Task Orchestrator / Maya Batch Queue",
                "primary_method": "task_orchestrator_export_report",
                "proof": "scene asset discovery, dry-run task events, receipts and JSON artifact",
            },
        ]
        showcase_positioning = {
            "thesis": "A Maya-hosted AI Tool TA portfolio that turns one asset handoff into protocol, gate, review, delivery, and batch evidence.",
            "demo_mode": "DCC-first / Maya AuroraView",
            "module_shell_explanation": "The shell is the DCC presentation and evidence orchestration layer; the five modules are business stages in one asset publish chain, and Asset Handoff Gate is the composite gate that proves the chain can be evaluated as a batch.",
        }
        composite_gate = {
            "id": "asset-handoff-gate",
            "label": "Asset Handoff Gate",
            "gui_entry": "Right rail / Asset Handoff Gate",
            "primary_method": "asset_handoff_export_packet",
            "proof": "per-asset gate merges protocol, rule, texture, visual and queue evidence into a publish handoff packet",
            "report_version": "maya-asset-handoff-gate@0.1.0",
            "decision_method": "asset_handoff_export_decision_packet",
            "decision_report_version": "maya-asset-handoff-decision-packet@0.1.0",
            "decision_proof": "repair preview, owner disposition and engine handoff intents are exported without engine writes",
        }
        presentation_route = [
            {
                "id": "01-contract",
                "phase": "Author the handoff contract",
                "module_id": "asset-protocol",
                "business_question": "How does the scene carry gameplay/publish semantics without relying on file naming alone?",
                "operator_action": "Open Asset Protocol Workbench, publish the active payload, then inspect it from Maya Bridge.",
                "core_logic": "Encode role, platform, LOD, collision, and budget into a stable custom attr payload that downstream tools can parse.",
                "evidence_to_show": "Maya node custom attr, inspected protocol rows, DCC evidence JSON.",
                "reviewer_value": "Shows schema ownership and DCC-native metadata strategy.",
            },
            {
                "id": "02-gate",
                "phase": "Run the publish gate",
                "module_id": "rule-matrix",
                "business_question": "Can the tool turn project rules into repeatable DCC facts, failures, and fix previews?",
                "operator_action": "Run Collect Scene, Validate Scene, Preview Fixes, and Export DCC Report.",
                "core_logic": "Collect scene facts, evaluate deterministic rules, separate safe_auto fixes from manual_only decisions.",
                "evidence_to_show": "Rule results, fix preview rows, rule-matrix artifact.",
                "reviewer_value": "Shows production gate design instead of ad hoc checking.",
            },
            {
                "id": "03-review",
                "phase": "Make visual review reproducible",
                "module_id": "visual-review",
                "business_question": "How does subjective art review become a fixed camera/pass contract?",
                "operator_action": "Create the review camera rig, build pass manifest, preview capture, and export review evidence.",
                "core_logic": "Generate canonical cameras and pass rows from the scene so review output can be compared later.",
                "evidence_to_show": "Camera rig nodes, pass manifest, capture preview paths.",
                "reviewer_value": "Shows review standardization and repeatable visual evidence.",
            },
            {
                "id": "04-delivery",
                "phase": "Validate texture delivery",
                "module_id": "texture-delivery",
                "business_question": "Can texture handoff be checked against naming, color space, source path, and budget rules?",
                "operator_action": "Create the texture fixture, inspect file nodes, validate the scene, and export the manifest.",
                "core_logic": "Scan shading networks and file nodes, infer texture roles, compare actual color space/path/budget against policy.",
                "evidence_to_show": "Material/file node rows, validation gates, texture-delivery manifest.",
                "reviewer_value": "Shows the bridge between DCC material graphs and engine-facing delivery constraints.",
            },
            {
                "id": "05-orchestrate",
                "phase": "Package batch handoff evidence",
                "module_id": "task-orchestrator",
                "business_question": "Can many scene assets be turned into a dry-run publish queue with receipts?",
                "operator_action": "Discover scene assets, build the queue, run dry-run, and export the report.",
                "core_logic": "Convert discovered assets into protocol/material/texture/visual/export tasks and produce per-asset receipts.",
                "evidence_to_show": "Queue rows, dry-run events, receipts, orchestrator report.",
                "reviewer_value": "Shows how individual tools become a governed production workflow.",
            },
            {
                "id": "06-composite-gate",
                "phase": "Evaluate the composite handoff gate",
                "module_id": "asset-handoff-gate",
                "business_question": "Can the full asset handoff be judged as a batch instead of five separate demos?",
                "operator_action": "Use Asset Handoff Gate: Fixture, Evaluate Gate, Preview Actions, Export Packet.",
                "core_logic": "Merge protocol, rule, texture, visual and queue evidence into per-asset Ready/Review/Blocked gates.",
                "evidence_to_show": "Handoff asset rows, action preview rows, exported handoff packet.",
                "reviewer_value": "Shows the portfolio has a production workflow, not only individual module proofs.",
            },
            {
                "id": "07-owner-engine-handoff",
                "phase": "Resolve owner and engine handoff",
                "module_id": "asset-handoff-gate",
                "business_question": "Can the handoff decision explain who owns review rows and what would enter engine import?",
                "operator_action": "Use Asset Handoff Gate / Decision Packet after evaluating the batch gate.",
                "core_logic": "Turn Ready/Review asset gates into repair preview rows, owner disposition rows, and engine import intents without writing to engine.",
                "evidence_to_show": "Decision packet repairPreview, ownerDispositions, engineHandoff rows.",
                "reviewer_value": "Shows the TA boundary between deterministic evidence, owner authority, and engine handoff planning.",
            },
        ]
        demo_script = [
            {
                "id": "open-host",
                "segment": "Open Maya host",
                "operator_action": "Run show_portfolio() from Maya Script Editor or shelf.",
                "talk_track": "This is a Maya-hosted toolbench. The browser build is only the embedded UI surface.",
                "evidence_expected": "AuroraView panel opens with Maya Bridge connected.",
            },
            {
                "id": "build-plan",
                "segment": "Build DCC plan",
                "operator_action": "Click DCC Showcase Runbook / Build Plan.",
                "talk_track": "The runbook lists each production problem, its Maya API entry, and the proof artifact.",
                "evidence_expected": "Five module rows appear in the right rail.",
            },
            {
                "id": "run-smoke",
                "segment": "Run synthetic scene smoke",
                "operator_action": "Click Run Smoke or Export Package.",
                "talk_track": "The tool creates public synthetic Maya fixtures, runs all DCC adapters, and writes JSON artifacts.",
                "evidence_expected": "Five module artifacts are generated, with no Blocked module.",
            },
            {
                "id": "inspect-modules",
                "segment": "Inspect module panels",
                "operator_action": "Open each module from the left navigation and inspect its DCC panel.",
                "talk_track": "Each module exposes its own business loop: protocol, rules, visual review, texture delivery, and batch orchestration.",
                "evidence_expected": "Each module shows scene facts, gate rows, output path, and raw JSON.",
            },
            {
                "id": "run-handoff-gate",
                "segment": "Run composite handoff gate",
                "operator_action": "Click Asset Handoff Gate / Fixture, Evaluate Gate, Preview Actions, Export Packet.",
                "talk_track": "The composite gate proves the five module evidence streams can become one asset handoff decision.",
                "evidence_expected": "maya-asset-handoff-gate JSON contains 2 assets, 1 Ready, 1 Review, 0 Blocked.",
            },
            {
                "id": "run-decision-packet",
                "segment": "Export decision packet",
                "operator_action": "Click Asset Handoff Gate / Decision Packet.",
                "talk_track": "The decision packet shows repair previews, owner disposition, and engine handoff intent without approving or writing anything automatically.",
                "evidence_expected": "maya-asset-handoff-decision-packet JSON contains owner disposition rows and engine handoff mock rows.",
            },
            {
                "id": "handoff-package",
                "segment": "Export reviewer package",
                "operator_action": "Use Export Package and open the artifact path.",
                "talk_track": "The final claim is machine-checkable: DCC-backed evidence exists for every module, the composite gate, and the decision layer.",
                "evidence_expected": "maya-dcc-showcase-runbook-package JSON contains plan, smoke, presentation, handoff gate, decision packet, and artifacts.",
            },
        ]
        gui_click_checklist = [
            {"id": "right-rail-runbook", "target": "Right rail / DCC Showcase Runbook", "clicks": ["Build Plan", "Run Smoke", "Export Package"]},
            {"id": "right-rail-handoff-gate", "target": "Right rail / Asset Handoff Gate", "clicks": ["Fixture", "Evaluate Gate", "Preview Actions", "Export Packet", "Decision Packet"]},
            {"id": "asset-protocol-panel", "target": "Asset Protocol Workbench", "clicks": ["Export DCC Evidence"]},
            {"id": "rule-matrix-panel", "target": "Cross-DCC Rule Matrix / Maya Scene Rule Run", "clicks": ["Collect Scene", "Validate Scene", "Preview Fixes", "Export DCC Report"]},
            {"id": "visual-review-panel", "target": "Visual Review Studio / Maya Capture Setup", "clicks": ["Create Rig", "Build Manifest", "Preview Capture", "Export DCC Review"]},
            {"id": "texture-delivery-panel", "target": "Texture Delivery Console / Maya Texture Inspection", "clicks": ["Create Fixture", "Inspect Textures", "Validate Scene", "Export Manifest"]},
            {"id": "task-orchestrator-panel", "target": "Task Orchestrator / Maya Batch Queue", "clicks": ["Create Fixture", "Discover Scene", "Build Queue", "Dry Run", "Export Report"]},
        ]
        return {
            "ok": True,
            "schema": "maya-dcc-showcase-runbook@1.0.0",
            "title": "DCC-first Portfolio Demo Runbook",
            "mode": "maya-auroraview",
            "showcase_positioning": showcase_positioning,
            "modules": modules,
            "composite_gate": composite_gate,
            "presentation_route": presentation_route,
            "demo_script": demo_script,
            "gui_click_checklist": gui_click_checklist,
            "steps": [
                "Open show_portfolio() in Maya.",
                "Use DCC Showcase Runbook in the right rail to build the plan.",
                "Run smoke to create synthetic scene fixtures and execute all module adapters.",
                "Run Asset Handoff Gate to evaluate the composite handoff workflow.",
                "Export the Asset Handoff Decision Packet to inspect owner and engine handoff decisions.",
                "Open each module-specific panel to inspect the same evidence by business domain.",
                "Export package to hand off a single JSON proof bundle.",
            ],
            "mutation_policy": "Smoke creates synthetic demo nodes and JSON artifacts only; production scene mutation remains behind module-specific actions.",
        }

    def showcase_runbook_run_smoke(
        self,
        label: str = "dcc-showcase-runbook-smoke",
    ) -> Dict[str, Any]:
        started_at = time.strftime("%Y-%m-%d %H:%M:%S")
        safe_label = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in label)
        created: List[Dict[str, Any]] = []
        artifacts: List[Dict[str, Any]] = []
        modules: List[Dict[str, Any]] = []

        asset_fixture = self.scene_create_protocol_fixture(name="r9_7_asset_protocol_fixture")
        texture_fixture = self.texture_delivery_create_fixture(name="r9_7_texture_fixture")
        task_fixture = self.task_orchestrator_create_fixture(name="r9_7_task_batch")
        camera_rig = self.visual_review_create_camera_rig(name="r9_7_review_rig")
        rule_targets = [
            node
            for node in (
                list(asset_fixture.get("nodes", []))
                + [texture_fixture.get("mesh")]
                + list(task_fixture.get("nodes", [])[:1])
            )
            if node
        ]
        showcase_protocol_payload = {
            "schema": EXPECTED_PROTOCOL_SCHEMA,
            "role": "showcase_publish_target",
            "platform": "pc",
            "lod": "lod0",
            "collision": "simple",
            "budget": {"triangles": 12000, "textures": 4},
            "evidence": {"source": "r9.7 dcc showcase runbook"},
        }
        self.asset_apply_protocol_payload(payload=showcase_protocol_payload, names=rule_targets)
        created.extend(
            [
                {"kind": "asset_protocol_fixture", "root": asset_fixture.get("root"), "nodes": asset_fixture.get("nodes", [])},
                {"kind": "texture_fixture", "root": texture_fixture.get("root"), "nodes": [texture_fixture.get("mesh")]},
                {"kind": "task_fixture", "root": task_fixture.get("root"), "nodes": task_fixture.get("nodes", [])},
                {"kind": "visual_camera_rig", "root": camera_rig.get("root"), "nodes": [item["name"] for item in camera_rig.get("created", [])]},
            ]
        )

        def append_artifact(module_id: str, exported: Dict[str, Any]) -> None:
            if exported.get("path"):
                artifacts.append(
                    {
                        "module_id": module_id,
                        "path": exported["path"],
                        "bytes": exported.get("bytes"),
                    }
                )

        def append_module(
            module_id: str,
            label_text: str,
            gate: str,
            summary: Dict[str, Any],
            exported: Optional[Dict[str, Any]] = None,
        ) -> None:
            modules.append(
                {
                    "id": module_id,
                    "label": label_text,
                    "gate": gate,
                    "summary": summary,
                    "artifact": exported.get("path") if exported else None,
                }
            )
            if exported:
                append_artifact(module_id, exported)

        protocol_inspect = self.asset_inspect_protocol(names=asset_fixture.get("nodes", []))
        protocol_gate = "Ready" if protocol_inspect.get("count", 0) and all(row.get("has_protocol") for row in protocol_inspect.get("rows", [])) else "Review"
        protocol_report = {
            "reportVersion": "maya-asset-protocol-showcase@1.0.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "fixture": asset_fixture,
            "inspection": protocol_inspect,
            "gate": protocol_gate,
        }
        protocol_export = self.report_export_json(label=safe_label + "-asset-protocol", report=protocol_report)
        append_module(
            "asset-protocol",
            "Asset Protocol Workbench",
            protocol_gate,
            {"nodes": len(asset_fixture.get("nodes", [])), "rows": protocol_inspect.get("count", 0)},
            protocol_export,
        )

        rule_export = self.rule_matrix_export_report(label=safe_label + "-rule-matrix", names=rule_targets)
        rule_summary = rule_export["report"]["validation"]["summary"]
        append_module(
            "rule-matrix",
            "Cross-DCC Rule Matrix",
            rule_summary.get("gate", "Review"),
            {
                "facts": rule_export["report"]["collect"]["count"],
                "results": len(rule_export["report"]["validation"]["results"]),
                "fixes": rule_export["report"]["fixPreview"]["summary"]["total"],
            },
            rule_export,
        )

        visual_export = self.visual_review_export_report(label=safe_label + "-visual-review", include_all=True)
        visual_summary = visual_export["report"]["manifest"]["summary"]
        append_module(
            "visual-review",
            "Visual Review Studio",
            visual_summary.get("gate", "Review"),
            {
                "cameras": len(visual_export["report"]["manifest"]["cameras"]),
                "meshes": visual_export["report"]["manifest"]["mesh_summary"]["total"],
                "images": visual_summary.get("image_count", 0),
            },
            visual_export,
        )

        texture_export = self.texture_delivery_export_manifest(label=safe_label + "-texture-delivery", include_all=True)
        texture_summary = texture_export["report"]["validation"]["summary"]
        append_module(
            "texture-delivery",
            "Texture Delivery Console",
            texture_summary.get("gate", "Review"),
            {
                "sources": texture_summary.get("source_count", 0),
                "materials": texture_summary.get("material_count", 0),
                "results": len(texture_export["report"]["validation"]["results"]),
            },
            texture_export,
        )

        task_export = self.task_orchestrator_export_report(label=safe_label + "-task-orchestrator", include_all=True)
        task_summary = task_export["report"]["dryRun"]["summary"]
        append_module(
            "task-orchestrator",
            "Task Orchestrator",
            task_summary.get("gate", "Review"),
            {
                "assets": task_export["report"]["discovery"]["summary"]["asset_count"],
                "tasks": task_export["report"]["queue"]["summary"]["total"],
                "events": task_summary.get("events", 0),
                "receipts": len(task_export["report"]["dryRun"]["receipts"]),
            },
            task_export,
        )

        gate = "Blocked" if any(item["gate"] == "Blocked" for item in modules) else (
            "Review" if any(item["gate"] == "Review" for item in modules) else "Ready"
        )
        return {
            "ok": True,
            "schema": "maya-dcc-showcase-smoke@1.0.0",
            "started_at": started_at,
            "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "gate": gate,
            "created": created,
            "modules": modules,
            "artifacts": artifacts,
            "summary": {
                "module_count": len(modules),
                "ready": sum(1 for item in modules if item["gate"] == "Ready"),
                "review": sum(1 for item in modules if item["gate"] == "Review"),
                "blocked": sum(1 for item in modules if item["gate"] == "Blocked"),
                "artifact_count": len(artifacts),
            },
        }

    def showcase_runbook_export_package(
        self,
        label: str = "dcc-showcase-runbook-package",
    ) -> Dict[str, Any]:
        plan = self.showcase_runbook_build_plan()
        smoke = self.showcase_runbook_run_smoke(label=label)
        handoff_fixture = self.asset_handoff_create_fixture(name="r10_3_showcase_handoff")
        handoff_packet = self.asset_handoff_export_packet(
            label=label + "-asset-handoff",
            names=handoff_fixture["nodes"],
            include_all=False,
        )
        handoff_decision = self.asset_handoff_export_decision_packet(
            label=label + "-asset-handoff-decision",
            names=handoff_fixture["nodes"],
            include_all=False,
        )
        presentation = {
            "entry": "from ai_tool_ta_maya_host import show_portfolio; show_portfolio()",
            "recommended_order": [module["id"] for module in plan["modules"]],
            "showcase_positioning": plan["showcase_positioning"],
            "business_route": plan["presentation_route"],
            "composite_gate": plan["composite_gate"],
            "live_demo_script": plan["demo_script"],
            "gui_click_checklist": plan["gui_click_checklist"],
            "additional_artifacts": [
                {
                    "module_id": "asset-handoff-gate",
                    "path": handoff_packet["path"],
                    "bytes": handoff_packet["bytes"],
                    "reportVersion": handoff_packet["report"]["reportVersion"],
                    "gate": handoff_packet["report"]["summary"]["gate"],
                },
                {
                    "module_id": "asset-handoff-decision",
                    "path": handoff_decision["path"],
                    "bytes": handoff_decision["bytes"],
                    "reportVersion": handoff_decision["report"]["reportVersion"],
                    "gate": handoff_decision["report"]["summary"]["gate"],
                }
            ],
            "reviewer_claims": [
                {
                    "id": "dcc-hosted",
                    "claim": "The portfolio runs inside Maya through AuroraView.",
                    "proof": "environment_status and connected bridge methods are exported with the package.",
                },
                {
                    "id": "five-modules",
                    "claim": "All five portfolio modules have DCC-backed evidence.",
                    "proof": "smoke.summary.module_count == 5 and smoke.summary.artifact_count == 5.",
                },
                {
                    "id": "synthetic-public",
                    "claim": "The demo is public-safe and does not depend on proprietary assets.",
                    "proof": "smoke.created contains synthetic fixtures only.",
                },
                {
                    "id": "deterministic-gates",
                    "claim": "AI narration does not override deterministic gates.",
                    "proof": "module gates and receipts are computed before presentation fields.",
                },
                {
                    "id": "composite-handoff-gate",
                    "claim": "The five DCC evidence streams can be evaluated as one asset handoff gate.",
                    "proof": "presentation.additional_artifacts contains maya-asset-handoff-gate@0.1.0.",
                },
                {
                    "id": "owner-engine-decision",
                    "claim": "Review assets are held for owner disposition while Ready assets can produce engine handoff intent.",
                    "proof": "handoffDecision.summary contains owner_required == 1, engine_ready == 1 and engine_held == 1.",
                },
            ],
            "evidence_requirements": [
                "package gate must not be Blocked",
                "five module artifacts must be generated",
                "asset handoff gate artifact must be generated",
                "asset handoff decision packet must be generated",
                "each artifact path must exist under maya-auroraview-host/artifacts",
                "public case package must point to the latest DCC-first manifest",
            ],
            "public_case_package": {
                "readme": "public-case-package/DCC_FIRST_PACKAGE.md",
                "manifest": "public-case-package/dcc-first-package-manifest.json",
                "legacy_package": "public-case-package/README.md",
            },
            "final_claim": "The portfolio is one DCC-first asset publish chain with five inspectable business stages, one composite handoff gate, one owner/engine decision packet, and exported Maya evidence.",
        }
        report = {
            "reportVersion": "maya-dcc-showcase-runbook-package@1.4.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "plan": plan,
            "smoke": smoke,
            "handoffGate": {
                "fixture": handoff_fixture,
                "path": handoff_packet["path"],
                "bytes": handoff_packet["bytes"],
                "summary": handoff_packet["report"]["summary"],
                "reportVersion": handoff_packet["report"]["reportVersion"],
            },
            "handoffDecision": {
                "path": handoff_decision["path"],
                "bytes": handoff_decision["bytes"],
                "summary": handoff_decision["report"]["summary"],
                "reportVersion": handoff_decision["report"]["reportVersion"],
                "sourcePacket": handoff_decision["report"]["sourcePacket"],
            },
            "presentation": presentation,
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def showcase_runbook_build_gui_evidence_manifest(self) -> Dict[str, Any]:
        plan = self.showcase_runbook_build_plan()
        output_root = "public-case-package/gui-evidence/r10-7"
        shots = [
            {
                "id": "shot-01-host-open",
                "capture_type": "screenshot",
                "target": "Maya main window with AuroraView portfolio panel open",
                "operator_action": "Run show_portfolio() from Maya Script Editor or shelf.",
                "filename": "r10-7_01_maya_host_open.png",
                "must_show": ["Maya chrome", "AuroraView panel", "Maya Bridge connected state"],
                "acceptance": "Viewer can tell the tool is hosted inside Maya, not a standalone browser tab.",
            },
            {
                "id": "shot-02-runbook-route",
                "capture_type": "screenshot",
                "target": "Right rail / DCC Showcase Runbook",
                "operator_action": "Click Build Plan.",
                "filename": "r10-7_02_runbook_business_route.png",
                "must_show": ["DCC-first positioning", "6 business route rows", "composite gate row"],
                "acceptance": "Viewer can read the asset handoff story before seeing individual modules.",
            },
            {
                "id": "shot-03-smoke-package",
                "capture_type": "screenshot",
                "target": "DCC Showcase Runbook after Run Smoke",
                "operator_action": "Click Run Smoke.",
                "filename": "r10-7_03_runbook_smoke_gate.png",
                "must_show": ["Review/Ready gate", "5 module rows", "handoff artifact row"],
                "acceptance": "Viewer can verify the package is backed by generated Maya artifacts and the composite handoff packet.",
            },
            {
                "id": "shot-04-asset-protocol",
                "capture_type": "screenshot",
                "target": "Asset Protocol Workbench / DCC Scene Payload",
                "operator_action": "Inspect Maya protocol payload after writing active payload.",
                "filename": "r10-7_04_asset_protocol_dcc_payload.png",
                "must_show": ["selected Maya node", "custom attr protocol", "match/drift evidence"],
                "acceptance": "Viewer can see DCC-native business metadata, not only React form data.",
            },
            {
                "id": "shot-05-rule-matrix",
                "capture_type": "screenshot",
                "target": "Cross-DCC Rule Matrix / Maya Scene Rule Run",
                "operator_action": "Run Collect Scene, Validate Scene, and Preview Fixes.",
                "filename": "r10-7_05_rule_matrix_maya_gate.png",
                "must_show": ["scene facts", "validation rows", "fix preview"],
                "acceptance": "Viewer can see deterministic publish gate logic and manual/safe fix separation.",
            },
            {
                "id": "shot-06-texture-delivery",
                "capture_type": "screenshot",
                "target": "Texture Delivery Console / Maya Texture Inspection",
                "operator_action": "Create fixture, inspect textures, validate scene.",
                "filename": "r10-7_06_texture_delivery_graph.png",
                "must_show": ["material/file nodes", "color-space rows", "manifest gate"],
                "acceptance": "Viewer can see DCC material graph evidence tied to delivery rules.",
            },
            {
                "id": "shot-07-task-orchestrator",
                "capture_type": "screenshot",
                "target": "Task Orchestrator / Maya Batch Queue",
                "operator_action": "Discover scene, build queue, dry-run.",
                "filename": "r10-7_07_task_orchestrator_receipts.png",
                "must_show": ["asset discovery", "queue rows", "dry-run receipts"],
                "acceptance": "Viewer can see multiple assets becoming a governed handoff queue.",
            },
            {
                "id": "shot-08-asset-handoff-gate",
                "capture_type": "screenshot",
                "target": "Right rail / Asset Handoff Gate",
                "operator_action": "Run Fixture, Evaluate Gate, Preview Actions, and Export Packet.",
                "filename": "r10-7_08_asset_handoff_gate.png",
                "must_show": ["2 asset rows", "1 Ready", "1 Review", "handoff packet path"],
                "acceptance": "Viewer can see the five evidence streams compressed into one batch handoff decision.",
            },
            {
                "id": "shot-09-asset-handoff-decision",
                "capture_type": "screenshot",
                "target": "Right rail / Asset Handoff Gate / Decision Packet",
                "operator_action": "Click Decision Packet after running the handoff gate.",
                "filename": "r10-7_09_asset_handoff_decision_packet.png",
                "must_show": ["repair preview row", "owner disposition row", "engine handoff intent row"],
                "acceptance": "Viewer can see which asset can enter engine handoff and which asset is held for owner disposition.",
            },
        ]
        recordings = [
            {
                "id": "clip-01-primary-demo",
                "capture_type": "screen_recording",
                "target": "Maya GUI primary route",
                "operator_action": "Open host, Build Plan, Run Smoke, run Asset Handoff Gate, export Decision Packet, inspect one module, Export Package.",
                "filename": "r10-7_primary_dcc_first_route.mp4",
                "duration_target_seconds": 120,
                "acceptance": "A reviewer can understand the DCC-first portfolio without opening the source project.",
            }
        ]
        return {
            "ok": True,
            "schema": "maya-dcc-gui-evidence-manifest@1.2.0",
            "output_root": output_root,
            "showcase_positioning": plan["showcase_positioning"],
            "business_route": plan["presentation_route"],
            "shots": shots,
            "recordings": recordings,
            "summary": {
                "shot_count": len(shots),
                "recording_count": len(recordings),
                "business_route_steps": len(plan["presentation_route"]),
                "required_files": len(shots) + len(recordings),
            },
            "capture_policy": {
                "dcc_host_required": "Maya 2024 with AuroraView portfolio host",
                "assets": "Synthetic fixtures only",
                "naming": "Use r10-7 media prefix so screenshots include the Asset Handoff Decision Packet step.",
            },
        }

    def showcase_runbook_export_gui_evidence_manifest(
        self,
        label: str = "dcc-gui-evidence-manifest",
    ) -> Dict[str, Any]:
        manifest = self.showcase_runbook_build_gui_evidence_manifest()
        report = {
            "reportVersion": "maya-dcc-gui-evidence-manifest@1.2.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "guiEvidence": manifest,
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def showcase_runbook_audit_gui_media(
        self,
        media_root: Optional[str] = None,
    ) -> Dict[str, Any]:
        manifest = self.showcase_runbook_build_gui_evidence_manifest()
        root = Path(media_root) if media_root else PORTFOLIO_ROOT / "assets" / "dcc-first" / "r10-7-gui-evidence"
        root.mkdir(parents=True, exist_ok=True)

        rows: List[Dict[str, Any]] = []
        expected_items = list(manifest["shots"]) + list(manifest["recordings"])
        for item in expected_items:
            expected_path = root / item["filename"]
            exists = expected_path.exists()
            bytes_size = expected_path.stat().st_size if exists else 0
            minimum_bytes = 4096 if item["capture_type"] == "screenshot" else 100000
            status = "Missing"
            if exists and bytes_size >= minimum_bytes:
                status = "Present"
            elif exists:
                status = "Review"

            rows.append(
                {
                    "id": item["id"],
                    "capture_type": item["capture_type"],
                    "target": item["target"],
                    "filename": item["filename"],
                    "expected_path": str(expected_path),
                    "exists": exists,
                    "bytes": bytes_size,
                    "minimum_bytes": minimum_bytes,
                    "status": status,
                    "acceptance": item["acceptance"],
                }
            )

        present = len([row for row in rows if row["status"] == "Present"])
        review = len([row for row in rows if row["status"] == "Review"])
        missing = len([row for row in rows if row["status"] == "Missing"])
        gate = "Ready" if missing == 0 and review == 0 else "Review" if present > 0 or review > 0 else "CapturePending"

        return {
            "ok": True,
            "schema": "maya-dcc-gui-media-audit@0.2.0",
            "media_root": str(root),
            "manifest_schema": manifest["schema"],
            "rows": rows,
            "summary": {
                "gate": gate,
                "required_files": len(rows),
                "present": present,
                "review": review,
                "missing": missing,
                "shot_count": manifest["summary"]["shot_count"],
                "recording_count": manifest["summary"]["recording_count"],
            },
            "capture_policy": {
                "no_placeholder_media": True,
                "expected_media_root": str(root),
                "screenshots": "PNG files should be real Maya GUI captures.",
                "recordings": "MP4 file should be the primary Maya route recording.",
            },
        }

    def showcase_runbook_export_gui_media_audit(
        self,
        label: str = "r10-7-gui-media-audit",
        media_root: Optional[str] = None,
    ) -> Dict[str, Any]:
        audit = self.showcase_runbook_audit_gui_media(media_root=media_root)
        report = {
            "reportVersion": "maya-dcc-gui-media-audit@0.2.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "mediaAudit": audit,
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def showcase_runbook_build_case_page(
        self,
        label: str = "dcc-first-case-page",
    ) -> Dict[str, Any]:
        runbook_package = self.showcase_runbook_export_package(label=label + "-runbook")
        gui_manifest = self.showcase_runbook_export_gui_evidence_manifest(label=label + "-gui-evidence")
        runbook_report = runbook_package["report"]
        gui_report = gui_manifest["report"]
        presentation = runbook_report["presentation"]
        smoke_summary = runbook_report["smoke"]["summary"]
        handoff_summary = runbook_report["handoffGate"]["summary"]
        handoff_decision = runbook_report["handoffDecision"]
        decision_summary = handoff_decision["summary"]
        gui_summary = gui_report["guiEvidence"]["summary"]

        sections = [
            {
                "id": "case-thesis",
                "title": "Case Thesis",
                "body": "A Maya-hosted AI Tool TA portfolio that turns one synthetic asset handoff into protocol, publish gate, visual review, texture delivery, batch orchestration, and a composite handoff decision.",
                "proof": "Runbook presentation contains 7 business route steps, a composite Asset Handoff Gate artifact, and an Owner / Engine Decision packet.",
            },
            {
                "id": "dcc-entry",
                "title": "DCC Entry",
                "body": "Reviewer opens the portfolio through Maya Script Editor or shelf, then uses AuroraView right rail controls.",
                "proof": "environment_status is exported with Maya version and AuroraView state.",
            },
            {
                "id": "business-route",
                "title": "Business Route",
                "body": "The route is ordered by production handoff logic, not UI module order.",
                "proof": "presentation.business_route has %s steps." % len(presentation["business_route"]),
            },
            {
                "id": "composite-gate",
                "title": "Composite Handoff Gate",
                "body": "Asset Handoff Gate merges protocol, rule, texture, visual and queue evidence into per-asset Ready/Review/Blocked gates.",
                "proof": "handoff summary: %s assets, %s Ready, %s Review, %s Blocked."
                % (
                    handoff_summary["asset_count"],
                    handoff_summary["ready"],
                    handoff_summary["review"],
                    handoff_summary["blocked"],
                ),
            },
            {
                "id": "owner-engine-decision",
                "title": "Owner / Engine Decision",
                "body": "Decision Packet converts Ready/Review gates into repair preview rows, owner disposition rows, and engine handoff intents without approving or writing anything automatically.",
                "proof": "decision summary: %s repairs, %s owner-required, %s engine-ready, %s held."
                % (
                    decision_summary["repair_action_count"],
                    decision_summary["owner_required"],
                    decision_summary["engine_ready"],
                    decision_summary["engine_held"],
                ),
            },
            {
                "id": "media-plan",
                "title": "Maya GUI Evidence Plan",
                "body": "The case page has a concrete capture plan for screenshots and a route recording.",
                "proof": "GUI evidence manifest contains %s shots and %s recording."
                % (gui_summary["shot_count"], gui_summary["recording_count"]),
            },
        ]

        artifact_rows = [
            {
                "id": "runbook-package",
                "kind": "runbook",
                "path": runbook_package["path"],
                "bytes": runbook_package["bytes"],
                "reportVersion": runbook_report["reportVersion"],
                "gate": runbook_report["smoke"]["gate"],
            },
            {
                "id": "asset-handoff-gate",
                "kind": "handoff",
                "path": runbook_report["handoffGate"]["path"],
                "bytes": runbook_report["handoffGate"]["bytes"],
                "reportVersion": runbook_report["handoffGate"]["reportVersion"],
                "gate": handoff_summary["gate"],
            },
            {
                "id": "asset-handoff-decision",
                "kind": "handoff-decision",
                "path": handoff_decision["path"],
                "bytes": handoff_decision["bytes"],
                "reportVersion": handoff_decision["reportVersion"],
                "gate": decision_summary["gate"],
            },
            {
                "id": "gui-evidence-manifest",
                "kind": "gui-evidence",
                "path": gui_manifest["path"],
                "bytes": gui_manifest["bytes"],
                "reportVersion": gui_report["reportVersion"],
                "gate": "CapturePending",
            },
        ]

        return {
            "ok": True,
            "schema": "maya-dcc-portfolio-case-page@1.1.0",
            "title": "AI Tool TA DCC-first Portfolio Case",
            "host": {
                "dcc": "Autodesk Maya",
                "frontendHost": "AuroraView",
                "entry": "from ai_tool_ta_maya_host import show_portfolio; show_portfolio()",
            },
            "summary": {
                "gate": runbook_report["smoke"]["gate"],
                "module_count": smoke_summary["module_count"],
                "module_artifact_count": smoke_summary["artifact_count"],
                "business_route_steps": len(presentation["business_route"]),
                "live_demo_script_steps": len(presentation["live_demo_script"]),
                "gui_checklist_items": len(presentation["gui_click_checklist"]),
                "reviewer_claims": len(presentation["reviewer_claims"]),
                "handoff_assets": handoff_summary["asset_count"],
                "handoff_ready": handoff_summary["ready"],
                "handoff_review": handoff_summary["review"],
                "handoff_blocked": handoff_summary["blocked"],
                "handoff_decision_repairs": decision_summary["repair_action_count"],
                "handoff_decision_safe_auto": decision_summary["safe_auto"],
                "handoff_decision_manual_only": decision_summary["manual_only"],
                "handoff_decision_owner_dispositions": decision_summary["owner_dispositions"],
                "handoff_decision_owner_required": decision_summary["owner_required"],
                "handoff_decision_engine_ready": decision_summary["engine_ready"],
                "handoff_decision_engine_held": decision_summary["engine_held"],
                "gui_shots": gui_summary["shot_count"],
                "gui_recordings": gui_summary["recording_count"],
                "required_media_files": gui_summary["required_files"],
                "artifact_count": len(artifact_rows),
            },
            "sections": sections,
            "business_route": presentation["business_route"],
            "live_demo_script": presentation["live_demo_script"],
            "gui_evidence_shots": gui_report["guiEvidence"]["shots"],
            "artifacts": artifact_rows,
            "validation": [
                "npm run build",
                "python -m py_compile dcc-hosts/maya-auroraview-host/ai_tool_ta_maya_host/api.py",
                "Maya 2024 mayapy showcase_runbook_export_case_page smoke",
                "Maya 2024 mayapy asset_handoff_export_decision_packet smoke",
            ],
            "public_case_package": {
                "readme": "public-case-package/DCC_FIRST_PACKAGE.md",
                "manifest": "public-case-package/dcc-first-package-manifest.json",
            },
        }

    def showcase_runbook_export_case_page(
        self,
        label: str = "dcc-first-case-page",
    ) -> Dict[str, Any]:
        case_page = self.showcase_runbook_build_case_page(label=label)
        report = {
            "reportVersion": "maya-dcc-portfolio-case-page@1.1.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "casePage": case_page,
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}

    def dcc_presentation_build_pack(
        self,
        label: str = "r56-houdini-rule-adapter-presentation-pack",
    ) -> Dict[str, Any]:
        public_package_dir = PORTFOLIO_ROOT / "public-case-package"
        manifest_path = public_package_dir / "dcc-first-package-manifest.json"
        manifest = _read_json_dict(manifest_path)
        manifest_summary = manifest.get("summary", {}) if isinstance(manifest.get("summary"), dict) else {}
        runbook_plan = self.showcase_runbook_build_plan()
        media_audit = self.showcase_runbook_audit_gui_media()
        media_summary = media_audit["summary"]

        evidence_files = [
            _probe_file("public-manifest", "DCC-first package manifest", "manifest", str(manifest_path)),
            _probe_file("public-package-readme", "DCC-first package readme", "doc", "DCC_FIRST_PACKAGE.md", base_dir=public_package_dir),
            _probe_file("maya-host-readme", "Maya host readme", "doc", PORTFOLIO_ROOT / "dcc-hosts" / "maya-auroraview-host" / "README.md"),
            _probe_file("case-page", "DCC-first case page artifact", "artifact", manifest.get("verifiedArtifact")),
            _probe_file("runbook", "DCC showcase runbook artifact", "artifact", manifest.get("runbookArtifact")),
            _probe_file("gui-evidence-manifest", "GUI evidence manifest artifact", "artifact", manifest.get("guiEvidenceManifest")),
            _probe_file("gui-media-audit", "GUI media audit artifact", "artifact", manifest.get("guiMediaAuditArtifact")),
            _probe_file("asset-handoff-gate", "Asset Handoff Gate artifact", "artifact", manifest.get("assetHandoffArtifact")),
            _probe_file("asset-handoff-decision", "Asset Handoff Decision artifact", "artifact", manifest.get("assetHandoffDecisionArtifact")),
            _probe_file("engine-preflight", "Engine Handoff Preflight artifact", "artifact", manifest.get("engineHandoffPreflightArtifact")),
            _probe_file("engine-preset-comparison", "Engine Preset Comparison artifact", "artifact", manifest.get("enginePresetComparisonArtifact")),
            _probe_file("blender-rule-adapter", "Blender Rule Adapter artifact", "artifact", manifest.get("blenderRuleAdapterArtifact")),
            _probe_file("blender-l3-harness", "Blender L3 Harness readiness artifact", "artifact", manifest.get("blenderRuleAdapterL3HarnessArtifact")),
            _probe_file("max-rule-adapter", "3ds Max Rule Adapter artifact", "artifact", manifest.get("maxRuleAdapterArtifact")),
            _probe_file("max-l3-harness", "3ds Max L3 Harness readiness artifact", "artifact", manifest.get("maxRuleAdapterL3HarnessArtifact")),
            _probe_file(
                "max-texture-manifest-link",
                "3ds Max Material Texture Manifest Link artifact",
                "artifact",
                manifest.get("maxTextureManifestLinkArtifact"),
            ),
            _probe_file(
                "houdini-rule-adapter",
                "Houdini Rule Adapter contract artifact",
                "artifact",
                manifest.get("houdiniRuleAdapterArtifact"),
            ),
            _probe_file(
                "houdini-l3-readiness",
                "Houdini hython L3 readiness artifact",
                "artifact",
                manifest.get("houdiniRuleAdapterL3HarnessArtifact"),
            ),
            _probe_file("unreal-handoff-inspector", "Unreal Handoff Inspector artifact", "artifact", manifest.get("unrealHandoffInspectorArtifact")),
            _probe_file(
                "unreal-preset-fact-comparison",
                "Unreal Preset Fact Comparison artifact",
                "artifact",
                manifest.get("unrealPresetFactComparisonArtifact"),
            ),
            _probe_file(
                "unreal-preset-fact-review",
                "Unreal Preset Fact Review artifact",
                "artifact",
                manifest.get("unrealPresetFactReviewArtifact"),
            ),
            _probe_file(
                "scene-transaction-guard",
                "Scene Transaction Guard artifact",
                "artifact",
                manifest.get("sceneTransactionGuardArtifact"),
            ),
            _probe_file(
                "animation-continuity-maya-l3",
                "Animation Continuity Maya L3 artifact",
                "artifact",
                manifest.get("animationContinuityArtifact"),
            ),
            _probe_file(
                "unreal-animation-bridge-contract",
                "Unreal Animation Bridge contract artifact",
                "artifact",
                manifest.get("unrealAnimationBridgeContractArtifact"),
            ),
            _probe_file(
                "unreal-animation-bridge-import-l3",
                "Unreal Animation Bridge import L3 artifact",
                "artifact",
                manifest.get("unrealAnimationBridgeArtifact"),
            ),
            _probe_file(
                "unreal-animation-deep-facts",
                "Unreal AnimSequence Deep Facts artifact",
                "artifact",
                manifest.get("unrealAnimationDeepFactsArtifact"),
            ),
            _probe_file(
                "character-calibration-maya-l3",
                "Character Calibration Maya L3 artifact",
                "artifact",
                manifest.get("characterCalibrationArtifact"),
            ),
            _probe_file(
                "character-calibration-drilldown",
                "Character Calibration Drilldown artifact",
                "artifact",
                manifest.get("characterCalibrationDrilldownArtifact"),
            ),
            _probe_file(
                "unreal-control-rig-bridge",
                "Unreal Control Rig Bridge artifact",
                "artifact",
                manifest.get("unrealControlRigBridgeArtifact"),
            ),
            _probe_file(
                "unreal-control-rig-fixture-authoring",
                "Unreal Control Rig Fixture Authoring artifact",
                "artifact",
                manifest.get("unrealControlRigFixtureAuthoringArtifact"),
            ),
            _probe_file(
                "unreal-control-rig-face-skeleton-fixture",
                "Unreal Control Rig Face Skeleton Fixture artifact",
                "artifact",
                manifest.get("unrealControlRigFaceSkeletonFixtureArtifact"),
            ),
            _probe_file(
                "unreal-control-rig-deformation-link",
                "Unreal Control Rig Deformation Link artifact",
                "artifact",
                manifest.get("unrealControlRigDeformationLinkArtifact"),
            ),
            _probe_file(
                "unreal-control-rig-compile-status",
                "Unreal Control Rig Compile Status Bridge artifact",
                "artifact",
                manifest.get("unrealControlRigCompileStatusArtifact"),
            ),
            _probe_file(
                "groom-export-inspector",
                "Groom Export Inspector Maya L3 artifact",
                "artifact",
                manifest.get("groomExportInspectorArtifact"),
            ),
            _probe_file(
                "groom-unreal-readiness",
                "Groom Unreal Import Readiness artifact",
                "artifact",
                manifest.get("groomUnrealReadinessArtifact"),
            ),
            _probe_file(
                "groom-alembic-payload",
                "Groom Alembic Payload Receipt artifact",
                "artifact",
                manifest.get("groomAlembicPayloadArtifact"),
            ),
            _probe_file(
                "groom-alembic-cache",
                "Groom Alembic exported cache",
                "cache",
                manifest.get("groomAlembicPayloadCache"),
            ),
            _probe_file(
                "groom-alembic-import-postcheck",
                "Groom Alembic Import/Post-check artifact",
                "artifact",
                manifest.get("groomAlembicImportPostcheckArtifact"),
            ),
            _probe_file(
                "groom-plugin-api-fixture",
                "Groom Plugin/API Fixture artifact",
                "artifact",
                manifest.get("groomPluginApiFixtureArtifact"),
            ),
            _probe_file(
                "groom-controlled-executor",
                "Groom Controlled Executor artifact",
                "artifact",
                manifest.get("groomControlledExecutorArtifact"),
            ),
            _probe_file(
                "groom-runtime-facts",
                "Groom Runtime Fact Collector artifact",
                "artifact",
                manifest.get("groomRuntimeFactsArtifact"),
            ),
            _probe_file(
                "spatial-authoring-maya-l3",
                "Spatial Authoring Maya L3 artifact",
                "artifact",
                manifest.get("spatialAuthoringArtifact"),
            ),
            _probe_file(
                "spatial-authoring-drilldown",
                "Spatial Authoring Drilldown artifact",
                "artifact",
                manifest.get("spatialAuthoringDrilldownArtifact"),
            ),
            _probe_file(
                "unreal-socket-import-checker",
                "Unreal Socket Import Checker artifact",
                "artifact",
                manifest.get("unrealSocketImportCheckerArtifact"),
            ),
            _probe_file(
                "unreal-socket-authoring-executor",
                "Unreal Socket Authoring Executor artifact",
                "artifact",
                manifest.get("unrealSocketAuthoringExecutorArtifact"),
            ),
            _probe_file(
                "unreal-socket-api-docs",
                "Unreal Socket API docs probe artifact",
                "artifact",
                manifest.get("unrealSocketApiDocsArtifact"),
            ),
            _probe_file(
                "unreal-gameplay-attach-fixture",
                "Unreal Gameplay Attach Fixture artifact",
                "artifact",
                manifest.get("unrealGameplayAttachFixtureArtifact"),
            ),
            _probe_file(
                "platform-variant-forge",
                "Platform Variant Forge artifact",
                "artifact",
                manifest.get("platformVariantForgeArtifact"),
            ),
            _probe_file(
                "platform-variant-unreal-runtime",
                "Platform Variant Unreal Runtime Probe artifact",
                "artifact",
                manifest.get("platformVariantUnrealRuntimeArtifact"),
            ),
            _probe_file(
                "platform-variant-generation-plan",
                "Platform Variant Generation Plan artifact",
                "artifact",
                manifest.get("platformVariantGenerationPlanArtifact"),
            ),
            _probe_file(
                "platform-variant-texture-runtime",
                "Platform Variant Texture Runtime Collector artifact",
                "artifact",
                manifest.get("platformVariantTextureRuntimeArtifact"),
            ),
            _probe_file(
                "platform-variant-texture-payload-runtime",
                "Platform Variant Public Texture2D Payload artifact",
                "artifact",
                manifest.get("platformVariantTexturePayloadArtifact"),
            ),
            _probe_file(
                "platform-variant-controlled-executor",
                "Platform Variant Controlled Executor artifact",
                "artifact",
                manifest.get("platformVariantControlledExecutorArtifact"),
            ),
            _probe_file(
                "platform-variant-executor-expansion",
                "Platform Variant Executor Expansion Receipts artifact",
                "artifact",
                manifest.get("platformVariantExecutorExpansionArtifact"),
            ),
            _probe_file(
                "platform-variant-staticmesh-postcheck",
                "Platform Variant StaticMesh Post-check artifact",
                "artifact",
                manifest.get("platformVariantStaticMeshPostcheckArtifact"),
            ),
        ]

        missing_required = [row for row in evidence_files if row["required"] and not row["exists"]]
        if missing_required:
            gate = "Blocked"
        elif media_summary["gate"] == "CapturePending":
            gate = "CapturePending"
        elif media_summary["gate"] == "Review" or manifest.get("gate") == "Review":
            gate = "Review"
        else:
            gate = "Ready"

        demo_route = [
            {
                "id": "01-open-maya-host",
                "label": "Open Maya host",
                "operator_action": "Run show_portfolio() from Maya Script Editor or shelf.",
                "evidence_expected": "AuroraView panel opens inside Maya and bridge state is Connected.",
            },
            {
                "id": "02-export-case-page",
                "label": "Export DCC-first case page",
                "operator_action": "Open Task Orchestrator evidence view and click Export Case Page.",
                "evidence_expected": "maya-dcc-portfolio-case-page@1.1.0 artifact path is shown.",
            },
            {
                "id": "03-run-composite-gate",
                "label": "Run composite handoff gate",
                "operator_action": "Use Asset Handoff Gate: Fixture, Evaluate Gate, Preview Actions, Decision Packet.",
                "evidence_expected": "2 assets resolve to 1 Ready, 1 Review, 0 Blocked, with owner and engine intent rows.",
            },
            {
                "id": "04-compare-engine-presets",
                "label": "Compare engine presets",
                "operator_action": "Click Preset Compare with PC and Mobile presets.",
                "evidence_expected": "One platform split row and one held-across-presets row are exported with zero engine writes.",
            },
            {
                "id": "05-review-unreal-inspector",
                "label": "Review Unreal handoff inspector",
                "operator_action": "Open the Presenter Pack or public package and inspect the Unreal Handoff Inspector artifact.",
                "evidence_expected": "DCC import intents are checked against Unreal path, asset class, dependency, fingerprint, LOD, collision and owner-state rules.",
            },
            {
                "id": "06-review-unreal-preset-facts",
                "label": "Review Unreal preset facts",
                "operator_action": "Click Preset Fact Review inside the Maya-hosted case page.",
                "evidence_expected": "Preset facts resolve to matched, drift, waived or blocked rows with visible owner action and waiver evidence.",
            },
            {
                "id": "07-run-scene-transaction-guard",
                "label": "Run scene transaction guard",
                "operator_action": "Click Txn Guard inside the Maya-hosted case page.",
                "evidence_expected": "Before/after scene fingerprints, mutation risk rows and rollback preview are exported from Maya.",
            },
            {
                "id": "08-run-animation-continuity-l3",
                "label": "Run animation continuity L3",
                "operator_action": "Run python dcc-hosts/animation-continuity-lab/scripts/run_l3_smoke.py.",
                "evidence_expected": "Maya mayapy runtime exports keyed animCurve facts for rig identity, take range, sample rate, channels, sub-frame keys and root motion.",
            },
            {
                "id": "09-run-unreal-animation-bridge-import-l3",
                "label": "Run Unreal animation bridge import L3",
                "operator_action": "Run python dcc-hosts/unreal-animation-bridge/scripts/run_import_l3_smoke.py.",
                "evidence_expected": "Maya mayapy generates public FBX clips, Unreal Python imports synthetic Skeleton/SkeletalMesh/AnimSequence assets, and runtime facts are exported.",
            },
            {
                "id": "10-run-unreal-animation-deep-facts",
                "label": "Run Unreal animation deep facts",
                "operator_action": "Run python dcc-hosts/unreal-animation-bridge/scripts/run_deep_facts.py.",
                "evidence_expected": "Unreal Python reads existing public AnimSequence assets and exports duration, derived frame span, curve metadata, root motion and compression visibility without saving assets.",
            },
            {
                "id": "11-run-character-calibration-l3",
                "label": "Run character calibration L3",
                "operator_action": "Run python dcc-hosts/character-calibration-studio/scripts/run_l3_smoke.py.",
                "evidence_expected": "Maya mayapy creates synthetic character meshes and joints, then exports topology, joint coverage, calibration delta, face parameter, Control Rig mapping and skin budget facts.",
            },
            {
                "id": "12-run-character-calibration-drilldown",
                "label": "Run character calibration drilldown",
                "operator_action": "Run python dcc-hosts/character-calibration-studio/scripts/run_drilldown.py.",
                "evidence_expected": "Maya L3 character calibration facts become UI-ready drilldown panels, owner actions and fix previews.",
            },
            {
                "id": "13-run-unreal-control-rig-bridge",
                "label": "Run Unreal Control Rig bridge",
                "operator_action": "Run python dcc-hosts/unreal-control-rig-bridge/scripts/run_l3_smoke.py.",
                "evidence_expected": "Unreal Python verifies Control Rig API readiness, public SkeletalMesh/Skeleton binding and expected CR asset coverage from Character Calibration drilldown facts.",
            },
            {
                "id": "14-run-unreal-control-rig-fixture-authoring",
                "label": "Run Unreal Control Rig fixture authoring",
                "operator_action": "Run python dcc-hosts/unreal-control-rig-bridge/scripts/run_fixture_authoring.py, then rerun run_l3_smoke.py.",
                "evidence_expected": "Unreal Python creates the public CR_HeroFace fixture, adds required Maya controls to the runtime hierarchy, saves only /Game/AI_Tool_TA content, and proves the approved bridge row becomes Ready.",
            },
            {
                "id": "15-run-unreal-control-rig-face-skeleton-fixture",
                "label": "Run Unreal Control Rig face skeleton fixture",
                "operator_action": "Run python dcc-hosts/unreal-control-rig-bridge/scripts/run_face_skeleton_fixture.py, then rerun run_l3_smoke.py.",
                "evidence_expected": "Maya mayapy generates a public face Skeleton FBX, Unreal imports SK_HeroFace / SK_HeroFace_Skeleton, and R43 missing deformation targets are resolved inside the public fixture.",
            },
            {
                "id": "16-run-unreal-control-rig-deformation-link",
                "label": "Run Unreal Control Rig deformation link",
                "operator_action": "Run python dcc-hosts/unreal-control-rig-bridge/scripts/run_deformation_link.py.",
                "evidence_expected": "Unreal Python reads CR_HeroFace, links Maya controls to deformation target names, audits Skeleton coverage, hierarchy shape/offset readability and compile-status API visibility without saving assets.",
            },
            {
                "id": "17-run-unreal-control-rig-compile-status",
                "label": "Run Unreal Control Rig compile status bridge",
                "operator_action": "Run python dcc-hosts/unreal-control-rig-bridge/scripts/run_compile_status.py.",
                "evidence_expected": "Unreal Python invokes ControlRigBlueprint compile methods on the public CR_HeroFace fixture, then records diagnostic/status readability, dirty-state boundary and zero-save evidence.",
            },
            {
                "id": "18-run-groom-export-inspector",
                "label": "Run Groom Export Inspector L3",
                "operator_action": "Run python dcc-hosts/groom-export-inspector/scripts/run_l3_smoke.py.",
                "evidence_expected": "Maya mayapy creates public groom curves, then exports root UV, strand ID, guide curve, Alembic payload and Unreal binding readiness facts.",
            },
            {
                "id": "19-run-groom-unreal-readiness",
                "label": "Run Groom Unreal import readiness",
                "operator_action": "Run python dcc-hosts/groom-export-inspector/scripts/run_unreal_readiness.py.",
                "evidence_expected": "Unreal Python checks Groom/Alembic import API visibility, target SkeletalMesh presence, expected Groom/Binding assets and zero-write boundary.",
            },
            {
                "id": "20-run-groom-alembic-payload",
                "label": "Run Groom Alembic payload receipt",
                "operator_action": "Run python dcc-hosts/groom-export-inspector/scripts/run_alembic_payload.py.",
                "evidence_expected": "Maya AbcExport writes the approved public groom cache, records bytes/hash, holds TMP row, and keeps productionWrites=0.",
            },
            {
                "id": "21-run-groom-alembic-import-postcheck",
                "label": "Run Groom Alembic import/post-check readiness",
                "operator_action": "Run python dcc-hosts/groom-export-inspector/scripts/run_alembic_import_postcheck.py.",
                "evidence_expected": "Unreal Python reads the R48 .abc cache, verifies sha256 continuity, dry-runs AssetImportTask setup, checks Groom/Binding post-check targets and keeps engineWrites=0.",
            },
            {
                "id": "22-run-groom-plugin-api-fixture",
                "label": "Run Groom plugin/API fixture readiness",
                "operator_action": "Run python dcc-hosts/groom-export-inspector/scripts/run_groom_plugin_api_fixture.py.",
                "evidence_expected": "Unreal Python enters the public project with HairStrands/Alembic plugins enabled, verifies descriptor/project config readiness, Groom API visibility and zero asset writes.",
            },
            {
                "id": "23-run-groom-controlled-executor",
                "label": "Run Groom controlled executor",
                "operator_action": "Run python dcc-hosts/groom-export-inspector/scripts/run_groom_controlled_executor.py.",
                "evidence_expected": "Unreal Python imports the approved public .abc through AssetImportTask, post-checks Groom/Binding targets, records wrong asset class or binding blockers, and rolls back public fixture writes.",
            },
            {
                "id": "24-run-groom-runtime-facts",
                "label": "Run Groom runtime facts",
                "operator_action": "Run python dcc-hosts/groom-export-inspector/scripts/run_groom_runtime_facts.py.",
                "evidence_expected": "Unreal Python imports the approved GroomAsset/BindingAsset public fixture, reads runtime properties, method surface and callable facts, then rolls back without residue.",
            },
            {
                "id": "25-run-spatial-authoring-l3",
                "label": "Run spatial authoring L3",
                "operator_action": "Run python dcc-hosts/spatial-authoring-workbench/scripts/run_l3_smoke.py.",
                "evidence_expected": "Maya mayapy creates synthetic joints and locators, then exports socket, hotspot, pose frame, mirror pair and pose transfer facts.",
            },
            {
                "id": "26-run-spatial-authoring-drilldown",
                "label": "Run spatial authoring drilldown",
                "operator_action": "Run python dcc-hosts/spatial-authoring-workbench/scripts/run_drilldown.py.",
                "evidence_expected": "Maya L3 spatial authoring facts become UI-ready socket, hotspot, pose frame, transform and pose transfer panels.",
            },
            {
                "id": "27-run-unreal-socket-import-checker",
                "label": "Run Unreal socket import checker",
                "operator_action": "Run python dcc-hosts/unreal-socket-import-checker/scripts/run_l3_smoke.py.",
                "evidence_expected": "Unreal Python checks SkeletalMesh/Skeleton socket API readiness and expected engine socket coverage from Spatial Authoring drilldown facts.",
            },
            {
                "id": "28-run-unreal-socket-authoring-executor",
                "label": "Run Unreal socket authoring executor",
                "operator_action": "Run python dcc-hosts/unreal-socket-import-checker/scripts/run_socket_authoring_executor.py.",
                "evidence_expected": "Approved socket rows enter a controlled Unreal execution gate; UE 5.3 Python socket authoring limits and no-write rollback boundary are exported.",
            },
            {
                "id": "29-run-unreal-gameplay-attach-fixture",
                "label": "Run Unreal gameplay attach fixture",
                "operator_action": "Run python dcc-hosts/unreal-socket-import-checker/scripts/run_gameplay_attach_fixture.py.",
                "evidence_expected": "Maya socket/hotspot intent rows are joined to Unreal runtime asset/API facts so gameplay attach is blocked until required character sockets and hotspot semantics are present.",
            },
            {
                "id": "30-run-platform-variant-forge",
                "label": "Run platform variant forge",
                "operator_action": "Run python dcc-hosts/platform-variant-forge/scripts/run_smoke.py.",
                "evidence_expected": "PC and Mobile variant plans are checked against LOD, material, texture, collision, path, owner and Unreal preset fact evidence.",
            },
            {
                "id": "31-run-platform-variant-unreal-runtime",
                "label": "Run platform variant Unreal runtime",
                "operator_action": "Run python dcc-hosts/platform-variant-forge/scripts/run_unreal_runtime_probe.py.",
                "evidence_expected": "Unreal Python collects runtime StaticMesh facts for planned PC/Mobile variants and compares them against the R28 variant plan.",
            },
            {
                "id": "32-run-platform-variant-generation-plan",
                "label": "Run platform variant generation plan",
                "operator_action": "Run python dcc-hosts/platform-variant-forge/scripts/run_generation_plan.py.",
                "evidence_expected": "Runtime drift is converted into dry-run LOD, Nanite, material bake, texture downscale, collision and asset creation operations with transaction boundaries.",
            },
            {
                "id": "33-run-platform-variant-texture-runtime",
                "label": "Run platform variant texture runtime",
                "operator_action": "Run python dcc-hosts/platform-variant-forge/scripts/run_texture_runtime_probe.py.",
                "evidence_expected": "Unreal Python collects StaticMesh material slots, material dependency queries and Texture2D budget facts for PC/Mobile variants.",
            },
            {
                "id": "34-run-platform-variant-texture-payload",
                "label": "Run platform variant texture payload",
                "operator_action": "Run python dcc-hosts/platform-variant-forge/scripts/run_texture_payload_probe.py.",
                "evidence_expected": "A generated public 2048 Texture2D payload is imported, wired to the material, and rechecked against PC/Mobile texture budgets.",
            },
            {
                "id": "35-run-platform-variant-controlled-executor",
                "label": "Run platform variant controlled executor",
                "operator_action": "Run python dcc-hosts/platform-variant-forge/scripts/run_controlled_executor.py.",
                "evidence_expected": "Unreal Python executes a public texture max-size clamp, verifies post-state, and rolls back to the preflight fingerprint.",
            },
            {
                "id": "36-run-platform-variant-executor-expansion",
                "label": "Run platform variant executor expansion",
                "operator_action": "Run python dcc-hosts/platform-variant-forge/scripts/run_executor_expansion.py.",
                "evidence_expected": "LOD, Nanite and collision operations become approval receipts with deterministic params, writeSet and rollback boundaries.",
            },
            {
                "id": "37-run-platform-variant-staticmesh-postcheck",
                "label": "Run platform variant StaticMesh post-check",
                "operator_action": "Run python dcc-hosts/platform-variant-forge/scripts/run_staticmesh_postcheck.py.",
                "evidence_expected": "R34 LOD, Nanite and collision receipts are checked against read-only Unreal StaticMesh runtime facts.",
            },
            {
                "id": "38-review-blender-adapter",
                "label": "Review Blender rule adapter",
                "operator_action": "Open the Presenter Pack or public package and inspect the Blender Rule Adapter artifact.",
                "evidence_expected": "Blender object custom properties, collections, material slots, UVs, and collision proxies normalize into Cross-DCC rule input.",
            },
            {
                "id": "39-run-blender-l3-harness",
                "label": "Run Blender L3 harness",
                "operator_action": "Run python dcc-hosts/blender-rule-adapter/scripts/run_l3_smoke.py.",
                "evidence_expected": "Blender background runtime exports bpy scene facts into the Cross-DCC rule input shape.",
            },
            {
                "id": "40-run-3dsmax-adapter-harness",
                "label": "Run 3ds Max adapter harness",
                "operator_action": "Run python dcc-hosts/3dsmax-rule-adapter/scripts/run_l3_smoke.py --run-runtime --timeout-seconds 600.",
                "evidence_expected": "3ds Max batch runtime exports pymxs scene facts into the Cross-DCC rule input shape.",
            },
            {
                "id": "41-run-max-texture-manifest-link",
                "label": "Run Max texture manifest link",
                "operator_action": "Run python dcc-hosts/3dsmax-rule-adapter/scripts/run_texture_manifest_link.py.",
                "evidence_expected": "Max pymxs material bitmap slots are checked against package entries, channel semantics, color-space policy and platform resolution budgets.",
            },
            {
                "id": "42-review-houdini-adapter",
                "label": "Review Houdini rule adapter",
                "operator_action": "Open the Presenter Pack or public package and inspect the Houdini Rule Adapter contract artifact.",
                "evidence_expected": "HDA metadata, detail attributes, OUT_* role nodes, packed prototypes, PDG wedges and bake receipts normalize into Cross-DCC rule input.",
            },
            {
                "id": "43-run-houdini-l3-readiness",
                "label": "Run Houdini hython L3 readiness",
                "operator_action": "Run python dcc-hosts/houdini-rule-adapter/scripts/run_l3_smoke.py.",
                "evidence_expected": "The launcher either runs hython collection or exports a clear blocked readiness gate when hython.exe is not available.",
            },
            {
                "id": "44-audit-gui-media",
                "label": "Audit GUI media",
                "operator_action": "Click Audit Media or Export Presenter Pack after placing real Maya screenshots and recording.",
                "evidence_expected": "Media audit reports Present / Review / Missing for 9 screenshots and 1 recording.",
            },
            {
                "id": "45-handoff-presenter-pack",
                "label": "Handoff presenter pack",
                "operator_action": "Click Export Presenter Pack and open the generated JSON artifact.",
                "evidence_expected": "Pack lists route, public package, artifact probes, media gate, and mutation boundaries.",
            },
        ]

        capture_next_actions: List[Dict[str, Any]] = []
        if media_summary["missing"] or media_summary["review"]:
            capture_next_actions.append(
                {
                    "id": "capture-real-maya-media",
                    "owner": "tool-ta",
                    "state": "open",
                    "reason": "Presenter pack has code and JSON evidence, but Maya screenshots/recording are not yet complete.",
                    "target": media_audit["media_root"],
                    "missing": media_summary["missing"],
                    "review": media_summary["review"],
                }
            )
        if missing_required:
            capture_next_actions.append(
                {
                    "id": "restore-required-evidence",
                    "owner": "tool-ta",
                    "state": "blocked",
                    "reason": "Required public evidence files are missing from the local package.",
                    "missing_files": [row["id"] for row in missing_required],
                }
            )

        return {
            "ok": True,
            "schema": "maya-dcc-presentation-pack@0.1.0",
            "label": label,
            "title": "AI Tool TA DCC Presenter Pack",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "host": {
                "dcc": "Autodesk Maya",
                "mayaVersion": "2024",
                "frontendHost": "AuroraView",
                "entry": "from ai_tool_ta_maya_host import show_portfolio; show_portfolio()",
            },
            "summary": {
                "gate": gate,
                "package_id": manifest.get("packageId"),
                "package_version": manifest.get("packageVersion"),
                "source_gate": manifest.get("sourceCaseGate", manifest.get("gate")),
                "module_count": manifest_summary.get("moduleCount"),
                "business_route_steps": manifest_summary.get("businessRouteSteps", len(runbook_plan["presentation_route"])),
                "demo_route_steps": len(demo_route),
                "evidence_files": len(evidence_files),
                "present_evidence_files": sum(1 for row in evidence_files if row["exists"]),
                "missing_required_files": len(missing_required),
                "required_media_files": media_summary["required_files"],
                "gui_media_present": media_summary["present"],
                "gui_media_review": media_summary["review"],
                "gui_media_missing": media_summary["missing"],
                "engine_preset_platform_split": manifest_summary.get("enginePresetComparisonPlatformSplit"),
                "engine_preset_held_across_presets": manifest_summary.get("enginePresetComparisonHeldAcrossPresets"),
                "unreal_preset_fact_comparison_gate": manifest_summary.get("unrealPresetFactComparisonGate"),
                "unreal_preset_fact_comparison_presets": manifest_summary.get("unrealPresetFactComparisonPresets"),
                "unreal_preset_fact_comparison_assets": manifest_summary.get("unrealPresetFactComparisonAssets"),
                "unreal_preset_fact_comparison_rows": manifest_summary.get("unrealPresetFactComparisonRows"),
                "unreal_preset_fact_comparison_matched": manifest_summary.get("unrealPresetFactComparisonMatched"),
                "unreal_preset_fact_comparison_drift": manifest_summary.get("unrealPresetFactComparisonDrift"),
                "unreal_preset_fact_comparison_waived": manifest_summary.get("unrealPresetFactComparisonWaived"),
                "unreal_preset_fact_comparison_blocked": manifest_summary.get("unrealPresetFactComparisonBlocked"),
                "unreal_preset_fact_comparison_platform_split": manifest_summary.get("unrealPresetFactComparisonPlatformSplit"),
                "unreal_preset_fact_comparison_approved_waivers": manifest_summary.get("unrealPresetFactComparisonApprovedWaivers"),
                "unreal_preset_fact_review_gate": manifest_summary.get("unrealPresetFactReviewGate"),
                "unreal_preset_fact_review_rows": manifest_summary.get("unrealPresetFactReviewRows"),
                "unreal_preset_fact_review_attention_rows": manifest_summary.get("unrealPresetFactReviewAttentionRows"),
                "unreal_preset_fact_review_blocked": manifest_summary.get("unrealPresetFactReviewBlocked"),
                "unreal_preset_fact_review_waivers": manifest_summary.get("unrealPresetFactReviewWaivers"),
                "scene_transaction_guard_gate": manifest_summary.get("sceneTransactionGuardGate"),
                "scene_transaction_guard_created": manifest_summary.get("sceneTransactionGuardCreated"),
                "scene_transaction_guard_deleted": manifest_summary.get("sceneTransactionGuardDeleted"),
                "scene_transaction_guard_modified": manifest_summary.get("sceneTransactionGuardModified"),
                "scene_transaction_guard_rollback_actions": manifest_summary.get("sceneTransactionGuardRollbackActions"),
                "scene_transaction_guard_risk_rows": manifest_summary.get("sceneTransactionGuardRiskRows"),
                "animation_continuity_gate": manifest_summary.get("animationContinuityGate"),
                "animation_continuity_evidence_level": manifest_summary.get("animationContinuityEvidenceLevel"),
                "animation_continuity_l3_status": manifest_summary.get("animationContinuityL3Status"),
                "animation_continuity_maya_version": manifest_summary.get("animationContinuityMayaVersion"),
                "animation_continuity_runtime_collected": manifest_summary.get("animationContinuityRuntimeCollected"),
                "animation_continuity_assets": manifest_summary.get("animationContinuityAssets"),
                "animation_continuity_ready": manifest_summary.get("animationContinuityReady"),
                "animation_continuity_blocked": manifest_summary.get("animationContinuityBlocked"),
                "animation_continuity_pass_checks": manifest_summary.get("animationContinuityPassChecks"),
                "animation_continuity_warning_checks": manifest_summary.get("animationContinuityWarningChecks"),
                "animation_continuity_error_checks": manifest_summary.get("animationContinuityErrorChecks"),
                "unreal_animation_bridge_gate": manifest_summary.get("unrealAnimationBridgeGate"),
                "unreal_animation_bridge_evidence_level": manifest_summary.get("unrealAnimationBridgeEvidenceLevel"),
                "unreal_animation_bridge_l3_status": manifest_summary.get("unrealAnimationBridgeL3Status"),
                "unreal_animation_bridge_engine_version": manifest_summary.get("unrealAnimationBridgeEngineVersion"),
                "unreal_animation_bridge_api_probe": manifest_summary.get("unrealAnimationBridgeApiProbe"),
                "unreal_animation_bridge_assets": manifest_summary.get("unrealAnimationBridgeAssets"),
                "unreal_animation_bridge_ready": manifest_summary.get("unrealAnimationBridgeReady"),
                "unreal_animation_bridge_review": manifest_summary.get("unrealAnimationBridgeReview"),
                "unreal_animation_bridge_blocked": manifest_summary.get("unrealAnimationBridgeBlocked"),
                "unreal_animation_bridge_pass_checks": manifest_summary.get("unrealAnimationBridgePassChecks"),
                "unreal_animation_bridge_warning_checks": manifest_summary.get("unrealAnimationBridgeWarningChecks"),
                "unreal_animation_bridge_error_checks": manifest_summary.get("unrealAnimationBridgeErrorChecks"),
                "unreal_animation_bridge_missing_sequences": manifest_summary.get("unrealAnimationBridgeMissingSequences"),
                "unreal_animation_bridge_import_success": manifest_summary.get("unrealAnimationBridgeImportSuccess"),
                "unreal_animation_bridge_imported_assets": manifest_summary.get("unrealAnimationBridgeImportedAssets"),
                "unreal_animation_bridge_runtime_assets_present": manifest_summary.get("unrealAnimationBridgeRuntimeAssetsPresent"),
                "unreal_animation_deep_facts_gate": manifest_summary.get("unrealAnimationDeepFactsGate"),
                "unreal_animation_deep_facts_evidence_level": manifest_summary.get("unrealAnimationDeepFactsEvidenceLevel"),
                "unreal_animation_deep_facts_l3_status": manifest_summary.get("unrealAnimationDeepFactsL3Status"),
                "unreal_animation_deep_facts_engine_version": manifest_summary.get("unrealAnimationDeepFactsEngineVersion"),
                "unreal_animation_deep_facts_assets": manifest_summary.get("unrealAnimationDeepFactsAssets"),
                "unreal_animation_deep_facts_ready": manifest_summary.get("unrealAnimationDeepFactsReady"),
                "unreal_animation_deep_facts_review": manifest_summary.get("unrealAnimationDeepFactsReview"),
                "unreal_animation_deep_facts_blocked": manifest_summary.get("unrealAnimationDeepFactsBlocked"),
                "unreal_animation_deep_facts_pass_checks": manifest_summary.get("unrealAnimationDeepFactsPassChecks"),
                "unreal_animation_deep_facts_warning_checks": manifest_summary.get("unrealAnimationDeepFactsWarningChecks"),
                "unreal_animation_deep_facts_error_checks": manifest_summary.get("unrealAnimationDeepFactsErrorChecks"),
                "unreal_animation_deep_facts_runtime_rows": manifest_summary.get("unrealAnimationDeepFactsRuntimeRowsCollected"),
                "unreal_animation_deep_facts_duration_matched": manifest_summary.get("unrealAnimationDeepFactsDurationRowsMatched"),
                "unreal_animation_deep_facts_curve_readable": manifest_summary.get("unrealAnimationDeepFactsCurveMetadataReadable"),
                "unreal_animation_deep_facts_root_readable": manifest_summary.get("unrealAnimationDeepFactsRootMotionReadable"),
                "unreal_animation_deep_facts_compression_readable": manifest_summary.get("unrealAnimationDeepFactsCompressionReadable"),
                "unreal_animation_deep_facts_asset_writes": manifest_summary.get("unrealAnimationDeepFactsAssetWrites"),
                "character_calibration_gate": manifest_summary.get("characterCalibrationGate"),
                "character_calibration_evidence_level": manifest_summary.get("characterCalibrationEvidenceLevel"),
                "character_calibration_l3_status": manifest_summary.get("characterCalibrationL3Status"),
                "character_calibration_maya_version": manifest_summary.get("characterCalibrationMayaVersion"),
                "character_calibration_runtime_collected": manifest_summary.get("characterCalibrationRuntimeCollected"),
                "character_calibration_assets": manifest_summary.get("characterCalibrationAssets"),
                "character_calibration_ready": manifest_summary.get("characterCalibrationReady"),
                "character_calibration_review": manifest_summary.get("characterCalibrationReview"),
                "character_calibration_blocked": manifest_summary.get("characterCalibrationBlocked"),
                "character_calibration_pass_checks": manifest_summary.get("characterCalibrationPassChecks"),
                "character_calibration_warning_checks": manifest_summary.get("characterCalibrationWarningChecks"),
                "character_calibration_error_checks": manifest_summary.get("characterCalibrationErrorChecks"),
                "character_calibration_drilldown_gate": manifest_summary.get("characterCalibrationDrilldownGate"),
                "character_calibration_drilldown_evidence_level": manifest_summary.get("characterCalibrationDrilldownEvidenceLevel"),
                "character_calibration_drilldown_l3_status": manifest_summary.get("characterCalibrationDrilldownL3Status"),
                "character_calibration_drilldown_assets": manifest_summary.get("characterCalibrationDrilldownAssets"),
                "character_calibration_drilldown_panels": manifest_summary.get("characterCalibrationDrilldownPanels"),
                "character_calibration_drilldown_owner_actions": manifest_summary.get("characterCalibrationDrilldownOwnerActions"),
                "character_calibration_drilldown_owner_required": manifest_summary.get("characterCalibrationDrilldownOwnerRequired"),
                "character_calibration_drilldown_manual_review": manifest_summary.get("characterCalibrationDrilldownManualReview"),
                "character_calibration_drilldown_issues": manifest_summary.get("characterCalibrationDrilldownIssues"),
                "unreal_control_rig_bridge_gate": manifest_summary.get("unrealControlRigBridgeGate"),
                "unreal_control_rig_bridge_evidence_level": manifest_summary.get("unrealControlRigBridgeEvidenceLevel"),
                "unreal_control_rig_bridge_l3_status": manifest_summary.get("unrealControlRigBridgeL3Status"),
                "unreal_control_rig_bridge_engine_version": manifest_summary.get("unrealControlRigBridgeEngineVersion"),
                "unreal_control_rig_bridge_characters": manifest_summary.get("unrealControlRigBridgeCharacters"),
                "unreal_control_rig_bridge_ready": manifest_summary.get("unrealControlRigBridgeReady"),
                "unreal_control_rig_bridge_review": manifest_summary.get("unrealControlRigBridgeReview"),
                "unreal_control_rig_bridge_blocked": manifest_summary.get("unrealControlRigBridgeBlocked"),
                "unreal_control_rig_bridge_pass_checks": manifest_summary.get("unrealControlRigBridgePassChecks"),
                "unreal_control_rig_bridge_warning_checks": manifest_summary.get("unrealControlRigBridgeWarningChecks"),
                "unreal_control_rig_bridge_error_checks": manifest_summary.get("unrealControlRigBridgeErrorChecks"),
                "unreal_control_rig_bridge_asset_writes": manifest_summary.get("unrealControlRigBridgeAssetWrites"),
                "unreal_control_rig_fixture_authoring_gate": manifest_summary.get("unrealControlRigFixtureAuthoringGate"),
                "unreal_control_rig_fixture_authoring_evidence_level": manifest_summary.get("unrealControlRigFixtureAuthoringEvidenceLevel"),
                "unreal_control_rig_fixture_authoring_l3_status": manifest_summary.get("unrealControlRigFixtureAuthoringL3Status"),
                "unreal_control_rig_fixture_authoring_engine_version": manifest_summary.get("unrealControlRigFixtureAuthoringEngineVersion"),
                "unreal_control_rig_fixture_authoring_operations": manifest_summary.get("unrealControlRigFixtureAuthoringOperations"),
                "unreal_control_rig_fixture_authoring_held_rows": manifest_summary.get("unrealControlRigFixtureAuthoringHeldRows"),
                "unreal_control_rig_fixture_authoring_created_assets": manifest_summary.get("unrealControlRigFixtureAuthoringCreatedAssets"),
                "unreal_control_rig_fixture_authoring_saved_assets": manifest_summary.get("unrealControlRigFixtureAuthoringSavedAssets"),
                "unreal_control_rig_fixture_authoring_hierarchy_readable": manifest_summary.get("unrealControlRigFixtureAuthoringHierarchyReadable"),
                "unreal_control_rig_fixture_authoring_required_controls": manifest_summary.get("unrealControlRigFixtureAuthoringRequiredControls"),
                "unreal_control_rig_fixture_authoring_runtime_controls": manifest_summary.get("unrealControlRigFixtureAuthoringRuntimeControls"),
                "unreal_control_rig_fixture_authoring_missing_controls": manifest_summary.get("unrealControlRigFixtureAuthoringMissingControls"),
                "unreal_control_rig_fixture_authoring_asset_writes": manifest_summary.get("unrealControlRigFixtureAuthoringAssetWrites"),
                "unreal_control_rig_fixture_authoring_production_writes": manifest_summary.get("unrealControlRigFixtureAuthoringProductionWrites"),
                "unreal_control_rig_face_skeleton_fixture_gate": manifest_summary.get("unrealControlRigFaceSkeletonFixtureGate"),
                "unreal_control_rig_face_skeleton_fixture_evidence_level": manifest_summary.get("unrealControlRigFaceSkeletonFixtureEvidenceLevel"),
                "unreal_control_rig_face_skeleton_fixture_l3_status": manifest_summary.get("unrealControlRigFaceSkeletonFixtureL3Status"),
                "unreal_control_rig_face_skeleton_fixture_engine_version": manifest_summary.get("unrealControlRigFaceSkeletonFixtureEngineVersion"),
                "unreal_control_rig_face_skeleton_fixture_required_targets": manifest_summary.get("unrealControlRigFaceSkeletonFixtureRequiredTargets"),
                "unreal_control_rig_face_skeleton_fixture_target_matches": manifest_summary.get("unrealControlRigFaceSkeletonFixtureTargetMatches"),
                "unreal_control_rig_face_skeleton_fixture_previous_missing": manifest_summary.get("unrealControlRigFaceSkeletonFixturePreviousMissing"),
                "unreal_control_rig_face_skeleton_fixture_previous_missing_resolved": manifest_summary.get("unrealControlRigFaceSkeletonFixturePreviousMissingResolved"),
                "unreal_control_rig_face_skeleton_fixture_asset_writes": manifest_summary.get("unrealControlRigFaceSkeletonFixtureAssetWrites"),
                "unreal_control_rig_face_skeleton_fixture_production_writes": manifest_summary.get("unrealControlRigFaceSkeletonFixtureProductionWrites"),
                "unreal_control_rig_deformation_link_gate": manifest_summary.get("unrealControlRigDeformationLinkGate"),
                "unreal_control_rig_deformation_link_evidence_level": manifest_summary.get("unrealControlRigDeformationLinkEvidenceLevel"),
                "unreal_control_rig_deformation_link_l3_status": manifest_summary.get("unrealControlRigDeformationLinkL3Status"),
                "unreal_control_rig_deformation_link_engine_version": manifest_summary.get("unrealControlRigDeformationLinkEngineVersion"),
                "unreal_control_rig_deformation_link_characters": manifest_summary.get("unrealControlRigDeformationLinkCharacters"),
                "unreal_control_rig_deformation_link_ready": manifest_summary.get("unrealControlRigDeformationLinkReady"),
                "unreal_control_rig_deformation_link_review": manifest_summary.get("unrealControlRigDeformationLinkReview"),
                "unreal_control_rig_deformation_link_blocked": manifest_summary.get("unrealControlRigDeformationLinkBlocked"),
                "unreal_control_rig_deformation_link_controls": manifest_summary.get("unrealControlRigDeformationLinkControls"),
                "unreal_control_rig_deformation_link_runtime_controls": manifest_summary.get("unrealControlRigDeformationLinkRuntimeControls"),
                "unreal_control_rig_deformation_link_skeleton_matches": manifest_summary.get("unrealControlRigDeformationLinkSkeletonMatches"),
                "unreal_control_rig_deformation_link_shape_or_offset_readable": manifest_summary.get("unrealControlRigDeformationLinkShapeOrOffsetReadable"),
                "unreal_control_rig_deformation_link_compile_api_visible": manifest_summary.get("unrealControlRigDeformationLinkCompileApiVisible"),
                "unreal_control_rig_deformation_link_direct_compile_status": manifest_summary.get("unrealControlRigDeformationLinkDirectCompileStatus"),
                "unreal_control_rig_deformation_link_pass_checks": manifest_summary.get("unrealControlRigDeformationLinkPassChecks"),
                "unreal_control_rig_deformation_link_warning_checks": manifest_summary.get("unrealControlRigDeformationLinkWarningChecks"),
                "unreal_control_rig_deformation_link_error_checks": manifest_summary.get("unrealControlRigDeformationLinkErrorChecks"),
                "unreal_control_rig_deformation_link_owner_actions": manifest_summary.get("unrealControlRigDeformationLinkOwnerActions"),
                "unreal_control_rig_deformation_link_asset_writes": manifest_summary.get("unrealControlRigDeformationLinkAssetWrites"),
                "unreal_control_rig_deformation_link_production_writes": manifest_summary.get("unrealControlRigDeformationLinkProductionWrites"),
                "unreal_control_rig_compile_status_gate": manifest_summary.get("unrealControlRigCompileStatusGate"),
                "unreal_control_rig_compile_status_evidence_level": manifest_summary.get("unrealControlRigCompileStatusEvidenceLevel"),
                "unreal_control_rig_compile_status_l3_status": manifest_summary.get("unrealControlRigCompileStatusL3Status"),
                "unreal_control_rig_compile_status_engine_version": manifest_summary.get("unrealControlRigCompileStatusEngineVersion"),
                "unreal_control_rig_compile_status_characters": manifest_summary.get("unrealControlRigCompileStatusCharacters"),
                "unreal_control_rig_compile_status_ready": manifest_summary.get("unrealControlRigCompileStatusReady"),
                "unreal_control_rig_compile_status_review": manifest_summary.get("unrealControlRigCompileStatusReview"),
                "unreal_control_rig_compile_status_blocked": manifest_summary.get("unrealControlRigCompileStatusBlocked"),
                "unreal_control_rig_compile_status_candidates": manifest_summary.get("unrealControlRigCompileStatusCandidates"),
                "unreal_control_rig_compile_status_methods_visible": manifest_summary.get("unrealControlRigCompileStatusMethodsVisible"),
                "unreal_control_rig_compile_status_invoked": manifest_summary.get("unrealControlRigCompileStatusInvoked"),
                "unreal_control_rig_compile_status_succeeded": manifest_summary.get("unrealControlRigCompileStatusSucceeded"),
                "unreal_control_rig_compile_status_direct_status": manifest_summary.get("unrealControlRigCompileStatusDirectStatus"),
                "unreal_control_rig_compile_status_diagnostics": manifest_summary.get("unrealControlRigCompileStatusDiagnostics"),
                "unreal_control_rig_compile_status_settings": manifest_summary.get("unrealControlRigCompileStatusSettings"),
                "unreal_control_rig_compile_status_dirty_after": manifest_summary.get("unrealControlRigCompileStatusDirtyAfter"),
                "unreal_control_rig_compile_status_pass_checks": manifest_summary.get("unrealControlRigCompileStatusPassChecks"),
                "unreal_control_rig_compile_status_warning_checks": manifest_summary.get("unrealControlRigCompileStatusWarningChecks"),
                "unreal_control_rig_compile_status_error_checks": manifest_summary.get("unrealControlRigCompileStatusErrorChecks"),
                "unreal_control_rig_compile_status_asset_writes": manifest_summary.get("unrealControlRigCompileStatusAssetWrites"),
                "unreal_control_rig_compile_status_production_writes": manifest_summary.get("unrealControlRigCompileStatusProductionWrites"),
                "groom_export_inspector_gate": manifest_summary.get("groomExportInspectorGate"),
                "groom_export_inspector_evidence_level": manifest_summary.get("groomExportInspectorEvidenceLevel"),
                "groom_export_inspector_l3_status": manifest_summary.get("groomExportInspectorL3Status"),
                "groom_export_inspector_maya_version": manifest_summary.get("groomExportInspectorMayaVersion"),
                "groom_export_inspector_runtime_collected": manifest_summary.get("groomExportInspectorRuntimeCollected"),
                "groom_export_inspector_assets": manifest_summary.get("groomExportInspectorAssets"),
                "groom_export_inspector_ready": manifest_summary.get("groomExportInspectorReady"),
                "groom_export_inspector_review": manifest_summary.get("groomExportInspectorReview"),
                "groom_export_inspector_blocked": manifest_summary.get("groomExportInspectorBlocked"),
                "groom_export_inspector_pass_checks": manifest_summary.get("groomExportInspectorPassChecks"),
                "groom_export_inspector_warning_checks": manifest_summary.get("groomExportInspectorWarningChecks"),
                "groom_export_inspector_error_checks": manifest_summary.get("groomExportInspectorErrorChecks"),
                "groom_export_inspector_strands": manifest_summary.get("groomExportInspectorStrands"),
                "groom_export_inspector_guides": manifest_summary.get("groomExportInspectorGuides"),
                "groom_export_inspector_root_uv_missing": manifest_summary.get("groomExportInspectorRootUVMissing"),
                "groom_export_inspector_duplicate_strand_ids": manifest_summary.get("groomExportInspectorDuplicateStrandIds"),
                "groom_export_inspector_owner_actions": manifest_summary.get("groomExportInspectorOwnerActions"),
                "groom_export_inspector_asset_writes": manifest_summary.get("groomExportInspectorAssetWrites"),
                "groom_export_inspector_production_writes": manifest_summary.get("groomExportInspectorProductionWrites"),
                "groom_unreal_readiness_gate": manifest_summary.get("groomUnrealReadinessGate"),
                "groom_unreal_readiness_evidence_level": manifest_summary.get("groomUnrealReadinessEvidenceLevel"),
                "groom_unreal_readiness_l3_status": manifest_summary.get("groomUnrealReadinessL3Status"),
                "groom_unreal_readiness_engine_version": manifest_summary.get("groomUnrealReadinessEngineVersion"),
                "groom_unreal_readiness_assets": manifest_summary.get("groomUnrealReadinessAssets"),
                "groom_unreal_readiness_source_ready": manifest_summary.get("groomUnrealReadinessSourceReady"),
                "groom_unreal_readiness_source_blocked": manifest_summary.get("groomUnrealReadinessSourceBlocked"),
                "groom_unreal_readiness_groom_api_visible": manifest_summary.get("groomUnrealReadinessGroomApiVisible"),
                "groom_unreal_readiness_import_task_visible": manifest_summary.get("groomUnrealReadinessImportTaskVisible"),
                "groom_unreal_readiness_alembic_factory_visible": manifest_summary.get("groomUnrealReadinessAlembicFactoryVisible"),
                "groom_unreal_readiness_target_meshes": manifest_summary.get("groomUnrealReadinessTargetMeshesPresent"),
                "groom_unreal_readiness_expected_groom_assets": manifest_summary.get("groomUnrealReadinessExpectedGroomAssetsPresent"),
                "groom_unreal_readiness_expected_binding_assets": manifest_summary.get("groomUnrealReadinessExpectedBindingAssetsPresent"),
                "groom_unreal_readiness_cache_contract_ready": manifest_summary.get("groomUnrealReadinessCacheContractReady"),
                "groom_unreal_readiness_pass_checks": manifest_summary.get("groomUnrealReadinessPassChecks"),
                "groom_unreal_readiness_warning_checks": manifest_summary.get("groomUnrealReadinessWarningChecks"),
                "groom_unreal_readiness_error_checks": manifest_summary.get("groomUnrealReadinessErrorChecks"),
                "groom_unreal_readiness_owner_actions": manifest_summary.get("groomUnrealReadinessOwnerActions"),
                "groom_unreal_readiness_asset_writes": manifest_summary.get("groomUnrealReadinessAssetWrites"),
                "groom_unreal_readiness_production_writes": manifest_summary.get("groomUnrealReadinessProductionWrites"),
                "groom_alembic_payload_gate": manifest_summary.get("groomAlembicPayloadGate"),
                "groom_alembic_payload_evidence_level": manifest_summary.get("groomAlembicPayloadEvidenceLevel"),
                "groom_alembic_payload_l3_status": manifest_summary.get("groomAlembicPayloadL3Status"),
                "groom_alembic_payload_maya_version": manifest_summary.get("groomAlembicPayloadMayaVersion"),
                "groom_alembic_payload_assets": manifest_summary.get("groomAlembicPayloadAssets"),
                "groom_alembic_payload_selected": manifest_summary.get("groomAlembicPayloadSelected"),
                "groom_alembic_payload_held": manifest_summary.get("groomAlembicPayloadHeld"),
                "groom_alembic_payload_export_succeeded": manifest_summary.get("groomAlembicPayloadExportSucceeded"),
                "groom_alembic_payload_cache_files": manifest_summary.get("groomAlembicPayloadCacheFiles"),
                "groom_alembic_payload_cache_bytes": manifest_summary.get("groomAlembicPayloadCacheBytes"),
                "groom_alembic_payload_cache_hashes": manifest_summary.get("groomAlembicPayloadCacheHashes"),
                "groom_alembic_payload_pass_checks": manifest_summary.get("groomAlembicPayloadPassChecks"),
                "groom_alembic_payload_warning_checks": manifest_summary.get("groomAlembicPayloadWarningChecks"),
                "groom_alembic_payload_error_checks": manifest_summary.get("groomAlembicPayloadErrorChecks"),
                "groom_alembic_payload_owner_actions": manifest_summary.get("groomAlembicPayloadOwnerActions"),
                "groom_alembic_payload_asset_writes": manifest_summary.get("groomAlembicPayloadAssetWrites"),
                "groom_alembic_payload_engine_writes": manifest_summary.get("groomAlembicPayloadEngineWrites"),
                "groom_alembic_payload_production_writes": manifest_summary.get("groomAlembicPayloadProductionWrites"),
                "groom_alembic_import_postcheck_gate": manifest_summary.get("groomAlembicImportPostcheckGate"),
                "groom_alembic_import_postcheck_evidence_level": manifest_summary.get("groomAlembicImportPostcheckEvidenceLevel"),
                "groom_alembic_import_postcheck_l3_status": manifest_summary.get("groomAlembicImportPostcheckL3Status"),
                "groom_alembic_import_postcheck_engine_version": manifest_summary.get("groomAlembicImportPostcheckEngineVersion"),
                "groom_alembic_import_postcheck_operations": manifest_summary.get("groomAlembicImportPostcheckOperations"),
                "groom_alembic_import_postcheck_candidates": manifest_summary.get("groomAlembicImportPostcheckCandidates"),
                "groom_alembic_import_postcheck_cache_hash_matched": manifest_summary.get("groomAlembicImportPostcheckCacheHashMatched"),
                "groom_alembic_import_postcheck_task_dry_run": manifest_summary.get("groomAlembicImportPostcheckTaskDryRunRows"),
                "groom_alembic_import_postcheck_alembic_factory_visible": manifest_summary.get("groomAlembicImportPostcheckAlembicFactoryVisible"),
                "groom_alembic_import_postcheck_groom_api_ready": manifest_summary.get("groomAlembicImportPostcheckGroomApiReady"),
                "groom_alembic_import_postcheck_target_meshes": manifest_summary.get("groomAlembicImportPostcheckTargetMeshesPresent"),
                "groom_alembic_import_postcheck_import_executed": manifest_summary.get("groomAlembicImportPostcheckImportExecuted"),
                "groom_alembic_import_postcheck_import_held": manifest_summary.get("groomAlembicImportPostcheckImportHeld"),
                "groom_alembic_import_postcheck_pass_checks": manifest_summary.get("groomAlembicImportPostcheckPassChecks"),
                "groom_alembic_import_postcheck_warning_checks": manifest_summary.get("groomAlembicImportPostcheckWarningChecks"),
                "groom_alembic_import_postcheck_error_checks": manifest_summary.get("groomAlembicImportPostcheckErrorChecks"),
                "groom_alembic_import_postcheck_owner_actions": manifest_summary.get("groomAlembicImportPostcheckOwnerActions"),
                "groom_alembic_import_postcheck_asset_writes": manifest_summary.get("groomAlembicImportPostcheckAssetWrites"),
                "groom_alembic_import_postcheck_engine_writes": manifest_summary.get("groomAlembicImportPostcheckEngineWrites"),
                "groom_alembic_import_postcheck_production_writes": manifest_summary.get("groomAlembicImportPostcheckProductionWrites"),
                "groom_plugin_api_fixture_gate": manifest_summary.get("groomPluginApiFixtureGate"),
                "groom_plugin_api_fixture_evidence_level": manifest_summary.get("groomPluginApiFixtureEvidenceLevel"),
                "groom_plugin_api_fixture_l3_status": manifest_summary.get("groomPluginApiFixtureL3Status"),
                "groom_plugin_api_fixture_engine_version": manifest_summary.get("groomPluginApiFixtureEngineVersion"),
                "groom_plugin_api_fixture_project_requested": manifest_summary.get("groomPluginApiFixtureProjectRequestedRows"),
                "groom_plugin_api_fixture_descriptors_found": manifest_summary.get("groomPluginApiFixtureDescriptorRowsFound"),
                "groom_plugin_api_fixture_groom_classes": manifest_summary.get("groomPluginApiFixtureGroomClassNameRows"),
                "groom_plugin_api_fixture_hair_classes": manifest_summary.get("groomPluginApiFixtureHairClassNameRows"),
                "groom_plugin_api_fixture_alembic_classes": manifest_summary.get("groomPluginApiFixtureAlembicClassNameRows"),
                "groom_plugin_api_fixture_geometry_cache_classes": manifest_summary.get("groomPluginApiFixtureGeometryCacheClassNameRows"),
                "groom_plugin_api_fixture_groom_import_api_ready": manifest_summary.get("groomPluginApiFixtureGroomImportApiReady"),
                "groom_plugin_api_fixture_alembic_factory_visible": manifest_summary.get("groomPluginApiFixtureAlembicImportFactoryVisible"),
                "groom_plugin_api_fixture_asset_writes": manifest_summary.get("groomPluginApiFixtureAssetWrites"),
                "groom_plugin_api_fixture_engine_writes": manifest_summary.get("groomPluginApiFixtureEngineWrites"),
                "groom_plugin_api_fixture_production_writes": manifest_summary.get("groomPluginApiFixtureProductionWrites"),
                "groom_controlled_executor_gate": manifest_summary.get("groomControlledExecutorGate"),
                "groom_controlled_executor_evidence_level": manifest_summary.get("groomControlledExecutorEvidenceLevel"),
                "groom_controlled_executor_l3_status": manifest_summary.get("groomControlledExecutorL3Status"),
                "groom_controlled_executor_engine_version": manifest_summary.get("groomControlledExecutorEngineVersion"),
                "groom_controlled_executor_selected": manifest_summary.get("groomControlledExecutorSelectedOperations"),
                "groom_controlled_executor_import_attempted": manifest_summary.get("groomControlledExecutorImportAttempted"),
                "groom_controlled_executor_import_succeeded": manifest_summary.get("groomControlledExecutorImportSucceeded"),
                "groom_controlled_executor_imported_asset_class": manifest_summary.get("groomControlledExecutorImportedAssetClass"),
                "groom_controlled_executor_wrong_imported_class": manifest_summary.get("groomControlledExecutorWrongImportedClass"),
                "groom_controlled_executor_groom_postcheck": manifest_summary.get("groomControlledExecutorGroomPostCheckPassed"),
                "groom_controlled_executor_binding_attempted": manifest_summary.get("groomControlledExecutorBindingAttempted"),
                "groom_controlled_executor_binding_succeeded": manifest_summary.get("groomControlledExecutorBindingSucceeded"),
                "groom_controlled_executor_binding_postcheck": manifest_summary.get("groomControlledExecutorBindingPostCheckPassed"),
                "groom_controlled_executor_rollback": manifest_summary.get("groomControlledExecutorRollbackPassed"),
                "groom_controlled_executor_residual_assets": manifest_summary.get("groomControlledExecutorResidualAssetCount"),
                "groom_controlled_executor_asset_writes": manifest_summary.get("groomControlledExecutorAssetWrites"),
                "groom_controlled_executor_engine_writes": manifest_summary.get("groomControlledExecutorEngineWrites"),
                "groom_controlled_executor_production_writes": manifest_summary.get("groomControlledExecutorProductionWrites"),
                "groom_runtime_facts_gate": manifest_summary.get("groomRuntimeFactsGate"),
                "groom_runtime_facts_evidence_level": manifest_summary.get("groomRuntimeFactsEvidenceLevel"),
                "groom_runtime_facts_l3_status": manifest_summary.get("groomRuntimeFactsL3Status"),
                "groom_runtime_facts_engine_version": manifest_summary.get("groomRuntimeFactsEngineVersion"),
                "groom_runtime_facts_runtime_assets_present": manifest_summary.get("groomRuntimeFactsRuntimeAssetsPresent"),
                "groom_runtime_facts_readable_properties": manifest_summary.get("groomRuntimeFactsReadableProperties"),
                "groom_runtime_facts_method_surface": manifest_summary.get("groomRuntimeFactsMethodSurface"),
                "groom_runtime_facts_call_results": manifest_summary.get("groomRuntimeFactsCallResults"),
                "groom_runtime_facts_rollback": manifest_summary.get("groomRuntimeFactsRollbackPassed"),
                "groom_runtime_facts_residual_assets": manifest_summary.get("groomRuntimeFactsResidualAssetCount"),
                "groom_runtime_facts_pass_checks": manifest_summary.get("groomRuntimeFactsPassChecks"),
                "groom_runtime_facts_warning_checks": manifest_summary.get("groomRuntimeFactsWarningChecks"),
                "groom_runtime_facts_error_checks": manifest_summary.get("groomRuntimeFactsErrorChecks"),
                "groom_runtime_facts_asset_writes": manifest_summary.get("groomRuntimeFactsAssetWrites"),
                "groom_runtime_facts_production_writes": manifest_summary.get("groomRuntimeFactsProductionWrites"),
                "spatial_authoring_gate": manifest_summary.get("spatialAuthoringGate"),
                "spatial_authoring_evidence_level": manifest_summary.get("spatialAuthoringEvidenceLevel"),
                "spatial_authoring_l3_status": manifest_summary.get("spatialAuthoringL3Status"),
                "spatial_authoring_maya_version": manifest_summary.get("spatialAuthoringMayaVersion"),
                "spatial_authoring_runtime_collected": manifest_summary.get("spatialAuthoringRuntimeCollected"),
                "spatial_authoring_assets": manifest_summary.get("spatialAuthoringAssets"),
                "spatial_authoring_ready": manifest_summary.get("spatialAuthoringReady"),
                "spatial_authoring_review": manifest_summary.get("spatialAuthoringReview"),
                "spatial_authoring_blocked": manifest_summary.get("spatialAuthoringBlocked"),
                "spatial_authoring_pass_checks": manifest_summary.get("spatialAuthoringPassChecks"),
                "spatial_authoring_warning_checks": manifest_summary.get("spatialAuthoringWarningChecks"),
                "spatial_authoring_error_checks": manifest_summary.get("spatialAuthoringErrorChecks"),
                "spatial_authoring_drilldown_gate": manifest_summary.get("spatialAuthoringDrilldownGate"),
                "spatial_authoring_drilldown_evidence_level": manifest_summary.get("spatialAuthoringDrilldownEvidenceLevel"),
                "spatial_authoring_drilldown_l3_status": manifest_summary.get("spatialAuthoringDrilldownL3Status"),
                "spatial_authoring_drilldown_assets": manifest_summary.get("spatialAuthoringDrilldownAssets"),
                "spatial_authoring_drilldown_panels": manifest_summary.get("spatialAuthoringDrilldownPanels"),
                "spatial_authoring_drilldown_owner_actions": manifest_summary.get("spatialAuthoringDrilldownOwnerActions"),
                "spatial_authoring_drilldown_owner_required": manifest_summary.get("spatialAuthoringDrilldownOwnerRequired"),
                "spatial_authoring_drilldown_manual_review": manifest_summary.get("spatialAuthoringDrilldownManualReview"),
                "spatial_authoring_drilldown_issues": manifest_summary.get("spatialAuthoringDrilldownIssues"),
                "unreal_socket_import_checker_gate": manifest_summary.get("unrealSocketImportCheckerGate"),
                "unreal_socket_import_checker_evidence_level": manifest_summary.get("unrealSocketImportCheckerEvidenceLevel"),
                "unreal_socket_import_checker_l3_status": manifest_summary.get("unrealSocketImportCheckerL3Status"),
                "unreal_socket_import_checker_engine_version": manifest_summary.get("unrealSocketImportCheckerEngineVersion"),
                "unreal_socket_import_checker_spatial_rows": manifest_summary.get("unrealSocketImportCheckerSpatialRows"),
                "unreal_socket_import_checker_ready": manifest_summary.get("unrealSocketImportCheckerReady"),
                "unreal_socket_import_checker_review": manifest_summary.get("unrealSocketImportCheckerReview"),
                "unreal_socket_import_checker_blocked": manifest_summary.get("unrealSocketImportCheckerBlocked"),
                "unreal_socket_import_checker_pass_checks": manifest_summary.get("unrealSocketImportCheckerPassChecks"),
                "unreal_socket_import_checker_warning_checks": manifest_summary.get("unrealSocketImportCheckerWarningChecks"),
                "unreal_socket_import_checker_error_checks": manifest_summary.get("unrealSocketImportCheckerErrorChecks"),
                "unreal_socket_import_checker_socket_api_ready": manifest_summary.get("unrealSocketImportCheckerSocketApiReady"),
                "unreal_socket_import_checker_expected_sockets": manifest_summary.get("unrealSocketImportCheckerExpectedSockets"),
                "unreal_socket_import_checker_runtime_sockets": manifest_summary.get("unrealSocketImportCheckerRuntimeSockets"),
                "unreal_socket_import_checker_asset_writes": manifest_summary.get("unrealSocketImportCheckerAssetWrites"),
                "unreal_socket_authoring_executor_gate": manifest_summary.get("unrealSocketAuthoringExecutorGate"),
                "unreal_socket_authoring_executor_evidence_level": manifest_summary.get("unrealSocketAuthoringExecutorEvidenceLevel"),
                "unreal_socket_authoring_executor_l3_status": manifest_summary.get("unrealSocketAuthoringExecutorL3Status"),
                "unreal_socket_authoring_executor_engine_version": manifest_summary.get("unrealSocketAuthoringExecutorEngineVersion"),
                "unreal_socket_authoring_executor_selected_operations": manifest_summary.get("unrealSocketAuthoringExecutorSelectedOperations"),
                "unreal_socket_authoring_executor_held_rows": manifest_summary.get("unrealSocketAuthoringExecutorHeldRows"),
                "unreal_socket_authoring_executor_expected_sockets": manifest_summary.get("unrealSocketAuthoringExecutorExpectedSockets"),
                "unreal_socket_authoring_executor_created_sockets": manifest_summary.get("unrealSocketAuthoringExecutorCreatedSockets"),
                "unreal_socket_authoring_executor_post_check": manifest_summary.get("unrealSocketAuthoringExecutorPostCheckPassed"),
                "unreal_socket_authoring_executor_rollback": manifest_summary.get("unrealSocketAuthoringExecutorRollbackPassed"),
                "unreal_socket_authoring_executor_pass_checks": manifest_summary.get("unrealSocketAuthoringExecutorPassChecks"),
                "unreal_socket_authoring_executor_warning_checks": manifest_summary.get("unrealSocketAuthoringExecutorWarningChecks"),
                "unreal_socket_authoring_executor_error_checks": manifest_summary.get("unrealSocketAuthoringExecutorErrorChecks"),
                "unreal_socket_authoring_executor_asset_writes": manifest_summary.get("unrealSocketAuthoringExecutorAssetWrites"),
                "unreal_socket_authoring_executor_production_writes": manifest_summary.get("unrealSocketAuthoringExecutorProductionWrites"),
                "unreal_socket_authoring_executor_api_docs": manifest_summary.get("unrealSocketApiDocsArtifact"),
                "unreal_gameplay_attach_fixture_gate": manifest_summary.get("unrealGameplayAttachFixtureGate"),
                "unreal_gameplay_attach_fixture_evidence_level": manifest_summary.get("unrealGameplayAttachFixtureEvidenceLevel"),
                "unreal_gameplay_attach_fixture_l3_status": manifest_summary.get("unrealGameplayAttachFixtureL3Status"),
                "unreal_gameplay_attach_fixture_engine_version": manifest_summary.get("unrealGameplayAttachFixtureEngineVersion"),
                "unreal_gameplay_attach_fixture_intents": manifest_summary.get("unrealGameplayAttachFixtureIntentCount"),
                "unreal_gameplay_attach_fixture_ready": manifest_summary.get("unrealGameplayAttachFixtureReady"),
                "unreal_gameplay_attach_fixture_review": manifest_summary.get("unrealGameplayAttachFixtureReview"),
                "unreal_gameplay_attach_fixture_blocked": manifest_summary.get("unrealGameplayAttachFixtureBlocked"),
                "unreal_gameplay_attach_fixture_required_sockets": manifest_summary.get("unrealGameplayAttachFixtureRequiredSockets"),
                "unreal_gameplay_attach_fixture_missing_runtime_sockets": manifest_summary.get("unrealGameplayAttachFixtureMissingRuntimeSockets"),
                "unreal_gameplay_attach_fixture_required_hotspots": manifest_summary.get("unrealGameplayAttachFixtureRequiredHotspots"),
                "unreal_gameplay_attach_fixture_missing_hotspot_semantics": manifest_summary.get("unrealGameplayAttachFixtureMissingHotspotSemantics"),
                "unreal_gameplay_attach_fixture_attachable_assets_present": manifest_summary.get("unrealGameplayAttachFixtureAttachableAssetsPresent"),
                "unreal_gameplay_attach_fixture_animation_assets_present": manifest_summary.get("unrealGameplayAttachFixtureAnimationAssetsPresent"),
                "unreal_gameplay_attach_fixture_pass_checks": manifest_summary.get("unrealGameplayAttachFixturePassChecks"),
                "unreal_gameplay_attach_fixture_warning_checks": manifest_summary.get("unrealGameplayAttachFixtureWarningChecks"),
                "unreal_gameplay_attach_fixture_error_checks": manifest_summary.get("unrealGameplayAttachFixtureErrorChecks"),
                "unreal_gameplay_attach_fixture_asset_writes": manifest_summary.get("unrealGameplayAttachFixtureAssetWrites"),
                "unreal_gameplay_attach_fixture_production_writes": manifest_summary.get("unrealGameplayAttachFixtureProductionWrites"),
                "platform_variant_forge_gate": manifest_summary.get("platformVariantForgeGate"),
                "platform_variant_forge_evidence_level": manifest_summary.get("platformVariantForgeEvidenceLevel"),
                "platform_variant_forge_l3_status": manifest_summary.get("platformVariantForgeL3Status"),
                "platform_variant_forge_assets": manifest_summary.get("platformVariantForgeAssets"),
                "platform_variant_forge_variants": manifest_summary.get("platformVariantForgeVariants"),
                "platform_variant_forge_ready": manifest_summary.get("platformVariantForgeReady"),
                "platform_variant_forge_review": manifest_summary.get("platformVariantForgeReview"),
                "platform_variant_forge_blocked": manifest_summary.get("platformVariantForgeBlocked"),
                "platform_variant_forge_pass_checks": manifest_summary.get("platformVariantForgePassChecks"),
                "platform_variant_forge_warning_checks": manifest_summary.get("platformVariantForgeWarningChecks"),
                "platform_variant_forge_error_checks": manifest_summary.get("platformVariantForgeErrorChecks"),
                "platform_variant_unreal_runtime_gate": manifest_summary.get("platformVariantUnrealRuntimeGate"),
                "platform_variant_unreal_runtime_evidence_level": manifest_summary.get("platformVariantUnrealRuntimeEvidenceLevel"),
                "platform_variant_unreal_runtime_l3_status": manifest_summary.get("platformVariantUnrealRuntimeL3Status"),
                "platform_variant_unreal_runtime_engine_version": manifest_summary.get("platformVariantUnrealRuntimeEngineVersion"),
                "platform_variant_unreal_runtime_asset_writes": manifest_summary.get("platformVariantUnrealRuntimeAssetWrites"),
                "platform_variant_unreal_runtime_variants": manifest_summary.get("platformVariantUnrealRuntimeVariants"),
                "platform_variant_unreal_runtime_ready": manifest_summary.get("platformVariantUnrealRuntimeReady"),
                "platform_variant_unreal_runtime_review": manifest_summary.get("platformVariantUnrealRuntimeReview"),
                "platform_variant_unreal_runtime_blocked": manifest_summary.get("platformVariantUnrealRuntimeBlocked"),
                "platform_variant_unreal_runtime_pass_checks": manifest_summary.get("platformVariantUnrealRuntimePassChecks"),
                "platform_variant_unreal_runtime_warning_checks": manifest_summary.get("platformVariantUnrealRuntimeWarningChecks"),
                "platform_variant_unreal_runtime_error_checks": manifest_summary.get("platformVariantUnrealRuntimeErrorChecks"),
                "platform_variant_generation_plan_gate": manifest_summary.get("platformVariantGenerationPlanGate"),
                "platform_variant_generation_plan_evidence_level": manifest_summary.get("platformVariantGenerationPlanEvidenceLevel"),
                "platform_variant_generation_plan_l3_status": manifest_summary.get("platformVariantGenerationPlanL3Status"),
                "platform_variant_generation_plan_operations": manifest_summary.get("platformVariantGenerationPlanOperations"),
                "platform_variant_generation_plan_ready": manifest_summary.get("platformVariantGenerationPlanReady"),
                "platform_variant_generation_plan_review": manifest_summary.get("platformVariantGenerationPlanReview"),
                "platform_variant_generation_plan_blocked": manifest_summary.get("platformVariantGenerationPlanBlocked"),
                "platform_variant_generation_plan_satisfied": manifest_summary.get("platformVariantGenerationPlanSatisfied"),
                "platform_variant_generation_plan_owner_required": manifest_summary.get("platformVariantGenerationPlanOwnerRequired"),
                "platform_variant_texture_runtime_gate": manifest_summary.get("platformVariantTextureRuntimeGate"),
                "platform_variant_texture_runtime_evidence_level": manifest_summary.get("platformVariantTextureRuntimeEvidenceLevel"),
                "platform_variant_texture_runtime_l3_status": manifest_summary.get("platformVariantTextureRuntimeL3Status"),
                "platform_variant_texture_runtime_engine_version": manifest_summary.get("platformVariantTextureRuntimeEngineVersion"),
                "platform_variant_texture_runtime_asset_writes": manifest_summary.get("platformVariantTextureRuntimeAssetWrites"),
                "platform_variant_texture_runtime_variants": manifest_summary.get("platformVariantTextureRuntimeVariants"),
                "platform_variant_texture_runtime_ready": manifest_summary.get("platformVariantTextureRuntimeReady"),
                "platform_variant_texture_runtime_review": manifest_summary.get("platformVariantTextureRuntimeReview"),
                "platform_variant_texture_runtime_blocked": manifest_summary.get("platformVariantTextureRuntimeBlocked"),
                "platform_variant_texture_runtime_pass_checks": manifest_summary.get("platformVariantTextureRuntimePassChecks"),
                "platform_variant_texture_runtime_warning_checks": manifest_summary.get("platformVariantTextureRuntimeWarningChecks"),
                "platform_variant_texture_runtime_error_checks": manifest_summary.get("platformVariantTextureRuntimeErrorChecks"),
                "platform_variant_texture_runtime_texture_dependencies": manifest_summary.get("platformVariantTextureRuntimeTextureDependencies"),
                "platform_variant_texture_payload_gate": manifest_summary.get("platformVariantTexturePayloadGate"),
                "platform_variant_texture_payload_evidence_level": manifest_summary.get("platformVariantTexturePayloadEvidenceLevel"),
                "platform_variant_texture_payload_l3_status": manifest_summary.get("platformVariantTexturePayloadL3Status"),
                "platform_variant_texture_payload_engine_version": manifest_summary.get("platformVariantTexturePayloadEngineVersion"),
                "platform_variant_texture_payload_asset_writes": manifest_summary.get("platformVariantTexturePayloadAssetWrites"),
                "platform_variant_texture_payload_variants": manifest_summary.get("platformVariantTexturePayloadVariants"),
                "platform_variant_texture_payload_ready": manifest_summary.get("platformVariantTexturePayloadReady"),
                "platform_variant_texture_payload_review": manifest_summary.get("platformVariantTexturePayloadReview"),
                "platform_variant_texture_payload_blocked": manifest_summary.get("platformVariantTexturePayloadBlocked"),
                "platform_variant_texture_payload_pass_checks": manifest_summary.get("platformVariantTexturePayloadPassChecks"),
                "platform_variant_texture_payload_warning_checks": manifest_summary.get("platformVariantTexturePayloadWarningChecks"),
                "platform_variant_texture_payload_error_checks": manifest_summary.get("platformVariantTexturePayloadErrorChecks"),
                "platform_variant_texture_payload_texture_dependencies": manifest_summary.get("platformVariantTexturePayloadTextureDependencies"),
                "platform_variant_controlled_executor_gate": manifest_summary.get("platformVariantControlledExecutorGate"),
                "platform_variant_controlled_executor_evidence_level": manifest_summary.get("platformVariantControlledExecutorEvidenceLevel"),
                "platform_variant_controlled_executor_l3_status": manifest_summary.get("platformVariantControlledExecutorL3Status"),
                "platform_variant_controlled_executor_engine_version": manifest_summary.get("platformVariantControlledExecutorEngineVersion"),
                "platform_variant_controlled_executor_executed": manifest_summary.get("platformVariantControlledExecutorExecuted"),
                "platform_variant_controlled_executor_post_check": manifest_summary.get("platformVariantControlledExecutorPostCheck"),
                "platform_variant_controlled_executor_rollback": manifest_summary.get("platformVariantControlledExecutorRollback"),
                "platform_variant_controlled_executor_asset_writes": manifest_summary.get("platformVariantControlledExecutorAssetWrites"),
                "platform_variant_controlled_executor_persistent_mutation": manifest_summary.get("platformVariantControlledExecutorPersistentMutation"),
                "platform_variant_controlled_executor_pass_checks": manifest_summary.get("platformVariantControlledExecutorPassChecks"),
                "platform_variant_controlled_executor_warning_checks": manifest_summary.get("platformVariantControlledExecutorWarningChecks"),
                "platform_variant_controlled_executor_error_checks": manifest_summary.get("platformVariantControlledExecutorErrorChecks"),
                "platform_variant_executor_expansion_gate": manifest_summary.get("platformVariantExecutorExpansionGate"),
                "platform_variant_executor_expansion_evidence_level": manifest_summary.get("platformVariantExecutorExpansionEvidenceLevel"),
                "platform_variant_executor_expansion_l3_status": manifest_summary.get("platformVariantExecutorExpansionL3Status"),
                "platform_variant_executor_expansion_receipts": manifest_summary.get("platformVariantExecutorExpansionReceipts"),
                "platform_variant_executor_expansion_no_op": manifest_summary.get("platformVariantExecutorExpansionNoOpVerified"),
                "platform_variant_executor_expansion_approval_ready": manifest_summary.get("platformVariantExecutorExpansionApprovalReady"),
                "platform_variant_executor_expansion_readiness_only": manifest_summary.get("platformVariantExecutorExpansionReadinessOnly"),
                "platform_variant_executor_expansion_blocked": manifest_summary.get("platformVariantExecutorExpansionBlocked"),
                "platform_variant_executor_expansion_owner_approvals": manifest_summary.get("platformVariantExecutorExpansionOwnerApprovalsRequired"),
                "platform_variant_executor_expansion_rollback_receipts": manifest_summary.get("platformVariantExecutorExpansionRollbackReceiptsRequired"),
                "platform_variant_executor_expansion_production_writes": manifest_summary.get("platformVariantExecutorExpansionProductionWrites"),
                "platform_variant_staticmesh_postcheck_gate": manifest_summary.get("platformVariantStaticMeshPostcheckGate"),
                "platform_variant_staticmesh_postcheck_evidence_level": manifest_summary.get("platformVariantStaticMeshPostcheckEvidenceLevel"),
                "platform_variant_staticmesh_postcheck_l3_status": manifest_summary.get("platformVariantStaticMeshPostcheckL3Status"),
                "platform_variant_staticmesh_postcheck_engine_version": manifest_summary.get("platformVariantStaticMeshPostcheckEngineVersion"),
                "platform_variant_staticmesh_postcheck_receipts": manifest_summary.get("platformVariantStaticMeshPostcheckReceipts"),
                "platform_variant_staticmesh_postcheck_targets": manifest_summary.get("platformVariantStaticMeshPostcheckTargets"),
                "platform_variant_staticmesh_postcheck_target_assets_present": manifest_summary.get("platformVariantStaticMeshPostcheckTargetAssetsPresent"),
                "platform_variant_staticmesh_postcheck_no_op": manifest_summary.get("platformVariantStaticMeshPostcheckNoOpVerified"),
                "platform_variant_staticmesh_postcheck_runtime_no_op_matched": manifest_summary.get("platformVariantStaticMeshPostcheckRuntimeNoOpMatched"),
                "platform_variant_staticmesh_postcheck_approval_ready": manifest_summary.get("platformVariantStaticMeshPostcheckApprovalReady"),
                "platform_variant_staticmesh_postcheck_readiness_only": manifest_summary.get("platformVariantStaticMeshPostcheckReadinessOnly"),
                "platform_variant_staticmesh_postcheck_runtime_held": manifest_summary.get("platformVariantStaticMeshPostcheckRuntimeHeld"),
                "platform_variant_staticmesh_postcheck_owner_actions": manifest_summary.get("platformVariantStaticMeshPostcheckOwnerActions"),
                "platform_variant_staticmesh_postcheck_pass_checks": manifest_summary.get("platformVariantStaticMeshPostcheckPassChecks"),
                "platform_variant_staticmesh_postcheck_warning_checks": manifest_summary.get("platformVariantStaticMeshPostcheckWarningChecks"),
                "platform_variant_staticmesh_postcheck_error_checks": manifest_summary.get("platformVariantStaticMeshPostcheckErrorChecks"),
                "platform_variant_staticmesh_postcheck_asset_writes": manifest_summary.get("platformVariantStaticMeshPostcheckAssetWrites"),
                "platform_variant_staticmesh_postcheck_production_writes": manifest_summary.get("platformVariantStaticMeshPostcheckProductionWrites"),
                "blender_rule_adapter_gate": manifest_summary.get("blenderRuleAdapterGate"),
                "blender_rule_adapter_evidence_level": manifest_summary.get("blenderRuleAdapterEvidenceLevel"),
                "blender_rule_adapter_assets": manifest_summary.get("blenderRuleAdapterAssets"),
                "blender_rule_adapter_l3_harness_gate": manifest_summary.get("blenderRuleAdapterL3HarnessGate"),
                "blender_rule_adapter_l3_harness_blender_found": manifest_summary.get("blenderRuleAdapterL3HarnessBlenderFound"),
                "blender_rule_adapter_l3_harness_collector_ready": manifest_summary.get("blenderRuleAdapterL3HarnessCollectorReady"),
                "max_rule_adapter_gate": manifest_summary.get("maxRuleAdapterGate"),
                "max_rule_adapter_evidence_level": manifest_summary.get("maxRuleAdapterEvidenceLevel"),
                "max_rule_adapter_assets": manifest_summary.get("maxRuleAdapterAssets"),
                "max_rule_adapter_max_batch_available": manifest_summary.get("maxRuleAdapterMaxBatchAvailable"),
                "max_rule_adapter_l3_harness_gate": manifest_summary.get("maxRuleAdapterL3HarnessGate"),
                "max_rule_adapter_l3_harness_runtime_found": manifest_summary.get("maxRuleAdapterL3HarnessRuntimeFound"),
                "max_rule_adapter_l3_harness_collector_ready": manifest_summary.get("maxRuleAdapterL3HarnessCollectorReady"),
                "max_texture_manifest_link_gate": manifest_summary.get("maxTextureManifestLinkGate"),
                "max_texture_manifest_link_evidence_level": manifest_summary.get("maxTextureManifestLinkEvidenceLevel"),
                "max_texture_manifest_link_l3_status": manifest_summary.get("maxTextureManifestLinkL3Status"),
                "max_texture_manifest_link_assets": manifest_summary.get("maxTextureManifestLinkAssets"),
                "max_texture_manifest_link_material_rows": manifest_summary.get("maxTextureManifestLinkMaterialRows"),
                "max_texture_manifest_link_slot_textures": manifest_summary.get("maxTextureManifestLinkSlotTextures"),
                "max_texture_manifest_link_manifest_textures": manifest_summary.get("maxTextureManifestLinkManifestTextures"),
                "max_texture_manifest_link_missing_required_semantics": manifest_summary.get("maxTextureManifestLinkMissingRequiredSemantics"),
                "max_texture_manifest_link_pass_checks": manifest_summary.get("maxTextureManifestLinkPassChecks"),
                "max_texture_manifest_link_warning_checks": manifest_summary.get("maxTextureManifestLinkWarningChecks"),
                "max_texture_manifest_link_error_checks": manifest_summary.get("maxTextureManifestLinkErrorChecks"),
                "houdini_rule_adapter_gate": manifest_summary.get("houdiniRuleAdapterGate"),
                "houdini_rule_adapter_evidence_level": manifest_summary.get("houdiniRuleAdapterEvidenceLevel"),
                "houdini_rule_adapter_l3_status": manifest_summary.get("houdiniRuleAdapterL3Status"),
                "houdini_rule_adapter_assets": manifest_summary.get("houdiniRuleAdapterAssets"),
                "houdini_rule_adapter_ready": manifest_summary.get("houdiniRuleAdapterReady"),
                "houdini_rule_adapter_review": manifest_summary.get("houdiniRuleAdapterReview"),
                "houdini_rule_adapter_blocked": manifest_summary.get("houdiniRuleAdapterBlocked"),
                "houdini_rule_adapter_pass_checks": manifest_summary.get("houdiniRuleAdapterPassChecks"),
                "houdini_rule_adapter_warning_checks": manifest_summary.get("houdiniRuleAdapterWarningChecks"),
                "houdini_rule_adapter_error_checks": manifest_summary.get("houdiniRuleAdapterErrorChecks"),
                "houdini_rule_adapter_hython_available": manifest_summary.get("houdiniRuleAdapterHythonAvailable"),
                "houdini_rule_adapter_l3_harness_gate": manifest_summary.get("houdiniRuleAdapterL3HarnessGate"),
                "houdini_rule_adapter_l3_harness_hython_found": manifest_summary.get("houdiniRuleAdapterL3HarnessHythonFound"),
                "houdini_rule_adapter_l3_harness_collector_ready": manifest_summary.get("houdiniRuleAdapterL3HarnessCollectorReady"),
                "unreal_handoff_inspector_gate": manifest_summary.get("unrealHandoffInspectorGate"),
                "unreal_handoff_inspector_evidence_level": manifest_summary.get("unrealHandoffInspectorEvidenceLevel"),
                "unreal_handoff_inspector_l3_status": manifest_summary.get("unrealHandoffInspectorL3Status"),
                "unreal_handoff_inspector_engine_version": manifest_summary.get("unrealHandoffInspectorEngineVersion"),
                "unreal_handoff_inspector_asset_registry_queried": manifest_summary.get("unrealHandoffInspectorAssetRegistryQueried"),
                "unreal_handoff_inspector_registry_matched": manifest_summary.get("unrealHandoffInspectorRegistryMatched"),
                "unreal_handoff_inspector_registry_expected_assets": manifest_summary.get("unrealHandoffInspectorRegistryExpectedAssets"),
                "unreal_handoff_inspector_registry_matched_assets": manifest_summary.get("unrealHandoffInspectorRegistryMatchedAssets"),
                "unreal_handoff_inspector_registry_missing_assets": manifest_summary.get("unrealHandoffInspectorRegistryMissingAssets"),
                "unreal_handoff_inspector_registry_class_mismatches": manifest_summary.get("unrealHandoffInspectorRegistryClassMismatches"),
                "unreal_handoff_inspector_engine_facts_matched": manifest_summary.get("unrealHandoffInspectorEngineFactsMatched"),
                "unreal_handoff_inspector_engine_fact_expected": manifest_summary.get("unrealHandoffInspectorEngineFactExpected"),
                "unreal_handoff_inspector_engine_fact_matched": manifest_summary.get("unrealHandoffInspectorEngineFactMatched"),
                "unreal_handoff_inspector_engine_fact_missing": manifest_summary.get("unrealHandoffInspectorEngineFactMissing"),
                "unreal_handoff_inspector_source_import_matched": manifest_summary.get("unrealHandoffInspectorSourceImportMatched"),
                "unreal_handoff_inspector_material_slot_matched": manifest_summary.get("unrealHandoffInspectorMaterialSlotMatched"),
                "unreal_handoff_inspector_lod_count": manifest_summary.get("unrealHandoffInspectorLodCount"),
                "unreal_handoff_inspector_collision_simple_shapes": manifest_summary.get("unrealHandoffInspectorCollisionSimpleShapes"),
                "unreal_handoff_inspector_intents": manifest_summary.get("unrealHandoffInspectorIntents"),
            },
            "demo_route": demo_route,
            "business_route": runbook_plan["presentation_route"],
            "key_evidence_files": evidence_files,
            "media_audit": {
                "gate": media_summary["gate"],
                "media_root": media_audit["media_root"],
                "required_files": media_summary["required_files"],
                "present": media_summary["present"],
                "review": media_summary["review"],
                "missing": media_summary["missing"],
                "rows": media_audit["rows"],
            },
            "reviewer_claims": [
                "The portfolio opens from Maya through AuroraView.",
                "The browser UI is the embedded panel surface, not the primary presentation target.",
                "Five DCC modules are organized into one asset handoff business route.",
                "Composite gate, owner disposition, engine preflight, and preset comparison are machine-checkable JSON evidence.",
                "Engine-facing rows are dry-run sidecars and intents only; no engine write is executed.",
                "Unreal Handoff Inspector checks DCC import intents against real public Unreal fixture assets and import-task constraints.",
                "Unreal Preset Fact Comparison joins runtime engine facts with PC/Mobile preset policy and exception waiver rows.",
                "Unreal Preset Fact Review projects the comparison rows into a Maya-hosted reviewer queue with owner actions.",
                "Scene Transaction Guard captures DCC before/after scene mutation, risk rows and rollback preview from Maya.",
                "Animation Continuity Lab is now backed by Maya mayapy L3 animCurve evidence for rig identity, take range, sample rate, channels, sub-frame keys and root motion.",
                "Unreal Animation Bridge generates public Maya FBX clips, imports them into Unreal, and records real AnimSequence/Skeleton/SkeletalMesh facts.",
                "Unreal AnimSequence Deep Facts reads existing public AnimSequence assets and separates duration/frame-span facts from curve/root/compression API visibility without saving assets.",
                "Character Calibration Studio is now backed by Maya mayapy L3 topology, joint coverage, calibration delta, face parameter and Control Rig mapping evidence.",
                "Character Calibration Drilldown projects Maya L3 character facts into UI-ready panels, owner actions and fix previews.",
                "Unreal Control Rig Bridge joins Maya character mapping facts to Unreal Control Rig API readiness, SkeletalMesh/Skeleton binding and expected CR asset coverage.",
                "Unreal Control Rig Fixture Authoring creates the public CR_HeroFace fixture and proves required runtime control coverage under a public write boundary.",
                "Unreal Control Rig Face Skeleton Fixture generates a public SK_HeroFace Skeleton from Maya FBX, imports it into Unreal, and resolves R43's missing Eye/Jaw deformation targets.",
                "Unreal Control Rig Deformation Link audits CR_HeroFace against Maya deformation targets, Skeleton bone coverage, hierarchy shape/offset readability and compile-status API visibility.",
                "Unreal Control Rig Compile Status Bridge invokes public CR_HeroFace compile methods and records direct diagnostic readability, dirty-state boundary and zero-save evidence.",
                "Groom Export Inspector reads public Maya curve strands and validates root UV, strand ID, guide curve, Alembic payload and Unreal binding readiness.",
                "Groom Unreal Import Readiness joins R46 Maya groom facts to Unreal Groom/Alembic API visibility, target SkeletalMesh presence and zero-write import boundary.",
                "Groom Alembic Payload Receipt turns the approved R46 groom row into a real public Maya AbcExport cache receipt while holding blocked TMP groom rows.",
                "Groom Alembic Import/Post-check Readiness joins that .abc receipt to Unreal runtime import-task dry-run, cache sha256 continuity, target asset post-check gaps and no-write boundary.",
                "Groom Plugin/API Public Fixture Readiness proves the public Unreal project requests HairStrands and Alembic hair plugins, exposes Groom import API classes and keeps the probe read-only.",
                "Groom Controlled Executor imports the curve-only public .abc through Unreal HairStrandsFactory, creates the expected GroomAsset and BindingAsset, then rolls back public fixture writes without residue.",
                "Groom Runtime Fact Collector reads GroomAsset, GroomBindingAsset and target SkeletalMesh runtime facts while the public fixture assets exist, then rolls back without residue.",
                "Spatial Authoring Workbench is now backed by Maya mayapy L3 socket, hotspot, pose frame, mirror pair and pose transfer evidence.",
                "Spatial Authoring Drilldown projects Maya L3 spatial facts into UI-ready socket, hotspot, pose frame, transform and pose transfer panels.",
                "Unreal Socket Import Checker joins Maya spatial authoring facts to Unreal SkeletalMesh/Skeleton socket API readiness and expected socket coverage.",
                "Unreal Socket Authoring Executor proves the approved public socket row can enter an engine-side execution gate, and records the UE 5.3 Python read-only socket-name limitation as a blocked readiness artifact.",
                "Unreal Gameplay Attach Fixture joins Maya socket/hotspot intents to Unreal runtime asset and animation facts, blocking equip readiness when character socket contracts are absent.",
                "Platform Variant Forge joins PC/Mobile variant plans to Unreal preset fact evidence and exposes budget, owner and mutation boundaries.",
                "Platform Variant Unreal Runtime Probe compares planned variants against real Unreal StaticMesh path, LOD, material, collision and Nanite facts.",
                "Platform Variant Generation Planner turns runtime drift into dry-run Unreal operation contracts with rollback and approval boundaries.",
                "Platform Variant Texture Runtime Collector collects Unreal material slots, material dependency queries and Texture2D budget facts for planned variants.",
                "Platform Variant Public Texture2D Payload Fixture imports a generated public texture, wires it to Unreal material, and proves PC/Mobile texture budgets against real Texture2D facts.",
                "Platform Variant Controlled Executor performs an Unreal public-fixture write, verifies post-state, and rolls back to the preflight fingerprint.",
                "Platform Variant Executor Expansion turns LOD, Nanite and collision operations into approval and rollback receipts linked to the controlled executor proof.",
                "Platform Variant StaticMesh Post-check validates those receipts against read-only Unreal StaticMesh LOD, collision and Nanite facts.",
                "Blender Rule Adapter is now backed by real bpy L3 evidence on a public synthetic scene.",
                "3ds Max Rule Adapter is now backed by real pymxs L3 evidence on a public synthetic scene.",
                "3ds Max Material Texture Manifest Link joins pymxs material bitmap slots to package texture entries, channel semantics, color-space policy and platform budgets.",
                "Houdini Rule Adapter normalizes HDA state, detail attributes, OUT_* role nodes, packed instance prototypes, PDG wedge summaries and frozen bake receipts into the shared Cross-DCC rule matrix.",
                "Blender, 3ds Max and Houdini adapters expose pass, warning, and blocked rows through the same Cross-DCC Rule Matrix shape.",
                "GUI screenshots and recording are tracked by audit gate instead of being implied complete.",
            ],
            "next_actions": capture_next_actions,
            "boundary": {
                "mutation": "presenter_pack_export_only",
                "sceneWrites": "none",
                "engineWrites": 0,
                "assets": "public synthetic fixtures only",
                "proprietaryData": "not included",
            },
            "public_case_package": {
                "manifest": display_path(manifest_path),
                "readme": display_path(public_package_dir / "DCC_FIRST_PACKAGE.md"),
                "package_id": manifest.get("packageId"),
                "package_version": manifest.get("packageVersion"),
            },
        }

    def dcc_presentation_export_pack(
        self,
        label: str = "r56-houdini-rule-adapter-presentation-pack",
    ) -> Dict[str, Any]:
        pack = self.dcc_presentation_build_pack(label=label)
        report = {
            "reportVersion": "maya-dcc-presentation-pack@0.1.0",
            "generatedBy": "AI Tool TA Portfolio / Maya AuroraView Host",
            "environment": self.environment_status(),
            "presentationPack": pack,
        }
        exported = self.report_export_json(label=label, report=report)
        return {"ok": True, "path": exported["path"], "bytes": exported["bytes"], "report": report}
