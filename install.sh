#!/usr/bin/env bash
set -euo pipefail
[[ ${EUID} == 0 ]] || { echo 'Run with sudo/root.' >&2; exit 1; }
. /etc/os-release
[[ ${ID:-} == ubuntu && ${VERSION_ID:-} == 24.04 && $(uname -m) == x86_64 ]] || { echo 'Ubuntu 24.04 x86_64 required.' >&2; exit 1; }
command -v python3 >/dev/null && command -v curl >/dev/null || { echo 'python3 and curl are required.' >&2; exit 1; }
umask 077
d=$(mktemp -d /tmp/accounting-pro-bootstrap.XXXXXXXX)
trap 'rm -rf "$d"' EXIT
base=https://raw.githubusercontent.com/VIPserver-Team/Accounting-Pro-Installer/bootstrap-v1.1
curl --fail --silent --show-error --proto '=https' --tlsv1.2 "$base/bootstrap.py" -o "$d/bootstrap.py"
curl --fail --silent --show-error --proto '=https' --tlsv1.2 "$base/release.json" -o "$d/release.json"
python3 "$d/bootstrap.py" "$@"
