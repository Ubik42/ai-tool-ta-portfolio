"""Local command bridge helpers for controlling the Maya host from outside Maya."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_COMMAND_PORT = ":7107"
HOST_ROOT = Path(__file__).resolve().parents[1]


def _normalize_port(port: str | int) -> str:
    text = str(port).strip()
    return text if text.startswith(":") else f":{text}"


def _client_port(port: str | int) -> int:
    return int(_normalize_port(port).lstrip(":"))


def _ensure_host_path() -> None:
    host = str(HOST_ROOT)
    if host not in sys.path:
        sys.path.insert(0, host)


def _list_command_ports(cmds: Any) -> List[str]:
    try:
        ports = cmds.commandPort(query=True, listPorts=True) or []
    except Exception:
        ports = []
    return [str(port) for port in ports]


def command_bridge_status(port: str | int = DEFAULT_COMMAND_PORT) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    normalized = _normalize_port(port)
    ports = _list_command_ports(cmds)
    return {
        "ok": True,
        "port": normalized,
        "clientHost": "127.0.0.1",
        "clientPort": _client_port(normalized),
        "open": normalized in ports,
        "openPorts": ports,
    }


def start_command_bridge(
    port: str | int = DEFAULT_COMMAND_PORT,
    open_portfolio: bool = False,
) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    _ensure_host_path()
    normalized = _normalize_port(port)
    before = command_bridge_status(normalized)
    started = False

    if not before["open"]:
        try:
            cmds.commandPort(
                name=normalized,
                sourceType="python",
                echoOutput=True,
                securityWarning=False,
            )
        except TypeError:
            cmds.commandPort(name=normalized, sourceType="python", echoOutput=True)
        started = True

    if open_portfolio:
        from .entry_point import show_portfolio

        show_portfolio()

    status = command_bridge_status(normalized)
    status.update({"started": started, "hostRoot": str(HOST_ROOT)})
    return status


def stop_command_bridge(port: str | int = DEFAULT_COMMAND_PORT) -> Dict[str, Any]:
    import maya.cmds as cmds  # type: ignore

    normalized = _normalize_port(port)
    before = command_bridge_status(normalized)
    if before["open"]:
        cmds.commandPort(name=normalized, close=True)
    status = command_bridge_status(normalized)
    status.update({"stopped": before["open"], "hostRoot": str(HOST_ROOT)})
    return status
