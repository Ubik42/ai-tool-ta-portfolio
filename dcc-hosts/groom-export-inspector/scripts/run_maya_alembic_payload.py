from __future__ import annotations

import json
import os
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
        from groom_export_inspector.alembic_payload import build_alembic_payload_report

        fixture = HOST_ROOT / "fixtures" / "synthetic_groom_export_scene.json"
        artifact_dir = HOST_ROOT / "artifacts"
        export_mode = os.environ.get("AI_TOOL_TA_GROOM_ALEMBIC_EXPORT_MODE", "curve_only")
        cache_name = os.environ.get(
            "AI_TOOL_TA_GROOM_ALEMBIC_CACHE_NAME",
            "groom-alembic-r52-hair-schema" if export_mode.replace("-", "_").lower() == "curve_only" else "groom-alembic-r48",
        )
        cache_dir = artifact_dir / "cache" / cache_name
        artifact_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        output_path = artifact_dir / ("groom-alembic-payload-%s.json" % stamp)
        report = build_alembic_payload_report(fixture, cache_dir, export_mode=export_mode)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        summary = report["facts"]["summary"]
        evaluation = report["evaluation"]["summary"]
        print(
            json.dumps(
                {
                    "ok": True,
                    "path": str(output_path),
                    "reportVersion": report["reportVersion"],
                    "evidenceLevel": report["evidenceLevel"],
                    "l3Status": report["l3Status"],
                    "exportMode": report["facts"].get("exportMode"),
                    "gate": evaluation["gate"],
                    "selectedRows": summary["selectedRows"],
                    "heldRows": summary["heldRows"],
                    "exportSucceeded": summary["exportSucceeded"],
                    "cacheFiles": summary["cacheFiles"],
                    "cacheBytes": summary["cacheBytes"],
                    "schemaInspectedRows": summary.get("schemaInspectedRows"),
                    "schemaCompatibleRows": summary.get("schemaCompatibleRows"),
                    "meshShapeRows": summary.get("meshShapeRows"),
                    "curveShapeRows": summary.get("curveShapeRows"),
                    "pass": evaluation["pass"],
                    "warning": evaluation["warning"],
                    "error": evaluation["error"],
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
