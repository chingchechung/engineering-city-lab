import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import { EDUCATION_START, INTERACTION, TERMINALS, initializeEducationStart, nearestTerminal, hasClearApproach } from '../js/education-config.js';
import { createDemoSession, DEMO_QUESTIONS } from '../js/education-session.js';

const entity = (x, z, y = 0.22, speed = 0) => ({ position: { x, y, z }, heading: 0, speed, vx: 0, vz: 0 });

test('five immutable sites match the reviewed fixed coordinates and demo IDs', () => {
  assert.deepEqual(TERMINALS.map(({ id, x, z }) => [id, x, z]), [
    ['Q01', -12, 422.6], ['Q02', 11, 422.6], ['Q03', -12, 442.6], ['Q04', 12, 442.6], ['Q05', -12, 462.6]
  ]);
  assert.deepEqual(DEMO_QUESTIONS.map(q => q.id), TERMINALS.map(t => t.id));
  assert.ok(Object.isFrozen(TERMINALS) && TERMINALS.every(Object.isFrozen));
});

for (const [mode, radius] of [['person', 3], ['car', 18], ['cyclist', 8]]) {
  test(`${mode} uses horizontal proximity at its configured radius`, () => {
    assert.equal(INTERACTION.radius[mode], radius);
    assert.equal(nearestTerminal(entity(-12 - radius, 422.6), mode, 0.22)?.id, 'Q01');
    assert.equal(nearestTerminal(entity(-12 - radius - 0.01, 422.6), mode, 0.22), null);
  });
}

test('helicopter answering is disabled even at sidewalk height', () => {
  assert.equal(nearestTerminal(entity(-12, 422.6), 'helicopter', 0.22), null);
});

test('car overlaps select the nearest terminal, with stable ties', () => {
  assert.equal(nearestTerminal(entity(3.6, 410.6, 0), 'car', 0)?.id, 'Q02');
  assert.equal(nearestTerminal(entity(-10, 440), 'car', 0)?.id, 'Q03');
  assert.equal(nearestTerminal(entity(-0.5, 422.6), 'car', 0)?.id, 'Q01');
});

for (const mode of ['car', 'cyclist']) {
  test(`${mode} must stop, including sideways impulse velocity`, () => {
    assert.equal(nearestTerminal(entity(-12, 422.6, 0, 0.5), mode, 0)?.id, 'Q01');
    assert.equal(nearestTerminal(entity(-12, 422.6, 0, -0.51), mode, 0), null);
    const pushed = { ...entity(-12, 422.6, 0), vx: 0.7 };
    assert.equal(nearestTerminal(pushed, mode, 0), null);
    assert.equal(nearestTerminal({ ...pushed, vx: NaN }, mode, 0), null);
  });
}

test('jumping, elevated surfaces and invalid positions cannot answer ground questions', () => {
  assert.equal(nearestTerminal(entity(-12, 422.6, 10), 'car', 0), null);
  assert.equal(nearestTerminal(entity(-12, 422.6, 10), 'person', 10), null);
  assert.equal(nearestTerminal(entity(-12, 422.6, 1.2), 'person', 0.22), null);
  assert.equal(nearestTerminal(entity(NaN, 422.6), 'person', 0.22), null);
});

test('solid buildings block approach, low curbs and clear oriented corners do not', () => {
  const from = { x: -15, y: 0.22, z: 422.6 }, target = TERMINALS[0];
  const wall = { minX: -14, maxX: -13, minZ: 420, maxZ: 425, maxY: 8 };
  assert.equal(hasClearApproach(from, target, [wall]), false);
  assert.equal(hasClearApproach(from, target, [{ ...wall, maxY: 0.22 }]), true);
  const box = { minX: -16, maxX: -10, minZ: 419, maxZ: 426, maxY: 8,
    obb: { cx: -13.5, cz: 425, cs: Math.SQRT1_2, sn: Math.SQRT1_2, hx: 0.3, hz: 0.3 } };
  assert.equal(hasClearApproach(from, target, [box]), true);
});

test('blocked nearest site is excluded while another clear site can be selected', () => {
  const obstacle = { minX: 5, maxX: 6, minZ: 420, maxZ: 425, maxY: 8 };
  assert.equal(nearestTerminal(entity(0, 422.6), 'car', 0, [obstacle])?.id, 'Q01');
});

test('incorrect and malformed answers retain all prior completions; each pass is idempotent', () => {
  const session = createDemoSession();
  assert.equal(session.answer('Q01', 'A'), true);
  assert.equal(session.answer('Q02', 'A'), false);
  assert.equal(session.count, 1);
  assert.equal(session.answer('Q01', 'C'), false);
  assert.ok(session.hasPassed('Q01'));
  for (const label of [['A'], null, 'a', '', 'D']) assert.equal(session.answer('Q01', label), false);
  assert.equal(session.answer('missing', 'A'), false);
  assert.equal(session.answer('Q01', 'A'), true);
  assert.equal(session.count, 1);
  assert.equal(session.complete, false);
  for (const question of DEMO_QUESTIONS) session.answer(question.id, question.answer);
  assert.equal(session.count, 5);
  assert.equal(session.complete, true);
  assert.equal(createDemoSession().count, 0, 'new browser sessions have independent in-memory progress');
});

function vector(x, y, z) {
  return { x, y, z, set(x, y, z) { Object.assign(this, { x, y, z }); }, copy(p) { this.set(p.x, p.y, p.z); } };
}
const main = readFileSync(new URL('../js/main.js', import.meta.url), 'utf8');
test('production startup ignores stale storage and preserves independent other-mode locations', () => {
  const source = main.slice(main.indexOf('  const controllerManager = new ThirdPersonControllerManager'), main.indexOf('  function savePlayerState'));
  let reads = 0;
  const run = vm.runInNewContext(`(function() { ${source}; return controllerManager; })`, {
    scene: {}, allColliders: [], initializeEducationStart, createEducationTerminals: () => ({}),
    localStorage: { getItem() { reads++; return JSON.stringify({ version: 1, activeMode: 'helicopter', entities: { car: { x: 900, y: 0, z: 900, heading: 3 } } }); } },
    ThirdPersonControllerManager: class {
      constructor() {
        this.entities = Object.fromEntries(['car', 'person', 'cyclist', 'helicopter'].map((mode, i) => [mode, {
          position: vector(i, i + 1, i + 2), heading: i, mesh: { position: vector(0, 0, 0), rotation: {} }
        }]));
      }
      setMode(mode) { this.activeMode = mode; }
    }
  });
  const manager = run();
  assert.equal(reads, 0);
  assert.equal(manager.activeMode, 'car');
  assert.deepEqual([manager.entities.car.position.x, manager.entities.car.position.y, manager.entities.car.position.z, manager.entities.car.heading],
    [EDUCATION_START.x, EDUCATION_START.y, EDUCATION_START.z, EDUCATION_START.heading]);
  for (const [mode, i] of [['person', 1], ['cyclist', 2], ['helicopter', 3]]) {
    manager.setMode(mode);
    assert.deepEqual([manager.entities[mode].position.x, manager.entities[mode].position.y, manager.entities[mode].position.z], [i, i + 1, i + 2]);
  }
});

test('production modal frame gate skips physics/traffic/input but continues rendering without catch-up', () => {
  const start = main.indexOf('    // Freeze simulation together');
  const end = main.indexOf('    if (!document.hidden && now >= nextPlayerSave)', start);
  const gate = main.slice(start, end);
  const calls = [];
  const system = name => ({ update: () => calls.push(name) });
  const context = {
    educationUI: { isOpen: true }, elapsed: 10, dt: 0.016,
    gamepadControls: system('input'), controllerManager: { ...system('player'), getActiveEntity: () => ({}) },
    cameraSystem: { ...system('camera'), camera: {}, currentPos: {} },
    trafficSystem: system('traffic'), highwayTraffic: system('highway'), streetDetails: { signalClock: { value: 10 } }
  };
  vm.createContext(context);
  vm.runInContext(gate, context);
  assert.deepEqual(calls, []);
  assert.equal(context.elapsed, 10);
  context.educationUI.isOpen = false;
  vm.runInContext(gate, context);
  assert.deepEqual(calls, ['input', 'player', 'camera', 'traffic', 'highway']);
  assert.equal(context.elapsed, 10.016);
  assert.ok(main.indexOf('lastTime = now;') < start);
  const render = main.slice(end, main.indexOf('    if (!warmedUp) {', end));
  assert.match(render, /educationUI.update\(\)/);
  assert.match(main.slice(main.indexOf('    renderPipeline.render();', end)), /renderPipeline.render\(\)/);
});
