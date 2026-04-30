"""Behavioral checks for warden-refskills-restructure-distributed-warden-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/warden")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SKILL.md')
    assert 'description: Full-repository code sweep. Scans every file with Warden, verifies findings through deep tracing, creates draft PRs for validated issues. Use when asked to "sweep the repo", "scan everyth' in text, "expected to find: " + 'description: Full-repository code sweep. Scans every file with Warden, verifies findings through deep tracing, creates draft PRs for validated issues. Use when asked to "sweep the repo", "scan everyth'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SKILL.md')
    assert 'Run a full-repository Warden sweep: scan files, verify findings, create a tracking issue, open draft PRs for validated issues, and organize the final report.' in text, "expected to find: " + 'Run a full-repository Warden sweep: scan files, verify findings, create a tracking issue, open draft PRs for validated issues, and organize the final report.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SKILL.md')
    assert '7. For interrupted or partial runs, read `references/resume-and-artifacts.md` and continue from the first incomplete phase.' in text, "expected to find: " + '7. For interrupted or partial runs, read `references/resume-and-artifacts.md` and continue from the first incomplete phase.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SOURCES.md')
    assert '| Known issues/workarounds | partial | Resume, partial scans, skipped findings, and existing PR dedup are covered; CI follow-up and rate-limit recovery are not. |' in text, "expected to find: " + '| Known issues/workarounds | partial | Resume, partial scans, skipped findings, and existing PR dedup are covered; CI follow-up and rate-limit recovery are not. |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SOURCES.md')
    assert '| Version/migration variance | partial | Current artifact names and script interfaces are documented; no formal migration path exists for old sweep directories. |' in text, "expected to find: " + '| Version/migration variance | partial | Current artifact names and script interfaces are documented; no formal migration path exists for old sweep directories. |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SOURCES.md')
    assert '| Patch behavior | covered | `references/patch-phase.md` and `references/patch-prompt.md` define triage, worktree isolation, draft PR creation, and cleanup. |' in text, "expected to find: " + '| Patch behavior | covered | `references/patch-phase.md` and `references/patch-prompt.md` define triage, worktree isolation, draft PR creation, and cleanup. |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SPEC.md')
    assert 'It exists for batch remediation work where a normal targeted Warden run is too narrow. The workflow is intentionally conservative: scan broadly, verify before patching, deduplicate against existing PR' in text, "expected to find: " + 'It exists for batch remediation work where a normal targeted Warden run is too narrow. The workflow is intentionally conservative: scan broadly, verify before patching, deduplicate against existing PR'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SPEC.md')
    assert '- Common user requests: "sweep the repo", "scan everything", "find all bugs", "full codebase review", "batch code analysis", "run Warden across the whole repository".' in text, "expected to find: " + '- Common user requests: "sweep the repo", "scan everything", "find all bugs", "full codebase review", "batch code analysis", "run Warden across the whole repository".'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/SPEC.md')
    assert 'The `warden-sweep` skill runs a full-repository Warden scan, verifies findings through deeper code tracing, and creates draft PRs for validated issues.' in text, "expected to find: " + 'The `warden-sweep` skill runs a full-repository Warden scan, verifies findings through deeper code tracing, and creates draft PRs for validated issues.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/issue-phase.md')
    assert '3. If the script fails, show the error and continue to the patch phase. PRs can still be created without a tracking issue.' in text, "expected to find: " + '3. If the script fails, show the error and continue to the patch phase. PRs can still be created without a tracking issue.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/issue-phase.md')
    assert 'Create a tracking issue that ties all generated PRs together and gives reviewers one overview.' in text, "expected to find: " + 'Create a tracking issue that ties all generated PRs together and gives reviewers one overview.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/issue-phase.md')
    assert 'uv run <skill-root>/scripts/create_issue.py ${SWEEP_DIR}' in text, "expected to find: " + 'uv run <skill-root>/scripts/create_issue.py ${SWEEP_DIR}'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/organize-phase.md')
    assert 'Finalize sweep artifacts, security views, PR links, and the summary report.' in text, "expected to find: " + 'Finalize sweep artifacts, security views, PR links, and the summary report.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/organize-phase.md')
    assert '3. If the script fails, show the error and note which phases completed.' in text, "expected to find: " + '3. If the script fails, show the error and note which phases completed.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/organize-phase.md')
    assert '2. Confirm `summary.md` and `data/report.json` were produced.' in text, "expected to find: " + '2. Confirm `summary.md` and `data/report.json` were produced.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/patch-phase.md')
    assert "Run patch work using the host agent's task/delegation mechanism when available. Read `references/patch-prompt.md` and substitute the finding values and worktree path into the `${...}` placeholders." in text, "expected to find: " + "Run patch work using the host agent's task/delegation mechanism when available. Read `references/patch-prompt.md` and substitute the finding values and worktree path into the `${...}` placeholders."[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/patch-phase.md')
    assert '2. Chunk overlap: if a PR touches the same file, read `data/pr-diffs/<number>.diff` and check whether changed hunks overlap or sit within roughly 10 lines of the finding range.' in text, "expected to find: " + '2. Chunk overlap: if a PR touches the same file, read `data/pr-diffs/<number>.diff` and check whether changed hunks overlap or sit within roughly 10 lines of the finding range.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/patch-phase.md')
    assert 'Skip the finding only when there is both chunk overlap and the PR addresses the same concern. Record it with `"status": "existing"` and the matching `prUrl`.' in text, "expected to find: " + 'Skip the finding only when there is both chunk overlap and the PR addresses the same concern. Record it with `"status": "existing"` and the matching `prUrl`.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/resume-and-artifacts.md')
    assert 'Continue from the first incomplete phase. Do not start a new sweep unless the user asks for a clean run.' in text, "expected to find: " + 'Continue from the first incomplete phase. Do not start a new sweep unless the user asks for a clean run.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/resume-and-artifacts.md')
    assert 'Use this reference when resuming a partial sweep or inspecting generated files.' in text, "expected to find: " + 'Use this reference when resuming a partial sweep or inspecting generated files.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/resume-and-artifacts.md')
    assert '4. For issue, `create_issue.py` skips if `issueUrl` exists in the manifest.' in text, "expected to find: " + '4. For issue, `create_issue.py` skips if `issueUrl` exists in the manifest.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/scan-phase.md')
    assert '4. Treat exit code `2` as partial: report timed-out and errored files separately, then continue only if the user accepts the partial results.' in text, "expected to find: " + '4. Treat exit code `2` as partial: report timed-out and errored files separately, then continue only if the user accepts the partial results.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/scan-phase.md')
    assert 'Scanned **{filesScanned}** files, **{filesTimedOut}** timed out, **{filesErrored}** errors.' in text, "expected to find: " + 'Scanned **{filesScanned}** files, **{filesTimedOut}** timed out, **{filesErrored}** errors.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/scan-phase.md')
    assert '| 1 | **HIGH** | security-review | `src/db/query.ts:42` | SQL injection in query builder |' in text, "expected to find: " + '| 1 | **HIGH** | security-review | `src/db/query.ts:42` | SQL injection in query builder |'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/script-interfaces.md')
    assert 'Runs setup and scan in one call: generates a run ID, creates the sweep directory, checks dependencies, creates the `warden` label, enumerates files, runs Warden per file, writes `scan-index.jsonl`, an' in text, "expected to find: " + 'Runs setup and scan in one call: generates a run ID, creates the sweep directory, checks dependencies, creates the `warden` label, enumerates files, runs Warden per file, writes `scan-index.jsonl`, an'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/script-interfaces.md')
    assert 'Tags security findings, labels security PRs, updates finding reports with PR links, posts final results to the tracking issue, generates the summary report, and finalizes the manifest.' in text, "expected to find: " + 'Tags security findings, labels security PRs, updates finding reports with PR links, posts final results to the tracking issue, generates the summary report, and finalizes the manifest.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/script-interfaces.md')
    assert 'Use this reference before running Warden Sweep scripts. Run scripts from the repository root and pass the host skill-root path.' in text, "expected to find: " + 'Use this reference before running Warden Sweep scripts. Run scripts from the repository root and pass the host skill-root path.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/verify-phase.md')
    assert "2. Launch verification work using the host agent's task/delegation mechanism when available. Process findings in parallel batches up to 8 if the host supports parallel work." in text, "expected to find: " + "2. Launch verification work using the host agent's task/delegation mechanism when available. Process findings in parallel batches up to 8 if the host supports parallel work."[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/verify-phase.md')
    assert '| 1 | **HIGH** | high | `src/db/query.ts:42` | SQL injection in query builder | User input flows directly into... |' in text, "expected to find: " + '| 1 | **HIGH** | high | `src/db/query.ts:42` | SQL injection in query builder | User input flows directly into... |'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden-sweep/references/verify-phase.md')
    assert 'Deep-trace every finding before patching. This phase qualifies true issues and rejects false positives.' in text, "expected to find: " + 'Deep-trace every finding before patching. This phase qualifies true issues and rejects false positives.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SKILL.md')
    assert '| `<skill-root>/references/configuration.md` | Editing warden.toml, triggers, patterns, troubleshooting |' in text, "expected to find: " + '| `<skill-root>/references/configuration.md` | Editing warden.toml, triggers, patterns, troubleshooting |'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SKILL.md')
    assert '| `<skill-root>/references/creating-skills.md` | Writing custom skills, remote skills, skill discovery |' in text, "expected to find: " + '| `<skill-root>/references/creating-skills.md` | Writing custom skills, remote skills, skill discovery |'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SKILL.md')
    assert '| `<skill-root>/references/cli-reference.md` | Full option details, per-command flags, examples |' in text, "expected to find: " + '| `<skill-root>/references/cli-reference.md` | Full option details, per-command flags, examples |'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SOURCES.md')
    assert '| Config/runtime options | covered | `references/configuration.md` and `references/config-schema.md` cover `warden.toml` structure, fields, defaults, triggers, and environment variables. |' in text, "expected to find: " + '| Config/runtime options | covered | `references/configuration.md` and `references/config-schema.md` cover `warden.toml` structure, fields, defaults, triggers, and environment variables. |'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SOURCES.md')
    assert '- Keep Warden-specific skill creation guidance in this skill even though generic skill authoring belongs elsewhere, because Warden has its own discovery, config, and remote-skill behavior.' in text, "expected to find: " + '- Keep Warden-specific skill creation guidance in this skill even though generic skill authoring belongs elsewhere, because Warden has its own discovery, config, and remote-skill behavior.'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SOURCES.md')
    assert '| Version/migration variance | partial | Remote skill pinning and cache behavior are documented; package-version migration notes are not maintained here. |' in text, "expected to find: " + '| Version/migration variance | partial | Remote skill pinning and cache behavior are documented; package-version migration notes are not maintained here. |'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SPEC.md')
    assert 'It exists as the lightweight runtime companion to the Warden CLI. The skill should get agents to the right command or reference quickly without duplicating the full product documentation.' in text, "expected to find: " + 'It exists as the lightweight runtime companion to the Warden CLI. The skill should get agents to the right command or reference quickly without duplicating the full product documentation.'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SPEC.md')
    assert 'The `warden` skill teaches coding agents how to run Warden during local development, interpret its output, and update Warden configuration or skill definitions when asked.' in text, "expected to find: " + 'The `warden` skill teaches coding agents how to run Warden during local development, interpret its output, and update Warden configuration or skill definitions when asked.'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/SPEC.md')
    assert '- negative examples: repeated Warden reruns with no changes, invented config fields, stale CLI flags, or generic skill instructions that do not match Warden discovery' in text, "expected to find: " + '- negative examples: repeated Warden reruns with no changes, invented config fields, stale CLI flags, or generic skill instructions that do not match Warden discovery'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/cli-reference.md')
    assert '- Per-Command Options' in text, "expected to find: " + '- Per-Command Options'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/cli-reference.md')
    assert '- Severity Levels' in text, "expected to find: " + '- Severity Levels'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/cli-reference.md')
    assert '- Exit Codes' in text, "expected to find: " + '- Exit Codes'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/config-schema.md')
    assert '- Built-in Skip Patterns' in text, "expected to find: " + '- Built-in Skip Patterns'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/config-schema.md')
    assert '- Environment Variables' in text, "expected to find: " + '- Environment Variables'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/config-schema.md')
    assert '- Top-Level Structure' in text, "expected to find: " + '- Top-Level Structure'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/configuration.md')
    assert '- Environment Variables' in text, "expected to find: " + '- Environment Variables'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/configuration.md')
    assert '- Skill Configuration' in text, "expected to find: " + '- Skill Configuration'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/warden/references/configuration.md')
    assert '- Model Precedence' in text, "expected to find: " + '- Model Precedence'[:80]

