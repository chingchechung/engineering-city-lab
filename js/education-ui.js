import { DEMO_QUESTIONS } from './education-session.js';

function typing(target) {
  return target?.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(target?.tagName);
}

// Project the existing validated session into link availability; never track a second completion state.
export function questionResources(session, question) {
  const active = session.mode === 'assignment' && session.questions.includes(question);
  const passed = active && session.hasPassed(question.id);
  return {
    questionVideoUrl: active ? question.questionVideoUrl : null,
    explanationVideoUrl: passed ? question.explanationVideoUrl : null,
    explanationText: passed && question.explanationText?.trim() ? question.explanationText : null
  };
}

export function completionFormUrl(session) {
  return session.mode === 'assignment' && session.complete ? session.unit.googleFormUrl : null;
}

export function createEducationUI({ session, getNearby, available, progressAvailable = available, onPause, onResume, onPassed }) {
  const panel = document.getElementById('education-hud');
  const prompt = document.getElementById('education-prompt');
  const progress = document.getElementById('education-progress');
  const completion = document.getElementById('education-completion');
  const dialog = document.getElementById('education-dialog');
  const selector = document.getElementById('assignment-dialog');
  const form = document.getElementById('education-answer');
  const options = document.getElementById('education-options');
  const feedback = document.getElementById('education-feedback');
  const questionVideo = document.getElementById('education-question-video');
  const explanation = document.getElementById('education-explanation');
  const explanationVideo = document.getElementById('education-explanation-video');
  const explanationTextSection = document.getElementById('education-explanation-text-section');
  const explanationText = document.getElementById('education-explanation-text');
  const formLinks = [document.getElementById('education-unit-form'), document.getElementById('education-dialog-form')];
  const pressed = new Set(), suppressed = new Set();
  let current = null, previousFocus = null, owner = null;
  const isDemo = () => session.mode !== 'assignment';
  const questions = () => session.questions ?? DEMO_QUESTIONS;
  const modalOpen = () => dialog.open || Boolean(selector?.open);

  function setLink(element, url) {
    element.hidden = !url;
    if (url) element.setAttribute('href', url);
    else element.removeAttribute('href');
  }
  function renderResources() {
    const resources = questionResources(session, current);
    setLink(questionVideo, resources.questionVideoUrl);
    setLink(explanationVideo, resources.explanationVideoUrl);
    explanation.hidden = !resources.explanationVideoUrl;
    explanationTextSection.hidden = !resources.explanationText;
    explanationText.textContent = resources.explanationText ?? '';
  }
  function renderProgress() {
    const total = questions().length;
    document.getElementById('education-session-label').textContent = isDemo() ? 'Demo Mode · synthetic data' : `${session.unitId} · ${session.unit.title}`;
    panel.setAttribute('aria-label', isDemo() ? 'Synthetic question demo' : 'Assignment progress');
    progress.textContent = `${session.count} / ${total} ${isDemo() ? 'demo ' : ''}questions completed`;
    completion.textContent = isDemo() ? 'Demo complete! All five questions passed. Continue exploring the city.'
      : `${session.unitId} complete! All ${total} questions passed. Continue exploring the city.`;
    completion.hidden = !session.complete;
    for (const link of formLinks) setLink(link, completionFormUrl(session));
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
    renderResources();
    pauseForModal(dialog);
    dialog.showModal();
    options.querySelector('input').focus({ preventScroll: true });
    prompt.hidden = true;
  }

  function cleanup(modal = dialog) {
    if (owner !== modal) return;
    owner = null;
    current = null;
    renderResources();
    for (const code of pressed) suppressed.add(code);
    onResume();
    if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
  }
  function close() { dialog.close(); cleanup(); }
  dialog.addEventListener('close', () => { if (!dialog.open) cleanup(dialog); }); // Ignore an older queued close after a rapid reopen.
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
    renderResources();
  });

  // Keep native link navigation while stopping Enter/Space from reaching city controls in the HUD.
  for (const type of ['keydown', 'keyup']) formLinks[0].addEventListener(type, event => {
    if (event.code === 'Enter' || event.code === 'Space') event.stopPropagation();
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
  renderResources();
  return {
    get isOpen() { return modalOpen(); },
    pauseForSelector() { pauseForModal(selector); },
    resumeFromSelector() { cleanup(selector); },
    refresh() { renderProgress(); renderResources(); this.update(); },
    update() {
      const canInteract = available();
      const show = canInteract || (progressAvailable() && Boolean(completionFormUrl(session)));
      panel.hidden = !show;
      panel.classList.toggle('education-over-map', show && !canInteract);
      const nearby = canInteract && !modalOpen() ? getNearby() : null;
      prompt.hidden = !nearby;
      if (nearby) prompt.textContent = `Press X to answer ${nearby.id}${session.hasPassed(nearby.id) ? ' · completed' : ''}`;
    }
  };
}
