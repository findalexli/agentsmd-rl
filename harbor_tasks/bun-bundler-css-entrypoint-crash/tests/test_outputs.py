"""
Task: bun-bundler-css-entrypoint-crash
Repo: oven-sh/bun @ 7abe6c387d0746b26eeed7fe9175e14560840cbb
PR:   28251

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Zig code requires the full Bun build toolchain — cannot compile in container.
F2P tests use subprocess.run() to execute Python validation scripts that
analyze the Zig source for structural correctness of the fix.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
ZIG_FILE = Path(REPO) / "src/bundler/linker_context/computeChunks.zig"


def _read_zig():
    return ZIG_FILE.read_text()


def _extract_handler_body(text):
    """Extract the Handler struct body from computeChunks.zig."""
    m = re.search(r"const Handler\s*=\s*struct\s*\{(.*?)\n\s{8}\};", text, re.DOTALL)
    if not m:
        m = re.search(r"Handler.*=.*struct\s*\{(.*?)\n\s{8}\};", text, re.DOTALL)
    assert m, "Handler struct not found in computeChunks.zig"
    return m.group(1)


def _extract_next_body(handler_body):
    """Extract the body of Handler.next function."""
    m = re.search(r"pub fn next[^{]*\{(.*)\n\s{8,16}\}", handler_body, re.DOTALL)
    assert m, "Handler.next function not found"
    return m.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_zig_file_exists():
    """computeChunks.zig must exist and be non-empty."""
    assert ZIG_FILE.exists(), f"{ZIG_FILE} does not exist"
    assert ZIG_FILE.stat().st_size > 0, f"{ZIG_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_handler_next_no_direct_param_as_index():
    """Handler.next must not use its parameter directly as a chunks[] index.

    On the base commit, Handler.next does chunks[chunk_id] which crashes when
    CSS entry points cause gaps in the JS chunk index space. Any correct fix
    must translate the entry point ID through a mapping or restructure indexing.
    """
    r = subprocess.run(
        ["python3", "-c", (
            "import re, sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "# Extract Handler struct\n"
            "m = re.search(r\'const Handler\\s*=\\s*struct\\s*\\{(.*?)\\n\\s{8}\\};\', text, re.DOTALL)\n"
            "if not m:\n"
            "    m = re.search(r\'Handler.*=.*struct\\s*\\{(.*?)\\n\\s{8}\\};\', text, re.DOTALL)\n"
            "if not m:\n"
            "    print(\'FAIL: Handler struct not found\'); sys.exit(1)\n"
            "handler = m.group(1)\n"
            "# Get the parameter name of next()\n"
            "sig = re.search(r\'pub fn next\\s*\\(\\s*c\\s*:\\s*\\*@This\\(\\)\\s*,\\s*(\\w+)\\s*:\', handler)\n"
            "if not sig:\n"
            "    print(\'FAIL: Handler.next signature not found\'); sys.exit(1)\n"
            "param = sig.group(1)\n"
            "# Extract next body\n"
            "nm = re.search(r\'pub fn next[^{]*\\{(.*)\\n\\s{8,16}\\}\', handler, re.DOTALL)\n"
            "if not nm:\n"
            "    print(\'FAIL: Handler.next body not found\'); sys.exit(1)\n"
            "body = nm.group(1)\n"
            "# The raw parameter must NOT be used directly as chunks[param]\n"
            "if re.search(r\'c\\.chunks\\[\' + re.escape(param) + r\'\\]\', body):\n"
            "    print(f\'FAIL: parameter {param!r} used directly as chunks[] index\'); sys.exit(1)\n"
            "# Verify chunks IS still accessed (fix didn\'t delete core logic)\n"
            "has_chunks = bool(re.search(r\'c\\.chunks\\[\', body))\n"
            "has_core = \'getOrPut\' in body or \'files_with_parts_in_chunk\' in body\n"
            "if not (has_chunks or has_core):\n"
            "    print(\'FAIL: chunks access and core logic removed entirely\'); sys.exit(1)\n"
            "print(\'PASS\')\n"
        )],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Handler.next index check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_css_entry_point_guard():
    """Handler.next must guard/skip CSS-only entry points that have no JS chunk.

    On the base commit, Handler.next unconditionally accesses chunks[] with
    the entry point ID, causing a crash for CSS-only entries. The fix must
    add a guard (sentinel check, optional unwrap, bounds check, etc).
    """
    r = subprocess.run(
        ["python3", "-c", (
            "import re, sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "m = re.search(r\'const Handler\\s*=\\s*struct\\s*\\{(.*?)\\n\\s{8}\\};\', text, re.DOTALL)\n"
            "if not m:\n"
            "    m = re.search(r\'Handler.*=.*struct\\s*\\{(.*?)\\n\\s{8}\\};\', text, re.DOTALL)\n"
            "if not m:\n"
            "    print(\'FAIL: Handler struct not found\'); sys.exit(1)\n"
            "handler = m.group(1)\n"
            "nm = re.search(r\'pub fn next[^{]*\\{(.*)\\n\\s{8,16}\\}\', handler, re.DOTALL)\n"
            "if not nm:\n"
            "    print(\'FAIL: Handler.next body not found\'); sys.exit(1)\n"
            "body = nm.group(1)\n"
            "has_guard = (\n"
            "    bool(re.search(r\'maxInt|max_int|sentinel\', body))\n"
            "    or bool(re.search(r\'orelse\\s+return\', body))\n"
            "    or bool(re.search(r\'==\\s*null|!=\\s*null\', body))\n"
            "    or bool(re.search(r\'>=\\s*c\\.chunks\\.len|<\\s*c\\.chunks\\.len\', body))\n"
            "    or bool(re.search(r\'if\\s*\\(.*\\)\\s*return\', body))\n"
            ")\n"
            "if not has_guard:\n"
            "    print(\'FAIL: no guard for CSS-only entry points\'); sys.exit(1)\n"
            "print(\'PASS\')\n"
        )],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"CSS entry point guard check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_entry_point_to_chunk_mapping():
    """A mapping from entry point IDs to JS chunk indices must exist.

    The core fix requires translating entry_point IDs to JS chunk indices
    because CSS-only entry points don't get JS chunks. Accepts any data
    structure: flat array, HashMap, ArrayList, or named variable.
    """
    r = subprocess.run(
        ["python3", "-c", (
            "import re, sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "has_mapping = (\n"
            "    # Array allocated with entry_points.len\n"
            "    bool(re.search(r\'alloc\\(\\s*(?:u32|\\?u32)\\s*,\\s*(?:this\\.graph\\.)?entry_points\\.len\\)\', text))\n"
            "    # HashMap keyed on entry point IDs\n"
            "    or bool(re.search(r\'HashMap\\(.*entry.*chunk|AutoHashMap.*u32.*u32\', text))\n"
            "    # ArrayList for mapping\n"
            "    or bool(re.search(r\'ArrayList\\((?:u32|\\?u32)\\).*entry_point\', text))\n"
            "    # Variable allocated with entry_points.len\n"
            "    or bool(re.search(r\'\\w+\\s*=\\s*(?:try\\s+)?(?:temp_allocator|this\\.allocator|allocator)\\w*\\.alloc\\([^)]*entry_points\\.len\\)\', text))\n"
            "    # Slice field in Handler\n"
            "    or bool(re.search(r\'Handler.*struct.*\\[\\](?:const\\s+)?(?:u32|\\?u32)\', text, re.DOTALL))\n"
            ")\n"
            "if not has_mapping:\n"
            "    print(\'FAIL: no mapping from entry point IDs to chunk indices\'); sys.exit(1)\n"
            "print(\'PASS\')\n"
        )],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Entry point mapping check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_mapping_populated_during_chunk_creation():
    """The entry-point-to-chunk mapping must be written when JS chunks are created.

    On the base commit, no mapping is populated. The fix must record the chunk
    index at the point where js_chunks.getOrPut is called, otherwise the mapping
    array stays all-sentinels and every entry point gets skipped in Handler.next.
    """
    r = subprocess.run(
        ["python3", "-c", (
            "import re, sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "# Find the section where js_chunks.getOrPut is called\n"
            "getorput_section = re.search(\n"
            "    r\'js_chunks\\.getOrPut\\(js_chunk_key\\)(.*?)\\n\\s{8}\\}\',\n"
            "    text, re.DOTALL,\n"
            ")\n"
            "if not getorput_section:\n"
            "    print(\'FAIL: js_chunks.getOrPut(js_chunk_key) not found\'); sys.exit(1)\n"
            "section = getorput_section.group(1)\n"
            "# The mapping must be written in this section (any variable indexed by entry_id)\n"
            "has_mapping_write = bool(re.search(r\'\\w+\\[entry_id\\w*\\]\\s*=\', section))\n"
            "if not has_mapping_write:\n"
            "    print(\'FAIL: no mapping write near js_chunks.getOrPut\'); sys.exit(1)\n"
            "print(\'PASS\')\n"
        )],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Mapping population check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_handler_retains_core_logic():
    """Handler struct must retain chunks field, next function, and getOrPut logic."""
    text = _read_zig()
    handler_body = _extract_handler_body(text)

    assert "chunks" in handler_body, "Handler lost 'chunks' field"
    assert "fn next" in handler_body, "Handler lost 'next' function"
    assert "files_with_parts_in_chunk" in handler_body, "Handler lost files_with_parts_in_chunk"
    assert "getOrPut" in handler_body, "Handler lost getOrPut call"


# [pr_diff] pass_to_pass
def test_compute_chunks_structure():
    """computeChunks must still create js_chunks and css_chunks."""
    text = _read_zig()
    assert "js_chunks" in text, "js_chunks variable missing"
    assert "css_chunks" in text, "css_chunks variable missing"
    assert "entry_source_indices" in text, "entry_source_indices missing"


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_handler_next_not_stub():
    """Handler.next must have >= 3 meaningful lines (not a trivial stub)."""
    text = _read_zig()
    handler_body = _extract_handler_body(text)
    next_body = _extract_next_body(handler_body)

    lines = [ln.strip() for ln in next_body.split("\n")]
    meaningful = [ln for ln in lines if ln and not ln.startswith("//") and ln not in ("{", "}", "")]
    assert len(meaningful) >= 3, (
        f"Handler.next has only {len(meaningful)} meaningful lines — likely a stub"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:16 @ 7abe6c387d0746b26eeed7fe9175e14560840cbb
def test_no_prohibited_std_apis():
    """No std.fs/std.posix/std.os/std.process usage (bun.* wrappers required).

    Exception: std.math, std.mem, std.AutoArrayHashMap are OK per existing patterns.
    """
    text = _read_zig()
    bad = re.findall(r"std\.(fs|posix|os|process)\.", text)
    assert len(bad) == 0, f"Prohibited std.* API usage found: {bad}"


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 7abe6c387d0746b26eeed7fe9175e14560840cbb
def test_no_inline_imports():
    """No @import() inline inside function bodies."""
    text = _read_zig()
    fn_bodies = re.findall(r"pub fn \w+\([^)]*\)[^{]*\{(.*?)\n\s{8}\}", text, re.DOTALL)
    for body in fn_bodies:
        assert "@import(" not in body, "Found @import() inline inside a function body"


# [agent_config] pass_to_pass — src/CLAUDE.md:234-238 @ 7abe6c387d0746b26eeed7fe9175e14560840cbb
def test_no_catch_out_of_memory_pattern():
    """Must use bun.handleOom(), not 'catch bun.outOfMemory()' which swallows non-OOM errors."""
    text = _read_zig()
    bad = re.findall(r"catch\s+bun\.outOfMemory\(\)", text)
    assert len(bad) == 0, (
        f"Found {len(bad)} uses of 'catch bun.outOfMemory()' — "
        "use bun.handleOom() or 'try' instead"
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo CI: Prettier formatting
def test_repo_prettier_config_files():
    """Config files must be formatted according to Prettier (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "package.json", "tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Prettier check on oxlint.json
def test_repo_prettier_oxlint_json():
    """oxlint.json must be formatted according to Prettier (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "oxlint.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for oxlint.json:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Prettier check on .clang-tidy
def test_repo_prettier_clang_tidy():
    """.clang-tidy must be formatted according to Prettier (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", ".clang-tidy"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for .clang-tidy:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Prettier check on additional config files
def test_repo_prettier_misc_configs():
    """Additional config files must be formatted according to Prettier (pass_to_pass)."""
    config_files = [".prettierrc", ".clang-tidy"]
    existing = [f for f in config_files if (Path(REPO) / f).exists()]
    if existing:
        r = subprocess.run(
            ["npx", "prettier", "--check"] + existing,
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Basic Zig structure validation
def test_zig_file_basic_structure():
    """Zig file must have valid basic structure (balanced braces, key constructs)."""
    r = subprocess.run(
        ["python3", "-c", (
            "import sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "# Check balanced braces\n"
            "if text.count(\'{\') != text.count(\'}\'):\n"
            "    print(\'FAIL: Unbalanced braces\'); sys.exit(1)\n"
            "# Check balanced parentheses\n"
            "if text.count(\'(\') != text.count(\')\'):\n"
            "    print(\'FAIL: Unbalanced parentheses\'); sys.exit(1)\n"
            "# Check balanced brackets\n"
            "if text.count(\'[\') != text.count(\']\'):\n"
            "    print(\'FAIL: Unbalanced brackets\'); sys.exit(1)\n"
            "# Check key constructs exist\n"
            "if \'pub noinline fn computeChunks\' not in text:\n"
            "    print(\'FAIL: computeChunks function not found\'); sys.exit(1)\n"
            "if \'const Handler\' not in text:\n"
            "    print(\'FAIL: Handler struct not found\'); sys.exit(1)\n"
            "print(\'PASS\')\n"
        )],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Zig structure check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout




# [repo_tests] pass_to_pass — Python JSON validation for repo config files
def test_repo_json_valid():
    """package.json and tsconfig.json must be valid JSON (pass_to_pass)."""
    import json

    for filename in ["package.json", "tsconfig.json"]:
        filepath = Path(REPO) / filename
        if filepath.exists():
            try:
                with open(filepath) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                assert False, f"{filename} is not valid JSON: {e}"


# [repo_tests] pass_to_pass — Zig function signature validation
def test_zig_function_signatures():
    """Key Zig functions must have valid signatures (pass_to_pass)."""
    text = _read_zig()

    # computeChunks must be a pub function
    assert re.search(r'pub\s+(?:noinline\s+)?fn\s+computeChunks', text), \
        "computeChunks must be a pub function"

    # Handler.next must be a pub fn
    handler_body = _extract_handler_body(text)
    assert re.search(r'pub\s+fn\s+next', handler_body), \
        "Handler.next must be a pub fn"


# [repo_tests] pass_to_pass — Check for repo file existence
def test_repo_critical_files_exist():
    """Critical repo files must exist (pass_to_pass)."""
    critical_files = [
        "CLAUDE.md",
        "build.zig",
        "package.json",
        "tsconfig.json",
        "CONTRIBUTING.md",
    ]
    for filename in critical_files:
        filepath = Path(REPO) / filename
        assert filepath.exists(), f"Critical file {filename} is missing"
        assert filepath.stat().st_size > 0, f"Critical file {filename} is empty"


# [repo_tests] pass_to_pass — Zig syntax: no double semicolons
def test_zig_no_double_semicolons():
    """Zig file must not contain double semicolons (pass_to_pass)."""
    text = _read_zig()
    double_semicolons = text.count(";;")
    assert double_semicolons == 0, f"Found {double_semicolons} double semicolons"
