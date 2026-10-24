"""Optional full-city Chromium/Playwright interaction and placement check.

Run: python3 tests/browser_education.py --output /tmp/city-education-evidence
Requires Python Playwright and Chromium (BROWSER_EXECUTABLE can select a browser).
Software Vulkan is only a test launch setting; production renderer/imports stay unchanged.
Test-only main-module instrumentation observes the real city, without a shipped debug API.
"""
import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import threading
import urllib.request
from functools import partial

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    cache = output / 'cdn-cache'
    cache.mkdir(exist_ok=True)
    errors, messages, checks = [], [], []

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass

    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=os.environ.get('BROWSER_EXECUTABLE') or shutil.which('chromium'),
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--enable-unsafe-webgpu',
                      '--enable-unsafe-swiftshader', '--use-angle=swiftshader',
                      '--enable-features=Vulkan', '--use-vulkan=swiftshader'])
            context = browser.new_context(viewport={'width': 1280, 'height': 800})
            # Deliberately invalid saved travel state; the actual app must ignore it.
            context.add_init_script("""localStorage.setItem('nyc-player-state', JSON.stringify({
              version:1, activeMode:'helicopter', entities:{car:{x:900,y:20,z:900,heading:3},
              person:{x:800,y:0,z:800,heading:2},cyclist:{x:700,y:0,z:700,heading:1}}}));""")
            page = context.new_page()
            page.set_default_timeout(120000)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: messages.append({'type': m.type, 'text': m.text})
                    if m.type in ('warning', 'error') or m.text.startswith('[init]') else None)

            # In Cloud, Chromium does not inherit Python's proxy CA trust. Fetch the exact
            # original CDN URLs through urllib with normal TLS verification, then fulfill
            # them unchanged. Never disable TLS verification or replace dependency versions.
            if os.environ.get('HTTPS_PROXY'):
                def cdn(route):
                    url = route.request.url
                    saved = cache / hashlib.sha256(url.encode()).hexdigest()
                    if not saved.exists():
                        with urllib.request.urlopen(url, timeout=60) as response:
                            saved.write_bytes(response.read())
                    route.fulfill(body=saved.read_bytes(), content_type='application/javascript',
                                  headers={'access-control-allow-origin': '*'})
                page.route('https://cdn.jsdelivr.net/**', cdn)
                # External font hosts are outside this environment's allowed destinations.
                page.route('https://fonts.googleapis.com/**', lambda r: r.abort())
                page.route('https://fonts.gstatic.com/**', lambda r: r.abort())

            def observe_main(route):
                source = (ROOT / 'js/main.js').read_text()
                needle = '  let warmedUp = false;'
                assert source.count(needle) == 1
                observe = """  window.__city = {controllerManager, cameraSystem, mapSystem,
                  trafficSystem, highwayTraffic, scene, renderer, streetDetails, allColliders,
                  educationUI, demoSession, get elapsed(){return elapsed;},
                  starts: Object.fromEntries(Object.entries(controllerManager.entities).map(([k,e])=>
                    [k,{x:e.position.x,y:e.position.y,z:e.position.z,heading:e.heading}]))};
                renderer.backend.device.lost.then(info => window.__gpuLost = info.message);
                // Deterministic test-only frames keep software GPU work bounded. Each
                // step runs the actual production callback, physics and render pipeline.
                renderer.setAnimationLoop = update => {
                  window.__step = async () => {
                    update(lastTime + 16);
                    await renderer.backend.device.queue.onSubmittedWorkDone();
                  };
                  window.__step().then(() => window.__step()).then(() => window.__testReady = true);
                };
"""
                route.fulfill(body=source.replace(needle, observe + needle), content_type='application/javascript')

            page.route('**/js/main.js', observe_main)
            page.goto(f'http://127.0.0.1:{server.server_port}/', wait_until='domcontentloaded', timeout=120000)
            try:
                page.locator('#loading-overlay.hidden').wait_for(state='attached', timeout=600000)
                page.wait_for_function('window.__testReady', timeout=600000)
                assert not page.evaluate('window.__gpuLost'), 'Software WebGPU device lost; visual verification unavailable'
                assert not errors, errors
                starts = page.evaluate('__city.starts')
                assert starts['car'] == {'x': 3.6, 'y': 0, 'z': 410.6, 'heading': 0}, starts
                assert starts['person']['x'] == -11.6 and starts['cyclist']['x'] == 5.2 and starts['helicopter']['y'] == 96
                checks.append('fixed startup ignores stale positions for all four independent modes')
                print('Browser: city rendered; checking interactions', flush=True)
                page.screenshot(path=str(output / 'start.png'), timeout=180000)

                page.keyboard.down('x')
                page.keyboard.down('x')
                page.wait_for_function('document.getElementById("education-dialog").open')
                assert page.locator('#education-title').inner_text().startswith('Q02')
                paused = page.evaluate('({time:__city.elapsed,car:__city.controllerManager.entities.car.position.toArray(),camera:__city.cameraSystem.activePresetId})')
                page.keyboard.press('4')
                page.keyboard.press('m')
                page.keyboard.press('v')
                page.keyboard.down('w')
                page.evaluate('async () => {await __step(); await __step();}')
                assert page.evaluate('__city.elapsed') == paused['time']
                assert page.evaluate('__city.controllerManager.entities.car.position.toArray()') == paused['car']
                assert page.evaluate('__city.controllerManager.activeMode') == 'car'
                assert page.evaluate('__city.cameraSystem.activePresetId') == paused['camera']
                assert not page.evaluate('__city.mapSystem.isFullMapOpen')
                page.keyboard.press('Tab')
                assert page.evaluate('document.getElementById("education-dialog").contains(document.activeElement)')
                page.locator('input[name="demo-answer"][value="A"]').check()
                page.get_by_role('button', name='Submit Answer', exact=True).click()
                assert 'Incorrect' in page.locator('#education-feedback').inner_text()
                assert page.evaluate('__city.demoSession.count') == 0
                page.locator('input[name="demo-answer"][value="B"]').check()
                page.get_by_role('button', name='Submit Answer', exact=True).click()
                assert page.evaluate('__city.demoSession.count') == 1
                page.screenshot(path=str(output / 'question.png'), timeout=180000)
                page.keyboard.press('Escape')
                assert not page.locator('#education-dialog').evaluate('(d)=>d.open')
                page.keyboard.down('x')
                assert not page.locator('#education-dialog').evaluate('(d)=>d.open'), 'held X must not reopen'
                page.keyboard.up('x')
                # A key held through close cannot start moving on a repeated keydown.
                page.keyboard.down('w')
                assert not page.evaluate('__city.controllerManager.keys.forward')
                page.keyboard.up('w')
                page.keyboard.press('x')
                assert 'Already completed' in page.locator('#education-feedback').inner_text()
                page.locator('input[name="demo-answer"][value="A"]').check()
                page.get_by_role('button', name='Submit Answer', exact=True).click()
                assert page.evaluate('__city.demoSession.hasPassed("Q02")')
                page.get_by_role('button', name='Close', exact=True).click()
                checks.append('real X/radio/submit/retry/reopen, focus trap, shortcut lock, pause and held-key cleanup')
                print('Browser: answer/retry/dialog checks passed', flush=True)

                # Typing and modified/repeated X must not open a question.
                page.evaluate("""() => {const t=document.createElement('textarea');t.id='test-typing';document.body.append(t);t.focus();}""")
                page.keyboard.press('x')
                assert not page.locator('#education-dialog').evaluate('(d)=>d.open')
                page.evaluate('document.getElementById("test-typing").remove()')
                page.keyboard.press('Control+x')
                assert not page.locator('#education-dialog').evaluate('(d)=>d.open')
                page.keyboard.press('4')
                page.keyboard.press('x')
                assert not page.locator('#education-dialog').evaluate('(d)=>d.open')
                page.keyboard.press('2')
                assert page.evaluate('__city.controllerManager.entities.car.position.toArray()') == paused['car']
                checks.append('typing/modifier guards, helicopter disabled and independent mode locations')

                # Visit actual fixed sites using the existing safe teleport method on foot.
                page.keyboard.press('1')
                sites = page.evaluate('''() => __city.scene.getObjectByName('EducationDemoTerminals').children.map(t =>
                  ({id:t.name.slice(-3),x:t.position.x,z:t.position.z}))''')
                assert len(sites) == 5
                answers = {'Q01': 'A', 'Q02': 'B', 'Q03': 'C', 'Q04': 'A', 'Q05': 'B'}
                for site in sites:
                    page.evaluate('''t => {const c=__city.controllerManager;c.teleportActiveTo(t.x,t.z-2,0);
                      __city.cameraSystem.resetForTeleport();}''', site)
                    page.evaluate('async () => {await __step();}')
                    page.wait_for_function('id => document.getElementById("education-prompt").textContent.includes(id)', arg=site['id'])
                    page.screenshot(path=str(output / (site['id'] + '.png')), timeout=180000)
                    page.keyboard.press('x')
                    assert page.locator('#education-title').inner_text().startswith(site['id'])
                    page.locator(f'input[name="demo-answer"][value="{answers[site["id"]]}"]').check()
                    page.get_by_role('button', name='Submit Answer', exact=True).click()
                    page.get_by_role('button', name='Close', exact=True).click()
                assert page.evaluate('__city.demoSession.count') == 5
                assert page.locator('#education-completion').is_visible()
                page.keyboard.press('m')
                page.wait_for_function('__city.mapSystem.isFullMapOpen')
                page.locator('#fullmap-canvas').click(position={'x': 550, 'y': 400})
                assert page.evaluate('__city.demoSession.count') == 5
                page.keyboard.press('Escape')
                page.keyboard.press('2')
                page.keyboard.down('w')
                page.evaluate('''async () => {
                  for (let i=0;i<12 && __city.controllerManager.entities.car.speed<=0.5;i++) await __step();
                }''')
                assert page.evaluate('__city.controllerManager.entities.car.speed') > 0.5
                page.keyboard.up('w')
                page.keyboard.press('x')
                assert not page.locator('#education-dialog').evaluate('(d)=>d.open'), 'moving car must not answer'
                page.locator('[popovertarget="teleport-popover"]').click()
                page.locator('[data-teleport="empire"]').click()
                assert page.evaluate('''() => {const c=__city;const p=c.controllerManager.getActiveEntity().position;
                  return c.mapSystem.waypoint.x===p.x && c.mapSystem.waypoint.z===p.z;}''')
                page.keyboard.press('3')
                page.evaluate('''() => __city.controllerManager.teleportActiveTo(11, 440.6, 0)''')
                page.keyboard.press('x')
                assert page.locator('#education-title').inner_text().startswith('Q04')
                page.get_by_role('button', name='Close', exact=True).click()
                assert page.evaluate('__city.demoSession.count') == 5
                checks.append('all five rendered sites reachable, demo completion, map/preset teleports, driving, moving-car guard and bicycle answering preserve progress')
                assert not errors, errors
                assert not page.evaluate('window.__gpuLost'), 'WebGPU device was lost during the check'
                print(json.dumps({'checks': checks, 'starts': starts, 'sites': sites, 'browser': browser.version}, indent=2), flush=True)
            finally:
                (output / 'results.json').write_text(json.dumps({'checks': checks, 'page_errors': errors, 'console': messages}, indent=2))
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('/tmp/city-education-evidence'))
    run(parser.parse_args().output)
