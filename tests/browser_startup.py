"""Native startup failure checks, including a module-link failure before main runs.

No CDN or provider requests are sent; intentional broken modules stay test-only.
Run: python3 tests/browser_startup.py --output /tmp/city-startup-browser
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def run(site_root, output):
    output.mkdir(parents=True, exist_ok=True)
    checks = []

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(site_root)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=shutil.which('chromium'), headless=True,
                                        args=['--no-sandbox'])
            try:
                cases = {
                    'missing-local-three': 'actual application entry',
                    'module-link': "import { StorageStructNode } from './broken-tsl.js'; window.__entryRan = true;",
                    'entry-fetch': None,
                    'init-rejection': "window.__entryRan = true; Promise.reject(new Error('test WebGPU init failure'));",
                    'after-startup': "document.getElementById('loading-status').textContent = 'Ready'; document.getElementById('loading-overlay').classList.add('hidden'); throw new Error('test later error');",
                }
                for name, source in cases.items():
                    context = browser.new_context()
                    context.route('https://**', lambda route: route.abort())
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))

                    def entry(route):
                        if name == 'missing-local-three':
                            route.continue_()
                        elif source is None:
                            route.abort()
                        else:
                            route.fulfill(body=source, content_type='application/javascript')

                    page.route('**/js/main.js', entry)
                    if name == 'missing-local-three':
                        page.route('**/vendor/three/0.187.0/build/three.tsl.js', lambda route: route.fulfill(status=404, body='Deliberately missing dependency'))
                    page.route('**/js/broken-tsl.js', lambda route: route.fulfill(
                        body='export const differentSymbol = 1;', content_type='application/javascript'))
                    page.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='networkidle')
                    if name == 'after-startup':
                        assert page.locator('#loading-overlay').evaluate('(el) => el.classList.contains("hidden")')
                        assert page.locator('#loading-status').text_content() == 'Ready', page.locator('#loading-status').text_content()
                        assert any('test later error' in error for error in errors), errors
                    else:
                        assert page.locator('#loading-overlay').is_visible()
                        assert 'Rendering dependencies or WebGPU initialization failed.' in page.locator('#loading-status').inner_text()
                        assert not page.locator('.loader-track').evaluate('(el) => el.classList.contains("is-indeterminate")')
                        if name == 'missing-local-three':
                            assert page.locator('#canvas-container canvas').count() == 0
                            page.screenshot(path=str(output / 'missing-local-three.png'))
                        elif name == 'module-link':
                            assert not page.evaluate('Boolean(window.__entryRan)')
                            assert any('StorageStructNode' in error for error in errors), errors
                            page.screenshot(path=str(output / 'module-failure.png'))
                            page.set_viewport_size({'width': 390, 'height': 844})
                            assert page.locator('#loading-status').evaluate('''el => {
                              const box = el.getBoundingClientRect();
                              return box.x >= 0 && box.right <= innerWidth;
                            }''')
                            page.screenshot(path=str(output / 'module-failure-mobile.png'))
                        elif name == 'init-rejection':
                            assert page.evaluate('window.__entryRan')
                            assert any('test WebGPU init failure' in error for error in errors), errors
                    checks.append({'case': name, 'expected_page_errors': errors})
                    context.close()
                result = {'browser': browser.version, 'checks': checks}
                (output / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
                print(json.dumps(result, indent=2))
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site-root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, default=Path('/tmp/city-startup-browser'))
    args = parser.parse_args()
    run(args.site_root.resolve(), args.output)
