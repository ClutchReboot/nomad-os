"""Nomad robot entry point."""

import argparse

from nomad.core.conversation import ConversationService
from nomad.core.runtime import RobotRuntime


def main() -> None:
    """Start a Nomad command."""
    parser = argparse.ArgumentParser(prog="nomad")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run", help="Start the robot runtime loop.")
    subparsers.add_parser("chat", help="Start a local text chat with Nomad.")
    serve_parser = subparsers.add_parser("serve", help="Start the Nomad HTTP API.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8000, type=int)

    args = parser.parse_args()

    if args.command == "chat":
        chat()
        return

    if args.command == "serve":
        serve(args.host, args.port)
        return

    RobotRuntime().run()


def chat() -> None:
    """Start a local terminal chat loop."""
    conversation = ConversationService()
    print("Nomad chat started. Type 'exit' or 'quit' to leave.")

    while True:
        try:
            message = input("you> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if message.strip().lower() in {"exit", "quit"}:
            break

        if not message.strip():
            continue

        conversation.handle_message(message)


def serve(host: str, port: int) -> None:
    """Start the local API server."""
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Install API dependencies before starting the server.") from exc

    uvicorn.run("nomad.api.server:create_app", host=host, port=port, factory=True)


if __name__ == "__main__":
    main()
