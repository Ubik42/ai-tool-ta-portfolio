from __future__ import annotations

import json
import sys
import time
from pathlib import Path


HOST_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = HOST_ROOT / "artifacts"
MANIFEST = HOST_ROOT / "fixtures" / "synthetic_texture_delivery_manifest.json"

if str(HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(HOST_ROOT))

from max_rule_adapter.texture_manifest_link import build_texture_manifest_link_report  # noqa: E402


def _latest_l3_artifact() -> Path:
    candidates = sorted(ARTIFACTS.glob("max-rule-adapter-l3-*.json"))
    runtime_reports = []
    for path in candidates:
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if report.get("reportVersion") == "max-rule-adapter-pymxs-l3@0.1.0":
            runtime_reports.append(path)
    if not runtime_reports:
        raise FileNotFoundError(
            "No max-rule-adapter-pymxs-l3@0.1.0 artifact found. Run scripts/run_l3_smoke.py --run-runtime first."
        )
    return runtime_reports[-1]


def main() -> int:
    source = _latest_l3_artifact()
    report = build_texture_manifest_link_report(source, MANIFEST)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / ("max-texture-manifest-link-%s.json" % time.strftime("%Y%m%d-%H%M%S"))
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = report["evaluation"]["summary"]
    print(
        json.dumps(
            {
                "ok": True,
                "path": str(path),
                "source": str(source),
                "reportVersion": report["reportVersion"],
                "evidenceLevel": report["evidenceLevel"],
                "l3Status": report["l3Status"],
                "gate": summary["gate"],
                "assetCount": summary["assetCount"],
                "readyAssets": summary["readyAssets"],
                "reviewAssets": summary["reviewAssets"],
                "blockedAssets": summary["blockedAssets"],
                "materialRows": summary["materialRows"],
                "slotTextures": summary["slotTextures"],
                "manifestTextures": summary["manifestTextures"],
                "missingRequiredSemantics": summary["missingRequiredSemantics"],
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
