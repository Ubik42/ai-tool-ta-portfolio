from __future__ import annotations

import json
import sys
import time
from pathlib import Path


HOST_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = HOST_ROOT / "fixtures" / "synthetic_animation_scene.json"
ARTIFACTS = HOST_ROOT / "artifacts"

if str(HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(HOST_ROOT))

from animation_continuity_lab import build_report  # noqa: E402


def main() -> int:
    report = build_report(FIXTURE)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("animation-continuity-contract-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["evaluation"]["summary"]
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(path),
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
