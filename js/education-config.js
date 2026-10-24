// Fixed city extension settings. This module does not read storage or alter city geometry.
export const EDUCATION_START = Object.freeze({ x: 3.6, y: 0, z: 410.6, heading: 0 });
export const TERMINALS = Object.freeze([
  { id: 'Q01', x: -12, y: 0.22, z: 422.6 },
  { id: 'Q02', x: 11, y: 0.22, z: 422.6 }, // 1 m toward the street: clears the facade in the rendered survey.
  { id: 'Q03', x: -12, y: 0.22, z: 442.6 },
  { id: 'Q04', x: 12, y: 0.22, z: 442.6 },
  { id: 'Q05', x: -12, y: 0.22, z: 462.6 }
].map(Object.freeze));
export const INTERACTION = Object.freeze({
  radius: Object.freeze({ person: 3, car: 18, cyclist: 8 }),
  maxSpeed: 0.5,
  maxGroundOffset: 0.6,
  maxSurfaceDifference: 0.75
});

export function initializeEducationStart(manager) {
  const car = manager.entities.car;
  car.position.set(EDUCATION_START.x, EDUCATION_START.y, EDUCATION_START.z);
  car.heading = EDUCATION_START.heading;
  car.mesh.position.copy(car.position);
  car.mesh.rotation.y = car.heading;
  manager.setMode('car');
}

// Segment vs solid bounds, including the city's oriented building footprints.
// Sample at interaction height so curbs/ground do not block a sidewalk terminal.
export function hasClearApproach(from, terminal, colliders) {
  for (const c of colliders) {
    let ax = from.x, az = from.z, bx = terminal.x, bz = terminal.z;
    let minX = c.minX, maxX = c.maxX, minZ = c.minZ, maxZ = c.maxZ;
    if (c.obb) {
      const o = c.obb, x0 = ax - o.cx, z0 = az - o.cz, x1 = bx - o.cx, z1 = bz - o.cz;
      ax = x0 * o.cs - z0 * o.sn; az = x0 * o.sn + z0 * o.cs;
      bx = x1 * o.cs - z1 * o.sn; bz = x1 * o.sn + z1 * o.cs;
      minX = -o.hx; maxX = o.hx; minZ = -o.hz; maxZ = o.hz;
    }
    let enter = 0, exit = 1;
    for (const [a, b, lo, hi] of [
      [ax, bx, minX, maxX], [az, bz, minZ, maxZ],
      [from.y + 1.2, terminal.y + 1.35, c.minY ?? 0, c.maxY]
    ]) {
      const d = b - a;
      if (Math.abs(d) < 1e-8) {
        if (a <= lo || a >= hi) { exit = -1; break; }
      } else {
        const t0 = (lo - a) / d, t1 = (hi - a) / d;
        enter = Math.max(enter, Math.min(t0, t1));
        exit = Math.min(exit, Math.max(t0, t1));
      }
    }
    if (enter < exit && exit > 0 && enter < 1) return false;
  }
  return true;
}

export function nearestTerminal(entity, mode, groundHeight, colliders = [], settings = INTERACTION) {
  const radius = settings.radius[mode];
  if (!Number.isFinite(radius) || radius <= 0 || !entity || !Number.isFinite(groundHeight)) return null;
  const p = entity.position;
  if (![p.x, p.y, p.z].every(Number.isFinite) || Math.abs(p.y - groundHeight) > settings.maxGroundOffset) return null;
  if (mode !== 'person') {
    const h = entity.heading, speed = entity.speed;
    const actualSpeed = Math.hypot(Math.sin(h) * speed + (entity.vx ?? 0), Math.cos(h) * speed + (entity.vz ?? 0));
    if (!Number.isFinite(actualSpeed) || actualSpeed > settings.maxSpeed) return null;
  }
  let best = null, distance = radius;
  for (const terminal of TERMINALS) {
    const d = Math.hypot(p.x - terminal.x, p.z - terminal.z);
    if (d > distance || Math.abs(groundHeight - terminal.y) > settings.maxSurfaceDifference) continue;
    if (!hasClearApproach(p, terminal, colliders)) continue;
    if (!best || d < distance) { best = terminal; distance = d; }
  }
  return best;
}
