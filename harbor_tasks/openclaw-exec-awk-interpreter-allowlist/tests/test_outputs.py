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

    hit3 = _detect_inline(["nawk", '{gsub(/old/,\\"new\\"); print}', "file.txt"])
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


def test_repo_no_conflict_markers():
    """Repo has no git conflict markers (pass_to_pass)."""
    r = subprocess.run(
        ["node", "scripts/check-no-conflict-markers.mjs"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Conflict markers check failed:\n{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_bun_artifacts_build_a2ui_bundle():
    """pass_to_pass | CI job 'build-bun-artifacts' → step 'Build A2UI bundle'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm canvas:a2ui:bundle'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build A2UI bundle' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_additional_check_types_and_lint_and_oxfmt():
    """pass_to_pass | CI job 'check-additional' → step 'Check types and lint and oxfmt'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check types and lint and oxfmt' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_additional_strict_ts_build_smoke():
    """pass_to_pass | CI job 'check-additional' → step 'Strict TS build smoke'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build:strict-smoke'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Strict TS build smoke' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_run_matrix_task_matrix_runtime():
    """pass_to_pass | CI job 'check' → step 'Run ${{ matrix.task }} (${{ matrix.runtime }})'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test:extensions && pnpm build && pnpm test:contracts && pnpm protocol:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run ${{ matrix.task }} (${{ matrix.runtime }})' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_artifacts_build_dist():
    """pass_to_pass | CI job 'build-artifacts' → step 'Build dist'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build dist' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_artifacts_build_control_ui():
    """pass_to_pass | CI job 'build-artifacts' → step 'Build Control UI'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm ui:build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Control UI' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_smoke_smoke_test_cli_launcher_help():
    """pass_to_pass | CI job 'build-smoke' → step 'Smoke test CLI launcher help'"""
    r = subprocess.run(
        ["bash", "-lc", 'node openclaw.mjs --help'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Smoke test CLI launcher help' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_smoke_smoke_test_cli_launcher_status_json():
    """pass_to_pass | CI job 'build-smoke' → step 'Smoke test CLI launcher status json'"""
    r = subprocess.run(
        ["bash", "-lc", 'node openclaw.mjs status --json --timeout 1'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Smoke test CLI launcher status json' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_smoke_smoke_test_built_bundled_plugin_singleto():
    """pass_to_pass | CI job 'build-smoke' → step 'Smoke test built bundled plugin singleton'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test:build:singleton'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Smoke test built bundled plugin singleton' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_smoke_check_cli_startup_memory():
    """pass_to_pass | CI job 'build-smoke' → step 'Check CLI startup memory'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test:startup:memory'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check CLI startup memory' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_does_not_persist_interpreter_like_executables_fo():
    """fail_to_pass | PR added test 'does not persist interpreter-like executables for allow-always' in 'src/infra/exec-approvals-allow-always.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/infra/exec-approvals-allow-always.test.ts" -t "does not persist interpreter-like executables for allow-always" 2>&1 || npx vitest run "src/infra/exec-approvals-allow-always.test.ts" -t "does not persist interpreter-like executables for allow-always" 2>&1 || pnpm jest "src/infra/exec-approvals-allow-always.test.ts" -t "does not persist interpreter-like executables for allow-always" 2>&1 || npx jest "src/infra/exec-approvals-allow-always.test.ts" -t "does not persist interpreter-like executables for allow-always" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'does not persist interpreter-like executables for allow-always' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_prevents_allow_always_bypass_for_awk_interpreter():
    """fail_to_pass | PR added test 'prevents allow-always bypass for awk interpreters' in 'src/infra/exec-approvals-allow-always.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/infra/exec-approvals-allow-always.test.ts" -t "prevents allow-always bypass for awk interpreters" 2>&1 || npx vitest run "src/infra/exec-approvals-allow-always.test.ts" -t "prevents allow-always bypass for awk interpreters" 2>&1 || pnpm jest "src/infra/exec-approvals-allow-always.test.ts" -t "prevents allow-always bypass for awk interpreters" 2>&1 || npx jest "src/infra/exec-approvals-allow-always.test.ts" -t "prevents allow-always bypass for awk interpreters" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'prevents allow-always bypass for awk interpreters' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_prevents_allow_always_bypass_for_shell_carried_a():
    """fail_to_pass | PR added test 'prevents allow-always bypass for shell-carried awk interpreters' in 'src/infra/exec-approvals-allow-always.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/infra/exec-approvals-allow-always.test.ts" -t "prevents allow-always bypass for shell-carried awk interpreters" 2>&1 || npx vitest run "src/infra/exec-approvals-allow-always.test.ts" -t "prevents allow-always bypass for shell-carried awk interpreters" 2>&1 || pnpm jest "src/infra/exec-approvals-allow-always.test.ts" -t "prevents allow-always bypass for shell-carried awk interpreters" 2>&1 || npx jest "src/infra/exec-approvals-allow-always.test.ts" -t "prevents allow-always bypass for shell-carried awk interpreters" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'prevents allow-always bypass for shell-carried awk interpreters' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_ignores_normal_script_execution():
    """fail_to_pass | PR added test 'ignores normal script execution' in 'src/infra/exec-inline-eval.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/infra/exec-inline-eval.test.ts" -t "ignores normal script execution" 2>&1 || npx vitest run "src/infra/exec-inline-eval.test.ts" -t "ignores normal script execution" 2>&1 || pnpm jest "src/infra/exec-inline-eval.test.ts" -t "ignores normal script execution" 2>&1 || npx jest "src/infra/exec-inline-eval.test.ts" -t "ignores normal script execution" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'ignores normal script execution' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_matches_interpreter_like_allowlist_patterns():
    """fail_to_pass | PR added test 'matches interpreter-like allowlist patterns' in 'src/infra/exec-inline-eval.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "src/infra/exec-inline-eval.test.ts" -t "matches interpreter-like allowlist patterns" 2>&1 || npx vitest run "src/infra/exec-inline-eval.test.ts" -t "matches interpreter-like allowlist patterns" 2>&1 || pnpm jest "src/infra/exec-inline-eval.test.ts" -t "matches interpreter-like allowlist patterns" 2>&1 || npx jest "src/infra/exec-inline-eval.test.ts" -t "matches interpreter-like allowlist patterns" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'matches interpreter-like allowlist patterns' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
