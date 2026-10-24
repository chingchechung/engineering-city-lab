import assert from 'node:assert/strict';
import test from 'node:test';
import { readFileSync } from 'node:fs';
import { loadModule } from './helpers/module.cjs';
import * as config from '../js/city-config.js';
import { EDUCATION_START, TERMINALS } from '../js/education-config.js';
import { createEducationNavigation, nearbyArrival, trafficOccupies, NEARBY_LIMIT } from '../js/education-navigation.js';

const { ThirdPersonControllerManager } = loadModule(readFileSync(new URL('../js/controllers.js', import.meta.url), 'utf8'), {
  imports: { 'three/webgpu': {}, './city-config.js': config, './tsl-materials.js': {}, './actor-models.js': {},
    './pedestrians.js': {}, './vehicle-lights.js': {}, './landmarks.js': {} }
});
function vector(x = 0, y = 0, z = 0) {
  return { x, y, z, copy(p) { Object.assign(this, {x:p.x,y:p.y,z:p.z}); } };
}
function harness(mode = 'car', colliders = []) {
  const manager = Object.create(ThirdPersonControllerManager.prototype);
  manager.colliders = colliders;
  manager._colliderCells = null;
  manager.activeMode = mode;
  manager.resetInput = () => { manager.keys = {}; };
  const pivot = () => ({ position: vector(), rotation: {} });
  manager.entities = Object.fromEntries(['car', 'person', 'cyclist', 'helicopter'].map((type, i) => [type, {
    type, label: type, position: vector(i * 30 - 90, type === 'helicopter' ? 96 : 0, 600), heading: 0,
    chaseDistance: 6.9, chaseHeight: 2.12, mesh: pivot(), speed: 12, vx: 3, vz: -4,
    chassisPivot: pivot(), wheels: [], leanPivot: pivot(), tiltPivot: pivot(),
    rig: { reset() {} }, crowd: { begin() {}, add() {}, end() {} }
  }]));
  const calls = [], messages = [];
  let blocked = false, actors = [];
  const nav = createEducationNavigation({
    manager, getActors: () => actors, isBlocked: () => blocked,
    teleport(x, z, heading) { calls.push({mode:manager.activeMode,x,z,heading}); return manager.teleportActiveTo(x,z,heading); },
    onStatus(message, ok) { messages.push({ message, ok }); }
  });
  return { manager, nav, calls, messages, block: value => blocked = value, actors: value => actors = value };
}
function place(entity, x, z, y = 0, heading = 0) { Object.assign(entity.position, {x,y,z}); entity.heading = heading; }
const distance = (a,b) => Math.hypot(a.x-b.x,a.z-b.z);

test('terminal sidewalks cover Fifth Avenue and three nearby cross streets with short walking routes', () => {
  const names = new Set();
  for (const t of TERMINALS) {
    const b = config.blockAt(t.x,t.z);
    assert.ok(b, `${t.id} is on a sidewalk island`);
    assert.ok(!b.rects.some(([x0,x1,z0,z1])=>t.x>=x0 && t.x<=x1 && t.z>=z0 && t.z<=z1), `${t.id} is outside building lots`);
    names.add(config.nearestRoads(t.x,t.z,20)[0].road.name);
    const route = Math.abs(EDUCATION_START.x-11) + Math.abs(EDUCATION_START.z-t.z) + Math.abs(11-t.x);
    assert.ok(route<250,`${t.id}: sidewalk-route estimate ${route}`);
  }
  assert.ok(names.has('5th Ave'));
  assert.ok([...names].some(n=>n.includes('36th')) && [...names].some(n=>n.includes('37th')) && [...names].some(n=>n.includes('38th')));
  assert.ok(TERMINALS.some(t=>distance(t,EDUCATION_START)<18));
});

for (const from of ['car','person','cyclist']) for (const to of ['car','person','cyclist'].filter(t=>t!==from)) {
  test(`${from} -> ${to} uses production safe placement within 20 m and clears destination motion`, () => {
    const h=harness(from); const source=h.manager.entities[from];
    place(source,from==='person'?11:3.6,410.6,from==='person'?0.22:0);
    const origin={...source.position};
    assert.ok(h.nav.switchMode(to).ok);
    assert.equal(h.manager.activeMode,to);
    assert.ok(distance(h.manager.entities[to].position,origin)<=NEARBY_LIMIT);
    assert.deepEqual({...source.position},origin,'source remains parked at its current location during the transaction');
    assert.equal(h.calls.length,1);
    assert.equal(h.manager.entities[to].speed,0);
    if(to==='car') assert.deepEqual([h.manager.entities[to].vx,h.manager.entities[to].vz],[0,0]);
  });
}

test('switching near Central Park stays near the current car, not the original spawn', () => {
  const h=harness(); const start=config.TELEPORT_LOCATIONS.centralpark;
  place(h.manager.entities.car,start.x,start.z);
  assert.ok(h.nav.switchMode('person').ok);
  const p=h.manager.getActiveEntity().position;
  assert.ok(distance(p,start)<=20);
  assert.ok(distance(p,EDUCATION_START)>1000);
});

test('nearby arrival reuses real building clearance and avoids an occupied road', () => {
  const wall={minX:1,maxX:6,minZ:406,maxZ:416,maxY:20};
  const h=harness('person',[wall]); place(h.manager.entities.person,11,410.6,0.22);
  h.actors([{edge:{},x:3.6,z:420,yaw:0,half:2.3,halfWidth:0.9}]);
  assert.ok(h.nav.switchMode('car').ok);
  const p=h.manager.entities.car.position;
  assert.ok(distance(p,{x:11,z:410.6})<=20);
  assert.deepEqual({...h.manager.findTeleportPosition(p.x,p.z,0,0)},{x:p.x,z:p.z});
  assert.equal(trafficOccupies(p,0,'car',0,[{edge:{},x:3.6,z:420,yaw:0,half:2.3,halfWidth:0.9}]),false);
});

test('traffic arrival checks account for rotated buses, unplaced actors and elevation', () => {
  const bus={edge:{},x:3.6,z:410.6,yaw:Math.PI/2,half:5.72,halfWidth:1.3};
  assert.equal(trafficOccupies({x:8,z:410.6},0,'car',0,[bus]),true);
  assert.equal(trafficOccupies({x:8,z:420},0,'car',0,[bus]),false);
  assert.equal(trafficOccupies({x:8,z:410.6},0,'car',0,[{...bus,y:10}]),false);
  assert.equal(trafficOccupies({x:8,z:410.6},0,'car',0,[{...bus,edge:null}]),false);
});

test('distant original-search fallbacks are rejected before any entity moves', () => {
  const h=harness('person'); place(h.manager.entities.person,11,410.6,0.22);
  const before=JSON.stringify(h.manager.entities);
  h.manager.findTeleportPosition=(x,z)=>({x:x+300,z});
  assert.equal(h.nav.switchMode('car').ok,false);
  assert.equal(h.manager.activeMode,'person');
  assert.equal(JSON.stringify(h.manager.entities),before);
  assert.equal(h.calls.length,0);
  assert.match(h.messages.at(-1).message,/20 m/);
  assert.equal(h.messages.at(-1).ok,false);
});

test('helicopter transitions keep all entity locations independent; repeated selection does not relocate', () => {
  const h=harness(); const before=JSON.stringify(h.manager.entities);
  assert.ok(h.nav.switchMode('helicopter').ok);
  assert.ok(h.nav.switchMode('person').ok);
  assert.ok(h.nav.switchMode('person').ok);
  assert.equal(h.calls.length,0);
  assert.equal(JSON.stringify(h.manager.entities),before);
});

for (const mode of ['car','person','cyclist','helicopter']) {
  test(`Return to Start from far-away ${mode} uses a safe nearby arrival and stops motion`, () => {
    const h=harness(mode), far=config.TELEPORT_LOCATIONS.centralpark;
    place(h.manager.entities[mode],far.x,far.z,mode==='helicopter'?150:0);
    assert.ok(h.nav.returnToStart().ok);
    assert.equal(h.manager.activeMode,mode==='helicopter'?'car':mode);
    assert.ok(distance(h.manager.getActiveEntity().position,EDUCATION_START)<=20);
    assert.equal(h.manager.getActiveEntity().speed,0);
    assert.equal(h.calls.length,1);
    assert.match(h.messages.at(-1).message,/progress kept/);
  });
}

test('failed Return from helicopter restores its original mode/location with feedback', () => {
  const h=harness('helicopter'),before=JSON.stringify(h.manager.entities);
  h.manager.findTeleportPosition=()=>null;
  assert.equal(h.nav.returnToStart().ok,false);
  assert.equal(h.manager.activeMode,'helicopter');
  assert.equal(JSON.stringify(h.manager.entities),before);
  assert.equal(h.calls.length,0);
  assert.equal(h.messages.at(-1).ok,false);
});

test('dialog guard prevents mode changes and Return before placement or feedback', () => {
  const h=harness();h.block(true);
  assert.equal(h.nav.switchMode('person').ok,false);
  assert.equal(h.nav.returnToStart().ok,false);
  assert.equal(h.manager.activeMode,'car');
  assert.equal(h.calls.length,0);
  assert.equal(h.messages.length,0);
});
