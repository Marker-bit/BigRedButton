import subprocess
from dataclasses import dataclass
from typing import Literal

statuses = ["offline", "unauthorized", "device"]


@dataclass
class Device:
    id: str
    status: Literal["offline", "unauthorized", "device", "unknown"]


def get_devices():
    result = subprocess.run(
        ["adb", "devices"], capture_output=True, text=True, check=False
    )

    devices: list[Device] = []

    for line in result.stdout.splitlines()[1:]:
        if not line.strip():  # Guard against empty lines
            continue

        device_id, parsed_status = line.split()

        status: Literal["offline", "unauthorized", "device", "unknown"] = "unknown"

        if parsed_status in statuses:
            status = parsed_status  # type: ignore

        devices.append(Device(id=device_id, status=status))

    return devices


def open_url(url: str, device_id: str):
    subprocess.run(
        [
            "adb",
            "-s",
            device_id,
            "shell",
            "am",
            "start",
            "-a",
            "android.intent.action.VIEW",
            "-d",
            url,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
