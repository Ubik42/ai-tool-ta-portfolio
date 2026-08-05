from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_houdini_l3.py"
ARTIFACTS = ROOT / "artifacts"


def candidate_paths() -> List[Path]:
    direct = [
        Path("C:/Program Files/Side Effects Software/Houdini 21.0.440/bin/hython.exe"),
        Path("C:/Program Files/Side Effects Software/Houdini 20.5.654/bin/hython.exe"),
        Path("C:/Program Files/Side Effects Software/Houdini 20.0.724/bin/hython.exe"),
        Path("C:/Program Files/Side Effects Software/Houdini 19.5.805/bin/hython.exe"),
        Path("D:/Program Files/Side Effects Software/Houdini 21.0.440/bin/hython.exe"),
        Path("D:/Program Files/Side Effects Software/Houdini 20.5.654/bin/hython.exe"),
        Path("D:/Program Files/Side Effects Software/Houdini 20.0.724/bin/hython.exe"),
    ]
    scanned: List[Path] = []
    for base in (
        Path("C:/Program Files/Side Effects Software"),
        Path("D:/Program Files/Side Effects Software"),
    ):
        if base.exists():
            scanned.extend(sorted(base.glob("Houdini*/bin/hython.exe")))
    return direct + [path for path in scanned if path not in direct]


def find_hython() -> Dict[str, object]:
    env_path = os.environ.get("AI_TOOL_TA_HYTHON")
    candidates = candidate_paths()
    if env_path and Path(env_path).exists():
        return {"available": True, "path": env_path, "searched": [str(path) for path in candidates]}
    found = shutil.which("hython")
    if found:
        return {"available": True, "path": found, "searched": [str(path) for path in candidates]}
    for candidate in candidates:
        if candidate.exists():
            return {"available": True, "path": str(candidate), "searched": [str(path) for path in candidates]}
    return {"available": False, "path": None, "searched": [str(path) for path in candidates]}


def write_readiness_report(search: Dict[str, object]) -> Path:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("houdini-rule-adapter-l3-readiness-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    report = {
        "reportVersion": "houdini-rule-adapter-l3-readiness@0.1.0",
        "generatedBy": "AI Tool TA Portfolio / Houdini Rule Adapter",
        "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidenceLevel": "L2+",
        "gate": "Blocked",
        "l3Status": "blocked_by_missing_hython",
        "houdiniRuntime": {
            "runner": "hython.exe",
            "available": False,
            "path": None,
            "searched": search["searched"],
            "runtimeLaunchPolicy": "automatic_when_hython_discovered",
        },
        "collector": {
            "script": str(SCRIPT),
            "ready": SCRIPT.exists(),
            "expectedCommand": "hython %s" % SCRIPT,
            "reportWhenAvailable": "houdini-rule-adapter-hython-l3@0.1.0",
        },
        "boundary": {
            "mutation": "no_houdini_runtime_invoked",
            "sceneWrites": 0,
            "assetWrites": 0,
            "productionWrites": 0,
        },
        "nextActions": [
            {
                "id": "install-or-locate-hython",
                "state": "blocked",
                "owner": "tool-ta",
                "reason": "hython.exe was not found in PATH, AI_TOOL_TA_HYTHON, or standard Houdini install locations.",
            },
            {
                "id": "run-hython-l3-smoke",
                "state": "ready_after_hython",
                "command": "python %s" % Path(__file__).resolve(),
            },
        ],
        "reviewerClaims": [
            "The Houdini contract, hython launcher and hou collector are present and compile in normal Python.",
            "The current machine cannot complete Houdini L3 because hython.exe is not installed or discoverable.",
            "No production HIP, cache, asset or engine data is mutated without a Houdini runtime.",
        ],
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    search = find_hython()
    if not search["available"]:
        path = write_readiness_report(search)
        print(
            json.dumps(
                {
                    "ok": True,
                    "path": str(path),
                    "reportVersion": "houdini-rule-adapter-l3-readiness@0.1.0",
                    "evidenceLevel": "L2+",
                    "l3Status": "blocked_by_missing_hython",
                    "gate": "Blocked",
                    "collectorReady": SCRIPT.exists(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    output = ARTIFACTS / ("houdini-rule-adapter-hython-l3-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    env = os.environ.copy()
    env["AI_TOOL_TA_HOUDINI_L3_OUTPUT"] = str(output)
    completed = subprocess.run([str(search["path"]), str(SCRIPT)], cwd=str(ROOT), env=env, text=True, timeout=300)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
