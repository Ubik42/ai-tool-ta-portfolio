from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
GENERATION_ARTIFACT = ROOT / "artifacts" / "platform-variant-generation-plan-20260805-190052.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from platform_variant_forge.executor_expansion import build_executor_expansion_report  # noqa: E402


def main() -> int:
    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    controlled_executor = _latest_controlled_executor_artifact()
    if not controlled_executor:
        print(json.dumps({"ok": False, "reason": "missing_controlled_executor_artifact"}, ensure_ascii=False, indent=2))
        return 1
    output_path = artifact_dir / ("platform-variant-executor-expansion-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = build_executor_expansion_report(GENERATION_ARTIFACT, controlled_executor)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    result = {
        "ok": True,
        "path": str(output_path),
        "reportVersion": report.get("reportVersion"),
        "evidenceLevel": report.get("evidenceLevel"),
        "l3Status": report.get("l3Status"),
        "summary": report.get("summary"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _latest_controlled_executor_artifact() -> Optional[Path]:
    candidates = sorted(ROOT.glob("artifacts/platform-variant-controlled-executor-*.json"))
    return candidates[-1] if candidates else None


if __name__ == "__main__":
    raise SystemExit(main())
