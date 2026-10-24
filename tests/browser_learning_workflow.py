"""Phase 3 native-link checks. External fixture targets are intercepted, never contacted."""
import json
import re


def mock_external_links(context, on_navigation=lambda url, headers: None):
    def intercept(route):
        if route.request.is_navigation_request():
            on_navigation(route.request.url, route.request.headers)
            route.fulfill(content_type='text/html', body='<title>TEST ONLY external tab</title><p>External navigation intercepted for review. No video or Form provider was contacted.</p>')
        else:
            route.fulfill(status=204, body='')
    context.route(re.compile(r'^https://(?:(?:www\.)?youtube\.com|youtu\.be|forms\.gle|docs\.google\.com)/'), intercept)


class LearningWorkflowChecks:
    def __init__(self, page, output, checks):
        self.page, self.output, self.checks = page, output, checks
        self.expected, self.requests, self.popups = [], [], []
        self.visited = set()
        page.context.on('page', lambda popup: self.popups.append(popup))
        def navigation(url, headers):
            assert url in self.expected, f'Unexpected external navigation: {url}'
            assert 'referer' not in headers, headers.get('referer')
            self.requests.append(url)
        mock_external_links(page.context, navigation)
        for control in ['education-question-video','education-explanation-video','education-unit-form','education-dialog-form']:
            assert page.locator('#'+control).get_attribute('href') is None
            assert not page.locator('#'+control).is_visible()
        assert 'Demo complete!' in page.locator('#education-completion').inner_text()
        self.passive()
        checks.append('completed Demo Mode preserves its message and supplies no invented video, explanation or Form links')

    def passive(self):
        assert len(self.popups) == len(self.expected), 'A tab opened without an explicit test action'
        assert len(self.requests) == len(self.expected), 'A resource navigated without an explicit test action'

    def link(self, control, expected):
        element = self.page.locator('#'+control)
        assert element.get_attribute('href') == expected
        assert element.get_attribute('target') == '_blank'
        assert set(element.get_attribute('rel').split()) == {'noopener','noreferrer'}
        return element

    def state(self):
        return self.page.evaluate('''() => ({unit:__city.demoSession.unitId,count:__city.demoSession.count,
          complete:__city.demoSession.complete,mode:__city.controllerManager.activeMode,
          positions:Object.fromEntries(Object.entries(__city.controllerManager.entities).map(([k,e])=>[k,e.position.toArray()])),
          camera:__city.cameraSystem.activePresetId,dialog:document.getElementById('education-dialog').open,
          title:document.getElementById('education-title').textContent,
          selected:document.querySelector('#education-options input:checked')?.value})''')

    def open_external(self, control, expected, keyboard=False):
        self.passive()
        element = self.link(control, expected)
        assert element.is_visible()
        before = self.state()
        self.expected.append(expected)
        with self.page.context.expect_page() as event:
            if keyboard:
                element.focus(); self.page.keyboard.press('Enter')
            else:
                element.click()
        popup = event.value
        popup.wait_for_load_state('domcontentloaded')
        assert popup.url == expected
        assert popup.evaluate('window.opener === null')
        assert 'intercepted for review' in popup.locator('body').inner_text()
        popup.close(); self.page.bring_to_front()
        assert self.state() == before
        self.passive()
        if before['dialog']:
            elapsed = self.page.evaluate('__city.elapsed')
            for key in ['w','m','v','4']:
                self.page.keyboard.press(key)
            self.page.evaluate('__step(2)')
            assert self.page.evaluate('__city.elapsed') == elapsed
            assert self.state() == before

    @staticmethod
    def prepare_units(a, b):
        # Test-only response mutations: exercise absent/blank/literal text and detect
        # stale links across units. Reference fixture files remain byte-identical.
        a['questions'][0]['explanationText'] = '<b>TEST ONLY literal explanation</b>\n第二行 🧪'
        a['questions'][2].pop('explanationText')
        a['questions'][3]['explanationText'] = ' \n\t '
        b['googleFormUrl'] = 'https://docs.google.com/forms/d/e/1FAIpQLSc/viewform'
        for question in b['questions']:
            question['questionVideoUrl'], question['explanationVideoUrl'] = question['explanationVideoUrl'], question['questionVideoUrl']

    def before_answer(self, unit_id, question_id):
        self.passive()
        data = self.page.evaluate('id => __city.demoSession.question(id)', question_id)
        video = self.link('education-question-video', data['questionVideoUrl'])
        assert video.is_visible()
        assert video.evaluate('(e) => Boolean(e.compareDocumentPosition(document.getElementById("education-options")) & Node.DOCUMENT_POSITION_FOLLOWING)')
        assert self.page.locator('#education-question').is_visible()
        assert self.page.locator('#education-options').is_visible()
        passed = self.page.evaluate('id => __city.demoSession.hasPassed(id)', question_id)
        if not passed:
            assert not self.page.locator('#education-explanation').is_visible()
            assert self.page.locator('#education-explanation-video').get_attribute('href') is None
            assert self.page.locator('#education-explanation-text').inner_text() == ''
        if (unit_id,question_id) in [('S01','Q01'),('S02','Q05')] and (unit_id,question_id) not in self.visited:
            self.visited.add((unit_id,question_id))
            self.open_external('education-question-video',data['questionVideoUrl'],keyboard=unit_id=='S02')
            self.checks.append(f'{unit_id} question video uses its exact URL, secure new tab and explicit {"keyboard" if unit_id=="S02" else "click"}; modal pause/input survive return')

    def after_answer(self, unit_id, question_id):
        self.passive()
        question = self.page.evaluate('id => __city.demoSession.question(id)', question_id)
        passed = self.page.evaluate('id => __city.demoSession.hasPassed(id)', question_id)
        if not passed:
            assert not self.page.locator('#education-explanation').is_visible()
            assert self.page.locator('#education-explanation-video').get_attribute('href') is None
            return
        assert self.page.locator('#education-explanation').is_visible()
        assert self.link('education-explanation-video',question['explanationVideoUrl']).is_visible()
        text = question.get('explanationText','')
        assert self.page.locator('#education-explanation-text-section').is_visible() == bool(text.strip())
        assert self.page.locator('#education-explanation-text').text_content() == (text if text.strip() else '')
        assert self.page.locator('#education-explanation-text b').count() == 0, 'Explanation HTML must remain literal text'
        if unit_id=='S01' and question_id=='Q01' and 'explanation' not in self.visited:
            self.visited.add('explanation')
            self.open_external('education-explanation-video',question['explanationVideoUrl'],keyboard=True)
            self.page.screenshot(path=str(self.output/'learning-explanation.png'),timeout=180000)
        complete = self.page.evaluate('__city.demoSession.complete')
        form = self.page.evaluate('__city.demoSession.unit.googleFormUrl')
        for control in ['education-unit-form','education-dialog-form']:
            assert self.page.locator('#'+control).get_attribute('href') == (form if complete else None)
            assert self.page.locator('#'+control).evaluate('(e)=>e.hidden') == (not complete)
        if unit_id=='S02' and complete:
            self.open_external('education-dialog-form',form,keyboard=True)

    def four_complete(self):
        self.passive()
        form = self.page.evaluate('__city.demoSession.unit.googleFormUrl')
        self.open_external('education-unit-form',form)
        self.page.set_viewport_size({'width':390,'height':844})
        box=self.page.locator('#education-unit-form').bounding_box()
        assert box and 0<=box['x'] and box['x']+box['width']<=390 and box['y']+box['height']<=844
        self.page.screenshot(path=str(self.output/'learning-small-hud.png'),timeout=180000)
        self.page.set_viewport_size({'width':1280,'height':800})
        self.checks.append('four-question completion unlocks exact Form link in HUD/dialog; native click, small viewport and return preserve state')

    def map_form(self):
        self.page.evaluate('__step()')
        form=self.page.evaluate('__city.demoSession.unit.googleFormUrl')
        link=self.link('education-unit-form',form)
        assert link.is_visible()
        assert link.evaluate('''e => {const r=e.getBoundingClientRect(); return e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2));}''')
        self.open_external('education-unit-form',form,keyboard=True)
        assert self.page.evaluate('__city.mapSystem.isFullMapOpen')
        self.checks.append('completed Form remains clickable over the full map and keyboard activation preserves the map/session')

    def replaced(self):
        self.passive()
        for control in ['education-unit-form','education-dialog-form','education-question-video','education-explanation-video']:
            assert self.page.locator('#'+control).get_attribute('href') is None
            assert not self.page.locator('#'+control).is_visible()
        assert self.page.locator('#education-explanation-text').text_content()==''
        self.checks.append('confirmed replacement clears prior video/explanation/Form URLs and locks the new attempt')

    def finish_five(self, question):
        for qid,label in [('Q01','A'),('Q02','B'),('Q03','C'),('Q04','D')]:
            question('S02',qid,label)
            self.page.get_by_role('button',name='Close',exact=True).click()
            if qid=='Q03':
                assert self.page.evaluate('__city.demoSession.count')==4
                assert self.page.locator('#education-unit-form').get_attribute('href') is None
        assert self.page.evaluate('__city.demoSession.complete')
        assert self.page.evaluate('__city.demoSession.count')==5
        assert '5 / 5' in self.page.locator('#education-progress').inner_text()
        self.page.evaluate('__step()')
        self.page.screenshot(path=str(self.output/'learning-five-complete.png'),timeout=180000)
        self.passive()
        self.checks.append('v1 five-question completion unlocks the replacement Form only at 5/5; final dialog keyboard activation keeps completion')
        (self.output/'learning-external-actions.json').write_text(json.dumps(self.requests,indent=2))
