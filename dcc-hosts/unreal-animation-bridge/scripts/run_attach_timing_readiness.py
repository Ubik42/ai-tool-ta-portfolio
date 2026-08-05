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
REPORT_VERSION = "unreal-animation-attach-timing-readiness@0.1.0"


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_animation_bridge.attach_timing import build_attach_timing_report

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-animation-attach-timing-readiness-%s.json" % stamp)
    gameplay_path = _latest_report(
        SOCKET_ARTIFACT_DIR,
        "unreal-gameplay-attach-controlled-readiness-*.json",
        "unreal-gameplay-attach-controlled-readiness@0.1.0",
    )
    deep_path = _latest_report(
        ARTIFACT_DIR,
        "unreal-animation-deep-facts-*.json",
        "unreal-animation-deep-facts@0.1.0",
    )
    if not gameplay_path or not deep_path:
        report = _blocked_report(gameplay_path, deep_path)
    else:
        report = build_attach_timing_report(gameplay_path, deep_path)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report.get("evaluation", {}).get("summary", {})
    result = {
        "ok": bool(output_path.exists()),
        "path": str(output_path),
        "reportVersion": report.get("reportVersion"),
        "evidenceLevel": report.get("evidenceLevel"),
        "l3Status": report.get("l3Status"),
        "gate": summary.get("gate"),
        "intentCount": summary.get("intentCount"),
        "timingReady": summary.get("timingReady"),
        "timingBlocked": summary.get("timingBlocked"),
        "heldBySocketOrSource": summary.get("heldBySocketOrSource"),
        "notifyReadableIntents": summary.get("notifyReadableIntents"),
        "missingAttachTimingEvents": summary.get("missingAttachTimingEvents"),
        "productionWrites": summary.get("productionWrites"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _latest_report(root: Path, pattern: str, report_version: str) -> Optional[Path]:
    matches = []
    for path in sorted(root.glob(pattern), key=lambda item: item.stat().st_mtime):
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if report.get("reportVersion") == report_version:
            matches.append(path)
    return matches[-1] if matches else None


def _blocked_report(gameplay_path: Optional[Path], deep_path: Optional[Path]) -> dict:
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Animation Attach Timing Readiness",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked",
        "l3Status": "blocked_by_missing_source_artifact",
        "sourceGameplayReadiness": {"path": str(gameplay_path) if gameplay_path else None},
        "sourceAnimSequenceDeepFacts": {"path": str(deep_path) if deep_path else None},
        "facts": {
            "schema": "unreal-animation-attach-timing-readiness-input@0.1.0",
            "runtimeDeepFactsCollected": False,
            "intents": [],
            "runtimeBoundary": {"assetWrites": 0, "engineWrites": 0, "productionWrites": 0},
        },
        "evaluation": {
            "schema": "unreal-animation-attach-timing-readiness-evaluation@0.1.0",
            "summary": {
                "gate": "Blocked",
                "intentCount": 0,
                "timingReady": 0,
                "timingBlocked": 0,
                "heldBySocketOrSource": 0,
                "notifyReadableIntents": 0,
                "missingAttachTimingEvents": 0,
                "assetWrites": 0,
                "engineWrites": 0,
                "productionWrites": 0,
            },
            "rows": [],
            "ownerActions": [],
        },
        "reviewerClaims": ["Attach timing readiness could not be built because source artifacts were missing."],
    }


if __name__ == "__main__":
    raise SystemExit(main())
