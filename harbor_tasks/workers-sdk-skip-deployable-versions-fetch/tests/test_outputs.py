"""Behavioral tests for cloudflare/workers-sdk#13072.

Validates the `wrangler versions deploy` skip-deployable-versions optimization
by running the post-PR vitest suite against the agent's modified deploy.ts.

The reference test file (versions.deploy.test.ts.post) is copied into the
repo at test time, overwriting whatever the agent left there. This guarantees
the snapshot expectations match the post-PR API and prevents the agent from
"passing" by mutating tests instead of fixing the code.
"""
import os
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/workers-sdk")
WRANGLER = REPO / "packages" / "wrangler"
TEST_FILE = WRANGLER / "src" / "__tests__" / "versions" / "versions.deploy.test.ts"
DEPLOY_FILE = WRANGLER / "src" / "versions" / "deploy.ts"
REFERENCE_TEST = Path("/opt/fixtures/versions.deploy.test.ts.post")
VITEST = WRANGLER / "node_modules" / ".bin" / "vitest"


def _ensure_reference_test_in_place():
    assert REFERENCE_TEST.exists(), f"Reference test missing: {REFERENCE_TEST}"
    shutil.copy(REFERENCE_TEST, TEST_FILE)


def _run(cmd, cwd=WRANGLER, timeout=300):
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "1"},
    )


def test_versions_deploy_full_suite_passes():
    """fail_to_pass: post-PR vitest suite for `wrangler versions deploy`.

    The reference test file expects "Fetching versions" snapshots and uses
    an mswGetVersion30000000 handler that is only consulted when
    fetchDeployableVersions is skipped. At base commit, deploy.ts emits
    "Fetching deployable versions" and always calls fetchDeployableVersions,
    causing 16 of 48 vitest assertions to fail.
    """
    _ensure_reference_test_in_place()
    r = _run(
        [str(VITEST), "run", "src/__tests__/versions/versions.deploy.test.ts"],
        timeout=300,
    )
    assert r.returncode == 0, (
        f"vitest failed (exit {r.returncode}).\n"
        f"--- stdout (last 2500) ---\n{r.stdout[-2500:]}\n"
        f"--- stderr (last 1500) ---\n{r.stderr[-1500:]}"
    )


def test_versions_deploy_max_versions_subtest_passes():
    """fail_to_pass: targets the `--yes` + 3-version-IDs path specifically.

    These tests exercise the new optimization directly: when --yes and
    explicit version IDs are provided, fetchDeployableVersions is skipped
    and individual GET /versions/:id calls are made instead. The reference
    test registers `mswGetVersion30000000` for this exact pathway.
    """
    _ensure_reference_test_in_place()
    r = _run(
        [
            str(VITEST),
            "run",
            "src/__tests__/versions/versions.deploy.test.ts",
            "-t",
            "max versions restrictions",
        ],
        timeout=300,
    )
    assert r.returncode == 0, (
        f"max versions subtest failed (exit {r.returncode}).\n"
        f"--- stdout (last 2000) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (last 1500) ---\n{r.stderr[-1500:]}"
    )


def test_repo_typecheck_passes():
    """pass_to_pass (origin: repo_tests): wrangler tsc clean.

    The repo's own typecheck must still pass after any agent edit.
    """
    r = _run(["pnpm", "check:type"], timeout=600)
    assert r.returncode == 0, (
        f"pnpm check:type failed (exit {r.returncode}).\n"
        f"--- stdout (last 2000) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (last 1500) ---\n{r.stderr[-1500:]}"
    )


def test_versions_list_suite_passes():
    """pass_to_pass (origin: repo_tests): sibling versions.list.test.ts.

    Adjacent test file unrelated to this PR. Acts as a regression guard
    against agents who modify shared MSW helpers or test infrastructure.
    """
    r = _run(
        [str(VITEST), "run", "src/__tests__/versions/versions.list.test.ts"],
        timeout=300,
    )
    assert r.returncode == 0, (
        f"versions.list.test.ts failed (exit {r.returncode}).\n"
        f"--- stdout (last 2000) ---\n{r.stdout[-2000:]}\n"
        f"--- stderr (last 1500) ---\n{r.stderr[-1500:]}"
    )


def test_changeset_added_when_wrangler_modified():
    """pass_to_pass (origin: agent_config): AGENTS.md changeset rule.

    Per AGENTS.md (root): "Every change to package code requires a changeset
    or it will not trigger a release."

    This check is *vacuous* when the agent did not modify the wrangler source
    (e.g., NOP run). When the agent did modify wrangler source code, a NEW
    `.changeset/*.md` file referencing wrangler must accompany the change.
    """
    r = subprocess.run(
        ["git", "status", "--porcelain", "--", "packages/wrangler/src/"],
        cwd=str(REPO), capture_output=True, text=True, timeout=30,
    )
    # Exclude the __tests__/ tree — we overwrite the deploy test file from
    # the harness, so its status is not a signal of agent activity.
    wrangler_modified = False
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:]  # strip 2-char status + space
        if path.startswith("packages/wrangler/src/__tests__/"):
            continue
        wrangler_modified = True
        break
    if not wrangler_modified:
        return  # vacuous pass — agent didn't touch wrangler production source

    r = subprocess.run(
        ["git", "status", "--porcelain", "--", ".changeset/"],
        cwd=str(REPO), capture_output=True, text=True, timeout=30,
    )
    new_changeset_paths = [
        line[3:] for line in r.stdout.splitlines()
        if line.startswith("?? ") or line.startswith("A  ")
    ]
    new_changeset_paths = [p for p in new_changeset_paths if p.endswith(".md")]
    assert new_changeset_paths, (
        "AGENTS.md requires a changeset for every change to a published "
        "package, but no new file was added under .changeset/. "
        "Add a `.changeset/*.md` file with `\"wrangler\": patch` frontmatter."
    )

    bodies = [(REPO / p).read_text() for p in new_changeset_paths]
    assert any('"wrangler"' in b for b in bodies), (
        "A new changeset was added but none reference the wrangler package. "
        "Frontmatter should look like `\"wrangler\": patch`."
    )
