"""Qt/AuroraView window hosted inside Maya."""

from __future__ import annotations

from typing import Optional

from .api import MayaPortfolioApi
from .config import FRONTEND_DIST, FRONTEND_INDEX, frontend_ready, paths_report

_DIALOG = None


def maya_main_window():
    import maya.OpenMayaUI as omui  # type: ignore
    from qtpy import QtWidgets

    try:
        from shiboken2 import wrapInstance  # type: ignore
    except Exception:  # pragma: no cover - Maya 2025+ may use shiboken6
        from shiboken6 import wrapInstance  # type: ignore

    ptr = omui.MQtUtil.mainWindow()
    if ptr is None:
        raise RuntimeError("Cannot find Maya main window")
    return wrapInstance(int(ptr), QtWidgets.QWidget)


def _missing_frontend_html() -> str:
    report = paths_report()
    return """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body { margin: 0; padding: 24px; background: #202124; color: #f2f2f2; font-family: Arial, sans-serif; }
      code { color: #f6b15a; }
      pre { background: #121316; padding: 12px; white-space: pre-wrap; }
    </style>
  </head>
  <body>
    <h1>AI Tool TA Portfolio</h1>
    <p>Frontend dist was not found. Build it before opening the Maya host.</p>
    <pre>cd {frontend_root}
npm install
npm run build</pre>
    <p>Expected index: <code>{frontend_index}</code></p>
  </body>
</html>
""".format(**report)


def _dialog_class():
    from auroraview import QtWebView
    from qtpy import QtWidgets

    class PortfolioDialog(QtWidgets.QDialog):
        def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
            super().__init__(parent)
            self.setObjectName("AiToolTaPortfolioAuroraViewDialog")
            self.setWindowTitle("AI Tool TA Portfolio - Maya Host")
            self.resize(1280, 820)
            self.setSizeGripEnabled(True)
            self.setStyleSheet("background-color: #232528;")

            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(8, 8, 8, 8)

            self.webview = QtWebView(
                parent=self,
                title="AI Tool TA Portfolio",
                width=1260,
                height=780,
                dev_tools=True,
                context_menu=True,
                asset_root=str(FRONTEND_DIST),
                allow_file_protocol=False,
            )
            layout.addWidget(self.webview)
            self.webview.bind_api(MayaPortfolioApi())

            if frontend_ready():
                self.webview.load_file(FRONTEND_INDEX)
            else:
                self.webview.load_html(_missing_frontend_html())

            self.webview.show()

    return PortfolioDialog


def show_portfolio():
    """Show the portfolio host dialog in Maya and keep it alive."""
    global _DIALOG
    parent = maya_main_window()
    PortfolioDialog = _dialog_class()

    try:
        if _DIALOG is not None:
            _DIALOG.close()
    except Exception:
        pass

    _DIALOG = PortfolioDialog(parent)
    _DIALOG.show()
    return _DIALOG
