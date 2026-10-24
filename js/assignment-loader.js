import { validateManifest, normalizeManifest, validateUnit, normalizeUnit, validateOrThrow } from './assignment-contract.js';

// Adapted from the reference student loader: no maze DOM, resets or progress storage.
export function createAssignmentLoader({ fetch: fetchData = globalThis.fetch,
  baseURL = new URL('../assignments/', import.meta.url), onReady } = {}) {
  let units = Object.freeze([]), generation = 0, controller = null;
  function cancel() { generation++; controller?.abort(); controller = null; }
  function begin() { cancel(); controller = new AbortController(); return { token: generation, signal: controller.signal }; }
  const current = request => request.token === generation && !request.signal.aborted;
  const cancelled = () => ({ ok: false, cancelled: true });
  const failure = error => ({ ok: false, cancelled: false, message: error.message, issues: error.issues ?? [] });

  async function read(file, signal) {
    let response;
    try {
      response = await fetchData(new URL(file, baseURL), { cache: 'no-store', signal, redirect: 'error' });
    } catch (error) {
      if (error.name === 'AbortError') throw error;
      throw new Error(`Unable to read ${file}. Check your connection and retry.`);
    }
    if (!response.ok) throw new Error(`${file} could not be loaded (HTTP ${response.status}).`);
    try { return await response.json(); }
    catch (error) {
      if (error.name === 'AbortError') throw error;
      throw new Error(`${file} is not valid JSON.`);
    }
  }

  return Object.freeze({
    get units() { return units; },
    cancel,
    async refresh() {
      const request = begin();
      units = Object.freeze([]); // A failed refresh must not authorize requests using an obsolete list.
      try {
        const data = await read('manifest.json', request.signal);
        if (!current(request)) return cancelled();
        validateOrThrow(validateManifest(data), 'manifest.json');
        units = Object.freeze(normalizeManifest(data).units.map(Object.freeze));
        return { ok: true, units };
      } catch (error) { return current(request) ? failure(error) : cancelled(); }
    },
    async load(unitId) {
      const request = begin();
      const entry = units.find(unit => unit.unitId === unitId);
      if (!entry) return failure(new Error('Select a unit from the current published list.'));
      try {
        const data = await read(entry.file, request.signal);
        if (!current(request)) return cancelled();
        validateOrThrow(validateUnit(data, entry.file), entry.file);
        const unit = normalizeUnit(data);
        // Synchronous commit after the last generation check; never reset the previous attempt first.
        onReady?.(unit, entry.file);
        return { ok: true, unit };
      } catch (error) { return current(request) ? failure(error) : cancelled(); }
    }
  });
}
