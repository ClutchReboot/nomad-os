from nomad.voice.speech_to_text import SpeechToText
from nomad.voice.text_to_speech import TextToSpeech
from nomad.core.conversation import ConversationService


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
        print()
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