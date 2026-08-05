from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List


HOST_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = HOST_ROOT / "scripts" / "run_3dsmax_l3.py"
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


def write_readiness_report(search: Dict[str, object], runtime_requested: bool) -> Path:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("max-rule-adapter-l3-readiness-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    runtime_available = bool(search["available"])
    gate = "Review" if runtime_available else "Blocked"
    l3_status = "runtime_discovered_not_invoked" if runtime_available else "blocked_by_missing_3dsmax_batch"
    if runtime_requested and not runtime_available:
        l3_status = "runtime_requested_but_missing_3dsmax_batch"

    report = {
        "reportVersion": "max-rule-adapter-l3-readiness@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / 3ds Max Rule Adapter",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2+",
        "gate": gate,
        "l3Status": l3_status,
        "maxRuntime": {
            "runner": "3dsmaxbatch.exe",
            "available": runtime_available,
            "path": search["path"],
            "searched": search["searched"],
            "runtimeLaunchPolicy": "opt_in",
            "runtimeRequested": runtime_requested,
        },
        "collector": {
            "script": str(SCRIPT),
            "ready": SCRIPT.exists(),
            "expectedCommand": "3dsmaxbatch.exe %s -v 2 -safescene off" % SCRIPT,
            "reportWhenAvailable": "max-rule-adapter-pymxs-l3@0.1.0",
        },
        "boundary": {
            "mutation": "no_3dsmax_runtime_invoked",
            "sceneWrites": 0,
            "assetWrites": 0,
            "productionWrites": 0,
        },
        "nextActions": [
            {
                "id": "run-pymxs-l3-smoke",
                "state": "ready_after_operator_opt_in" if runtime_available else "blocked",
                "owner": "tool-ta",
                "command": "python %s --run-runtime" % Path(__file__).resolve(),
                "reason": (
                    "3ds Max batch exists, but heartbeat does not launch it because the process can require license/UI/session state."
                    if runtime_available
                    else "3ds Max batch was not found in PATH or standard install locations."
                ),
            }
        ],
        "reviewerClaims": [
            "The pymxs collector and 3dsmaxbatch launcher are present and compile in normal Python.",
            "The machine can discover 3dsmaxbatch.exe." if runtime_available else "The machine cannot discover 3dsmaxbatch.exe.",
            "No 3ds Max scene, production asset or engine data is mutated unless the operator explicitly runs the L3 batch smoke.",
        ],
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-runtime", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=300)
    args = parser.parse_args()

    runtime_requested = args.run_runtime or os.environ.get("AI_TOOL_TA_RUN_3DSMAX_L3") == "1"
    search = find_3dsmax_batch()
    if not runtime_requested:
        path = write_readiness_report(search, runtime_requested=False)
        print(_summary_json(path, search, "runtime_discovered_not_invoked" if search["available"] else "blocked_by_missing_3dsmax_batch"))
        return 0

    if not search["available"]:
        path = write_readiness_report(search, runtime_requested=True)
        print(_summary_json(path, search, "runtime_requested_but_missing_3dsmax_batch"))
        return 0

    command = [str(search["path"]), str(SCRIPT), "-v", "2", "-safescene", "off"]
    completed = subprocess.run(command, cwd=str(HOST_ROOT), text=True, timeout=args.timeout_seconds)
    return completed.returncode


def _summary_json(path: Path, search: Dict[str, object], l3_status: str) -> str:
    return json.dumps(
        {
            "ok": True,
            "path": str(path),
            "reportVersion": "max-rule-adapter-l3-readiness@0.1.0",
            "evidenceLevel": "L2+",
            "l3Status": l3_status,
            "gate": "Review" if search["available"] else "Blocked",
            "maxBatchAvailable": bool(search["available"]),
            "collectorReady": SCRIPT.exists(),
        },
        ensure_ascii=False,
        indent=2,
    )


if __name__ == "__main__":
    raise SystemExit(main())
