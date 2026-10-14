#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
export LANG=C.UTF-8 PYTHONUTF8=1 VPNPLUS_INSTALL_LANGUAGE=en
unset GH_TOKEN GITHUB_TOKEN GITHUB_PAT
printf 'ACCOUNTING PRO\nCreated by VIPServer Team\nChecking operating system...\n'
[[ ${EUID} == 0 ]] || { echo 'Run with sudo/root.' >&2; exit 1; }
. /etc/os-release
[[ ${ID:-} == ubuntu && ${VERSION_ID:-} == 24.04 && $(uname -m) == x86_64 ]] || { echo 'Ubuntu 24.04 x86_64 required.' >&2; exit 1; }
if ! command -v python3 >/dev/null || ! command -v curl >/dev/null; then
    echo 'Installing bootstrap prerequisites...'
    apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-upgrade python3 curl ca-certificates >/dev/null
fi
d=$(mktemp -d /tmp/accounting-pro-bootstrap.XXXXXXXX)
trap 'rm -rf "$d"' EXIT
trap 'echo "Installation stopped; no success claimed." >&2' ERR
base=https://raw.githubusercontent.com/VIPserver-Team/Accounting-Pro-Installer/bootstrap-v3.3
curl --fail --silent --show-error --proto '=https' --tlsv1.2 "$base/bootstrap.py" -o "$d/bootstrap.py"
curl --fail --silent --show-error --proto '=https' --tlsv1.2 "$base/release.json" -o "$d/release.json"
python3 "$d/bootstrap.py" "$@"
