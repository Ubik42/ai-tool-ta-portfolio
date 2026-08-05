from __future__ import annotations

import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from unreal_animation_bridge.contract import build_report  # noqa: E402


def main() -> int:
    fixture = ROOT / "fixtures" / "synthetic_unreal_animation_bridge.json"
    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    output_path = artifact_dir / ("unreal-animation-bridge-contract-%s.json" % stamp)
    report = build_report(fixture)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["evaluation"]["summary"]
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(output_path),
                "reportVersion": report["reportVersion"],
                "evidenceLevel": report["evidenceLevel"],
                "l3Status": report["l3Status"],
                "gate": summary["gate"],
                "assetCount": summary["assetCount"],
                "readyAssets": summary["readyAssets"],
                "reviewAssets": summary["reviewAssets"],
                "blockedAssets": summary["blockedAssets"],
                "pass": summary["pass"],
                "warning": summary["warning"],
                "error": summary["error"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
