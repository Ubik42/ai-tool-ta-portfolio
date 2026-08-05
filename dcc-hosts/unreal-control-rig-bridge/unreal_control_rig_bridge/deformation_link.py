"""Read-only Control Rig deformation target and compile-readiness facts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "unreal-control-rig-deformation-link@0.1.0"
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


def build_deformation_link_report(
    source_bridge_path: str | Path,
    fixture_authoring_path: str | Path,
    runtime_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    bridge_path = resolve_public_path(source_bridge_path)
    fixture_path = resolve_public_path(fixture_authoring_path)
    bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    runtime_snapshot = runtime_snapshot or {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "characters": [],
    }
    facts = build_link_facts(bridge, fixture, runtime_snapshot)
    evaluation = evaluate_deformation_link(facts, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    blocked_reason = runtime.get("blockedReason")
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Control Rig Deformation Link",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked" if blocked_reason else "L3" if executed else "L2",
        "l3Status": blocked_reason or ("unreal_control_rig_deformation_link_collected" if executed else "contract_fixture_collected"),
        "sourceArtifact": {
            "path": public_path(bridge_path),
            "reportVersion": bridge.get("reportVersion"),
            "evidenceLevel": bridge.get("evidenceLevel"),
            "l3Status": bridge.get("l3Status"),
            "gate": bridge.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "fixtureAuthoringArtifact": {
            "path": public_path(fixture_path),
            "reportVersion": fixture.get("reportVersion"),
            "evidenceLevel": fixture.get("evidenceLevel"),
            "l3Status": fixture.get("l3Status"),
            "gate": fixture.get("fixtureAuthoring", {}).get("summary", {}).get("gate"),
        },
        "sourceBridgeSummary": bridge.get("evaluation", {}).get("summary", {}),
        "fixtureAuthoringSummary": fixture.get("fixtureAuthoring", {}).get("summary", {}),
        "unrealRuntime": runtime,
        "facts": facts,
        "evaluation": evaluation,
        "adapter": {
            "id": "unreal-control-rig-deformation-link",
            "name": "Unreal Control Rig Deformation Link",
            "methodSource": "Post-authoring Control Rig fixture audit against Maya character deformation intent",
            "protocolCarrier": "Character Calibration raw mapping + Unreal ControlRigBlueprint hierarchy / Skeleton facts",
            "boundary": {
                "mutation": "public_unreal_test_project_read_only",
                "engineWrites": runtime.get("engineWrites", 0),
                "assetWrites": runtime.get("assetWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "read-only /Game/AI_Tool_TA fact collection"),
            },
        },
        "reviewerClaims": [
            "R43 audits the generated public CR_HeroFace fixture as an engine-side character binding artifact, not just as an asset-presence check.",
            "The report links Maya required controls to deformation target names, Unreal runtime controls, hierarchy shape/offset readability and Skeleton target coverage.",
            "Compile readiness is reported from the UE Python API surface only; missing direct compile status remains a review gate instead of being treated as success.",
            "The collector is read-only and records zero asset writes, engine writes and production writes.",
        ],
    }


def build_link_facts(
    bridge: Dict[str, Any],
    fixture: Dict[str, Any],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    characters = runtime_snapshot.get("characters", [])
    return {
        "schema": "unreal-control-rig-deformation-link@0.1.0",
        "sourceBridgeCharacters": bridge.get("facts", {}).get("sourceRows"),
        "sourceBridgeReadyRows": bridge.get("evaluation", {}).get("summary", {}).get("readyRows"),
        "fixtureOperationRows": fixture.get("fixtureAuthoring", {}).get("summary", {}).get("operationRows"),
        "fixtureRequiredControls": fixture.get("fixtureAuthoring", {}).get("summary", {}).get("requiredControlCount"),
        "runtimeCollected": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "characters": characters,
        "summary": summarize_facts(characters, runtime_snapshot),
    }


def evaluate_deformation_link(facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("characters", []):
        evaluations.extend(_evaluate_character(row, runtime_snapshot))
    return {
        "schema": "unreal-control-rig-deformation-link-evaluation@0.1.0",
        "summary": summarize_evaluations(evaluations),
        "evaluations": evaluations,
        "ownerActions": owner_actions(evaluations),
    }


def summarize_facts(characters: Iterable[Dict[str, Any]], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    rows = list(characters)
    control_rows = [control for row in rows for control in row.get("controlLinks", [])]
    compile_rows = [row.get("compileProbe", {}) for row in rows]
    return {
        "characterRows": len(rows),
        "controlsEvaluated": len(control_rows),
        "runtimeControlsPresent": sum(1 for control in control_rows if control.get("runtimeControlExists")),
        "mappedTargetNames": sum(1 for control in control_rows if control.get("deformationTarget")),
        "skeletonTargetMatches": sum(1 for control in control_rows if control.get("targetInUnrealSkeleton") is True),
        "skeletonTargetUnknown": sum(1 for control in control_rows if control.get("targetInUnrealSkeleton") == "unknown"),
        "shapeOrOffsetReadableControls": sum(1 for control in control_rows if control.get("shapeReadable") or control.get("offsetReadable")),
        "compileApiVisibleRows": sum(1 for row in compile_rows if row.get("compileApiVisible")),
        "directCompileStatusRows": sum(1 for row in compile_rows if row.get("directCompileStatusReadable")),
        "assetWrites": runtime_snapshot.get("runtime", {}).get("assetWrites", 0),
        "engineWrites": runtime_snapshot.get("runtime", {}).get("engineWrites", 0),
        "productionWrites": runtime_snapshot.get("runtime", {}).get("productionWrites", 0),
    }


def summarize_evaluations(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
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


def owner_actions(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for row in evaluations:
        if row["status"] == "pass":
            continue
        actions.append(
            {
                "id": "owner-action:%s" % row["id"],
                "assetId": row["assetId"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "mutationScope": "owner_required" if row["status"] == "error" else "manual_review",
                "owner": owner_for_rule(row["ruleId"]),
                "preview": row["fixPreview"],
                "writeBoundary": "read_only_probe",
            }
        )
    return actions


def owner_for_rule(rule_id: str) -> str:
    if rule_id in ("unreal-python-runtime", "control-rig-asset-readable", "control-rig-compile-api"):
        return "engine-ta"
    if rule_id in ("runtime-control-coverage", "control-shape-offset-readability", "compile-status-direct-readability"):
        return "control-rig-owner"
    if rule_id in ("source-bridge-ready", "deformation-target-source-clean", "deformation-target-skeleton-link"):
        return "character-owner"
    if rule_id == "read-only-boundary":
        return "pipeline-ta"
    return "reviewer"


def _evaluate_character(row: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = str(row.get("assetId"))
    control_links = row.get("controlLinks", [])
    missing_runtime_controls = [control.get("control") for control in control_links if not control.get("runtimeControlExists")]
    missing_targets = [control.get("control") for control in control_links if not control.get("deformationTarget")]
    missing_skeleton_targets = [
        "%s->%s" % (control.get("control"), control.get("deformationTarget"))
        for control in control_links
        if control.get("targetInUnrealSkeleton") is False
    ]
    unknown_skeleton_targets = [
        "%s->%s" % (control.get("control"), control.get("deformationTarget"))
        for control in control_links
        if control.get("targetInUnrealSkeleton") == "unknown"
    ]
    unreadable_shape_controls = [
        control.get("control")
        for control in control_links
        if control.get("runtimeControlExists") and not (control.get("shapeReadable") or control.get("offsetReadable"))
    ]
    compile_probe = row.get("compileProbe", {})
    runtime = runtime_snapshot.get("runtime", {})
    return [
        _eval(
            asset_id,
            "source-bridge-ready",
            row.get("sourceStatus") == "Ready",
            "error",
            "Source Bridge Ready",
            "Only approved Character Calibration bridge rows should be treated as deformation-link candidates.",
            str(row.get("sourceStatus")),
            "Resolve Character Calibration drilldown and bridge owner actions before engine binding review.",
        ),
        _eval(
            asset_id,
            "unreal-python-runtime",
            bool(runtime.get("executed")),
            "error",
            "Unreal Python Runtime",
            "The deformation link report must be collected inside Unreal Python.",
            str(runtime.get("executed")),
            "Run the R43 harness with UnrealEditor-Cmd against the public test project.",
        ),
        _eval(
            asset_id,
            "control-rig-asset-readable",
            bool(row.get("controlRigExists")) and bool(row.get("hierarchyReadable")),
            "error",
            "Control Rig Asset Readable",
            "CR_HeroFace must exist and expose hierarchy facts before deformation links can be trusted.",
            "exists=%s hierarchy=%s class=%s" % (row.get("controlRigExists"), row.get("hierarchyReadable"), row.get("controlRigClass")),
            "Create or repair the public Control Rig fixture, then rerun the read-only deformation probe.",
        ),
        _eval(
            asset_id,
            "runtime-control-coverage",
            not missing_runtime_controls,
            "error",
            "Runtime Control Coverage",
            "Every Maya required control should exist in the Unreal Control Rig runtime hierarchy.",
            str(missing_runtime_controls),
            "Add missing controls or hold the binding with an explicit owner waiver.",
        ),
        _eval(
            asset_id,
            "deformation-target-source-clean",
            not row.get("sourceMissingJoints") and not row.get("sourceTemporaryJoints") and not missing_targets,
            "error",
            "Source Deformation Targets",
            "Maya control mappings should resolve to approved deformation targets before engine handoff.",
            "missingJoints=%s temporaryJoints=%s missingTargets=%s"
            % (row.get("sourceMissingJoints"), row.get("sourceTemporaryJoints"), missing_targets),
            "Restore approved joints and complete Maya control target mapping before Control Rig handoff.",
        ),
        _eval(
            asset_id,
            "deformation-target-skeleton-link",
            not missing_skeleton_targets,
            "error",
            "Skeleton Target Link",
            "Control Rig targets should be visible in the Unreal Skeleton when the Skeleton API exposes bone names.",
            "missing=%s unknown=%s skeletonReadable=%s"
            % (missing_skeleton_targets, unknown_skeleton_targets, row.get("skeletonBoneNamesReadable")),
            "Relink the public Skeleton or expose a stronger Skeleton bone-name collector before approval.",
        ),
        _eval(
            asset_id,
            "control-shape-offset-readability",
            not unreadable_shape_controls,
            "warning",
            "Control Shape / Offset Readability",
            "Reviewer should be able to inspect control shape or offset facts for each runtime control.",
            str(unreadable_shape_controls),
            "Use a C++/Editor Utility adapter if UE Python cannot expose the required hierarchy transform facts.",
        ),
        _eval(
            asset_id,
            "control-rig-compile-api",
            bool(compile_probe.get("compileApiVisible")),
            "error",
            "Compile API Surface",
            "The Control Rig asset should expose VM / compile API methods before compile-readiness can be discussed.",
            str(compile_probe.get("compileMethods", [])),
            "Enable ControlRig/RigVM support in the public project.",
        ),
        _eval(
            asset_id,
            "compile-status-direct-readability",
            bool(compile_probe.get("directCompileStatusReadable")),
            "warning",
            "Direct Compile Status",
            "UE Python must expose a stable direct compile status before this report can claim compile success.",
            str(compile_probe.get("directCompileStatus")),
            "Treat this as API-limited readiness, or add an Editor Utility/C++ bridge for direct compile status.",
        ),
        _eval(
            asset_id,
            "read-only-boundary",
            runtime.get("assetWrites", 0) == 0 and runtime.get("engineWrites", 0) == 0 and runtime.get("productionWrites", 0) == 0,
            "error",
            "Read-only Boundary",
            "The deformation link collector should not save public or production assets.",
            "assetWrites=%s engineWrites=%s productionWrites=%s"
            % (runtime.get("assetWrites"), runtime.get("engineWrites"), runtime.get("productionWrites")),
            "Stop the run and inspect the write set before exposing the artifact.",
        ),
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
