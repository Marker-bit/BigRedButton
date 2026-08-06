import re
from dataclasses import dataclass


@dataclass
class EpisodeIndex:
    season: int
    episode: int


def parse_season_episode(episode_title: str) -> EpisodeIndex | None:
    result = re.match(
        r"^Сокровища императора, (\d+) сезон, (\d+) выпуск$", episode_title
    )
    if not result:
        return

    return EpisodeIndex(season=int(result.group(1)), episode=int(result.group(2)))
