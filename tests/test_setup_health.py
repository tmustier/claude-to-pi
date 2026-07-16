import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


RUNNER = Path(__file__).resolve().parents[1] / "scripts" / "setup-health"


class SetupHealthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.agent = self.root / "agent"
        self.agent.mkdir()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def executable(self, name: str, body: str) -> Path:
        target = self.bin / name
        target.write_text(f"#!/bin/sh\n{body}\n")
        target.chmod(0o755)
        return target

    def manifest(self, checks: list[dict]) -> Path:
        target = self.root / "health.json"
        target.write_text(json.dumps({"version": 1, "name": "fixture", "checks": checks}))
        return target

    def run_health(self, manifest: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ | {
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "PI_CODING_AGENT_DIR": str(self.agent),
        }
        return subprocess.run(
            [str(RUNNER), "--manifest", str(manifest), *args],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def test_command_version_run_and_live_skip(self) -> None:
        self.executable("healthy", "echo healthy")
        self.executable("versioned", "echo v2.4.1")
        manifest = self.manifest(
            [
                {"id": "command", "type": "command", "command": "healthy"},
                {"id": "version", "type": "version", "command": ["versioned"], "minimum": "2.4.0"},
                {"id": "run", "type": "run", "command": ["healthy"], "expectStdout": "healthy"},
                {"id": "live", "type": "run", "command": ["missing"], "live": True},
            ]
        )
        completed = self.run_health(manifest, "--json")
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["counts"], {"pass": 3, "warn": 0, "fail": 0, "skip": 1})

    def test_failure_does_not_expose_command_output(self) -> None:
        self.executable("leaky", "echo VERY_PRIVATE_VALUE >&2; exit 7")
        manifest = self.manifest(
            [{"id": "live", "label": "Live probe", "type": "run", "command": ["leaky"], "live": True}]
        )
        completed = self.run_health(manifest, "--live")
        self.assertEqual(completed.returncode, 1)
        self.assertIn("exited with status 7", completed.stdout)
        self.assertNotIn("VERY_PRIVATE_VALUE", completed.stdout + completed.stderr)

    def test_package_sources_are_read_from_string_and_object_entries(self) -> None:
        settings = self.agent / "settings.json"
        settings.write_text(json.dumps({"packages": ["npm:one", {"source": "git:two@feature/test"}, "npm:web"]}))
        manifest = self.manifest(
            [
                {
                    "id": "packages",
                    "type": "packages",
                    "settings": "{agent_dir}/settings.json",
                    "expectedSources": ["npm:one", "git:two"],
                    "expectedAnyOf": [["npm:web", "git:web"]],
                }
            ]
        )
        completed = self.run_health(manifest, "--json")
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["counts"]["pass"], 1)

    def test_json_models_alternative_paths_and_freshness(self) -> None:
        settings = self.agent / "settings.json"
        settings.write_text(
            json.dumps(
                {
                    "models": ["openai-codex/gpt-5.6-sol:medium", "anthropic/claude-opus-4-8:xhigh"],
                    "policy": {"threshold": 200000},
                }
            )
        )
        marker = self.root / "fresh"
        marker.write_text("ok")
        manifest = self.manifest(
            [
                {"id": "file", "type": "file", "paths": [str(self.root / "missing"), str(marker)]},
                {"id": "age", "type": "file_age", "path": str(marker), "maximumDays": 1},
                {"id": "same", "type": "same_file", "expected": str(marker), "actual": str(marker)},
                {
                    "id": "json",
                    "type": "json_values",
                    "path": str(settings),
                    "expected": {"policy.threshold": 200000},
                },
                {
                    "id": "models",
                    "type": "models",
                    "path": str(settings),
                    "expected": ["openai-codex/gpt-5.6-sol", "anthropic/claude-opus-4-8"],
                },
            ]
        )
        completed = self.run_health(manifest, "--json")
        self.assertEqual(completed.returncode, 0, completed.stdout)
        self.assertEqual(json.loads(completed.stdout)["counts"]["pass"], 5)

    def test_allow_missing_does_not_hide_a_broken_root_symlink(self) -> None:
        root = self.root / "root-link"
        root.symlink_to(self.root / "missing")
        manifest = self.manifest(
            [{"id": "root", "type": "broken_symlinks", "path": str(root), "allowMissing": True}]
        )
        completed = self.run_health(manifest)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("broken root symlink", completed.stdout)

    def test_broken_symlink_is_a_failure(self) -> None:
        links = self.root / "links"
        links.mkdir()
        (links / "broken").symlink_to(self.root / "missing")
        manifest = self.manifest(
            [{"id": "links", "type": "broken_symlinks", "path": str(links)}]
        )
        completed = self.run_health(manifest)
        self.assertEqual(completed.returncode, 1)
        self.assertIn("broken symlink", completed.stdout)


if __name__ == "__main__":
    unittest.main()
