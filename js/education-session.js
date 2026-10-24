// Synthetic interaction fixtures, not course assignments or a v1/v2 JSON loader.
export const DEMO_QUESTIONS = Object.freeze([
  { id: 'Q01', title: 'Demo colors', prompt: 'Synthetic demo: which option names a color?', options: ['Blue', 'Triangle', 'Monday'], answer: 'A' },
  { id: 'Q02', title: 'Demo shapes', prompt: 'Synthetic demo: which shape has three sides?', options: ['Circle', 'Triangle', 'Square'], answer: 'B' },
  { id: 'Q03', title: 'Demo counting', prompt: 'Synthetic demo: what is one plus one?', options: ['One', 'Three', 'Two'], answer: 'C' },
  { id: 'Q04', title: 'Demo directions', prompt: 'Synthetic demo: which option names a direction?', options: ['North', 'Purple', 'Friday'], answer: 'A' },
  { id: 'Q05', title: 'Demo sequence', prompt: 'Synthetic demo: which letter follows A?', options: ['D', 'B', 'C'], answer: 'B' }
].map(q => Object.freeze({ ...q, options: Object.freeze(q.options) })));

export function createDemoSession() {
  const passed = new Set();
  return Object.freeze({
    get count() { return passed.size; },
    get complete() { return passed.size === DEMO_QUESTIONS.length; },
    hasPassed(id) { return passed.has(id); },
    answer(id, label) {
      const question = DEMO_QUESTIONS.find(q => q.id === id);
      const correct = Boolean(question && typeof label === 'string' && label === question.answer);
      if (correct) passed.add(id);
      return correct;
    }
  });
}
