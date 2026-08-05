from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from unreal_handoff_inspector.contract import build_report  # noqa: E402


COMMON_UNREAL_CLI = [
    r"C:\Program Files\Epic Games\UE_5.6\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.5\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"C:\Program Files\Epic Games\UE_5.2\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
    r"D:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe",
]


def find_unreal_cli() -> Optional[str]:
    for name in ("UnrealEditor-Cmd", "UnrealEditor-Cmd.exe", "UnrealEditor", "UnrealEditor.exe"):
        found = shutil.which(name)
        if found:
            return found
    for candidate in COMMON_UNREAL_CLI:
        if Path(candidate).exists():
            return candidate
    return None


def find_unreal_project() -> Optional[str]:
    env_path = os.environ.get("AI_TOOL_TA_UNREAL_PROJECT")
    if env_path and Path(env_path).exists():
        return str(Path(env_path))
    return None


def main() -> int:
    fixture_path = ROOT / "fixtures" / "synthetic_unreal_handoff.json"
    artifact_dir = ROOT / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    unreal_cli = find_unreal_cli()
    unreal_project = find_unreal_project()
    report = build_report(
        fixture_path,
        unreal_cli_available=bool(unreal_cli),
        unreal_cli_path=unreal_cli,
        unreal_project_path=unreal_project,
        unreal_python_executed=False,
    )
    artifact_path = artifact_dir / ("unreal-handoff-inspector-contract-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    artifact_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["evaluation"]["summary"]
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(artifact_path),
                "reportVersion": report["reportVersion"],
                "evidenceLevel": report["evidenceLevel"],
                "l3Status": report["l3Status"],
                "unrealCliAvailable": report["unrealCli"]["available"],
                "unrealProjectAvailable": report["unrealProject"]["available"],
                "gate": summary["gate"],
                "intentCount": summary["intentCount"],
                "importReady": summary["importReady"],
                "review": summary["review"],
                "blocked": summary["blocked"],
                "dryRunCommands": summary["dryRunCommands"],
                "passChecks": summary["passChecks"],
                "reviewChecks": summary["reviewChecks"],
                "blockedChecks": summary["blockedChecks"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
