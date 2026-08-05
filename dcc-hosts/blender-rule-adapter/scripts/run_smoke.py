from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path


HOST_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = HOST_ROOT / "blender_rule_adapter"
FIXTURE = HOST_ROOT / "fixtures" / "synthetic_blender_scene.json"
ARTIFACTS = HOST_ROOT / "artifacts"

if str(HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(HOST_ROOT))

from blender_rule_adapter import build_report  # noqa: E402


def _find_blender() -> str | None:
    found = shutil.which("blender")
    if found:
        return found

    candidates = [
        Path("C:/Program Files/Blender Foundation/Blender 4.4/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.3/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 3.6/blender.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def main() -> int:
    blender_path = _find_blender()
    report = build_report(
        fixture_path=FIXTURE,
        blender_cli_available=bool(blender_path),
        blender_cli_path=blender_path,
    )
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("blender-rule-adapter-contract-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
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
