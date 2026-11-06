"""Native module identity, local HTTP refresh/cache and nested deployment checks.

Uses a test-only HTML harness with the packaged import map and original vendor
bytes; no renderer, routing, CDN responses or browser-cache disabling is used.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import shutil
import tempfile
import threading
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def run(site_root, output):
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((site_root / 'vendor/three/0.187.0/manifest.json').read_text())
    paths = [e['path'] for e in manifest['files'] if e['path'].endswith('.js')]
    import_map = re.search(r'<script type="importmap">(.*?)</script>', (site_root / 'index.html').read_text(), re.S)[0]
    checks, requests, statuses, cache_events, errors = [], [], [], [], []
    with tempfile.TemporaryDirectory() as temporary:
        web = Path(temporary)
        prefixes = ['', 'course/city/', '~username/engineering-city-lab/']
        for prefix in prefixes:
            target = web / prefix
            # Root and nested copies have identical original package bytes.
            shutil.copytree(site_root, target, dirs_exist_ok=True)
            harness = import_map + '''<script type="module">
              const modules = await Promise.all(PATHS.map(path => import('./vendor/three/0.187.0/' + path)));
              const a = await import('three'), b = await import('three/webgpu');
              window.vendorReady = {revision: a.REVISION, sameInstance: a === b, count: modules.length};
            </script>'''.replace('PATHS', json.dumps(paths))
            (target / 'vendor-check.html').write_text(harness, encoding='utf-8')

        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                pass

        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(web)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=shutil.which('chromium'), headless=True,
                                            args=['--no-sandbox'])
                try:
                    context = browser.new_context()
                    page = context.new_page()
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('request', lambda request: requests.append(request.url))
                    session = context.new_cdp_session(page)
                    session.send('Network.enable')
                    session.on('Network.requestServedFromCache', lambda event: cache_events.append(event))
                    session.on('Network.responseReceivedExtraInfo', lambda event: statuses.append(event['statusCode']))
                    for prefix in prefixes:
                        url = f'http://127.0.0.1:{server.server_port}/' + prefix + 'vendor-check.html'
                        page.goto(url)
                        page.wait_for_function('window.vendorReady')
                        assert page.evaluate('vendorReady') == {'revision': '187', 'sameInstance': True, 'count': 17}
                        for _ in range(2):
                            page.reload()
                            page.wait_for_function('window.vendorReady')
                            assert page.evaluate('vendorReady') == {'revision': '187', 'sameInstance': True, 'count': 17}
                        checks.append(prefix or '/')
                    assert not errors, errors
                    assert all(urlsplit(url).hostname == '127.0.0.1' for url in requests), requests
                    assert cache_events or 304 in statuses, (len(cache_events), statuses)
                    result = {'browser': browser.version, 'paths_tested': checks, 'page_errors': errors,
                              'requests': requests, 'cache_hits': len(cache_events), 'http_304': statuses.count(304)}
                    (output / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                    print(json.dumps({k: v for k, v in result.items() if k != 'requests'}, indent=2))
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('/tmp/city-vendor-cache'))
    args = parser.parse_args()
    run(args.site_root.resolve(), args.output)
