import { nearestRoads } from './city-config.js';
import { EDUCATION_START } from './education-config.js';

export const NEARBY_LIMIT = 20;
const groundModes = new Set(['person', 'car', 'cyclist']);
const bodies = { person: [0.48, 0.48], car: [0.86, 2.18], cyclist: [0.65, 1] };

// Extra arrival checks only; the original traffic, collision grids and physics are not changed.
export function trafficOccupies(point, heading, mode, groundY, actors) {
  const [w, l] = bodies[mode];
  for (const actor of actors) {
    if (!(actor.edge || actor.placed) || ![actor.x, actor.z].every(Number.isFinite)) continue;
    if (Math.abs((actor.y ?? 0) - groundY) > 2.5) continue;
    const aw = actor.rig ? 0.4 : actor.halfWidth ?? 0.92;
    const al = actor.rig ? 0.4 : actor.half ?? 2.3;
    const dx = point.x - actor.x, dz = point.z - actor.z;
    if (Math.hypot(dx, dz) > Math.hypot(w, l) + Math.hypot(aw, al) + 0.4) continue;
    const h = (actor.yaw ?? 0) + (actor.yawOffset ?? 0);
    const right = [Math.cos(heading), -Math.sin(heading)], forward = [Math.sin(heading), Math.cos(heading)];
    const ar = [Math.cos(h), -Math.sin(h)], af = [Math.sin(h), Math.cos(h)];
    const dot = (a, b) => a[0] * b[0] + a[1] * b[1];
    if ([right, forward, ar, af].every(axis => Math.abs(dx * axis[0] + dz * axis[1]) <
      w * Math.abs(dot(axis, right)) + l * Math.abs(dot(axis, forward)) +
      aw * Math.abs(dot(axis, ar)) + al * Math.abs(dot(axis, af)) + 0.3)) return true;
  }
  return false;
}

function suitableSurface(manager, point) {
  if (manager.activeMode === 'person') return manager.isPointOnSidewalk(point.x, point.z);
  const margin = manager.activeMode === 'car' ? 2.5 : 1;
  return !manager.isPointOnSidewalk(point.x, point.z) && nearestRoads(point.x, point.z, 20)
    .some(({ road, dist }) => dist + margin < road.w / 2);
}

export function nearbyArrival(manager, anchor, actors = []) {
  if (![anchor.x, anchor.z, anchor.heading].every(Number.isFinite)) return null;
  const seeds = [{ x: anchor.x, z: anchor.z }];
  for (let radius = 4; radius <= NEARBY_LIMIT; radius += 4) {
    for (let i = 0; i < 16; i++) {
      seeds.push({ x: anchor.x + Math.cos(i * Math.PI / 8) * radius, z: anchor.z + Math.sin(i * Math.PI / 8) * radius });
    }
  }
  for (const seed of seeds) {
    if (!suitableSurface(manager, seed)) continue;
    // Preflight the original search, rejecting its potentially distant fallback before any entity moves.
    const p = manager.findTeleportPosition(seed.x, seed.z, anchor.heading, 0);
    if (!p || Math.hypot(p.x - anchor.x, p.z - anchor.z) > NEARBY_LIMIT || !suitableSurface(manager, p)) continue;
    const y = manager.getGroundHeight(p.x, p.z, manager.activeMode);
    if (!trafficOccupies(p, anchor.heading, manager.activeMode, y, actors)) return p;
  }
  return null;
}

export function createEducationNavigation({ manager, teleport, getActors, isBlocked, onStatus }) {
  function relocate(mode, anchor, returning) {
    const previous = manager.activeMode;
    manager.setMode(mode);
    let committed = false;
    try {
      const point = nearbyArrival(manager, anchor, getActors());
      if (!point) {
        onStatus(`No clear ${mode === 'person' ? 'walking area' : 'roadway'} within 20 m${returning ? ' of start' : ''}. Position and progress kept; try again near an open street.`, false);
        return { ok: false };
      }
      // Preflight and placement are synchronous: the validated point stays clear for the shared teleport call.
      teleport(point.x, point.z, anchor.heading);
      committed = true;
      onStatus(returning ? 'Returned near start. Question progress kept.' : `${manager.getActiveEntity().label} placed nearby. Question progress kept.`, true);
      return { ok: true, relocated: true };
    } finally {
      if (!committed) manager.setMode(previous);
    }
  }
  return Object.freeze({
    switchMode(mode) {
      if (isBlocked() || !Object.hasOwn(manager.entities, mode)) return { ok: false };
      const previous = manager.activeMode;
      if (mode === previous) return { ok: true, relocated: false };
      if (groundModes.has(previous) && groundModes.has(mode)) {
        const entity = manager.getActiveEntity();
        return relocate(mode, { x: entity.position.x, z: entity.position.z, heading: entity.heading }, false);
      }
      manager.setMode(mode); // Helicopter transitions retain the selected entity's independent location.
      manager.resetInput();
      return { ok: true, relocated: false };
    },
    returnToStart() {
      if (isBlocked()) return { ok: false };
      return relocate(manager.activeMode === 'helicopter' ? 'car' : manager.activeMode, EDUCATION_START, true);
    }
  });
}
