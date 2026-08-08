import asyncio

from androidtvremote2 import AndroidTVRemote, ConnectionClosed, InvalidAuth

from config import credentials_path


async def pair(remote: AndroidTVRemote) -> None:
    await remote.async_start_pairing()
    code = input("Введите код с телевизора: ").strip()
    await remote.async_finish_pairing(code)


async def open_rutube_video(remote: AndroidTVRemote, video_id: str):
    link = f"rutube://rutube.ru/video/{video_id}/"
    try:
        remote.send_launch_app_command(link)
    except ConnectionClosed:
        await remote.async_connect()
        remote.send_launch_app_command(link)
    await asyncio.sleep(1)


async def get_remote(host: str) -> AndroidTVRemote:
    remote = AndroidTVRemote(
        client_name="Python H96 Controller",
        certfile=str(credentials_path / "cert.pem"),
        keyfile=str(credentials_path / "key.pem"),
        host=host,
    )

    generated_credentials = await remote.async_generate_cert_if_missing()
    (credentials_path / "cert.pem").chmod(0o600)
    (credentials_path / "key.pem").chmod(0o600)
    if generated_credentials:
        await pair(remote)

    try:
        await remote.async_connect()
    except InvalidAuth:
        await pair(remote)
        await remote.async_connect()

    return remote
