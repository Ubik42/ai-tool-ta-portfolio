"""Public face Skeleton fixture import and target-coverage report."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "unreal-control-rig-face-skeleton-fixture@0.1.0"
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


def build_face_skeleton_fixture_report(
    source_deformation_path: str | Path,
    fbx_manifest_path: str | Path | None,
    runtime_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    source_path = resolve_public_path(source_deformation_path)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    fbx_manifest = _load_optional_json(fbx_manifest_path)
    runtime_snapshot = runtime_snapshot or {
        "runtime": {
            "executed": False,
            "runtime": "not_run",
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
            "writeScope": "none",
        },
        "import": {"attempted": False, "success": False},
        "faceSkeleton": {},
    }
    facts = build_face_skeleton_facts(source, fbx_manifest, runtime_snapshot)
    evaluation = evaluate_face_skeleton_fixture(facts, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    blocked_reason = runtime.get("blockedReason")
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Control Rig Face Skeleton Fixture",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked" if blocked_reason else "L3" if executed else "L2",
        "l3Status": blocked_reason or ("unreal_control_rig_face_skeleton_fixture_imported" if executed else "contract_fixture_collected"),
        "sourceArtifact": {
            "path": public_path(source_path),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "fbxManifest": {
            "path": public_path(fbx_manifest_path) if fbx_manifest_path else None,
            "reportVersion": fbx_manifest.get("reportVersion") if fbx_manifest else None,
            "exported": fbx_manifest.get("fixture", {}).get("exported") if fbx_manifest else None,
        },
        "unrealRuntime": runtime,
        "facts": facts,
        "evaluation": evaluation,
        "adapter": {
            "id": "unreal-control-rig-face-skeleton-fixture",
            "name": "Unreal Control Rig Face Skeleton Fixture",
            "methodSource": "Maya synthetic face Skeleton FBX -> Unreal public SkeletalMesh/Skeleton import",
            "protocolCarrier": "R43 Control Rig deformation-link missing target facts + imported Unreal Skeleton bone facts",
            "boundary": {
                "mutation": "public_unreal_test_project_fixture_only",
                "engineWrites": runtime.get("engineWrites", 0),
                "assetWrites": runtime.get("assetWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
                "writeScope": runtime.get("writeScope", "/Game/AI_Tool_TA public fixture only"),
            },
        },
        "reviewerClaims": [
            "R44 creates a public face Skeleton fixture instead of waiving R43's missing deformation targets.",
            "The report proves whether Head, Jaw, Eye_L and Eye_R are readable from the imported Unreal Skeleton.",
            "The fixture is generated from public synthetic Maya data and writes only under /Game/AI_Tool_TA.",
            "The result is a relink target for the Control Rig bridge; direct compile-status proof remains a separate adapter task.",
        ],
    }


def build_face_skeleton_facts(
    source: Dict[str, Any],
    fbx_manifest: Dict[str, Any],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    required_targets = _required_targets_from_source(source)
    previous_missing = _previous_missing_targets(source)
    face_skeleton = runtime_snapshot.get("faceSkeleton", {})
    bone_names = list(face_skeleton.get("boneNames") or [])
    target_rows = [
        {
            "target": target,
            "presentInImportedSkeleton": target in set(bone_names),
            "wasMissingInR43": target in set(previous_missing),
        }
        for target in required_targets
    ]
    return {
        "schema": "unreal-control-rig-face-skeleton-fixture@0.1.0",
        "sourceDeformationSummary": source.get("facts", {}).get("summary", {}),
        "requiredTargets": required_targets,
        "previousMissingTargets": previous_missing,
        "runtimeCollected": bool(runtime_snapshot.get("runtime", {}).get("executed")),
        "import": runtime_snapshot.get("import", {}),
        "faceSkeleton": face_skeleton,
        "targetRows": target_rows,
        "summary": summarize_facts(target_rows, runtime_snapshot),
    }


def evaluate_face_skeleton_fixture(facts: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    evaluations = [
        _eval(
            "face-skeleton-fixture",
            "source-deformation-link-present",
            bool(facts.get("sourceDeformationSummary")),
            "error",
            "Source Deformation Link",
            "Face Skeleton fixture should answer a concrete R43 deformation-link gap.",
            str(facts.get("sourceDeformationSummary")),
            "Run R43 deformation-link first and feed its artifact into this fixture importer.",
        ),
        _eval(
            "face-skeleton-fixture",
            "maya-fbx-generated",
            bool(facts.get("import", {}).get("sourceFbx")),
            "error",
            "Maya FBX Generated",
            "The public face Skeleton should come from a generated synthetic Maya FBX.",
            str(facts.get("import", {}).get("sourceFbx")),
            "Regenerate the face Skeleton FBX with mayapy.",
        ),
        _eval(
            "face-skeleton-fixture",
            "unreal-import-success",
            bool(facts.get("import", {}).get("success")),
            "error",
            "Unreal Import Success",
            "The generated FBX must import into the public Unreal project.",
            str(facts.get("import", {}).get("failures", [])),
            "Inspect the Unreal import task options and rerun the fixture importer.",
        ),
        _eval(
            "face-skeleton-fixture",
            "face-skeleton-readable",
            bool(facts.get("faceSkeleton", {}).get("exists")) and bool(facts.get("faceSkeleton", {}).get("boneNamesReadable")),
            "error",
            "Face Skeleton Readable",
            "The imported Skeleton must expose bone names through Unreal Python.",
            "exists=%s readable=%s"
            % (facts.get("faceSkeleton", {}).get("exists"), facts.get("faceSkeleton", {}).get("boneNamesReadable")),
            "Fix the import target or Skeleton bone-name collector.",
        ),
        _eval(
            "face-skeleton-fixture",
            "target-coverage",
            facts.get("summary", {}).get("targetMatches") == facts.get("summary", {}).get("requiredTargetCount")
            and facts.get("summary", {}).get("requiredTargetCount", 0) > 0,
            "error",
            "Required Face Target Coverage",
            "Control Rig deformation targets should all exist in the imported public face Skeleton.",
            str(facts.get("targetRows")),
            "Regenerate the public face Skeleton with the missing deformation targets.",
        ),
        _eval(
            "face-skeleton-fixture",
            "r43-missing-target-resolution",
            facts.get("summary", {}).get("previousMissingResolved") == facts.get("summary", {}).get("previousMissingCount"),
            "error",
            "R43 Missing Target Resolution",
            "Every R43 missing approved-row deformation target should be present in the public face Skeleton fixture.",
            "resolved=%s missing=%s"
            % (facts.get("summary", {}).get("previousMissingResolved"), facts.get("summary", {}).get("previousMissingCount")),
            "Add the unresolved R43 targets to the fixture before bridge relink.",
        ),
        _eval(
            "face-skeleton-fixture",
            "public-fixture-write-boundary",
            runtime_snapshot.get("runtime", {}).get("productionWrites", 0) == 0
            and str(runtime_snapshot.get("runtime", {}).get("writeScope", "")).startswith("/Game/AI_Tool_TA"),
            "error",
            "Public Fixture Write Boundary",
            "This importer may write public synthetic fixtures but must not touch production assets.",
            "assetWrites=%s engineWrites=%s productionWrites=%s scope=%s"
            % (
                runtime_snapshot.get("runtime", {}).get("assetWrites", 0),
                runtime_snapshot.get("runtime", {}).get("engineWrites", 0),
                runtime_snapshot.get("runtime", {}).get("productionWrites", 0),
                runtime_snapshot.get("runtime", {}).get("writeScope"),
            ),
            "Stop the run and inspect the write set before exposing the artifact.",
        ),
        _eval(
            "face-skeleton-fixture",
            "bridge-recheck-required",
            False,
            "warning",
            "Bridge Recheck Required",
            "The fixture is useful only after the Control Rig bridge and deformation-link collector are rerun against SK_HeroFace.",
            str(facts.get("faceSkeleton", {}).get("skeletonPath")),
            "Rerun run_l3_smoke.py and run_deformation_link.py after switching approved targets to the face Skeleton fixture.",
        ),
    ]
    return {
        "schema": "unreal-control-rig-face-skeleton-fixture-evaluation@0.1.0",
        "summary": _summarize(evaluations),
        "evaluations": evaluations,
        "ownerActions": _owner_actions(evaluations),
    }


def summarize_facts(target_rows: Iterable[Dict[str, Any]], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    rows = list(target_rows)
    previous_missing = [row for row in rows if row.get("wasMissingInR43")]
    return {
        "requiredTargetCount": len(rows),
        "targetMatches": sum(1 for row in rows if row.get("presentInImportedSkeleton")),
        "previousMissingCount": len(previous_missing),
        "previousMissingResolved": sum(1 for row in previous_missing if row.get("presentInImportedSkeleton")),
        "assetWrites": runtime_snapshot.get("runtime", {}).get("assetWrites", 0),
        "engineWrites": runtime_snapshot.get("runtime", {}).get("engineWrites", 0),
        "productionWrites": runtime_snapshot.get("runtime", {}).get("productionWrites", 0),
    }


def _required_targets_from_source(source: Dict[str, Any]) -> List[str]:
    targets = set()
    for row in source.get("facts", {}).get("characters", []):
        if row.get("assetId") != "char-hero-head-001":
            continue
        for control in row.get("controlLinks", []):
            target = control.get("deformationTarget")
            if target:
                targets.add(str(target))
    return sorted(targets)


def _previous_missing_targets(source: Dict[str, Any]) -> List[str]:
    targets = set()
    for row in source.get("facts", {}).get("characters", []):
        if row.get("assetId") != "char-hero-head-001":
            continue
        for control in row.get("controlLinks", []):
            if control.get("targetInUnrealSkeleton") is False and control.get("deformationTarget"):
                targets.add(str(control.get("deformationTarget")))
    return sorted(targets)


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
    blocked = [row for row in rows if row["status"] == "error"]
    review = [row for row in rows if row["status"] == "warning"]
    return {
        "gate": "Blocked" if blocked else "Review" if review else "Ready",
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": len(review),
        "error": len(blocked),
        "ownerActionCount": len(blocked) + len(review),
    }


def _owner_actions(evaluations: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
                "owner": "engine-ta" if "unreal" in row["ruleId"] or "bridge" in row["ruleId"] else "character-owner",
                "preview": row["fixPreview"],
                "writeBoundary": "public_fixture_only",
            }
        )
    return actions


def _load_optional_json(path: str | Path | None) -> Dict[str, Any]:
    if not path:
        return {}
    resolved = resolve_public_path(path)
    if not resolved.exists():
        return {}
    return json.loads(resolved.read_text(encoding="utf-8"))
