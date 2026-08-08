from pathlib import Path

config_path = Path.home() / "BigRedButton"
credentials_path = config_path / "h96_credentials"


def init_config():
    config_path.mkdir(parents=True, exist_ok=True)
    credentials_path.mkdir(mode=0o700, exist_ok=True)
    credentials_path.chmod(0o700)


def get_last_picked(show_id: str):
    path = config_path / f"{show_id}_last_picked.txt"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def set_last_picked(show_id: str, data: str):
    path = config_path / f"{show_id}_last_picked.txt"
    with open(path, "w", encoding="utf-8") as file:
        file.write(data)
