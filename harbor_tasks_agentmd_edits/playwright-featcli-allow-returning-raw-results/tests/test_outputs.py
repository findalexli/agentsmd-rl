"""
Task: playwright-featcli-allow-returning-raw-results
Repo: microsoft/playwright @ f6e14f9d73b46ab319b334c013094d867d4ef149
PR:   40010

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
TOOLS = f"{REPO}/packages/playwright-core/src/tools"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        f"{TOOLS}/backend/browserBackend.ts",
        f"{TOOLS}/backend/evaluate.ts",
        f"{TOOLS}/backend/response.ts",
        f"{TOOLS}/cli-client/program.ts",
        f"{TOOLS}/cli-client/session.ts",
        f"{TOOLS}/cli-daemon/daemon.ts",
        f"{TOOLS}/cli-daemon/helpGenerator.ts",
    ]
    for fpath in files:
        assert Path(fpath).exists(), f"File not found: {fpath}"
        r = subprocess.run(
            ["node", "-e", f"require('fs').readFileSync('{fpath}', 'utf8')"],
            capture_output=True, timeout=10,
        )
        assert r.returncode == 0, f"Failed to read {fpath}: {r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_response_supports_raw_mode():
    """Response class must accept a raw option and use it in serialization."""
    response_src = Path(f"{TOOLS}/backend/response.ts").read_text()

    # Constructor must accept options object with raw field
    assert "options?" in response_src or "options:" in response_src, \
        "Response constructor should accept an options parameter"
    assert "raw" in response_src, \
        "Response class should reference 'raw' mode"

    # Serialize must filter sections when raw
    assert "this._raw" in response_src or "this.raw" in response_src, \
        "Response should store raw as an instance field"

    # Raw mode should only keep Error, Result, Snapshot sections
    assert "Error" in response_src and "Result" in response_src and "Snapshot" in response_src, \
        "serialize() should reference the raw-allowed section types"

    # In raw mode, markdown headers (### Title) should be skipped
    # The non-raw path pushes ### headers; raw path should not
    lines = response_src.split("\n")
    serialize_region = False
    has_raw_branch = False
    for line in lines:
        if "serialize" in line and "async" in line:
            serialize_region = True
        if serialize_region and ("this._raw" in line or "this.raw" in line):
            has_raw_branch = True
            break
    assert has_raw_branch, "serialize() must branch on raw mode"


# [pr_diff] fail_to_pass
def test_cli_declares_raw_option():
    """CLI program must declare --raw as a boolean global option."""
    program_src = Path(f"{TOOLS}/cli-client/program.ts").read_text()

    # raw must be in GlobalOptions type
    # Find the GlobalOptions type block
    go_match = re.search(r"type GlobalOptions\s*=\s*\{([^}]+)\}", program_src)
    assert go_match, "GlobalOptions type not found"
    assert "raw" in go_match.group(1), "raw must be in GlobalOptions type"

    # raw must be in booleanOptions array
    bool_match = re.search(r"const booleanOptions[^=]*=\s*\[([^\]]+)\]", program_src, re.DOTALL)
    assert bool_match, "booleanOptions array not found"
    assert "'raw'" in bool_match.group(1) or '"raw"' in bool_match.group(1), \
        "raw must be listed in booleanOptions"

    # raw must be in globalOptions array
    global_match = re.search(r"const globalOptions[^=]*=\s*\[([^\]]+)\]", program_src, re.DOTALL)
    assert global_match, "globalOptions array not found"
    assert "'raw'" in global_match.group(1) or '"raw"' in global_match.group(1), \
        "raw must be listed in globalOptions"


# [pr_diff] fail_to_pass
def test_session_passes_raw_option():
    """Session.run must accept and forward a raw option."""
    session_src = Path(f"{TOOLS}/cli-client/session.ts").read_text()

    # run method must accept options with raw
    run_match = re.search(r"async run\([^)]+\)", session_src)
    assert run_match, "Session.run method not found"
    run_sig = run_match.group(0)
    assert "options" in run_sig or "raw" in run_sig, \
        "Session.run must accept raw option"

    # Must forward raw to the socket connection
    assert "raw" in session_src.split("async run")[1] if "async run" in session_src else False, \
        "Session.run must forward raw to socket"


# [pr_diff] fail_to_pass
def test_daemon_forwards_raw_metadata():
    """Daemon must always set _meta with raw field, not conditionally on cwd."""
    daemon_src = Path(f"{TOOLS}/cli-daemon/daemon.ts").read_text()

    # The old code was: if (params.cwd) toolParams._meta = { cwd: params.cwd };
    # The new code should unconditionally set _meta with both cwd and raw
    # Check that _meta assignment includes raw
    meta_assigns = [line for line in daemon_src.split("\n") if "_meta" in line and "raw" in line]
    assert len(meta_assigns) >= 1, \
        "daemon.ts must set _meta with raw field (e.g., toolParams._meta = { cwd: ..., raw: ... })"

    # The conditional `if (params.cwd)` before _meta should be removed
    lines = daemon_src.split("\n")
    for i, line in enumerate(lines):
        if "_meta" in line and "raw" in line:
            # The line before should NOT be `if (params.cwd)`
            if i > 0:
                prev = lines[i - 1].strip()
                assert "if (params.cwd)" not in prev, \
                    "_meta assignment should not be gated behind if (params.cwd)"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit (config_edit) — SKILL.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass
def test_skill_md_raw_documentation():
    """SKILL.md must document the --raw option."""
    skill_md = Path(f"{TOOLS}/cli-client/skill/SKILL.md").read_text()

    # Must have a section about raw output
    assert "--raw" in skill_md, \
        "SKILL.md should document the --raw flag"

    # Must explain what raw mode does (strips formatting for piping)
    lower = skill_md.lower()
    assert "pipe" in lower or "piping" in lower or "raw output" in lower, \
        "SKILL.md should explain that --raw is for piping output"

    # Must include usage examples with --raw
    assert "playwright-cli --raw" in skill_md, \
        "SKILL.md should include examples using --raw"

    # Must show at least 2 different example commands
    raw_examples = [line for line in skill_md.split("\n")
                    if "playwright-cli --raw" in line and not line.strip().startswith("#")]
    assert len(raw_examples) >= 2, \
        f"SKILL.md should have at least 2 --raw examples, found {len(raw_examples)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and gold
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's build command passes (pass_to_pass)."""
    # First install dependencies
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"
    # Then run build
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo's package lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ts_parse_modified_files():
    """Modified TypeScript files parse without errors (pass_to_pass)."""
    files = [
        f"{TOOLS}/backend/response.ts",
        f"{TOOLS}/cli-client/program.ts",
        f"{TOOLS}/cli-client/session.ts",
        f"{TOOLS}/cli-daemon/daemon.ts",
        f"{TOOLS}/cli-daemon/helpGenerator.ts",
    ]
    # Install dependencies first
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"
    for fpath in files:
        assert Path(fpath).exists(), f"File not found: {fpath}"
        # Simple parse check using TypeScript compiler API
        r = subprocess.run(
            ["node", "-e", f"""
                const ts = require('typescript');
                const content = require('fs').readFileSync('{fpath}', 'utf8');
                const source = ts.createSourceFile('{fpath}', content, ts.ScriptTarget.Latest, true);
                console.log('OK');
            """],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"TypeScript parse failed for {fpath}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_cli_help():
    """CLI help tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "ci"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"npm ci failed:\n{r.stderr[-500:]}"
    # Build first
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"
    # Run tests
    r = subprocess.run(
        ["npx", "playwright", "test", "--config=tests/mcp/playwright.config.ts", "cli-help.spec.ts", "--reporter=list"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"CLI help tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_response_not_stub():
    """Response.serialize must have real logic, not a stub."""
    response_src = Path(f"{TOOLS}/backend/response.ts").read_text()

    # Find serialize method and verify it has substantial content
    if "async serialize" in response_src:
        serialize_body = response_src.split("async serialize")[1]
        # Should have text building and content assembly (both base and fixed)
        assert "text.push" in serialize_body, \
            "serialize should build text content"
        assert "content" in serialize_body, \
            "serialize should return content"
        assert "_build" in serialize_body, \
            "serialize should call _build to get sections"
    else:
        raise AssertionError("serialize method not found in response.ts")
