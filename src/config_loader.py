from pathlib import Path
import yaml

CONFIG_DIR = Path("config")


def load_settings():
    """
    Loads global settings from config/settings.yaml.
    Returns a dictionary with all configuration values.
    """
    settings_path = CONFIG_DIR / "settings.yaml"

    if not settings_path.exists():
        raise FileNotFoundError("Missing config/settings.yaml")

    with settings_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_forums():
    """
    Loads forum configurations from config/forums.yaml.
    Returns a list of forum dictionaries.
    """
    forums_path = CONFIG_DIR / "forums.yaml"

    if not forums_path.exists():
        raise FileNotFoundError("Missing config/forums.yaml")

    with forums_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    forums = data.get("forums", [])
    if not isinstance(forums, list):
        raise ValueError("forums.yaml must contain a 'forums:' list")

    return forums
