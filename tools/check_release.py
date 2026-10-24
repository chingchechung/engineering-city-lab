"""Read-only CI checks for source syntax, schemas and static release inputs."""
import argparse
import ast
import json
from pathlib import Path
import subprocess

if __package__:
    from .package_release import ROOT, release_files
else:
    from package_release import ROOT, release_files


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--syntax', action='store_true')
    args = parser.parse_args()
    if args.syntax:
        counts = {'JavaScript': 0, 'Python': 0}
        for directory in ('js', 'tools', 'tests'):
            for path in sorted((ROOT / directory).rglob('*')):
                if path.suffix in ('.js', '.mjs', '.cjs'):
                    subprocess.run(['node', '--check', str(path)], check=True)
                    counts['JavaScript'] += 1
                elif path.suffix == '.py':
                    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
                    counts['Python'] += 1
        print(f'Syntax valid: {counts}')
    else:
        from jsonschema import Draft202012Validator
        for path in sorted((ROOT / 'schemas').glob('*.schema.json')):
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding='utf-8')))
        files = release_files()
        manifest = json.loads((ROOT / 'assignments/manifest.json').read_text(encoding='utf-8'))
        schema = json.loads((ROOT / 'schemas/manifest-v1.schema.json').read_text(encoding='utf-8'))
        Draft202012Validator(schema).validate(manifest)
        print(f'Valid schemas, empty public manifest and {len(files)} static release files')


if __name__ == '__main__':
    main()
