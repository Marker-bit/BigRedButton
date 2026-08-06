from adb import Device, get_devices, open_url
from config import get_last_picked, init_config, set_last_picked
from processes import kill_by_name
from rutube_api import Episode, get_tv_show_series
from series import EpisodeIndex, parse_season_episode


def main():
    kill_by_name("Koala Clash")
    init_config()

    episodes = get_tv_show_series("380158", 3)
    last_picked = get_last_picked("380158")
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

    devices = get_devices()

    if len(devices) == 1 and devices[0].status == "unauthorized":
        print("Устройство неавторизовано")
        return

    device: Device | None = None
    if len(devices) == 1 and devices[0].status == "device":
        device = devices[0]
    else:
        print("Выберите устройство:")
        for idx, d in enumerate(filter(lambda d: d.status == "device", devices)):
            print(f"{idx + 1}. {d.id}")

        device_idx = int(input("Номер устройства: "))
        device = devices[device_idx]

    print("Выбрано устройство", device.id)
    open_url(picked_episode.url, device.id)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # noqa: BLE001
        print(
            f"Произошла ошибка \"{err}\", нажмите Enter для завершения.\nЗапустите программу заново после завершения."
        )
