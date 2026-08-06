from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
SOCKET_ARTIFACT_DIR = PORTFOLIO_ROOT / "dcc-hosts" / "unreal-socket-import-checker" / "artifacts"
REPORT_VERSION = "unreal-gameplay-attach-timing-controlled-readiness@0.1.0"


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_animation_bridge.gameplay_timing_controlled import build_gameplay_attach_timing_controlled_report

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-gameplay-attach-timing-controlled-readiness-%s.json" % stamp)
    gameplay_path = _latest_report(
        SOCKET_ARTIFACT_DIR,
        "unreal-gameplay-attach-controlled-readiness-*.json",
        "unreal-gameplay-attach-controlled-readiness@0.1.0",
    )
    attach_timing_path = _latest_report(
        ARTIFACT_DIR,
        "unreal-animation-attach-timing-readiness-*.json",
        "unreal-animation-attach-timing-readiness@0.1.0",
    )
    notify_controlled_path = _latest_report(
        ARTIFACT_DIR,
        "unreal-animation-notify-native-controlled-write-*.json",
        "unreal-animation-notify-native-controlled-write@0.1.0",
        require_summary_gate="Ready",
    )

    if not gameplay_path or not attach_timing_path or not notify_controlled_path:
        report = _blocked_report(output_path, gameplay_path, attach_timing_path, notify_controlled_path)
    else:
        report = build_gameplay_attach_timing_controlled_report(gameplay_path, attach_timing_path, notify_controlled_path)

    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report.get("evaluation", {}).get("summary", {})
    result = {
        "ok": summary.get("gate") in ("Review", "Ready"),
        "path": str(output_path),
        "reportVersion": report.get("reportVersion"),
        "evidenceLevel": report.get("evidenceLevel"),
        "l3Status": report.get("l3Status"),
        "gate": summary.get("gate"),
        "fullFixtureGate": summary.get("fullFixtureGate"),
        "notifyControlledWriteReady": summary.get("notifyControlledWriteReady"),
        "timingReadyByControlledWrite": summary.get("timingReadyByControlledWrite"),
        "heldBySocketOrSource": summary.get("heldBySocketOrSource"),
        "timingBlocked": summary.get("timingBlocked"),
        "missingAttachTimingEventsAfterControlledWrite": summary.get("missingAttachTimingEventsAfterControlledWrite"),
        "productionWrites": summary.get("productionWrites"),
        "finalHashRestored": summary.get("finalHashRestored"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _latest_report(root: Path, pattern: str, report_version: str, require_summary_gate: Optional[str] = None) -> Optional[Path]:
    matches = []
    for path in sorted(root.glob(pattern), key=lambda item: item.stat().st_mtime):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if report.get("reportVersion") != report_version:
            continue
        if require_summary_gate and report.get("summary", {}).get("gate") != require_summary_gate:
            continue
        matches.append(path)
    return matches[-1] if matches else None


def _blocked_report(
    output_path: Path,
    gameplay_path: Optional[Path],
    attach_timing_path: Optional[Path],
    notify_controlled_path: Optional[Path],
) -> dict:
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Gameplay Attach Timing Controlled Readiness",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked",
        "l3Status": "blocked_by_missing_source_artifact",
        "output": str(output_path),
        "sourceGameplayReadiness": {"path": str(gameplay_path) if gameplay_path else None},
        "sourceAttachTimingReadiness": {"path": str(attach_timing_path) if attach_timing_path else None},
        "sourceNotifyControlledWrite": {"path": str(notify_controlled_path) if notify_controlled_path else None},
        "facts": {
            "schema": "unreal-gameplay-attach-timing-controlled-readiness-input@0.1.0",
            "intents": [],
            "notifyControlledWrite": {},
        },
        "evaluation": {
            "schema": "unreal-gameplay-attach-timing-controlled-readiness-evaluation@0.1.0",
            "summary": {
                "gate": "Blocked",
                "fullFixtureGate": "Blocked",
                "notifyControlledWriteReady": False,
                "intentCount": 0,
                "timingReadyByControlledWrite": 0,
                "heldBySocketOrSource": 0,
                "timingBlocked": 0,
                "missingAttachTimingEventsAfterControlledWrite": 0,
                "productionWrites": 0,
                "finalHashRestored": False,
            },
            "rows": [],
            "ownerActions": [],
        },
        "reviewerClaims": [
            "The gameplay attach timing controlled readiness artifact could not be built because required source evidence was missing."
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
