"""Exact historical GPT-6 payload migration, prevalidation and rollback."""
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


def historical_install(target):
    fixture = json.loads((ROOT / 'fixtures/installer/v4.3.1-payload.json').read_bytes())
    assert fixture['source_commit'] == '4236500a7c8ee31c93663b0a99d46f9b6b338143'
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
    manifest.update(version='v4.3.1', schema_version=4,
                    model_contract=copy.deepcopy(installer._GPT6_STABLE_CONTRACT),
                    source_commit=fixture['source_commit'])
    manifest_path.write_text(json.dumps(manifest), 'utf-8')
    state = target / 'sol-luna-v4/state/gpt6-v4'
    state.mkdir(parents=True, exist_ok=True)
    (state / 'worker-profile.json').write_bytes(b'{"historical-state":"preserve"}\n')


class Gpt61InstallerTests(unittest.TestCase):
    def test_exact_v431_upgrade_zero_write_repeat_and_exact_rollback(self):
        with sandbox() as directory:
            target = Path(directory) / '.codex'
            historical_install(target)
            before = installation_hash(target)
            args = dict(project_root=ROOT, generated_at=FIXED_TIME + timedelta(days=1),
                        allow_validation_sandbox=True, source_commit='6' * 40)
            dry = dry_run_install(target, **args)
            self.assertEqual(dry['effective_changes'], 11)
            self.assertEqual(installation_hash(target), before)
            result = call_install(target, source_commit='6' * 40, generated_at=args['generated_at'])
            self.assertEqual(result['status'], 'UPGRADED')
            manifest = json.loads((target / installer.MANIFEST_RELATIVE).read_bytes())
            self.assertEqual(manifest['model_contract'], worker_selector.cache_identity())
            self.assertEqual(manifest['model_contract']['models']['sol'], 'gpt-6.1-sol')
            upgraded = installation_hash(target)
            repeat = call_install(target, source_commit='6' * 40)
            self.assertEqual(repeat['effective_changes'], 0)
            self.assertIsNone(repeat['backup'])
            self.assertEqual(installation_hash(target), upgraded)
            restored = installer.rollback(target, Path(result['backup']), project_root=ROOT,
                                          allow_validation_sandbox=True)
            self.assertEqual(restored['status'], 'ROLLBACK_EXACT_PASS')
            self.assertEqual(installation_hash(target), before)

    def test_old_version_new_contract_and_unknown_version_are_zero_write_rejections(self):
        for alteration in ('new-contract', 'old-model-tamper', 'unknown-version', 'future-version'):
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
                else:
                    manifest['version'] = 'v5.0.0'
                path.write_text(json.dumps(manifest), 'utf-8')
                before = installation_hash(target)
                for action in (call_install, dry_run_install):
                    with self.assertRaises(installer.InstallerError) as raised:
                        action(target, **({'allow_validation_sandbox': True} if action is dry_run_install else {}))
                    self.assertEqual(raised.exception.reason_code, 'MANIFEST_INVALID')
                    self.assertEqual(installation_hash(target), before)

    def test_tampered_new_trial_contract_is_a_zero_write_rejection(self):
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


if __name__ == '__main__':
    unittest.main()
