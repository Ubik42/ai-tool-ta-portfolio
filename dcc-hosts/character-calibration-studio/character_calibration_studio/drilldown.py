"""Build UI-ready drilldown data from Maya character calibration evidence."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .contract import public_path


REPORT_VERSION = "character-calibration-drilldown@0.1.0"
PANEL_RULES = {
    "topology": ["topology-signature"],
    "skeleton": ["joint-coverage", "tmp-joint-boundary"],
    "skin": ["skin-influence-budget"],
    "calibration": ["calibration-delta"],
    "face": ["face-param-coverage"],
    "controlRig": ["control-rig-mapping"],
    "mirror": ["mirror-pair-coverage"],
}


def build_drilldown_report(l3_artifact_path: str | Path) -> Dict[str, Any]:
    artifact_path = Path(l3_artifact_path)
    source = json.loads(artifact_path.read_text(encoding="utf-8"))
    characters = source.get("facts", {}).get("characters", [])
    evaluations = source.get("evaluation", {}).get("evaluations", [])
    fix_preview = source.get("evaluation", {}).get("fixPreview", [])
    evaluation_index = _group_by_asset(evaluations)
    fix_index = _group_by_asset(fix_preview)
    drilldowns = [
        _character_drilldown(row, evaluation_index.get(row.get("assetId"), []), fix_index.get(row.get("assetId"), []))
        for row in characters
    ]
    summary = _summarize(drilldowns, source)
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Character Calibration Studio",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3-derived",
        "l3Status": "maya_character_calibration_rows_to_drilldown",
        "sourceArtifact": {
            "path": public_path(artifact_path),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "summary": summary,
        "uiContract": {
            "schema": "character-calibration-drilldown-ui@0.1.0",
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
            "tabs": ["topology", "skeleton", "skin", "calibration", "face", "controlRig", "mirror", "ownerActions"],
        },
        "drilldowns": drilldowns,
        "adapter": {
            "id": "character-calibration-drilldown",
            "name": "Character Calibration Maya Drilldown",
            "methodSource": "Maya L3 character calibration facts to UI drilldown and owner action rows",
            "protocolCarrier": "Maya topology, joint DAG, skin, face params, Control Rig mapping and fix preview evidence",
            "boundary": {
                "mutation": "drilldown_projection_only",
                "sceneWrites": 0,
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "reviewerClaims": [
            "R35 turns Maya L3 character calibration rows into reviewer-oriented drilldown data instead of another flat checklist.",
            "Every blocked character shows the exact topology, joint, skin, face parameter and Control Rig reasons behind the hold.",
            "Owner actions keep mutation scope explicit: owner_required and manual_review are separated.",
            "The drilldown is derived from Maya runtime facts and does not mutate production character assets.",
        ],
    }


def _character_drilldown(
    row: Dict[str, Any],
    evaluations: List[Dict[str, Any]],
    fixes: List[Dict[str, Any]],
) -> Dict[str, Any]:
    normalized = row.get("normalized", {})
    panels = [_panel(panel_id, normalized, evaluations) for panel_id in PANEL_RULES]
    owner_actions = [_owner_action(fix, evaluations) for fix in fixes]
    status = _asset_status(evaluations)
    return {
        "assetId": row.get("assetId"),
        "assetLabel": row.get("assetLabel"),
        "status": status,
        "sourceDcc": row.get("sourceDcc"),
        "ownerState": normalized.get("character.ownerState"),
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


def _panel(panel_id: str, normalized: Dict[str, Any], evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    rules = PANEL_RULES[panel_id]
    panel_evals = [item for item in evaluations if item.get("ruleId") in rules]
    return {
        "id": panel_id,
        "label": _label(panel_id),
        "status": _panel_status(panel_evals),
        "metrics": _metrics(panel_id, normalized),
        "evidenceRows": panel_evals,
    }


def _metrics(panel_id: str, n: Dict[str, Any]) -> Dict[str, Any]:
    if panel_id == "topology":
        return {
            "actualSignature": n.get("mesh.topologySignature"),
            "expectedSignature": n.get("mesh.expectedTopologySignature"),
            "vertexCount": n.get("mesh.vertexCount"),
            "edgeCount": n.get("mesh.edgeCount"),
            "faceCount": n.get("mesh.faceCount"),
        }
    if panel_id == "skeleton":
        return {
            "expectedCount": n.get("joints.expectedCount"),
            "actualCount": n.get("joints.actualCount"),
            "missing": n.get("joints.missing"),
            "extra": n.get("joints.extra"),
            "temporary": n.get("joints.tmp"),
        }
    if panel_id == "skin":
        return {
            "maxInfluences": n.get("skin.maxInfluences"),
            "influenceBudget": n.get("skin.influenceBudget"),
        }
    if panel_id == "calibration":
        return {
            "maxDelta": n.get("calibration.maxDelta"),
            "allowedMaxDelta": n.get("calibration.allowedMaxDelta"),
        }
    if panel_id == "face":
        return {
            "requiredCount": n.get("faceParams.requiredCount"),
            "actualCount": n.get("faceParams.actualCount"),
            "missing": n.get("faceParams.missing"),
            "outOfRange": n.get("faceParams.outOfRange"),
        }
    if panel_id == "controlRig":
        return {
            "requiredCount": n.get("controlRig.requiredCount"),
            "actualCount": n.get("controlRig.actualCount"),
            "missingControls": n.get("controlRig.missingControls"),
            "targetMismatches": n.get("controlRig.targetMismatches"),
            "unresolvedTargets": n.get("controlRig.unresolvedTargets"),
        }
    if panel_id == "mirror":
        return {"missingPairs": n.get("mirror.missingPairs")}
    return {}


def _owner_action(fix: Dict[str, Any], evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    evaluation = next((item for item in evaluations if item.get("ruleId") == fix.get("ruleId")), {})
    return {
        "id": "owner-action:%s:%s" % (fix.get("assetId"), fix.get("ruleId")),
        "assetId": fix.get("assetId"),
        "ruleId": fix.get("ruleId"),
        "status": fix.get("status"),
        "mutationScope": fix.get("mutationScope"),
        "owner": "character-owner" if fix.get("mutationScope") == "owner_required" else "reviewer",
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


def _label(panel_id: str) -> str:
    return {
        "topology": "Topology",
        "skeleton": "Skeleton",
        "skin": "Skin",
        "calibration": "Calibration Delta",
        "face": "Face Params",
        "controlRig": "Control Rig",
        "mirror": "Mirror Pairs",
    }.get(panel_id, panel_id)
