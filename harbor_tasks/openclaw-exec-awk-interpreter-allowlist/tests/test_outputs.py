"""
Task: openclaw-exec-awk-interpreter-allowlist
Repo: openclaw/openclaw @ b7b46ad185392f53a995124f6861d2b356f84976
PR:   57772

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/openclaw"


def _eval_ts(code: str, timeout: int = 30) -> object:
    """Write a .mts script, run it with tsx, return parsed JSON from stdout."""
    script = Path(REPO) / "__test_probe.mts"
    script.write_text(code)
    try:
        r = subprocess.run(
            ["npx", "tsx", str(script)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        assert r.returncode == 0, (
            f"tsx failed (exit {r.returncode}):\n{r.stderr}\n{r.stdout}"
        )
        return json.loads(r.stdout.strip())
    finally:
        script.unlink(missing_ok=True)


def _check_allowlist(pattern: str) -> bool:
    """Check if a pattern is interpreter-like."""
    return _eval_ts(textwrap.dedent(f"""\
        import {{ isInterpreterLikeAllowlistPattern }} from "./src/infra/exec-inline-eval.js";
        console.log(JSON.stringify(isInterpreterLikeAllowlistPattern({json.dumps(pattern)})));
    """))


def _detect_inline(argv: list[str]) -> dict | None:
    """Detect interpreter inline eval for an argv."""
    return _eval_ts(textwrap.dedent(f"""\
        import {{ detectInterpreterInlineEvalArgv }} from "./src/infra/exec-inline-eval.js";
        console.log(JSON.stringify(detectInterpreterInlineEvalArgv({json.dumps(argv)})));
    """))


def _describe_hit(hit: dict) -> str:
    """Get description of an inline eval hit."""
    return _eval_ts(textwrap.dedent(f"""\
        import {{ describeInterpreterInlineEval }} from "./src/infra/exec-inline-eval.js";
        console.log(JSON.stringify(describeInterpreterInlineEval({json.dumps(hit)})));
    """))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core awk allowlist recognition
# ---------------------------------------------------------------------------

def test_allowlist_recognizes_awk():
    """isInterpreterLikeAllowlistPattern recognizes awk paths as interpreter-like."""
    assert _check_allowlist("/usr/bin/awk") is True
    assert _check_allowlist("/usr/local/bin/awk") is True
    assert _check_allowlist("awk") is True


def test_allowlist_recognizes_awk_variants():
    """isInterpreterLikeAllowlistPattern recognizes gawk, mawk, nawk."""
    assert _check_allowlist("**/gawk") is True
    assert _check_allowlist("/usr/bin/mawk") is True
    assert _check_allowlist("nawk") is True


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- inline eval detection
# ---------------------------------------------------------------------------

def test_detect_awk_inline_positional():
    """detectInterpreterInlineEvalArgv detects awk positional inline program."""
    hit = _detect_inline(["awk", "{print $1}", "data.csv"])
    assert hit is not None, "awk positional program should be detected"
    assert hit.get("flag") == "<program>", f"expected flag '<program>', got {hit.get('flag')}"

    hit2 = _detect_inline(["mawk", "BEGIN { print 1 }"])
    assert hit2 is not None, "mawk positional program should be detected"

    hit3 = _detect_inline(["nawk", '{gsub(/old/,\"new\"); print}', "file.txt"])
    assert hit3 is not None, "nawk positional program should be detected"


def test_detect_awk_with_value_flags():
    """detectInterpreterInlineEvalArgv detects awk program after -F/-v flags."""
    hit = _detect_inline(["gawk", "-F", ",", "{print $1}", "data.csv"])
    assert hit is not None, "gawk with -F should still detect inline program"

    hit2 = _detect_inline(["awk", "-v", "x=1", "{print x, $0}", "input.txt"])
    assert hit2 is not None, "awk with -v should still detect inline program"

    hit3 = _detect_inline(["awk", "-F", ":", "-v", "n=3", "{print $n}", "/etc/passwd"])
    assert hit3 is not None, "awk with multiple value flags should still detect inline"


def test_awk_detection_description():
    """describeInterpreterInlineEval returns '<variant> inline program' format."""
    for variant in ["awk", "gawk", "mawk"]:
        hit = _detect_inline([variant, "{print $1}"])
        assert hit is not None, f"{variant} inline detection must return a hit"
        desc = _describe_hit(hit)
        assert variant in desc, f"description must mention '{variant}', got: {desc}"
        assert "inline program" in desc, f"description must say 'inline program', got: {desc}"


def test_awk_double_dash_positional():
    """awk -- '{program}' detects inline code after double-dash separator."""
    hit = _detect_inline(["awk", "--", "{print $1}", "data.csv"])
    assert hit is not None, "awk with -- separator should still detect inline program"
    assert hit.get("flag") == "<program>", f"expected flag '<program>', got {hit.get('flag')}"

    hit2 = _detect_inline(["gawk", "--", "BEGIN { print 42 }"])
    assert hit2 is not None, "gawk with -- should detect inline program"

    hit3 = _detect_inline(["awk", "--"])
    assert hit3 is None, "awk -- with no following arg should return null"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- integration wiring
# ---------------------------------------------------------------------------

def test_allowlist_imports_interpreter_check():
    """exec-approvals-allowlist.ts must call isInterpreterLikeAllowlistPattern."""
    src = Path(f"{REPO}/src/infra/exec-approvals-allowlist.ts").read_text()
    assert "isInterpreterLikeAllowlistPattern" in src, (
        "allowlist module must import and use isInterpreterLikeAllowlistPattern"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- existing behavior preserved
# ---------------------------------------------------------------------------

def test_existing_interpreters_still_detected():
    """python3, node, perl, ruby are still recognized as interpreter-like."""
    assert _check_allowlist("/usr/bin/python3") is True
    assert _check_allowlist("**/node") is True
    assert _check_allowlist("/usr/bin/perl") is True

    hit = _detect_inline(["python3", "-c", "print(1)"])
    assert hit is not None, "python3 -c should still be detected"

    hit2 = _detect_inline(["node", "-e", "console.log(1)"])
    assert hit2 is not None, "node -e should still be detected"

    hit3 = _detect_inline(["perl", "-e", "print 1"])
    assert hit3 is not None, "perl -e should still be detected"


def test_awk_file_flag_not_inline():
    """awk -f script.awk is file-based, not inline eval."""
    hit = _detect_inline(["awk", "-f", "script.awk", "data.csv"])
    assert hit is None, "awk -f should NOT be detected as inline eval"

    hit2 = _detect_inline(["gawk", "--file", "prog.awk", "input.txt"])
    assert hit2 is None, "gawk --file should NOT be detected as inline eval"

    hit3 = _detect_inline(["mawk", "-f", "transform.awk"])
    assert hit3 is None, "mawk -f should NOT be detected as inline eval"


def test_non_interpreters_not_flagged():
    """Non-interpreter programs must not be detected as interpreter-like."""
    for prog in ["/usr/bin/ls", "/usr/bin/cat", "/usr/bin/rg", "/usr/bin/grep"]:
        assert _check_allowlist(prog) is False, f"{prog} should not be interpreter-like"

    for argv in [
        ["ls", "-la", "/tmp"],
        ["cat", "file.txt"],
        ["grep", "-r", "pattern", "."],
    ]:
        hit = _detect_inline(argv)
        assert hit is None, f"{argv[0]} should not be detected as inline eval"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) -- rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------

def test_no_ts_nocheck():
    """No @ts-nocheck in modified files (CLAUDE.md:146)."""
    for fname in ["exec-inline-eval.ts", "exec-approvals-allowlist.ts"]:
        src = Path(f"{REPO}/src/infra/{fname}").read_text()
        assert "@ts-nocheck" not in src, f"@ts-nocheck found in {fname}"


def test_no_any_type_annotations():
    """No 'any' type annotations in modified files (CLAUDE.md:144)."""
    import re
    pattern = re.compile(r":\s*any\b|<any>|as\s+any\b")
    for fname in ["exec-inline-eval.ts", "exec-approvals-allowlist.ts"]:
        src = Path(f"{REPO}/src/infra/{fname}").read_text()
        assert not pattern.search(src), f"'any' type found in {fname}"


def test_no_ts_ignore():
    """No @ts-ignore in modified files; use @ts-expect-error with justification (CLAUDE.md:146)."""
    for fname in ["exec-inline-eval.ts", "exec-approvals-allowlist.ts"]:
        src = Path(f"{REPO}/src/infra/{fname}").read_text()
        assert "@ts-ignore" not in src, (
            f"@ts-ignore found in {fname} — use @ts-expect-error with justification"
        )


def test_no_prototype_mutation():
    """No prototype mutation patterns in modified files (CLAUDE.md:160)."""
    import re
    pattern = re.compile(r"\.prototype\s*[.=\[]")
    for fname in ["exec-inline-eval.ts", "exec-approvals-allowlist.ts"]:
        src = Path(f"{REPO}/src/infra/{fname}").read_text()
        assert not pattern.search(src), f"prototype mutation found in {fname}"


def test_no_inline_lint_suppressions():
    """No inline lint suppressions (eslint-disable / oxlint-disable) in modified files (CLAUDE.md:146)."""
    import re
    pattern = re.compile(r"//\s*(eslint-disable|oxlint-disable)")
    for fname in ["exec-inline-eval.ts", "exec-approvals-allowlist.ts"]:
        src = Path(f"{REPO}/src/infra/{fname}").read_text()
        assert not pattern.search(src), (
            f"inline lint suppression found in {fname} — fix the root cause instead"
        )


def test_no_dynamic_import_mixed_with_static():
    """No dynamic import of exec-inline-eval mixed with its static import (CLAUDE.md:155)."""
    import re
    src = Path(f"{REPO}/src/infra/exec-approvals-allowlist.ts").read_text()
    # The file must use a static import (already required by allowlist_imports_interpreter_check)
    assert "from \"./exec-inline-eval.js\"" in src or "from './exec-inline-eval.js'" in src, (
        "exec-approvals-allowlist.ts must statically import exec-inline-eval.js"
    )
    # Must not also dynamically import the same module
    dynamic = re.compile(r"""await\s+import\s*\(\s*['"]\.\/exec-inline-eval""")
    assert not dynamic.search(src), (
        "exec-approvals-allowlist.ts must not mix await import() with static import of exec-inline-eval"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- repo CI/CD checks
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo's oxlint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", "--type-aware"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_unit_tests_infra_exec():
    """Repo's exec-related infra unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "--config", "vitest.unit.config.ts", "src/infra/exec-inline-eval.test.ts", "src/infra/exec-approvals-allow-always.test.ts", "src/infra/exec-approvals.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Infra exec unit tests failed:\n{r.stderr[-500:]}"


def test_repo_unit_tests_security_audit():
    """Repo's security audit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "--config", "vitest.unit.config.ts", "src/security/audit.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Security audit tests failed:\n{r.stderr[-500:]}"
