"""
Task: nextjs-server-action-fallback-shell
Repo: vercel/next.js @ 6a8a31a7f42bb7d133aed5a6d854d069883aa57b
PR:   91711

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: app-page.ts is a build template compiled by webpack/turbopack at next build
time. It cannot be imported or called outside the full Next.js build pipeline.
All checks necessarily use source analysis.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TARGET = f"{REPO}/packages/next/src/build/templates/app-page.ts"


def _read_stripped():
    """Read the target file with comments removed (prevents gaming via comments)."""
    src = Path(TARGET).read_text()
    src = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    return src


def _get_static_path_key_region(src: str, window: int = 1500) -> str:
    """Extract the region around `let staticPathKey` declaration."""
    idx = src.index("let staticPathKey")
    return src[idx : idx + window]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """app-page.ts must have balanced braces and export the handler function."""
    src = Path(TARGET).read_text()

    depth = 0
    for ch in src:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        assert depth >= 0, "Unbalanced braces (depth went negative)"
    assert depth == 0, f"Unbalanced braces (final depth={depth})"

    assert re.search(
        r"export\s+async\s+function\s+handler", src
    ), "Missing 'export async function handler'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_server_action_guard_in_static_path_key():
    """The staticPathKey condition must reference server actions.

    On the buggy base commit, the condition at ~line 621 sets staticPathKey for
    all dynamic SSG fallback requests, including server action requests. The fix
    must add a server-action-aware guard to this condition.

    Accepts any reasonable naming: isPossibleServerAction, isServerAction,
    isActionRequest, Next-Action header check, actionId, etc.
    """
    src = _read_stripped()
    region = _get_static_path_key_region(src)

    # Look for server action guard specifically (variable names like isPossibleServerAction,
    # isServerAction, etc.) - NOT just any occurrence of "Action" which could be in
    # unrelated variables like serverActionsManifest
    has_action_ref = bool(
        re.search(r"is[A-Za-z]*[Ss]erver[Aa]ction", region)  # isPossibleServerAction, isServerAction
        or re.search(r"[Aa]ctionRequest", region)
        or re.search(r"[Nn]ext-[Aa]ction", region)
        or re.search(r"actionId", region)
        or re.search(r"actionHeader", region)
    )
    assert has_action_ref, (
        "staticPathKey condition has no server-action reference — "
        "server action requests will incorrectly enter the fallback rendering block"
    )


# [pr_diff] fail_to_pass
def test_server_action_excluded_from_static_path_key():
    """Server actions must be EXCLUDED (negated) from staticPathKey assignment.

    It's not enough to merely reference server actions — the condition must
    negate/exclude them so that staticPathKey is NOT set for action requests.
    Accepts: !isPossibleServerAction, !isServerAction, === false, early return, etc.
    """
    src = _read_stripped()
    region = _get_static_path_key_region(src)

    # Check negation in the staticPathKey region itself
    has_negation = bool(
        re.search(r"!\s*is[A-Za-z]*[Aa]ction", region)
        or re.search(r"!\s*isPossible[A-Za-z]*[Aa]ction", region)
        or re.search(r"[Aa]ction\s*===?\s*false", region)
        or re.search(r"false\s*===?\s*[A-Za-z]*[Aa]ction", region)
        or re.search(r"!\s*\w*[Aa]ction[A-Za-z]*", region)
    )

    # Also accept early-return pattern before staticPathKey
    if not has_negation:
        idx = src.index("let staticPathKey")
        before = src[max(0, idx - 3000) : idx]
        has_negation = bool(
            re.search(
                r"if\s*\([^)]*[Aa]ction[^)]*\)\s*\{\s*[\s\S]{0,200}return", before
            )
        )

    assert has_negation, (
        "staticPathKey condition does not exclude server actions — "
        "action requests will get the fallback HTML shell prepended"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_dev_mode_preserved():
    """routeModule.isDev path must still be present in staticPathKey condition.

    Dev mode relies on staticPathKey being set when routeModule.isDev is true.
    The fix must not remove this branch.
    """
    src = _read_stripped()
    region = _get_static_path_key_region(src)
    assert re.search(r"routeModule\.isDev", region), (
        "routeModule.isDev removed from staticPathKey condition — breaks dev mode"
    )


# [pr_diff] pass_to_pass
def test_ssg_dynamic_fallback_preserved():
    """isSSG, pageIsDynamic, and fallbackRouteParams must remain in the condition.

    These are the existing conditions for setting staticPathKey on dynamic SSG
    fallback routes. The fix should add an exclusion for actions, not remove
    these conditions.
    """
    src = _read_stripped()
    region = _get_static_path_key_region(src)
    assert re.search(r"isSSG", region), "isSSG missing from staticPathKey condition"
    assert re.search(r"pageIsDynamic", region), (
        "pageIsDynamic missing from staticPathKey condition"
    )
    assert re.search(r"fallbackRouteParams", region), (
        "fallbackRouteParams missing from staticPathKey condition"
    )


# [static] pass_to_pass
def test_handler_not_stub():
    """handler() must be exported and non-trivial (>100 lines, file >30KB)."""
    src = Path(TARGET).read_text()

    m = re.search(r"export\s+async\s+function\s+handler", src)
    assert m, "handler function not exported"

    after_handler = src[m.start() :]
    assert len(after_handler.splitlines()) >= 100, "handler function appears gutted"
    assert len(src.encode()) >= 30000, (
        f"File is only {len(src.encode())} bytes — appears truncated/gutted"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:407 @ 6a8a31a
def test_no_relative_require():
    """No relative-path require() in build template (AGENTS.md:407).

    app-page.ts is traced by webpack/turbopack at build time. Relative require()
    paths won't be resolvable from the user's project. Helpers must be exported
    from entry-base.ts and accessed via entryBase.*.
    """
    src = _read_stripped()
    matches = re.findall(r'require\s*\(\s*["\']\.\.?/', src)
    assert len(matches) == 0, (
        f"Found {len(matches)} relative-path require() calls in build template"
    )


# [agent_config] pass_to_pass — AGENTS.md:306 @ 6a8a31a
def test_no_hardcoded_secrets():
    """No hardcoded secret values in source (AGENTS.md:306)."""
    src = Path(TARGET).read_text()
    assert not re.search(
        r"(?:api[_-]?key|secret[_-]?key|password|credential)\s*[:=]\s*['\"][^'\"]+['\"]",
        src,
        re.IGNORECASE,
    ), "Potential hardcoded secret value found in source"


# [agent_config] pass_to_pass — AGENTS.md:398 @ 6a8a31a
def test_no_react_server_dom_webpack_import():
    """react-server-dom-webpack/* imports must stay in entry-base.ts (AGENTS.md:398).

    Build templates must consume these through entryBase.* exports, not import
    them directly.
    """
    src = _read_stripped()
    matches = re.findall(r"""(?:import|require)\s*\(?['"]\s*react-server-dom-webpack""", src)
    assert len(matches) == 0, (
        f"Found {len(matches)} direct react-server-dom-webpack import(s) in build template — "
        "must use entryBase.* exports instead"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_check_error_codes():
    """Repo's error codes check passes (pass_to_pass).

    Verifies that all error codes in the Next.js package are properly defined.
    """
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm run check-error-codes"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check-error-codes failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_eslint():
    """Repo's ESLint passes on app-page.ts (pass_to_pass).

    Verifies that the modified build template passes ESLint checks.
    """
    r = subprocess.run(
        ["bash", "-c", f"corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm exec eslint --config eslint.cli.config.mjs {TARGET}"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Repo's Prettier formatting passes on app-page.ts (pass_to_pass).

    Verifies that the modified build template is properly formatted.
    """
    r = subprocess.run(
        ["bash", "-c", f"corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm exec prettier --check {TARGET}"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_ast_grep():
    """Repo's ast-grep linting passes (pass_to_pass).

    Verifies that the codebase passes ast-grep pattern matching for code quality.
    """
    r = subprocess.run(
        ["bash", "-c", "corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm exec ast-grep scan"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ast-grep scan failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"

