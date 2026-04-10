"""
Task: openclaw-config-audit-exec-override
Repo: openclaw/openclaw @ 1ca4261d7e055d0be141ed79ebb1365d0fbc7364

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/openclaw"
TARGET_FILE = Path(REPO) / "src/security/audit.test.ts"
BASE_COMMIT = "1ca4261d7e055d0be141ed79ebb1365d0fbc7364"


def _strip_comments(code: str) -> str:
    """Remove JS single-line and block comments."""
    code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return code


def _get_agent_added_lines() -> list[str]:
    """Return lines added by the agent (diff vs base commit) in audit.test.ts."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--", "src/security/audit.test.ts"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    return [
        line[1:]
        for line in r.stdout.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]


@pytest.fixture(scope="module")
def vitest_result():
    return subprocess.run(
        ["npx", "vitest", "run", "src/security/audit.test.ts", "--reporter=verbose"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """audit.test.ts must parse without TypeScript syntax errors."""
    assert TARGET_FILE.exists(), f"{TARGET_FILE} not found"
    r = subprocess.run(
        [
            "node", "-e",
            "require('esbuild').transformSync("
            f"require('fs').readFileSync('{TARGET_FILE}','utf8'),"
            "{loader:'ts'})",
        ],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"TypeScript syntax error:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_exec_test_case_present():
    """audit.test.ts has a test case with exec in a gateway tools.allow array."""
    code = _strip_comments(TARGET_FILE.read_text())
    assert re.search(
        r"allow\s*:\s*\[[^\]]*['\"]exec['\"][^\]]*\]",
        code, re.DOTALL,
    ), (
        "No 'exec' found in a tools.allow array in audit.test.ts — "
        "add a test case that passes exec via gateway.tools.allow"
    )


# [pr_diff] fail_to_pass
def test_exec_expects_critical_severity():
    """The exec test case must assert critical severity (not just presence)."""
    code = _strip_comments(TARGET_FILE.read_text())
    # Both conditions must hold: exec in tools.allow, and critical severity expected
    has_exec_allow = re.search(
        r"allow\s*:\s*\[[^\]]*['\"]exec['\"]",
        code, re.DOTALL,
    )
    has_critical = re.search(
        r"expectedSeverity\s*:\s*['\"]critical['\"]",
        code,
    )
    assert has_exec_allow and has_critical, (
        "exec test case must exist AND expect critical severity — "
        f"exec_in_allow={bool(has_exec_allow)}, critical_expected={bool(has_critical)}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_vitest_suite_passes(vitest_result):
    """Full vitest run on audit.test.ts must exit 0 after the change."""
    out = vitest_result.stdout + vitest_result.stderr
    assert vitest_result.returncode == 0, f"Vitest failed:\n{out[-3000:]}"


# [repo_tests] pass_to_pass — CI/CD lint check
def test_repo_lint():
    """Repo's oxlint must pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "oxlint", "--type-aware"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — CI/CD typecheck (using tsgo)
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes via tsgo (pass_to_pass)."""
    r = subprocess.run(
        ["./node_modules/.bin/tsgo", "--noEmit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — CI/CD security audit tests
def test_repo_security_audit_tests():
    """Repo's security audit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/security/audit.test.ts", "--config", "vitest.unit.config.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    out = r.stdout + r.stderr
    assert r.returncode == 0, f"Security audit tests failed:\n{out[-1000:]}"


# [repo_tests] pass_to_pass — CI/CD comprehensive check
def test_repo_check():
    """Repo's comprehensive check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "check"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    out = r.stdout + r.stderr
    assert r.returncode == 0, f"Check failed:\n{out[-1000:]}"


# [repo_tests] pass_to_pass — CI/CD strict build smoke test
def test_repo_build_strict_smoke():
    """Repo's strict build smoke test passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "build:strict-smoke"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    out = r.stdout + r.stderr
    assert r.returncode == 0, f"Build strict smoke failed:\n{out[-1000:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:131,164 @ 1ca4261d7e055d0be141ed79ebb1365d0fbc7364
def test_uses_existing_test_pattern():
    """The exec test must be in the runConfigAuditCases cases array, not standalone."""
    code = _strip_comments(TARGET_FILE.read_text())
    # tools.allow with exec must appear inside an object with expectedSeverity,
    # which is the runConfigAuditCases pattern
    assert re.search(
        r"tools\s*:\s*\{[^}]*allow\s*:\s*\[[^\]]*['\"]exec['\"]",
        code, re.DOTALL,
    ), (
        "exec test case not found in tools.allow config pattern — "
        "AGENTS.md:131,164 says use existing patterns. "
        "Add exec to the runConfigAuditCases array, don't create a standalone test block."
    )


# [agent_config] pass_to_pass — AGENTS.md:144,147 @ 1ca4261d7e055d0be141ed79ebb1365d0fbc7364
def test_no_any_type():
    """Agent's changes must not introduce `any` type annotations."""
    added_lines = _get_agent_added_lines()
    for line in added_lines:
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
            continue
        if re.search(r'\b(as\s+any|:\sany\b|<any>)', line):
            assert False, (
                f"Agent added a line with `any` type — AGENTS.md:144 requires strict typing. "
                f"Use `unknown`, a real type, or a narrow adapter instead.\n"
                f"  {stripped}"
            )


# [agent_config] pass_to_pass — AGENTS.md:146 @ 1ca4261d7e055d0be141ed79ebb1365d0fbc7364
def test_no_lint_suppressions():
    """Agent's changes must not add @ts-nocheck or inline lint suppressions."""
    added_lines = _get_agent_added_lines()
    added_text = "\n".join(added_lines)
    suppression_patterns = [
        (r'@ts-nocheck', '@ts-nocheck'),
        (r'@ts-ignore', '@ts-ignore'),
        (r'@ts-expect-error', '@ts-expect-error'),
        (r'eslint-disable', 'eslint-disable'),
        (r'oxlint-ignore', 'oxlint-ignore'),
    ]
    for pattern, name in suppression_patterns:
        assert not re.search(pattern, added_text), (
            f"Agent added `{name}` — AGENTS.md:146 forbids inline lint suppressions."
        )


# [agent_config] pass_to_pass — AGENTS.md:220 @ 1ca4261d7e055d0be141ed79ebb1365d0fbc7364
def test_no_real_credentials_in_tests():
    """Added test config values must use obviously fake placeholders, not real credentials."""
    added_lines = _get_agent_added_lines()
    added_text = "\n".join(added_lines)

    # Check for real-looking API keys / tokens (e.g. sk-..., ghp_..., or long hex/base64)
    suspicious_patterns = [
        (r'\b(sk-[A-Za-z0-9]{20,})', "OpenAI-style API key (sk-...)"),
        (r'\b(ghp_[A-Za-z0-9]{36,}|ghs_[A-Za-z0-9]{36,})', "GitHub PAT (ghp_/ghs_...)"),
        (r'["\'][0-9a-fA-F]{32,}["\']', "long hex string (possible real token)"),
        # E.164 or NANP phone numbers
        (r'\+?1?\s*\(?\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}', "phone number"),
    ]
    for pattern, desc in suspicious_patterns:
        matches = re.findall(pattern, added_text)
        assert len(matches) == 0, (
            f"Agent added what looks like a {desc} — AGENTS.md:220 requires "
            f"obviously fake placeholders (e.g. 'secret', 'test-token') in tests, "
            f"not real config values.\n"
            f"Matches: {matches}"
        )


# [agent_config] pass_to_pass — AGENTS.md:162 @ 1ca4261d7e055d0be141ed79ebb1365d0fbc7364
def test_no_prototype_mutation():
    """Agent's test must not use prototype mutation for sharing behavior."""
    added_lines = _get_agent_added_lines()
    added_text = "\n".join(added_lines)
    proto_assigns = re.findall(r'\.prototype\.\w+\s*=', added_text)
    assert len(proto_assigns) == 0, (
        f"Agent added prototype mutation — AGENTS.md:162 says prefer "
        f"per-instance stubs over prototype mutation in tests.\n"
        f"Matches: {proto_assigns}"
    )
