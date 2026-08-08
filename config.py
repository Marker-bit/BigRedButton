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


def get_last_visible_season(show_id: str) -> int | None:
    path = config_path / f"{show_id}_last_visible_season.txt"
    if not path.exists():
        return None
    try:
        season = int(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return None
    return season if season > 0 else None


def set_last_visible_season(show_id: str, season: int) -> None:
    path = config_path / f"{show_id}_last_visible_season.txt"
    path.write_text(str(season), encoding="utf-8")


def get_last_notified_version() -> str | None:
    path = config_path / "last_notified_version.txt"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip() or None


def set_last_notified_version(version: str) -> None:
    path = config_path / "last_notified_version.txt"
    path.write_text(version, encoding="utf-8")
