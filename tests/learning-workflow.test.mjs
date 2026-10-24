import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { createAssignmentSession } from '../js/assignment-session.js';
import { createAssignmentLoader } from '../js/assignment-loader.js';
import { questionResources, completionFormUrl } from '../js/education-ui.js';

const fixture = (version = 1, id = 'S01') => JSON.parse(readFileSync(new URL(`./fixtures/${version === 2 ? 'v2/' : ''}${id}.json`, import.meta.url)));
const empty = { questionVideoUrl: null, explanationVideoUrl: null, explanationText: null };
function active(version = 1, id = 'S01', data = fixture(version, id)) {
  const session = createAssignmentSession(); session.activate(data, `${id}.json`); return session;
}
function finish(session) {
  for (const question of session.questions) session.answer(question.id, question.correctOptions?.[0] ?? question.correctOption);
}

test('Demo Mode supplies no external resources, including after all five passes', () => {
  const session = createAssignmentSession();
  for (const [index, label] of [...'ABCAB'].entries()) {
    const question = session.questions[index];
    assert.deepEqual(questionResources(session, question), empty);
    session.answer(question.id, label);
    assert.deepEqual(questionResources(session, question), empty);
  }
  assert.ok(session.complete); assert.equal(completionFormUrl(session), null);
});

for (const version of [1, 2]) {
  test(`v${version} offers the exact validated question URL before answering, with no explanation`, () => {
    const session = active(version), question = session.question('Q01');
    assert.deepEqual(questionResources(session, question), { ...empty, questionVideoUrl: question.questionVideoUrl });
    assert.equal(completionFormUrl(session), null); assert.equal(session.count, 0);
  });
  test(`v${version} incorrect retry cannot reveal a new explanation or revoke another pass`, () => {
    const session = active(version), question = session.question('Q01');
    session.answer('Q02', 'B'); assert.equal(session.count, 1);
    assert.equal(session.answer('Q01', 'D'), false);
    assert.equal(questionResources(session, question).explanationVideoUrl, null);
    assert.equal(questionResources(session, question).explanationText, null);
    assert.equal(session.count, 1); assert.equal(completionFormUrl(session), null);
  });
  test(`v${version} correct answer immediately reveals supplied explanation and preserves it on a wrong review`, () => {
    const session = active(version), question = session.question('Q01');
    assert.equal(session.answer('Q01', 'A'), true);
    assert.deepEqual(questionResources(session, question), {
      questionVideoUrl: question.questionVideoUrl, explanationVideoUrl: question.explanationVideoUrl,
      explanationText: question.explanationText
    });
    assert.equal(session.answer('Q01', 'D'), false);
    assert.equal(questionResources(session, question).explanationVideoUrl, question.explanationVideoUrl);
    assert.equal(session.count, 1);
  });
}

test('one accepted v2 label C reveals explanation; an array or combined selection does not pass', () => {
  const session = active(2), question = session.question('Q02');
  for (const answer of [['B','C'], 'BC', 'D']) {
    assert.equal(session.answer('Q02', answer), false);
    assert.equal(questionResources(session, question).explanationVideoUrl, null);
  }
  assert.equal(session.answer('Q02', 'C'), true);
  assert.equal(questionResources(session, question).explanationVideoUrl, question.explanationVideoUrl);
  assert.equal(session.count, 1);
});

for (const text of [undefined, '', ' \n\t ', '\ufeff\u3000']) {
  test(`missing or blank explanation text ${JSON.stringify(text)} is omitted without hiding the required video`, () => {
    const data = fixture(2);
    if (text === undefined) delete data.questions[0].explanationText;
    else data.questions[0].explanationText = text;
    const session = active(2, 'S01', data); session.answer('Q01', 'A');
    const resource = questionResources(session, session.question('Q01'));
    assert.equal(resource.explanationText, null); assert.ok(resource.explanationVideoUrl);
  });
}

test('supplied multiline explanation and language are preserved without inventing text', () => {
  const data = fixture(2); data.questions[0].explanationText = '<b>TEST ONLY literal</b>\n第二行 🧪';
  const session = active(2, 'S01', data); session.answer('Q01','A');
  assert.equal(questionResources(session, session.question('Q01')).explanationText, data.questions[0].explanationText);
});

for (const [id, total] of [['S01', 4], ['S02', 5]]) {
  test(`${total}-question Form unlock uses session.complete and the exact unit URL, with no extra destination`, () => {
    const session = active(2, id);
    for (const question of session.questions.slice(0, total - 1)) session.answer(question.id, question.correctOptions[0]);
    assert.equal(session.count, total - 1); assert.equal(completionFormUrl(session), null);
    const last = session.questions.at(-1); session.answer(last.id, last.correctOptions[0]);
    assert.ok(session.complete); assert.equal(completionFormUrl(session), session.unit.googleFormUrl);
    assert.equal(Boolean(session.question('Q05')), total === 5);
    session.answer(last.id, 'invalid');
    assert.equal(completionFormUrl(session), session.unit.googleFormUrl);
  });
}

test('successful unit replacement removes old question resources and locks the new Form until completion', () => {
  const session = active(2), old = session.question('Q01'); finish(session);
  assert.ok(completionFormUrl(session)); assert.ok(questionResources(session, old).explanationVideoUrl);
  session.activate(fixture(1, 'S02'), 'S02.json');
  assert.deepEqual(questionResources(session, old), empty, 'even a same-ID stale object cannot supply old links');
  assert.equal(completionFormUrl(session), null); assert.equal(session.count, 0);
  assert.equal(questionResources(session, session.question('Q01')).explanationVideoUrl, null);
});

test('failed validation leaves the completed unit Form and review resources unchanged', () => {
  const session = active(2); finish(session);
  const question = session.question('Q02'), before = questionResources(session, question), form = completionFormUrl(session);
  const bad = fixture(1, 'S02'); bad.googleFormUrl = 'javascript:alert(1)';
  assert.throws(() => session.activate(bad, 'S02.json'));
  assert.equal(completionFormUrl(session), form); assert.deepEqual(questionResources(session, question), before);
});

test('cancelled/stale transport cannot replace a completed unit or its Form link', async () => {
  const session = active(2); finish(session);
  const before = completionFormUrl(session), next = fixture(1, 'S02');
  let resolve;
  const pending = new Promise(done => resolve = done);
  const loader = createAssignmentLoader({ baseURL: new URL('https://example.test/course/city/assignments/'),
    fetch: async url => url.pathname.endsWith('manifest.json')
      ? { ok: true, json: async () => ({ schemaVersion:1, units:[{ unitId:'S02', title:next.title, file:'S02.json' }] }) }
      : pending,
    onReady: (unit,file) => session.activate(unit,file)
  });
  await loader.refresh(); const loading = loader.load('S02'); loader.cancel();
  resolve({ ok:true, json:async () => next });
  assert.equal((await loading).cancelled, true);
  assert.equal(completionFormUrl(session), before); assert.equal(session.count, 4);
});
