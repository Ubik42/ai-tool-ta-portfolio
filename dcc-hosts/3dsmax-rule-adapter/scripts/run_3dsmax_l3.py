from __future__ import annotations

import json
import sys
import time
from pathlib import Path


HOST_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = HOST_ROOT / "fixtures" / "synthetic_3dsmax_scene.json"
ARTIFACTS = HOST_ROOT / "artifacts"

if str(HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(HOST_ROOT))

from max_rule_adapter import build_pymxs_report  # noqa: E402


def main() -> int:
    report = build_pymxs_report(FIXTURE)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("max-rule-adapter-l3-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
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
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
