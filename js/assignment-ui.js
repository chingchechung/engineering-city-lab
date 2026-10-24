// The selector shares the question dialog's pause/input/focus ownership.
export function createAssignmentUI({ loader, session, available, onPause, onResume }) {
  const dialog = document.getElementById('assignment-dialog');
  const select = document.getElementById('assignment-unit');
  const load = document.getElementById('assignment-load');
  const refresh = document.getElementById('assignment-refresh');
  const status = document.getElementById('assignment-status');
  const warning = document.getElementById('assignment-switch');
  const confirm = document.getElementById('assignment-confirm');
  let pending = null, generation = 0, ownsPause = false;

  function invalidate() { generation++; pending = null; warning.hidden = true; loader.cancel(); }
  function choices() {
    select.replaceChildren();
    for (const entry of loader.units) {
      const option = document.createElement('option');
      option.value = entry.unitId; option.textContent = `${entry.unitId} · ${entry.title}`;
      select.append(option);
    }
    if (loader.units.some(entry => entry.unitId === session.unitId)) select.value = session.unitId;
    select.disabled = load.disabled = !loader.units.length;
  }
  function cleanup() {
    if (!ownsPause) return;
    ownsPause = false;
    invalidate();
    onResume();
  }
  function close() { dialog.close(); cleanup(); }
  async function refreshList() {
    invalidate();
    const token = generation;
    select.disabled = load.disabled = true;
    status.textContent = 'Reading published units…';
    const result = await loader.refresh();
    if (token !== generation || !dialog.open) return;
    choices();
    if (!result.ok) { if (!result.cancelled) status.textContent = result.message; return; }
    status.textContent = loader.units.length ? 'Select a unit. Your current attempt is kept until a replacement loads successfully.'
      : session.mode === 'demo' ? 'No published units. Close to continue Demo Mode.' : 'No published units. Your current assignment and progress are kept.';
  }
  load.addEventListener('click', () => {
    invalidate();
    pending = loader.units.find(entry => entry.unitId === select.value);
    if (!pending) return;
    document.getElementById('assignment-switch-message').textContent = `Start ${pending.unitId}? This replaces question progress only after the unit loads successfully. Your city location is kept.`;
    warning.hidden = false;
    confirm.disabled = false;
    confirm.focus({ preventScroll: true });
  });
  confirm.addEventListener('click', async () => {
    if (!pending || !loader.units.includes(pending)) return;
    const token = generation, entry = pending;
    pending = null;
    confirm.disabled = select.disabled = load.disabled = true;
    status.textContent = `Loading ${entry.unitId}…`;
    const result = await loader.load(entry.unitId);
    if (token !== generation || !dialog.open) return;
    warning.hidden = true;
    choices();
    if (result.ok) close();
    else if (!result.cancelled) { status.textContent = result.message; select.focus({ preventScroll: true }); }
  });
  select.addEventListener('change', () => { invalidate(); status.textContent = 'Select Load Unit to continue.'; });
  refresh.addEventListener('click', refreshList);
  document.getElementById('assignment-close').addEventListener('click', close);
  document.getElementById('assignment-cancel').addEventListener('click', close);
  dialog.addEventListener('close', cleanup);
  dialog.addEventListener('cancel', event => { event.preventDefault(); close(); });
  return Object.freeze({
    open() {
      if (!available() || dialog.open || document.querySelector('dialog[open]')) return;
      onPause(); ownsPause = true;
      dialog.showModal();
      status.focus({ preventScroll: true });
      refreshList();
    }
  });
}
