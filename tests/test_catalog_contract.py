import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'plugins/agent-roles/scripts/validate_catalog.py'
spec = importlib.util.spec_from_file_location('catalog', SCRIPT)
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)


class CatalogContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid = catalog.load_yaml(ROOT / 'plugins/agent-roles/roles/catalog.yml')

    def test_builtin(self):
        self.assertEqual(catalog.validate(self.valid), self.valid)

    def test_invalid_fields_are_exit_two_without_traceback(self):
        cases = [
            (['metadata', 'name'], ''), (['metadata', 'version'], -1),
            (['spec', 'artifactTypes'], [{}]), (['spec', 'artifactTypes'], ['a', 'a']),
            (['spec', 'roles', 0, 'version'], True), (['spec', 'roles', 0, 'mission'], None),
            (['spec', 'roles', 0, 'produces'], []), (['spec', 'roles', 0, 'authority'], ['unknown']),
            (['spec', 'roles', 0, 'receives'], [{}]), (['spec', 'roles', 0, 'responsibilities'], [None]),
            (['spec', 'relations', 0, 'from'], {}), (['spec', 'relations', 0, 'permits'], ['research']),
            (['spec', 'relations', 0, 'sends'], ['review_report']),
            (['spec', 'exchange'], 'invalid'), (['spec', 'exchange', 'maxRounds'], False),
            (['spec', 'exchange', 'unresolved'], 'ignore'), (['spec', 'exchange', 'duplicates', 'report'], 'replace'),
            (['spec', 'isolation'], None), (['spec', 'isolation', 'workerCannotReviewOwnArtifact'], False),
        ]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'catalog.json'
            for keys, value in cases:
                with self.subTest(keys=keys, value=value):
                    document = copy.deepcopy(self.valid)
                    target = document
                    for key in keys[:-1]:
                        target = target[key]
                    target[keys[-1]] = value
                    path.write_text(json.dumps(document))
                    result = subprocess.run(['python3', str(SCRIPT), str(path)], text=True, capture_output=True)
                    self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                    self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
