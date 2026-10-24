"""Adapted reference validation tests; synthetic data only, no teacher GUI or maze."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import unittest

from tests.contract_cases import contract_cases
from tests.contract_cases_v2 import answer_cases
from tools.assignment_data import (UNIT_SCHEMA, UNIT_SCHEMA_V2, SCHEMA_DIR,
    validate_unit, validate_manifest, normalize_unit, normalize_manifest, accepts_answer)
from tools.validate_assignments import validate_path

ROOT = Path(__file__).resolve().parents[1]


def errors(case):
    return validate_unit(case['data'], case['filename']) if case['kind'] == 'unit' else validate_manifest(case['data'])


def normalized(case):
    return normalize_unit(case['data']) if case['kind'] == 'unit' else normalize_manifest(case['data'])


class AssignmentContractTests(unittest.TestCase):
    def test_reference_acceptance_and_no_input_mutation(self):
        for case in contract_cases():
            with self.subTest(case=case['name']):
                before = deepcopy(case['data'])
                self.assertEqual(not errors(case), case['valid'])
                normalized(case)
                self.assertEqual(before, case['data'])

    def test_native_javascript_adapter_has_exact_python_errors_normalization_and_url_patterns(self):
        cases, answers = contract_cases(), answer_cases()
        process = subprocess.run(['node', str(ROOT/'tests/assignment_parity.mjs')],
            cwd=ROOT, input=json.dumps({'cases': cases, 'answers': answers}, ensure_ascii=False),
            text=True, capture_output=True, check=True)
        output = json.loads(process.stdout)
        self.assertEqual(output['rules'], {key: UNIT_SCHEMA['$defs'][key]['pattern'] for key in ('youtubeUrl','googleFormUrl')})
        for case, result in zip(cases, output['results'], strict=True):
            with self.subTest(case=case['name']):
                self.assertEqual(result['errors'], [issue.as_dict() for issue in errors(case)])
                self.assertEqual(result['normalized'], normalized(case))
        self.assertEqual(output['answers'], [case['expected'] for case in answers])
        print(f'Parity: {len(cases)} validation cases and {len(answers)} answer selections')

    def test_python_single_choice_membership(self):
        for case in answer_cases():
            with self.subTest(case=case):
                self.assertEqual(accepts_answer(case['question'], case['selected']), case['expected'])

    def test_json_schemas_agree_with_complete_reference_corpus(self):
        from jsonschema import Draft202012Validator
        schemas = {'unit': UNIT_SCHEMA, 'unit_v2': UNIT_SCHEMA_V2,
            'manifest': json.loads((SCHEMA_DIR/'manifest-v1.schema.json').read_text())}
        validators = {}
        for kind, schema in schemas.items():
            Draft202012Validator.check_schema(schema)
            validators[kind] = Draft202012Validator(schema)
        for case in contract_cases():
            with self.subTest(case=case['name']):
                data = normalized(case)
                kind = 'unit_v2' if case['kind'] == 'unit' and isinstance(data,dict) and data.get('schemaVersion') == 2 else case['kind']
                expected = case['valid']
                runtime_errors = errors(case)
                if case['kind'] == 'unit' and runtime_errors and all(issue.code == 'filename' for issue in runtime_errors):
                    expected = True  # Filename context lives outside JSON Schema.
                self.assertEqual(not list(validators[kind].iter_errors(data)), expected)

    def test_read_only_cli_empty_public_manifest_and_both_fixture_versions(self):
        for path in [ROOT/'assignments/manifest.json', ROOT/'tests/fixtures/manifest.json', ROOT/'tests/fixtures/v2/manifest.json']:
            self.assertEqual(validate_path(path), [])


if __name__ == '__main__':
    unittest.main()
