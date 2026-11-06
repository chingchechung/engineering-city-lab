"""Create a new static-only release directory; no archives, uploads or publication.

Uses only the standard library and the existing read-only assignment validator.
The copy allowlist follows the reviewed local module/style graph, not directories.
"""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
import re
import posixpath
import shutil
import sys
import zipfile
from urllib.parse import urlsplit

if __package__:
    from .assignment_data import read_json
    from .validate_assignments import validate_path
    from .three_runtime import IMPORTS, VENDOR, checksum, module_specifiers, vendor_inventory
else:
    from assignment_data import read_json
    from validate_assignments import validate_path
    from three_runtime import IMPORTS, VENDOR, checksum, module_specifiers, vendor_inventory

ROOT = Path(__file__).resolve().parents[1]
NOTICES = ('LICENSE', 'THIRD_PARTY_NOTICES.html')


def regular_file(root, relative):
    path = root / relative
    if any(part.is_symlink() for part in [path, *path.parents] if part.is_relative_to(root)):
        raise ValueError(f'Symlinks are not release inputs: {relative}')
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Missing or unsafe release input: {relative}')
    return path


class RuntimeLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.import_maps = []
        self.in_import_map = False

    def handle_data(self, data):
        if self.in_import_map:
            self.import_maps[-1] += data

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_import_map = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and attrs.get('type') == 'importmap':
            self.in_import_map = True
            self.import_maps.append('')
        if tag == 'script' and 'src' in attrs:
            if not attrs['src'].startswith('./'):
                raise ValueError('Script runtime inputs must be relative and local')
            self.urls.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') == 'modulepreload' and not attrs['href'].startswith('./'):
            raise ValueError('Module preloads must be relative and local')
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'modulepreload', 'icon'):
            self.urls.append(attrs['href'])


def runtime_files(root):
    """Return only local HTML module/style dependencies, rejecting unsafe paths."""
    parser = RuntimeLinks()
    parser.feed(regular_file(root, 'index.html').read_text(encoding='utf-8'))
    if len(parser.import_maps) != 1 or json.loads(parser.import_maps[0]) != {'imports': IMPORTS}:
        raise ValueError('Three.js import map must use one exact local version')
    inventory = vendor_inventory(root, regular_file)
    files, pending = {'index.html'}, [(Path('.'), url) for url in parser.urls]
    while pending:
        parent, url = pending.pop()
        parsed = urlsplit(url)
        if parsed.scheme in ('https', 'data'):
            continue
        if parsed.scheme or parsed.netloc or '\\' in url or '%' in parsed.path or not parsed.path.startswith('./') and parent == Path('.'):
            raise ValueError(f'Runtime URL must be HTTPS, data or relative: {url}')
        vendor_parent = parent.as_posix().startswith(VENDOR + '/')
        relative = posixpath.normpath((parent / parsed.path).as_posix())
        if (not vendor_parent and '..' in Path(parsed.path).parts or
                vendor_parent and not relative.startswith(VENDOR + '/') or
                not relative.startswith(('js/', 'css/', VENDOR + '/'))):
            raise ValueError(f'Unsafe runtime input: {url}')
        if Path(relative).suffix not in ('.js', '.css'):
            raise ValueError(f'Unreviewed runtime asset type: {url}')
        if relative in files:
            continue
        source = regular_file(root, relative).read_text(encoding='utf-8')
        files.add(relative)
        if relative.endswith('.js'):
            for spec in module_specifiers(source):
                if spec.startswith('.'):
                    pending.append((Path(relative).parent, spec))
                elif spec in IMPORTS:
                    pending.append((Path('.'), IMPORTS[spec]))
                elif spec.startswith('three/addons/'):
                    pending.append((Path('.'), IMPORTS['three/addons/'] + spec.removeprefix('three/addons/')))
                else:
                    raise ValueError(f'Unmapped or external JavaScript import: {spec}')
        else:
            # Consume a complete quoted data URL so embedded SVG url(...) is not
            # mistaken for an additional local stylesheet dependency.
            for match in re.findall(r'''url\(\s*(?:"([^"]*)"|'([^']*)'|([^\s)]+))\s*\)''', source):
                url = next(value for value in match if value)
                if not url.startswith('data:'):
                    raise ValueError(f'Review and allowlist new CSS asset before packaging: {url}')
    vendor_js = {name for name in files if name.startswith(VENDOR + '/')}
    if vendor_js != {name for name in inventory if name.endswith('.js')}:
        raise ValueError('Three.js inventory must exactly match the transitive module graph')
    return files | {f'{VENDOR}/LICENSE', f'{VENDOR}/manifest.json'}


def release_files(root=ROOT):
    root = Path(root).resolve()
    regular_file(root, 'assignments/manifest.json')
    errors = validate_path(root / 'assignments/manifest.json')
    if errors:
        raise ValueError('\n'.join(errors))
    if read_json(root / 'assignments/manifest.json')['units']:
        raise ValueError('Release candidate requires an empty public units list')
    files = runtime_files(root) | {'assignments/manifest.json', *NOTICES}
    for relative in files:
        regular_file(root, relative)
    return sorted(files)


def package(destination, root=ROOT):
    root = Path(root).resolve()
    # Never merge with an older package or publish a directory from inside source.
    destination = Path(destination).absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError(f'Destination must not already exist: {destination}')
    if destination.resolve().is_relative_to(root) or root.is_relative_to(destination.resolve()):
        raise ValueError('Destination must be separate from the source tree')
    files = release_files(root)
    destination.mkdir(parents=True)
    for relative in files:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / relative, target)
    return files


def archive_package(site, archive):
    """Reproducible ZIP: sorted allowlist, fixed timestamps/permissions, root index."""
    site, archive = Path(site).resolve(), Path(archive).absolute()
    if archive.suffix != '.zip':
        raise ValueError('Archive must have a .zip extension')
    if archive.exists() or archive.is_symlink():
        raise ValueError('Archive must not already exist')
    if archive.resolve().is_relative_to(site):
        raise ValueError('Archive must be outside the packaged site')
    files = release_files(site)
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as output:
        for relative in files:
            info = zipfile.ZipInfo(relative, date_time=(2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(info, (site / relative).read_bytes(), compresslevel=9)
    return checksum(archive.read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory outside this checkout')
    parser.add_argument('--zip', type=Path, help='Optional new ZIP outside the site; writes adjacent SHA256SUMS.txt')
    args = parser.parse_args()
    try:
        if args.zip:
            if args.zip.suffix != '.zip':
                raise ValueError('Archive must have a .zip extension')
            for path in (args.zip, args.zip.parent / 'SHA256SUMS.txt'):
                if path.exists() or path.is_symlink():
                    raise ValueError('ZIP and checksum outputs must not already exist')
            if args.zip.resolve().is_relative_to(ROOT) or args.zip.resolve().is_relative_to(args.output.resolve()):
                raise ValueError('ZIP must be outside source and packaged site')
        files = package(args.output)
        if args.zip:
            digest = archive_package(args.output, args.zip)
            (args.zip.parent / 'SHA256SUMS.txt').write_text(f'{digest}  {args.zip.name}\n', encoding='utf-8')
            print(f'ZIP: {args.zip.stat().st_size} bytes, SHA-256 {digest}')
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f'Packaged {len(files)} files in {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
