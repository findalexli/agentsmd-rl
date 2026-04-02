"""
Task: nextjs-turbo-persistence-mmap-alignment
Repo: vercel/next.js @ bdb2f2ce4dea0c1435af5fa433767d63fca11c0c
PR:   91640

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
META_FILE = Path(REPO) / "turbopack/crates/turbo-persistence/src/meta_file.rs"
MMAP_HELPER = Path(REPO) / "turbopack/crates/turbo-persistence/src/mmap_helper.rs"


def _read(path: Path) -> str:
    return path.read_text()


def _extract_fn(src: str, fn_name: str) -> str:
    """Extract a Rust function body (from 'fn name' to the next 'fn ' or end)."""
    parts = src.split(f"fn {fn_name}")
    assert len(parts) >= 2, f"Function {fn_name} not found"
    body = parts[1]
    # Find the next top-level fn definition (heuristic: '\n    fn ' or '\n    pub fn ')
    m = re.search(r"\n    (?:pub )?fn ", body)
    if m:
        body = body[: m.start()]
    return body


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_mmap_maps_from_byte_zero():
    """mmap must map the entire file from byte 0, not use options.offset()."""
    # AST-only because: Rust code cannot be imported/executed in Python
    src = _read(META_FILE)
    open_internal = _extract_fn(src, "open_internal")

    # The buggy code calls options.offset(offset) — must be removed
    assert "options.offset(" not in open_internal, (
        "options.offset() still present — mmap offset not removed"
    )
    # The fix uses MmapOptions::new().map(&file) directly
    assert "MmapOptions::new()" in open_internal, (
        "Expected MmapOptions::new() direct construction"
    )
    assert ".map(&file)" in open_internal or ".map(& file)" in open_internal, (
        "Expected .map(&file) call on MmapOptions"
    )


# [pr_diff] fail_to_pass
def test_amqf_data_start_field():
    """MetaFile struct must have an amqf_data_start field storing the header-end offset."""
    # AST-only because: Rust struct definitions cannot be executed in Python
    src = _read(META_FILE)

    # Extract the struct definition
    struct_match = re.search(
        r"pub struct MetaFile\s*\{(.*?)\n\}", src, re.DOTALL
    )
    assert struct_match, "MetaFile struct not found"
    struct_body = struct_match.group(1)

    # Field must exist with usize type
    assert "amqf_data_start" in struct_body, (
        "amqf_data_start field not in MetaFile struct"
    )
    assert re.search(r"amqf_data_start\s*:\s*usize", struct_body), (
        "amqf_data_start must be of type usize"
    )


# [pr_diff] fail_to_pass
def test_amqf_data_returns_offset_slice():
    """amqf_data() must return &self.mmap[self.amqf_data_start..] not &self.mmap."""
    # AST-only because: Rust method cannot be called from Python
    src = _read(META_FILE)
    amqf_data_fn = _extract_fn(src, "amqf_data")

    # Must slice from amqf_data_start, not return the whole mmap
    assert "self.amqf_data_start" in amqf_data_fn, (
        "amqf_data() does not reference amqf_data_start"
    )
    assert re.search(r"self\.mmap\[self\.amqf_data_start", amqf_data_fn), (
        "amqf_data() must index mmap with amqf_data_start"
    )


# [pr_diff] fail_to_pass
def test_amqf_data_start_set_in_constructor():
    """amqf_data_start must be initialized from the stream position in open_internal."""
    # AST-only because: Rust constructor cannot be executed from Python
    src = _read(META_FILE)
    open_internal = _extract_fn(src, "open_internal")

    # The field must be assigned in the Self constructor
    assert "amqf_data_start:" in open_internal or "amqf_data_start :" in open_internal, (
        "amqf_data_start not set in open_internal constructor"
    )
    # It should derive from the stream position (offset variable)
    # Check multiple patterns: direct cast, as usize, or variable assignment
    assert re.search(r"amqf_data_start:\s*offset\b", open_internal) or \
        re.search(r"amqf_data_start:\s*\w*offset\w*\s+as\s+usize", open_internal), (
        "amqf_data_start must be set from the stream position offset"
    )


# [pr_diff] fail_to_pass
def test_mmap_helper_error_context():
    """mmap_helper.rs must import anyhow::Context and add .context() to advise calls."""
    # AST-only because: Rust code cannot be imported in Python
    src = _read(MMAP_HELPER)

    # Must import Context from anyhow
    assert re.search(r"use\s+anyhow::Context", src), (
        "Missing 'use anyhow::Context' import in mmap_helper.rs"
    )

    # Must have .context() or .with_context() on DontFork and Unmergeable advise calls
    context_calls = re.findall(r'\.(?:with_)?context\([^)]+\)', src)
    assert len(context_calls) >= 2, (
        f"Expected >= 2 .context()/.with_context() calls in mmap_helper.rs, found {len(context_calls)}"
    )

    # Verify context strings mention the specific advice types
    combined = " ".join(context_calls)
    assert "DontFork" in combined or "Unmergeable" in combined, (
        "Context messages should mention the specific mmap advice type"
    )


# [pr_diff] fail_to_pass
def test_meta_file_open_error_context():
    """open_internal must have .context() on File::open, stream_position, mmap, and advise."""
    # AST-only because: Rust code cannot be imported in Python
    src = _read(META_FILE)
    open_internal = _extract_fn(src, "open_internal")

    context_calls = re.findall(r'\.(?:with_)?context\([^)]+\)', open_internal)
    assert len(context_calls) >= 3, (
        f"Expected >= 3 .context()/.with_context() calls in open_internal, found {len(context_calls)}"
    )

    # Check that key operations have context
    combined = " ".join(context_calls)
    assert "open" in combined.lower() or "meta file" in combined.lower(), (
        "Missing error context for File::open"
    )
    assert "mmap" in combined.lower(), (
        "Missing error context for mmap operation"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub + structural integrity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_files_exist():
    """Both modified files must exist."""
    assert META_FILE.exists(), f"{META_FILE} does not exist"
    assert MMAP_HELPER.exists(), f"{MMAP_HELPER} does not exist"


# [static] pass_to_pass
def test_not_stub():
    """Modified files must have substantial content (not stubbed out)."""
    meta_lines = _read(META_FILE).splitlines()
    helper_lines = _read(MMAP_HELPER).splitlines()

    assert len(meta_lines) >= 100, (
        f"meta_file.rs has {len(meta_lines)} lines, expected >= 100"
    )
    assert len(helper_lines) >= 5, (
        f"mmap_helper.rs has {len(helper_lines)} lines, expected >= 5"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:414 @ bdb2f2ce4dea0c1435af5fa433767d63fca11c0c
def test_rust_files_formatted():
    """Modified Rust files must be properly formatted (cargo fmt / rustfmt)."""
    for path in [META_FILE, MMAP_HELPER]:
        r = subprocess.run(
            ["rustfmt", "--edition", "2021", "--check", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"rustfmt found formatting issues in {path.name}:\n{r.stdout}{r.stderr}"
        )


# [agent_config] pass_to_pass — CLAUDE.md:348 @ bdb2f2ce4dea0c1435af5fa433767d63fca11c0c
def test_no_claude_footer():
    """Commits must not contain 'Generated with Claude Code' footers."""
    r = subprocess.run(
        ["git", "log", "--format=%B", "-n5"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    log = r.stdout
    assert "Generated with Claude" not in log, (
        "Commit message contains 'Generated with Claude' footer"
    )
    assert "Co-Authored-By: Claude" not in log, (
        "Commit message contains 'Co-Authored-By: Claude' footer"
    )
