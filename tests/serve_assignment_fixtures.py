"""Loopback-only manual test server. Never changes the empty public manifest.

Run: py -3 tests/serve_assignment_fixtures.py --version 2 --prefix course/city
Only /assignments/ routes are mapped to synthetic test files in memory. This is
test tooling, not a public unit publisher or production backend.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def serve(version=2, port=8000, prefix='', review_browser=None):
    base = '/' + prefix.strip('/') + '/' if prefix.strip('/') else '/'
    fixture_dir = ROOT/'tests/fixtures'/('v2' if version == 2 else '')

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            path = urlsplit(self.path).path
            if not path.startswith(base):
                self.send_error(404); return
            relative = path[len(base):]
            if relative == 'assignments/manifest.json':
                data = (fixture_dir/'manifest.json').read_bytes()
            elif relative in ('assignments/S01.json','assignments/S02.json'):
                data = (fixture_dir/relative.split('/')[-1]).read_bytes()
            elif relative.startswith('assignments/'):
                self.send_error(404); return
            else:
                return super().do_GET()
            self.send_response(200)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(data)))
            self.end_headers(); self.wfile.write(data)

        def translate_path(self, path):
            return super().translate_path('/' + path[len(base):])

    server = ThreadingHTTPServer(('127.0.0.1',port),partial(Handler,directory=str(ROOT)))
    url = f'http://127.0.0.1:{server.server_address[1]}{base}'
    print(f'TEST ONLY v{version}: {url}',flush=True)
    if review_browser:
        # Optional physical review: native browser/production frames, with fixture
        # provider requests intercepted before even the first new-tab navigation.
        from playwright.sync_api import sync_playwright, Error
        from browser_learning_workflow import mock_external_links
        thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
        try:
            with sync_playwright() as p:
                browser=p.chromium.launch(headless=False,channel=review_browser)
                try:
                    context=browser.new_context(viewport={'width':1280,'height':800})
                    mock_external_links(context,lambda target,headers: print('MOCK external action: '+target,flush=True))
                    page=context.new_page(); page.goto(url,wait_until='domcontentloaded')
                    print('Manual review browser ready. External fixture tabs are mocked; close the city tab to stop.',flush=True)
                    while not page.is_closed():
                        try: page.wait_for_timeout(1000)
                        except Error:
                            if not page.is_closed(): raise
                finally: browser.close()
        except KeyboardInterrupt: pass
        finally:
            server.shutdown(); server.server_close(); thread.join()
        return
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version',type=int,choices=(1,2),default=2)
    parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--prefix',default='')
    parser.add_argument('--review-browser',choices=('chrome','msedge'),help='Optional headed physical review with all fixture video/Form navigations mocked; requires Playwright and the selected installed browser')
    args=parser.parse_args()
    serve(args.version,args.port,args.prefix,args.review_browser)
