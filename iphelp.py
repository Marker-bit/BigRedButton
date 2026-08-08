import subprocess


def get_ethernet_neigh() -> list[str]:
    result = subprocess.run(
        ["ip", "neigh"], capture_output=True, text=True, check=False
    )

    # print("stdout:", result.stdout)

    ips: list[str] = []

    for line in result.stdout.splitlines():
        items = line.split(" ")
        if not items[2].startswith("e"):
            continue
        ips.append(items[0])

    return ips
