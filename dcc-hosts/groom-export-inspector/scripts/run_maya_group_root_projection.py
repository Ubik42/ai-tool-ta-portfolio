from __future__ import annotations

import json
import sys
import time
from pathlib import Path


HOST_ROOT = Path(__file__).resolve().parents[1]
if str(HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(HOST_ROOT))


def main() -> int:
    import maya.standalone  # type: ignore

    maya.standalone.initialize(name="python")
    try:
        from groom_export_inspector.group_root_projection import build_group_root_projection_report

        fixture = HOST_ROOT / "fixtures" / "synthetic_groom_group_projection_scene.json"
        artifact_dir = HOST_ROOT / "artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        output_path = artifact_dir / ("groom-group-root-projection-%s.json" % stamp)
        report = build_group_root_projection_report(fixture)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        summary = report["summary"]
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
                    "blockedAssets": summary["blockedAssets"],
                    "strandProjectionRows": summary["strandProjectionRows"],
                    "groupCoverageRows": summary["groupCoverageRows"],
                    "projectionMatchedStrands": summary["projectionMatchedStrands"],
                    "groupMatchedStrands": summary["groupMatchedStrands"],
                    "maxProjectionDrift": summary["maxProjectionDrift"],
                    "pass": summary["pass"],
                    "warning": summary["warning"],
                    "error": summary["error"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    finally:
        try:
            maya.standalone.uninitialize()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
