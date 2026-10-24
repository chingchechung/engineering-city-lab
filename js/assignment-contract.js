// Native-module bridge for the unchanged reference UMD files. Evaluation order matters.
import './assignment-rules.js';
import * as legacy from './assignment-validator.js';

const validator = legacy.default ?? globalThis.AssignmentValidator;
export const { normalizeUnit, normalizeManifest, validateUnit, validateUnitV1,
  validateUnitV2, validateManifest, acceptsAnswer } = validator;

export function validateOrThrow(issues, file) {
  if (!issues.length) return;
  const error = new Error(`${file} failed validation: ` + issues.slice(0, 3)
    .map(issue => `${issue.path}: ${issue.message}`).join('; '));
  error.issues = issues; // Retain every original path/code/message, including those beyond the summary.
  throw error;
}
