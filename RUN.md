# Running BigRedButton from a wheel

This app is distributed as a wheel (`.whl`). You don't install it permanently —
`uv` builds a temporary environment with the wheel **and all its dependencies**
(camoufox, playwright, requests, ...), then runs `main`.

## Prerequisites

1. **uv** installed — `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux)
2. **adb** on your PATH — macOS: `brew install android-platform-tools` \
   Arch/CachyOS: `sudo pacman -S android-tools`
3. **Android device** with USB debugging enabled, plugged in, and authorized
   (accept the RSA prompt on the phone). Verify with: `adb devices`
4. **Python 3.13+** — uv will auto-download a matching Python if you don't have one
5. **Playwright's chromium browser** — installed once per machine (see below)

## Installing the browser (required once)

The app scrapes the show page with Playwright's **chromium**. Installing the
package does **not** download the browser — uv has no post-install hooks, so
you must run this manually once per machine, as the same user that will run
the app:

```sh
uv run --with bigredbutton-0.1.0-py3-none-any.whl playwright install chromium
```

On Linux, also install system libraries (needs sudo):

```sh
sudo env "PATH=$PATH" uv run --with bigredbutton-0.1.0-py3-none-any.whl playwright install-deps chromium
```

> `sudo env "PATH=$PATH"` is needed because sudo resets PATH to a minimal
> set, and `uv` lives in `~/.local/bin` — plain `sudo uv ...` fails with
> `uv: command not found`. The `env` trick passes your user PATH to root.

**Arch/CachyOS:** `install-deps` doesn't recognize `ID=cachyos` in
`/etc/os-release` and falls back to `apt-get` (which doesn't exist there).
Install the same packages directly with pacman instead:

```sh
sudo pacman -S --needed nss nspr atk at-spi2-atk at-spi2-core cups libdrm mesa \
  libxkbcommon libxcomposite libxdamage libxfixes libxrandr pango cairo gtk3 \
  libx11 libxcb libxext libxi libxtst ttf-liberation
```

`--needed` skips packages you already have. Either way, the browser itself is
downloaded with the no-sudo `playwright install chromium` command above.

The browser is cached in `~/.cache/ms-playwright` (Linux) or
`~/Library/Caches/ms-playwright` (macOS) and shared by all uv environments,
so you only do this once per machine.

In the dev project, the equivalent commands are
`uv run playwright install chromium` and
`sudo env "PATH=$PATH" uv run playwright install-deps chromium`.

If you skip this, the app fails at startup with an error like
*"Executable doesn't exist at .../chromium"*.

## Getting the wheel

If you built it yourself:

```sh
uv build
# produces dist/bigredbutton-0.1.0-py3-none-any.whl
```

Otherwise, place the received `.whl` file somewhere and note its path.

## Running

From a directory **outside** the project (so uv doesn't pick up the local
pyproject), with the wheel next to you:

```sh
uv run --with bigredbutton-0.1.0-py3-none-any.whl python -m main
```

The exact filename may differ if the version changed — adjust accordingly.

> Tip: rename it for convenience if you want:
> `mv bigredbutton-0.1.0-py3-none-any.whl bigredbutton.whl` and use
> `uv run --with bigredbutton.whl python -m main`.

## What happens when you run it

1. Kills the "Koala Clash" app and initializes config
2. Lists episodes of the show (format `season:episode - Сезон N, серия M`)
3. Prompts: `Выберите эпизод:` — type e.g. `3:5`
4. Picks the device if more than one is connected
5. Opens the episode URL on the device via adb

Your last-picked episode is remembered in `~/BigRedButton/` on the machine
you run it on.

## Desktop shortcut (KDE)

The app exits right after opening the URL, which would close the terminal
instantly. The shortcut below wraps it in a script that keeps the window open
until you press Enter.

### 1. Put the wheel somewhere stable

```sh
mkdir -p ~/BigRedButton
cp bigredbutton-0.1.0-py3-none-any.whl ~/BigRedButton/bigredbutton.whl
```

### 2. Create the launcher script

Save this as `~/BigRedButton/run.sh`:

```sh
#!/usr/bin/env sh
# Launch BigRedButton and keep the window open until Enter is pressed.
export PATH="$HOME/.local/bin:$PATH"   # GUI-launched apps don't always see uv
cd "$HOME/BigRedButton" || exit 1
uv run --with bigredbutton.whl python -m main
printf '\nPress Enter to close... '
read _
```

The `export PATH` line matters: apps launched from the Plasma desktop get a
minimal PATH, and `uv` lives in `~/.local/bin`.

Make it executable:

```sh
chmod +x ~/BigRedButton/run.sh
```

### 3. Create the .desktop shortcut

Save this as `~/Desktop/bigredbutton.desktop` (replace `user` with your
username):

```ini
[Desktop Entry]
Type=Application
Version=1.0
Name=BigRedButton
Comment=Open the episode on your Android device
Exec=konsole -e /home/user/BigRedButton/run.sh
Icon=media-playback-start
Terminal=false
Categories=Utility;
```

Then:

```sh
chmod +x ~/Desktop/bigredbutton.desktop
```

On Wayland, KDE may block the new shortcut — right-click the file on the
desktop and choose **Allow launching** (or **Unblock**). You can also move it
to `~/.local/share/applications/` to get it in the app menu instead.

### 4. Test it

```sh
~/BigRedButton/run.sh
```

If it works from the terminal, the desktop shortcut will behave the same —
konsole opens, the app runs, and the window stays until you press Enter.

## Troubleshooting

| Problem | Fix |
|---|---|
| `adb: command not found` | Install adb, or add it to PATH |
| `Устройство неавторизовано` (device unauthorized) | Unplug/plug, accept the RSA prompt, re-check `adb devices` |
| No devices shown | Enable USB debugging in Developer options, try a different cable/port |
| `No matching distribution found` / Python error | You need Python 3.13+; uv installs it automatically if allowed |
