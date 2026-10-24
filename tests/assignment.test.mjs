import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync, readdirSync } from 'node:fs';
import { validateUnit, validateUnitV1, validateUnitV2, validateManifest, normalizeUnit, acceptsAnswer } from '../js/assignment-contract.js';
import { createAssignmentSession } from '../js/assignment-session.js';
import { createAssignmentLoader } from '../js/assignment-loader.js';

const fixture = (version = 1, id = 'S01') => JSON.parse(readFileSync(new URL(`./fixtures/${version === 2 ? 'v2/' : ''}${id}.json`, import.meta.url)));
const response = data => ({ ok: true, json: async () => structuredClone(data) });
const manifest = (...units) => ({ schemaVersion: 1, units: units.map(unit => ({ unitId: unit.unitId, title: unit.title, file: `${unit.unitId}.json` })) });
const deferred = () => { let resolve; const promise = new Promise(done => resolve = done); return { promise, resolve }; };
const turn = () => new Promise(resolve => setImmediate(resolve));
function harness(files = {}) {
  const session = createAssignmentSession(), calls = [], commits = [];
  const loader = createAssignmentLoader({
    baseURL: new URL('https://example.test/nested/city/assignments/'),
    fetch: async (url, options) => {
      const file = url.pathname.split('/').at(-1); calls.push({ file, url, options });
      const value = files[file];
      if (typeof value === 'function') return value(options);
      if (value instanceof Error) throw value;
      return value === undefined ? { ok: false, status: 404 } : response(value);
    },
    onReady: (unit, file) => { session.activate(unit, file); commits.push(unit.unitId); }
  });
  return { loader, session, calls, commits, files };
}

for (const version of [1, 2]) for (const [id, count] of [['S01', 4], ['S02', 5]]) {
  test(`reference v${version} ${count}-question fixture validates and keeps its version`, () => {
    const data = fixture(version, id), session = createAssignmentSession();
    assert.deepEqual(validateUnit(data, `${id}.json`), []);
    session.activate(data, `${id}.json`);
    assert.equal(session.unit.schemaVersion, version);
    assert.equal(session.total, count);
    assert.equal(Boolean(session.question('Q05')), count === 5);
  });
}

test('explicit validators reject other versions and mixed answer fields without migration', () => {
  assert.ok(validateUnitV1(fixture(2)).length);
  assert.ok(validateUnitV2(fixture(1)).length);
  for (const version of [1, 2]) {
    const data = fixture(version);
    data.questions[0][version === 1 ? 'correctOptions' : 'correctOption'] = version === 1 ? ['A'] : 'A';
    assert.ok(validateUnit(data).some(error => error.code === 'unknown_field'));
  }
  assert.ok(validateUnit({ ...fixture(), schemaVersion: 3 }).some(error => error.code === 'schema_version'));
});

test('all twelve exact unit IDs work; IDs and answer labels are never trimmed', () => {
  for (let i = 1; i <= 12; i++) {
    const unitId = `S${String(i).padStart(2, '0')}`;
    assert.deepEqual(validateUnit({ ...fixture(), unitId }, `${unitId}.json`), []);
  }
  for (const unitId of ['S00', 'S13', 's01', ' S01', 'S01\n']) assert.ok(validateUnit({ ...fixture(), unitId }).length);
  assert.equal(acceptsAnswer(fixture(2).questions[0], ' A '), false);
});

test('normalization preserves language, option order, source data and exact answer labels', () => {
  const data = fixture(2), before = structuredClone(data);
  data.title = '\ufeff 測試 🧪 \u3000'; data.questions[0].options = [' 第二 ', ' 第一 ', ' third '];
  const original = structuredClone(data), normalized = normalizeUnit(data);
  assert.equal(normalized.title, '測試 🧪');
  assert.deepEqual(normalized.questions[0].options, ['第二', '第一', 'third']);
  assert.deepEqual(normalized.questions[0].correctOptions, before.questions[0].correctOptions);
  assert.deepEqual(data, original);
});

test('default session preserves the five-question Phase 1 demo and retry behavior', () => {
  const session = createAssignmentSession();
  assert.equal(session.mode, 'demo'); assert.equal(session.unit, null); assert.equal(session.total, 5);
  for (const [id, label] of [['Q01','A'],['Q02','B'],['Q03','C'],['Q04','A'],['Q05','B']]) assert.equal(session.answer(id, label), true);
  assert.equal(session.complete, true);
  assert.equal(session.answer('Q01', 'B'), false);
  assert.equal(session.count, 5);
});

test('v2 accepts one of multiple labels, never an array or combined student selection', () => {
  const session = createAssignmentSession(); session.activate(fixture(2), 'S01.json');
  assert.equal(session.answer('Q02', 'B'), true);
  assert.equal(session.answer('Q02', 'C'), true);
  for (const choice of [['B', 'C'], ['B'], 'BC', 'D', null, true]) assert.equal(session.answer('Q02', choice), false);
  assert.equal(session.count, 1); assert.equal(session.hasPassed('Q02'), true);
  assert.equal(session.answer('Q01', 'D'), false, 'no hidden fourth option');
});

test('four-question completion excludes Q05 and wrong reviews never revoke a pass', () => {
  const session = createAssignmentSession(); session.activate(fixture(), 'S01.json');
  for (const [index, label] of [...'ABCD'].entries()) session.answer(`Q0${index+1}`, label);
  assert.equal(session.complete, true); assert.equal(session.count, 4);
  assert.equal(session.question('Q05'), null); assert.equal(session.answer('Q05', 'A'), false);
  assert.equal(session.answer('Q01', 'D'), false); assert.equal(session.answer('Q99', 'A'), false);
  assert.equal(session.complete, true); assert.equal(session.count, 4);
});

test('five-question completion requires Q05 and successful replacement alone clears passes', () => {
  const session = createAssignmentSession(), data = fixture(2, 'S02'); session.activate(data, 'S02.json');
  for (const question of data.questions.slice(0, 4)) session.answer(question.id, question.correctOptions[0]);
  assert.equal(session.complete, false);
  session.answer('Q05', data.questions[4].correctOptions[0]); assert.equal(session.complete, true);
  session.activate(fixture(), 'S01.json'); assert.equal(session.count, 0); assert.equal(session.total, 4);
});

test('invalid replacements preserve the complete prior session and expose exact issues', () => {
  const session = createAssignmentSession(); session.activate(fixture(2), 'S01.json'); session.answer('Q02', 'C');
  const before = session.unit, data = fixture(); data.questions[0].correctOption = 'AB';
  assert.throws(() => session.activate(data, 'S01.json'), error => {
    assert.deepEqual(error.issues, validateUnit(data, 'S01.json'));
    assert.equal(error.issues[0].message, 'Choose exactly one of A, B, C, D.'); return true;
  });
  assert.equal(session.unit, before); assert.equal(session.count, 1); assert.ok(session.hasPassed('Q02'));
});

test('active assignment data is an immutable normalized snapshot, independent of the input', () => {
  const session = createAssignmentSession(), data = fixture(2); session.activate(data, 'S01.json');
  data.questions[0].correctOptions[0] = 'B';
  assert.equal(session.answer('Q01', 'A'), true);
  assert.throws(() => session.questions.push({}));
  assert.throws(() => { session.questions[0].options[0] = 'changed'; });
  assert.throws(() => { session.unit.title = 'changed'; });
});

test('committed public allowlist is valid, empty and contains no unit exports', () => {
  const path = new URL('../assignments/', import.meta.url), publicData = JSON.parse(readFileSync(new URL('manifest.json', path)));
  assert.deepEqual(publicData, { schemaVersion: 1, units: [] });
  assert.deepEqual(validateManifest(publicData), []);
  assert.deepEqual(readdirSync(path), ['manifest.json']);
});

test('loader cannot request any unit before a valid manifest or from an empty manifest', async () => {
  const h = harness({ 'manifest.json': manifest() });
  assert.equal((await h.loader.load('S01')).ok, false); assert.equal(h.calls.length, 0);
  assert.ok((await h.loader.refresh()).ok);
  assert.equal((await h.loader.load('S01')).ok, false);
  assert.deepEqual(h.calls.map(call => call.file), ['manifest.json']);
});

test('strict allowlisting requests only selected published filenames with nested-path safe fetch options', async () => {
  const data = fixture(2), h = harness({ 'manifest.json': manifest(data), 'S01.json': data });
  await h.loader.refresh();
  for (const id of ['S02', 'S13', '../S01.json', 'https://evil.test/S01.json', null]) assert.equal((await h.loader.load(id)).ok, false);
  assert.ok((await h.loader.load('S01')).ok); assert.deepEqual(h.commits, ['S01']);
  assert.deepEqual(h.calls.map(call => call.file), ['manifest.json', 'S01.json']);
  for (const call of h.calls) {
    assert.equal(call.url.origin, 'https://example.test');
    assert.ok(call.url.pathname.startsWith('/nested/city/assignments/'));
    assert.equal(call.options.cache, 'no-store'); assert.equal(call.options.redirect, 'error');
    assert.ok(call.options.signal instanceof AbortSignal);
  }
  assert.ok(Object.isFrozen(h.loader.units) && Object.isFrozen(h.loader.units[0]));
});

test('v1 and v2 coexist in one version-1 manifest and activate only after validation', async () => {
  const a = fixture(), b = fixture(2, 'S02'), h = harness({ 'manifest.json': manifest(a, b), 'S01.json': a, 'S02.json': b });
  await h.loader.refresh(); await h.loader.load('S01'); assert.equal(h.session.unit.schemaVersion, 1);
  await h.loader.load('S02'); assert.equal(h.session.unit.schemaVersion, 2); assert.equal(h.session.total, 5);
});

test('malformed manifests never authorize traversal, remote URLs, duplicates or unsupported versions', async () => {
  const valid = manifest(fixture());
  const bad = [{ ...valid, schemaVersion: 2 }, { ...valid, units: [...valid.units, ...valid.units] }, null,
    ...['../S01.json', 'https://evil.test/S01.json', '/S01.json', 'S01.json?x'].map(file => ({ ...valid, units: [{ ...valid.units[0], file }] }))];
  for (const data of bad) {
    const h = harness({ 'manifest.json': data }), result = await h.loader.refresh();
    assert.equal(result.ok, false); assert.deepEqual(result.issues, validateManifest(data));
    assert.equal((await h.loader.load('S01')).ok, false); assert.equal(h.calls.length, 1);
  }
});

test('failed manifest refresh revokes its old allowlist while preserving a valid attempt', async () => {
  const data = fixture(), h = harness({ 'manifest.json': manifest(data), 'S01.json': data });
  await h.loader.refresh(); await h.loader.load('S01'); h.session.answer('Q01', 'A');
  h.files['manifest.json'] = { schemaVersion: 3, units: [] };
  assert.equal((await h.loader.refresh()).ok, false);
  assert.equal((await h.loader.load('S01')).ok, false);
  assert.equal(h.session.unitId, 'S01'); assert.equal(h.session.count, 1);
});

for (const [name, failure, expected] of [
  ['HTTP 404', () => ({ ok: false, status: 404 }), /HTTP 404/],
  ['HTTP 503', () => ({ ok: false, status: 503 }), /HTTP 503/],
  ['network failure', () => { throw new TypeError('offline'); }, /Unable to read S01.json/],
  ['malformed JSON', () => ({ ok: true, json: async () => { throw new SyntaxError('bad'); } }), /S01.json is not valid JSON/]
]) test(`${name} preserves the previous valid unit and progress`, async () => {
  const data = fixture(), h = harness({ 'manifest.json': manifest(data), 'S01.json': data });
  await h.loader.refresh(); await h.loader.load('S01'); h.session.answer('Q01', 'A');
  h.files['S01.json'] = failure;
  const before = h.session.unit, result = await h.loader.load('S01');
  assert.equal(result.ok, false); assert.match(result.message, expected);
  assert.equal(h.session.unit, before); assert.equal(h.session.count, 1); assert.equal(h.commits.length, 1);
});

for (const [name, mutate] of [
  ['wrong version', data => { data.schemaVersion = 3; }],
  ['filename/unit mismatch', data => { data.unitId = 'S02'; }],
  ['invalid accepted labels', data => { data.questions[0].correctOptions = ['D']; }],
  ['invalid video URL', data => { data.questions[0].questionVideoUrl = 'javascript:alert(1)'; }],
  ['invalid Form URL', data => { data.googleFormUrl = 'https://evil.test/form'; }]
]) test(`rejected ${name} leaves the existing attempt intact with original validation issues`, async () => {
  const data = fixture(2), h = harness({ 'manifest.json': manifest(data), 'S01.json': data });
  await h.loader.refresh(); await h.loader.load('S01'); h.session.answer('Q02', 'C');
  const bad = structuredClone(data); mutate(bad); h.files['S01.json'] = bad;
  const before = h.session.unit, result = await h.loader.load('S01');
  assert.equal(result.ok, false); assert.deepEqual(result.issues, validateUnit(bad, 'S01.json'));
  assert.equal(h.session.unit, before); assert.equal(h.session.count, 1); assert.equal(h.commits.length, 1);
});

test('a pending replacement leaves progress untouched until its validated synchronous commit', async () => {
  const a = fixture(), b = fixture(2, 'S02'), pending = deferred();
  const h = harness({ 'manifest.json': manifest(a, b), 'S01.json': a, 'S02.json': () => pending.promise });
  await h.loader.refresh(); await h.loader.load('S01'); h.session.answer('Q01', 'A');
  const request = h.loader.load('S02'); await turn();
  assert.equal(h.session.unitId, 'S01'); assert.equal(h.session.count, 1);
  pending.resolve(response(b)); assert.ok((await request).ok);
  assert.equal(h.session.unitId, 'S02'); assert.equal(h.session.count, 0);
});

for (const stage of ['response', 'JSON body']) test(`cancelling during ${stage} blocks late success even when transport ignores abort`, async () => {
  const data = fixture(), pending = deferred();
  const h = harness({ 'manifest.json': manifest(data), 'S01.json': stage === 'response' ? () => pending.promise : () => ({ ok: true, json: () => pending.promise }) });
  h.session.answer('Q02', 'B'); await h.loader.refresh();
  const request = h.loader.load('S01'); await turn(); h.loader.cancel();
  assert.equal(h.calls.at(-1).options.signal.aborted, true);
  pending.resolve(stage === 'response' ? response(data) : data);
  assert.deepEqual(await request, { ok: false, cancelled: true });
  assert.equal(h.session.mode, 'demo'); assert.equal(h.session.count, 1); assert.equal(h.commits.length, 0);
});

test('out-of-order unit responses cannot replace the newer validated unit', async () => {
  const a = fixture(), b = fixture(2, 'S02'), pending = deferred();
  const h = harness({ 'manifest.json': manifest(a, b), 'S01.json': () => pending.promise, 'S02.json': b });
  await h.loader.refresh(); const old = h.loader.load('S01'); await turn();
  await h.loader.load('S02'); h.session.answer('Q02', 'C');
  pending.resolve(response(a)); assert.equal((await old).cancelled, true);
  assert.equal(h.session.unitId, 'S02'); assert.equal(h.session.count, 1); assert.deepEqual(h.commits, ['S02']);
});

test('out-of-order manifest responses cannot restore an obsolete publication list', async () => {
  const pending = deferred(), h = harness({ 'manifest.json': () => pending.promise });
  const old = h.loader.refresh(); await turn();
  h.files['manifest.json'] = manifest(fixture(2, 'S02')); await h.loader.refresh();
  pending.resolve(response(manifest(fixture()))); assert.equal((await old).cancelled, true);
  assert.deepEqual(h.loader.units.map(unit => unit.unitId), ['S02']);
});

test('refreshing the manifest invalidates a pending unit and retains the old attempt', async () => {
  const data = fixture(), pending = deferred(), h = harness({ 'manifest.json': manifest(data), 'S01.json': () => pending.promise });
  h.session.answer('Q02', 'B'); await h.loader.refresh();
  const request = h.loader.load('S01'); await turn();
  h.files['manifest.json'] = manifest(); await h.loader.refresh();
  pending.resolve(response(data)); assert.equal((await request).cancelled, true);
  assert.equal(h.session.mode, 'demo'); assert.equal(h.session.count, 1);
});
