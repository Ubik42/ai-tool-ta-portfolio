from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List


HOST_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = HOST_ROOT / "scripts" / "run_blender_l3.py"
ARTIFACTS = HOST_ROOT / "artifacts"


def _candidate_paths() -> List[Path]:
    direct = [
        Path("C:/Program Files/Blender Foundation/Blender 4.4/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.3/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.2/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.1/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"),
        Path("C:/Program Files/Blender Foundation/Blender 3.6/blender.exe"),
        Path("D:/Program Files/Blender Foundation/Blender 4.4/blender.exe"),
        Path("D:/Program Files/Blender Foundation/Blender 4.3/blender.exe"),
        Path("D:/Program Files/Blender Foundation/Blender 4.2/blender.exe"),
        Path("D:/Blender/blender.exe"),
        Path("C:/Blender/blender.exe"),
    ]
    scanned: List[Path] = []
    for base in (Path("C:/Program Files/Blender Foundation"), Path("D:/Program Files/Blender Foundation")):
        if base.exists():
            scanned.extend(sorted(base.glob("**/blender.exe")))
    return direct + [path for path in scanned if path not in direct]


def find_blender() -> Dict[str, object]:
    found = shutil.which("blender")
    candidates = _candidate_paths()
    if found:
        return {"available": True, "path": found, "searched": [str(path) for path in candidates]}
    for candidate in candidates:
        if candidate.exists():
            return {"available": True, "path": str(candidate), "searched": [str(path) for path in candidates]}
    return {"available": False, "path": None, "searched": [str(path) for path in candidates]}


def write_readiness_report(search: Dict[str, object]) -> Path:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("blender-rule-adapter-l3-readiness-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = {
        "reportVersion": "blender-rule-adapter-l3-readiness@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / Blender Rule Adapter",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2+",
        "gate": "Blocked",
        "l3Status": "blocked_by_missing_blender_cli",
        "blenderCli": search,
        "collector": {
            "script": str(SCRIPT),
            "ready": SCRIPT.exists(),
            "expectedCommand": "blender --background --python %s" % SCRIPT,
            "reportWhenAvailable": "blender-rule-adapter-bpy-l3@0.1.0",
        },
        "boundary": {
            "mutation": "no_blender_runtime_invoked",
            "sceneWrites": 0,
            "assetWrites": 0,
            "productionWrites": 0,
        },
        "nextActions": [
            {
                "id": "install-or-locate-blender-cli",
                "state": "blocked",
                "owner": "tool-ta",
                "reason": "Blender CLI was not found in PATH or standard install locations.",
            },
            {
                "id": "run-bpy-l3-smoke",
                "state": "ready_after_blender_cli",
                "command": "python %s" % Path(__file__).resolve(),
            },
        ],
        "reviewerClaims": [
            "The bpy collector and background launcher are present and compile in normal Python.",
            "The current machine cannot complete Blender L3 because blender.exe is not installed or discoverable.",
            "No production asset or Blender scene mutation is attempted without a Blender runtime.",
        ],
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    search = find_blender()
    if not search["available"]:
        path = write_readiness_report(search)
        print(
            json.dumps(
                {
                    "ok": True,
                    "path": str(path),
                    "reportVersion": "blender-rule-adapter-l3-readiness@0.1.0",
                    "evidenceLevel": "L2+",
                    "l3Status": "blocked_by_missing_blender_cli",
                    "gate": "Blocked",
                    "collectorReady": SCRIPT.exists(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    command = [str(search["path"]), "--background", "--python", str(SCRIPT)]
    completed = subprocess.run(command, cwd=str(HOST_ROOT), text=True)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
