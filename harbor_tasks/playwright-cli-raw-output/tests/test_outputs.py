"""
Task: playwright-cli-raw-output
Repo: playwright @ f6e14f9d73b46ab319b334c013094d867d4ef149
PR:   40010

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"

RESPONSE_TS = Path(REPO) / "packages/playwright-core/src/tools/backend/response.ts"
BACKEND_TS = Path(REPO) / "packages/playwright-core/src/tools/backend/browserBackend.ts"
EVALUATE_TS = Path(REPO) / "packages/playwright-core/src/tools/backend/evaluate.ts"
PROGRAM_TS = Path(REPO) / "packages/playwright-core/src/tools/cli-client/program.ts"
SESSION_TS = Path(REPO) / "packages/playwright-core/src/tools/cli-client/session.ts"
DAEMON_TS = Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/daemon.ts"
HELP_TS = Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/helpGenerator.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified TypeScript files must exist and contain valid content."""
    for ts_file in [RESPONSE_TS, BACKEND_TS, EVALUATE_TS, PROGRAM_TS,
                    SESSION_TS, DAEMON_TS, HELP_TS]:
        assert ts_file.is_file(), f"Missing: {ts_file}"
        content = ts_file.read_text()
        assert len(content) > 100, f"File too small: {ts_file}"
        assert "import" in content, f"No imports in {ts_file.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_response_raw_constructor_and_field():
    """Response constructor must accept an options object with a raw boolean field."""
    content = RESPONSE_TS.read_text()

    # Must have a private _raw boolean field declaration
    assert re.search(r'private\s+_raw\s*:\s*boolean', content), \
        "Response class must declare 'private _raw: boolean'"

    # Constructor must take options parameter with raw field (not positional relativeTo)
    assert re.search(r'constructor\s*\([^)]*options\s*\?\s*:', content), \
        "Constructor must accept an 'options?' parameter"
    assert re.search(r'raw\s*\?\s*:\s*boolean', content), \
        "Options type must include 'raw?: boolean'"

    # _raw must be assigned from options (with default false)
    assert re.search(r'this\._raw\s*=\s*options\?\.\s*raw\s*\?\?\s*false', content), \
        "_raw must default to false via 'options?.raw ?? false'"

    # relativeTo must also come from options (not positional)
    assert re.search(r'options\?\.\s*relativeTo', content), \
        "relativeTo must be read from options object"


# [pr_diff] fail_to_pass
def test_raw_mode_section_filtering():
    """Raw mode must filter serialized sections to only Error, Result, and Snapshot."""
    content = RESPONSE_TS.read_text()

    # serialize() must define the allowed raw sections
    for section_name in ["Error", "Result", "Snapshot"]:
        assert re.search(rf"['\"]{ section_name}['\"]", content), \
            f"'{section_name}' must appear in raw section allowlist"

    # Must have filtering logic using this._raw
    assert ".filter(" in content, "serialize must use .filter() for raw section filtering"
    assert "this._raw" in content, "Section filtering must reference this._raw"

    # The filtering must use .includes() to check section titles
    assert ".includes(" in content, "Raw filtering should use .includes() to match section titles"


# [pr_diff] fail_to_pass
def test_raw_mode_strips_markdown():
    """Raw mode must output plain content without markdown headers or code fences."""
    content = RESPONSE_TS.read_text()

    # Must have conditional: if (!this._raw) before markdown formatting
    assert "!this._raw" in content, \
        "Markdown formatting must be guarded by '!this._raw'"

    # In the else branch (raw=true), content should be pushed directly
    serialize_match = re.search(r'async\s+serialize\s*\(\)', content)
    assert serialize_match, "serialize() method must exist"

    # The else branch for raw mode must push section.content without headers
    raw_else = re.search(
        r'else\s*\{[^}]*section\.content',
        content,
        re.DOTALL
    )
    assert raw_else, "else branch for raw mode must push section.content directly"

    # The non-raw branch should have ### header formatting
    assert "### ${section.title}" in content, \
        "Non-raw branch must format sections with ### headers"


# [pr_diff] fail_to_pass
def test_raw_option_cli_pipeline():
    """--raw must be wired from CLI args through session to daemon to backend."""
    # 1. program.ts: GlobalOptions type must include raw
    program = PROGRAM_TS.read_text()
    assert re.search(r"raw\s*\?\s*:\s*boolean", program), \
        "GlobalOptions type must include 'raw?: boolean'"

    # 2. program.ts: raw in globalOptions and booleanOptions arrays
    global_opts = re.search(
        r"const\s+globalOptions\s*(?::\s*[^=]*)?\s*=\s*\[(.*?)\]",
        program, re.DOTALL,
    )
    assert global_opts, "globalOptions array must exist"
    assert "'raw'" in global_opts.group(1), "'raw' must be in globalOptions array"

    bool_opts = re.search(
        r"const\s+booleanOptions\s*(?::\s*[^=]*)?\s*=\s*\[(.*?)\]",
        program, re.DOTALL,
    )
    assert bool_opts, "booleanOptions array must exist"
    assert "'raw'" in bool_opts.group(1), "'raw' must be in booleanOptions array"

    # 3. program.ts: runInSession must extract raw from args
    assert re.search(r"args\.raw", program), \
        "runInSession must read raw from args"

    # 4. session.ts: run() must accept options with raw
    session = SESSION_TS.read_text()
    assert re.search(r"run\s*\([^)]*options\s*\?", session), \
        "Session.run() must accept options parameter"
    assert re.search(r"raw\s*:\s*options\?\.\s*raw", session), \
        "Session must forward raw to socket connection"

    # 5. daemon.ts: must set _meta with raw unconditionally
    daemon = DAEMON_TS.read_text()
    assert re.search(r"_meta\s*=\s*\{[^}]*raw\s*:", daemon), \
        "Daemon must include raw in _meta object"
    # Must NOT gate _meta assignment on params.cwd
    assert not re.search(r"if\s*\(\s*params\.cwd\s*\)\s*\n?\s*toolParams\._meta", daemon), \
        "Daemon must set _meta unconditionally (not gated on params.cwd)"

    # 6. browserBackend.ts: must read raw from _meta and pass to Response
    backend = BACKEND_TS.read_text()
    assert re.search(r"_meta\?\.\s*raw", backend), \
        "Backend must read raw from rawArguments._meta"
    assert re.search(r"new\s+Response\s*\([^)]*\{\s*relativeTo", backend), \
        "Backend must pass options object to Response constructor"


# [pr_diff] fail_to_pass
def test_evaluate_error_handling():
    """Evaluate tool must catch errors and report them via response.addError."""
    content = EVALUATE_TS.read_text()

    # Must have .catch() handler
    assert ".catch(" in content, "Evaluate must have .catch() error handler"

    # The catch handler must call response.addError
    assert "addError" in content, "Catch handler must call response.addError()"

    # Should extract message from Error instances
    assert re.search(r"e\s+instanceof\s+Error", content), \
        "Error handler must check instanceof Error for message extraction"

    # Should stringify non-Error values
    assert "String(e)" in content, \
        "Error handler must convert non-Error values to string"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — help text
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_help_includes_raw_option():
    """Help generator must document the --raw global option."""
    content = HELP_TS.read_text()
    assert "--raw" in content, "Help must document --raw option"
    assert re.search(r"--raw.*result.*value", content, re.IGNORECASE) or \
           re.search(r"--raw.*output.*result", content, re.IGNORECASE) or \
           re.search(r"--raw.*without.*status", content, re.IGNORECASE), \
        "Help text for --raw should describe its purpose"
