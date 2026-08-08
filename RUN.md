# Running BigRedButton

BigRedButton opens a selected RUTUBE episode on an Android TV over Ethernet.
USB debugging and ADB are not required for the main flow.

## Requirements

- Linux with `ip`, `curl`, and an Ethernet connection to the same network as
  the TV
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Python 3.13 or newer (uv can install it automatically)
- Android TV Remote Service ports 6466 and 6467 available on the TV

## Recommended installation

Save the release launcher once:

```sh
mkdir -p "$HOME/BigRedButton"
curl --fail --location \
  https://github.com/Marker-bit/BigRedButton/releases/latest/download/run.sh \
  -o "$HOME/BigRedButton/run.sh"
chmod +x "$HOME/BigRedButton/run.sh"
```

Run it with:

```sh
"$HOME/BigRedButton/run.sh"
```

The launcher checks the latest GitHub Release, downloads the actual versioned
wheel filename, verifies its SHA-256 checksum, and then runs it. It keeps the
last verified wheel, so the app continues to work if GitHub or the Internet is
temporarily unavailable. A failed or incomplete download never replaces the
current release.

Cached data is stored under `~/BigRedButton`:

```text
~/BigRedButton/
├── current-wheel
├── h96_credentials/
│   ├── cert.pem
│   └── key.pem
├── release.json
├── releases/
│   └── v0.1.15/bigredbutton-0.1.15-py3-none-any.whl
└── run.sh
```

The certificate and private key remain on the user's computer. They are not
part of the wheel, release, or repository.

## First run

1. Open RUTUBE on the TV.
2. Start `run.sh`.
3. Enter the pairing code shown on the TV. This happens only once unless the
   TV is reset or `~/BigRedButton/h96_credentials` is removed.
4. Use the left/right arrow keys to change which season is displayed. Enter
   any season and episode separated by a space, for example `1 3`; the typed
   selection is independent of the season currently displayed. The displayed
   season is remembered for the next launch. Press Enter without typing to
   reuse the previous selection.
5. The selected episode opens immediately in the already-running RUTUBE app.

Opening RUTUBE manually avoids the firmware/app bug that leaves both the home
screen and video screen active. The program sends only the `rutube://` episode
deep link.

## KDE desktop shortcut

Create `~/.local/share/applications/bigredbutton.desktop`:

```ini
[Desktop Entry]
Type=Application
Version=1.0
Name=BigRedButton
Comment=Open a RUTUBE episode on the TV
Exec=konsole -e /bin/sh -c "$HOME/BigRedButton/run.sh"
Icon=media-playback-start
Terminal=false
Categories=Utility;
```

The app should then appear in the KDE application menu.

## Run a wheel manually

For a directory containing one wheel, a wildcard is fine:

```sh
uv run --isolated --no-project --with ./bigredbutton*.whl python -m main
```

Do not use that wildcard in the release cache because it can contain multiple
versions. The launcher uses `current-wheel` to select exactly one verified
file and does not depend on a hard-coded version such as `0.1.15`.

## Build locally

```sh
uv lock --check
uv build --wheel
```

The wheel is written to `dist/` with its current project version in the
filename.

## Publishing a release

The workflow in `.github/workflows/release.yml` runs when a `v*` tag is
pushed. The tag must match the version in `pyproject.toml` exactly.

```sh
uv version --bump patch
uv lock
git add pyproject.toml uv.lock
git commit -m "Release v0.1.16"
git tag v0.1.16
git push origin main v0.1.16
```

GitHub Actions builds and smoke-tests the wheel, then publishes the wheel,
`SHA256SUMS`, `release.json`, and `run.sh`. `release.json` contains the exact
wheel filename and checksum used by the updater.

## Troubleshooting

| Problem | Fix |
|---|---|
| Pairing code appears every run | Keep `~/BigRedButton/h96_credentials`; check that the files are writable by the user |
| `Called ... after disconnect` | Update to the latest release; current versions reconnect once during send and disconnect cleanly |
| `Проверьте подключение кабеля Ethernet.` | Check the TV cable and run `ip neigh`; exactly one reachable Ethernet TV is expected |
| `No verified BigRedButton release is cached` | Connect to the Internet and run the launcher once |
| Update fails but an older version exists | The launcher reports the update error and runs the cached verified wheel |
| `uv: not found` | Install uv; GUI launchers expect it in `~/.local/bin` |

`rutube_media.py` is a separate playback-progress diagnostic and still needs
ADB. It is not used by the main application.
