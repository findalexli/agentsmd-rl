"""
Task: bun-inspect-env-transpiler-cache
Repo: oven-sh/bun @ 047cedb2b3b05fb89b7081ab753d77a2f4df0135
PR:   #28189

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
VM_FILE = Path(REPO) / "src/bun.js/VirtualMachine.zig"
ARGS_FILE = Path(REPO) / "src/cli/Arguments.zig"


# ---------------------------------------------------------------------------
# Helpers — Zig source parsing (cannot compile Zig in test container)
# ---------------------------------------------------------------------------

def _extract_zig_fn(source: str, fn_name: str) -> str | None:
    """Extract a Zig function body using balanced brace counting."""
    pattern = re.compile(r"\bfn\s+" + re.escape(fn_name) + r"\b")
    m = pattern.search(source)
    if not m:
        return None
    brace_start = source.find("{", m.end())
    if brace_start < 0:
        return None
    depth, i = 0, brace_start
    while i < len(source):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[m.start() : i + 1]
        i += 1
    return None


def _strip_zig_comments(code: str) -> str:
    """Strip // line comments from Zig source."""
    out = []
    for line in code.split("\n"):
        in_str, buf, i = False, [], 0
        while i < len(line):
            if line[i] == '"' and (i == 0 or line[i - 1] != "\\"):
                in_str = not in_str
            elif not in_str and i + 1 < len(line) and line[i : i + 2] == "//":
                break
            buf.append(line[i])
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def _get_configure_debugger() -> str:
    """Return comment-stripped configureDebugger function body."""
    src = VM_FILE.read_text()
    body = _extract_zig_fn(src, "configureDebugger")
    assert body is not None, "configureDebugger function not found in VirtualMachine.zig"
    return _strip_zig_comments(body)


def _added_lines(*paths: str) -> list[str]:
    """Return added lines from git diff HEAD for given paths."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--"] + list(paths),
        capture_output=True, text=True, cwd=REPO,
    )
    return [
        l[1:] for l in r.stdout.split("\n")
        if l.startswith("+") and not l.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cache_disabled_in_configure_debugger():
    """configureDebugger must disable RuntimeTranspilerCache."""
    body = _get_configure_debugger()
    has_disable = (
        re.search(r"RuntimeTranspilerCache\S*\.\s*is_disabled\s*=\s*true", body)
        or re.search(r"RuntimeTranspilerCache\S*\.disable\s*\(", body)
    )
    assert has_disable, "RuntimeTranspilerCache is not disabled in configureDebugger"
    # Verify it's a real code statement (not just a substring match on something else)
    for line in body.split("\n"):
        s = line.strip()
        if "RuntimeTranspilerCache" in s and ("is_disabled" in s or "disable(" in s):
            if "=" in s or "(" in s:
                return
    assert False, "RuntimeTranspilerCache disable is not a real code statement"


# [pr_diff] fail_to_pass
def test_cache_disable_applies_to_all_inspector_modes():
    """Cache disable must not be gated on mode != .connect (must work for BUN_INSPECT)."""
    body = _get_configure_debugger()
    lines = body.split("\n")

    # Find the cache disable line
    cache_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if "RuntimeTranspilerCache" in s and ("is_disabled" in s or "disable(" in s):
            if "=" in s or "(" in s:
                cache_idx = i
                break
    assert cache_idx is not None, "No RuntimeTranspilerCache disable found in configureDebugger"

    # Walk backwards — must NOT be inside a mode != .connect block
    depth = 0
    for i in range(cache_idx - 1, -1, -1):
        depth += lines[i].count("}") - lines[i].count("{")
        if depth < 0 and re.search(
            r"mode\s*!=\s*\.connect|mode\s*!=\s*InspectorMode\.connect", lines[i]
        ):
            assert False, "Cache disable is gated on mode != .connect — BUN_INSPECT won't work"

    # Function must check for inspector being enabled
    assert any(
        kw in body
        for kw in ("isInspectorEnabled()", "inspector_enabled", "BUN_INSPECT")
    ), "configureDebugger doesn't check whether inspector is enabled"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_debugger_settings_preserved():
    """Existing debugger options (minify_*, debugger=true) must be preserved."""
    body = _get_configure_debugger()
    for setting in ("minify_identifiers", "minify_syntax", "minify_whitespace"):
        found = any(setting in ln and "=" in ln for ln in body.split("\n"))
        assert found, f"Debugger setting '{setting}' missing from configureDebugger"
    assert any(
        s in body for s in ("debugger = true", "debugger=true", ".debugger = true")
    ), "debugger = true not set in configureDebugger"


# [pr_diff] pass_to_pass
def test_inspect_flags_handled():
    """Arguments.zig must still handle --inspect, --inspect-wait, --inspect-brk."""
    src = ARGS_FILE.read_text()
    for flag in ('--inspect"', '--inspect-wait"', '--inspect-brk"'):
        assert flag in src, f"Arguments.zig no longer handles {flag}"


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_not_stub():
    """VirtualMachine.zig must have non-trivial code changes."""
    added = _added_lines("src/bun.js/VirtualMachine.zig")
    removed_r = subprocess.run(
        ["git", "diff", "HEAD", "--", "src/bun.js/VirtualMachine.zig"],
        capture_output=True, text=True, cwd=REPO,
    )
    removed = [
        l[1:] for l in removed_r.stdout.split("\n")
        if l.startswith("-") and not l.startswith("---")
    ]
    code_changes = sum(
        1 for l in added + removed
        if l.strip() and not l.strip().startswith("//")
    )
    assert code_changes >= 3, f"Only {code_changes} real code changes — appears to be a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 047cedb
def test_no_inline_import_in_changes():
    """No @import() inline inside functions (src/CLAUDE.md:11)."""
    for line in _added_lines("src/bun.js/VirtualMachine.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        if "@import(" in s and "const" not in s.split("@import")[0]:
            assert False, f"Inline @import found: {s}"


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 047cedb
def test_no_std_api_in_changes():
    """No std.fs/std.posix/std.os/std.base64/std.mem usage in changes (src/CLAUDE.md:16-28)."""
    forbidden = ("std.fs.", "std.posix.", "std.os.", "std.process.", "std.base64.")
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        for f in forbidden:
            if f in s:
                assert False, f"Forbidden {f} usage: {s}"


# [agent_config] pass_to_pass — src/CLAUDE.md:25 @ 047cedb
def test_no_std_mem_for_strings():
    """No std.mem string ops in added code; use bun.strings.* instead (src/CLAUDE.md:25)."""
    forbidden = ("std.mem.eql(", "std.mem.startsWith(", "std.mem.endsWith(", "std.mem.indexOf(")
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        for f in forbidden:
            if f in s:
                assert False, f"Use bun.strings.* instead of {f}: {s}"


# [agent_config] pass_to_pass — src/CLAUDE.md:234 @ 047cedb
def test_no_catch_out_of_memory():
    """Must use bun.handleOom() not 'catch bun.outOfMemory()' (src/CLAUDE.md:234-238)."""
    for line in _added_lines("src/bun.js/VirtualMachine.zig", "src/cli/Arguments.zig"):
        s = line.strip()
        if s.startswith("//"):
            continue
        if "catch" in s and "outOfMemory" in s:
            assert False, f"Use bun.handleOom() instead of catch outOfMemory: {s}"
