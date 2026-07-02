import argparse


def build_parser() -> argparse.ArgumentParser:
    """Create and return the Nomad CLI parser."""
    parser = argparse.ArgumentParser(prog="nomad")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Start the robot runtime loop.")
    subparsers.add_parser("chat", help="Start a local text chat with Nomad.")
    subparsers.add_parser("voice", help="Start a voice chat loop with Nomad.")

    serve_parser = subparsers.add_parser("serve", help="Start the Nomad HTTP API.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8000, type=int)

    return parser