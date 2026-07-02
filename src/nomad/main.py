from nomad.core.runtime import RobotRuntime
from nomad.voice.commands import is_stop_command
from nomad import app

def main() -> None:
    """Start a Nomad command."""
    parser = app.build_parser()
    args = parser.parse_args()

    if args.command == "chat":
        app.chat()
        return

    if args.command == "voice":
        app.voice_chat()
        return

    if args.command == "serve":
        app.serve(args.host, args.port)
        return

    RobotRuntime().run()


if __name__ == "__main__":
    main()
