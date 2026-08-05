from __future__ import annotations

import json
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "synthetic_houdini_scene.json"
ARTIFACTS = ROOT / "artifacts"


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from houdini_rule_adapter.contract import build_report

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("houdini-rule-adapter-contract-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = build_report(FIXTURE)
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
                "assets": summary["assets"],
                "ready": summary["ready"],
                "review": summary["review"],
                "blocked": summary["blocked"],
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
