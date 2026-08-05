"""Compare Maya character calibration intent against Unreal Control Rig facts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "unreal-control-rig-bridge@0.1.0"
NORMALIZED_SCHEMA = "unreal-control-rig-bridge-input@0.1.0"
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


def build_report(character_drilldown_path: str | Path, runtime_snapshot: Dict[str, Any] | None = None) -> Dict[str, Any]:
    source_path = resolve_public_path(character_drilldown_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source_l3 = _load_source_l3(source)
    runtime_snapshot = runtime_snapshot or {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "assetWrites": 0,
            "writeScope": "none",
        },
        "facts": {},
    }
    facts = build_bridge_facts(source, source_l3, runtime_snapshot)
    evaluation = evaluate_bridge(facts, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    blocked_reason = runtime.get("blockedReason")
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Control Rig Bridge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked" if blocked_reason else "L3" if executed else "L2",
        "l3Status": blocked_reason or ("unreal_control_rig_bridge_facts_collected" if executed else "contract_fixture_collected"),
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
            "id": "unreal-control-rig-bridge",
            "name": "Unreal Control Rig Bridge",
            "methodSource": "Maya character calibration / Control Rig mapping to Unreal runtime readiness",
            "protocolCarrier": "Character Calibration drilldown + Unreal Python Control Rig and Skeleton facts",
            "boundary": {
                "mutation": "public_unreal_test_project_read_only",
                "engineWrites": runtime.get("engineWrites", 0),
                "assetWrites": runtime.get("assetWrites", 0),
                "productionWrites": 0,
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public fixture only"),
            },
        },
        "reviewerClaims": [
            "R37 joins Maya character Control Rig intent to Unreal runtime facts instead of treating Control Rig as a Maya-only checklist.",
            "The bridge separates source mapping defects, Unreal skeleton binding, Control Rig API readiness and missing Control Rig asset coverage.",
            "The first Unreal pass is read-only against the public test project; missing CR assets block runtime approval without mutating production content.",
        ],
    }


def build_bridge_facts(
    source: Dict[str, Any],
    source_l3: Dict[str, Any],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    runtime_facts = runtime_snapshot.get("facts", {}).get("characters", {})
    characters = []
    for row in source.get("drilldowns", []):
        asset_id = str(row.get("assetId"))
        source_character = _source_character(source_l3, asset_id)
        source_control = _panel(row, "controlRig")
        source_skeleton = _panel(row, "skeleton")
        expected = expected_unreal_targets(asset_id)
        runtime_row = runtime_facts.get(asset_id, {})
        required_controls = _required_controls(source_character, source_control)
        characters.append(
            {
                "assetId": asset_id,
                "assetLabel": row.get("assetLabel"),
                "sourceStatus": row.get("status"),
                "sourceIssueCount": row.get("issueCount"),
                "sourceControlRig": {
                    "requiredCount": source_control.get("metrics", {}).get("requiredCount"),
                    "actualCount": source_control.get("metrics", {}).get("actualCount"),
                    "requiredControls": required_controls,
                    "missingControls": source_control.get("metrics", {}).get("missingControls", []),
                    "targetMismatches": source_control.get("metrics", {}).get("targetMismatches", []),
                    "unresolvedTargets": source_control.get("metrics", {}).get("unresolvedTargets", []),
                    "panelStatus": source_control.get("status"),
                },
                "sourceSkeleton": {
                    "missing": source_skeleton.get("metrics", {}).get("missing", []),
                    "temporary": source_skeleton.get("metrics", {}).get("temporary", []),
                    "panelStatus": source_skeleton.get("status"),
                },
                "expectedUnreal": expected,
                "runtime": runtime_row,
                "normalized": _normalized(row, source_control, source_skeleton, expected, runtime_row, runtime_snapshot),
            }
        )
    return {
        "schema": NORMALIZED_SCHEMA,
        "sourceRows": len(characters),
        "runtimeCollected": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "characters": characters,
    }


def evaluate_bridge(facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("characters", []):
        evaluations.extend(_evaluate_character(row, runtime_snapshot))
    return {
        "schema": "unreal-control-rig-bridge-evaluation@0.1.0",
        "summary": _summarize(evaluations),
        "evaluations": evaluations,
        "ownerActions": _owner_actions(evaluations),
    }


def expected_unreal_targets(asset_id: str) -> Dict[str, Any]:
    is_tmp = "tmp" in asset_id.lower()
    if not is_tmp:
        return {
            "skeletalMeshPath": "/Game/AI_Tool_TA/Characters/SK_HeroFace",
            "skeletonPath": "/Game/AI_Tool_TA/Characters/SK_HeroFace_Skeleton",
            "controlRigPath": "/Game/AI_Tool_TA/Characters/CR_HeroFace",
            "bindingPolicy": "read_existing_public_face_skeleton_fixture_assets",
        }
    suffix = "_TMP"
    return {
        "skeletalMeshPath": "/Game/AI_Tool_TA/Characters/SK_Hero%s" % suffix,
        "skeletonPath": "/Game/AI_Tool_TA/Characters/SK_Hero%s_Skeleton" % suffix,
        "controlRigPath": "/Game/AI_Tool_TA/Characters/CR_HeroFace%s" % suffix,
        "bindingPolicy": "read_existing_public_fixture_assets",
    }


def _normalized(
    row: Dict[str, Any],
    source_control: Dict[str, Any],
    source_skeleton: Dict[str, Any],
    expected: Dict[str, Any],
    runtime_row: Dict[str, Any],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    api = runtime_snapshot.get("runtime", {}).get("api", {})
    classes = api.get("classes", {})
    required_controls = set(runtime_row.get("requiredControls", []))
    runtime_controls = set(runtime_row.get("controlRigFacts", {}).get("controls", []))
    return {
        "source.status": row.get("status"),
        "source.controlRigPanelStatus": source_control.get("status"),
        "source.skeletonPanelStatus": source_skeleton.get("status"),
        "source.missingControls": source_control.get("metrics", {}).get("missingControls", []),
        "source.targetMismatches": source_control.get("metrics", {}).get("targetMismatches", []),
        "source.unresolvedTargets": source_control.get("metrics", {}).get("unresolvedTargets", []),
        "source.missingJoints": source_skeleton.get("metrics", {}).get("missing", []),
        "source.temporaryJoints": source_skeleton.get("metrics", {}).get("temporary", []),
        "runtime.executed": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "runtime.controlRigApiReady": bool(classes.get("ControlRigBlueprint") or classes.get("ControlRig")),
        "runtime.skeletalMeshPath": expected.get("skeletalMeshPath"),
        "runtime.skeletalMeshExists": bool(runtime_row.get("skeletalMeshExists")),
        "runtime.skeletonPath": expected.get("skeletonPath"),
        "runtime.skeletonExists": bool(runtime_row.get("skeletonExists")),
        "runtime.controlRigPath": expected.get("controlRigPath"),
        "runtime.controlRigExists": bool(runtime_row.get("controlRigExists")),
        "runtime.requiredControls": sorted(required_controls),
        "runtime.controlsReadable": bool(runtime_row.get("controlRigFacts", {}).get("controlsReadable")),
        "runtime.missingControls": sorted(required_controls - runtime_controls) if runtime_controls else sorted(required_controls),
        "runtime.assetRegistryScanned": bool(runtime_snapshot.get("runtime", {}).get("assetRegistryScanned")),
    }


def _evaluate_character(row: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    n = row.get("normalized", {})
    asset_id = row.get("assetId")
    return [
        _eval(asset_id, "source-drilldown-ready", n.get("source.status") == "Ready", "error", "Source Character Drilldown", "Only Ready Maya character calibration rows should proceed to Unreal Control Rig binding.", str(n.get("source.status")), "Resolve Maya character drilldown owner actions before engine bridge."),
        _eval(asset_id, "unreal-python-runtime", n.get("runtime.executed"), "error", "Unreal Python Runtime", "The bridge must collect engine facts through Unreal Python.", str(n.get("runtime.executed")), "Run the L3 harness with UnrealEditor-Cmd against the public test project."),
        _eval(asset_id, "control-rig-api-availability", n.get("runtime.controlRigApiReady"), "error", "Control Rig API", "Unreal Control Rig API or plugin must be visible before mapping facts are trusted.", str(runtime_snapshot.get("runtime", {}).get("api", {}).get("classes", {})), "Enable ControlRig plugin in the public test project."),
        _eval(asset_id, "skeletal-mesh-binding", n.get("runtime.skeletalMeshExists") and n.get("runtime.skeletonExists"), "error", "Skeletal Mesh Binding", "Control Rig mapping needs an existing SkeletalMesh and Skeleton target.", "mesh=%s skeleton=%s" % (n.get("runtime.skeletalMeshExists"), n.get("runtime.skeletonExists")), "Import or relink the public SkeletalMesh/Skeleton before bridge approval."),
        _eval(asset_id, "maya-control-mapping-clean", n.get("source.controlRigPanelStatus") == "Ready", "error", "Maya Control Mapping", "Maya control mapping must have no missing controls, mismatches or unresolved deformation targets.", "missing=%s mismatch=%s unresolved=%s" % (n.get("source.missingControls"), n.get("source.targetMismatches"), n.get("source.unresolvedTargets")), "Complete source Control Rig mapping in Maya before Unreal binding."),
        _eval(asset_id, "control-rig-asset-presence", n.get("runtime.controlRigExists"), "error", "Control Rig Asset", "The expected Unreal Control Rig asset must exist before runtime control coverage can be audited.", n.get("runtime.controlRigPath"), "Create or import the public Control Rig asset under the expected engine path."),
        _eval(asset_id, "runtime-control-coverage", n.get("runtime.controlRigExists") and not n.get("runtime.missingControls"), "error", "Runtime Control Coverage", "Runtime Control Rig controls must cover every required Maya control mapping.", str(n.get("runtime.missingControls")), "Regenerate Control Rig controls or attach an explicit owner waiver."),
        _eval(asset_id, "deformation-target-coverage", not n.get("source.missingJoints") and not n.get("source.temporaryJoints"), "warning", "Deformation Target Coverage", "Missing or temporary Maya deformation joints should not enter engine Control Rig binding.", "missing=%s tmp=%s" % (n.get("source.missingJoints"), n.get("source.temporaryJoints")), "Restore approved deformation joints or hold the bridge for owner review."),
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
        "evidence": str(evidence),
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
        "characterRows": len(asset_ids),
        "readyRows": len(ready),
        "reviewRows": len(review),
        "blockedRows": len(blocked),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "readyAssetIds": ready,
        "reviewAssetIds": review,
        "blockedAssetIds": blocked,
    }


def _owner_actions(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": "owner-action:%s" % row["id"],
            "assetId": row["assetId"],
            "ruleId": row["ruleId"],
            "status": row["status"],
            "mutationScope": "owner_required" if row["status"] == "error" else "manual_review",
            "owner": _owner_for_rule(row["ruleId"]),
            "preview": row["fixPreview"],
            "writeBoundary": "preview_only",
        }
        for row in evaluations
        if row["status"] != "pass"
    ]


def _owner_for_rule(rule_id: str) -> str:
    if rule_id in ("unreal-python-runtime", "control-rig-api-availability", "skeletal-mesh-binding"):
        return "engine-ta"
    if rule_id in ("control-rig-asset-presence", "runtime-control-coverage"):
        return "control-rig-owner"
    if rule_id in ("source-drilldown-ready", "maya-control-mapping-clean", "deformation-target-coverage"):
        return "character-owner"
    return "reviewer"


def _load_source_l3(source: Dict[str, Any]) -> Dict[str, Any]:
    path_text = source.get("sourceArtifact", {}).get("path")
    if not path_text:
        return {}
    path = resolve_public_path(path_text)
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


def _source_character(source_l3: Dict[str, Any], asset_id: str) -> Dict[str, Any]:
    for row in source_l3.get("facts", {}).get("characters", []):
        if row.get("assetId") == asset_id:
            return row
    return {}


def _panel(row: Dict[str, Any], panel_id: str) -> Dict[str, Any]:
    for panel in row.get("panels", []):
        if panel.get("id") == panel_id:
            return panel
    return {"id": panel_id, "status": "Missing", "metrics": {}}


def _required_controls(source_character: Dict[str, Any], source_control: Dict[str, Any]) -> List[str]:
    raw = source_character.get("raw", {}).get("controlRigMappings", {})
    controls = set(str(name) for name in raw.keys())
    controls.update(str(name) for name in source_control.get("metrics", {}).get("missingControls", []))
    for mismatch in source_control.get("metrics", {}).get("targetMismatches", []):
        controls.add(str(mismatch.get("control")))
    return sorted(name for name in controls if name and name != "None")
