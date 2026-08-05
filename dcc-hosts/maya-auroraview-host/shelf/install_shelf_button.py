"""Install a Maya shelf button for the AI Tool TA portfolio host."""

from __future__ import annotations

import sys
from pathlib import Path

import maya.cmds as cmds  # type: ignore


HOST_ROOT = Path(__file__).resolve().parents[1]
COMMAND = r"""
import sys
host = r"{host}"
if host not in sys.path:
    sys.path.insert(0, host)
from ai_tool_ta_maya_host import show_portfolio
show_portfolio()
""".format(host=str(HOST_ROOT))

BRIDGE_COMMAND = r"""
import sys
host = r"{host}"
if host not in sys.path:
    sys.path.insert(0, host)
from ai_tool_ta_maya_host import start_command_bridge
print(start_command_bridge())
""".format(host=str(HOST_ROOT))


def _delete_existing_button(shelf_name: str, label: str) -> None:
    children = cmds.shelfLayout(shelf_name, query=True, childArray=True) or []
    for child in children:
        try:
            if cmds.shelfButton(child, query=True, label=True) == label:
                cmds.deleteUI(child)
        except RuntimeError:
            continue


def install() -> str:
    shelf_name = "AI_Tool_TA"
    if not cmds.shelfLayout(shelf_name, exists=True):
        cmds.shelfLayout(shelf_name, parent="ShelfLayout")

    _delete_existing_button(shelf_name, "AI Tool TA")
    _delete_existing_button(shelf_name, "TA Bridge")

    button = cmds.shelfButton(
        parent=shelf_name,
        label="AI Tool TA",
        annotation="Open AI Tool TA Portfolio AuroraView host",
        command=COMMAND,
        sourceType="python",
        imageOverlayLabel="TA",
    )

    cmds.shelfButton(
        parent=shelf_name,
        label="TA Bridge",
        annotation="Start AI Tool TA local command bridge on 127.0.0.1:7107",
        command=BRIDGE_COMMAND,
        sourceType="python",
        imageOverlayLabel="IO",
    )
    return button


install()
