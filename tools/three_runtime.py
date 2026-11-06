"""Pinned Three.js provenance and the native module syntax used by this runtime.

No network access. Future upstream syntax/assets need a reviewed graph update.
"""
import hashlib
import json
from pathlib import PurePosixPath
import re

VERSION = '0.187.0'
VENDOR = f'vendor/three/{VERSION}'
SOURCE = {
    'name': 'three', 'version': VERSION,
    'metadata': f'https://registry.npmjs.org/three/{VERSION}',
    'tarball': f'https://registry.npmjs.org/three/-/three-{VERSION}.tgz',
    'integrity': 'sha512-Qiu7R+Cmh8CstZsY1uJOSWnVlfo7ZtNLV7mF8Jltk3LB3AtDu9cRZlcnRKkAk8Y4z6KKw35z7Y7Urd7jWY8etA==',
    'sha256': 'ff540832ded0cfe919764d24a3d88f3e2a05f23303f876423e4f893841e90728',
}
IMPORTS = {
    'three': f'./{VENDOR}/build/three.webgpu.js',
    'three/webgpu': f'./{VENDOR}/build/three.webgpu.js',
    'three/tsl': f'./{VENDOR}/build/three.tsl.js',
    'three/addons/': f'./{VENDOR}/examples/jsm/',
}
# Anchored declarations avoid documentation examples ("* import ...") and
# strings containing prose such as "from ..." in the original Three.js builds.
STATIC_IMPORT = re.compile(r'''(?m)(?:^|[;\n])\s*(?:import\s*(?![.\w$(])(?:[^;]*?\bfrom\s*)?|export\s*(?:\*\s*(?:as\s+\w+\s*)?|\{[^}]*\}\s*)from\s*)['"]([^'"\n]+)['"]''')
DYNAMIC_IMPORT = re.compile(r'''\bimport\s*\(\s*(['"])([^'"\n]+)\1\s*\)''')


def module_specifiers(source):
    dynamic = list(DYNAMIC_IMPORT.finditer(source))
    if len(dynamic) != len(re.findall(r'\bimport\s*\(', source)):
        raise ValueError('Computed or unsupported dynamic import requires explicit review')
    return sorted(set(STATIC_IMPORT.findall(source)) | {m[2] for m in dynamic})


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def vendor_inventory(root, regular_file):
    manifest = json.loads(regular_file(root, f'{VENDOR}/manifest.json').read_text(encoding='utf-8'))
    if set(manifest) != {'schemaVersion', 'source', 'files'} or manifest['schemaVersion'] != 1 or manifest['source'] != SOURCE:
        raise ValueError('Unexpected Three.js version or package provenance')
    files = {}
    for entry in manifest['files']:
        if set(entry) != {'path', 'bytes', 'sha256'}:
            raise ValueError('Invalid Three.js inventory entry')
        rel = entry['path']
        if not isinstance(rel, str) or not rel or '..' in PurePosixPath(rel).parts or '\\' in rel or PurePosixPath(rel).is_absolute():
            raise ValueError('Unsafe vendor inventory path')
        if rel != 'LICENSE' and not (rel.startswith(('build/', 'examples/jsm/')) and rel.endswith('.js')):
            raise ValueError('Unreviewed vendor file type')
        name = f'{VENDOR}/{rel}'
        if name in files:
            raise ValueError('Duplicate vendor inventory path')
        data = regular_file(root, name).read_bytes()
        if len(data) != entry['bytes'] or checksum(data) != entry['sha256']:
            raise ValueError(f'Three.js checksum mismatch: {name}')
        files[name] = entry
    if f'{VENDOR}/LICENSE' not in files:
        raise ValueError('Three.js MIT license is required')
    return files
