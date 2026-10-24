"""Optional native-browser static package checks; no renderer or provider contact.

Complements, rather than replaces, browser_education.py --workflow --site-root.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
import threading

from playwright.sync_api import sync_playwright


def run(site_root, output):
    output.mkdir(parents=True, exist_ok=True)
    checks = []
    with tempfile.TemporaryDirectory() as temporary:
        web = Path(temporary)
        prefix = '/~username/engineering-city-lab/'
        shutil.copytree(site_root, web / prefix.lstrip('/'))
        class Quiet(SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=str(web)))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(executable_path=shutil.which('chromium'), headless=True, args=['--no-sandbox'])
                try:
                    context = browser.new_context(viewport={'width': 1280, 'height': 800})
                    # This checks actual static HTML/CSS/native modules without running a
                    # second renderer. No remote font, CDN or fixture URL is contacted.
                    context.route('https://**', lambda route: route.abort())
                    context.route('**/js/main.js', lambda route: route.fulfill(body='', content_type='application/javascript'))
                    page = context.new_page()
                    base = f'http://127.0.0.1:{server.server_port}' + prefix
                    assert page.goto(base.rstrip('/')).status == 200
                    assert page.url == base
                    assert page.reload().status == 200
                    assert page.goto(base + 'index.html').status == 200
                    # Real native ES-module loading from the nested package; no app code edits.
                    result = page.evaluate('''async () => {
                      const {createAssignmentLoader}=await import('./js/assignment-loader.js');
                      const loader=createAssignmentLoader();
                      return await loader.refresh();
                    }''')
                    assert result['units'] == [], result
                    checks.append('native module/manifest loading, directory redirect, direct index navigation and refresh at a real tilde-prefixed path')
                    page.locator('#loading-overlay').evaluate('(element)=>element.classList.add("hidden")')
                    attribution = page.locator('#data-attribution')
                    for width, height in ((1280, 800), (390, 844)):
                        page.set_viewport_size({'width': width, 'height': height})
                        for clean, full_map in ((False, False), (True, False), (False, True), (True, True)):
                            page.evaluate('''({clean,full_map})=>{
                              document.body.classList.toggle('hud-minimized',clean);
                              document.querySelector('#fullmap-modal').classList.toggle('hidden',!full_map);
                            }''', {'clean': clean, 'full_map': full_map})
                            assert attribution.is_visible()
                            assert attribution.evaluate('''element=>{
                              const box=element.getBoundingClientRect();
                              return box.x>=0 && box.y>=0 && box.right<=innerWidth && box.bottom<=innerHeight &&
                                element.contains(document.elementFromPoint(box.x+20,box.y+box.height/2));
                            }''')
                    checks.append('visible readable attribution remains within desktop/mobile viewport above city, clean view and full map')
                    link = attribution.get_by_role('link', name='Licenses & data', exact=True)
                    with context.expect_page() as event:
                        link.focus()
                        page.keyboard.press('Enter')
                    popup = event.value
                    popup.wait_for_load_state('domcontentloaded')
                    assert popup.url == base + 'THIRD_PARTY_NOTICES.html'
                    assert popup.evaluate('window.opener===null')
                    assert popup.get_by_role('heading', name='Geographic database and OpenStreetMap').is_visible()
                    assert popup.get_by_role('link', name='js/nyc-geodata.js', exact=True).get_attribute('href') == './js/nyc-geodata.js'
                    popup.close()
                    page.screenshot(path=str(output / 'attribution-mobile-map.png'))
                    checks.append('native license keyboard link opens packaged notices with no opener and a relative machine-readable geographic database link')
                    result = {'checks': checks, 'browser': browser.version}
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
    parser.add_argument('--site-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('/tmp/city-release-browser'))
    args = parser.parse_args()
    run(args.site_root.resolve(), args.output)
