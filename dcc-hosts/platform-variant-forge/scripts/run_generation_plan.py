from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from platform_variant_forge.generation_plan import build_generation_report  # noqa: E402


def _latest_runtime_artifact() -> Path:
    artifacts = sorted(
        (ROOT / "artifacts").glob("platform-variant-unreal-runtime-*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not artifacts:
        raise FileNotFoundError("No platform-variant-unreal-runtime artifact found.")
    return artifacts[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a dry-run platform variant generation plan.")
    parser.add_argument("--runtime-artifact", default=None, help="R29 runtime-vs-plan artifact path.")
    args = parser.parse_args()

    runtime_artifact = Path(args.runtime_artifact) if args.runtime_artifact else _latest_runtime_artifact()
    report = build_generation_report(runtime_artifact)
    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    output_path = artifact_dir / ("platform-variant-generation-plan-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
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


if __name__ == "__main__":
    raise SystemExit(main())
