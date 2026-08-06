# rutube_media.py

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass


class AdbError(RuntimeError):
    """Raised when an ADB command fails."""


class RutubeSessionNotFound(RuntimeError):
    """Raised when no active RuTube media session is found."""


@dataclass(frozen=True)
class RutubePlayback:
    title: str
    position_ms: int
    buffered_position_ms: int | None
    is_playing: bool

    @property
    def progress_seconds(self) -> float:
        return self.position_ms / 1000

    @property
    def progress_formatted(self) -> str:
        return format_duration(self.position_ms)

    @property
    def buffered_progress_formatted(self) -> str | None:
        if self.buffered_position_ms is None:
            return None

        return format_duration(self.buffered_position_ms)


def format_duration(milliseconds: int) -> str:
    total_seconds = max(0, milliseconds // 1000)

    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    return f"{minutes}:{seconds:02d}"


def _run_adb(*args: str, serial: str | None = None) -> str:
    command = ["adb"]

    if serial is not None:
        command.extend(["-s", serial])

    command.extend(args)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as error:
        raise AdbError(
            "ADB was not found. Install Android Platform Tools and ensure "
            "`adb` is available in PATH."
        ) from error

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()
        raise AdbError(message or "ADB command failed")

    return result.stdout


def _extract_rutube_session(dump: str) -> str:
    package_marker = "package=ru.rutube.app"
    package_index = dump.find(package_marker)

    if package_index == -1:
        raise RutubeSessionNotFound("No active RuTube media session found")

    # The next session normally begins with another deeply-indented
    # MediaSession record. Limiting the section avoids parsing another app.
    remaining = dump[package_index:]
    next_package_match = re.search(r"\n\s+package=", remaining[len(package_marker) :])

    if next_package_match:
        end = len(package_marker) + next_package_match.start()
        return remaining[:end]

    return remaining


def _extract_title(session: str) -> str:
    metadata_match = re.search(
        r"^\s*metadata:.*?description=(.+)$",
        session,
        flags=re.MULTILINE,
    )

    if metadata_match is None:
        return "Unknown title"

    description = metadata_match.group(1).strip()

    # Android's media description is commonly:
    # title, subtitle, description
    # In RuTube's output, the first value is the useful video title.
    title = description.split(", null", maxsplit=1)[0].strip()

    return title or "Unknown title"


def get_rutube_playback(
    *,
    serial: str | None = None,
) -> RutubePlayback:
    """
    Return the current RuTube title and playback progress.

    Args:
        serial:
            Optional ADB device serial or network address, for example
            "192.168.1.50:5555".

    Raises:
        AdbError:
            If ADB cannot be executed.
        RutubeSessionNotFound:
            If RuTube has no active media session.
    """
    dump = _run_adb(
        "shell",
        "dumpsys",
        "media_session",
        serial=serial,
    )

    session = _extract_rutube_session(dump)

    state_match = re.search(
        r"state=PlaybackState\s*\{"
        r"state=([A-Z_]+)\(\d+\),\s*"
        r"position=(\d+),\s*"
        r"buffered position=(\d+)",
        session,
    )

    if state_match is None:
        raise RutubeSessionNotFound(
            "RuTube session exists, but playback state is unavailable"
        )

    state_name = state_match.group(1)
    position_ms = int(state_match.group(2))
    buffered_position_ms = int(state_match.group(3))

    return RutubePlayback(
        title=_extract_title(session),
        position_ms=position_ms,
        buffered_position_ms=buffered_position_ms,
        is_playing=state_name == "PLAYING",
    )


if __name__ == "__main__":
    playback = get_rutube_playback()

    print(f"Title: {playback.title}")
    print(f"Progress: {playback.progress_formatted}")
    print(f"Playing: {playback.is_playing}")
