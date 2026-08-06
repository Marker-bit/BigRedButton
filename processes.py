import signal

import psutil


def kill_by_name(name: str):
    for proc in psutil.process_iter(["pid", "name"]):
        # print(proc.info['name'])
        if proc.info["name"] == name:
            try:
                proc.send_signal(signal.SIGINT)
                proc.send_signal(signal.SIGINT)
                print(f"Sent Ctrl+C to {name} (PID: {proc.info['pid']})")
                break
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"Could not signal PID {proc.info['pid']}: {e}")
