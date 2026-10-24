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
  const selector = document.getElementById('assignment-dialog');
  const form = document.getElementById('education-answer');
  const options = document.getElementById('education-options');
  const feedback = document.getElementById('education-feedback');
  const pressed = new Set(), suppressed = new Set();
  let current = null, previousFocus = null, owner = null;
  const isDemo = () => session.mode !== 'assignment';
  const questions = () => session.questions ?? DEMO_QUESTIONS;
  const modalOpen = () => dialog.open || Boolean(selector?.open);

  function renderProgress() {
    const total = questions().length;
    document.getElementById('education-session-label').textContent = isDemo() ? 'Demo Mode · synthetic data' : `${session.unitId} · ${session.unit.title}`;
    panel.setAttribute('aria-label', isDemo() ? 'Synthetic question demo' : 'Assignment progress');
    progress.textContent = `${session.count} / ${total} ${isDemo() ? 'demo ' : ''}questions completed`;
    completion.textContent = isDemo() ? 'Demo complete! All five questions passed. Continue exploring the city.'
      : `${session.unitId} complete! All ${total} questions passed. Continue exploring the city.`;
    completion.hidden = !session.complete;
  }

  function pauseForModal(modal) {
    if (owner) return;
    previousFocus = document.activeElement;
    for (const pop of document.querySelectorAll('.popover[popover]')) {
      if (pop.matches(':popover-open')) pop.hidePopover();
    }
    owner = modal;
    onPause();
  }

  function open(terminal) {
    current = questions().find(q => q.id === terminal.id);
    if (!current) return;
    document.getElementById('education-demo-note').textContent = isDemo() ? 'Synthetic interaction demo · not actual coursework' : `${session.unitId} · validated assignment`;
    document.getElementById('education-title').textContent = `${current.id}${current.title ? ' · ' + current.title : ''}`;
    document.getElementById('education-question').textContent = current.prompt ?? '';
    options.replaceChildren();
    current.options.forEach((text, index) => {
      const label = document.createElement('label');
      const radio = document.createElement('input');
      radio.type = 'radio'; radio.name = 'demo-answer'; radio.value = 'ABCD'[index]; radio.required = true;
      const caption = document.createElement('span');
      caption.textContent = `${radio.value}. ${text}`;
      label.append(radio, caption); options.append(label);
    });
    feedback.textContent = session.hasPassed(current.id) ? `Already completed. You can review this ${isDemo() ? 'demo ' : ''}question.` : '';
    feedback.dataset.result = session.hasPassed(current.id) ? 'correct' : '';
    pauseForModal(dialog);
    dialog.showModal();
    options.querySelector('input').focus({ preventScroll: true });
    prompt.hidden = true;
  }

  function cleanup(modal = dialog) {
    if (owner !== modal) return;
    owner = null;
    current = null;
    for (const code of pressed) suppressed.add(code);
    onResume();
    if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
  }
  function close() { dialog.close(); cleanup(); }
  dialog.addEventListener('close', () => cleanup(dialog));
  dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
  document.getElementById('education-close').addEventListener('click', close);
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!dialog.open || !current) return;
    const choice = new FormData(form).get('demo-answer');
    if (typeof choice !== 'string') { feedback.textContent = 'Choose one answer first.'; return; }
    const correct = session.answer(current.id, choice);
    feedback.dataset.result = correct ? 'correct' : 'incorrect';
    feedback.textContent = correct ? `Correct! This ${isDemo() ? 'demo ' : ''}question is completed.` : 'Incorrect. Try again; your completed questions are kept.';
    if (correct) onPassed(current.id);
    renderProgress();
  });

  // Capture before the original window-level movement/map/camera listeners.
  window.addEventListener('keydown', event => {
    pressed.add(event.code);
    if (modalOpen()) {
      event.stopImmediatePropagation();
      if (event.code === 'Escape' && dialog.open) { event.preventDefault(); close(); }
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
    if (suppressed.delete(event.code) || modalOpen()) event.stopImmediatePropagation();
  }, true);
  const clear = () => { pressed.clear(); suppressed.clear(); };
  window.addEventListener('blur', clear);
  document.addEventListener('visibilitychange', () => { if (document.hidden) clear(); });
  renderProgress();
  return {
    get isOpen() { return modalOpen(); },
    pauseForSelector() { pauseForModal(selector); },
    resumeFromSelector() { cleanup(selector); },
    refresh() { renderProgress(); this.update(); },
    update() {
      const show = available();
      panel.hidden = !show;
      const nearby = show && !modalOpen() ? getNearby() : null;
      prompt.hidden = !nearby;
      if (nearby) prompt.textContent = `Press X to answer ${nearby.id}${session.hasPassed(nearby.id) ? ' · completed' : ''}`;
    }
  };
}
