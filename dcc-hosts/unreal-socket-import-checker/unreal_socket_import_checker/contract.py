"""Compare Maya spatial authoring intent against Unreal socket facts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


REPORT_VERSION = "unreal-socket-import-checker@0.1.0"
NORMALIZED_SCHEMA = "unreal-socket-import-checker-input@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def resolve_public_path(path: str | Path) -> Path:
    text = str(path)
    if text.startswith("<repo>\\"):
        return PORTFOLIO_ROOT / text.replace("<repo>\\", "", 1)
    return Path(path)


def build_report(spatial_drilldown_path: str | Path, runtime_snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    source_path = resolve_public_path(spatial_drilldown_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source_l3 = _load_source_l3(source)
    runtime_snapshot = runtime_snapshot or {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "assetWrites": 0,
            "engineWrites": 0,
            "writeScope": "none",
        },
        "facts": {},
    }
    facts = build_socket_facts(source, source_l3, runtime_snapshot)
    evaluation = evaluate_socket_import(facts, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    blocked_reason = runtime.get("blockedReason")
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Socket Import Checker",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked" if blocked_reason else "L3" if executed else "L2",
        "l3Status": blocked_reason or ("unreal_socket_facts_collected" if executed else "contract_fixture_collected"),
        "sourceArtifact": {
            "path": public_path(source_path),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("summary", {}).get("gate"),
        },
        "sourceMayaL3": _source_l3_summary(source_l3),
        "unrealRuntime": runtime,
        "facts": facts,
        "evaluation": evaluation,
        "adapter": {
            "id": "unreal-socket-import-checker",
            "name": "Unreal Socket Import Checker",
            "methodSource": "Maya spatial authoring / sockets / hotspots / pose transfer to Unreal socket readiness",
            "protocolCarrier": "Spatial Authoring drilldown + Unreal Python SkeletalMesh/Skeleton socket facts",
            "boundary": {
                "mutation": "public_unreal_test_project_read_only",
                "engineWrites": runtime.get("engineWrites", 0),
                "assetWrites": runtime.get("assetWrites", 0),
                "productionWrites": 0,
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public fixture only"),
            },
        },
        "reviewerClaims": [
            "R38 joins Maya socket and hotspot authoring facts to Unreal SkeletalMesh/Skeleton socket readiness.",
            "The checker separates source authoring defects, runtime target presence, socket API readiness and missing engine socket coverage.",
            "The first Unreal socket pass is read-only; expected missing sockets become owner actions instead of silent engine mutation.",
        ],
    }


def build_socket_facts(
    source: Dict[str, Any],
    source_l3: Dict[str, Any],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    runtime_facts = runtime_snapshot.get("facts", {}).get("spatialAssets", {})
    assets = []
    for row in source.get("drilldowns", []):
        asset_id = str(row.get("assetId"))
        expected = expected_unreal_targets(asset_id, row)
        sockets_panel = _panel(row, "sockets")
        hotspot_panel = _panel(row, "hotspots")
        parent_panel = _panel(row, "parentJoint")
        transform_panel = _panel(row, "transforms")
        pose_transfer_panel = _panel(row, "poseTransfer")
        expected_sockets = _expected_sockets(sockets_panel)
        runtime_row = runtime_facts.get(asset_id, {})
        assets.append(
            {
                "assetId": asset_id,
                "assetLabel": row.get("assetLabel"),
                "sourceStatus": row.get("status"),
                "sourceIssueCount": row.get("issueCount"),
                "ownerState": row.get("ownerState"),
                "expectedUnreal": expected,
                "sourceSockets": expected_sockets,
                "sourceHotspots": _source_hotspots(hotspot_panel),
                "sourcePanels": {
                    "parentJoint": _panel_summary(parent_panel),
                    "sockets": _panel_summary(sockets_panel),
                    "hotspots": _panel_summary(hotspot_panel),
                    "transforms": _panel_summary(transform_panel),
                    "poseTransfer": _panel_summary(pose_transfer_panel),
                },
                "sourceL3": _source_l3_asset(source_l3, asset_id),
                "runtime": runtime_row,
                "normalized": _normalized(
                    row,
                    parent_panel,
                    sockets_panel,
                    hotspot_panel,
                    transform_panel,
                    pose_transfer_panel,
                    expected,
                    expected_sockets,
                    runtime_row,
                    runtime_snapshot,
                ),
            }
        )
    return {
        "schema": NORMALIZED_SCHEMA,
        "sourceRows": len(assets),
        "runtimeCollected": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "assets": assets,
    }


def evaluate_socket_import(facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("assets", []):
        evaluations.extend(_evaluate_asset(row, runtime_snapshot))
    return {
        "schema": "unreal-socket-import-checker-evaluation@0.1.0",
        "summary": _summarize(evaluations),
        "evaluations": evaluations,
        "ownerActions": _owner_actions(evaluations),
    }


def expected_unreal_targets(asset_id: str, row: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    row = row or {}
    is_tmp = "tmp" in asset_id.lower() or str(row.get("ownerState", "")).lower() == "temporary"
    suffix = "_TMP" if is_tmp else ""
    return {
        "skeletalMeshPath": "/Game/AI_Tool_TA/Characters/SK_Hero%s" % suffix,
        "skeletonPath": "/Game/AI_Tool_TA/Characters/SK_Hero%s_Skeleton" % suffix,
        "bindingPolicy": "read_existing_public_fixture_assets",
        "socketContainer": "SkeletalMesh or Skeleton sockets under /Game/AI_Tool_TA/Characters",
    }


def _normalized(
    row: Dict[str, Any],
    parent_panel: Dict[str, Any],
    sockets_panel: Dict[str, Any],
    hotspot_panel: Dict[str, Any],
    transform_panel: Dict[str, Any],
    pose_transfer_panel: Dict[str, Any],
    expected: Dict[str, Any],
    expected_sockets: List[Dict[str, Any]],
    runtime_row: Dict[str, Any],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    api = runtime_snapshot.get("runtime", {}).get("api", {})
    classes = api.get("classes", {})
    runtime_socket_names = sorted(
        set(runtime_row.get("skeletalMeshSocketNames", []))
        | set(runtime_row.get("skeletonSocketNames", []))
    )
    expected_socket_names = sorted(s["exportName"] for s in expected_sockets if s.get("exportName"))
    missing_runtime_sockets = sorted(set(expected_socket_names) - set(runtime_socket_names))
    parent_mismatches = _parent_mismatches(expected_sockets, runtime_row)
    return {
        "source.status": row.get("status"),
        "source.parentPanelStatus": parent_panel.get("status"),
        "source.socketPanelStatus": sockets_panel.get("status"),
        "source.hotspotPanelStatus": hotspot_panel.get("status"),
        "source.transformPanelStatus": transform_panel.get("status"),
        "source.poseTransferPanelStatus": pose_transfer_panel.get("status"),
        "source.parentIssues": parent_panel.get("metrics", {}).get("parentIssues", []),
        "source.offsetViolations": sockets_panel.get("metrics", {}).get("offsetViolations", []),
        "source.spaceIssues": transform_panel.get("metrics", {}).get("spaceIssues", []),
        "source.scaleIssues": transform_panel.get("metrics", {}).get("scaleIssues", []),
        "source.hotspotSemanticIssues": hotspot_panel.get("metrics", {}).get("semanticIssues", []),
        "source.poseTransferIssues": pose_transfer_panel.get("metrics", {}).get("issues", {}),
        "runtime.executed": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "runtime.socketApiReady": bool(classes.get("SkeletalMesh") and classes.get("Skeleton") and runtime_row.get("socketApiReady")),
        "runtime.skeletalMeshPath": expected.get("skeletalMeshPath"),
        "runtime.skeletalMeshExists": bool(runtime_row.get("skeletalMeshExists")),
        "runtime.skeletonPath": expected.get("skeletonPath"),
        "runtime.skeletonExists": bool(runtime_row.get("skeletonExists")),
        "runtime.expectedSocketNames": expected_socket_names,
        "runtime.socketNames": runtime_socket_names,
        "runtime.missingSockets": missing_runtime_sockets,
        "runtime.parentMismatches": parent_mismatches,
        "runtime.assetRegistryScanned": bool(runtime_snapshot.get("runtime", {}).get("assetRegistryScanned")),
    }


def _evaluate_asset(row: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    n = row.get("normalized", {})
    asset_id = row.get("assetId")
    return [
        _eval(asset_id, "source-drilldown-ready", n.get("source.status") == "Ready", "error", "Source Spatial Drilldown", "Only Ready Maya spatial authoring rows should proceed to Unreal socket approval.", str(n.get("source.status")), "Resolve Maya spatial drilldown owner actions before engine socket approval."),
        _eval(asset_id, "unreal-python-runtime", n.get("runtime.executed"), "error", "Unreal Python Runtime", "The checker must collect engine socket facts through Unreal Python.", str(n.get("runtime.executed")), "Run the L3 harness with UnrealEditor-Cmd against the public test project."),
        _eval(asset_id, "socket-api-availability", n.get("runtime.socketApiReady"), "error", "Socket API", "SkeletalMesh or Skeleton socket APIs must be visible before attach points are trusted.", str(runtime_snapshot.get("runtime", {}).get("api", {}).get("classes", {})), "Use a public Unreal project with Python, Editor Scripting and SkeletalMesh/Skeleton socket APIs available."),
        _eval(asset_id, "skeletal-target-presence", n.get("runtime.skeletalMeshExists") and n.get("runtime.skeletonExists"), "error", "Skeletal Target Presence", "Expected SkeletalMesh and Skeleton targets must exist before socket coverage can be checked.", "mesh=%s skeleton=%s" % (n.get("runtime.skeletalMeshExists"), n.get("runtime.skeletonExists")), "Import or relink the public SkeletalMesh/Skeleton before socket approval."),
        _eval(asset_id, "source-parent-joints-clean", n.get("source.parentPanelStatus") == "Ready", "error", "Source Parent Joints", "Socket and hotspot locators must bind to approved runtime joints in Maya.", str(n.get("source.parentIssues")), "Restore missing joints or remap locators to approved parent joints."),
        _eval(asset_id, "source-socket-authoring-clean", n.get("source.socketPanelStatus") == "Ready" and n.get("source.transformPanelStatus") == "Ready", "error", "Source Socket Authoring", "Socket offsets, local space and scale must be within export policy before engine import.", "offset=%s space=%s scale=%s" % (n.get("source.offsetViolations"), n.get("source.spaceIssues"), n.get("source.scaleIssues")), "Fix source socket offsets, space and scale before engine import."),
        _eval(asset_id, "engine-socket-presence", not n.get("runtime.missingSockets"), "error", "Engine Socket Presence", "Every exported Maya socket name must exist on the Unreal SkeletalMesh or Skeleton.", str(n.get("runtime.missingSockets")), "Create or import the expected public engine sockets under the approved SkeletalMesh/Skeleton target."),
        _eval(asset_id, "engine-socket-parent-binding", not n.get("runtime.parentMismatches") and not n.get("runtime.missingSockets"), "error", "Engine Socket Parent Binding", "Engine sockets must bind back to the same parent joints as the Maya authoring rows.", str(n.get("runtime.parentMismatches") or n.get("runtime.missingSockets")), "Relink engine sockets to the matching Skeleton bones or hold for owner review."),
        _eval(asset_id, "hotspot-owner-ready", n.get("source.hotspotPanelStatus") == "Ready", "warning", "Hotspot Owner Readiness", "Gameplay hotspots need approved semantic and owner metadata before engine handoff.", str(n.get("source.hotspotSemanticIssues")), "Assign hotspot semantic and owner or add an explicit waiver."),
        _eval(asset_id, "pose-transfer-ready", n.get("source.poseTransferPanelStatus") == "Ready", "warning", "Pose Transfer Readiness", "Pose transfer requires local-space pairs, target pose and owner approval.", str(n.get("source.poseTransferIssues")), "Complete pose transfer pair, target pose and approval before downstream use."),
    ]


def _eval(
    asset_id: str,
    rule_id: str,
    passed: bool,
    fail_status: str,
    label: str,
    reason: str,
    evidence: Any,
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


def _summarize(evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for row in evaluations:
        grouped.setdefault(row["assetId"], []).append(row)
    ready = []
    review = []
    blocked = []
    for asset_id, rows in grouped.items():
        statuses = [row.get("status") for row in rows]
        if "error" in statuses:
            blocked.append(asset_id)
        elif "warning" in statuses:
            review.append(asset_id)
        else:
            ready.append(asset_id)
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "spatialRows": len(grouped),
        "readyRows": len(ready),
        "reviewRows": len(review),
        "blockedRows": len(blocked),
        "pass": sum(1 for row in evaluations if row.get("status") == "pass"),
        "warning": sum(1 for row in evaluations if row.get("status") == "warning"),
        "error": sum(1 for row in evaluations if row.get("status") == "error"),
        "readyAssetIds": sorted(ready),
        "reviewAssetIds": sorted(review),
        "blockedAssetIds": sorted(blocked),
    }


def _owner_actions(evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    owner_by_rule = {
        "source-drilldown-ready": "spatial-owner",
        "unreal-python-runtime": "engine-ta",
        "socket-api-availability": "engine-ta",
        "skeletal-target-presence": "engine-ta",
        "source-parent-joints-clean": "spatial-owner",
        "source-socket-authoring-clean": "spatial-owner",
        "engine-socket-presence": "engine-ta",
        "engine-socket-parent-binding": "engine-ta",
        "hotspot-owner-ready": "gameplay-owner",
        "pose-transfer-ready": "animation-owner",
    }
    actions = []
    for row in evaluations:
        status = row.get("status")
        if status == "pass":
            continue
        actions.append(
            {
                "id": "owner-action:%s:%s" % (row.get("assetId"), row.get("ruleId")),
                "assetId": row.get("assetId"),
                "ruleId": row.get("ruleId"),
                "status": status,
                "mutationScope": "manual_review" if status == "warning" else "owner_required",
                "owner": owner_by_rule.get(row.get("ruleId"), "tool-ta"),
                "preview": row.get("fixPreview"),
                "writeBoundary": "preview_only",
            }
        )
    return actions


def _expected_sockets(sockets_panel: Dict[str, Any]) -> List[Dict[str, Any]]:
    sockets = []
    for socket in sockets_panel.get("metrics", {}).get("sockets", []):
        export_name = socket.get("exportName") or socket.get("name")
        sockets.append(
            {
                "sourceName": socket.get("name"),
                "exportName": export_name,
                "parentJoint": socket.get("parentJoint"),
                "mirrorOf": socket.get("mirrorOf"),
                "side": socket.get("side"),
                "space": socket.get("space"),
                "previewLocator": socket.get("previewLocator"),
                "translate": socket.get("translate", []),
                "rotate": socket.get("rotate", []),
                "scale": socket.get("scale", []),
                "offsetCm": socket.get("offsetCm"),
            }
        )
    return sockets


def _source_hotspots(hotspot_panel: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for hotspot in hotspot_panel.get("metrics", {}).get("hotspots", []):
        rows.append(
            {
                "sourceName": hotspot.get("name"),
                "semantic": hotspot.get("semantic"),
                "owner": hotspot.get("owner"),
                "parentJoint": hotspot.get("parentJoint"),
                "space": hotspot.get("space"),
                "previewLocator": hotspot.get("previewLocator"),
            }
        )
    return rows


def _panel_summary(panel: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": panel.get("status"),
        "label": panel.get("label"),
        "metrics": panel.get("metrics", {}),
    }


def _panel(row: Dict[str, Any], panel_id: str) -> Dict[str, Any]:
    for panel in row.get("panels", []):
        if panel.get("id") == panel_id:
            return panel
    return {"id": panel_id, "status": "Missing", "metrics": {}}


def _parent_mismatches(expected_sockets: List[Dict[str, Any]], runtime_row: Dict[str, Any]) -> List[Dict[str, Any]]:
    by_name = runtime_row.get("socketDetailsByName", {})
    mismatches = []
    for socket in expected_sockets:
        name = socket.get("exportName")
        if not name or name not in by_name:
            continue
        expected_parent = socket.get("parentJoint")
        runtime_parent = by_name.get(name, {}).get("boneName")
        if expected_parent and runtime_parent and str(expected_parent) != str(runtime_parent):
            mismatches.append(
                {
                    "socket": name,
                    "expectedParentJoint": expected_parent,
                    "runtimeBone": runtime_parent,
                }
            )
    return mismatches


def _load_source_l3(source: Dict[str, Any]) -> Dict[str, Any]:
    source_path = source.get("sourceArtifact", {}).get("path")
    if not source_path:
        return {}
    path = resolve_public_path(source_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _source_l3_summary(source_l3: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "available": bool(source_l3),
        "reportVersion": source_l3.get("reportVersion"),
        "evidenceLevel": source_l3.get("evidenceLevel"),
        "l3Status": source_l3.get("l3Status"),
        "runtimeCollected": source_l3.get("facts", {}).get("scene", {}).get("runtimeCollected"),
    }


def _source_l3_asset(source_l3: Dict[str, Any], asset_id: str) -> Dict[str, Any]:
    for row in source_l3.get("facts", {}).get("assets", []):
        if str(row.get("assetId")) == asset_id:
            return {
                "assetId": row.get("assetId"),
                "assetLabel": row.get("assetLabel"),
                "normalized": row.get("normalized", {}),
            }
    return {}
