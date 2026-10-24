import * as THREE from 'three/webgpu';
import { TERMINALS } from './education-config.js';

export function createEducationTerminals(scene) {
  const group = new THREE.Group();
  group.name = 'EducationDemoTerminals';
  const stand = new THREE.BoxGeometry(0.55, 1.25, 0.45);
  const screen = new THREE.BoxGeometry(0.95, 0.65, 0.2);
  const standMaterial = new THREE.MeshStandardNodeMaterial({ color: 0x202830, roughness: 0.85 });
  const screens = new Map();
  const markers = new Map();
  function drawLabel(ctx, id, caption) {
    ctx.fillStyle = '#18212a'; ctx.fillRect(0, 0, 256, 160);
    ctx.fillStyle = '#ffffff'; ctx.textAlign = 'center';
    ctx.font = 'bold 68px sans-serif'; ctx.fillText(id, 128, 85);
    ctx.fillStyle = '#ffc21a'; ctx.font = 'bold 28px sans-serif'; ctx.fillText(caption, 128, 130);
  }
  for (const terminal of TERMINALS) {
    const root = new THREE.Group();
    root.name = `DemoTerminal-${terminal.id}`;
    root.position.set(terminal.x, terminal.y, terminal.z);
    const post = new THREE.Mesh(stand, standMaterial);
    post.position.y = 0.625;
    const material = new THREE.MeshStandardNodeMaterial({ color: 0xffc21a, roughness: 0.6 });
    const head = new THREE.Mesh(screen, material);
    head.position.y = 1.5;
    const canvas = document.createElement('canvas');
    canvas.width = 256; canvas.height = 160;
    const ctx = canvas.getContext('2d');
    drawLabel(ctx, terminal.id, 'DEMO');
    const texture = new THREE.CanvasTexture(canvas);
    texture.colorSpace = THREE.SRGBColorSpace;
    const label = new THREE.Sprite(new THREE.SpriteNodeMaterial({ map: texture }));
    label.position.y = 2.1;
    label.scale.set(1.25, 0.78, 1);
    root.add(post, head, label);
    group.add(root);
    screens.set(terminal.id, material);
    markers.set(terminal.id, { root, ctx, texture, material });
  }
  scene.add(group);
  return {
    markPassed(id) { screens.get(id)?.color.setHex(0x5ee08f); },
    setSession(session) {
      for (const [id, { root, ctx, texture, material }] of markers) {
        root.visible = Boolean(session.question(id));
        material.color.setHex(session.hasPassed(id) ? 0x5ee08f : 0xffc21a);
        drawLabel(ctx, id, session.mode === 'demo' ? 'DEMO' : session.unitId);
        texture.needsUpdate = true;
      }
    }
  };
}
