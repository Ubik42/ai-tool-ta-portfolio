from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List


HOST_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = HOST_ROOT / "scripts" / "run_maya_alembic_payload.py"
ARTIFACTS = HOST_ROOT / "artifacts"
PORTFOLIO_ROOT = HOST_ROOT.parents[1]


def public_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def _candidate_paths() -> List[Path]:
    direct = [
        Path("C:/Program Files/Autodesk/Maya2026/bin/mayapy.exe"),
        Path("C:/Program Files/Autodesk/Maya2025/bin/mayapy.exe"),
        Path("C:/Program Files/Autodesk/Maya2024/bin/mayapy.exe"),
        Path("C:/Program Files/Autodesk/Maya2023/bin/mayapy.exe"),
        Path("D:/Program Files/Autodesk/Maya2026/bin/mayapy.exe"),
        Path("D:/Program Files/Autodesk/Maya2025/bin/mayapy.exe"),
        Path("D:/Program Files/Autodesk/Maya2024/bin/mayapy.exe"),
    ]
    scanned: List[Path] = []
    for base in (Path("C:/Program Files/Autodesk"), Path("D:/Program Files/Autodesk")):
        if base.exists():
            scanned.extend(sorted(base.glob("**/mayapy.exe")))
    return direct + [path for path in scanned if path not in direct]


def find_mayapy() -> Dict[str, object]:
    found = shutil.which("mayapy")
    candidates = _candidate_paths()
    if found:
        return {"available": True, "path": found, "searched": [str(path) for path in candidates]}
    for candidate in candidates:
        if candidate.exists():
            return {"available": True, "path": str(candidate), "searched": [str(path) for path in candidates]}
    return {"available": False, "path": None, "searched": [str(path) for path in candidates]}


def write_readiness_report(search: Dict[str, object]) -> Path:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("groom-alembic-payload-readiness-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = {
        "reportVersion": "groom-alembic-payload-readiness@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / Groom Export Inspector",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2+",
        "gate": "Blocked",
        "l3Status": "blocked_by_missing_mayapy",
        "requestedExportMode": os.environ.get("AI_TOOL_TA_GROOM_ALEMBIC_EXPORT_MODE", "curve_only"),
        "mayaRuntime": search,
        "collector": {
            "script": public_path(SCRIPT),
            "ready": SCRIPT.exists(),
            "expectedCommand": "mayapy %s" % public_path(SCRIPT),
            "reportWhenAvailable": "groom-alembic-payload@0.2.0",
        },
        "boundary": {
            "mutation": "no_maya_runtime_invoked",
            "sceneWrites": 0,
            "assetWrites": 0,
            "engineWrites": 0,
            "productionWrites": 0,
        },
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    search = find_mayapy()
    if not search["available"]:
        path = write_readiness_report(search)
        print(
            json.dumps(
                {
                    "ok": True,
                    "path": str(path),
                    "reportVersion": "groom-alembic-payload-readiness@0.1.0",
                    "evidenceLevel": "L2+",
                    "l3Status": "blocked_by_missing_mayapy",
                    "gate": "Blocked",
                    "collectorReady": SCRIPT.exists(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    completed = subprocess.run([str(search["path"]), str(SCRIPT)], cwd=str(HOST_ROOT), text=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
