# Accounting Pro

Created by VIPServer Team

Install on a fresh **Ubuntu 24.04 LTS x86_64** server from an interactive terminal:

```sh
curl -fsSL https://raw.githubusercontent.com/VIPserver-Team/Accounting-Pro-Installer/main/install.sh | sudo bash
```

**No GitHub token, GitHub login or private repository access is required.** The bootstrap downloads an immutable public release manifest and public runtime archive, verifies its SHA-256, exact application commit and canonical source digest, and then starts the normal setup wizard. Download and verification do not read stdin or require `/dev/tty`; only the interactive setup wizard uses terminal input when the installer is piped to Bash.

Terminal output is English-only. Persian remains available in the Web UI. Choose your Owner username and hidden password, configure the domain and panel port, and choose Let's Encrypt, an existing certificate or SSL later. Without SSL the panel stays local; use an SSH tunnel until HTTPS is configured. Run `sudo accounting-pro` for post-install management.

The manifest specifies the release version, public asset URL, SHA-256, exact application commit, source digest and minimum bootstrap version. Invalid manifests, unsupported systems, missing downloads, checksum mismatches and unsafe/corrupt archives stop installation. Ubuntu repositories, GitHub, PyPI, npm and nodejs.org must be reachable. Bootstrap prerequisites are installed from the existing Ubuntu repositories if needed.

The public asset contains only the installable runtime/application source, pinned dependency metadata, required installer/update helpers and frontend assets. It excludes repository history, GitHub configuration, operational configuration, databases, backups, tests, lab/developer helpers, credentials and private infrastructure references. The full VPN-Plus repository remains private. Public runtime files/source are intentionally distributed in the release asset.

Real public DNS and Let's Encrypt issuance/renewal validation remain **PENDING** until a suitable disposable public domain/server is available. Local DNS simulation and self-signed certificates do not establish public ACME qualification.
