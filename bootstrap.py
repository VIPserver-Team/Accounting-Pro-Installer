"""Tokenless public release bootstrap; interactive input belongs to setup only."""
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from urllib.parse import urlparse

BOOTSTRAP_VERSION = 3
MAX_BYTES = 32 * 1024 * 1024
PUBLIC_REPO = 'VIPserver-Team/Accounting-Pro-Installer'
ALLOWED_HOSTS = {'github.com', 'raw.githubusercontent.com', 'release-assets.githubusercontent.com'}

class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def validate_url(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('Unexpected public download URL')

def download(url):
    validate_url(url)
    opener = urllib.request.build_opener(PublicRedirect())
    with opener.open(urllib.request.Request(url, headers={'User-Agent': 'Accounting-Pro-Installer'}), timeout=60) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('Release exceeds download limit')
    return data

def validate_manifest(value):
    required = {'format', 'version', 'tag', 'asset', 'asset_url', 'sha256', 'application_commit', 'source_digest', 'minimum_bootstrap_version', 'files', 'bytes'}
    if not isinstance(value, dict) or set(value) != required or type(value['format']) is not int or value['format'] != 2:
        raise ValueError('Invalid release manifest')
    for name in ('sha256', 'source_digest'):
        if not isinstance(value[name], str) or not re.fullmatch(r'[0-9a-f]{64}', value[name]):
            raise ValueError('Invalid release digest')
    if not isinstance(value['application_commit'], str) or not re.fullmatch(r'[0-9a-f]{40}', value['application_commit']):
        raise ValueError('Invalid application commit')
    if not isinstance(value['version'], str) or not re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', value['version']):
        raise ValueError('Invalid release version')
    if not isinstance(value['tag'], str) or not re.fullmatch(r'accounting-pro-v[0-9][0-9A-Za-z.-]*', value['tag']):
        raise ValueError('Invalid release tag')
    if type(value['minimum_bootstrap_version']) is not int or not 1 <= value['minimum_bootstrap_version'] <= BOOTSTRAP_VERSION:
        raise ValueError('This release requires a newer bootstrap')
    if type(value['files']) is not int or not 1 <= value['files'] <= 10000 or type(value['bytes']) is not int or not 1 <= value['bytes'] <= MAX_BYTES:
        raise ValueError('Invalid release size or inventory')
    asset = 'accounting-pro-' + value['application_commit'] + '.tar.gz'
    expected = 'https://github.com/' + PUBLIC_REPO + '/releases/download/' + value['tag'] + '/' + asset
    if value['asset'] != asset or value['asset_url'] != expected:
        raise ValueError('Release asset must belong to the official public repository')
    return value

def unpack(data, destination, release):
    if len(data) != release['bytes'] or hashlib.sha256(data).hexdigest() != release['sha256']:
        raise ValueError('Release checksum or size mismatch')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = archive.getmembers()
        seen = set()
        if len(members) != release['files'] or sum(m.size for m in members) > 64 * 1024 * 1024:
            raise ValueError('Invalid release inventory')
        for member in members:
            path = PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or member.name != path.as_posix() or path.as_posix() in seen or any(p.startswith('.') for p in path.parts):
                raise ValueError('Unsafe release archive')
            if path.parts[0] not in ('backend', 'deploy', 'frontend', 'install.sh', 'source.commit'):
                raise ValueError('Unexpected release contents')
            seen.add(path.as_posix())
            target = destination.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
            target.chmod(0o600)
    if (destination / 'source.commit').read_text().strip() != release['application_commit']:
        raise ValueError('Release commit mismatch')
    sys.path.insert(0, str(destination))
    from deploy.installer import source_digest
    if source_digest(destination) != release['source_digest']:
        raise ValueError('Application source digest mismatch')

def check_platform():
    values = dict(line.split('=', 1) for line in Path('/etc/os-release').read_text().splitlines() if '=' in line)
    if os.geteuid() != 0:
        raise RuntimeError('Run with sudo/root.')
    if values.get('ID', '').strip('"') != 'ubuntu' or values.get('VERSION_ID', '').strip('"') != '24.04' or platform.machine() != 'x86_64':
        raise RuntimeError('Ubuntu 24.04 x86_64 is required.')

def main():
    print('ACCOUNTING PRO\nCreated by VIPServer Team\nChecking operating system...', flush=True)
    check_platform()
    release = validate_manifest(json.loads((Path(__file__).parent / 'release.json').read_text()))
    print('Downloading verified public release...', flush=True)
    data = download(release['asset_url'])
    print('Verifying checksum and pinned application version...', flush=True)
    with tempfile.TemporaryDirectory(prefix='accounting-pro-app-') as tmp:
        destination = Path(tmp)
        unpack(data, destination, release)
        print('Checksum PASS. Application commit and source digest PASS.', flush=True)
        print('Preparing resumable web setup...', flush=True)
        env = dict(os.environ, VPNPLUS_INSTALL_LANGUAGE='en')
        for name in ('GH_TOKEN', 'GITHUB_TOKEN', 'GITHUB_PAT'):
            env.pop(name, None)
        if '--preflight' in sys.argv[1:]:
            subprocess.run(['bash',str(destination/'install.sh'),'--preflight'],check=True,cwd=destination,env=env)
        else:
            subprocess.run([sys.executable,'-m','deploy.setup_web'],check=True,cwd=destination,env=env)
    print('Setup is ready. Finish the guided web wizard; reconnect safely if SSH disconnects.', flush=True)

if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, OSError, KeyError, TypeError, tarfile.TarError, subprocess.CalledProcessError) as error:
        print('Accounting Pro installation failed. Check the public release, manifest, checksum and system requirements. No success claimed.', file=sys.stderr)
        sys.exit(1)
