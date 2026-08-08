import asyncio

# from adb import Device, get_devices, open_url
from config import get_last_picked, init_config, set_last_picked
from iphelp import get_ethernet_neigh
from processes import kill_by_name
from remote import get_remote, open_rutube_video
from rutube_api import Episode, get_tv_show_series
from series import EpisodeIndex, parse_season_episode


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

    last_picked = get_last_picked("380158")
    last_season = int(last_picked.split(":")[0]) if last_picked is not None else None
    episodes = get_tv_show_series("380158", last_season or 3)
    options: list[tuple[EpisodeIndex, Episode]] = []
    for episode in episodes:
        idx = parse_season_episode(episode.title)
        if not idx:
            continue
        options.append((idx, episode))
        s = f"{idx.season}:{idx.episode} - Сезон {idx.season}, серия {idx.episode}"
        if last_picked == f"{idx.season}:{idx.episode}":
            s += " (выбрали в последний раз)"
        print(s)

    opt = input("Выберите эпизод: ")
    if ":" not in opt and opt.isdigit():
        opt = f"{opt}:1"
    season, episode = opt.split(":")
    season, episode = int(season), int(episode)
    set_last_picked("380158", f"{season}:{episode}")

    picked_episode: Episode | None = None
    for option in options:
        if option[0].season == season and option[0].episode == episode:
            picked_episode = option[1]
            break

    if not picked_episode:
        print("Неверный эпизод")
        return

    input("Откройте RUTUBE на телевизоре и нажмите Enter...")
    await open_rutube_video(
        remote, picked_episode.url.split("/video/")[1].replace("/", "")
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as err:  # noqa: BLE001
        print(
            f'Произошла ошибка "{err}", нажмите Enter для завершения.\nЗапустите программу заново после завершения.'
        )
