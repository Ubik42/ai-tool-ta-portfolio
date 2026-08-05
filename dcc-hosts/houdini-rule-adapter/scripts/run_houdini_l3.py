from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "synthetic_houdini_scene.json"
ARTIFACTS = ROOT / "artifacts"


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from houdini_rule_adapter.hou_collector import build_hou_report

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    output = os.environ.get("AI_TOOL_TA_HOUDINI_L3_OUTPUT")
    path = Path(output) if output else ARTIFACTS / ("houdini-rule-adapter-hython-l3-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = build_hou_report(FIXTURE)
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
                "runtimeNodeCount": report["facts"]["scene"].get("runtimeNodeCount"),
                "houdiniVersion": report["facts"]["scene"].get("houdiniVersion"),
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
