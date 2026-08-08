from __future__ import annotations

import sys
import termios
import tty
from collections.abc import Callable, Mapping, Sequence

from series import EpisodeIndex

CLEAR_SCREEN = "\033[2J\033[H"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


def parse_episode_input(
    value: str, default: EpisodeIndex | None
) -> EpisodeIndex | None:
    parts = value.split()
    if not parts:
        return default
    if len(parts) != 2:
        return None
    if not all(part.isdigit() and int(part) > 0 for part in parts):
        return None
    return EpisodeIndex(season=int(parts[0]), episode=int(parts[1]))


def move_visible_season(
    seasons: Sequence[int], current: int, direction: int
) -> int:
    index = seasons.index(current)
    return seasons[(index + direction) % len(seasons)]


def render_picker(
    options: Mapping[int, Sequence[EpisodeIndex]],
    visible_season: int,
    default: EpisodeIndex | None,
    typed: str = "",
    message: str | None = None,
) -> str:
    seasons = tuple(options)
    tabs = "   ".join(
        f"[ {season} ]" if season == visible_season else f"  {season}  "
        for season in seasons
    )
    lines = [f"Сезоны: {tabs}", "← → — показать другой сезон", ""]

    for idx in options[visible_season]:
        line = f"{idx.season} {idx.episode} - Сезон {idx.season}, серия {idx.episode}"
        if idx == default:
            line += " (выбрана в прошлый раз)"
        lines.append(line)

    if message:
        lines.extend(("", message))

    default_text = f" [{default.season} {default.episode}]" if default else ""
    lines.extend(("", f"Выберите эпизод{default_text}: {typed}█"))
    return "\n".join(lines)


def _read_key() -> str:
    key = sys.stdin.read(1)
    if key == "\x1b":
        suffix = sys.stdin.read(2)
        if suffix == "[D":
            return "LEFT"
        if suffix == "[C":
            return "RIGHT"
        return "ESCAPE"
    if key in {"\r", "\n"}:
        return "ENTER"
    if key in {"\x7f", "\b"}:
        return "BACKSPACE"
    if key == "\x03":
        raise KeyboardInterrupt
    return key


def choose_episode(
    options: Mapping[int, Sequence[EpisodeIndex]],
    default: EpisodeIndex | None,
    initial_visible_season: int | None = None,
    on_visible_season_changed: Callable[[int], None] | None = None,
) -> EpisodeIndex:
    seasons = tuple(options)
    visible_season = (
        initial_visible_season
        if initial_visible_season in options
        else default.season
        if default and default.season in options
        else seasons[-1]
    )
    if on_visible_season_changed:
        on_visible_season_changed(visible_season)

    if not sys.stdin.isatty():
        while True:
            print(render_picker(options, visible_season, default, typed="")[:-1])
            selection = parse_episode_input(input(), default)
            if selection and selection in options.get(selection.season, ()):
                return selection
            print("Неверный эпизод")

    original_settings = termios.tcgetattr(sys.stdin)
    typed = ""
    message = None
    try:
        tty.setraw(sys.stdin.fileno())
        sys.stdout.write(HIDE_CURSOR)
        while True:
            sys.stdout.write(
                CLEAR_SCREEN
                + render_picker(
                    options,
                    visible_season,
                    default,
                    typed=typed,
                    message=message,
                )
            )
            sys.stdout.flush()
            key = _read_key()
            message = None

            if key == "LEFT":
                visible_season = move_visible_season(seasons, visible_season, -1)
                if on_visible_season_changed:
                    on_visible_season_changed(visible_season)
            elif key == "RIGHT":
                visible_season = move_visible_season(seasons, visible_season, 1)
                if on_visible_season_changed:
                    on_visible_season_changed(visible_season)
            elif key == "BACKSPACE":
                typed = typed[:-1]
            elif key == "ENTER":
                selection = parse_episode_input(typed, default)
                if selection and selection in options.get(selection.season, ()):
                    return selection
                message = "Неверный эпизод. Введите сезон и серию через пробел."
            elif len(key) == 1 and (key.isdigit() or key == " "):
                typed += key
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)
        sys.stdout.write(SHOW_CURSOR + "\n")
        sys.stdout.flush()
