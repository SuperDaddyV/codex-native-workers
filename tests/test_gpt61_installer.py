"""Exact historical GPT-6 and GPT-6.1 trial migration to Stable."""
import copy
import hashlib
import json
import unittest
from datetime import timedelta
from pathlib import Path

from scripts import install as installer
from src import worker_selector
from test_installer_lifecycle import (
    ROOT, FIXED_TIME, sandbox, call_install, installation_hash, dry_run_install,
)


HISTORICAL_SOURCES = {
    'v4.3.1': '4236500a7c8ee31c93663b0a99d46f9b6b338143',
    'v4.4.0-local.1': '84502cf6706ff529b1e0f7824de633b939653b7d',
}
TRIAL_PAYLOAD_SHA256 = 'e0ff29960a046afe85cfde1a489c2f4b221a2976731500349fbba09820072476'


def historical_install(target, version='v4.3.1'):
    raw_fixture = (ROOT / f'fixtures/installer/{version}-payload.json').read_bytes()
    if version == 'v4.4.0-local.1':
        assert hashlib.sha256(raw_fixture).hexdigest() == TRIAL_PAYLOAD_SHA256
    fixture = json.loads(raw_fixture)
    assert fixture['source_commit'] == HISTORICAL_SOURCES[version]
    assert fixture['version'] == version
    call_install(target, source_commit=fixture['source_commit'])
    manifest_path = target / installer.MANIFEST_RELATIVE
    manifest = json.loads(manifest_path.read_bytes())
    skills = Path(manifest['skills_root'])
    for source, row in fixture['files'].items():
        raw = row['text'].encode('utf-8')
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        if source.startswith('payload/skills/'):
            relative = source.removeprefix('payload/skills/')
            if relative.startswith('sol-luna-status/'):
                raw = installer.render_status_skill(row['text'], target).encode('utf-8')
            elif relative.startswith('sol-luna-delegate/'):
                raw = installer.render_delegate_skill(row['text'], target).encode('utf-8')
            path = skills / relative
            manifest['owned_skill_files'][relative] = hashlib.sha256(raw).hexdigest()
        else:
            relative = source.removeprefix('.codex/') if source.startswith('.codex/') else source.replace('src/', 'sol-luna-v4/', 1)
            path = target / relative
            manifest['owned_files'][relative] = hashlib.sha256(raw).hexdigest()
        path.write_bytes(raw)
    manifest.update(version=version, schema_version=4,
                    model_contract=copy.deepcopy(installer._HISTORICAL_SCHEMA4_CONTRACTS[version]),
                    source_commit=fixture['source_commit'])
    manifest_path.write_text(json.dumps(manifest), 'utf-8')
    state = target / 'sol-luna-v4/state/gpt6-v4'
    state.mkdir(parents=True, exist_ok=True)
    (state / 'worker-profile.json').write_bytes(b'{"historical-state":"preserve"}\n')


def tree_snapshot(target):
    """Observe bytes and timestamps in both roots to detect even no-op writes."""
    roots = (target, target.parent / '.agents' / 'skills')
    return {(index, path.relative_to(root).as_posix()):
            (path.read_bytes(), path.stat().st_mtime_ns)
            for index, root in enumerate(roots)
            for path in root.rglob('*') if path.is_file()}


class Gpt61InstallerTests(unittest.TestCase):
    def test_exact_v431_upgrade_zero_write_repeat_and_exact_rollback(self):
        with sandbox() as directory:
            target = Path(directory) / '.codex'
            historical_install(target)
            before = installation_hash(target)
            before_snapshot = tree_snapshot(target)
            args = dict(project_root=ROOT, generated_at=FIXED_TIME + timedelta(days=1),
                        allow_validation_sandbox=True, source_commit='6' * 40)
            dry = dry_run_install(target, **args)
            self.assertEqual(dry['effective_changes'], 11)
            self.assertEqual(installation_hash(target), before)
            self.assertEqual(tree_snapshot(target), before_snapshot)
            result = call_install(target, source_commit='6' * 40, generated_at=args['generated_at'])
            self.assertEqual(result['status'], 'UPGRADED')
            manifest = json.loads((target / installer.MANIFEST_RELATIVE).read_bytes())
            self.assertEqual(manifest['model_contract'], worker_selector.cache_identity())
            self.assertEqual(manifest['version'], 'v4.4.0')
            self.assertEqual(manifest['model_contract']['models']['sol'], 'gpt-6.1-sol')
            upgraded = installation_hash(target)
            upgraded_snapshot = tree_snapshot(target)
            repeat = call_install(target, source_commit='6' * 40)
            self.assertEqual(repeat['effective_changes'], 0)
            self.assertIsNone(repeat['backup'])
            self.assertEqual(installation_hash(target), upgraded)
            self.assertEqual(tree_snapshot(target), upgraded_snapshot)
            restored = installer.rollback(target, Path(result['backup']), project_root=ROOT,
                                          allow_validation_sandbox=True)
            self.assertEqual(restored['status'], 'ROLLBACK_EXACT_PASS')
            self.assertEqual(installation_hash(target), before)

    def test_exact_trial_upgrade_preservation_zero_write_repeat_and_exact_rollback(self):
        fixture_path = ROOT / 'fixtures/installer/v4.4.0-local.1-payload.json'
        source_before = fixture_path.read_bytes()
        with sandbox() as directory:
            target = Path(directory) / '.codex'
            historical_install(target, 'v4.4.0-local.1')
            manifest_path = target / installer.MANIFEST_RELATIVE
            historical_manifest = json.loads(manifest_path.read_bytes())
            self.assertEqual(historical_manifest['model_contract'], worker_selector.cache_identity())
            self.assertEqual(historical_manifest['source_commit'], HISTORICAL_SOURCES['v4.4.0-local.1'])
            preserved = {
                target / 'sol-luna-v4/state/gpt61sol-v1/worker-profile.json': b'{"trial-state":"preserve"}\n',
                target / 'sol-luna-v4/state/gpt6-v3/worker-last-good.json': b'{"old-state":"preserve"}\n',
                target / 'user-owned.txt': b'Unmanaged home data\n',
                target.parent / '.agents/skills/user-skill/SKILL.md': b'Unmanaged Skill\n',
            }
            for path, raw in preserved.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            # Coordinator settings remain user-owned outside the managed block.
            config_path = target / 'config.toml'
            config_path.write_bytes(b'model = "user-selected-model"\nmodel_reasoning_effort = "high"\n'
                                    + config_path.read_bytes())
            preserved[config_path] = config_path.read_bytes()
            preserved[target / 'AGENTS.md'] = (target / 'AGENTS.md').read_bytes()
            before = installation_hash(target)
            before_snapshot = tree_snapshot(target)
            args = dict(project_root=ROOT, generated_at=FIXED_TIME + timedelta(days=1),
                        allow_validation_sandbox=True, source_commit='6' * 40)
            dry = dry_run_install(target, **args)
            self.assertEqual(dry['status'], 'DRY_RUN_PASS')
            self.assertEqual(dry['created'], [])
            self.assertEqual(dry['removed'], [])
            required = {installer.MANIFEST_RELATIVE.as_posix(),
                        'sol-luna-v4/selector.py', 'sol-luna-v4/worker_selector.py'}
            allowed = required | {f'skills:{name}/SKILL.md' for name in installer.SKILL_FILES}
            self.assertTrue(required <= set(dry['modified']) <= allowed)
            self.assertEqual(dry['effective_changes'], len(dry['modified']))
            self.assertEqual(tree_snapshot(target), before_snapshot)
            result = call_install(target, source_commit='6' * 40, generated_at=args['generated_at'])
            self.assertEqual(result['status'], 'UPGRADED')
            for field in ('created', 'modified', 'removed', 'effective_changes'):
                self.assertEqual(result[field], dry[field])
            manifest = json.loads(manifest_path.read_bytes())
            self.assertEqual(manifest['version'], 'v4.4.0')
            self.assertEqual(manifest['source_commit'], '6' * 40)
            self.assertEqual(manifest['model_contract'], historical_manifest['model_contract'])
            self.assertEqual(manifest['installed_at'], historical_manifest['installed_at'])
            for path, raw in preserved.items():
                self.assertEqual(path.read_bytes(), raw)
            upgraded = tree_snapshot(target)
            for action in (dry_run_install, call_install):
                repeat = action(target, **(args if action is dry_run_install else {'source_commit': '6' * 40}))
                self.assertEqual(repeat['status'], 'IDEMPOTENT_PASS')
                self.assertEqual(repeat['effective_changes'], 0)
                self.assertIsNone(repeat['backup'])
                self.assertEqual(tree_snapshot(target), upgraded)
            restored = installer.rollback(target, Path(result['backup']), project_root=ROOT,
                                          allow_validation_sandbox=True)
            self.assertEqual(restored['status'], 'ROLLBACK_EXACT_PASS')
            self.assertEqual(installation_hash(target), before)
            self.assertEqual(json.loads(manifest_path.read_bytes()), historical_manifest)
        self.assertEqual(fixture_path.read_bytes(), source_before)

    def test_old_version_new_contract_and_unknown_version_are_zero_write_rejections(self):
        for alteration in ('new-contract', 'old-model-tamper', 'unknown-version', 'future-version',
                           'trial-version-old-contract', 'stable-version-old-contract'):
            with self.subTest(alteration=alteration), sandbox() as directory:
                target = Path(directory) / '.codex'
                historical_install(target)
                path = target / installer.MANIFEST_RELATIVE
                manifest = json.loads(path.read_bytes())
                if alteration == 'new-contract':
                    manifest['model_contract'] = worker_selector.cache_identity()
                elif alteration == 'old-model-tamper':
                    manifest['model_contract']['models']['sol'] = 'gpt-5.6-sol'
                elif alteration == 'unknown-version':
                    manifest['version'] = 'v4.3.2'
                elif alteration == 'trial-version-old-contract':
                    manifest['version'] = 'v4.4.0-local.1'
                elif alteration == 'stable-version-old-contract':
                    manifest['version'] = 'v4.4.0'
                else:
                    manifest['version'] = 'v5.0.0'
                path.write_text(json.dumps(manifest), 'utf-8')
                before = installation_hash(target)
                for action in (call_install, dry_run_install):
                    with self.assertRaises(installer.InstallerError) as raised:
                        action(target, **({'allow_validation_sandbox': True} if action is dry_run_install else {}))
                    self.assertEqual(raised.exception.reason_code, 'MANIFEST_INVALID')
                    self.assertEqual(installation_hash(target), before)

    def test_tampered_new_stable_contract_is_a_zero_write_rejection(self):
        with sandbox() as directory:
            target = Path(directory) / '.codex'
            call_install(target)
            path = target / installer.MANIFEST_RELATIVE
            manifest = json.loads(path.read_bytes())
            manifest['model_contract']['models']['sol'] = 'gpt-6-sol'
            path.write_text(json.dumps(manifest), 'utf-8')
            before = installation_hash(target)
            with self.assertRaises(installer.InstallerError):
                call_install(target)
            self.assertEqual(installation_hash(target), before)

    def test_wrong_trial_contract_inventory_or_hash_rejects_before_writes(self):
        alterations = ('old-sol', 'old-luna', 'efforts', 'axis', 'policy', 'extra-contract',
                       'unknown-trial-version', 'missing-file', 'extra-skill', 'file-tamper')
        for alteration in alterations:
            with self.subTest(alteration=alteration), sandbox() as directory:
                target = Path(directory) / '.codex'
                historical_install(target, 'v4.4.0-local.1')
                path = target / installer.MANIFEST_RELATIVE
                manifest = json.loads(path.read_bytes())
                contract = manifest['model_contract']
                if alteration == 'old-sol':
                    contract['models']['sol'] = 'gpt-6-sol'
                elif alteration == 'old-luna':
                    contract['models']['luna'] = 'gpt-5.6-luna'
                elif alteration == 'efforts':
                    contract['efforts'].append('ultra')
                elif alteration == 'axis':
                    contract['sol_axes']['backend'] = ['overallRankings', 'score']
                elif alteration == 'policy':
                    contract['policy_version'] = 3
                elif alteration == 'extra-contract':
                    contract['unexpected'] = True
                elif alteration == 'unknown-trial-version':
                    manifest['version'] = 'v4.4.0-local.2'
                elif alteration == 'missing-file':
                    del manifest['owned_files']['agents/sol-high.toml']
                elif alteration == 'extra-skill':
                    manifest['owned_skill_files']['user-skill/SKILL.md'] = '0' * 64
                else:
                    (target / 'sol-luna-v4/selector.py').write_bytes(b'# tampered\n')
                path.write_text(json.dumps(manifest), 'utf-8')
                before = tree_snapshot(target)
                reason = 'OWNERSHIP_CONFLICT' if alteration == 'file-tamper' else 'MANIFEST_INVALID'
                for action in (call_install, dry_run_install):
                    with self.assertRaises(installer.InstallerError) as raised:
                        action(target, **({'allow_validation_sandbox': True} if action is dry_run_install else {}))
                    self.assertEqual(raised.exception.reason_code, reason)
                    self.assertEqual(tree_snapshot(target), before)

    def test_historical_schema4_version_mapping_is_exact(self):
        expected_versions = {'v4.3.0', 'v4.3.1', 'v4.4.0-local.1'}
        self.assertEqual(set(installer._HISTORICAL_SCHEMA4_CONTRACTS), expected_versions)
        for version in ('v4.3.0', 'v4.3.1'):
            self.assertTrue(installer._schema4_contract_matches(
                {'version': version, 'model_contract': installer._GPT6_STABLE_CONTRACT}))
            self.assertFalse(installer._schema4_contract_matches(
                {'version': version, 'model_contract': worker_selector.cache_identity()}))


if __name__ == '__main__':
    unittest.main()
