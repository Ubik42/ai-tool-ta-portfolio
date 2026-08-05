from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import run_texture_runtime_probe  # noqa: E402


def main() -> int:
    os.environ["AI_TOOL_TA_PLATFORM_VARIANT_TEXTURE_PAYLOAD"] = "1"
    os.environ["AI_TOOL_TA_PLATFORM_VARIANT_TEXTURE_OUTPUT_PREFIX"] = "platform-variant-texture-payload-runtime"
    return run_texture_runtime_probe.main()


if __name__ == "__main__":
    raise SystemExit(main())
