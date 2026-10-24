"""Create a new static-only release directory; no archives, uploads or publication.

Uses only the standard library and the existing read-only assignment validator.
The copy allowlist follows the reviewed local module/style graph, not directories.
"""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import sys
from urllib.parse import urlsplit

if __package__:
    from .assignment_data import read_json
    from .validate_assignments import validate_path
else:
    from assignment_data import read_json
    from validate_assignments import validate_path

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

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script' and 'src' in attrs:
            self.urls.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ('stylesheet', 'modulepreload', 'icon'):
            self.urls.append(attrs['href'])


def runtime_files(root):
    """Return only local HTML module/style dependencies, rejecting unsafe paths."""
    parser = RuntimeLinks()
    parser.feed(regular_file(root, 'index.html').read_text(encoding='utf-8'))
    files, pending = {'index.html'}, [(Path('.'), url) for url in parser.urls]
    while pending:
        parent, url = pending.pop()
        parsed = urlsplit(url)
        if parsed.scheme in ('https', 'data'):
            continue
        if parsed.scheme or parsed.netloc or not parsed.path.startswith('./') and parent == Path('.'):
            raise ValueError(f'Runtime URL must be HTTPS, data or relative: {url}')
        relative = (parent / parsed.path).as_posix()
        if '..' in Path(relative).parts or not relative.startswith(('js/', 'css/')):
            raise ValueError(f'Unsafe runtime input: {url}')
        if Path(relative).suffix not in ('.js', '.css'):
            raise ValueError(f'Unreviewed runtime asset type: {url}')
        if relative in files:
            continue
        source = regular_file(root, relative).read_text(encoding='utf-8')
        files.add(relative)
        if relative.endswith('.js'):
            imports = re.findall(r'''(?:\bfrom\s*|\bimport\s*)['"](\.[^'"]+)['"]''', source)
            pending.extend((Path(relative).parent, url) for url in imports)
        else:
            # Consume a complete quoted data URL so embedded SVG url(...) is not
            # mistaken for an additional local stylesheet dependency.
            for match in re.findall(r'''url\(\s*(?:"([^"]*)"|'([^']*)'|([^\s)]+))\s*\)''', source):
                url = next(value for value in match if value)
                if not url.startswith('data:'):
                    raise ValueError(f'Review and allowlist new CSS asset before packaging: {url}')
    return files


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New directory outside this checkout')
    args = parser.parse_args()
    try:
        files = package(args.output)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    print(f'Packaged {len(files)} files in {args.output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
