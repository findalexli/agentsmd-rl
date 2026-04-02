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
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/src/js/internal/streams/readable.ts"

# ---------------------------------------------------------------------------
# Helper: JS that extracts `function ondata` body (strips $debug lines)
# ---------------------------------------------------------------------------
EXTRACT_ONDATA_JS = textwrap.dedent(r"""
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
    let funcSrc = content.substring(ondataIdx, i);
    funcSrc = funcSrc.split('\n').filter(l => !l.includes('$debug')).join('\n');
    process.stdout.write(funcSrc);
""").strip()


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


def _run_node_test(script: str) -> subprocess.CompletedProcess:
    """Write a Node.js test script to /tmp, run it against TARGET."""
    _install_node()
    Path("/tmp/extract_ondata.js").write_text(EXTRACT_ONDATA_JS)
    Path("/tmp/test_script.js").write_text(script)
    return subprocess.run(
        ["node", "/tmp/test_script.js", TARGET],
        capture_output=True, text=True, timeout=30,
    )


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
# Gate (pass_to_pass, static) — target file exists and has basic structure
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_target_file_exists():
    """Target file exists and contains Readable.prototype.pipe."""
    content = Path(TARGET).read_text()
    assert "Readable.prototype.pipe" in content, "Readable.prototype.pipe not found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_write_error_caught_and_forwarded():
    """dest.write() throwing TypeError must be caught; error forwarded via dest.destroy()."""
    r = _run_node_test(textwrap.dedent(r"""
        const { execFileSync } = require('child_process');
        const funcSrc = execFileSync('node', ['/tmp/extract_ondata.js', process.argv[2]], { encoding: 'utf8' });

        let destroyed = false;
        const dest = {
            write(chunk) { throw new TypeError('ERR_INVALID_ARG_TYPE: expected string or Buffer'); },
            destroy(err) { destroyed = true; },
            emit() {}
        };
        let paused = false;
        function pause() { paused = true; }

        eval(funcSrc);

        let threwUncaught = false;
        try { ondata({ hello: 'world' }); } catch(e) { threwUncaught = true; }

        if (threwUncaught) { console.error('write error escaped ondata'); process.exit(1); }
        if (!destroyed) { console.error('dest.destroy not called'); process.exit(1); }
    """))
    assert r.returncode == 0, f"Write error not caught/forwarded:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_exact_error_object_propagated():
    """The exact error object thrown by write() must be passed to dest.destroy()."""
    r = _run_node_test(textwrap.dedent(r"""
        const { execFileSync } = require('child_process');
        const funcSrc = execFileSync('node', ['/tmp/extract_ondata.js', process.argv[2]], { encoding: 'utf8' });

        const writeError = new TypeError('ERR_INVALID_ARG_TYPE');
        let destroyErr = null;

        const dest = {
            write(chunk) { throw writeError; },
            destroy(err) { destroyErr = err; },
            emit() {}
        };
        function pause() {}

        eval(funcSrc);
        try { ondata({ x: 1 }); } catch(e) { process.exit(1); }

        if (destroyErr !== writeError) {
            console.error('error was swallowed or replaced');
            process.exit(1);
        }
    """))
    assert r.returncode == 0, f"Error object not propagated:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_different_error_types_caught():
    """RangeError from write() is also caught (not just TypeError)."""
    r = _run_node_test(textwrap.dedent(r"""
        const { execFileSync } = require('child_process');
        const funcSrc = execFileSync('node', ['/tmp/extract_ondata.js', process.argv[2]], { encoding: 'utf8' });

        const rangeError = new RangeError('source is too large');
        let destroyErr = null;

        const dest = {
            write(chunk) { throw rangeError; },
            destroy(err) { destroyErr = err; },
            emit() {}
        };
        function pause() {}

        eval(funcSrc);
        let threw = false;
        try { ondata(Buffer.from('test')); } catch(e) { threw = true; }

        if (threw) { console.error('RangeError escaped'); process.exit(1); }
        if (destroyErr !== rangeError) { console.error('RangeError not forwarded'); process.exit(1); }
    """))
    assert r.returncode == 0, f"RangeError not caught:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_normal_write_still_works():
    """Non-throwing dest.write() still passes data through without pause or destroy."""
    r = _run_node_test(textwrap.dedent(r"""
        const { execFileSync } = require('child_process');
        const funcSrc = execFileSync('node', ['/tmp/extract_ondata.js', process.argv[2]], { encoding: 'utf8' });

        let written = null;
        let destroyed = false;
        const dest = {
            write(chunk) { written = chunk; return true; },
            destroy(err) { destroyed = true; },
            emit() {}
        };
        let paused = false;
        function pause() { paused = true; }

        eval(funcSrc);
        ondata(Buffer.from('hello'));

        if (written === null) { console.error('write not called'); process.exit(1); }
        if (destroyed) { console.error('dest destroyed on valid write'); process.exit(1); }
        if (paused) { console.error('paused on true return'); process.exit(1); }
    """))
    assert r.returncode == 0, f"Normal write broken:\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_backpressure_pause():
    """dest.write() returning false still triggers pause()."""
    r = _run_node_test(textwrap.dedent(r"""
        const { execFileSync } = require('child_process');
        const funcSrc = execFileSync('node', ['/tmp/extract_ondata.js', process.argv[2]], { encoding: 'utf8' });

        let destroyed = false;
        const dest = {
            write(chunk) { return false; },
            destroy(err) { destroyed = true; },
            emit() {}
        };
        let paused = false;
        function pause() { paused = true; }

        eval(funcSrc);
        ondata(Buffer.from('data'));

        if (!paused) { console.error('pause not called on false'); process.exit(1); }
        if (destroyed) { console.error('dest destroyed on non-throwing write'); process.exit(1); }
    """))
    assert r.returncode == 0, f"Backpressure broken:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ondata_not_stub():
    """ondata function has real logic (>= 4 meaningful statements, references dest.write)."""
    body = _extract_ondata_body()
    meaningful = [
        l for l in body.split("\n")
        if l.strip()
        and not l.strip().startswith("//")
        and not l.strip().startswith("*")
        and "$debug" not in l
        and l.strip() not in ("{", "}")
    ]
    assert len(meaningful) >= 4, f"ondata too trivial ({len(meaningful)} lines)"
    assert any("write" in l for l in meaningful), "no write call in ondata"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — src/js/CLAUDE.md @ 2d4c2beb
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/js/CLAUDE.md:56-65 @ 2d4c2beb
def test_no_bare_call_apply_in_ondata():
    """Agent code in ondata must use .$call/.$apply, not .call/.apply (src/js/CLAUDE.md)."""
    body = _extract_ondata_body()
    # Strip comments
    lines = [l for l in body.split("\n") if not l.strip().startswith("//")]
    clean = "\n".join(lines)
    # .call( or .apply( NOT preceded by $
    bare_call = re.search(r'(?<!\$)\.call\(', clean)
    bare_apply = re.search(r'(?<!\$)\.apply\(', clean)
    assert not bare_call, f"Found bare .call() in ondata (use .$call): {bare_call.group()}"
    assert not bare_apply, f"Found bare .apply() in ondata (use .$apply): {bare_apply.group()}"


# [agent_config] pass_to_pass — src/js/CLAUDE.md:71 @ 2d4c2beb
def test_no_console_log_in_ondata():
    """Debug logging must use $debug(), not console.log (src/js/CLAUDE.md)."""
    body = _extract_ondata_body()
    lines = [l for l in body.split("\n") if not l.strip().startswith("//")]
    clean = "\n".join(lines)
    assert "console.log" not in clean, "Found console.log in ondata — use $debug() instead"
    assert "console.warn" not in clean, "Found console.warn in ondata — use $debug() instead"
    assert "console.error" not in clean, "Found console.error in ondata — use $debug() instead"
