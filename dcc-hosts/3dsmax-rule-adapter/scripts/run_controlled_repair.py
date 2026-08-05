from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List


HOST_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = HOST_ROOT / "scripts" / "run_3dsmax_controlled_repair.py"
ARTIFACTS = HOST_ROOT / "artifacts"


def _candidate_paths() -> List[Path]:
    direct = [
        Path("C:/Program Files/Autodesk/3ds Max 2026/3dsmaxbatch.exe"),
        Path("C:/Program Files/Autodesk/3ds Max 2025/3dsmaxbatch.exe"),
        Path("C:/Program Files/Autodesk/3ds Max 2024/3dsmaxbatch.exe"),
        Path("C:/Program Files/Autodesk/3ds Max 2023/3dsmaxbatch.exe"),
        Path("C:/Program Files/Autodesk/3ds Max 2022/3dsmaxbatch.exe"),
        Path("D:/Program Files/Autodesk/3ds Max 2026/3dsmaxbatch.exe"),
        Path("D:/Program Files/Autodesk/3ds Max 2025/3dsmaxbatch.exe"),
        Path("D:/Program Files/Autodesk/3ds Max 2024/3dsmaxbatch.exe"),
        Path("D:/Program Files/Autodesk/3ds Max 2023/3dsmaxbatch.exe"),
        Path("D:/Program Files/Autodesk/3ds Max 2022/3dsmaxbatch.exe"),
    ]
    scanned: List[Path] = []
    for base in (Path("C:/Program Files/Autodesk"), Path("D:/Program Files/Autodesk")):
        if base.exists():
            scanned.extend(sorted(base.glob("**/3dsmaxbatch.exe")))
    return direct + [path for path in scanned if path not in direct]


def find_3dsmax_batch() -> Dict[str, object]:
    found = shutil.which("3dsmaxbatch")
    candidates = _candidate_paths()
    if found:
        return {"available": True, "path": found, "searched": [str(path) for path in candidates]}
    for candidate in candidates:
        if candidate.exists():
            return {"available": True, "path": str(candidate), "searched": [str(path) for path in candidates]}
    return {"available": False, "path": None, "searched": [str(path) for path in candidates]}


def write_readiness_report(search: Dict[str, object]) -> Path:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("max-controlled-repair-readiness-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = {
        "reportVersion": "max-controlled-repair-readiness@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / 3ds Max Rule Adapter",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2+",
        "gate": "Blocked",
        "l3Status": "blocked_by_missing_3dsmax_batch",
        "maxRuntime": {
            "runner": "3dsmaxbatch.exe",
            "available": False,
            "path": search["path"],
            "searched": search["searched"],
        },
        "executor": {
            "script": str(SCRIPT),
            "ready": SCRIPT.exists(),
            "expectedCommand": "3dsmaxbatch.exe %s -v 2 -safescene off" % SCRIPT,
            "reportWhenAvailable": "max-controlled-repair-executor@0.1.0",
        },
        "boundary": {
            "mutation": "no_3dsmax_runtime_invoked",
            "sceneWrites": 0,
            "assetWrites": 0,
            "productionWrites": 0,
        },
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    timeout_seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    search = find_3dsmax_batch()
    if not search["available"]:
        path = write_readiness_report(search)
        print(
            json.dumps(
                {
                    "ok": True,
                    "path": str(path),
                    "reportVersion": "max-controlled-repair-readiness@0.1.0",
                    "evidenceLevel": "L2+",
                    "l3Status": "blocked_by_missing_3dsmax_batch",
                    "gate": "Blocked",
                    "executorReady": SCRIPT.exists(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    command = [str(search["path"]), str(SCRIPT), "-v", "2", "-safescene", "off"]
    completed = subprocess.run(command, cwd=str(HOST_ROOT), text=True, timeout=timeout_seconds)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
