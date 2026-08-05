"""Start the local Maya command bridge for AI Tool TA Portfolio control."""

from __future__ import annotations

import sys
import os
from pathlib import Path


def _resolve_host_root() -> Path:
    if "__file__" in globals():
        return Path(__file__).resolve().parents[1]
    override = os.environ.get("AI_TOOL_TA_MAYA_HOST")
    if override:
        return Path(override).resolve()
    return Path.cwd().resolve()


HOST_ROOT = _resolve_host_root()

if str(HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(HOST_ROOT))

from ai_tool_ta_maya_host.external_control import start_command_bridge


print(start_command_bridge())
