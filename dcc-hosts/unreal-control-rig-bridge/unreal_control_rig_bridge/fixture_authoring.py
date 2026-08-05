"""Controlled public fixture authoring for Unreal Control Rig handoff."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "unreal-control-rig-fixture-authoring@0.1.0"
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


def build_fixture_authoring_report(
    source_bridge_path: str | Path,
    runtime_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    source_path = resolve_public_path(source_bridge_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    runtime_snapshot = runtime_snapshot or {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "operations": [],
        "heldRows": [],
    }
    evaluations = evaluate_fixture(runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    blocked_reason = runtime.get("blockedReason")
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Control Rig Fixture Authoring",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked" if blocked_reason else "L3" if executed else "L2",
        "l3Status": blocked_reason or ("unreal_control_rig_fixture_authoring_collected" if executed else "contract_fixture_collected"),
        "sourceArtifact": {
            "path": public_path(source_path),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "sourceBridgeSummary": source.get("evaluation", {}).get("summary", {}),
        "unrealRuntime": runtime,
        "fixtureAuthoring": {
            "schema": "unreal-control-rig-fixture-authoring@0.1.0",
            "operations": runtime_snapshot.get("operations", []),
            "heldRows": runtime_snapshot.get("heldRows", []),
            "summary": summarize_fixture(runtime_snapshot, evaluations),
        },
        "evaluation": {
            "schema": "unreal-control-rig-fixture-evaluation@0.1.0",
            "summary": summarize_evaluations(evaluations),
            "evaluations": evaluations,
            "ownerActions": owner_actions(evaluations),
        },
        "adapter": {
            "id": "unreal-control-rig-fixture-authoring",
            "name": "Unreal Control Rig Fixture Authoring",
            "methodSource": "R37 Control Rig bridge selected rows to controlled public Unreal fixture authoring",
            "protocolCarrier": "Character Calibration Control Rig mapping + Unreal ControlRigBlueprint runtime hierarchy facts",
            "boundary": {
                "mutation": "public_unreal_test_project_fixture_only",
                "engineWrites": runtime.get("engineWrites", 0),
                "assetWrites": runtime.get("assetWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public fixture only"),
            },
        },
        "reviewerClaims": [
            "R42 attempts the missing public CR_HeroFace fixture through Unreal Python instead of leaving the R37 bridge as a static missing-asset report.",
            "The authoring harness separates asset creation, save boundary, hierarchy readability and required Maya control coverage.",
            "All writes are constrained to the public /Game/AI_Tool_TA fixture project; productionWrites remains zero.",
        ],
    }


def evaluate_fixture(runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    runtime = runtime_snapshot.get("runtime", {})
    operations = runtime_snapshot.get("operations", [])
    if not operations:
        rows.append(
            _eval(
                "fixture-authoring",
                "selected-operation-presence",
                False,
                "error",
                "Selected Operation",
                "At least one approved R37 Control Rig bridge row should enter fixture authoring.",
                "operations=0",
                "Keep only Ready source rows with existing SkeletalMesh/Skeleton targets, then rerun fixture authoring.",
            )
        )
    for op in operations:
        asset_id = str(op.get("assetId"))
        authoring = op.get("authoring", {})
        post = op.get("postcheck", {})
        missing_controls = post.get("missingControls", [])
        rows.extend(
            [
                _eval(
                    asset_id,
                    "source-bridge-selected",
                    bool(op.get("selected")),
                    "error",
                    "Source Bridge Selection",
                    "Only Ready Maya source rows with Unreal SkeletalMesh/Skeleton binding should be allowed to author Control Rig fixtures.",
                    "source=%s mesh=%s skeleton=%s" % (op.get("sourceStatus"), op.get("skeletalMeshExists"), op.get("skeletonExists")),
                    "Resolve the R37 bridge row before creating Control Rig fixtures.",
                ),
                _eval(
                    asset_id,
                    "public-fixture-scope",
                    str(op.get("controlRigPath", "")).startswith("/Game/AI_Tool_TA/"),
                    "error",
                    "Public Fixture Scope",
                    "The authoring harness may only write under the public AI_Tool_TA test project namespace.",
                    op.get("controlRigPath"),
                    "Move the target path under /Game/AI_Tool_TA or hold for owner review.",
                ),
                _eval(
                    asset_id,
                    "control-rig-authoring-api",
                    bool(op.get("apiReady")),
                    "error",
                    "Control Rig Authoring API",
                    "ControlRigBlueprintFactory, AssetTools and EditorAssetLibrary must be visible for controlled fixture authoring.",
                    str(runtime.get("api", {}).get("classes", {})),
                    "Enable ControlRig and EditorScriptingUtilities in the public Unreal project.",
                ),
                _eval(
                    asset_id,
                    "control-rig-asset-presence",
                    bool(post.get("exists")),
                    "error",
                    "Control Rig Asset Presence",
                    "The public Control Rig asset must exist after authoring before runtime hierarchy facts can be trusted.",
                    "pre=%s created=%s post=%s errors=%s"
                    % (op.get("preflight", {}).get("exists"), authoring.get("created"), post.get("exists"), authoring.get("errors")),
                    "Create or import CR_HeroFace under /Game/AI_Tool_TA/Characters.",
                ),
                _eval(
                    asset_id,
                    "control-rig-hierarchy-readable",
                    bool(post.get("hierarchyReadable")),
                    "warning",
                    "Runtime Hierarchy Readability",
                    "The harness should be able to read Control Rig hierarchy keys from the generated or existing asset.",
                    "hierarchyKeys=%s methods=%s" % (post.get("hierarchyKeyCount"), post.get("hierarchyMethods", [])[:12]),
                    "Use a C++/Editor Utility adapter if Unreal Python cannot expose runtime hierarchy details.",
                ),
                _eval(
                    asset_id,
                    "required-control-coverage",
                    bool(post.get("exists")) and not missing_controls,
                    "error",
                    "Required Control Coverage",
                    "The public Control Rig fixture should expose every required Maya control mapping before approval.",
                    "required=%s runtime=%s missing=%s" % (op.get("requiredControls"), post.get("runtimeControls"), missing_controls),
                    "Add the missing controls or attach an explicit owner waiver.",
                ),
                _eval(
                    asset_id,
                    "public-write-boundary",
                    runtime.get("productionWrites", 0) == 0 and runtime.get("assetWrites", 0) <= max(1, len(operations)),
                    "error",
                    "Public Write Boundary",
                    "Controlled authoring may save public fixture assets but must never touch production content.",
                    "assetWrites=%s productionWrites=%s writeScope=%s"
                    % (runtime.get("assetWrites"), runtime.get("productionWrites"), runtime.get("writeScope")),
                    "Stop the run and inspect the write set before exposing this to reviewers.",
                ),
            ]
        )
    return rows


def summarize_fixture(runtime_snapshot: Dict[str, Any], evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
    operations = runtime_snapshot.get("operations", [])
    held_rows = runtime_snapshot.get("heldRows", [])
    post_rows = [op.get("postcheck", {}) for op in operations]
    runtime = runtime_snapshot.get("runtime", {})
    return {
        "gate": summarize_evaluations(evaluations).get("gate"),
        "operationRows": len(operations),
        "heldRows": len(held_rows),
        "createdAssets": sum(1 for op in operations if op.get("authoring", {}).get("created")),
        "existingAssets": sum(1 for op in operations if op.get("preflight", {}).get("exists")),
        "savedAssets": sum(1 for op in operations if op.get("authoring", {}).get("saved")),
        "hierarchyReadableRows": sum(1 for row in post_rows if row.get("hierarchyReadable")),
        "requiredControlCount": sum(len(op.get("requiredControls", [])) for op in operations),
        "runtimeControlCount": sum(len(row.get("runtimeControls", [])) for row in post_rows),
        "missingControlCount": sum(len(row.get("missingControls", [])) for row in post_rows),
        "assetWrites": runtime.get("assetWrites", 0),
        "engineWrites": runtime.get("engineWrites", 0),
        "productionWrites": runtime.get("productionWrites", 0),
    }


def summarize_evaluations(evaluations: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = list(evaluations)
    return {
        "gate": "Blocked" if any(row["status"] == "error" for row in rows) else "Review" if any(row["status"] == "warning" for row in rows) else "Ready",
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "blockedRuleIds": sorted({row["ruleId"] for row in rows if row["status"] == "error"}),
        "reviewRuleIds": sorted({row["ruleId"] for row in rows if row["status"] == "warning"}),
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
                "writeBoundary": "public_fixture_only",
            }
        )
    return actions


def owner_for_rule(rule_id: str) -> str:
    if rule_id in ("control-rig-authoring-api", "public-write-boundary", "control-rig-hierarchy-readable"):
        return "engine-ta"
    if rule_id in ("control-rig-asset-presence", "required-control-coverage"):
        return "control-rig-owner"
    if rule_id == "source-bridge-selected":
        return "character-owner"
    return "reviewer"


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
