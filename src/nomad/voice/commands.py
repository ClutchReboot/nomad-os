"""Voice command parsing."""


def parse_command(text: str) -> str:
    """Normalize a spoken command."""
    return text.strip().lower()
