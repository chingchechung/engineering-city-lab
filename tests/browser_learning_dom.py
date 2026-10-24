"""Fast native DOM regression for Phase 3 links and rapid dialog reopening.

Uses the actual educational HTML/modules and validated session, without loading
the city renderer. Full-city checks remain in browser_education.py --workflow.
All provider requests are intercepted before new-tab navigation.
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import threading

from playwright.sync_api import sync_playwright
from browser_learning_workflow import mock_external_links

ROOT = Path(__file__).resolve().parents[1]


def run(output):
    output.mkdir(parents=True,exist_ok=True)
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    checks,requests,errors=[],[],[]
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
            try:
                context=browser.new_context();opened=[]
                context.on('page',lambda popup:opened.append(popup))
                mock_external_links(context,lambda url,headers:requests.append((url,headers)))
                page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
                source=(ROOT/'index.html').read_text()
                fragment=source[source.index('  <aside id="education-hud"'):source.index('</body>')]
                html='<link rel="stylesheet" href="./css/style.css"><link rel="stylesheet" href="./css/education.css">'+fragment
                page.route('**/workflow-dom.html',lambda route:route.fulfill(content_type='text/html',body=html))
                page.goto(f'http://127.0.0.1:{server.server_port}/workflow-dom.html')
                page.evaluate('''async data => {
                  const {createAssignmentSession}=await import('./js/assignment-session.js');
                  const {createEducationUI}=await import('./js/education-ui.js');
                  const session=createAssignmentSession();session.activate(data,'S01.json');
                  window.__learningDOM={session,id:'Q01'};
                  const ui=createEducationUI({session,getNearby:()=>({id:__learningDOM.id}),available:()=>true,
                    onPause:()=>{},onResume:()=>{},onPassed:()=>{}});
                  __learningDOM.ui=ui;ui.update();
                }''',json.loads((ROOT/'tests/fixtures/v2/S01.json').read_text()))

                def external(control,keyboard=False):
                    before=page.evaluate('({count:__learningDOM.session.count,open:document.getElementById("education-dialog").open})')
                    link=page.locator('#'+control);url=link.get_attribute('href')
                    with context.expect_page() as event:
                        if keyboard:link.focus();page.keyboard.press('Enter')
                        else:link.click()
                    popup=event.value;popup.wait_for_load_state('domcontentloaded')
                    assert popup.url==url and popup.evaluate('window.opener===null')
                    assert 'referer' not in requests[-1][1]
                    popup.close();page.bring_to_front()
                    assert page.evaluate('({count:__learningDOM.session.count,open:document.getElementById("education-dialog").open})')==before

                page.keyboard.press('x');external('education-question-video')
                checks.append('native question click opens exact intercepted URL with no opener/referrer and retains the dialog')
                for qid,label in [('Q01','A'),('Q02','C'),('Q03','B'),('Q04','A')]:
                    if qid!='Q01':
                        page.evaluate('id=>__learningDOM.id=id',qid);page.keyboard.press('x')
                    assert page.locator('#education-title').inner_text().startswith(qid)
                    # Simulate an older native close event delivered after this dialog reopened.
                    page.locator('#education-dialog').evaluate('e=>e.dispatchEvent(new Event("close"))')
                    page.locator(f'input[value="{label}"]').check()
                    page.get_by_role('button',name='Submit Answer',exact=True).click()
                    assert page.locator('#education-feedback').inner_text().startswith('Correct')
                    if qid=='Q01':external('education-explanation-video',True)
                    page.locator('#education-close').click()
                assert page.evaluate('__learningDOM.session.complete')
                assert page.evaluate('__learningDOM.session.count')==4
                checks.append('rapid and delayed-close reopening keeps each new question active; all four answers pass')
                external('education-unit-form',True)
                assert len(requests)==3 and not errors
                checks.append('native explanation/Form Enter activation preserves progress and opens no unsolicited tabs')
                assert len(opened)==4
                page.screenshot(path=str(output/'dom-complete.png'))
                print(json.dumps({'checks':checks,'browser':browser.version,'actions':len(requests),'page_errors':errors},indent=2),flush=True)
            finally:browser.close()
    finally:
        server.shutdown();server.server_close();thread.join()
        (output/'results.json').write_text(json.dumps({'checks':checks,'actions':[url for url,headers in requests],'page_errors':errors},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=Path('/tmp/city-learning-dom'))
    run(parser.parse_args().output)
