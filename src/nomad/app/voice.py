from nomad.core.conversation import ConversationService
from nomad.voice import SpeechToText, TextToSpeech, is_stop_command


def voice_chat(
    conversation: ConversationService | None = None,
    speech_to_text: SpeechToText | None = None,
    text_to_speech: TextToSpeech | None = None,
    stop_after: int | None = None,
) -> None:
    """Start a voice chat loop with wake-word detection.

    The loop listens for "Nomad" as a wake-word, then captures the command,
    and processes what follows.
    """
    conversation_service = conversation or ConversationService()
    recognizer = speech_to_text or SpeechToText()
    speaker = text_to_speech or TextToSpeech()

    print("Nomad voice chat started. Say 'Nomad' followed by your command.")
    print("To exit, say 'Nomad exit', 'Nomad quit', 'Nomad stop', or 'Nomad bye'.")
    print("Listening for wake word", end="", flush=True)

    processed_turns = 0
    while stop_after is None or processed_turns < stop_after:
        try:
            # Wait for wake-word detection
            if not recognizer.detect_wakeword():
                continue

            print("Wake word detected! Listening for command...")
            # Record the command after wake-word
            command = recognizer.listen_continuously()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not command or not command.strip():
            continue

        command = command.strip().lower()

        # Clean up any remnants of wake-word from the command
        command = command.replace("nomad", "").replace("no mad", "").strip()

        if is_stop_command(command):
            break

        if command:
            conversation_service.handle_message(command)
            processed_turns += 1
