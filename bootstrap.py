"""Public bootstrap; application assets require the operator's GitHub access."""
import getpass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import warnings
from urllib.parse import urlparse

RELEASE = json.loads((Path(__file__).parent / 'release.json').read_text())
API = 'https://api.github.com/repos/' + RELEASE['repository']
MAX_BYTES = 32 * 1024 * 1024

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def request(url, token=None, binary=False):
    headers = {'Accept': 'application/octet-stream' if binary else 'application/vnd.github+json',
               'User-Agent': 'Accounting-Pro-Installer', 'X-GitHub-Api-Version': '2022-11-28'}
    if token:
        if urlparse(url).hostname != 'api.github.com':
            raise ValueError('Credentials may only be sent to api.github.com')
        headers['Authorization'] = 'Bearer ' + token
    opener = urllib.request.build_opener(NoRedirect())
    try:
        response = opener.open(urllib.request.Request(url, headers=headers), timeout=60)
    except urllib.error.HTTPError as error:
        if binary and error.code == 302:
            location = error.headers.get('Location', '')
            parsed = urlparse(location)
            if parsed.scheme != 'https' or parsed.hostname != 'release-assets.githubusercontent.com':
                raise ValueError('Unexpected release download host') from None
            # Signed download URL, never forward the GitHub token to storage.
            return request(location, binary=True)
        raise RuntimeError('GitHub download failed (HTTP %s); check repository access and release publication.' % error.code) from None
    with response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('Release exceeds download limit')
    return data

def unpack(data, destination, release=RELEASE):
    if hashlib.sha256(data).hexdigest() != release['sha256']:
        raise ValueError('Release checksum mismatch')
    import io
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = archive.getmembers()
        seen = set()
        if len(members) != release['files'] or sum(m.size for m in members) > 64 * 1024 * 1024:
            raise ValueError('Invalid release inventory')
        for member in members:
            path = PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or member.name in seen:
                raise ValueError('Unsafe release archive')
            seen.add(member.name)
            target = destination.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
            target.chmod(0o600)
    if (destination / 'source.commit').read_text().strip() != release['commit']:
        raise ValueError('Release commit mismatch')
    # Verify the same source identity that the official updater records.
    sys.path.insert(0, str(destination))
    from deploy.installer import source_digest
    if source_digest(destination) != release['source_digest']:
        raise ValueError('Application source digest mismatch')

def main():
    if os.geteuid() != 0:
        raise RuntimeError('Run this installer with sudo/root.')
    if platform.machine() != 'x86_64' or 'VERSION_ID="24.04"' not in Path('/etc/os-release').read_text():
        raise RuntimeError('Ubuntu 24.04 x86_64 is required.')
    print('ACCOUNTING PRO\nCrate By VIPServer Team', flush=True)
    print('Private release access: enter your own GitHub token with Contents: read permission.\nدسترسی نسخه خصوصی: توکن گیت‌هاب خود را با مجوز خواندن Contents وارد کنید.', flush=True)
    if not os.isatty(0):
        raise RuntimeError('An interactive terminal is required for hidden token entry.')
    # getpass opens /dev/tty for input itself. The prompt stream is write-only:
    # buffered read/write mode cannot be used on a non-seekable terminal.
    with open('/dev/tty', 'w', encoding='utf-8') as tty:
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            token = getpass.getpass('GitHub token / توکن گیت‌هاب: ', stream=tty)
    if not token or any(c in token for c in '\r\n'):
        raise ValueError('A valid GitHub token is required')
    try:
        metadata = json.loads(request(API + '/releases/tags/' + RELEASE['tag'], token))
        assets = [a for a in metadata.get('assets', []) if a['name'] == RELEASE['asset']]
        if len(assets) != 1 or assets[0]['size'] != RELEASE['bytes']:
            raise ValueError('Pinned private release asset is unavailable')
        data = request(API + '/releases/assets/' + str(int(assets[0]['id'])), token, binary=True)
    finally:
        # Clear our credential reference before verification or application execution,
        # including failure paths. No environment, file or subprocess receives it.
        token = None
    with tempfile.TemporaryDirectory(prefix='accounting-pro-app-') as tmp:
        destination = Path(tmp)
        unpack(data, destination)
        subprocess.run(['bash', str(destination / 'install.sh'), *sys.argv[1:]], check=True,
                       cwd=destination)

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError, subprocess.CalledProcessError, getpass.GetPassWarning):
        print('Accounting Pro bootstrap failed. Verify OS, GitHub access, release availability and checksum.\nراه‌اندازی ناموفق بود؛ سیستم‌عامل، دسترسی گیت‌هاب و نسخه را بررسی کنید.', file=sys.stderr)
        sys.exit(1)
