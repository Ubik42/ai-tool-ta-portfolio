"""Build UI-ready drilldown data from Maya spatial authoring evidence."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path


REPORT_VERSION = "spatial-authoring-drilldown@0.1.0"
PANEL_RULES = {
    "protocol": ["protocol-carrier"],
    "parentJoint": ["parent-joint-coverage"],
    "sockets": ["socket-offset-tolerance"],
    "mirror": ["mirror-pair-symmetry"],
    "hotspots": ["hotspot-semantic-owner"],
    "poseFrames": ["pose-frame-coverage-range"],
    "transforms": ["transform-scale-lock", "local-space-consistency"],
    "preview": ["preview-locator-presence"],
    "poseTransfer": ["pose-transfer-boundary"],
}


def build_drilldown_report(l3_artifact_path: str | Path) -> Dict[str, Any]:
    artifact_path = Path(l3_artifact_path)
    source = json.loads(artifact_path.read_text(encoding="utf-8"))
    assets = source.get("facts", {}).get("assets", [])
    evaluations = source.get("evaluation", {}).get("evaluations", [])
    fix_preview = source.get("evaluation", {}).get("fixPreview", [])
    evaluation_index = _group_by_asset(evaluations)
    fix_index = _group_by_asset(fix_preview)
    drilldowns = [
        _asset_drilldown(row, evaluation_index.get(row.get("assetId"), []), fix_index.get(row.get("assetId"), []))
        for row in assets
    ]
    summary = _summarize(drilldowns, source)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Spatial Authoring Workbench",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-derived",
        "l3Status": "maya_spatial_authoring_rows_to_drilldown",
        "sourceArtifact": {
            "path": public_path(artifact_path),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "summary": summary,
        "uiContract": {
            "schema": "spatial-authoring-drilldown-ui@0.1.0",
            "defaultAssetId": _default_asset(drilldowns),
            "assetSelector": [
                {
                    "assetId": row["assetId"],
                    "label": row["assetLabel"],
                    "status": row["status"],
                    "issueCount": row["issueCount"],
                }
                for row in drilldowns
            ],
            "tabs": [
                "protocol",
                "parentJoint",
                "sockets",
                "mirror",
                "hotspots",
                "poseFrames",
                "transforms",
                "preview",
                "poseTransfer",
                "ownerActions",
            ],
        },
        "drilldowns": drilldowns,
        "adapter": {
            "id": "spatial-authoring-drilldown",
            "name": "Spatial Authoring Maya Drilldown",
            "methodSource": "Maya L3 socket, hotspot, pose frame and pose transfer facts to UI drilldown",
            "protocolCarrier": "Maya joints, locator transforms, spatial custom attributes and fix preview evidence",
            "boundary": {
                "mutation": "drilldown_projection_only",
                "sceneWrites": 0,
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "reviewerClaims": [
            "R36 turns Maya L3 spatial authoring rows into reviewer-oriented drilldown data instead of another flat checklist.",
            "Every blocked spatial asset shows the exact parent joint, socket offset, mirror, hotspot, pose frame and pose transfer reasons behind the hold.",
            "Owner actions keep spatial mutation scope explicit: owner_required and manual_review are separated.",
            "The drilldown is derived from Maya runtime facts and does not mutate production DCC or engine assets.",
        ],
    }


def _asset_drilldown(
    row: Dict[str, Any],
    evaluations: List[Dict[str, Any]],
    fixes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    normalized = row.get("normalized", {})
    raw = row.get("raw", {})
    panels = [_panel(panel_id, normalized, raw, evaluations) for panel_id in PANEL_RULES]
    owner_actions = [_owner_action(fix, evaluations) for fix in fixes]
    status = _asset_status(evaluations)
    return {
        "assetId": row.get("assetId"),
        "assetLabel": row.get("assetLabel"),
        "status": status,
        "sourceDcc": row.get("sourceDcc"),
        "ownerState": normalized.get("asset.ownerState"),
        "issueCount": sum(1 for item in evaluations if item.get("status") in ("warning", "error")),
        "errorCount": sum(1 for item in evaluations if item.get("status") == "error"),
        "warningCount": sum(1 for item in evaluations if item.get("status") == "warning"),
        "panels": panels,
        "ownerActions": owner_actions,
        "mutationBoundary": {
            "canAutoFix": False,
            "ownerRequiredActions": sum(1 for item in owner_actions if item.get("mutationScope") == "owner_required"),
            "manualReviewActions": sum(1 for item in owner_actions if item.get("mutationScope") == "manual_review"),
            "productionWrites": 0,
        },
    }


def _panel(
    panel_id: str,
    normalized: Dict[str, Any],
    raw: Dict[str, Any],
    evaluations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    rules = PANEL_RULES[panel_id]
    panel_evals = [item for item in evaluations if item.get("ruleId") in rules]
    return {
        "id": panel_id,
        "label": _label(panel_id),
        "status": _panel_status(panel_evals),
        "metrics": _metrics(panel_id, normalized, raw),
        "evidenceRows": panel_evals,
    }


def _metrics(panel_id: str, n: Dict[str, Any], raw: Dict[str, Any]) -> Dict[str, Any]:
    constraints = raw.get("constraints", {})
    if panel_id == "protocol":
        return {
            "schema": n.get("spatial.protocol.schema"),
            "ownerState": n.get("asset.ownerState"),
            "namespace": raw.get("namespace"),
            "rootNode": raw.get("rootNode"),
        }
    if panel_id == "parentJoint":
        return {
            "expectedCount": n.get("joints.expectedCount"),
            "actualCount": n.get("joints.actualCount"),
            "missingJoints": n.get("joints.missing"),
            "temporaryJoints": n.get("joints.tmp"),
            "parentIssues": n.get("parentJoint.missing"),
        }
    if panel_id == "sockets":
        return {
            "count": n.get("sockets.count"),
            "names": n.get("sockets.names"),
            "offsetViolations": n.get("sockets.offsetViolations"),
            "maxSocketOffsetCm": constraints.get("maxSocketOffsetCm"),
            "sockets": raw.get("sockets", []),
        }
    if panel_id == "mirror":
        return {
            "pairs": n.get("mirror.pairs"),
            "missingPairs": n.get("mirror.missingPairs"),
            "symmetryViolations": n.get("mirror.symmetryViolations"),
            "maxMirrorDeltaCm": constraints.get("maxMirrorDeltaCm"),
        }
    if panel_id == "hotspots":
        return {
            "count": n.get("hotspots.count"),
            "semanticIssues": n.get("hotspots.semanticIssues"),
            "allowedSemantics": constraints.get("allowedHotspotSemantics"),
            "requiredOwners": constraints.get("requiredHotspotOwners"),
            "hotspots": raw.get("hotspots", []),
        }
    if panel_id == "poseFrames":
        return {
            "count": n.get("poseFrames.count"),
            "required": n.get("poseFrames.required"),
            "issues": n.get("poseFrames.issues"),
            "poseFrameRange": constraints.get("poseFrameRange"),
            "poseFrames": raw.get("poseFrames", []),
        }
    if panel_id == "transforms":
        return {
            "scaleIssues": n.get("transforms.scaleIssues"),
            "spaceIssues": n.get("transforms.spaceIssues"),
            "allowedSpaces": constraints.get("allowedSpaces"),
            "requireUniformScale": constraints.get("requireUniformScale"),
        }
    if panel_id == "preview":
        return {
            "missing": n.get("previewLocator.missing"),
            "requirePreviewLocator": constraints.get("requirePreviewLocator"),
        }
    if panel_id == "poseTransfer":
        return {
            "requiredPairs": n.get("poseTransfer.requiredPairs"),
            "issues": n.get("poseTransfer.issues"),
            "payload": raw.get("poseTransfer"),
        }
    return {}


def _owner_action(fix: Dict[str, Any], evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    evaluation = next((item for item in evaluations if item.get("ruleId") == fix.get("ruleId")), {})
    return {
        "id": "owner-action:%s:%s" % (fix.get("assetId"), fix.get("ruleId")),
        "assetId": fix.get("assetId"),
        "ruleId": fix.get("ruleId"),
        "status": fix.get("status"),
        "mutationScope": fix.get("mutationScope"),
        "owner": _owner_for_rule(str(fix.get("ruleId")), str(fix.get("mutationScope"))),
        "evidence": evaluation.get("evidence"),
        "reason": evaluation.get("reason"),
        "fixPreview": fix.get("preview"),
        "writeBoundary": "preview_only",
    }


def _summarize(drilldowns: Iterable[Dict[str, Any]], source: Dict[str, Any]) -> Dict[str, Any]:
    rows = list(drilldowns)
    owner_actions = [action for row in rows for action in row.get("ownerActions", [])]
    blocked = sum(1 for row in rows if row["status"] == "Blocked")
    review = sum(1 for row in rows if row["status"] == "Review")
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "assetDrilldowns": len(rows),
        "panelCount": sum(len(row.get("panels", [])) for row in rows),
        "readyAssets": sum(1 for row in rows if row["status"] == "Ready"),
        "reviewAssets": review,
        "blockedAssets": blocked,
        "issueCount": sum(row.get("issueCount", 0) for row in rows),
        "ownerActions": len(owner_actions),
        "ownerRequiredActions": sum(1 for action in owner_actions if action.get("mutationScope") == "owner_required"),
        "manualReviewActions": sum(1 for action in owner_actions if action.get("mutationScope") == "manual_review"),
        "sourcePass": source.get("evaluation", {}).get("summary", {}).get("pass"),
        "sourceWarning": source.get("evaluation", {}).get("summary", {}).get("warning"),
        "sourceError": source.get("evaluation", {}).get("summary", {}).get("error"),
        "productionWrites": 0,
    }


def _asset_status(evaluations: List[Dict[str, Any]]) -> str:
    if any(item.get("status") == "error" for item in evaluations):
        return "Blocked"
    if any(item.get("status") == "warning" for item in evaluations):
        return "Review"
    return "Ready"


def _panel_status(evaluations: List[Dict[str, Any]]) -> str:
    if any(item.get("status") == "error" for item in evaluations):
        return "Blocked"
    if any(item.get("status") == "warning" for item in evaluations):
        return "Review"
    return "Ready"


def _group_by_asset(rows: Iterable[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    result: Dict[str, List[Dict[str, Any]]] = {}
    for row in rows:
        result.setdefault(str(row.get("assetId")), []).append(row)
    return result


def _default_asset(drilldowns: List[Dict[str, Any]]) -> str | None:
    blocked = [row for row in drilldowns if row["status"] == "Blocked"]
    return (blocked or drilldowns)[0].get("assetId") if drilldowns else None


def _owner_for_rule(rule_id: str, mutation_scope: str) -> str:
    if mutation_scope == "manual_review":
        return "reviewer"
    return {
        "parent-joint-coverage": "technical-animation-owner",
        "socket-offset-tolerance": "technical-animation-owner",
        "mirror-pair-symmetry": "technical-animation-owner",
        "hotspot-semantic-owner": "gameplay-vfx-owner",
        "pose-frame-coverage-range": "animation-owner",
        "local-space-consistency": "technical-animation-owner",
        "pose-transfer-boundary": "animation-owner",
    }.get(rule_id, "spatial-owner")


def _label(panel_id: str) -> str:
    return {
        "protocol": "Protocol",
        "parentJoint": "Parent Joint",
        "sockets": "Sockets",
        "mirror": "Mirror Pairs",
        "hotspots": "Hotspots",
        "poseFrames": "Pose Frames",
        "transforms": "Transforms",
        "preview": "Preview Locators",
        "poseTransfer": "Pose Transfer",
    }.get(panel_id, panel_id)
