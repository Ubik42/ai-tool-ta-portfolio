"""Read-only Unreal AnimSequence deep facts report."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .contract import public_path, resolve_public_path


REPORT_VERSION = "unreal-animation-deep-facts@0.1.0"


def build_deep_facts_report(source_path: str, runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    source_file = resolve_public_path(source_path)
    source = json.loads(Path(source_file).read_text(encoding="utf-8"))
    runtime_snapshot = dict(runtime_snapshot)
    runtime_snapshot["sourceEvaluations"] = _source_evaluations_by_asset(source)
    sequences = [_sequence(row, runtime_snapshot) for row in source.get("facts", {}).get("sequences", [])]
    rows: List[Dict[str, Any]] = []
    for sequence in sequences:
        rows.extend(_evaluate_sequence(sequence, runtime_snapshot))
    summary = _summary(sequences, rows, runtime_snapshot)
    runtime = runtime_snapshot.get("runtime", {})
    executed = bool(runtime.get("executed"))
    blocked_reason = runtime.get("blockedReason")
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Animation Bridge",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L3" if executed else "Blocked",
        "l3Status": blocked_reason or ("unreal_animsequence_deep_facts_collected" if executed else "blocked_by_missing_unreal_runtime"),
        "sourceImportL3": {
            "path": public_path(source_file),
            "reportVersion": source.get("reportVersion"),
            "evidenceLevel": source.get("evidenceLevel"),
            "l3Status": source.get("l3Status"),
            "gate": source.get("evaluation", {}).get("summary", {}).get("gate"),
        },
        "unrealRuntime": runtime,
        "facts": {
            "schema": "unreal-animation-deep-facts-input@0.1.0",
            "sequences": sequences,
        },
        "evaluation": {
            "schema": "unreal-animation-deep-facts-evaluation@0.1.0",
            "summary": summary,
            "rows": rows,
            "ownerActions": _owner_actions(rows),
        },
        "adapter": {
            "id": "unreal-animation-deep-facts",
            "name": "Unreal AnimSequence Deep Facts",
            "methodSource": "R25 imported public AnimSequence assets + Unreal Python read-only metadata probe",
            "protocolCarrier": "AnimSequence runtime metadata, derived frame span, skeleton binding, curve/root/compression API visibility",
            "boundary": {
                "mutation": "read_only_unreal_runtime_probe",
                "assetWrites": runtime.get("assetWrites", 0),
                "engineWrites": runtime.get("engineWrites", 0),
                "productionWrites": runtime.get("productionWrites", 0),
            },
        },
        "reviewerClaims": [
            "R41 deepens the R25 Unreal Animation Bridge from asset presence to AnimSequence runtime metadata.",
            "The collector is read-only: it opens existing public Unreal assets, derives frame spans from play length, and records curve/root/compression API visibility without import or save.",
            "Blocked rows remain tied to source animation business failures; missing Unreal metadata is separated into reviewer warnings instead of hiding behind a green import result.",
        ],
    }


def _sequence(source_row: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    expected_path = source_row.get("expectedAnimSequencePath")
    runtime_row = (runtime_snapshot.get("sequences", {}) or {}).get(expected_path, {})
    source_evaluations = runtime_snapshot.get("sourceEvaluations", {}).get(source_row.get("assetId"), [])
    return {
        "assetId": source_row.get("assetId"),
        "mayaTakeName": source_row.get("mayaTakeName"),
        "ownerState": source_row.get("ownerState"),
        "expectedAnimSequencePath": expected_path,
        "expectedSkeletonPath": source_row.get("expectedSkeletonPath"),
        "expectedUnreal": source_row.get("expectedUnreal", {}),
        "sourceMaya": source_row.get("sourceMaya", {}),
        "sourceBridgeFailures": source_evaluations,
        "runtimeUnreal": runtime_row,
    }


def _source_evaluations_by_asset(source: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    rows: Dict[str, List[Dict[str, Any]]] = {}
    for row in source.get("evaluation", {}).get("evaluations", []):
        asset_id = row.get("assetId")
        if not asset_id:
            continue
        rows.setdefault(asset_id, []).append(row)
    return rows


def _evaluate_sequence(sequence: Dict[str, Any], runtime_snapshot: Dict[str, Any]) -> List[Dict[str, Any]]:
    runtime = sequence.get("runtimeUnreal", {})
    expected = sequence.get("expectedUnreal", {})
    deep = runtime.get("deepFacts", {})
    source_failures = [row for row in sequence.get("sourceBridgeFailures", []) if row.get("status") == "error"]
    expected_rate = float(expected.get("sampleRate") or 0.0)
    expected_span = _expected_frame_span(expected)
    derived_span = deep.get("derivedFrameSpanAtExpectedRate")
    frame_delta = None if derived_span is None or expected_span is None else abs(int(derived_span) - int(expected_span))
    curve = deep.get("curveMetadata", {})
    root = deep.get("rootMotion", {})
    compression = deep.get("compression", {})
    return [
        _row(
            sequence,
            "source-bridge-ready",
            not source_failures,
            "error",
            "sourceErrors=%s" % [row.get("ruleId") for row in source_failures],
            "Fix the Maya animation source row before accepting engine metadata.",
        ),
        _row(
            sequence,
            "runtime-animsequence-present",
            bool(runtime.get("animSequenceExists") and deep.get("class") == "AnimSequence"),
            "error",
            "exists=%s class=%s path=%s"
            % (runtime.get("animSequenceExists"), deep.get("class"), sequence.get("expectedAnimSequencePath")),
            "Import or relink the public AnimSequence fixture before deep metadata review.",
        ),
        _row(
            sequence,
            "runtime-skeleton-binding",
            bool(deep.get("skeletonPath")) and deep.get("skeletonPath") == sequence.get("expectedSkeletonPath"),
            "error",
            "runtime=%s expected=%s" % (deep.get("skeletonPath"), sequence.get("expectedSkeletonPath")),
            "Bind the AnimSequence to the expected public Skeleton.",
        ),
        _row(
            sequence,
            "runtime-duration-frame-span",
            frame_delta is not None and frame_delta <= 1,
            "error",
            "playLength=%s expectedRate=%s derivedSpan=%s expectedSpan=%s delta=%s"
            % (deep.get("playLength"), expected_rate, derived_span, expected_span, frame_delta),
            "Reimport or trim the animation so Unreal duration matches the expected take frame span.",
        ),
        _row(
            sequence,
            "runtime-direct-frame-rate",
            bool(deep.get("directFrameRateReadable")),
            "warning",
            "samplingFrameRate=%s readable=%s derivedRate=%s"
            % (deep.get("samplingFrameRate"), deep.get("directFrameRateReadable"), deep.get("derivedFrameRateSource")),
            "Expose direct sampling frame-rate metadata or keep using derived frame-span checks.",
        ),
        _row(
            sequence,
            "runtime-curve-metadata",
            bool(curve.get("curveNamesReadable")),
            "warning",
            "required=%s names=%s api=%s"
            % (expected.get("requiredCurveNames", []), curve.get("curveNames"), curve.get("apiAvailable")),
            "Expose animation curve names through Unreal Python or keep curve ownership in the Maya L3 source report.",
        ),
        _row(
            sequence,
            "runtime-root-motion-settings",
            bool(root.get("propertiesReadable")),
            "warning",
            "expectedMode=%s properties=%s"
            % (expected.get("rootMotionMode"), root.get("properties")),
            "Expose root motion settings through Unreal Python before claiming runtime root-motion policy parity.",
        ),
        _row(
            sequence,
            "runtime-compression-settings",
            bool(compression.get("propertiesReadable")),
            "warning",
            "expected=%s properties=%s"
            % (expected.get("compression", {}), compression.get("properties")),
            "Expose compression settings or attach an engine-owner review receipt.",
        ),
        _row(
            sequence,
            "read-only-boundary",
            runtime_snapshot.get("runtime", {}).get("assetWrites", 0) == 0
            and runtime_snapshot.get("runtime", {}).get("engineWrites", 0) == 0
            and runtime_snapshot.get("runtime", {}).get("productionWrites", 0) == 0,
            "error",
            "assetWrites=%s engineWrites=%s productionWrites=%s"
            % (
                runtime_snapshot.get("runtime", {}).get("assetWrites", 0),
                runtime_snapshot.get("runtime", {}).get("engineWrites", 0),
                runtime_snapshot.get("runtime", {}).get("productionWrites", 0),
            ),
            "Keep deep fact collection read-only.",
        ),
    ]


def _row(
    sequence: Dict[str, Any],
    rule_id: str,
    passed: bool,
    fail_status: str,
    evidence: str,
    fix_preview: str,
) -> Dict[str, Any]:
    return {
        "id": "%s:%s" % (sequence.get("assetId"), rule_id),
        "assetId": sequence.get("assetId"),
        "ruleId": rule_id,
        "status": "pass" if passed else fail_status,
        "evidence": evidence,
        "fixPreview": "None" if passed else fix_preview,
    }


def _summary(
    sequences: Iterable[Dict[str, Any]],
    rows: Iterable[Dict[str, Any]],
    runtime_snapshot: Dict[str, Any],
) -> Dict[str, Any]:
    row_list = list(rows)
    sequence_list = list(sequences)
    blocked_assets = sorted({row["assetId"] for row in row_list if row["status"] == "error"})
    review_assets = sorted({row["assetId"] for row in row_list if row["status"] == "warning"} - set(blocked_assets))
    ready_assets = sorted({row.get("assetId") for row in sequence_list} - set(blocked_assets) - set(review_assets))
    runtime_rows = [row.get("runtimeUnreal", {}).get("deepFacts", {}) for row in sequence_list]
    return {
        "gate": "Blocked" if blocked_assets else "Review" if review_assets else "Ready",
        "assetCount": len(sequence_list),
        "readyAssets": len(ready_assets),
        "reviewAssets": len(review_assets),
        "blockedAssets": len(blocked_assets),
        "pass": sum(1 for row in row_list if row["status"] == "pass"),
        "warning": sum(1 for row in row_list if row["status"] == "warning"),
        "error": sum(1 for row in row_list if row["status"] == "error"),
        "readyAssetIds": ready_assets,
        "reviewAssetIds": review_assets,
        "blockedAssetIds": blocked_assets,
        "runtimeRowsCollected": sum(1 for row in runtime_rows if row),
        "durationRowsMatched": sum(
            1 for row in row_list if row["ruleId"] == "runtime-duration-frame-span" and row["status"] == "pass"
        ),
        "directFrameRateReadable": sum(1 for row in runtime_rows if row.get("directFrameRateReadable")),
        "curveMetadataReadable": sum(1 for row in runtime_rows if row.get("curveMetadata", {}).get("curveNamesReadable")),
        "rootMotionReadable": sum(1 for row in runtime_rows if row.get("rootMotion", {}).get("propertiesReadable")),
        "compressionReadable": sum(1 for row in runtime_rows if row.get("compression", {}).get("propertiesReadable")),
        "assetWrites": runtime_snapshot.get("runtime", {}).get("assetWrites", 0),
        "engineWrites": runtime_snapshot.get("runtime", {}).get("engineWrites", 0),
        "productionWrites": runtime_snapshot.get("runtime", {}).get("productionWrites", 0),
    }


def _owner_actions(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    actions = []
    for row in rows:
        if row.get("status") == "pass":
            continue
        actions.append(
            {
                "id": "anim-deep-action:%s" % row.get("id"),
                "assetId": row.get("assetId"),
                "ruleId": row.get("ruleId"),
                "owner": "animation-ta" if row.get("status") == "error" else "engine-ta",
                "preview": row.get("fixPreview"),
            }
        )
    return actions


def _expected_frame_span(expected: Dict[str, Any]) -> Optional[int]:
    start = expected.get("startFrame")
    end = expected.get("endFrame")
    if start is None or end is None:
        return None
    return int(round(float(end) - float(start)))
