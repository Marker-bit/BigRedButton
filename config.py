from pathlib import Path

config_path = Path.home() / "BigRedButton"


def init_config():
    config_path.mkdir(parents=True, exist_ok=True)


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
