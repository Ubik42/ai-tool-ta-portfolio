"""Shared paths for the Maya AuroraView host."""

from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
HOST_ROOT = PACKAGE_ROOT.parent
PORTFOLIO_ROOT = PACKAGE_ROOT.parents[2]
FRONTEND_ROOT = PORTFOLIO_ROOT / "showcases" / "portfolio-site"
FRONTEND_DIST = FRONTEND_ROOT / "dist"
FRONTEND_INDEX = FRONTEND_DIST / "index.html"
ARTIFACTS_DIR = HOST_ROOT / "artifacts"


def ensure_artifacts_dir() -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    return ARTIFACTS_DIR


def frontend_ready() -> bool:
    return FRONTEND_INDEX.exists()


def paths_report() -> dict:
    return {
        "host_root": str(HOST_ROOT),
        "portfolio_root": str(PORTFOLIO_ROOT),
        "frontend_root": str(FRONTEND_ROOT),
        "frontend_dist": str(FRONTEND_DIST),
        "frontend_index": str(FRONTEND_INDEX),
        "frontend_ready": frontend_ready(),
        "artifacts_dir": str(ARTIFACTS_DIR),
    }
