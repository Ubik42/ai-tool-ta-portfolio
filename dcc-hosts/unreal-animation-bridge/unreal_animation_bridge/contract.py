"""Unreal animation bridge contract.

The bridge compares Maya animation-continuity facts to Unreal AnimSequence
expectations. Runtime probes can attach Unreal Python facts when available.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPORT_VERSION = "unreal-animation-bridge-contract@0.1.0"
READINESS_REPORT_VERSION = "unreal-animation-bridge-readiness@0.1.0"
FIXTURE_SCHEMA = "synthetic-unreal-animation-bridge@0.1.0"
PORTFOLIO_ROOT = Path(__file__).resolve().parents[3]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def resolve_public_path(path: str | Path) -> Path:
    if isinstance(path, Path):
        return path
    text = str(path)
    if text.startswith("<repo>"):
        return PORTFOLIO_ROOT / text[len("<repo>") :].lstrip("\\/")
    return Path(text)


def load_fixture(path: str | Path) -> Dict[str, Any]:
    fixture_path = Path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Fixture root must be a JSON object.")
    if payload.get("schema") != FIXTURE_SCHEMA:
        raise ValueError("Unsupported fixture schema: %s" % payload.get("schema"))
    return payload


def load_maya_report(fixture: Dict[str, Any]) -> Dict[str, Any]:
    report_path = resolve_public_path(fixture.get("sourceMayaL3Artifact", ""))
    return json.loads(report_path.read_text(encoding="utf-8"))


def build_report(
    fixture_path: str | Path,
    runtime_snapshot: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    fixture = load_fixture(fixture_path)
    maya_report = load_maya_report(fixture)
    facts = build_bridge_facts(fixture, maya_report, runtime_snapshot)
    evaluation = evaluate_bridge(facts)
    runtime_executed = bool(runtime_snapshot and runtime_snapshot.get("executed"))
    runtime_assets = facts.get("unrealRuntime", {}).get("assets", {})
    all_expected_assets_present = bool(runtime_assets.get("allExpectedAssetsPresent"))
    report_version = READINESS_REPORT_VERSION if runtime_executed else REPORT_VERSION
    evidence_level = "L3-readiness" if runtime_executed else "L2"
    l3_status = (
        "unreal_animation_assets_ready"
        if runtime_executed and all_expected_assets_present
        else "unreal_animation_api_probe_collected"
        if runtime_executed
        else "contract_fixture_collected"
    )
    return {
        "reportVersion": report_version,
        "generatedBy": "AI Tool TA Portfolio / Unreal Animation Bridge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": evidence_level,
        "l3Status": l3_status,
        "fixture": {
            "path": public_path(fixture_path),
            "schema": fixture.get("schema"),
            "intent": fixture.get("intent"),
        },
        "sourceMayaReport": {
            "path": fixture.get("sourceMayaL3Artifact"),
            "reportVersion": maya_report.get("reportVersion"),
            "evidenceLevel": maya_report.get("evidenceLevel"),
            "l3Status": maya_report.get("l3Status"),
            "runtimeCollected": maya_report.get("facts", {}).get("scene", {}).get("runtimeCollected"),
        },
        "adapter": {
            "id": "unreal-animation-bridge",
            "name": "Unreal Animation Bridge",
            "methodSource": "Lightbox animation export / Unreal AnimSequence import continuity",
            "protocolCarrier": "Maya animation-continuity L3 artifact + Unreal AnimSequence/Skeleton facts",
            "boundary": {
                "mutation": "unreal_runtime_probe_only" if runtime_executed else "contract_validation_only",
                "engineWrites": 0,
                "assetWrites": 0,
                "productionWrites": 0,
            },
        },
        "facts": facts,
        "evaluation": evaluation,
        "reviewerClaims": [
            "The bridge compares Maya keyed animCurve facts with Unreal AnimSequence expectations instead of trusting an FBX handoff label.",
            "Runtime readiness enters Unreal Python and records animation API / asset availability without creating or saving production assets.",
            "Blocked rows are explicit owner or fixture gaps: skeleton binding, sample rate, curve coverage, frame range, root motion and compression boundaries stay auditable.",
        ],
    }


def build_bridge_facts(
    fixture: Dict[str, Any],
    maya_report: Dict[str, Any],
    runtime_snapshot: Dict[str, Any] | None,
) -> Dict[str, Any]:
    maya_assets = {
        row.get("assetId"): row
        for row in maya_report.get("facts", {}).get("assets", [])
    }
    sequence_rows = [
        _sequence_fact(row, maya_assets.get(row.get("assetId")), runtime_snapshot)
        for row in fixture.get("animationSequences", [])
    ]
    return {
        "schema": "unreal-animation-bridge-input@0.1.0",
        "unrealProject": fixture.get("unrealProject", {}),
        "sourceMaya": {
            "reportVersion": maya_report.get("reportVersion"),
            "evidenceLevel": maya_report.get("evidenceLevel"),
            "l3Status": maya_report.get("l3Status"),
            "runtimeCollected": maya_report.get("facts", {}).get("scene", {}).get("runtimeCollected"),
            "assetCount": maya_report.get("facts", {}).get("scene", {}).get("assetCount"),
        },
        "sequences": sequence_rows,
        "unrealRuntime": runtime_snapshot or {
            "executed": False,
            "runtime": "not_run",
        },
    }


def evaluate_bridge(facts: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    for sequence in facts.get("sequences", []):
        rows.extend(_evaluate_sequence(sequence, facts))
    summary = _summarize(rows)
    return {
        "schema": "unreal-animation-bridge-evaluation@0.1.0",
        "summary": summary,
        "evaluations": rows,
        "fixPreview": [
            {
                "id": "fix:%s" % row["id"],
                "assetId": row["assetId"],
                "ruleId": row["ruleId"],
                "status": row["status"],
                "mutationScope": "owner_required" if row["status"] == "error" else "manual_only",
                "preview": row["fixPreview"],
            }
            for row in rows
            if row["status"] != "pass"
        ],
    }


def _sequence_fact(
    fixture_row: Dict[str, Any],
    maya_asset: Dict[str, Any] | None,
    runtime_snapshot: Dict[str, Any] | None,
) -> Dict[str, Any]:
    normalized = (maya_asset or {}).get("normalized", {})
    raw = (maya_asset or {}).get("raw", {})
    runtime_assets = ((runtime_snapshot or {}).get("assets") or {}).get("rows", {})
    runtime_row = runtime_assets.get(fixture_row.get("expectedAnimSequencePath"), {})
    return {
        "assetId": fixture_row.get("assetId"),
        "mayaTakeName": fixture_row.get("mayaTakeName"),
        "expectedAnimSequencePath": fixture_row.get("expectedAnimSequencePath"),
        "expectedSkeletonPath": fixture_row.get("expectedSkeletonPath"),
        "ownerState": fixture_row.get("ownerState"),
        "sourceMayaFound": bool(maya_asset),
        "sourceMaya": {
            "rigId": normalized.get("character.rigId"),
            "expectedRigId": normalized.get("character.expectedRigId"),
            "skeletonFingerprint": normalized.get("character.skeletonFingerprint"),
            "expectedSkeletonFingerprint": normalized.get("character.expectedSkeletonFingerprint"),
            "takeName": normalized.get("take.name"),
            "startFrame": normalized.get("take.startFrame"),
            "endFrame": normalized.get("take.endFrame"),
            "actualFirstKey": normalized.get("take.actualFirstKey"),
            "actualLastKey": normalized.get("take.actualLastKey"),
            "sampleRate": normalized.get("take.sampleRate"),
            "missingChannels": normalized.get("channels.missing", []),
            "duplicateChannels": normalized.get("channels.duplicates", []),
            "subFrameCount": normalized.get("keys.subFrameCount"),
            "outsideRangeCount": normalized.get("keys.outsideRangeCount"),
            "rootMotionPolicy": normalized.get("rootMotion.policy"),
            "rootMotionDelta": normalized.get("rootMotion.delta"),
            "scaleMaxDrift": normalized.get("scale.maxDrift"),
            "additiveWithoutOwner": normalized.get("animationLayers.additiveWithoutOwner"),
            "channelIdentities": raw.get("channelIdentities", []),
        },
        "expectedUnreal": {
            "skeletonFingerprint": fixture_row.get("expectedSkeletonFingerprint"),
            "sampleRate": fixture_row.get("expectedSampleRate"),
            "startFrame": fixture_row.get("expectedStartFrame"),
            "endFrame": fixture_row.get("expectedEndFrame"),
            "rootMotionMode": fixture_row.get("rootMotionMode"),
            "requiredCurveNames": fixture_row.get("requiredCurveNames", []),
            "compression": fixture_row.get("compression", {}),
        },
        "runtimeUnreal": runtime_row,
    }


def _evaluate_sequence(sequence: Dict[str, Any], facts: Dict[str, Any]) -> List[Dict[str, Any]]:
    source = sequence.get("sourceMaya", {})
    expected = sequence.get("expectedUnreal", {})
    runtime = sequence.get("runtimeUnreal", {})
    runtime_executed = bool(facts.get("unrealRuntime", {}).get("executed"))
    required_curves = set(expected.get("requiredCurveNames", []))
    maya_curves = set(source.get("channelIdentities", []))
    missing_unreal_curves = sorted(required_curves - maya_curves)
    root_delta = float(source.get("rootMotionDelta") or 0.0)
    root_mode = expected.get("rootMotionMode")
    root_ok = root_delta > 0.001 if root_mode == "enabled" else root_delta <= 0.001
    return [
        _eval(
            sequence,
            "maya-source-l3",
            bool(sequence.get("sourceMayaFound")) and facts.get("sourceMaya", {}).get("evidenceLevel") == "L3",
            "error",
            "Maya source L3",
            "Unreal animation bridge must start from real Maya keyed animCurve evidence.",
            "sourceFound=%s evidence=%s" % (sequence.get("sourceMayaFound"), facts.get("sourceMaya", {}).get("evidenceLevel")),
            "Run Animation Continuity Maya L3 before engine comparison.",
        ),
        _eval(
            sequence,
            "skeleton-binding",
            source.get("skeletonFingerprint") == expected.get("skeletonFingerprint"),
            "error",
            "Skeleton binding",
            "Unreal AnimSequence must bind to the same approved skeleton fingerprint as the Maya take.",
            "maya=%s expected=%s" % (source.get("skeletonFingerprint"), expected.get("skeletonFingerprint")),
            "Retarget or re-export from the approved skeleton before import.",
        ),
        _eval(
            sequence,
            "sample-rate",
            float(source.get("sampleRate") or 0.0) == float(expected.get("sampleRate") or 0.0),
            "error",
            "Sample rate",
            "Unreal import should not silently resample the take.",
            "maya=%s expected=%s" % (source.get("sampleRate"), expected.get("sampleRate")),
            "Resample or bake the Maya take to the target engine sample rate.",
        ),
        _eval(
            sequence,
            "frame-range",
            float(source.get("actualFirstKey") or 0.0) >= float(expected.get("startFrame") or 0.0)
            and float(source.get("actualLastKey") or 0.0) <= float(expected.get("endFrame") or 0.0),
            "warning",
            "Frame range",
            "Keys outside the declared take can leak poses into the imported AnimSequence.",
            "first=%s last=%s expected=%s-%s"
            % (source.get("actualFirstKey"), source.get("actualLastKey"), expected.get("startFrame"), expected.get("endFrame")),
            "Trim keys or split the take before import.",
        ),
        _eval(
            sequence,
            "curve-coverage",
            not missing_unreal_curves and not source.get("duplicateChannels"),
            "error",
            "Curve coverage",
            "Gameplay curves required by Unreal must be present and uniquely identified in Maya.",
            "missing=%s duplicates=%s" % (missing_unreal_curves, source.get("duplicateChannels")),
            "Restore missing channels and resolve namespace/source collisions.",
        ),
        _eval(
            sequence,
            "sub-frame-boundary",
            int(source.get("subFrameCount") or 0) == 0,
            "error",
            "Sub-frame boundary",
            "Unreal compression can quantize sub-frame keys differently unless they are explicitly approved.",
            "subFrameCount=%s" % source.get("subFrameCount"),
            "Bake sub-frame keys or attach an animation owner waiver.",
        ),
        _eval(
            sequence,
            "root-motion",
            root_ok,
            "error",
            "Root motion",
            "Root motion mode must match the root translate curve evidence before engine import.",
            "mode=%s delta=%.4f" % (root_mode, root_delta),
            "Bake root motion into the approved root or convert the clip to in-place.",
        ),
        _eval(
            sequence,
            "runtime-asset-readiness",
            (not runtime_executed) or bool(runtime.get("animSequenceExists") and runtime.get("skeletonExists")),
            "warning",
            "Runtime asset readiness",
            "Unreal runtime probe should see the expected AnimSequence and Skeleton before claiming full L3.",
            "executed=%s anim=%s skeleton=%s"
            % (runtime_executed, runtime.get("animSequenceExists"), runtime.get("skeletonExists")),
            "Create public skeletal animation fixture assets or keep this row as readiness.",
        ),
    ]


def _eval(
    sequence: Dict[str, Any],
    rule_id: str,
    passed: bool,
    fail_status: str,
    label: str,
    reason: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (sequence.get("assetId"), rule_id),
        "assetId": sequence.get("assetId"),
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
    blocked_assets = sorted({row["assetId"] for row in rows if row["status"] == "error"})
    review_assets = sorted({row["assetId"] for row in rows if row["status"] == "warning"} - set(blocked_assets))
    ready_assets = sorted(set(asset_ids) - set(blocked_assets) - set(review_assets))
    return {
        "gate": "Blocked" if blocked_assets else "Review" if review_assets else "Ready",
        "assetCount": len(asset_ids),
        "readyAssets": len(ready_assets),
        "reviewAssets": len(review_assets),
        "blockedAssets": len(blocked_assets),
        "pass": sum(1 for row in rows if row["status"] == "pass"),
        "warning": sum(1 for row in rows if row["status"] == "warning"),
        "error": sum(1 for row in rows if row["status"] == "error"),
        "readyAssetIds": ready_assets,
        "reviewAssetIds": review_assets,
        "blockedAssetIds": blocked_assets,
    }
