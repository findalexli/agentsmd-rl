"""
Task: nextjs-turbopack-compact-span-hierarchy
Repo: vercel/next.js @ df886d4a2d36b63717f8aa5eae1147811ad025f8
PR:   91693

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

DB_FILE = Path("/workspace/next.js/turbopack/crates/turbo-persistence/src/db.rs")
MOD_FILE = Path("/workspace/next.js/turbopack/crates/turbo-tasks-backend/src/backend/mod.rs")


def _strip_comments(text: str) -> str:
    """Remove single-line // comments from Rust source."""
    return re.sub(r"//[^\n]*", "", text)


def _extract_fn_body(src: str, fn_name: str) -> str | None:
    """Extract the body of a named function from Rust source."""
    in_fn = False
    depth = 0
    lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if re.search(rf"fn\s+{fn_name}\b", stripped):
            in_fn = True
            depth = 0
        if in_fn:
            depth += stripped.count("{") - stripped.count("}")
            lines.append(stripped)
            if depth <= 0 and len(lines) > 1:
                break
    return "\n".join(lines) if lines else None


def _find_span_macros(src: str) -> list[dict]:
    """Find all tracing span macros and their arguments in Rust source."""
    results = []
    for m in re.finditer(
        r"(info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)\s*\(", src
    ):
        name = m.group(1)
        start = m.end()
        d = 1
        i = start
        while i < len(src) and d > 0:
            if src[i] == "(":
                d += 1
            elif src[i] == ")":
                d -= 1
            i += 1
        body = src[start : i - 1] if d == 0 else src[start : start + 300]
        results.append({"name": name, "body": body, "pos": m.start()})
    return results


def _run_node(code: str, *args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js script that analyzes Rust source files."""
    script = Path("/workspace/next.js/_eval_tmp.mjs")
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/workspace/next.js",
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_compact_span_removed_from_db():
    """compact() in db.rs must no longer create its own tracing span."""
    r = _run_node(
        """
import { readFileSync } from 'fs';
const src = readFileSync(process.argv[1], 'utf8').replace(/\\/\\/[^\\n]*/g, '');
const lines = src.split('\\n');
let inFn = false, depth = 0, body = [];
for (const line of lines) {
    const s = line.trim();
    if (/fn\\s+compact\\b/.test(s)) { inFn = true; depth = 0; }
    if (inFn) {
        depth += (s.match(/{/g)||[]).length - (s.match(/}/g)||[]).length;
        body.push(s);
        if (depth <= 0 && body.length > 1) break;
    }
}
const fnText = body.join('\\n');
const spanRe = /(?:info_span!|trace_span!|debug_span!|warn_span!|error_span!|span!)\\s*\\(/g;
let match;
while ((match = spanRe.exec(fnText)) !== null) {
    let start = match.index + match[0].length, d = 1, i = start;
    while (i < fnText.length && d > 0) {
        if (fnText[i] === '(') d++; else if (fnText[i] === ')') d--;
        i++;
    }
    const macroBody = fnText.slice(start, i - 1);
    if (/"[^"]*compact[^"]*"/i.test(macroBody)) {
        process.stderr.write('compact span still in db.rs: ' + macroBody.slice(0, 80));
        process.exit(1);
    }
}
console.log('PASS');
""",
        str(DB_FILE),
    )
    assert r.returncode == 0, f"Node analysis failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_compact_span_added_to_mod():
    """A compact-related tracing span must exist in mod.rs (the call site)."""
    src = _strip_comments(MOD_FILE.read_text())
    for span in _find_span_macros(src):
        if re.search(r'"[^"]*compact[^"]*"', span["body"], re.IGNORECASE):
            return
    # Fallback: check near .compact() call
    lines = src.splitlines()
    for idx, line in enumerate(lines):
        if ".compact()" in line:
            window = "\n".join(lines[max(0, idx - 15) : idx + 5])
            if _find_span_macros(window):
                return
    assert False, "No compact-related tracing span found in mod.rs"


# [pr_diff] fail_to_pass
def test_root_span_in_mod():
    """A root span (parent: None) must exist in mod.rs for background work."""
    src = MOD_FILE.read_text()
    patterns = [
        r"(?:info_span!|trace_span!|debug_span!|span!)\s*\(\s*parent\s*:\s*None",
        r"parent\s*:\s*None\s*,\s*\"",
        r"Span::none\(\)",
    ]
    for pat in patterns:
        if re.search(pat, src):
            return
    assert False, "No root span (parent: None) found in mod.rs"


# [pr_diff] fail_to_pass
def test_sync_span_not_info_level():
    """'sync new files' span in db.rs must not be at info level."""
    r = _run_node(
        """
import { readFileSync } from 'fs';
const src = readFileSync(process.argv[1], 'utf8');
if (!src.includes('"sync new files"')) { console.log('PASS'); process.exit(0); }
const lines = src.split('\\n');
for (let i = 0; i < lines.length; i++) {
    if (!lines[i].includes('"sync new files"')) continue;
    const ctx = lines.slice(Math.max(0, i - 3), i + 1).join('\\n')
        .replace(/\\/\\/[^\\n]*/g, '');
    if (/info_span!|warn_span!/.test(ctx)) {
        process.stderr.write('sync new files still at info level');
        process.exit(1);
    }
    if (/trace_span!|debug_span!|Level::TRACE|Level::DEBUG/.test(ctx)) {
        console.log('PASS'); process.exit(0);
    }
}
process.stderr.write('Could not determine sync new files span level');
process.exit(1);
""",
        str(DB_FILE),
    )
    assert r.returncode == 0, f"Node analysis failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_snapshot_and_persist_not_called_with_none():
    """snapshot_and_persist must not be called with None as first arg."""
    src = _strip_comments(MOD_FILE.read_text())
    calls = re.findall(r"snapshot_and_persist\(\s*([^,)]+)", src)
    if not calls:
        assert "snapshot_and_persist" not in src, (
            "snapshot_and_persist exists but no calls found"
        )
        return
    for arg in calls:
        assert arg.strip() != "None", "snapshot_and_persist still called with None"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_compact_call_still_present():
    """Compaction logic must still invoke compact() on backing storage."""
    src = MOD_FILE.read_text()
    assert re.search(r"\.compact\(\)", src), "compact() call missing from mod.rs"


# [static] pass_to_pass
def test_mod_rs_not_stub():
    """mod.rs has substantial content (not a stub replacement)."""
    line_count = len(MOD_FILE.read_text().splitlines())
    assert line_count > 2000, f"mod.rs has only {line_count} lines (possible stub)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:414 @ df886d4a
def test_no_formatting_issues():
    """No tabs or trailing whitespace in modified files (cargo fmt)."""
    issues = []
    for path in [DB_FILE, MOD_FILE]:
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if "\t" in line and not line.lstrip().startswith("//"):
                issues.append(f"{path.name}:{i}: tab character")
            stripped = line.rstrip()
            if stripped != line and stripped:
                issues.append(f"{path.name}:{i}: trailing whitespace")
    assert not issues, f"Formatting issues: {issues[:5]}"


# ---------------------------------------------------------------------------
# Repo CI pass_to_pass — cargo check, fmt, clippy for modified crates
# ---------------------------------------------------------------------------

REPO = Path("/workspace/next.js")


# [repo_tests] pass_to_pass
def test_repo_cargo_check_turbo_persistence():
    """Cargo check passes for turbo-persistence crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "turbo-persistence"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check turbo-persistence failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check_turbo_tasks_backend():
    """Cargo check passes for turbo-tasks-backend crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "turbo-tasks-backend"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check turbo-tasks-backend failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_fmt_check():
    """Cargo fmt check passes for workspace (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy_turbo_persistence():
    """Cargo clippy passes for turbo-persistence crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "turbo-persistence", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy turbo-persistence failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy_turbo_tasks_backend():
    """Cargo clippy passes for turbo-tasks-backend crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "turbo-tasks-backend", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy turbo-tasks-backend failed:\n{r.stderr[-500:]}"
