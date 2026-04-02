"""
Task: opencode-changelog-deterministic-commit-range
Repo: anomalyco/opencode @ ee018d5c82a593907bae9011bc074766e670d593
PR:   19987

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

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
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_changelog_runs_without_llm_sdk():
    """changelog.ts must not import @opencode-ai/sdk or @opencode-ai/script.

    Base code: top-level imports of both packages exist.  The correct fix
    removes those imports entirely so the script gathers commits
    deterministically without the LLM SDK.

    Structural check because: TS module — can only execute via bun subprocess,
    and the SDK packages happen to be installed in the Docker image so the
    import itself wouldn't crash.  We need to verify the imports are gone.
    """
    src = (Path(REPO) / "script/changelog.ts").read_text()
    assert "@opencode-ai/sdk" not in src, (
        "changelog.ts still imports @opencode-ai/sdk — script relies on LLM SDK"
    )
    assert "@opencode-ai/script" not in src, (
        "changelog.ts still imports @opencode-ai/script — script relies on LLM SDK"
    )


# [pr_diff] fail_to_pass
def test_help_documents_from_and_to_flags():
    """changelog.ts must not import LLM SDK and must declare --from/--to flags.

    Base code: @opencode-ai imports at the top level mean the script depends on
    the LLM SDK.  Fixed code removes those imports; the CLI flags --from and
    --to must also be present for deterministic range control.

    Structural check because: base code's SDK packages may be installed in
    the Docker image, so bun --help would succeed on both base and fixed.
    The f2p signal comes from the SDK import removal.
    """
    src = (Path(REPO) / "script/changelog.ts").read_text()
    assert "@opencode-ai" not in src, (
        "LLM SDK imports still present — script still depends on LLM"
    )
    assert "--from" in src, "changelog.ts missing --from flag"
    assert "--to" in src, "changelog.ts missing --to flag"


# [pr_diff] fail_to_pass
def test_changelog_accepts_from_to_without_import_errors():
    """changelog.ts must use deterministic gh api / git log, not LLM calls.

    Base code: calls createOpencode(), session.create(), session.prompt() — the
    LLM resolves the commit range.  Fixed code replaces this with gh api + git
    log calls so commit gathering is deterministic.

    Structural check because: actual execution needs GitHub API access and a
    valid release history.
    """
    src = (Path(REPO) / "script/changelog.ts").read_text()
    # No LLM SDK usage
    assert "createOpencode" not in src, (
        "changelog.ts still calls createOpencode() — LLM still owns the commit range"
    )
    assert "session.create" not in src, (
        "changelog.ts still calls session.create() — LLM session still present"
    )
    assert "session.prompt" not in src, (
        "changelog.ts still calls session.prompt() — LLM summarisation still present"
    )
    # Deterministic commands present
    assert re.search(r"gh api|git log", src), (
        "changelog.ts missing deterministic gh api / git log calls"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural checks on fixed files
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


# [agent_config] pass_to_pass — AGENTS.md:13 @ ee018d5c82a593907bae9011bc074766e670d593
def test_no_any_type():
    """Changed files must not use the `any` type (AGENTS.md line 13)."""
    for f in ("script/changelog.ts", "script/version.ts"):
        src = (Path(REPO) / f).read_text()
        for i, line in enumerate(src.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            if re.search(r":\s*any\b|<any\b|\bas\s+any\b", stripped):
                assert False, f"{f}:{i} uses `any` type: {stripped}"
