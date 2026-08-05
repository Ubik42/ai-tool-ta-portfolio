"""Send Python commands to a running Maya commandPort bridge."""

from __future__ import annotations

import argparse
import socket
from pathlib import Path


HOST_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PORT = 7107


def _exec_command(source: str) -> str:
    return "exec({0!r})".format(source)


def build_show_portfolio_command() -> str:
    return _exec_command(
        "\n".join(
            [
                "import sys",
                f"host = {str(HOST_ROOT)!r}",
                "if host not in sys.path:",
                "    sys.path.insert(0, host)",
                "from ai_tool_ta_maya_host import show_portfolio",
                "show_portfolio()",
            ]
        )
    )


def build_export_presenter_pack_command(label: str) -> str:
    return _exec_command(
        "\n".join(
            [
                "import sys",
                f"host = {str(HOST_ROOT)!r}",
                "if host not in sys.path:",
                "    sys.path.insert(0, host)",
                "from ai_tool_ta_maya_host.api import MayaPortfolioApi",
                f"print(MayaPortfolioApi().dcc_presentation_export_pack(label={label!r}))",
            ]
        )
    )


def send_command(command: str, port: int, timeout_seconds: float) -> str:
    payload = (command.rstrip() + "\n").encode("utf-8")
    chunks: list[bytes] = []
    with socket.create_connection(("127.0.0.1", port), timeout=timeout_seconds) as sock:
        sock.settimeout(timeout_seconds)
        sock.sendall(payload)
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        except socket.timeout:
            pass
    return b"".join(chunks).decode("utf-8", errors="replace").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout-seconds", type=float, default=2.0)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--show-portfolio", action="store_true")
    group.add_argument("--export-presenter-pack")
    group.add_argument("--eval", dest="eval_source")
    args = parser.parse_args()

    if args.show_portfolio:
        command = build_show_portfolio_command()
    elif args.export_presenter_pack:
        command = build_export_presenter_pack_command(args.export_presenter_pack)
    else:
        command = str(args.eval_source)

    response = send_command(command, args.port, args.timeout_seconds)
    if response:
        print(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
