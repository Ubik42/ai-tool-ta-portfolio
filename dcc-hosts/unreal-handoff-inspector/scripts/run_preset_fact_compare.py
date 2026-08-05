from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO_ROOT = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from unreal_handoff_inspector.contract import build_preset_fact_comparison_report  # noqa: E402


def _default_unreal_report() -> Path:
    manifest_path = PORTFOLIO_ROOT / "public-case-package" / "dcc-first-package-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        candidate = manifest.get("unrealHandoffInspectorArtifact")
        if candidate and Path(candidate).exists():
            return Path(candidate)
    artifacts = sorted(ROOT.glob("artifacts/unreal-handoff-inspector-l3-*.json"))
    if not artifacts:
        raise FileNotFoundError("No Unreal L3 artifact found.")
    return artifacts[-1]


def main() -> int:
    fixture_path = ROOT / "fixtures" / "synthetic_unreal_handoff.json"
    unreal_report_path = Path(os.environ.get("AI_TOOL_TA_UNREAL_L3_REPORT", "")) if os.environ.get("AI_TOOL_TA_UNREAL_L3_REPORT") else _default_unreal_report()
    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    output_path = artifact_dir / ("unreal-preset-fact-comparison-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = build_preset_fact_comparison_report(fixture_path, unreal_report_path)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(output_path),
                "reportVersion": report["reportVersion"],
                "gate": summary["gate"],
                "presetCount": summary["presetCount"],
                "assetCount": summary["assetCount"],
                "factRows": summary["factRows"],
                "matched": summary["matched"],
                "drift": summary["drift"],
                "waived": summary["waived"],
                "blocked": summary["blocked"],
                "platformSplit": summary["platformSplit"],
                "sourceEvidenceLevel": summary["sourceEvidenceLevel"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
