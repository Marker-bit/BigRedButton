#!/bin/sh

set -u

APP_DIR="${BIGREDBUTTON_HOME:-$HOME/BigRedButton}"
RELEASE_BASE_URL="${BIGREDBUTTON_RELEASE_BASE_URL:-https://github.com/Marker-bit/BigRedButton/releases/latest/download}"
RELEASES_DIR="$APP_DIR/releases"
CURRENT_FILE="$APP_DIR/current-wheel"
METADATA_FILE="$APP_DIR/release.json"

export PATH="$HOME/.local/bin:$PATH"

mkdir -p "$RELEASES_DIR"

checksum() {
    if command -v sha256sum >/dev/null 2>&1; then
        sha256sum "$1" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then
        shasum -a 256 "$1" | awk '{print $1}'
    else
        return 1
    fi
}

json_string() {
    key="$1"
    sed -n "s/.*\"$key\":\"\([^\"]*\)\".*/\1/p" "$METADATA_FILE"
}

download_update() {
    tmp_metadata="$METADATA_FILE.tmp.$$"
    if ! curl --fail --silent --show-error --location \
        "$RELEASE_BASE_URL/release.json" -o "$tmp_metadata"; then
        rm -f "$tmp_metadata"
        return 1
    fi
    mv "$tmp_metadata" "$METADATA_FILE"

    version="$(json_string version)"
    wheel="$(json_string wheel)"
    expected="$(json_string sha256)"
    case "$version:$wheel:$expected" in
        *[!A-Za-z0-9._:+-]*|::*|*/*) return 1 ;;
    esac

    version_dir="$RELEASES_DIR/$version"
    wheel_path="$version_dir/$wheel"
    mkdir -p "$version_dir"

    if [ ! -f "$wheel_path" ] || [ "$(checksum "$wheel_path")" != "$expected" ]; then
        tmp_wheel="$wheel_path.tmp.$$"
        if ! curl --fail --silent --show-error --location \
            "$RELEASE_BASE_URL/$wheel" -o "$tmp_wheel"; then
            rm -f "$tmp_wheel"
            return 1
        fi
        if [ "$(checksum "$tmp_wheel")" != "$expected" ]; then
            echo "Проверка контрольной суммы загруженного обновления не пройдена." >&2
            rm -f "$tmp_wheel"
            return 1
        fi
        mv "$tmp_wheel" "$wheel_path"
    fi

    tmp_current="$CURRENT_FILE.tmp.$$"
    printf '%s\n' "$wheel_path" >"$tmp_current"
    mv "$tmp_current" "$CURRENT_FILE"
}

download_update || echo "Обновление недоступно; запускаю сохранённую версию." >&2

wheel_path=""
if [ -f "$CURRENT_FILE" ]; then
    IFS= read -r wheel_path <"$CURRENT_FILE"
fi

if [ -z "$wheel_path" ] || [ ! -f "$wheel_path" ]; then
    echo "На компьютере нет проверенной версии BigRedButton." >&2
    echo "Подключитесь к Интернету и запустите программу ещё раз." >&2
    exit 1
fi

uv run --isolated --no-project --with "$wheel_path" python -m main
status=$?
printf '\nНажмите клавишу Ввод, чтобы закрыть окно... '
read -r _
exit "$status"
