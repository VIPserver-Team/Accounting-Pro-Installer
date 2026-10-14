# Accounting Pro — guided web setup

Created by VIPServer Team

Run on Ubuntu 24.04 LTS x86_64 as root/sudo:

```sh
curl -fsSL https://raw.githubusercontent.com/VIPserver-Team/Accounting-Pro-Installer/main/install.sh | sudo bash
```

No GitHub token or private repository access is needed. The bootstrap verifies a pinned public runtime archive, then starts an owned web setup service. Terminal messages stay English. The web wizard defaults to Persian with real RTL, bundled licensed Persian fonts, mobile layout, English switching and light/dark appearance.

The terminal gives the secure SSH-tunnel command, local setup URL and a private one-time setup code. Keep the code private; never enter your SSH password into the web page. The setup service binds only to localhost and is not exposed publicly. After opening the tunnel, follow the browser wizard: welcome, server checks, safe installation mode, Owner settings and panel access.

Choose **IP only**, **domain without SSL**, or **domain with Let's Encrypt**. Domain and SSL are optional. A DNS mismatch warns and retains IP access; it does not prevent installation. For access without HTTPS, use an SSH tunnel for administrator login until HTTPS is configured.

Installation runs in a separate systemd job, with protected durable checkpoints and a secret-free stage journal. Closing SSH or the browser does not terminate it. Reconnect and run the same public command: the existing job/status is detected; failed stages can safely resume. Existing owned data and administrator identities are preserved. Interrupted Debian packages are repaired without deleting lock files or automatically restarting SSH.

The progress page shows 14 stages, concise explanations, retry/resume and optional technical details. The success page shows the panel URL, Owner username, SSL choice and health summary, never the password. `sudo accounting-pro` opens post-install management.

The public manifest pins release version, URL, SHA-256, application commit, source digest and minimum bootstrap version. Unsafe/corrupt archives, missing assets, wrong manifests and unsupported systems fail closed. Only audited runtime/application source and required assets are released; the full VPN-Plus repository, Git history, private configuration, credentials and backups remain private.

After completion, running the same command again verifies the current public release and uses the canonical backup/update path if an update is needed, preserving data and administrator identities. Completed setup units are disabled for boot; completed re-entry closes the protected setup gateway and removes enrollment material.
