"""Stable GPT-6.1 identity and old-cache rejection; synthetic evidence only."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import selector, worker_selector
from publication_fixtures import publication_bundle
from test_reference_runtime import NOW


ROOT = Path(__file__).resolve().parents[1]


def old_publication():
    api = json.loads((ROOT / 'fixtures/modeldial-gpt6/api-complete-v1.1.json').read_bytes())
    for group in ('rankings', 'overallRankings'):
        for row in api[group]:
            row['provider'], row['route'] = selector.BENCHMARK_PAIRS[1]
    return publication_bundle(api)


class Gpt61MigrationTests(unittest.TestCase):
    def test_exact_stable_contract_and_unchanged_luna(self):
        self.assertEqual(worker_selector.VERSION, 'v4.4.0')
        self.assertEqual(selector.USER_AGENT, 'codex-native-workers/4.4.0')
        self.assertEqual(worker_selector.SOL_MODEL, 'gpt-6.1-sol')
        self.assertEqual(worker_selector.LUNA_MODEL, 'gpt-6-luna')
        self.assertEqual(worker_selector.CACHE_NAMESPACE, 'gpt61sol-v1')
        self.assertEqual(worker_selector.EFFORTS, ('low', 'medium', 'high', 'xhigh', 'max'))

    def test_old_publication_cannot_supply_new_sol_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            profile = selector.ensure_worker_profile(old_publication(), state_dir=directory, now=NOW)
            self.assertEqual(profile['routing']['luna']['mode'], 'live')
            for route in profile['routing']['sol']['views'].values():
                self.assertEqual(route['mode'], 'basic')
                self.assertEqual(route['model'], 'gpt-6.1-sol')
                self.assertEqual(route['evidence_scope'], 'no_benchmark')
                self.assertNotIn('selected_role', route)
                self.assertNotIn('selected_effort', route)

    def test_old_namespace_and_relocated_old_cache_are_rejected_and_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(worker_selector, 'SOL_MODEL', 'gpt-6-sol'), \
                 patch.object(worker_selector, 'MODEL_BY_FAMILY', {'sol': 'gpt-6-sol', 'luna': 'gpt-6-luna'}), \
                 patch.object(selector, 'REFERENCE_MODEL', 'gpt-6-sol'), \
                 patch.object(selector, 'CACHE_NAMESPACE', 'gpt6-v4'):
                old = selector.ensure_worker_profile(old_publication(), state_dir=root, now=NOW)
            self.assertEqual(old['routing']['sol']['views']['backend']['mode'], 'live')
            old_root = root / 'gpt6-v4'
            before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns)
                      for p in old_root.iterdir() if p.is_file()}
            new_root = root / selector.CACHE_NAMESPACE
            new_root.mkdir()
            for name in ('worker-profile.json', 'worker-last-good.json'):
                (new_root / name).write_bytes((old_root / name).read_bytes())
            profile = selector.ensure_worker_profile({}, state_dir=root, now=NOW)
            for route in profile['routing']['sol']['views'].values():
                self.assertEqual(route['mode'], 'basic')
                self.assertEqual(route['model'], 'gpt-6.1-sol')
                self.assertNotIn('selected_effort', route)
            self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns)
                                     for p in old_root.iterdir() if p.is_file()})

    def test_new_reference_score_binding_stays_strict(self):
        valid = publication_bundle()
        for axis in ('frontend', 'knowledge', 'overall'):
            data = copy.deepcopy(valid)
            archive = data['benchmark_snapshots'][axis]
            rows = archive['entries'] if axis == 'overall' else next(iter(archive['axes'].values()))['entries']
            row = next(item for item in rows if item['model_id'] == 'gpt-6.1-sol')
            row['model_id'] = 'gpt-6-sol'
            with self.subTest(axis=axis), tempfile.TemporaryDirectory() as directory:
                profile = selector.ensure_worker_profile(data, state_dir=directory, now=NOW)
                view = {'knowledge': 'reasoning', 'overall': 'general'}.get(axis, axis)
                self.assertEqual(profile['routing']['sol']['views'][view]['mode'], 'basic')


if __name__ == '__main__':
    unittest.main()
