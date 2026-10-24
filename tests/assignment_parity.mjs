// Native-module adapter is exercised by the shared Python/reference corpus.
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import * as validator from '../js/assignment-contract.js';
const rules = createRequire(import.meta.url)('../js/assignment-rules.js');
const { cases, answers } = JSON.parse(readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify({ rules,
  results: cases.map(item => ({
    errors: item.kind === 'unit' ? validator.validateUnit(item.data, item.filename ?? null) : validator.validateManifest(item.data),
    normalized: item.kind === 'unit' ? validator.normalizeUnit(item.data) : validator.normalizeManifest(item.data)
  })), answers: answers.map(item => validator.acceptsAnswer(item.question, item.selected))
}));
