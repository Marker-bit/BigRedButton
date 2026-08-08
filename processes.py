import signal

import psutil


def kill_by_name(name: str):
    for proc in psutil.process_iter(["pid", "name"]):
        # print(proc.info['name'])
        if proc.info["name"] == name:
            try:
                proc.send_signal(signal.SIGINT)
                proc.send_signal(signal.SIGINT)
                print(f"Приложение {name} остановлено (PID: {proc.info['pid']}).")
                break
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"Не удалось остановить процесс {proc.info['pid']}: {e}")
