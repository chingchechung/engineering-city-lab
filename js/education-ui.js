import { DEMO_QUESTIONS } from './education-session.js';

function typing(target) {
  return target?.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target?.tagName);
}

export function createEducationUI({ session, getNearby, available, onPause, onResume, onPassed }) {
  const panel = document.getElementById('education-hud');
  const prompt = document.getElementById('education-prompt');
  const progress = document.getElementById('education-progress');
  const completion = document.getElementById('education-completion');
  const dialog = document.getElementById('education-dialog');
  const form = document.getElementById('education-answer');
  const options = document.getElementById('education-options');
  const feedback = document.getElementById('education-feedback');
  const pressed = new Set(), suppressed = new Set();
  let current = null, previousFocus = null, ownsPause = false;

  function renderProgress() {
    progress.textContent = `${session.count} / ${DEMO_QUESTIONS.length} demo questions completed`;
    completion.hidden = !session.complete;
  }

  function open(terminal) {
    current = DEMO_QUESTIONS.find(q => q.id === terminal.id);
    if (!current) return;
    previousFocus = document.activeElement;
    document.getElementById('education-title').textContent = `${current.id} · ${current.title}`;
    document.getElementById('education-question').textContent = current.prompt;
    options.replaceChildren();
    current.options.forEach((text, index) => {
      const label = document.createElement('label');
      const radio = document.createElement('input');
      radio.type = 'radio'; radio.name = 'demo-answer'; radio.value = 'ABCD'[index]; radio.required = true;
      const caption = document.createElement('span');
      caption.textContent = `${radio.value}. ${text}`;
      label.append(radio, caption); options.append(label);
    });
    feedback.textContent = session.hasPassed(current.id) ? 'Already completed. You can review this demo question.' : '';
    feedback.dataset.result = session.hasPassed(current.id) ? 'correct' : '';
    for (const pop of document.querySelectorAll('.popover[popover]')) {
      if (pop.matches(':popover-open')) pop.hidePopover();
    }
    onPause(); ownsPause = true;
    dialog.showModal();
    options.querySelector('input').focus({ preventScroll: true });
    prompt.hidden = true;
  }

  function cleanup() {
    if (!ownsPause) return;
    ownsPause = false;
    current = null;
    for (const code of pressed) suppressed.add(code);
    onResume();
    if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
  }
  function close() { dialog.close(); cleanup(); }
  dialog.addEventListener('close', cleanup);
  dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
  document.getElementById('education-close').addEventListener('click', close);
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!dialog.open || !current) return;
    const choice = new FormData(form).get('demo-answer');
    if (typeof choice !== 'string') { feedback.textContent = 'Choose one answer first.'; return; }
    const correct = session.answer(current.id, choice);
    feedback.dataset.result = correct ? 'correct' : 'incorrect';
    feedback.textContent = correct ? 'Correct! This demo question is completed.' : 'Incorrect. Try again; your completed questions are kept.';
    if (correct) onPassed(current.id);
    renderProgress();
  });

  // Capture before the original window-level movement/map/camera listeners.
  window.addEventListener('keydown', event => {
    pressed.add(event.code);
    if (dialog.open) {
      event.stopImmediatePropagation();
      if (event.code === 'Escape') { event.preventDefault(); close(); }
      return; // Keep native radio, Enter and Tab default actions inside the modal.
    }
    if (suppressed.has(event.code)) { event.preventDefault(); event.stopImmediatePropagation(); return; }
    if (event.code !== 'KeyX' || event.repeat || event.isComposing || event.ctrlKey || event.metaKey || event.altKey || event.shiftKey || typing(event.target)) return;
    if (!available() || document.querySelector('dialog[open]')) return;
    const terminal = getNearby();
    if (terminal) { event.preventDefault(); event.stopImmediatePropagation(); open(terminal); }
  }, true);
  window.addEventListener('keyup', event => {
    pressed.delete(event.code);
    if (suppressed.delete(event.code) || dialog.open) event.stopImmediatePropagation();
  }, true);
  const clear = () => { pressed.clear(); suppressed.clear(); };
  window.addEventListener('blur', clear);
  document.addEventListener('visibilitychange', () => { if (document.hidden) clear(); });
  renderProgress();
  return {
    get isOpen() { return dialog.open; },
    update() {
      const show = available();
      panel.hidden = !show;
      const nearby = show && !dialog.open ? getNearby() : null;
      prompt.hidden = !nearby;
      if (nearby) prompt.textContent = `Press X to answer ${nearby.id}${session.hasPassed(nearby.id) ? ' · completed' : ''}`;
    }
  };
}
