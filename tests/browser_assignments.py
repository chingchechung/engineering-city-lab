"""Phase 2 real-city checks, invoked by browser_education.py --assignments.

Only this test routes synthetic fixture bytes to assignment requests. The
committed public manifest stays empty; the production loader/UI are unchanged.
"""
import json
from pathlib import Path
from playwright.sync_api import Error

ROOT = Path(__file__).resolve().parents[1]


def check_assignments(page, output, checks, base_path, workflow=False):
    selector = page.locator('#assignment-dialog')
    status = page.locator('#assignment-status')
    positions = 'Object.fromEntries(Object.entries(__city.controllerManager.entities).map(([k,e])=>[k,e.position.toArray()]))'
    colors = '__city.scene.getObjectByName("EducationDemoTerminals").children.map(t=>t.children[1].material.color.getHex())'
    learning = None
    if workflow:
        from browser_learning_workflow import LearningWorkflowChecks
        learning = LearningWorkflowChecks(page,output,checks)
    def snapshot():
        return page.evaluate(f'({{positions:{positions}, colors:{colors}, mode:__city.controllerManager.activeMode, count:__city.demoSession.count, unit:__city.demoSession.unitId, form:document.getElementById("education-unit-form").getAttribute("href"),formHidden:document.getElementById("education-unit-form").hidden}})')

    def open_selector():
        page.get_by_role('button', name='Assignments', exact=True).click()
        page.wait_for_function('document.getElementById("assignment-dialog").open')

    def close_selector():
        selector.get_by_role('button', name='Close', exact=True).click()
        page.wait_for_function('!document.getElementById("assignment-dialog").open')

    # First read the actual committed empty manifest, without any synthetic routing.
    before = snapshot()
    open_selector()
    page.wait_for_function('document.getElementById("assignment-status").textContent.includes("No published units")')
    assert page.locator('#assignment-load').is_disabled()
    assert page.locator('#btn-return-start').is_disabled()
    assert page.evaluate('__city.educationNavigation.returnToStart().ok') is False
    elapsed = page.evaluate('__city.elapsed')
    for key in ['w','1','v','m','x']:
        page.keyboard.press(key)
    page.evaluate('__step(3)')
    assert page.evaluate('__city.elapsed') == elapsed
    assert snapshot() == before
    page.keyboard.press('Escape')
    page.wait_for_function('!document.getElementById("assignment-dialog").open')
    assert snapshot() == before
    assert page.evaluate('document.activeElement.id') == 'btn-assignments'
    checks.append('actual empty public manifest keeps Demo Mode, location/progress, selector pause/input/focus and Return guard')
    print('Browser Phase 2: empty manifest and shared modal ownership passed', flush=True)

    fixture = lambda version, unit_id: json.loads((ROOT/f'tests/fixtures/{"v2/" if version == 2 else ""}{unit_id}.json').read_text())
    a, b = fixture(2, 'S01'), fixture(1, 'S02')
    if learning: learning.prepare_units(a,b)
    units = { 'S01.json': a, 'S02.json': b }
    manifest = {'schemaVersion':1,'units':[{'unitId':u['unitId'],'title':u['title'],'file':name} for name,u in units.items()]}
    state = {'manifest':manifest,'failure':None,'hold':False}
    requests, held = [], []

    def route_assignments(route):
        url = route.request.url
        requests.append(url)
        file = url.split('?')[0].split('/')[-1]
        if file == 'manifest.json':
            route.fulfill(json=state['manifest'])
        elif file not in units:
            route.fulfill(status=404, body='Unpublished')
        elif state['hold']:
            held.append(route)
        elif state['failure'] == 'http':
            route.fulfill(status=503, body='Temporarily unavailable')
        elif state['failure'] == 'json':
            route.fulfill(body='{"schemaVersion":', content_type='application/json')
        elif state['failure'] == 'answer':
            bad = json.loads(json.dumps(units[file])); bad['questions'][0]['correctOption'] = 'AB'
            route.fulfill(json=bad)
        elif state['failure'] == 'url':
            bad = json.loads(json.dumps(units[file])); bad['googleFormUrl'] = 'https://evil.test/form'
            route.fulfill(json=bad)
        else:
            route.fulfill(json=units[file])

    page.route('**/assignments/**', route_assignments)

    def ready():
        page.wait_for_function('!document.getElementById("assignment-load").disabled')

    def select_load(unit_id):
        page.locator('#assignment-unit').select_option(unit_id)
        selector.get_by_role('button', name='Load Unit', exact=True).click()
        assert page.locator('#assignment-switch').is_visible()

    # A deliberate switch requires confirmation and cancellation leaves the demo intact.
    before = snapshot()
    open_selector(); ready(); select_load('S01')
    assert not any(url.endswith('S01.json') for url in requests)
    selector.get_by_role('button', name='Cancel', exact=True).click()
    assert snapshot() == before
    open_selector(); ready(); select_load('S01')
    page.screenshot(path=str(output/'assignment-selector.png'), timeout=180000)
    selector.get_by_role('button', name='Confirm Replacement', exact=True).click()
    page.wait_for_function('__city.demoSession.unitId === "S01" && !document.getElementById("assignment-dialog").open')
    assert page.evaluate(positions) == before['positions']
    assert page.evaluate('__city.demoSession.mode') == 'assignment'
    assert page.evaluate('__city.demoSession.total') == 4
    assert page.evaluate('__city.scene.getObjectByName("DemoTerminal-Q05").visible') is False
    assert 'S01' in page.locator('#education-session-label').inner_text()
    assert page.locator('#education-progress').inner_text().startswith('0 / 4')
    checks.append('published v2 four-question unit activates only after confirmation; no city relocation; Q05 hidden')

    sites = page.evaluate('''async () => (await import('./js/education-config.js')).TERMINALS''')
    def question(unit_id, question_id, label):
        site = next(site for site in sites if site['id'] == question_id)
        # Use the unchanged city teleport path for these data/UI checks. Normal
        # walking reachability of the same fixed sites was checked by the demo run.
        road_z = {'Q01':398.6,'Q02':422.6,'Q03':398.6,'Q04':477,'Q05':320.2}[question_id]
        x = 3.6 if question_id == 'Q02' else site['x']
        page.keyboard.press('2')
        page.evaluate('''async p => {
          __city.controllerManager.teleportActiveTo(p.x,p.z,0);
          __city.cameraSystem.resetForTeleport(); await __step();
        }''', {'x':x,'z':road_z})
        page.keyboard.press('x')
        page.wait_for_function('document.getElementById("education-dialog").open')
        assert page.locator('#education-title').inner_text().startswith(question_id)
        assert page.locator('#education-demo-note').inner_text() == f'{unit_id} · validated assignment'
        if learning: learning.before_answer(unit_id,question_id)
        page.locator(f'input[name="demo-answer"][value="{label}"]').check()
        page.get_by_role('button', name='Submit Answer', exact=True).click()
        if learning: learning.after_answer(unit_id,question_id)

    # Three options show three radios. Q02 accepts C as a single selection as well as B.
    question('S01','Q01','B')
    assert page.locator('#education-options input').count() == 3
    assert page.locator('#education-feedback').inner_text().startswith('Incorrect')
    assert page.evaluate('__city.demoSession.count') == 0
    page.locator('input[name="demo-answer"][value="A"]').check()
    page.get_by_role('button', name='Submit Answer', exact=True).click()
    assert page.evaluate('__city.demoSession.count') == 1
    if learning: learning.after_answer('S01','Q01')
    page.get_by_role('button', name='Close', exact=True).click()
    question('S01','Q02','C')
    assert page.locator('#education-options input').count() == 4
    assert page.locator('#education-options input:checked').count() == 1
    assert page.locator('#education-feedback').inner_text().startswith('Correct')
    assert page.evaluate('__city.demoSession.count') == 2
    page.screenshot(path=str(output/'assignment-question.png'), timeout=180000)
    page.get_by_role('button', name='Close', exact=True).click()

    # Wrong review keeps the old pass, and Q05 has no eligible question.
    question('S01','Q02','A')
    assert page.evaluate('__city.demoSession.count') == 2
    page.get_by_role('button', name='Close', exact=True).click()
    page.evaluate('''async () => { __city.controllerManager.teleportActiveTo(65,320.2,0); await __step(); }''')
    page.keyboard.press('x')
    assert not page.locator('#education-dialog').evaluate('(dialog)=>dialog.open')
    for qid,label in [('Q03','B'),('Q04','A')]:
        question('S01',qid,label)
        page.get_by_role('button', name='Close', exact=True).click()
    assert page.evaluate('__city.demoSession.complete')
    assert 'All 4 questions passed' in page.locator('#education-completion').inner_text()
    page.evaluate('__step()')  # Render the newly passed marker before capturing completion colors.
    page.screenshot(path=str(output/'assignment-four-complete.png'), timeout=180000)
    if learning: learning.four_complete()
    checks.append('v2 three/four radios, one accepted label, incorrect retry/review, four-question completion and Q05 denial')
    print('Browser Phase 2: v2 interaction and four-question completion passed', flush=True)

    # Native Return/mode/map/preset changes preserve the real assignment and green markers.
    completed = page.evaluate(colors)
    page.get_by_role('button', name='Return to Start', exact=True).click()
    for key in ['1','3','2','4','2','v']:
        page.keyboard.press(key)
    page.keyboard.press('m')
    if learning: learning.map_form()
    page.locator('#fullmap-canvas').click(position={'x':550,'y':400})
    page.keyboard.press('Escape')
    if learning: page.evaluate('__step()')
    page.locator('[popovertarget="teleport-popover"]').click()
    page.locator('[data-teleport="centralpark"]').click()
    assert page.evaluate('__city.demoSession.unitId') == 'S01'
    assert page.evaluate('__city.demoSession.count') == 4
    assert page.evaluate(colors) == completed
    checks.append('validated-session progress/colors survive Return, camera/modes, full-map and preset teleportation')

    # Every failed replacement preserves unit, passes, colors and all entity positions.
    for failure, expected in [('http','HTTP 503'),('json','not valid JSON'),('answer','Choose exactly one'),('url','supported HTTPS Google Forms')]:
        state['failure'] = failure
        before = snapshot()
        open_selector(); ready(); select_load('S02')
        selector.get_by_role('button', name='Confirm Replacement', exact=True).click()
        page.wait_for_function('(s) => document.getElementById("assignment-status").textContent.includes(s)', arg=expected)
        assert snapshot() == before
        close_selector()
    state['failure'] = None

    # Cancelling an actual in-flight request cannot commit its late response.
    before = snapshot(); state['hold'] = True
    open_selector(); ready(); select_load('S02')
    selector.get_by_role('button', name='Confirm Replacement', exact=True).click()
    page.wait_for_function('document.getElementById("assignment-status").textContent.includes("Loading S02")')
    # Pump Playwright's event loop until the route handler has captured the request.
    page.wait_for_timeout(100)
    assert held
    close_selector(); state['hold'] = False
    for route in held:
        try: route.fulfill(json=b)
        except Error: pass  # Chromium may already have discarded the aborted request.
    held.clear()
    page.wait_for_timeout(100)
    assert snapshot() == before

    # A malformed manifest clears the choices and never probes the unpublished target.
    state['manifest'] = {'schemaVersion':1,'units':[{'unitId':'S03','title':'Bad path','file':'../S03.json'}]}
    before = snapshot(); open_selector()
    page.wait_for_function('document.getElementById("assignment-status").textContent.includes("paths and remote URLs are forbidden")')
    assert page.locator('#assignment-load').is_disabled()
    assert snapshot() == before
    assert not any('S03.json' in url for url in requests)
    close_selector(); state['manifest'] = manifest
    checks.append('HTTP/JSON/answer/URL failures, cancelled loading and invalid manifest preserve the full previous attempt')

    # V1 five-question replacement restores Q05 without moving the city or changing sites.
    before = snapshot(); open_selector(); ready(); select_load('S02')
    selector.get_by_role('button', name='Confirm Replacement', exact=True).click()
    page.wait_for_function('__city.demoSession.unitId === "S02" && !document.getElementById("assignment-dialog").open')
    assert page.evaluate(positions) == before['positions']
    assert page.evaluate('__city.demoSession.count') == 0
    assert page.evaluate('__city.demoSession.total') == 5
    if learning: learning.replaced()
    assert page.evaluate('__city.scene.getObjectByName("DemoTerminal-Q05").visible')
    question('S02','Q05','A')
    assert page.locator('#education-options input').count() == 4
    assert page.locator('#education-feedback').inner_text().startswith('Correct')
    page.get_by_role('button', name='Close', exact=True).click()
    assert page.evaluate('__city.demoSession.count') == 1
    assert not page.evaluate('__city.demoSession.complete')
    assert page.evaluate('''async () => (await import('./js/education-config.js')).TERMINALS''') == sites
    expected_prefix = f'/{base_path}assignments/'
    assert all(expected_prefix in url for url in requests), requests
    assert all(url.endswith(('manifest.json','S01.json','S02.json')) for url in requests), requests
    if learning: learning.finish_five(question)
    checks.append('v1 five-question replacement restores fixed Q05; nested relative paths and exact manifest allowlisting')
    (output/'assignment-requests.json').write_text(json.dumps(requests,indent=2))
    print('Browser Phase 2: failures/cancellation, v1 replacement, travel and nested paths passed', flush=True)
