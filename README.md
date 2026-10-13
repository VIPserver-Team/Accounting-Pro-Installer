# Accounting Pro installer

ACCOUNTING PRO — Crate By VIPServer Team

Supports Ubuntu 24.04 LTS x86_64. Run on a fresh server as root/sudo. Python 3 and curl must be installed. Interactive terminal required.

This repository contains only the bootstrap and a pinned release manifest. The Accounting Pro application remains in a private repository. Installation requires your own GitHub fine-grained token with **Contents: read** permission for `VIPserver-Team/VPN-Plus`, approved for the organization if required. A public bootstrap does not grant private application access. Enter the token at the hidden prompt; never put it in the command, environment, logs or configuration files. The bootstrap uses it in memory for the GitHub Releases API and does not retain it.

Installation command (pinned bootstrap release `bootstrap-v1`):

```sh
sudo bash -c 'd=$(mktemp -d /tmp/accounting-pro.XXXXXXXX) || exit; trap "rm -rf $d" EXIT; curl -fsSL --proto "=https" https://raw.githubusercontent.com/VIPserver-Team/Accounting-Pro-Installer/bootstrap-v1/install.sh -o "$d/install.sh" && bash "$d/install.sh"'
```

The bootstrap verifies the private release archive SHA-256, validates archive entries, and verifies the intended application commit and source digest before invoking the official application installer. English/Persian menus, initial Owner credentials and installation management are supplied by that installer. Dependency downloads still require internet access.

The release is pinned; updates require a reviewed new manifest and bootstrap release. Protect published release tags against changes. Run `accounting-pro` for post-install management. The private bundle includes deployable Python and frontend source; authorized recipients can inspect that source. No mechanism here conceals code from administrators who install it.

Real public DNS and Let's Encrypt validation: PENDING. A public domain and suitable disposable test server are required.
