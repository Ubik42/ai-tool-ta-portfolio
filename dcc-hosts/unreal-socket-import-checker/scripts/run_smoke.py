from __future__ import annotations

import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
SOURCE_ARTIFACT = (
    PORTFOLIO_ROOT
    / "dcc-hosts"
    / "spatial-authoring-workbench"
    / "artifacts"
    / "spatial-authoring-drilldown-20260805-203713.json"
)


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from unreal_socket_import_checker.contract import build_report

    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("unreal-socket-import-checker-contract-%s.json" % stamp)
    report = build_report(SOURCE_ARTIFACT)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report.get("evaluation", {}).get("summary", {})
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(output_path),
                "reportVersion": report.get("reportVersion"),
                "evidenceLevel": report.get("evidenceLevel"),
                "l3Status": report.get("l3Status"),
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
