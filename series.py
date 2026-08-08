import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EpisodeIndex:
    season: int
    episode: int


def parse_season_episode(episode_title: str) -> EpisodeIndex | None:
    result = re.match(
        r"^Сокровища императора, (?:(\d+) сезон, )?(\d+) выпуск(?:\. ФИНАЛ)?$",
        episode_title,
    )
    if not result:
        return

    return EpisodeIndex(
        season=int(result.group(1) or 1),
        episode=int(result.group(2)),
    )
