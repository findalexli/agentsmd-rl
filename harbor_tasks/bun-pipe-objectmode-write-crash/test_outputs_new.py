"""
Task: bun-pipe-objectmode-write-crash
Repo: oven-sh/bun @ 2d4c2beb23085873380840c9bd18eeca29645843
PR:   28432

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
import re
import os
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/src/js/internal/streams/readable.ts"


def _install_node():
    """Ensure Node.js is available (needed for behavioral tests)."""
    r = subprocess.run(["node", "--version"], capture_output=True)
    if r.returncode == 0:
        return
    subprocess.run(
        "curl -fsSL https://nodejs.org/dist/v20.11.0/node-v20.11.0-linux-x64.tar.xz "
        "| tar -xJ -C /usr/local --strip-components=1",
        shell=True, capture_output=True, timeout=120,
    )


def _install_bun():
    """Ensure Bun is available (needed for repo tests). Returns the bun bin path."""
    r = subprocess.run(["which", "bun"], capture_output=True)
    if r.returncode == 0:
        return "/root/.bun/bin"
    subprocess.run(
        "apt-get update -qq && apt-get install -y -qq unzip > /dev/null 2>&1",
        shell=True, capture_output=True, timeout=60,
    )
    subprocess.run(
        "curl -fsSL https://bun.sh/install | bash",
        shell=True, capture_output=True, timeout=120,
    )
    return "/root/.bun/bin"


def _extract_ondata_body() -> str:
    """Extract the ondata function body from the target file (pure Python)."""
    content = Path(TARGET).read_text()
    idx = content.find("function ondata")
    assert idx != -1, "function ondata not found in target file"
    brace = content.index("{", idx)
    depth, i = 1, brace + 1
    while depth > 0 and i < len(content):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
        i += 1
    return content[brace + 1 : i - 1]


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) - target file exists and has basic structure
# ---------------------------------------------------------------------------

def test_target_file_exists():
    """Target file exists and contains Readable.prototype.pipe."""
    content = Path(TARGET).read_text()
    assert "Readable.prototype.pipe" in content, "Readable.prototype.pipe not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# These tests verify error handling when dest.write() throws.
# They accept ANY valid error-notification mechanism (destroy OR emit).
# ---------------------------------------------------------------------------

def test_write_error_caught_and_forwarded():
    """dest.write() throwing must be caught; error must not escape uncaught."""
    _install_node()
    script = textwrap.dedent(r"""
        const fs = require('fs');

        const content = fs.readFileSync(process.argv[2], 'utf8');

        const ondataIdx = content.indexOf('function ondata');
        if (ondataIdx === -1) { console.error('No ondata function found'); process.exit(1); }
        const openBrace = content.indexOf('{', ondataIdx);
        if (openBrace === -1) process.exit(1);
        let depth = 1, i = openBrace + 1;
        while (depth > 0 && i < content.length) {
            if (content[i] === '{') depth++;
            else if (content[i] === '}') depth--;
            i++;
        }
        const funcSrc = content.substring(ondataIdx, i);
        const cleanFunc = funcSrc.replace(/\$debug\([^)]*\);?/g, '');

        let notifyMethod = null;
        let notifyErr = null;
        const dest = {
            write(chunk) { throw new TypeError('ERR_INVALID_ARG_TYPE: expected string or Buffer'); },
            destroy(err) { notifyMethod = 'destroy'; notifyErr = err; },
            emit(event, err) { if (event === 'error') { notifyMethod = 'emit'; notifyErr = err; } }
        };
        function pause() {}

        let errorEscaped = false;
        try {
            eval(cleanFunc);
            try { ondata({ hello: 'world' }); } catch(e) { errorEscaped = true; }
        } catch (e) {
            errorEscaped = true;
        }

        if (errorEscaped) {
            console.error('FAIL: error escaped uncaught');
            process.exit(1);
        }
        if (!notifyMethod) {
            console.error('FAIL: no error notification');
            process.exit(1);
        }
        console.log('PASS: error caught and ' + notifyMethod + ' called');
    """).strip()
    Path("/tmp/test_error_caught.js").write_text(script)
    r = subprocess.run(
        ["node", "/tmp/test_error_caught.js", TARGET],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Write error not caught/forwarded:\n{r.stderr}\n{r.stdout}"


def test_exact_error_object_propagated():
    """The exact error object thrown by write() must reach the notification handler."""
    _install_node()
    script = textwrap.dedent(r"""
        const fs = require('fs');

        const content = fs.readFileSync(process.argv[2], 'utf8');

        const ondataIdx = content.indexOf('function ondata');
        if (ondataIdx === -1) { console.error('No ondata function found'); process.exit(1); }
        const openBrace = content.indexOf('{', ondataIdx);
        if (openBrace === -1) process.exit(1);
        let depth = 1, i = openBrace + 1;
        while (depth > 0 && i < content.length) {
            if (content[i] === '{') depth++;
            else if (content[i] === '}') depth--;
            i++;
        }
        const funcSrc = content.substring(ondataIdx, i);
        const cleanFunc = funcSrc.replace(/\$debug\([^)]*\);?/g, '');

        const writeError = new TypeError('ERR_INVALID_ARG_TYPE');
        let notifyMethod = null;
        let notifyErr = null;

        const dest = {
            write(chunk) { throw writeError; },
            destroy(err) { notifyMethod = 'destroy'; notifyErr = err; },
            emit(event, err) { if (event === 'error') { notifyMethod = 'emit'; notifyErr = err; } }
        };
        function pause() {}

        let errorEscaped = false;
        try {
            eval(cleanFunc);
            try { ondata({ x: 1 }); } catch(e) { errorEscaped = true; }
        } catch (e) {
            errorEscaped = true;
        }

        if (errorEscaped) {
            console.error('FAIL: error escaped uncaught');
            process.exit(1);
        }
        if (!notifyMethod) {
            console.error('FAIL: no error notification');
            process.exit(1);
        }
        if (notifyErr !== writeError) {
            console.error('FAIL: error was replaced or not propagated');
            process.exit(1);
        }
        console.log('PASS: exact error object propagated via ' + notifyMethod);
    """).strip()
    Path("/tmp/test_error_propagated.js").write_text(script)
    r = subprocess.run(
        ["node", "/tmp/test_error_propagated.js", TARGET],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Error object not propagated:\n{r.stderr}\n{r.stdout}"


def test_different_error_types_caught():
    """RangeError from write() is also caught and forwarded (not just TypeError)."""
    _install_node()
    script = textwrap.dedent(r"""
        const fs = require('fs');

        const content = fs.readFileSync(process.argv[2], 'utf8');

        const ondataIdx = content.indexOf('function ondata');
        if (ondataIdx === -1) { console.error('No ondata function found'); process.exit(1); }
        const openBrace = content.indexOf('{', ondataIdx);
        if (openBrace === -1) process.exit(1);
        let depth = 1, i = openBrace + 1;
        while (depth > 0 && i < content.length) {
            if (content[i] === '{') depth++;
            else if (content[i] === '}') depth--;
            i++;
        }
        const funcSrc = content.substring(ondataIdx, i);
        const cleanFunc = funcSrc.replace(/\$debug\([^)]*\);?/g, '');

        const rangeError = new RangeError('source is too large');
        let notifyMethod = null;
        let notifyErr = null;

        const dest = {
            write(chunk) { throw rangeError; },
            destroy(err) { notifyMethod = 'destroy'; notifyErr = err; },
            emit(event, err) { if (event === 'error') { notifyMethod = 'emit'; notifyErr = err; } }
        };
        function pause() {}

        let errorEscaped = false;
        try {
            eval(cleanFunc);
            try { ondata(Buffer.from('test')); } catch(e) { errorEscaped = true; }
        } catch (e) {
            errorEscaped = true;
        }

        if (errorEscaped) {
            console.error('FAIL: RangeError escaped uncaught');
            process.exit(1);
        }
        if (!notifyMethod) {
            console.error('FAIL: no error notification');
            process.exit(1);
        }
        if (notifyErr !== rangeError) {
            console.error('FAIL: RangeError not forwarded');
            process.exit(1);
        }
        console.log('PASS: RangeError caught and forwarded via ' + notifyMethod);
    """).strip()
    Path("/tmp/test_range_error.js").write_text(script)
    r = subprocess.run(
        ["node", "/tmp/test_range_error.js", TARGET],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"RangeError not caught:\n{r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression tests
# ---------------------------------------------------------------------------

def test_normal_write_still_works():
    """Non-throwing dest.write() still passes data through without pause or destroy."""
    _install_node()
    script = textwrap.dedent(r"""
        const fs = require('fs');

        const content = fs.readFileSync(process.argv[2], 'utf8');

        const ondataIdx = content.indexOf('function ondata');
        if (ondataIdx === -1) { console.error('No ondata function found'); process.exit(1); }
        const openBrace = content.indexOf('{', ondataIdx);
        if (openBrace === -1) process.exit(1);
        let depth = 1, i = openBrace + 1;
        while (depth > 0 && i < content.length) {
            if (content[i] === '{') depth++;
            else if (content[i] === '}') depth--;
            i++;
        }
        const funcSrc = content.substring(ondataIdx, i);
        const cleanFunc = funcSrc.replace(/\$debug\([^)]*\);?/g, '');

        let written = null;
        let destroyed = false;
        let emitCalled = false;

        const dest = {
            write(chunk) { written = chunk; return true; },
            destroy(err) { destroyed = true; },
            emit(event, err) { if (event === 'error') emitCalled = true; }
        };
        let paused = false;
        function pause() { paused = true; }

        eval(cleanFunc);
        ondata(Buffer.from('hello'));

        if (written === null) { console.error('FAIL: write not called'); process.exit(1); }
        if (destroyed) { console.error('FAIL: dest destroyed on valid write'); process.exit(1); }
        if (emitCalled) { console.error('FAIL: emit(error) called on valid write'); process.exit(1); }
        if (paused) { console.error('FAIL: paused on true return'); process.exit(1); }
        console.log('PASS');
    """).strip()
    Path("/tmp/test_normal_write.js").write_text(script)
    r = subprocess.run(
        ["node", "/tmp/test_normal_write.js", TARGET],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Normal write broken:\n{r.stderr}\n{r.stdout}"


def test_backpressure_pause():
    """dest.write() returning false still triggers pause()."""
    _install_node()
    script = textwrap.dedent(r"""
        const fs = require('fs');

        const content = fs.readFileSync(process.argv[2], 'utf8');

        const ondataIdx = content.indexOf('function ondata');
        if (ondataIdx === -1) { console.error('No ondata function found'); process.exit(1); }
        const openBrace = content.indexOf('{', ondataIdx);
        if (openBrace === -1) process.exit(1);
        let depth = 1, i = openBrace + 1;
        while (depth > 0 && i < content.length) {
            if (content[i] === '{') depth++;
            else if (content[i] === '}') depth--;
            i++;
        }
        const funcSrc = content.substring(ondataIdx, i);
        const cleanFunc = funcSrc.replace(/\$debug\([^)]*\);?/g, '');

        let destroyed = false;
        let emitCalled = false;

        const dest = {
            write(chunk) { return false; },
            destroy(err) { destroyed = true; },
            emit(event, err) { if (event === 'error') emitCalled = true; }
        };
        let paused = false;
        function pause() { paused = true; }

        eval(cleanFunc);
        ondata(Buffer.from('data'));

        if (!paused) { console.error('FAIL: pause not called on false'); process.exit(1); }
        if (destroyed) { console.error('FAIL: dest destroyed on non-throwing write'); process.exit(1); }
        if (emitCalled) { console.error('FAIL: emit(error) called on non-throwing write'); process.exit(1); }
        console.log('PASS');
    """).strip()
    Path("/tmp/test_backpressure.js").write_text(script)
    r = subprocess.run(
        ["node", "/tmp/test_backpressure.js", TARGET],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Backpressure broken:\n{r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

def test_ondata_not_stub():
    """ondata function has real logic (>= 3 meaningful statements, references dest.write)."""
    body = _extract_ondata_body()
    meaningful = [
        l for l in body.split("\n")
        if l.strip()
        and not l.strip().startswith("//")
        and not l.strip().startswith("*")
        and "$debug" not in l
        and l.strip() not in ("{", "}")
    ]
    assert len(meaningful) >= 3, f"ondata too trivial ({len(meaningful)} lines)"
    assert any("write" in l for l in meaningful), "no write call in ondata"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) - src/js/CLAUDE.md @ 2d4c2beb
# ---------------------------------------------------------------------------

def test_no_bare_call_apply_in_ondata():
    """Agent code in ondata must use .$call/.$apply, not .call/.apply (src/js/CLAUDE.md)."""
    body = _extract_ondata_body()
    lines = [l for l in body.split("\n") if not l.strip().startswith("//")]
    clean = "\n".join(lines)
    bare_call = re.search(r'(?<!$)\.call\(', clean)
    bare_apply = re.search(r'(?<!$)\.apply\(', clean)
    assert not bare_call, f"Found bare .call() in ondata (use .$call): {bare_call.group()}"
    assert not bare_apply, f"Found bare .apply() in ondata (use .$apply): {bare_apply.group()}"


def test_no_console_log_in_ondata():
    """Debug logging must use $debug(), not console.log (src/js/CLAUDE.md)."""
    body = _extract_ondata_body()
    lines = [l for l in body.split("\n") if not l.strip().startswith("//")]
    clean = "\n".join(lines)
    assert "console.log" not in clean, "Found console.log in ondata - use $debug() instead"
    assert "console.warn" not in clean, "Found console.warn in ondata - use $debug() instead"
    assert "console.error" not in clean, "Found console.error in ondata - use $debug() instead"


# ---------------------------------------------------------------------------
# Repo CI checks (pass_to_pass)
# ---------------------------------------------------------------------------

def test_repo_bun_stream_tests():
    """Repo's Bun stream tests pass (pass_to_pass). Tests the modified readable.ts module."""
    bun_bin = _install_bun()
    env = {**os.environ, "PATH": f"{bun_bin}:{os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["bun", "test", "test/js/node/stream/node-stream.test.js"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Bun stream tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_target_file_syntax_valid():
    """Target file has valid JavaScript/TypeScript syntax (pass_to_pass)."""
    _install_node()
    script = textwrap.dedent(r"""
        const fs = require('fs');
        const vm = require('vm');
        const content = fs.readFileSync(process.argv[2], 'utf8');
        const ondataIdx = content.indexOf('function ondata');
        if (ondataIdx === -1) { console.error('No ondata function found'); process.exit(1); }
        const openBrace = content.indexOf('{', ondataIdx);
        if (openBrace === -1) { console.error('No opening brace found'); process.exit(1); }
        let depth = 1, i = openBrace + 1;
        while (depth > 0 && i < content.length) {
            if (content[i] === '{') depth++;
            else if (content[i] === '}') depth--;
            i++;
        }
        const funcSrc = content.substring(ondataIdx, i);
        const cleanFunc = funcSrc.replace(/\$debug\([^)]*\);?/g, '');
        try {
            new vm.Script(cleanFunc);
            console.log('Syntax valid');
        } catch (e) {
            console.error('Syntax error:', e.message);
            process.exit(1);
        }
    """).strip()
    Path("/tmp/syntax_check.js").write_text(script)
    r = subprocess.run(
        ["node", "/tmp/syntax_check.js", TARGET],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax validation failed:\n{r.stderr}"


def test_claude_md_conventions():
    """Target file follows src/js/CLAUDE.md conventions (pass_to_pass)."""
    content = Path(TARGET).read_text()
    assert "console.log" not in content, "Found console.log in file - use $debug() per CLAUDE.md"
    assert "Readable.prototype.pipe" in content, "Readable.prototype.pipe not found"
    assert "function ondata" in content, "function ondata not found"


def test_repo_prettier_target():
    """Target file passes prettier format check (pass_to_pass)."""
    _install_node()
    r = subprocess.run(
        ["npx", "-y", "prettier@latest", "--config", f"{REPO}/.prettierrc",
         "--check", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_oxlint_target():
    """Target file passes oxlint (pass_to_pass)."""
    _install_node()
    r = subprocess.run(
        ["npx", "-y", "oxlint@0.15.0", f"--config={REPO}/oxlint.json", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Oxlint check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_oxlint_streams_dir():
    """Streams directory passes oxlint (pass_to_pass)."""
    _install_node()
    r = subprocess.run(
        ["npx", "-y", "oxlint@0.15.0", f"--config={REPO}/oxlint.json", f"{REPO}/src/js/internal/streams/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Oxlint check failed:\n{r.stdout}\n{r.stderr}"
