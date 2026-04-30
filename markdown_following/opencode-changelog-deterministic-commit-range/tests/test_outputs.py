"""
Task: opencode-changelog-deterministic-commit-range
Repo: anomalyco/opencode @ ee018d5c82a593907bae9011bc074766e670d593
PR:   19987

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/opencode"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence / minimal structure
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must exist and be non-trivial."""
    for f in (
        "script/changelog.ts",
        "script/version.ts",
        ".opencode/command/changelog.md",
        ".gitignore",
    ):
        p = Path(REPO) / f
        assert p.exists(), f"{f} does not exist"
        assert p.stat().st_size > 50, f"{f} is suspiciously small (stub?)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_changelog_help_deterministic():
    """Running `bun script/changelog.ts --help` must show 'non-draft' release behavior.

    Base help text says "Starting version (default: latest GitHub release)".
    Fixed help text says "Starting version (default: latest non-draft GitHub release)".
    The --help flag is supported in both versions but the output content differs,
    making this a reliable behavioral fail-to-pass test.
    """
    r = subprocess.run(
        ["bun", "script/changelog.ts", "--help"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"--help failed: {r.stderr}"
    assert "non-draft" in r.stdout, (
        "Help text doesn't mention 'non-draft' — script still uses old release logic.\n"
        f"Output: {r.stdout[:500]}"
    )


# [pr_diff] fail_to_pass
def test_changelog_transpile_no_llm_sdk():
    """Transpiling changelog.ts with Bun must not contain LLM SDK references.

    Base code has top-level imports:
      import { createOpencode } from "@opencode-ai/sdk/v2"
      import { Script } from "@opencode-ai/script"
    and calls session.create() / session.prompt() for LLM-based summarisation.

    Fixed code removes all of these so the script gathers commits deterministically.
    Uses Bun.Transpiler to convert TypeScript to JavaScript and inspects the output.
    """
    r = subprocess.run(
        ["bun", "-e",
         'const s = await Bun.file("script/changelog.ts").text();'
         'const t = new Bun.Transpiler({loader:"ts"});'
         'console.log(t.transformSync(s));'],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Transpile failed: {r.stderr}"
    assert "createOpencode" not in r.stdout, (
        "Transpiled output references createOpencode — LLM SDK still imported"
    )
    assert "@opencode-ai" not in r.stdout, (
        "Transpiled output references @opencode-ai SDK packages"
    )
    assert "session.prompt" not in r.stdout, (
        "Transpiled output calls session.prompt() — LLM summarisation still present"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural checks on non-executable files
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_version_pins_upper_bound():
    """version.ts must pass --to when invoking the changelog command.

    Base code: `opencode run --command changelog` — no upper-bound pin.
    Fixed code: reads GITHUB_SHA and passes `--to <sha>` so the commit range
    is deterministically capped at the release point.

    Structural check because: version.ts requires the full opencode CLI to run.
    """
    src = (Path(REPO) / "script/version.ts").read_text()
    assert "GITHUB_SHA" in src, (
        "version.ts does not reference GITHUB_SHA to pin the commit range upper bound"
    )
    changelog_lines = [l for l in src.splitlines() if "changelog" in l]
    assert changelog_lines, "No changelog invocation found in version.ts"
    assert any("--to" in l for l in changelog_lines), (
        "Changelog invocation does not pass --to to pin the upper bound.\n"
        "Lines: " + "\n".join(changelog_lines)
    )


# [pr_diff] fail_to_pass
def test_command_prompt_consumes_structured_data():
    """Command prompt must not instruct LLM to fetch releases or find PRs.

    Base prompt: tells LLM to "fetch the latest github release" and "find each PR".
    Fixed prompt: consumes pre-computed structured data piped from script/changelog.ts.

    Structural check because: this is a markdown prompt file, not executable code.
    """
    content = (Path(REPO) / ".opencode/command/changelog.md").read_text()
    assert not re.search(r"fetch the latest.*release", content, re.IGNORECASE), (
        "Command prompt still instructs LLM to fetch GitHub releases"
    )
    assert not re.search(r"find each PR", content, re.IGNORECASE), (
        "Command prompt still instructs LLM to find PRs"
    )
    assert re.search(r"script/changelog|changelog\.ts", content), (
        "Command prompt does not reference changelog script as structured input source"
    )


# [pr_diff] fail_to_pass
def test_gitignore_upcoming_changelog():
    """UPCOMING_CHANGELOG.md must be listed in .gitignore.

    Base .gitignore does not include it.  The fix adds it so the generated
    file is not accidentally committed.
    """
    gitignore = (Path(REPO) / ".gitignore").read_text()
    assert "UPCOMING_CHANGELOG" in gitignore, (
        "UPCOMING_CHANGELOG.md not found in .gitignore"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:12 @ ee018d5c82a593907bae9011bc074766e670d593
def test_no_try_catch():
    """Changed files must not use try/catch blocks (AGENTS.md line 12).

    Base changelog.ts has a try/catch inside buildNotes.
    Fixed code removes it by restructuring the logic.
    """
    for f in ("script/changelog.ts", "script/version.ts"):
        src = (Path(REPO) / f).read_text()
        non_comment = "\n".join(
            l for l in src.splitlines()
            if not l.strip().startswith("//") and not l.strip().startswith("*")
        )
        assert not re.search(r"\btry\s*\{", non_comment), (
            f"{f} contains a try/catch block (violates AGENTS.md:12)"
        )


# [agent_config] fail_to_pass — AGENTS.md:27-32 @ ee018d5c82a593907bae9011bc074766e670d593
def test_single_word_function_names():
    """Declared functions in changelog.ts must use single-word names (AGENTS.md lines 27-32).

    Base code declares multi-word camelCase functions: getLatestRelease, getCommits,
    filterRevertedCommits, getSection, summarizeCommit, generateChangelog, getContributors,
    buildNotes.  Fixed code uses single-word names: latest, diff, section, reverted,
    commits, contributors, published, thanks, format, ref.
    """
    src = (Path(REPO) / "script/changelog.ts").read_text()
    func_names = re.findall(r"\b(?:async\s+)?function\s+([a-zA-Z_]\w*)\s*[(<]", src)
    multi_word = [n for n in set(func_names) if re.search(r"[a-z][A-Z]", n)]
    assert not multi_word, (
        f"Multi-word camelCase function names violate AGENTS.md naming rule: "
        f"{', '.join(sorted(multi_word))}"
    )


# [agent_config] fail_to_pass — AGENTS.md:27-32 @ ee018d5c82a593907bae9011bc074766e670d593
def test_no_camelcase_locals():
    """Local variable declarations in changelog.ts must not use multi-word camelCase names (AGENTS.md lines 27-32).

    Base code declares camelCase locals: fromRef, toRef, commitData, sectionOrder,
    revertPattern, revertMsg.  Fixed code replaces all of these with single-word names.
    """
    src = (Path(REPO) / "script/changelog.ts").read_text()
    # Strip comment lines before scanning
    non_comment = "\n".join(
        l for l in src.splitlines()
        if not l.strip().startswith("//") and not l.strip().startswith("*")
    )
    # Match `const <camelCase>` or `let <camelCase>` where camelCase has a
    # lowercase-then-uppercase transition (e.g. fromRef, commitData)
    camel_vars = re.findall(
        r'\b(?:const|let)\s+([a-z][a-z]+[A-Z][a-zA-Z0-9]*)\b',
        non_comment,
    )
    assert not camel_vars, (
        f"Multi-word camelCase local variable names violate AGENTS.md naming rule: "
        f"{', '.join(sorted(set(camel_vars)))}"
    )


# [agent_config] pass_to_pass — AGENTS.md:13 @ ee018d5c82a593907bae9011bc074766e670d593
def test_no_any_type():
    """Changed files must not use the `any` type (AGENTS.md line 13)."""
    for f in ("script/changelog.ts", "script/version.ts"):
        src = (Path(REPO) / f).read_text()
        lines = src.splitlines()
        assert len(lines) > 10, f"{f} is too short ({len(lines)} lines) — likely a stub"
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            if re.search(r":\s*any\b|<any\b|\bas\s+any\b", stripped):
                assert False, f"{f}:{i} uses `any` type: {stripped}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's CI/CD tests that should pass on base
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Modified files pass Prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "prettier", "--check", "script/changelog.ts", "script/version.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build_changelog():
    """Repo's TypeScript changelog.ts builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "build", "./script/changelog.ts", "--target=bun", "--outdir=/tmp/dist"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build_version():
    """Repo's TypeScript version.ts builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "build", "./script/version.ts", "--target=bun", "--outdir=/tmp/dist"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")