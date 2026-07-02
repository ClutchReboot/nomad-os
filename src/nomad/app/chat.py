from nomad.core.conversation import ConversationService


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
