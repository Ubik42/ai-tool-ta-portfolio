"""Control Rig compile invocation and diagnostic-readiness facts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "unreal-control-rig-compile-status@0.1.0"
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


def build_compile_status_report(
    source_deformation_path: str | Path,
    runtime_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    source_path = resolve_public_path(source_deformation_path)
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
        "characters": [],
    }
    facts = build_compile_facts(source, runtime_snapshot)
    evaluation = evaluate_compile_status(facts, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    blocked_reason = runtime.get("blockedReason")
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Control Rig Compile Status Bridge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked" if blocked_reason else "L3" if executed else "L2",
        "l3Status": blocked_reason or ("unreal_control_rig_compile_status_collected" if executed else "contract_fixture_collected"),
        "sourceArtifact": {
            "path": public_path(source_path),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "sourceDeformationSummary": source.get("facts", {}).get("summary", {}),
        "sourceEvaluationSummary": source.get("evaluation", {}).get("summary", {}),
        "unrealRuntime": runtime,
        "facts": facts,
        "evaluation": evaluation,
        "adapter": {
            "id": "unreal-control-rig-compile-status",
            "name": "Unreal Control Rig Compile Status Bridge",
            "methodSource": "Post-face-skeleton Control Rig transient compile invocation and diagnostic probe",
            "protocolCarrier": "R44 deformation-link rows + Unreal ControlRigBlueprint compile / diagnostic API surface",
            "boundary": {
                "mutation": "public_unreal_test_project_transient_compile_probe",
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "transient compile probe; no save"),
            },
        },
        "reviewerClaims": [
            "R45 moves beyond Control Rig asset and hierarchy presence by invoking the Unreal ControlRigBlueprint compile API on the public fixture.",
            "The report separates compile method visibility, compile invocation success, direct diagnostic/status readability and package dirty-state boundary.",
            "The probe does not save assets and records zero production writes; any dirty package state is surfaced as review evidence.",
        ],
    }


def build_compile_facts(source: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    source_rows = {str(row.get("assetId")): row for row in source.get("facts", {}).get("characters", [])}
    runtime_rows = runtime_snapshot.get("characters", [])
    characters = []
    for row in runtime_rows:
        source_row = source_rows.get(str(row.get("assetId")), {})
        merged = dict(row)
        merged["sourceStatus"] = source_row.get("sourceStatus")
        merged["sourceControlRigPath"] = source_row.get("controlRigPath")
        merged["sourceControlRigExists"] = source_row.get("controlRigExists")
        merged["sourceHierarchyReadable"] = source_row.get("hierarchyReadable")
        merged["sourceCompileApiVisible"] = source_row.get("compileProbe", {}).get("compileApiVisible")
        merged["sourceDirectCompileStatusReadable"] = source_row.get("compileProbe", {}).get("directCompileStatusReadable")
        characters.append(merged)
    return {
        "schema": "unreal-control-rig-compile-status@0.1.0",
        "sourceCharacters": len(source_rows),
        "runtimeCollected": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "characters": characters,
        "summary": summarize_facts(characters, runtime_snapshot),
    }


def summarize_facts(characters: Iterable[Dict[str, Any]], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    rows = list(characters)
    return {
        "characterRows": len(rows),
        "compileCandidateRows": sum(1 for row in rows if row.get("controlRigExists")),
        "compileMethodVisibleRows": sum(1 for row in rows if row.get("compileMethodVisible")),
        "compileInvocationAttemptedRows": sum(1 for row in rows if row.get("compileInvocationAttempted")),
        "compileInvocationSucceededRows": sum(1 for row in rows if row.get("compileInvocationSucceeded")),
        "directStatusReadableRows": sum(1 for row in rows if row.get("directStatusReadable")),
        "diagnosticReadableRows": sum(1 for row in rows if row.get("diagnosticReadable")),
        "compileSettingsReadableRows": sum(1 for row in rows if row.get("compileSettingsReadable")),
        "dirtyBeforeRows": sum(1 for row in rows if row.get("packageDirtyBefore") is True),
        "dirtyAfterRows": sum(1 for row in rows if row.get("packageDirtyAfter") is True),
        "assetWrites": runtime_snapshot.get("runtime", {}).get("assetWrites", 0),
        "engineWrites": runtime_snapshot.get("runtime", {}).get("engineWrites", 0),
        "productionWrites": runtime_snapshot.get("runtime", {}).get("productionWrites", 0),
    }


def evaluate_compile_status(facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    evaluations: List[Dict[str, Any]] = []
    for row in facts.get("characters", []):
        evaluations.extend(_evaluate_character(row, runtime_snapshot))
    return {
        "schema": "unreal-control-rig-compile-status-evaluation@0.1.0",
        "summary": summarize_evaluations(evaluations),
        "evaluations": evaluations,
        "ownerActions": owner_actions(evaluations),
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
                "writeBoundary": "transient_compile_probe",
            }
        )
    return actions


def owner_for_rule(rule_id: str) -> str:
    if rule_id in ("unreal-python-runtime", "control-rig-asset-readable", "compile-method-visible", "compile-invocation-succeeded"):
        return "engine-ta"
    if rule_id in ("direct-status-or-diagnostics-readable", "package-dirty-boundary"):
        return "control-rig-owner"
    if rule_id == "source-deformation-link-reviewable":
        return "character-owner"
    if rule_id == "no-save-boundary":
        return "pipeline-ta"
    return "reviewer"


def _evaluate_character(row: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    asset_id = str(row.get("assetId"))
    runtime = runtime_snapshot.get("runtime", {})
    dirty_after = row.get("packageDirtyAfter")
    dirty_before = row.get("packageDirtyBefore")
    direct_status_or_diag = bool(row.get("directStatusReadable") or row.get("diagnosticReadable"))
    return [
        _eval(
            asset_id,
            "source-deformation-link-reviewable",
            row.get("sourceStatus") == "Ready",
            "error",
            "Source Deformation Link Row",
            "Only approved post-face deformation-link rows should enter direct compile readiness.",
            str(row.get("sourceStatus")),
            "Resolve source Character Calibration / deformation-link owner actions before compile readiness.",
        ),
        _eval(
            asset_id,
            "unreal-python-runtime",
            bool(runtime.get("executed")),
            "error",
            "Unreal Python Runtime",
            "Compile readiness must be collected inside Unreal Python.",
            str(runtime.get("executed")),
            "Run the compile status bridge with UnrealEditor-Cmd against the public test project.",
        ),
        _eval(
            asset_id,
            "control-rig-asset-readable",
            bool(row.get("controlRigExists")),
            "error",
            "Control Rig Asset",
            "The expected public Control Rig asset must be loadable before compile readiness can be probed.",
            row.get("controlRigPath"),
            "Create or relink the public Control Rig fixture before compile readiness.",
        ),
        _eval(
            asset_id,
            "compile-method-visible",
            bool(row.get("compileMethodVisible")),
            "error",
            "Compile Method Surface",
            "Unreal should expose ControlRigBlueprint compile or recompile methods on the public fixture.",
            str(row.get("compileMethods", [])),
            "Enable ControlRig/RigVM editor APIs or use an Editor Utility/C++ adapter.",
        ),
        _eval(
            asset_id,
            "compile-invocation-succeeded",
            bool(row.get("compileInvocationSucceeded")),
            "error",
            "Compile Invocation",
            "At least one transient compile invocation should complete without exception on the public Control Rig fixture.",
            str(row.get("compileInvocationRows", [])),
            "Fix compile errors or expose a stronger compile adapter before claiming engine readiness.",
        ),
        _eval(
            asset_id,
            "direct-status-or-diagnostics-readable",
            direct_status_or_diag,
            "warning",
            "Direct Status / Diagnostics",
            "Reviewer should see a direct compile status or diagnostic readback, not only a successful method call.",
            "directStatusReadable=%s diagnosticReadable=%s rows=%s"
            % (row.get("directStatusReadable"), row.get("diagnosticReadable"), row.get("statusRows", [])[:8]),
            "Add an Editor Utility/C++ bridge if UE Python cannot expose compile diagnostics.",
        ),
        _eval(
            asset_id,
            "package-dirty-boundary",
            not (dirty_before is False and dirty_after is True),
            "warning",
            "Package Dirty Boundary",
            "A compile probe should not silently leave the public fixture newly dirty without surfacing the state.",
            "before=%s after=%s" % (dirty_before, dirty_after),
            "Reload or rollback the public fixture before reviewer capture if compile marks the package dirty.",
        ),
        _eval(
            asset_id,
            "no-save-boundary",
            runtime.get("assetWrites", 0) == 0 and runtime.get("productionWrites", 0) == 0,
            "error",
            "No Save Boundary",
            "Compile readiness should be a transient probe in this public test project unless an explicit write receipt exists.",
            "assetWrites=%s productionWrites=%s" % (runtime.get("assetWrites"), runtime.get("productionWrites")),
            "Stop the run and add an explicit save / rollback receipt before exposing this as evidence.",
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
