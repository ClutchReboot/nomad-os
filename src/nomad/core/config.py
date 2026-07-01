"""Configuration loading for Nomad."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AppConfig:
    """Loaded runtime configuration."""

    settings: dict[str, Any]
    devices: dict[str, Any]
    secrets: dict[str, str | None]
    root_dir: Path

    @property
    def robot_name(self) -> str:
        return str(self.settings.get("robot", {}).get("name", "Nomad"))

    @property
    def initial_mode(self) -> str:
        return str(self.settings.get("runtime", {}).get("initial_mode", "idle"))

    @property
    def heartbeat_seconds(self) -> float:
        return float(self.settings.get("runtime", {}).get("heartbeat_seconds", 5))


def load_config(root_dir: Path | None = None) -> AppConfig:
    """Load YAML and environment-style config files from the project root."""
    project_root = root_dir or Path(__file__).resolve().parents[3]
    config_dir = project_root / "config"

    return AppConfig(
        settings=_load_yaml(config_dir / "settings.yaml"),
        devices=_load_yaml(config_dir / "devices.yaml"),
        secrets=_load_env(config_dir / "secrets.env"),
        root_dir=project_root,
    )


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("Install PyYAML before loading YAML config.") from exc

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in config file: {path}")

    return data


def _load_env(path: Path) -> dict[str, str | None]:
    if not path.exists():
        return {}

    values: dict[str, str | None] = {}

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)
            values[key.strip()] = value.strip() or None

    return values
