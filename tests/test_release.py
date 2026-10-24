"""Release-only boundaries: exact bytes, private-file exclusion and real nested HTTP."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from tools.package_release import ROOT, package, release_files


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
                         'js/private-draft.js', 'css/backup.css', '__pycache__/cached.pyc'):
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
        self.assertEqual(len([p for p in files if p.endswith('.js')]), 40)
        self.assertIn('THIRD_PARTY_NOTICES.html', files)
        self.assertIn('LICENSE', files)

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
