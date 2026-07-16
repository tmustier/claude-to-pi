# Setup-health manifests

`scripts/setup-health` runs deterministic checks from one or more trusted JSON manifests. It is intended for installation drift, not application correctness.

## Trust boundary

A manifest may execute commands. Only pass manifests from repositories you trust and have reviewed. Commands are arrays passed directly to `subprocess.run`; the runner does not invoke a shell. It captures and suppresses stdout and stderr so auth probes cannot accidentally print tokens or private data into an agent transcript.

The runner does not install, upgrade, repair, upload, or send anything. A command check should therefore be read-only. Put authenticated, networked, or potentially expensive probes behind `"live": true`.

## Invocation

```bash
scripts/setup-health
scripts/setup-health --manifest health-checks.json --manifest team-health.json
scripts/setup-health --quick --summary
scripts/setup-health --live --json
```

- `--manifest` is repeatable. Without it, the runner uses the `health-checks.json` beside its repository root.
- `--quick` skips checks marked `"quick": false`.
- `--live` enables checks marked `"live": true`; they are skipped otherwise.
- `--summary` emits only failures, warnings, and counts.
- `--json` emits stable structured results.
- Exit status is 1 when a required check fails. Optional failures are warnings and do not change the exit status.

## Manifest format

```json
{
  "version": 1,
  "name": "Example team",
  "checks": [
    {
      "id": "version.example",
      "type": "version",
      "label": "Example CLI",
      "command": ["example", "--version"],
      "minimum": "2.4.0"
    }
  ]
}
```

Every check needs a stable `id` and `type`. `label` is optional. Common fields are:

- `optional`: turn a failure into a warning.
- `live`: run only with explicit `--live`.
- `quick: false`: skip during quick startup checks.
- `timeoutSeconds`: command timeout (default 15 seconds for run checks).

String values support `{home}`, `{agent_dir}`, and `{manifest_dir}` placeholders plus normal `~` and environment-variable expansion.

## Check types

| Type | Required fields | Purpose |
| --- | --- | --- |
| `command` | `command` string | Verify a command is on PATH. |
| `version` | `command` array; `minimum` or `exact` optional | Run a version command and compare numeric dotted versions. `regex` can override parsing. |
| `run` | `command` array | Require a read-only command to exit 0. `expectStdout` can assert a non-sensitive pattern; output remains suppressed. |
| `file` | `path`, or `paths` alternatives | Require an existing path. Supports `kind: file|directory` and `executable`. |
| `same_file` | `expected`, `actual` | Detect stale installed helper copies by byte equality. |
| `file_age` | `path`, `maximumDays` | Check the age of a trusted freshness marker. |
| `broken_symlinks` | `path` | Find broken links below a resource directory. `allowMissing` permits an absent root. |
| `json_values` | `path`, `expected` object | Compare exact values at dotted JSON paths. |
| `models` | `path`, `expected` array | Check Pi `enabledModels` (or legacy `models`) after removing thinking-level suffixes. |
| `packages` | `settings` | Check exact `expectedSources` and/or alternative source groups in `expectedAnyOf`. |

## Result contract

Each result contains:

```json
{
  "id": "version.example",
  "label": "Example CLI",
  "status": "pass",
  "message": "version 2.4.1",
  "duration_ms": 12
}
```

Statuses are `pass`, `warn`, `fail`, or `skip`. Consumers should alert on `fail`; warnings are suitable for manual reports but should not create noisy startup notifications.

Machine health cannot prove behavioral correctness such as safe domain matching, account identity selection, validator contracts, or package tarball contents. Keep those assertions in the owning repository's CI.
