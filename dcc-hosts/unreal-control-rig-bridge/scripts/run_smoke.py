from __future__ import annotations

import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ARTIFACT = ROOT.parents[0] / "character-calibration-studio" / "artifacts" / "character-calibration-drilldown-20260805-202259.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from unreal_control_rig_bridge.contract import build_report  # noqa: E402


def main() -> int:
    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    output_path = artifact_dir / ("unreal-control-rig-bridge-contract-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = build_report(SOURCE_ARTIFACT)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(output_path),
                "reportVersion": report.get("reportVersion"),
                "evidenceLevel": report.get("evidenceLevel"),
                "l3Status": report.get("l3Status"),
                "summary": report.get("evaluation", {}).get("summary"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
