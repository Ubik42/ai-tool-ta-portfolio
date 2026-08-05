"""Character calibration contract.

The module models a Lightbox-style character handoff check: topology and rig
facts must remain stable before DNA / face-control / Control Rig data can be
trusted downstream.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "character-calibration-contract@0.1.0"
NORMALIZED_SCHEMA = "character-calibration-input@0.1.0"
FIXTURE_SCHEMA = "synthetic-character-calibration-scene@0.1.0"
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
    return build_facts_from_characters(
        scene=fixture.get("scene", {}),
        characters=fixture.get("characters", []),
        source_dcc="Fixture",
        runtime_collected=False,
    )


def build_facts_from_characters(
    scene: Dict[str, Any],
    characters: List[Dict[str, Any]],
    source_dcc: str,
    runtime_collected: bool,
) -> Dict[str, Any]:
    rows = [_build_character_facts(character, source_dcc) for character in characters]
    return {
        "schema": NORMALIZED_SCHEMA,
        "scene": {
            "sourceDcc": source_dcc,
            "unit": scene.get("unit"),
            "upAxis": scene.get("upAxis"),
            "characterCount": len(rows),
            "runtimeCollected": runtime_collected,
        },
        "characters": rows,
    }


def evaluate_scene(facts: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("characters", []):
        evaluations.extend(_evaluate_character(row))
    return {
        "schema": "character-calibration-evaluation@0.1.0",
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
        "generatedBy": "AI Tool TA Portfolio / Character Calibration Studio",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2",
        "l3Status": "contract_fixture_collected",
        "fixture": {
            "path": public_path(fixture_path),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "adapter": {
            "id": "character-calibration",
            "name": "Character Calibration & Intent Transfer Studio",
            "methodSource": "Lightbox character DNA / topology / joint coverage / Control Rig transfer",
            "protocolCarrier": "Maya mesh topology + joint list + calibration payload + face-control mapping",
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


def _build_character_facts(character: Dict[str, Any], source_dcc: str) -> Dict[str, Any]:
    mesh = character.get("mesh", {})
    skeleton = character.get("skeleton", {})
    calibration = character.get("calibration", {})
    face_params = character.get("faceParams", {})
    control_rig = character.get("controlRig", {})
    actual_joints = [str(name) for name in skeleton.get("actualJoints", [])]
    expected_joints = [str(name) for name in skeleton.get("expectedJoints", [])]
    actual_params = face_params.get("actual", {})
    required_params = [str(name) for name in face_params.get("required", [])]
    actual_mappings = control_rig.get("actualMappings", {})
    required_mappings = control_rig.get("requiredMappings", {})
    deltas = [float(sample.get("delta", 0.0)) for sample in calibration.get("samples", [])]
    max_delta = max(deltas or [0.0])
    topology_signature = mesh.get("topologySignature") or _topology_signature(
        int(mesh.get("actualVertexCount", mesh.get("expectedVertexCount", 0)) or 0),
        int(mesh.get("actualEdgeCount", mesh.get("expectedEdgeCount", 0)) or 0),
        int(mesh.get("actualFaceCount", mesh.get("expectedFaceCount", 0)) or 0),
    )
    return {
        "assetId": character.get("id"),
        "assetLabel": character.get("label"),
        "sourceDcc": source_dcc,
        "normalizedSchema": NORMALIZED_SCHEMA,
        "protocolCarrier": "mesh topology + joint list + calibration payload + control mapping",
        "sourceFields": {
            "topology": "mesh vertex/edge/face counts",
            "joints": "joint DAG names under character root",
            "calibration": "aiToolTaCalibrationSamples payload",
            "faceParams": "aiToolTaFaceParams payload",
            "controlRig": "aiToolTaControlRigMap payload",
        },
        "normalized": {
            "character.protocol.schema": character.get("protocolSchema", "character-calibration@dcc-r26"),
            "character.ownerState": character.get("ownerState"),
            "mesh.name": mesh.get("name"),
            "mesh.topologySignature": topology_signature,
            "mesh.expectedTopologySignature": mesh.get("expectedTopologySignature"),
            "mesh.vertexCount": int(mesh.get("actualVertexCount", mesh.get("expectedVertexCount", 0)) or 0),
            "mesh.edgeCount": int(mesh.get("actualEdgeCount", mesh.get("expectedEdgeCount", 0)) or 0),
            "mesh.faceCount": int(mesh.get("actualFaceCount", mesh.get("expectedFaceCount", 0)) or 0),
            "joints.expectedCount": len(expected_joints),
            "joints.actualCount": len(actual_joints),
            "joints.missing": sorted(set(expected_joints) - set(actual_joints)),
            "joints.extra": sorted(set(actual_joints) - set(expected_joints)),
            "joints.tmp": sorted(name for name in actual_joints if "TMP" in name.upper() or name.upper().startswith("TMP")),
            "skin.maxInfluences": int(character.get("skin", {}).get("maxInfluences", 0) or 0),
            "skin.influenceBudget": int(character.get("skin", {}).get("influenceBudget", 0) or 0),
            "calibration.maxDelta": max_delta,
            "calibration.allowedMaxDelta": float(calibration.get("maxDelta", 0.0) or 0.0),
            "faceParams.requiredCount": len(required_params),
            "faceParams.actualCount": len(actual_params),
            "faceParams.missing": sorted(set(required_params) - set(actual_params)),
            "faceParams.outOfRange": _out_of_range_params(actual_params, face_params.get("range", [0.0, 1.0])),
            "controlRig.requiredCount": len(required_mappings),
            "controlRig.actualCount": len(actual_mappings),
            "controlRig.missingControls": sorted(set(required_mappings) - set(actual_mappings)),
            "controlRig.targetMismatches": sorted(
                [
                    {
                        "control": control,
                        "expected": expected_target,
                        "actual": actual_mappings.get(control),
                    }
                    for control, expected_target in required_mappings.items()
                    if control in actual_mappings and actual_mappings.get(control) != expected_target
                ],
                key=lambda row: row["control"],
            ),
            "controlRig.unresolvedTargets": sorted(
                control
                for control, target in actual_mappings.items()
                if target not in actual_joints
            ),
            "mirror.missingPairs": _missing_mirror_pairs(skeleton.get("mirrorPairs", []), actual_joints),
        },
        "raw": {
            "namespace": character.get("namespace"),
            "mesh": mesh,
            "expectedJoints": expected_joints,
            "actualJoints": actual_joints,
            "calibrationSamples": calibration.get("samples", []),
            "faceParams": actual_params,
            "controlRigMappings": actual_mappings,
        },
    }


def _evaluate_character(row: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = row.get("assetId")
    n = row.get("normalized", {})
    return [
        _eval(
            asset_id,
            "protocol-carrier",
            n.get("character.protocol.schema") == "character-calibration@dcc-r26",
            "error",
            "Calibration protocol carrier",
            "Character calibration checks need a typed protocol before transfer.",
            str(n.get("character.protocol.schema")),
            "Write character-calibration@dcc-r26 on the character root.",
        ),
        _eval(
            asset_id,
            "topology-signature",
            n.get("mesh.topologySignature") == n.get("mesh.expectedTopologySignature"),
            "error",
            "Topology signature",
            "DNA, blendshape and facial calibration data require stable vertex/edge/face topology.",
            "actual=%s expected=%s"
            % (n.get("mesh.topologySignature"), n.get("mesh.expectedTopologySignature")),
            "Rebuild from the approved head topology or regenerate downstream calibration.",
        ),
        _eval(
            asset_id,
            "joint-coverage",
            not n.get("joints.missing"),
            "error",
            "Joint coverage",
            "Required deformation and face joints must exist before Control Rig mapping is trusted.",
            "missing=%s actual=%s" % (n.get("joints.missing"), n.get("joints.actualCount")),
            "Restore missing joints or attach an owner-approved retarget map.",
        ),
        _eval(
            asset_id,
            "tmp-joint-boundary",
            not n.get("joints.tmp"),
            "warning",
            "Temporary joint boundary",
            "TMP joints are review-only and should not enter downstream character runtime.",
            str(n.get("joints.tmp")),
            "Rename, delete, or explicitly waive temporary joints before export.",
        ),
        _eval(
            asset_id,
            "skin-influence-budget",
            int(n.get("skin.maxInfluences") or 0) <= int(n.get("skin.influenceBudget") or 0),
            "error",
            "Skin influence budget",
            "Runtime character assets must stay within the agreed influence budget.",
            "max=%s budget=%s" % (n.get("skin.maxInfluences"), n.get("skin.influenceBudget")),
            "Prune weights or move this asset to a higher-cost platform bucket.",
        ),
        _eval(
            asset_id,
            "calibration-delta",
            float(n.get("calibration.maxDelta") or 0.0) <= float(n.get("calibration.allowedMaxDelta") or 0.0),
            "error",
            "Calibration delta",
            "Sculpt or wrap deltas beyond tolerance can invalidate face DNA / expression transfer.",
            "maxDelta=%.4f allowed=%.4f"
            % (float(n.get("calibration.maxDelta") or 0.0), float(n.get("calibration.allowedMaxDelta") or 0.0)),
            "Re-wrap the sculpt or regenerate calibration deltas from the approved base.",
        ),
        _eval(
            asset_id,
            "face-param-coverage",
            not n.get("faceParams.missing") and not n.get("faceParams.outOfRange"),
            "error",
            "Face parameter coverage",
            "Required face parameters must exist and stay within the declared control range.",
            "missing=%s outOfRange=%s" % (n.get("faceParams.missing"), n.get("faceParams.outOfRange")),
            "Restore missing controls and clamp or remap out-of-range parameters.",
        ),
        _eval(
            asset_id,
            "control-rig-mapping",
            not n.get("controlRig.missingControls")
            and not n.get("controlRig.targetMismatches")
            and not n.get("controlRig.unresolvedTargets"),
            "error",
            "Control Rig mapping",
            "Every required runtime control must resolve to an existing deformation target.",
            "missing=%s mismatch=%s unresolved=%s"
            % (
                n.get("controlRig.missingControls"),
                n.get("controlRig.targetMismatches"),
                n.get("controlRig.unresolvedTargets"),
            ),
            "Complete Control Rig mapping or block the transfer.",
        ),
        _eval(
            asset_id,
            "mirror-pair-coverage",
            not n.get("mirror.missingPairs"),
            "warning",
            "Mirror pair coverage",
            "Left/right face controls need mirrored target coverage to avoid asymmetric transfer defects.",
            str(n.get("mirror.missingPairs")),
            "Restore missing mirror targets or mark the expression as intentionally asymmetric.",
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


def _topology_signature(vertex_count: int, edge_count: int, face_count: int) -> str:
    return "topo:head:v%d:e%d:f%d" % (vertex_count, edge_count, face_count)


def _out_of_range_params(actual_params: Dict[str, Any], value_range: List[float]) -> List[Dict[str, Any]]:
    low = float(value_range[0]) if value_range else 0.0
    high = float(value_range[1]) if len(value_range) > 1 else 1.0
    rows = []
    for name, value in actual_params.items():
        numeric = float(value)
        if numeric < low or numeric > high:
            rows.append({"name": name, "value": numeric, "range": [low, high]})
    return rows


def _missing_mirror_pairs(mirror_pairs: List[List[str]], actual_joints: List[str]) -> List[List[str]]:
    actual = set(actual_joints)
    return [pair for pair in mirror_pairs if len(pair) == 2 and (pair[0] not in actual or pair[1] not in actual)]


def _reviewer_claims() -> List[str]:
    return [
        "Character calibration validates topology, joint coverage, face controls and Control Rig mappings as business facts, not as a screenshot-only review.",
        "The fixture includes one approved character and one intentionally blocked temporary sculpt, so failure behavior is part of the evidence.",
        "Contract mode performs no scene writes; Maya L3 mode creates only public synthetic meshes, joints and custom attributes.",
    ]
