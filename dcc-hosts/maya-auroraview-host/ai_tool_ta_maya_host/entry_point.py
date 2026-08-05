"""Public entry point for Maya shelf/script editor usage."""

from __future__ import annotations

from .maya_window import show_portfolio


def show():
    return show_portfolio()
