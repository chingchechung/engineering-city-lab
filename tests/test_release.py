"""Release-only boundaries: exact bytes, private-file exclusion and real nested HTTP."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
import zipfile
from urllib.error import HTTPError
from urllib.request import urlopen

from tools.package_release import ROOT, package, release_files, archive_package
from tools.three_runtime import VENDOR, checksum, module_specifiers
from tools.vendor_three import vendor


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)

    def copy_source(self):
        source = self.base / 'source'
        for relative in release_files():
            target = source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        return source

    def test_reproducible_bytes_and_only_runtime_plus_notices(self):
        source = self.copy_source()
        # Files and directories beside the runtime graph must never leak by a glob.
        for relative in ('teacher_data/private.json', 'assignments/S01.json',
                         'tests/fixtures/S01.json', '.git/config', '.env',
                         'js/private-draft.js', 'css/backup.css', '__pycache__/cached.pyc',
                         'vendor/three/private.js', 'vendor/three/0.187.0/examples/unrelated.js'):
            path = source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('DO NOT PUBLISH', encoding='utf-8')
        first, second = self.base / 'first', self.base / 'second'
        files = package(first, source)
        self.assertEqual(files, package(second, source))
        self.assertEqual(set(files), {p.relative_to(first).as_posix() for p in first.rglob('*') if p.is_file()})
        for relative in files:
            self.assertEqual((first / relative).read_bytes(), (source / relative).read_bytes())
            self.assertEqual((first / relative).read_bytes(), (second / relative).read_bytes())
        self.assertEqual({p.name for p in (first / 'assignments').iterdir()}, {'manifest.json'})
        self.assertEqual(json.loads((first / 'assignments/manifest.json').read_text())['units'], [])
        self.assertEqual(len([p for p in files if p.startswith('js/') and p.endswith('.js')]), 40)
        self.assertEqual(len([p for p in files if p.startswith('vendor/') and p.endswith('.js')]), 17)
        self.assertEqual(len(files), 66)
        self.assertIn('vendor/three/0.187.0/LICENSE', files)
        self.assertIn('vendor/three/0.187.0/manifest.json', files)
        self.assertIn('THIRD_PARTY_NOTICES.html', files)
        self.assertIn('LICENSE', files)
        archive_one, archive_two = self.base / 'one.zip', self.base / 'two.zip'
        digest = archive_package(first, archive_one)
        self.assertEqual(digest, archive_package(second, archive_two))
        self.assertEqual(archive_one.read_bytes(), archive_two.read_bytes())
        with zipfile.ZipFile(archive_one) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(archive.namelist(), files)
            for relative in files:
                self.assertEqual(archive.read(relative), (source / relative).read_bytes())
        with self.assertRaisesRegex(ValueError, 'already exist'):
            archive_package(first, archive_one)

    def test_refuses_existing_or_source_destination_without_deleting(self):
        source = self.copy_source()
        existing = self.base / 'existing'
        existing.mkdir()
        marker = existing / 'keep.txt'
        marker.write_text('keep')
        for destination in (existing, source / 'release', source.parent):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                package(destination, source)
        self.assertEqual(marker.read_text(), 'keep')

    def test_refuses_missing_or_root_relative_runtime_inputs(self):
        source = self.copy_source()
        (source / 'js/main.js').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            package(self.base / 'missing', source)
        self.assertFalse((self.base / 'missing').exists())
        shutil.copyfile(ROOT / 'js/main.js', source / 'js/main.js')
        html = source / 'index.html'
        html.write_text(html.read_text().replace('./js/main.js', '/js/main.js'))
        with self.assertRaisesRegex(ValueError, 'relative'):
            package(self.base / 'absolute', source)

    def test_refuses_published_or_malformed_release_manifest(self):
        source = self.copy_source()
        manifest = source / 'assignments/manifest.json'
        for path in ('manifest.json', 'S01.json', 'S02.json'):
            shutil.copyfile(ROOT / 'tests/fixtures' / path, source / 'assignments' / path)
        with self.assertRaisesRegex(ValueError, 'empty public'):
            package(self.base / 'published', source)
        manifest.write_text('{ broken')
        with self.assertRaisesRegex(ValueError, 'cannot read UTF-8 JSON'):
            package(self.base / 'invalid', source)

    def test_refuses_file_and_directory_symlinks(self):
        source = self.copy_source()
        main = source / 'js/main.js'
        main.unlink()
        main.symlink_to(ROOT / 'js/main.js')
        with self.assertRaisesRegex(ValueError, 'Symlinks'):
            package(self.base / 'file-link', source)
        main.unlink()
        shutil.copyfile(ROOT / 'js/main.js', main)
        shutil.move(source / 'assignments', self.base / 'linked-assignments')
        (source / 'assignments').symlink_to(self.base / 'linked-assignments', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlinks'):
            package(self.base / 'directory-link', source)

    def test_vendor_missing_or_modified_bytes_are_rejected_before_output(self):
        source = self.copy_source()
        path = source / VENDOR / 'build/three.core.js'
        original = path.read_bytes()
        path.write_bytes(original + b'\n// modified')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            package(self.base / 'modified', source)
        self.assertFalse((self.base / 'modified').exists())
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing'):
            package(self.base / 'missing-vendor', source)

    def test_vendor_file_and_parent_symlinks_are_rejected(self):
        source = self.copy_source()
        path = source / VENDOR / 'build/three.core.js'
        path.unlink()
        path.symlink_to(ROOT / VENDOR / 'build/three.core.js')
        with self.assertRaisesRegex(ValueError, 'Symlinks'):
            package(self.base / 'vendor-link', source)
        path.unlink()
        shutil.copyfile(ROOT / VENDOR / 'build/three.core.js', path)
        shutil.move(source / VENDOR, self.base / 'linked-vendor')
        (source / VENDOR).symlink_to(self.base / 'linked-vendor', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlinks'):
            package(self.base / 'vendor-parent-link', source)

    def test_rejects_external_or_mixed_import_maps_and_remote_scripts(self):
        source = self.copy_source()
        html = source / 'index.html'
        original = html.read_text()
        changes = [
            original.replace('./vendor/three/0.187.0/build/three.tsl.js', './vendor/three/0.186.0/build/three.tsl.js'),
            original.replace('./vendor/three/0.187.0/', 'https://cdn.jsdelivr.net/npm/three@0.187.0/'),
            original.replace('./js/main.js', 'https://other-cdn.example/main.js'),
        ]
        for index, content in enumerate(changes):
            html.write_text(content)
            with self.subTest(index=index), self.assertRaises(ValueError):
                package(self.base / f'bad-map-{index}', source)

    def test_rejects_external_dynamic_imports_and_first_party_traversal(self):
        source = self.copy_source()
        main = source / 'js/main.js'
        original = main.read_text()
        for index, statement in enumerate(["import('https://example.test/module.js');", "import '../outside.js';", 'import(variable);']):
            main.write_text(original + '\n' + statement)
            with self.subTest(statement=statement), self.assertRaises(ValueError):
                package(self.base / f'bad-import-{index}', source)

    def test_vendor_graph_cannot_escape_its_version_directory(self):
        source = self.copy_source()
        rel = 'examples/jsm/tsl/utils/RNoise.js'
        path = source / VENDOR / rel
        data = path.read_bytes() + b"\nimport '../../../../../../js/main.js';\n"
        path.write_bytes(data)
        manifest_path = source / VENDOR / 'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        entry = next(e for e in manifest['files'] if e['path'] == rel)
        entry.update(bytes=len(data), sha256=checksum(data))
        manifest_path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            package(self.base / 'vendor-escape', source)

    def test_vendor_inventory_requires_license_exact_closure_and_provenance(self):
        source = self.copy_source()
        path = source / VENDOR / 'manifest.json'
        original = json.loads(path.read_text())
        missing_license = json.loads(json.dumps(original))
        missing_license['files'] = [e for e in missing_license['files'] if e['path'] != 'LICENSE']
        wrong_version = json.loads(json.dumps(original))
        wrong_version['source']['version'] = '0.186.0'
        extra = json.loads(json.dumps(original))
        data = b'export const unrelated = 1;'
        extra_path = source / VENDOR / 'build/unrelated.js'
        extra_path.write_bytes(data)
        extra['files'].append({'path': 'build/unrelated.js', 'bytes': len(data), 'sha256': checksum(data)})
        unsafe = json.loads(json.dumps(original))
        unsafe['files'][0]['path'] = '../LICENSE'
        for index, manifest in enumerate([missing_license, wrong_version, extra, unsafe]):
            path.write_text(json.dumps(manifest))
            with self.subTest(index=index), self.assertRaises(ValueError):
                package(self.base / f'inventory-{index}', source)

    def test_import_scanner_and_tarball_integrity_fail_closed(self):
        source = """import{a}from './a.js'; import './b.js';
export {c} from '../c.js';
export * from './d.js';
const lazy = import('./lazy.js');
/**
 * import {fake} from 'https://example.test/documentation-only.js';
 */
"""
        self.assertEqual(module_specifiers(source), ['../c.js', './a.js', './b.js', './d.js', './lazy.js'])
        with self.assertRaisesRegex(ValueError, 'Computed'):
            module_specifiers('import(path)')
        tarball = self.base / 'tampered.tgz'
        tarball.write_bytes(b'not the official package')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            vendor(tarball, self.base / 'destination')
        self.assertFalse((self.base / 'destination').exists())

    def test_packaged_nested_http_mime_redirect_refresh_utf8_and_missing_files(self):
        web = self.base / 'web'
        prefix = '/~username/engineering-city-lab/'
        target = web / prefix.lstrip('/')
        files = package(target)
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(web)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f'http://127.0.0.1:{server.server_port}' + prefix
            for relative in files:
                with self.subTest(file=relative), urlopen(base + relative, timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(response.read(), (target / relative).read_bytes())
                    if relative.endswith('.js'):
                        self.assertIn(response.headers.get_content_type(), ('text/javascript', 'application/javascript'))
                    if relative.endswith('.json'):
                        self.assertEqual(response.headers.get_content_type(), 'application/json')
                    if relative.endswith('.css'):
                        self.assertEqual(response.headers.get_content_type(), 'text/css')
            for url in (base.rstrip('/'), base, base + 'index.html', base):
                with urlopen(url, timeout=10) as response:
                    self.assertEqual(response.read(), (target / 'index.html').read_bytes())
                    self.assertIn('charset="utf-8"', (target / 'index.html').read_text().lower())
            for missing in ('assignments/S01.json', 'assignments/S12.json', 'js/missing.js', 'tests/fixtures/S01.json', '.git/config'):
                with self.subTest(missing=missing), self.assertRaises(HTTPError) as error:
                    urlopen(base + missing, timeout=10)
                self.assertEqual(error.exception.code, 404)
            # Temporary HTTP-only authoring simulation; never writes to the RC or repository.
            # Check both contracts and Chinese UTF-8 unit bytes at the exact nested unit URL.
            for version in ('', 'v2'):
                fixture = ROOT / 'tests/fixtures' / version
                for relative in ('manifest.json', 'S01.json', 'S02.json'):
                    shutil.copyfile(fixture / relative, target / 'assignments' / relative)
                with urlopen(base + 'assignments/S01.json', timeout=10) as response:
                    unit = json.loads(response.read().decode('utf-8'))
                    self.assertEqual(unit, json.loads((fixture / 'S01.json').read_text(encoding='utf-8')))
                    self.assertTrue(any(ord(c) > 127 for c in json.dumps(unit, ensure_ascii=False)))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
