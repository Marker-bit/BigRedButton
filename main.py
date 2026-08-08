import asyncio

# from adb import Device, get_devices, open_url
from config import (
    get_last_picked,
    get_last_visible_season,
    init_config,
    set_last_picked,
    set_last_visible_season,
)
from iphelp import get_ethernet_neigh
from picker import choose_episode
from processes import kill_by_name
from remote import get_remote, open_rutube_video
from rutube_api import Episode, get_tv_show_series
from series import EpisodeIndex, parse_season_episode

SHOW_ID = "380158"
DEFAULT_SEASON = 3


def parse_saved_episode(value: str | None) -> EpisodeIndex | None:
    if value is None:
        return None
    try:
        season, episode = (int(part) for part in value.strip().split(":"))
    except (TypeError, ValueError):
        return None
    if season < 1 or episode < 1:
        return None
    return EpisodeIndex(season=season, episode=episode)


def get_season_options(season: int) -> list[tuple[EpisodeIndex, Episode]]:
    options: list[tuple[EpisodeIndex, Episode]] = []
    for episode in get_tv_show_series(SHOW_ID, season):
        idx = parse_season_episode(episode.title)
        if idx and idx.season == season:
            options.append((idx, episode))
    return options


async def main():
    kill_by_name("Koala Clash")
    init_config()
    neigh = get_ethernet_neigh()
    if len(neigh) != 1:
        print("Проверьте подключение кабеля Ethernet.")
        return

    remote = await get_remote(neigh[0])

    try:
        await choose_and_open_episode(remote)
    finally:
        remote.disconnect()


async def choose_and_open_episode(remote):
    last_picked = parse_saved_episode(get_last_picked(SHOW_ID))
    episode_options = {
        season: get_season_options(season) for season in range(1, DEFAULT_SEASON + 1)
    }
    indices = {
        season: tuple(idx for idx, _ in options)
        for season, options in episode_options.items()
    }
    selection = choose_episode(
        indices,
        last_picked,
        initial_visible_season=get_last_visible_season(SHOW_ID),
        on_visible_season_changed=lambda season: set_last_visible_season(
            SHOW_ID, season
        ),
    )
    picked_episode = next(
        episode
        for idx, episode in episode_options[selection.season]
        if idx == selection
    )

    set_last_picked(SHOW_ID, f"{selection.season}:{selection.episode}")
    await open_rutube_video(
        remote, picked_episode.url.split("/video/")[1].replace("/", "")
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as err:  # noqa: BLE001
        print(
            f'Произошла ошибка: "{err}". Нажмите клавишу Enter для завершения.\nПосле этого запустите программу заново.'
        )
