"""Voice command parsing."""


def parse_command(text: str) -> str:
    """Normalize a spoken command."""
    return text.strip().lower()


def is_stop_command(text: str) -> bool:
    """Return True when the spoken text requests the voice loop to stop."""
    return parse_command(text) in {"exit", "quit", "stop", "bye"}
