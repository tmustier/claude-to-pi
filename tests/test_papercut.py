from __future__ import annotations

import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "papercut"
HEADER = "# Papercuts\n\nAppend-only test file.\n"


class PapercutCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(prefix="papercut-tests-")
        self.root = Path(self.tempdir.name)
        self.agent_dir = self.root / "pi-agent"
        self.outside = self.root / "outside"
        self.outside.mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def run_cli(
        self,
        *args: str,
        cwd: Path | None = None,
        check: bool = True,
        extra_env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PI_CODING_AGENT_DIR"] = str(self.agent_dir)
        env["HOME"] = str(self.root / "home")
        if extra_env:
            env.update(extra_env)
        result = subprocess.run(
            [str(SCRIPT), *args],
            cwd=str(cwd or self.outside),
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if check and result.returncode != 0:
            self.fail(f"command failed ({result.returncode}): {result.stderr}\n{result.stdout}")
        return result

    def make_repo(self, name: str = "repo") -> Path:
        repo = self.root / name
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True, timeout=10)
        return repo

    def test_global_fallback_records_timestamp_model_and_context(self) -> None:
        result = self.run_cli(
            "--model",
            "test/provider-model",
            "--context",
            "test:global-flow",
            "--",
            "The resolver used the global default outside Git. The entry retained useful metadata.",
        )

        target = self.agent_dir / "PAPERCUTS.md"
        self.assertIn("Recorded papercut", result.stdout)
        self.assertTrue(target.exists())
        content = target.read_text()
        self.assertRegex(content, r"## \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}")
        self.assertIn("- Model: `test/provider-model`", content)
        self.assertIn("- Context: `test:global-flow`", content)
        self.assertIn("The resolver used the global default outside Git.", content)
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)

    def test_explicit_local_creates_at_git_root(self) -> None:
        repo = self.make_repo()
        nested = repo / "one" / "two"
        nested.mkdir(parents=True)

        self.run_cli(
            "--local",
            "--model",
            "test/model",
            "--",
            "Explicit local capture created one file at the repository root.",
            cwd=nested,
        )

        target = repo / "PAPERCUTS.md"
        self.assertTrue(target.exists())
        self.assertIn("repo:repo/one/two", target.read_text())
        self.assertFalse((self.agent_dir / "PAPERCUTS.md").exists())
        self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o644)

    def test_nearest_local_file_overrides_ancestor_and_global(self) -> None:
        repo = self.make_repo()
        root_file = repo / "PAPERCUTS.md"
        root_file.write_text(HEADER + "root marker\n")
        area = repo / "area"
        area.mkdir()
        nearest = area / "PAPERCUTS.md"
        nearest.write_text(HEADER + "nearest marker\n")
        deep = area / "feature" / "src"
        deep.mkdir(parents=True)
        self.agent_dir.mkdir()
        global_file = self.agent_dir / "PAPERCUTS.md"
        global_file.write_text(HEADER + "global marker\n")

        root_before = root_file.read_bytes()
        global_before = global_file.read_bytes()
        self.run_cli(
            "--model",
            "test/model",
            "--",
            "Automatic resolution selected the closest repository-local override.",
            cwd=deep,
        )

        self.assertIn("Automatic resolution selected", nearest.read_text())
        self.assertEqual(root_file.read_bytes(), root_before)
        self.assertEqual(global_file.read_bytes(), global_before)

        resolved = self.run_cli("resolve", "--cwd", str(deep), "--json")
        payload = json.loads(resolved.stdout)
        self.assertEqual(Path(payload["target"]).resolve(), nearest.resolve())
        self.assertEqual(payload["reason"], "nearest-local-override")

    def test_repo_without_local_file_falls_back_to_global(self) -> None:
        repo = self.make_repo()
        self.run_cli(
            "--model",
            "test/model",
            "--",
            "A repository without an opt-in file retained the global default.",
            cwd=repo,
        )
        self.assertTrue((self.agent_dir / "PAPERCUTS.md").exists())
        self.assertFalse((repo / "PAPERCUTS.md").exists())

    def test_review_all_combines_global_and_effective_local(self) -> None:
        repo = self.make_repo()
        self.run_cli(
            "--global",
            "--model",
            "global/model",
            "--context",
            "global:test",
            "--",
            "Global review evidence remained available.",
            cwd=repo,
        )
        self.run_cli(
            "--local",
            "--model",
            "local/model",
            "--context",
            "repo:test",
            "--",
            "Local review evidence overrode automatic append resolution.",
            cwd=repo,
        )

        result = self.run_cli("review", "--all", "--limit", "10", cwd=repo)
        self.assertIn("Explicit one-off review bundle", result.stdout)
        self.assertIn("Global review evidence", result.stdout)
        self.assertIn("Local review evidence", result.stdout)
        self.assertIn("Matched: 2; showing newest: 2", result.stdout)

        json_result = self.run_cli("review", "--all", "--json", cwd=repo)
        payload = json.loads(json_result.stdout)
        self.assertEqual(payload["matched"], 2)
        self.assertEqual({entry["scope"] for entry in payload["entries"]}, {"global", "local"})

    def test_secret_like_input_is_rejected_without_creating_file(self) -> None:
        result = self.run_cli(
            "--model",
            "test/model",
            "--",
            "The failing credential was sk-proj-abcdefghijklmnop1234567890.",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("possible OpenAI or Anthropic API key detected", result.stderr)
        self.assertNotIn("sk-proj-", result.stderr)
        self.assertFalse((self.agent_dir / "PAPERCUTS.md").exists())

    def test_more_than_two_sentences_is_rejected(self) -> None:
        result = self.run_cli(
            "--model",
            "test/model",
            "--",
            "The first step was slow. The retry was unclear. The final output hid the cause.",
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("one or two sentences", result.stderr)
        self.assertFalse((self.agent_dir / "PAPERCUTS.md").exists())

    def test_dry_run_resolves_without_writing(self) -> None:
        repo = self.make_repo()
        result = self.run_cli(
            "--dry-run",
            "--model",
            "test/model",
            "--",
            "Dry-run resolution did not mutate either target.",
            cwd=repo,
        )
        self.assertIn("Would record papercut", result.stdout)
        self.assertFalse((self.agent_dir / "PAPERCUTS.md").exists())
        self.assertFalse((repo / "PAPERCUTS.md").exists())

    def test_review_redacts_sensitive_preexisting_structured_entry(self) -> None:
        self.agent_dir.mkdir()
        target = self.agent_dir / "PAPERCUTS.md"
        dummy_token = "sk-proj-abcdefghijklmnop1234567890"
        target.write_text(
            "# Papercuts\n\n"
            "## 2026-07-10T09:00:00+01:00\n"
            "- Model: `test/model`\n"
            "- Context: `test:manual-fixture`\n"
            f"- Friction: A manually inserted fixture contained {dummy_token}.\n"
        )

        result = self.run_cli("review", "--global")
        self.assertIn("[redacted: possible sensitive data in stored entry]", result.stdout)
        self.assertNotIn(dummy_token, result.stdout)

    def test_symlink_target_is_refused_without_touching_destination(self) -> None:
        repo = self.make_repo()
        destination = self.root / "must-not-change.md"
        destination.write_text("sentinel\n")
        (repo / "PAPERCUTS.md").symlink_to(destination)

        result = self.run_cli(
            "--model",
            "test/model",
            "--",
            "A symlink should never redirect this append.",
            cwd=repo,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing symlink target", result.stderr)
        self.assertEqual(destination.read_text(), "sentinel\n")

    def test_concurrent_appends_remain_complete(self) -> None:
        env = os.environ.copy()
        env["PI_CODING_AGENT_DIR"] = str(self.agent_dir)
        env["HOME"] = str(self.root / "home")
        processes: list[subprocess.Popen[str]] = []
        for number in range(12):
            processes.append(
                subprocess.Popen(
                    [
                        str(SCRIPT),
                        "--global",
                        "--model",
                        "concurrency/model",
                        "--context",
                        "test:concurrency",
                        "--",
                        f"Concurrent append number {number} stayed intact.",
                    ],
                    cwd=str(self.outside),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
            )

        for process in processes:
            stdout, stderr = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, f"{stdout}\n{stderr}")

        content = (self.agent_dir / "PAPERCUTS.md").read_text()
        self.assertEqual(content.count("## "), 12)
        for number in range(12):
            self.assertEqual(content.count(f"Concurrent append number {number} stayed intact."), 1)


if __name__ == "__main__":
    unittest.main()
