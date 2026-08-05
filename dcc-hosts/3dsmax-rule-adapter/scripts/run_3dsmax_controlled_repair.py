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

from max_rule_adapter.controlled_repair import build_controlled_repair_report  # noqa: E402


def main() -> int:
    report = build_controlled_repair_report(FIXTURE)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("max-controlled-repair-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["summary"]
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(path),
                "reportVersion": report["reportVersion"],
                "evidenceLevel": report["evidenceLevel"],
                "l3Status": report["l3Status"],
                "gate": summary["gate"],
                "preGate": summary["preGate"],
                "postGate": summary["postGate"],
                "rollbackPassed": summary["rollbackPassed"],
                "selectedOperations": summary["selectedOperations"],
                "executedOperations": summary["executedOperations"],
                "postReadyAssets": summary["postReadyAssets"],
                "postBlockedAssets": summary["postBlockedAssets"],
                "assetWrites": summary["assetWrites"],
                "productionWrites": summary["productionWrites"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
