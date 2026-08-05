from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "artifacts"
REPORT_VERSION = "unreal-gameplay-attach-controlled-readiness@0.1.0"


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_socket_import_checker.gameplay_attach_controlled import build_gameplay_attach_controlled_report

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = ARTIFACT_DIR / ("unreal-gameplay-attach-controlled-readiness-%s.json" % stamp)
    gameplay_path = _latest_report("unreal-gameplay-attach-fixture-*.json", "unreal-gameplay-attach-fixture@0.1.0")
    controlled_path = _latest_report(
        "unreal-socket-native-controlled-write-*.json",
        "unreal-socket-native-controlled-write@0.1.0",
        require_summary_gate="Ready",
    )
    if not gameplay_path or not controlled_path:
        report = _blocked_report(output_path, gameplay_path, controlled_path)
    else:
        report = build_gameplay_attach_controlled_report(gameplay_path, controlled_path)
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
        "readyByControlledExecutor": summary.get("readyByControlledExecutor"),
        "heldBySourceOwner": summary.get("heldBySourceOwner"),
        "blockedIntents": summary.get("blockedIntents"),
        "missingControlledSockets": summary.get("missingControlledSockets"),
        "publishRequiredIntents": summary.get("publishRequiredIntents"),
        "productionWrites": summary.get("productionWrites"),
        "finalHashRestored": summary.get("finalHashRestored"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


def _latest_report(pattern: str, report_version: str, require_summary_gate: Optional[str] = None) -> Optional[Path]:
    matches = []
    for path in sorted(ARTIFACT_DIR.glob(pattern), key=lambda item: item.stat().st_mtime):
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


def _blocked_report(output_path: Path, gameplay_path: Optional[Path], controlled_path: Optional[Path]) -> dict:
    return {
        "reportVersion": REPORT_VERSION,
        "generatedBy": "AI Tool TA Portfolio / Unreal Gameplay Attach Controlled Readiness",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "Blocked",
        "l3Status": "blocked_by_missing_source_artifact",
        "output": str(output_path),
        "sourceGameplayAttach": {"path": str(gameplay_path) if gameplay_path else None},
        "sourceControlledWrite": {"path": str(controlled_path) if controlled_path else None},
        "facts": {
            "schema": "unreal-gameplay-attach-controlled-readiness-input@0.1.0",
            "intents": [],
            "controlledWrite": {},
        },
        "evaluation": {
            "schema": "unreal-gameplay-attach-controlled-readiness-evaluation@0.1.0",
            "summary": {
                "gate": "Blocked",
                "fullFixtureGate": "Blocked",
                "controlledWriteReady": False,
                "intentCount": 0,
                "readyByControlledExecutor": 0,
                "heldBySourceOwner": 0,
                "blockedIntents": 0,
                "missingControlledSockets": 0,
                "publishRequiredIntents": 0,
                "productionWrites": 0,
                "finalHashRestored": False,
            },
            "rows": [],
            "ownerActions": [],
        },
        "reviewerClaims": [
            "The controlled gameplay attach readiness artifact could not be built because required source evidence was missing."
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
