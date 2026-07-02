"""Nomad robot entry point."""

import argparse

from nomad.core.conversation import ConversationService
from nomad.core.runtime import RobotRuntime
from nomad.voice.commands import is_stop_command
from nomad.voice.speech_to_text import SpeechToText
from nomad.voice.text_to_speech import TextToSpeech


def main() -> None:
    """Start a Nomad command."""
    parser = argparse.ArgumentParser(prog="nomad")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run", help="Start the robot runtime loop.")
    subparsers.add_parser("chat", help="Start a local text chat with Nomad.")
    subparsers.add_parser("voice", help="Start a voice chat loop with Nomad.")
    serve_parser = subparsers.add_parser("serve", help="Start the Nomad HTTP API.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=8000, type=int)

    args = parser.parse_args()

    if args.command == "chat":
        chat()
        return

    if args.command == "voice":
        voice_chat()
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


def voice_chat(
    conversation: ConversationService | None = None,
    speech_to_text: SpeechToText | None = None,
    text_to_speech: TextToSpeech | None = None,
    stop_after: int | None = None,
) -> None:
    """Start a voice chat loop with wake-word detection.

    The loop listens continuously for "Nomad" as a wake-word, then processes
    what follows as a command or message.
    """
    conversation_service = conversation or ConversationService()
    recognizer = speech_to_text or SpeechToText()
    speaker = text_to_speech or TextToSpeech()

    print("Nomad voice chat started. Say 'Nomad' followed by your command.")
    print("To exit, say 'Nomad exit', 'Nomad quit', 'Nomad stop', or 'Nomad bye'.")

    processed_turns = 0
    while stop_after is None or processed_turns < stop_after:
        try:
            transcript = recognizer.listen_continuously()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not transcript or not transcript.strip():
            continue

        normalized = transcript.strip().lower()
        # Remove spaces to handle "no mad" being recognized as two words
        normalized_compact = normalized.replace(" ", "")
        if not normalized_compact.startswith("nomad"):
            continue

        # Extract the command after "nomad" (skipping the 5 characters of "nomad")
        command = normalized_compact[5:].strip()

        if is_stop_command(command):
            break

        if command:
            conversation_service.handle_message(command)
            processed_turns += 1


def serve(host: str, port: int) -> None:
    """Start the local API server."""
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Install API dependencies before starting the server.") from exc

    uvicorn.run("nomad.api.server:create_app", host=host, port=port, factory=True)


if __name__ == "__main__":
    main()
