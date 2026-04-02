"""
Task: bun-toml-parse-log-deinit-leak
Repo: oven-sh/bun @ 36f17caa987d130788b97a6e9d7c9aea7895b6ed
PR:   28492

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Bun requires its full build system (Zig compiler, JSC, cmake) which
cannot run in the test container. All checks are structural analysis on
comment-stripped Zig source — this is the only viable approach for this task.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/src/bun.js/api/TOMLObject.zig"


def _strip_comments(text: str) -> str:
    """Remove // and /* */ comments from Zig source."""
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def _extract_fn_body(text: str, fn_name: str) -> str | None:
    """Extract the full body of a pub fn by name from comment-stripped source."""
    pattern = rf"pub\s+fn\s+{fn_name}\b"
    m = re.search(pattern, text)
    if not m:
        return None
    brace = text.find("{", m.start())
    if brace == -1:
        return None
    depth = 0
    for i in range(brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[m.start() : i + 1]
    return None


def _read_parse_body() -> str:
    """Read TOMLObject.zig and return the parse function body (stripped)."""
    raw = Path(TARGET).read_text()
    stripped = _strip_comments(raw)
    body = _extract_fn_body(stripped, "parse")
    assert body is not None, "pub fn parse not found in TOMLObject.zig"
    return body


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_log_deinit_after_init():
    """Log.init must be paired with a deferred log.deinit() to prevent memory leak."""
    body = _read_parse_body()

    assert re.search(r"Log\.init\s*\(", body), "Log.init() call not found"
    assert re.search(
        r"(defer|errdefer)\s+(\{?\s*)?log\.deinit\s*\(\s*\)", body
    ), "defer log.deinit() not found after Log.init()"

    init_pos = re.search(r"Log\.init\s*\(", body).start()
    deinit_pos = re.search(
        r"(defer|errdefer)\s+(\{?\s*)?log\.deinit\s*\(\s*\)", body
    ).start()
    assert deinit_pos > init_pos, "log.deinit() must come after Log.init()"


# [pr_diff] fail_to_pass
def test_modern_argument_api():
    """Argument access must use callframe.argument(), not deprecated arguments_old."""
    body = _read_parse_body()

    assert "arguments_old" not in body, (
        "parse() still uses deprecated arguments_old API"
    )
    assert re.search(r"callframe\.argument\s*\(", body), (
        "parse() does not use modern callframe.argument() API"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_input_validation_preserved():
    """Input validation for empty/null/undefined must be present with error throw."""
    body = _read_parse_body()

    assert re.search(
        r"(isEmptyOrUndefinedOrNull|isNull|isUndefined|isEmpty)", body
    ), "No null/undefined/empty check found in parse()"
    assert re.search(
        r"(throwInvalidArguments|throwError|@panic|return\s+error)", body
    ), "No error throwing found for invalid input"


# [pr_diff] pass_to_pass
def test_parse_chain_intact():
    """TOML parse call chain (toSlice + TOML.parse) must remain intact."""
    body = _read_parse_body()

    assert re.search(r"\.toSlice\s*\(", body), "toSlice() call missing from parse()"
    assert re.search(r"TOML\.parse\s*\(", body), "TOML.parse() call missing"


# [pr_diff] pass_to_pass
def test_peer_parsers_unmodified():
    """Peer parsers (JSONC, JSON5, YAML) must not be modified."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--name-only"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    changed = r.stdout.strip().split("\n") if r.stdout.strip() else []
    peers = ["JSONCObject.zig", "JSON5Object.zig", "YAMLObject.zig"]
    modified = [f for f in changed if any(p in f for p in peers)]
    assert not modified, f"Peer parsers were modified: {modified}"


# [pr_diff] pass_to_pass
def test_changes_scoped():
    """Only TOMLObject.zig should have substantial changes (>20 lines)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--numstat"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    lines = r.stdout.strip().split("\n") if r.stdout.strip() else []
    large = []
    for line in lines:
        parts = line.split("\t")
        if len(parts) == 3:
            try:
                total = int(parts[0]) + int(parts[1])
                if total > 20 and "TOMLObject.zig" not in parts[2]:
                    large.append(parts[2])
            except ValueError:
                pass
    assert not large, f"Large changes outside TOMLObject.zig: {large}"


# [static] pass_to_pass
def test_not_stub():
    """TOMLObject.zig must retain real structure — not stubbed out."""
    raw = Path(TARGET).read_text()
    stripped = _strip_comments(raw)

    line_count = len(raw.strip().splitlines())
    assert line_count >= 40, f"File too short ({line_count} lines), likely stubbed"

    pub_fns = re.findall(r"pub\s+fn\s+\w+", stripped)
    assert len(pub_fns) >= 2, f"Only {len(pub_fns)} pub fns, expected >= 2"

    body = _extract_fn_body(stripped, "parse")
    assert body is not None, "pub fn parse not found"
    stmts = [
        l.strip()
        for l in body.splitlines()
        if l.strip() and l.strip() not in ("}", "{")
    ]
    assert len(stmts) >= 8, f"parse() has only {len(stmts)} statements, likely a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from src/CLAUDE.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 36f17caa987d130788b97a6e9d7c9aea7895b6ed
def test_no_inline_import_in_functions():
    """No @import() calls inside function bodies (must be at module/struct level)."""
    raw = Path(TARGET).read_text()
    stripped = _strip_comments(raw)

    for m in re.finditer(r"(?:pub\s+)?fn\s+\w+", stripped):
        brace = stripped.find("{", m.start())
        if brace == -1:
            continue
        depth = 0
        for i in range(brace, len(stripped)):
            if stripped[i] == "{":
                depth += 1
            elif stripped[i] == "}":
                depth -= 1
                if depth == 0:
                    fn_body = stripped[brace : i + 1]
                    assert "@import(" not in fn_body, (
                        f"Inline @import found in function at offset {m.start()} "
                        f"(violates src/CLAUDE.md:11)"
                    )
                    break


# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 36f17caa987d130788b97a6e9d7c9aea7895b6ed
def test_bun_apis_over_std():
    """Must use bun.* APIs, not std.fs/posix/os/mem/process directly."""
    raw = Path(TARGET).read_text()
    stripped = _strip_comments(raw)

    # src/CLAUDE.md lines 16-28: std.fs, std.posix, std.os, std.mem (for strings),
    # std.process.Child are all banned in favor of bun.* equivalents
    violations = re.findall(r"std\.(fs|posix|os|process)\.\w+", stripped)
    assert not violations, (
        f"Uses std.* where bun.* should be used: {violations} "
        f"(violates src/CLAUDE.md:16)"
    )


# [agent_config] fail_to_pass — CLAUDE.md:232 @ 36f17caa987d130788b97a6e9d7c9aea7895b6ed
def test_defer_cleanup_for_inits():
    """Every resource .init() in parse() must have a corresponding defer .deinit()."""
    body = _read_parse_body()

    # Only check resources allocated with default_allocator (not arena-managed).
    # Arena allocations are freed implicitly by `defer arena.deinit()`.
    init_pattern = re.finditer(
        r"(?:var|const)\s+(\w+)\s*=\s*\w+[\.\w]*\.init\s*\(\s*default_allocator", body
    )
    for m in init_pattern:
        var_name = m.group(1)
        # Accept defer X.deinit(), defer X.exit(), errdefer X.deinit(), etc.
        cleanup_pat = rf"(defer|errdefer)\s+(\{{?\s*)?{re.escape(var_name)}\.(deinit|exit|close|free)\s*\("
        assert re.search(cleanup_pat, body), (
            f"Resource '{var_name}' initialized with default_allocator but no defer cleanup found "
            f"(violates CLAUDE.md:232 — use defer for cleanup)"
        )
