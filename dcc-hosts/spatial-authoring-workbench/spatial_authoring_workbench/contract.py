"""Spatial authoring contract.

This models a Lightbox-style authoring pass for game sockets, VFX hotspots,
pose frames and mirror transfer before those facts move into engine runtime.
"""

from __future__ import annotations

import json
import math
import time
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "spatial-authoring-contract@0.1.0"
NORMALIZED_SCHEMA = "spatial-authoring-input@0.1.0"
FIXTURE_SCHEMA = "synthetic-spatial-authoring-scene@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != FIXTURE_SCHEMA:
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def collect_scene_facts(fixture: Dict[str, Any]) -> Dict[str, Any]:
    return build_facts_from_assets(
        scene=fixture.get("scene", {}),
        assets=fixture.get("assets", []),
        source_dcc="Fixture",
        runtime_collected=False,
    )


def build_facts_from_assets(
    scene: Dict[str, Any],
    assets: List[Dict[str, Any]],
    source_dcc: str,
    runtime_collected: bool,
) -> Dict[str, Any]:
    rows = [_build_asset_facts(asset, scene, source_dcc) for asset in assets]
    return {
        "schema": NORMALIZED_SCHEMA,
        "scene": {
            "sourceDcc": source_dcc,
            "unit": scene.get("unit"),
            "upAxis": scene.get("upAxis"),
            "fps": scene.get("fps"),
            "playbackStart": scene.get("playbackStart"),
            "playbackEnd": scene.get("playbackEnd"),
            "assetCount": len(rows),
            "runtimeCollected": runtime_collected,
        },
        "assets": rows,
    }


def evaluate_scene(facts: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("assets", []):
        evaluations.extend(_evaluate_asset(row))
    return {
        "schema": "spatial-authoring-evaluation@0.1.0",
        "summary": _summarize(evaluations),
        "evaluations": evaluations,
        "fixPreview": _build_fix_preview(evaluations),
    }


def build_report(fixture_path: str | Path) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    facts = collect_scene_facts(fixture)
    evaluation = evaluate_scene(facts)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Spatial Authoring Workbench",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2",
        "l3Status": "contract_fixture_collected",
        "fixture": {
            "path": public_path(fixture_path),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "spatial-authoring",
            "name": "Spatial Authoring & Pose Transfer Workbench",
            "methodSource": "Lightbox socket / hotspot / locator preview / pose transfer authoring",
            "protocolCarrier": "Maya locators + joint ownership + pose frame custom attrs",
            "boundary": {
                "mutation": "contract_validation_only",
                "sceneWrites": 0,
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": _reviewer_claims(),
    }


def _build_asset_facts(asset: Dict[str, Any], scene: Dict[str, Any], source_dcc: str) -> Dict[str, Any]:
    constraints = asset.get("constraints", {})
    skeleton = asset.get("skeleton", {})
    actual_joints = [str(name) for name in skeleton.get("actualJoints", [])]
    expected_joints = [str(name) for name in skeleton.get("expectedJoints", [])]
    sockets = [_spatial_item_fact(item, "socket") for item in asset.get("sockets", [])]
    hotspots = [_spatial_item_fact(item, "hotspot") for item in asset.get("hotspots", [])]
    pose_frames = [_spatial_item_fact(item, "poseFrame") for item in asset.get("poseFrames", [])]
    all_items = sockets + hotspots + pose_frames
    pose_transfer = asset.get("poseTransfer", {})

    socket_by_name = {row["name"]: row for row in sockets}
    socket_names = sorted(socket_by_name)
    mirror_pair_rows = _mirror_pair_rows(sockets, float(constraints.get("maxMirrorDeltaCm", 0.0) or 0.0))
    missing_transfer_pairs = [
        pair
        for pair in pose_transfer.get("requiredPairs", [])
        if len(pair) != 2 or pair[0] not in socket_by_name or pair[1] not in socket_by_name
    ]
    pose_names = [row["name"] for row in pose_frames]
    pose_counts = Counter(pose_names)
    range_min, range_max = _range_pair(constraints.get("poseFrameRange", scene.get("playbackStart", 1)))
    allowed_spaces = {str(space) for space in constraints.get("allowedSpaces", ["local"])}
    allowed_semantics = {str(value) for value in constraints.get("allowedHotspotSemantics", [])}
    required_hotspot_owners = {str(value) for value in constraints.get("requiredHotspotOwners", [])}
    max_socket_offset = float(constraints.get("maxSocketOffsetCm", 0.0) or 0.0)

    parent_joint_issues = [
        {
            "kind": row["kind"],
            "name": row["name"],
            "parentJoint": row.get("parentJoint"),
        }
        for row in sockets + hotspots
        if row.get("parentJoint") not in actual_joints
    ]
    socket_offset_issues = [
        {"name": row["name"], "offsetCm": row["offsetCm"], "limitCm": max_socket_offset}
        for row in sockets
        if row["offsetCm"] > max_socket_offset
    ]
    hotspot_semantic_issues = [
        {
            "name": row["name"],
            "semantic": row.get("semantic"),
            "owner": row.get("owner"),
        }
        for row in hotspots
        if row.get("semantic") not in allowed_semantics or row.get("owner") not in required_hotspot_owners
    ]
    pose_frame_issues = {
        "missing": sorted(set(str(name) for name in constraints.get("requiredPoseFrames", [])) - set(pose_names)),
        "duplicates": sorted(name for name, count in pose_counts.items() if count > 1),
        "outsideRange": [
            {"name": row["name"], "frame": row["frame"], "range": [range_min, range_max]}
            for row in pose_frames
            if row["frame"] < range_min or row["frame"] > range_max
        ],
        "missingOwner": sorted(row["name"] for row in pose_frames if not row.get("owner")),
    }
    scale_issues = [
        {
            "kind": row["kind"],
            "name": row["name"],
            "scale": row["scale"],
        }
        for row in all_items
        if bool(constraints.get("requireUniformScale", True)) and not _uniform_scale(row["scale"])
    ]
    space_issues = [
        {
            "kind": row["kind"],
            "name": row["name"],
            "space": row.get("space"),
        }
        for row in all_items
        if str(row.get("space")) not in allowed_spaces
    ]
    preview_issues = [
        {"kind": row["kind"], "name": row["name"]}
        for row in all_items
        if bool(constraints.get("requirePreviewLocator", True)) and not bool(row.get("previewLocator"))
    ]
    pose_transfer_issues = {
        "space": pose_transfer.get("space"),
        "missingPairs": missing_transfer_pairs,
        "missingTargetPose": pose_transfer.get("targetPose") not in set(pose_names),
        "missingApproval": not bool(pose_transfer.get("approvedBy")),
    }

    return {
        "assetId": asset.get("id"),
        "assetLabel": asset.get("label"),
        "sourceDcc": source_dcc,
        "normalizedSchema": NORMALIZED_SCHEMA,
        "protocolCarrier": "spatial authoring protocol + locators + pose frame attrs",
        "sourceFields": {
            "joints": "joint DAG names under asset root",
            "sockets": "locator transforms tagged as socket payloads",
            "hotspots": "locator transforms tagged with semantic and owner payloads",
            "poseFrames": "pose frame locator attrs and frame numbers",
            "poseTransfer": "mirror axis, source/target pose and required socket pairs",
        },
        "normalized": {
            "spatial.protocol.schema": asset.get("protocolSchema"),
            "asset.ownerState": asset.get("ownerState"),
            "joints.expectedCount": len(expected_joints),
            "joints.actualCount": len(actual_joints),
            "joints.missing": sorted(set(expected_joints) - set(actual_joints)),
            "joints.tmp": sorted(name for name in actual_joints if "TMP" in name.upper()),
            "parentJoint.missing": parent_joint_issues,
            "sockets.count": len(sockets),
            "sockets.names": socket_names,
            "sockets.offsetViolations": socket_offset_issues,
            "mirror.pairs": mirror_pair_rows,
            "mirror.missingPairs": [row for row in mirror_pair_rows if row["state"] == "missing"],
            "mirror.symmetryViolations": [row for row in mirror_pair_rows if row["state"] == "mismatch"],
            "hotspots.count": len(hotspots),
            "hotspots.semanticIssues": hotspot_semantic_issues,
            "poseFrames.count": len(pose_frames),
            "poseFrames.required": constraints.get("requiredPoseFrames", []),
            "poseFrames.issues": pose_frame_issues,
            "transforms.scaleIssues": scale_issues,
            "transforms.spaceIssues": space_issues,
            "previewLocator.missing": preview_issues,
            "poseTransfer.requiredPairs": pose_transfer.get("requiredPairs", []),
            "poseTransfer.issues": pose_transfer_issues,
        },
        "raw": {
            "namespace": asset.get("namespace"),
            "rootNode": asset.get("rootNode"),
            "constraints": constraints,
            "actualJoints": actual_joints,
            "sockets": sockets,
            "hotspots": hotspots,
            "poseFrames": pose_frames,
            "poseTransfer": pose_transfer,
        },
    }


def _spatial_item_fact(item: Dict[str, Any], kind: str) -> Dict[str, Any]:
    local = item.get("local", {})
    translate = _float_triplet(local.get("translate", [0.0, 0.0, 0.0]))
    rotate = _float_triplet(local.get("rotate", [0.0, 0.0, 0.0]))
    scale = _float_triplet(local.get("scale", [1.0, 1.0, 1.0]))
    return {
        "kind": kind,
        "name": str(item.get("name")),
        "exportName": item.get("exportName"),
        "parentJoint": item.get("parentJoint"),
        "mirrorOf": item.get("mirrorOf"),
        "side": item.get("side"),
        "semantic": item.get("semantic"),
        "owner": item.get("owner"),
        "role": item.get("role"),
        "frame": int(item.get("frame", 0) or 0),
        "space": item.get("space", "local"),
        "previewLocator": bool(item.get("previewLocator")),
        "translate": translate,
        "rotate": rotate,
        "scale": scale,
        "offsetCm": _length(translate),
    }


def _mirror_pair_rows(sockets: List[Dict[str, Any]], max_delta: float) -> List[Dict[str, Any]]:
    by_name = {row["name"]: row for row in sockets}
    seen = set()
    rows: List[Dict[str, Any]] = []
    for row in sockets:
        name = row["name"]
        mirror_name = row.get("mirrorOf")
        if not mirror_name:
            rows.append({"pair": [name, None], "state": "missing", "deltaCm": None})
            continue
        key = tuple(sorted([name, str(mirror_name)]))
        if key in seen:
            continue
        seen.add(key)
        other = by_name.get(str(mirror_name))
        if not other:
            rows.append({"pair": [name, mirror_name], "state": "missing", "deltaCm": None})
            continue
        delta = _mirror_delta(row["translate"], other["translate"])
        state = "matched" if delta <= max_delta and other.get("mirrorOf") == name else "mismatch"
        rows.append({"pair": [name, mirror_name], "state": state, "deltaCm": round(delta, 4), "limitCm": max_delta})
    return rows


def _evaluate_asset(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = row.get("assetId")
    n = row.get("normalized", {})
    pose_issues = n.get("poseFrames.issues", {})
    pose_transfer = n.get("poseTransfer.issues", {})
    return [
        _eval(
            asset_id,
            "protocol-carrier",
            n.get("spatial.protocol.schema") == "spatial-authoring@dcc-r27",
            "error",
            "Spatial protocol carrier",
            "Sockets, hotspots and pose frames must expose a typed authoring protocol before export.",
            str(n.get("spatial.protocol.schema")),
            "Write spatial-authoring@dcc-r27 on the asset root.",
        ),
        _eval(
            asset_id,
            "parent-joint-coverage",
            not n.get("joints.missing") and not n.get("parentJoint.missing"),
            "error",
            "Parent joint coverage",
            "Socket and hotspot locators must bind to real runtime joints before engine attach points are trusted.",
            "missingJoints=%s parentIssues=%s" % (n.get("joints.missing"), n.get("parentJoint.missing")),
            "Restore missing joints or remap the locator to an approved parent joint.",
        ),
        _eval(
            asset_id,
            "socket-offset-tolerance",
            not n.get("sockets.offsetViolations"),
            "error",
            "Socket offset tolerance",
            "Large local offsets usually mean the locator was authored in the wrong space or copied from a different rig.",
            str(n.get("sockets.offsetViolations")),
            "Rebuild the socket under the intended parent joint and re-freeze the local offset.",
        ),
        _eval(
            asset_id,
            "mirror-pair-symmetry",
            not n.get("mirror.missingPairs") and not n.get("mirror.symmetryViolations"),
            "error",
            "Mirror pair symmetry",
            "Left/right sockets must exist as explicit pairs before pose or attach rules are mirrored.",
            "missing=%s mismatch=%s" % (n.get("mirror.missingPairs"), n.get("mirror.symmetryViolations")),
            "Create the missing mirror locator or correct mirrored local transform values.",
        ),
        _eval(
            asset_id,
            "hotspot-semantic-owner",
            not n.get("hotspots.semanticIssues"),
            "error",
            "Hotspot semantic and owner",
            "Gameplay and VFX hookups need stable semantic names plus an accountable owner.",
            str(n.get("hotspots.semanticIssues")),
            "Assign an approved hotspot semantic and owner before export.",
        ),
        _eval(
            asset_id,
            "pose-frame-coverage-range",
            not pose_issues.get("missing")
            and not pose_issues.get("duplicates")
            and not pose_issues.get("outsideRange")
            and not pose_issues.get("missingOwner"),
            "error",
            "Pose frame coverage and range",
            "Pose transfer depends on unique, owned frame markers inside the exported take range.",
            str(pose_issues),
            "Restore missing pose frames, remove duplicates and keep frame markers inside range.",
        ),
        _eval(
            asset_id,
            "transform-scale-lock",
            not n.get("transforms.scaleIssues"),
            "warning",
            "Transform scale lock",
            "Non-uniform locator scale can create misleading preview handles and bad engine offsets.",
            str(n.get("transforms.scaleIssues")),
            "Reset locator scale to 1,1,1 or mark the locator as visual-only.",
        ),
        _eval(
            asset_id,
            "local-space-consistency",
            not n.get("transforms.spaceIssues"),
            "error",
            "Local space consistency",
            "Authoring facts must stay in parent-local space before they are converted to engine attach transforms.",
            str(n.get("transforms.spaceIssues")),
            "Convert world-space locators back to parent-local transforms.",
        ),
        _eval(
            asset_id,
            "preview-locator-presence",
            not n.get("previewLocator.missing"),
            "warning",
            "Preview locator presence",
            "Reviewers need visible locator handles for socket, hotspot and pose frame authoring.",
            str(n.get("previewLocator.missing")),
            "Create preview locators or attach an explicit no-preview waiver.",
        ),
        _eval(
            asset_id,
            "pose-transfer-boundary",
            not pose_transfer.get("missingPairs")
            and not pose_transfer.get("missingTargetPose")
            and not pose_transfer.get("missingApproval")
            and pose_transfer.get("space") == "local",
            "error",
            "Pose transfer boundary",
            "Pose copy and mirror transfer need approved pair coverage and local-space source/target poses.",
            str(pose_transfer),
            "Complete transfer pairs, add owner approval and keep transfer data in local space.",
        ),
    ]


def _eval(
    asset_id: str,
    rule_id: str,
    passed: bool,
    fail_status: str,
    label: str,
    reason: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (asset_id, rule_id),
        "assetId": asset_id,
        "ruleId": rule_id,
        "label": label,
        "status": "pass" if passed else fail_status,
        "reason": reason,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summarize(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(evaluations)
    asset_ids = sorted({row["assetId"] for row in rows})
    blocked = sorted({row["assetId"] for row in rows if row["status"] == "error"})
    review = sorted({row["assetId"] for row in rows if row["status"] == "warning"} - set(blocked))
    ready = sorted(set(asset_ids) - set(blocked) - set(review))
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "assetCount": len(asset_ids),
        "readyAssets": len(ready),
        "reviewAssets": len(review),
        "blockedAssets": len(blocked),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "readyAssetIds": ready,
        "reviewAssetIds": review,
        "blockedAssetIds": blocked,
    }


def _build_fix_preview(evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": "fix:%s" % row["id"],
            "assetId": row["assetId"],
            "ruleId": row["ruleId"],
            "status": row["status"],
            "mutationScope": "owner_required" if row["status"] == "error" else "manual_review",
            "preview": row["fixPreview"],
        }
        for row in evaluations
        if row["status"] != "pass"
    ]


def _float_triplet(value: Any) -> List[float]:
    values = list(value or [])
    while len(values) < 3:
        values.append(0.0)
    return [float(values[0]), float(values[1]), float(values[2])]


def _range_pair(value: Any) -> List[int]:
    values = list(value or [1, 120])
    if len(values) < 2:
        values.append(values[0])
    return [int(values[0]), int(values[1])]


def _length(values: List[float]) -> float:
    return round(math.sqrt(sum(value * value for value in values)), 4)


def _mirror_delta(a: List[float], b: List[float]) -> float:
    return abs(a[0] + b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])


def _uniform_scale(scale: List[float]) -> bool:
    return all(abs(value - 1.0) <= 0.001 for value in scale)


def _reviewer_claims() -> List[str]:
    return [
        "Spatial authoring checks sockets, hotspots, pose frames and mirror transfer as exportable business facts.",
        "The fixture includes one approved weapon authoring row and one intentionally blocked temporary backpack row.",
        "Contract mode performs no scene writes; Maya L3 mode creates only public synthetic joints, locators and custom attributes.",
    ]

