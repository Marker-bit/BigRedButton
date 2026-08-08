from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class Episode:
    title: str
    url: str


# Rutube's WAF blocks non-browser User-Agents with a 403 "Access Blocked".
CHROME_UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

API_URL = "https://rutube.ru/api/metainfo/tv/{show_id}/video"


def get_tv_show_series(show_id: str, season: int):
    """Return the episodes of a TV show season via Rutube's public JSON API."""
    episodes: list[Episode] = []
    url = API_URL.format(show_id=show_id)
    params: dict[str, str | int] = {"format": "json", "season": season}

    while url:
        response = requests.get(
            url,
            params=params,
            headers={"User-Agent": CHROME_UA},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        for item in data.get("results", []):
            video_url = item.get("video_url")
            if not video_url:
                continue
            episodes.append(Episode(title=item.get("title") or "", url=video_url))

        url = data.get("next")
        params = {}

    return episodes
