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


def display_path(path: str | Path) -> str:
    path_obj = Path(path)
    try:
        relative = path_obj.resolve().relative_to(PORTFOLIO_ROOT.resolve())
    except Exception:
        return str(path_obj)
    return "<repo>\\" + str(relative)


def ensure_artifacts_dir() -> Path:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    return ARTIFACTS_DIR


def frontend_ready() -> bool:
    return FRONTEND_INDEX.exists()


def paths_report() -> dict:
    return {
        "host_root": display_path(HOST_ROOT),
        "portfolio_root": "<repo>",
        "frontend_root": display_path(FRONTEND_ROOT),
        "frontend_dist": display_path(FRONTEND_DIST),
        "frontend_index": display_path(FRONTEND_INDEX),
        "frontend_ready": frontend_ready(),
        "artifacts_dir": display_path(ARTIFACTS_DIR),
    }
