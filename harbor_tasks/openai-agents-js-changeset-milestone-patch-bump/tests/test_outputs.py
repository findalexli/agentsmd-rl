"""Behavioral tests for the changeset milestone-assignment script.

The script under test mutates remote GitHub state via fetch() calls. We
exercise it by importing the module from a Node harness that replaces
globalThis.fetch with a recorder, then assert on the recorded calls.

The Node harness source is embedded below and written to a tmp file at
runtime so that this directory only contains the test files Harbor
expects.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/openai-agents-js"
SCRIPT = (
    Path(REPO)
    / ".codex"
    / "skills"
    / "changeset-validation"
    / "scripts"
    / "changeset-assign-milestone.mjs"
)

_RUNNER_SOURCE = r"""
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const [, , bump, milestonesJson, scriptAbsPath] = process.argv;
const milestones = JSON.parse(milestonesJson);

const tmp = mkdtempSync(join(tmpdir(), 'milestone-test-'));
const eventPath = join(tmp, 'event.json');
writeFileSync(eventPath, JSON.stringify({
    repository: { owner: { login: 'foo' }, name: 'bar' },
    pull_request: { number: 42 },
}));
const bumpPath = join(tmp, 'bump.json');
writeFileSync(bumpPath, JSON.stringify({ required_bump: bump }));

process.env.GITHUB_TOKEN = 'fake-token';
process.env.GITHUB_EVENT_PATH = eventPath;

const calls = [];
globalThis.fetch = async (url, opts = {}) => {
    const method = (opts && opts.method) || 'GET';
    const entry = { method, url };
    if (opts && opts.body) {
        try { entry.body = JSON.parse(opts.body); }
        catch { entry.body = opts.body; }
    }
    calls.push(entry);
    if (method === 'GET' && url.includes('/milestones?')) {
        return { ok: true, status: 200, json: async () => milestones };
    }
    if (method === 'PATCH' && url.includes('/issues/')) {
        return { ok: true, status: 200, json: async () => ({}) };
    }
    return { ok: false, status: 404, json: async () => ({}) };
};

process.argv = ['node', 'driver', bumpPath];

await import(pathToFileURL(scriptAbsPath).href);

await new Promise((r) => setTimeout(r, 50));

process.stdout.write(JSON.stringify({ calls }) + '\n');
"""


def _runner_path() -> Path:
    """Materialise the Node runner once per test session."""
    cached = Path(tempfile.gettempdir()) / "_milestone_runner.mjs"
    if not cached.exists() or cached.read_text() != _RUNNER_SOURCE:
        cached.write_text(_RUNNER_SOURCE)
    return cached


def run_harness(bump: str, milestones: list[dict]) -> list[dict]:
    """Drive the script with a mocked fetch and return the recorded calls."""
    runner = _runner_path()
    proc = subprocess.run(
        [
            "node",
            str(runner),
            bump,
            json.dumps(milestones),
            str(SCRIPT),
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert proc.returncode == 0, (
        f"Harness exited {proc.returncode}\n"
        f"--- stdout ---\n{proc.stdout}\n"
        f"--- stderr ---\n{proc.stderr}"
    )
    last_line = proc.stdout.strip().splitlines()[-1]
    payload = json.loads(last_line)
    return payload["calls"]


def patch_call(calls: list[dict]) -> dict | None:
    for c in calls:
        if c.get("method") == "PATCH" and "/issues/" in c.get("url", ""):
            return c
    return None


# ---------------------------------------------------------------------------
# Sanity: prerequisite files exist and Node can parse the script.
# ---------------------------------------------------------------------------


def test_target_script_present():
    assert SCRIPT.is_file(), f"script missing: {SCRIPT}"


def test_node_syntax_check():
    """`node --check` succeeds on the script (pass_to_pass)."""
    proc = subprocess.run(
        ["node", "--check", str(SCRIPT)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"syntax error:\n{proc.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass: patch bumps must select the LOWEST X.Y.x milestone, not the
# newest. The script sorts milestones major-then-minor descending, so the
# lowest is the last entry of the sorted array.
# ---------------------------------------------------------------------------


def test_patch_three_milestones_picks_lowest():
    """With three open X.Y.x milestones, patch bump targets the oldest one."""
    milestones = [
        {"number": 30, "title": "0.5.x"},
        {"number": 20, "title": "0.4.x"},
        {"number": 10, "title": "0.3.x"},
    ]
    calls = run_harness("patch", milestones)
    pc = patch_call(calls)
    assert pc is not None, f"no PATCH call recorded: {calls}"
    assert pc["body"]["milestone"] == 10, (
        f"patch bump should target the lowest milestone (#10 '0.3.x'); "
        f"got {pc['body']['milestone']}"
    )


def test_patch_two_milestones_picks_older():
    """With two milestones, patch should pick the older (0.4.x) one."""
    milestones = [
        {"number": 7, "title": "0.5.x"},
        {"number": 3, "title": "0.4.x"},
    ]
    calls = run_harness("patch", milestones)
    pc = patch_call(calls)
    assert pc is not None, f"no PATCH call recorded: {calls}"
    assert pc["body"]["milestone"] == 3, (
        f"patch bump with two milestones should target #3 '0.4.x'; "
        f"got {pc['body']['milestone']}"
    )


def test_patch_unsorted_input_still_picks_lowest():
    """Caller-provided order must not matter — the script sorts internally."""
    milestones = [
        {"number": 4, "title": "0.4.x"},
        {"number": 5, "title": "0.5.x"},
        {"number": 3, "title": "0.3.x"},
    ]
    calls = run_harness("patch", milestones)
    pc = patch_call(calls)
    assert pc is not None
    assert pc["body"]["milestone"] == 3, (
        f"after internal sort, patch should target lowest (#3 '0.3.x'); "
        f"got {pc['body']['milestone']}"
    )


def test_patch_higher_major_picks_lowest_overall():
    """Across majors, patch still selects the lowest (oldest) entry."""
    milestones = [
        {"number": 100, "title": "1.0.x"},
        {"number": 50, "title": "0.9.x"},
        {"number": 1, "title": "0.1.x"},
    ]
    calls = run_harness("patch", milestones)
    pc = patch_call(calls)
    assert pc is not None
    assert pc["body"]["milestone"] == 1, (
        f"patch should target the oldest series '0.1.x' (#1); "
        f"got {pc['body']['milestone']}"
    )


def test_non_matching_titles_filtered_out():
    """Non-X.Y.x titles are filtered; lowest of the remaining is selected."""
    milestones = [
        {"number": 99, "title": "Backlog"},
        {"number": 50, "title": "Future"},
        {"number": 5, "title": "0.4.x"},
        {"number": 4, "title": "0.3.x"},
    ]
    calls = run_harness("patch", milestones)
    pc = patch_call(calls)
    assert pc is not None
    assert pc["body"]["milestone"] == 4, (
        f"non-matching titles should be filtered; expected #4 '0.3.x', "
        f"got {pc['body']['milestone']}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: minor-bump and edge-case behaviour is unchanged by the fix.
# ---------------------------------------------------------------------------


def test_minor_three_milestones_picks_second_newest():
    """Minor bump picks the second-most-recent milestone."""
    milestones = [
        {"number": 30, "title": "0.5.x"},
        {"number": 20, "title": "0.4.x"},
        {"number": 10, "title": "0.3.x"},
    ]
    calls = run_harness("minor", milestones)
    pc = patch_call(calls)
    assert pc is not None, f"no PATCH call recorded: {calls}"
    assert pc["body"]["milestone"] == 20, (
        f"minor bump should target second-newest (#20 '0.4.x'); "
        f"got {pc['body']['milestone']}"
    )


def test_minor_with_one_milestone_falls_back_to_only_one():
    """Minor bump falls back to the sole milestone when no second exists."""
    milestones = [{"number": 99, "title": "0.7.x"}]
    calls = run_harness("minor", milestones)
    pc = patch_call(calls)
    assert pc is not None
    assert pc["body"]["milestone"] == 99


def test_patch_with_one_milestone_uses_it():
    """Patch with a single milestone uses that milestone (lowest == only)."""
    milestones = [{"number": 99, "title": "0.7.x"}]
    calls = run_harness("patch", milestones)
    pc = patch_call(calls)
    assert pc is not None
    assert pc["body"]["milestone"] == 99


def test_none_bump_skips_assignment():
    """required_bump='none' performs no API calls at all."""
    milestones = [{"number": 1, "title": "0.3.x"}]
    calls = run_harness("none", milestones)
    assert calls == [], f"expected no fetch calls for 'none' bump; got {calls}"
