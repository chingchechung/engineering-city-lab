"""Reproduce the exact runtime subset from a separately downloaded official tarball.

No fetching, package install scripts, source transformations or tar extraction.
Run: python3 tools/vendor_three.py --tarball /tmp/three-0.187.0.tgz
The versioned destination must not already exist.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import tarfile

if __package__:
    from .three_runtime import IMPORTS, SOURCE, VENDOR, checksum, module_specifiers
else:
    from three_runtime import IMPORTS, SOURCE, VENDOR, checksum, module_specifiers

ROOT = Path(__file__).resolve().parents[1]


def resolve(specifier, parent):
    if specifier in IMPORTS:
        return IMPORTS[specifier].removeprefix(f'./{VENDOR}/')
    if specifier.startswith('three/addons/'):
        return 'examples/jsm/' + specifier.removeprefix('three/addons/')
    if specifier.startswith('.'):
        rel = posixpath.normpath(posixpath.join(posixpath.dirname(parent), specifier))
        if not rel.startswith('../') and rel.endswith('.js'):
            return rel
    raise ValueError(f'Unreviewed vendor import: {specifier}')


def vendor(tarball, root=ROOT):
    data = Path(tarball).read_bytes()
    integrity = 'sha512-' + base64.b64encode(hashlib.sha512(data).digest()).decode()
    if checksum(data) != SOURCE['sha256'] or integrity != SOURCE['integrity']:
        raise ValueError('Official Three.js tarball integrity mismatch')
    destination = root / VENDOR
    if destination.exists() or any(p.is_symlink() for p in [destination, *destination.parents]):
        raise ValueError('Vendor destination must be new and free of symlinks')
    pending = []
    for path in sorted((root / 'js').glob('*.js')):
        pending.extend(resolve(spec, '') for spec in module_specifiers(path.read_text(encoding='utf-8')) if spec.startswith('three'))
    files = {}
    with tarfile.open(tarball, 'r:gz') as archive:
        def read(rel):
            member = archive.getmember('package/' + rel)
            if not member.isfile():
                raise ValueError(f'Expected regular package file: {rel}')
            return archive.extractfile(member).read()
        package = json.loads(read('package.json'))
        if package['name'] != 'three' or package['version'] != SOURCE['version']:
            raise ValueError('Unexpected npm package')
        while pending:
            rel = pending.pop()
            if rel in files:
                continue
            if ('..' in PurePosixPath(rel).parts or '\\' in rel or
                    not rel.startswith(('build/', 'examples/jsm/')) or not rel.endswith('.js')):
                raise ValueError(f'Unsafe or unreviewed package path: {rel}')
            content = read(rel)
            if re.search(r'''new\s+URL\s*\(\s*['"]''', content.decode('utf-8')):
                raise ValueError('New vendor URL asset requires explicit packaging review')
            files[rel] = content
            pending.extend(resolve(spec, rel) for spec in module_specifiers(content.decode('utf-8')))
        files['LICENSE'] = read('LICENSE')
    inventory = [{'path': rel, 'bytes': len(content), 'sha256': checksum(content)} for rel, content in sorted(files.items())]
    # Validate the whole graph before writing anything. Never mutate upstream bytes.
    destination.mkdir(parents=True)
    for rel, content in sorted(files.items()):
        path = destination / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    (destination / 'manifest.json').write_text(json.dumps({'schemaVersion': 1, 'source': SOURCE, 'files': inventory}, indent=2) + '\n', encoding='utf-8', newline='\n')
    return inventory


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tarball', type=Path, required=True)
    args = parser.parse_args()
    print(f'Vendored {len(vendor(args.tarball))} original files plus provenance manifest')
