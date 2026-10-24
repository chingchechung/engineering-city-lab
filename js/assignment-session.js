import { DEMO_QUESTIONS, createDemoSession } from './education-session.js';
import { validateUnit, normalizeUnit, acceptsAnswer, validateOrThrow } from './assignment-contract.js';

function freeze(value) {
  if (value && typeof value === 'object') { Object.values(value).forEach(freeze); Object.freeze(value); }
  return value;
}

export function createAssignmentSession() {
  const demo = createDemoSession();
  let unit = null, passed = new Set();
  return Object.freeze({
    get mode() { return unit ? 'assignment' : 'demo'; },
    get unit() { return unit; },
    get unitId() { return unit?.unitId ?? null; },
    get questions() { return unit?.questions ?? DEMO_QUESTIONS; },
    get total() { return unit?.questions.length ?? DEMO_QUESTIONS.length; },
    get count() { return unit ? passed.size : demo.count; },
    get complete() { return unit ? passed.size === unit.questions.length : demo.complete; },
    question(id) { return (unit?.questions ?? DEMO_QUESTIONS).find(question => question.id === id) ?? null; },
    hasPassed(id) { return unit ? passed.has(id) : demo.hasPassed(id); },
    answer(id, selected) {
      if (!unit) return demo.answer(id, selected);
      const question = unit.questions.find(question => question.id === id);
      const correct = acceptsAnswer(question, selected);
      if (correct) passed.add(id);
      return correct;
    },
    activate(data, filename) {
      validateOrThrow(validateUnit(data, filename), filename ?? 'Assignment');
      const next = freeze(normalizeUnit(data));
      unit = next;
      passed = new Set(); // Only a deliberately confirmed, valid replacement starts a new attempt.
    }
  });
}
