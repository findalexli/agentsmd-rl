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


# [static] pass_to_pass
def test_zig_file_exists():
    """computeChunks.zig must exist and be non-empty."""
    assert ZIG_FILE.exists(), f"{ZIG_FILE} does not exist"
    assert ZIG_FILE.stat().st_size > 0, f"{ZIG_FILE} is empty"


# [pr_diff] fail_to_pass
def test_handler_next_no_direct_param_as_index():
    """Handler.next must not use its parameter directly as a chunks[] index."""
    r = subprocess.run(
        ["python3", "-c", (
            "import re, sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "m = re.search(r\'const Handler\\s*=\\s*struct\\s*\\{(.*?)\\n\\s{8}\};\', text, re.DOTALL)\n"
            "if not m:\n"
            "    m = re.search(r\'Handler.*=.*struct\\s*\\{(.*?)\\n\\s{8}\};\', text, re.DOTALL)\n"
            "if not m:\n"
            "    print(\'FAIL: Handler struct not found\'); sys.exit(1)\n"
            "handler = m.group(1)\n"
            "sig = re.search(r\'pub fn next\\s*\\(\\s*c\\s*:\\s*\\*@This\\(\\)\\s*,\\s*(\\w+)\\s*:\', handler)\n"
            "if not sig:\n"
            "    print(\'FAIL: Handler.next signature not found\'); sys.exit(1)\n"
            "param = sig.group(1)\n"
            "nm = re.search(r\'pub fn next[^{]*\\{(.*)\\n\\s{8,16}\}\', handler, re.DOTALL)\n"
            "if not nm:\n"
            "    print(\'FAIL: Handler.next body not found\'); sys.exit(1)\n"
            "body = nm.group(1)\n"
            "if re.search(r\'c\\.chunks\\[\' + re.escape(param) + r\'\\]\', body):\n"
            "    print(f\'FAIL: parameter {param!r} used directly as chunks[] index\'); sys.exit(1)\n"
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
    """Handler.next must guard/skip CSS-only entry points that have no JS chunk."""
    r = subprocess.run(
        ["python3", "-c", (
            "import re, sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "m = re.search(r\'const Handler\\s*=\\s*struct\\s*\\{(.*?)\\n\\s{8}\};\', text, re.DOTALL)\n"
            "if not m:\n"
            "    m = re.search(r\'Handler.*=.*struct\\s*\\{(.*?)\\n\\s{8}\};\', text, re.DOTALL)\n"
            "if not m:\n"
            "    print(\'FAIL: Handler struct not found\'); sys.exit(1)\n"
            "handler = m.group(1)\n"
            "nm = re.search(r\'pub fn next[^{]*\\{(.*)\\n\\s{8,16}\}\', handler, re.DOTALL)\n"
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
    """A mapping from entry point IDs to JS chunk indices must exist."""
    r = subprocess.run(
        ["python3", "-c", (
            "import re, sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "has_mapping = (\n"
            "    bool(re.search(r\'alloc\\(\\s*(?:u32|\\?u32)\\s*,\\s*(?:this\\.graph\\.)?entry_points\\.len\\)\', text))\n"
            "    or bool(re.search(r\'HashMap\\(.*entry.*chunk|AutoHashMap.*u32.*u32\', text))\n"
            "    or bool(re.search(r\'ArrayList\\((?:u32|\\?u32)\\).*entry_point\', text))\n"
            "    or bool(re.search(r\'\\w+\\s*=\\s*(?:try\\s+)?(?:temp_allocator|this\\.allocator|allocator)\\w*\\.alloc\\([^)]*entry_points\\.len\\)\', text))\n"
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
    """The entry-point-to-chunk mapping must be written when JS chunks are created."""
    r = subprocess.run(
        ["python3", "-c", (
            "import re, sys\n"
            "text = open(\'/workspace/bun/src/bundler/linker_context/computeChunks.zig\').read()\n"
            "getorput_section = re.search(\n"
            "    r\'js_chunks\\.getOrPut\\(js_chunk_key\\)(.*?)\\n\\s{8}\}\',\n"
            "    text, re.DOTALL,\n"
            ")\n"
            "if not getorput_section:\n"
            "    print(\'FAIL: js_chunks.getOrPut(js_chunk_key) not found\'); sys.exit(1)\n"
            "section = getorput_section.group(1)\n"
            "has_mapping_write = bool(re.search(r\'\\w+\\[entry_id\\w*\\]\\s*=\', section))\n"
            "if not has_mapping_write:\n"
            "    print(\'FAIL: no mapping write near js_chunks.getOrPut\'); sys.exit(1)\n"
            "print(\'PASS\')\n"
        )],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Mapping population check failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


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


# [static] pass_to_pass
def test_handler_next_not_stub():
    """Handler.next must have >= 3 meaningful lines (not a trivial stub)."""
    text = _read_zig()
    handler_body = _extract_handler_body(text)
    next_body = _extract_next_body(handler_body)
    lines = [ln.strip() for ln in next_body.split("\n")]
    meaningful = [ln for ln in lines if ln and not ln.startswith("//") and ln not in ("{", "}", "")]
    assert len(meaningful) >= 3, f"Handler.next has only {len(meaningful)} meaningful lines — likely a stub"


# [agent_config] pass_to_pass
def test_no_prohibited_std_apis():
    """No std.fs/std.posix/std.os/std.process usage (bun.* wrappers required)."""
    text = _read_zig()
    bad = re.findall(r"std\.(fs|posix|os|process)\.", text)
    assert len(bad) == 0, f"Prohibited std.* API usage found: {bad}"


# [agent_config] pass_to_pass
def test_no_inline_imports():
    """No @import() inline inside function bodies."""
    text = _read_zig()
    fn_bodies = re.findall(r"pub fn \w+\([^)]*\)[^{]*\{(.*?)\n\s{8}\}", text, re.DOTALL)
    for body in fn_bodies:
        assert "@import(" not in body, "Found @import() inline inside a function body"


# [agent_config] pass_to_pass
def test_no_catch_out_of_memory_pattern():
    """Must use bun.handleOom(), not 'catch bun.outOfMemory()'."""
    text = _read_zig()
    bad = re.findall(r"catch\s+bun\.outOfMemory\(\)", text)
    assert len(bad) == 0, f"Found {len(bad)} uses of 'catch bun.outOfMemory()' — use bun.handleOom() or 'try' instead"


# [repo_tests] pass_to_pass
def test_repo_prettier_config_files():
    """Config files must be formatted according to Prettier (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "package.json", "tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_oxlint_json():
    """oxlint.json must be formatted according to Prettier (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "oxlint.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for oxlint.json:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_clang_tidy():
    """.clang-tidy must be formatted according to Prettier (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", ".clang-tidy"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for .clang-tidy:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
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


# [repo_tests] pass_to_pass
def test_repo_prettier_bundler_files():
    """Bundler related files must pass Prettier formatting (pass_to_pass)."""
    bundler_files = ["tsconfig.json"]
    existing = [f for f in bundler_files if (Path(REPO) / f).exists()]
    if existing:
        r = subprocess.run(
            ["npx", "--yes", "prettier@3.6.2", "--check"] + existing,
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_git_status():
    """Git repository must be in a valid state (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git status failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_package_json_valid_subprocess():
    """package.json must be valid JSON (verified via Python subprocess) (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import json; json.load(open('/workspace/bun/package.json')); print('VALID')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"JSON validation failed:\n{r.stderr}"
    assert "VALID" in r.stdout, "package.json is not valid JSON"


# [repo_tests] pass_to_pass
def test_repo_tsconfig_json_valid_subprocess():
    """tsconfig.json must be valid JSON (verified via Python subprocess) (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import json; json.load(open('/workspace/bun/tsconfig.json')); print('VALID')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"JSON validation failed:\n{r.stderr}"
    assert "VALID" in r.stdout, "tsconfig.json is not valid JSON"


# [static] pass_to_pass
def test_zig_file_basic_structure():
    """Zig file must have valid basic structure (balanced braces, key constructs)."""
    text = _read_zig()
    assert text.count('{') == text.count('}'), "Unbalanced braces in Zig file"
    assert text.count('(') == text.count(')'), "Unbalanced parentheses in Zig file"
    assert text.count('[') == text.count(']'), "Unbalanced brackets in Zig file"
    assert 'pub noinline fn computeChunks' in text, "computeChunks function not found"
    assert 'const Handler' in text, "Handler struct not found"


# [static] pass_to_pass
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


# [static] pass_to_pass
def test_zig_function_signatures():
    """Key Zig functions must have valid signatures (pass_to_pass)."""
    text = _read_zig()
    assert re.search(r'pub\s+(?:noinline\s+)?fn\s+computeChunks', text), "computeChunks must be a pub function"
    handler_body = _extract_handler_body(text)
    assert re.search(r'pub\s+fn\s+next', handler_body), "Handler.next must be a pub fn"


# [static] pass_to_pass
def test_repo_critical_files_exist():
    """Critical repo files must exist (pass_to_pass)."""
    critical_files = ["meta.json", "build.zig", "package.json", "tsconfig.json", "CONTRIBUTING.md"]
    for filename in critical_files:
        filepath = Path(REPO) / filename
        assert filepath.exists(), f"Critical file {filename} is missing"
        assert filepath.stat().st_size > 0, f"Critical file {filename} is empty"


# [static] pass_to_pass
def test_zig_no_double_semicolons():
    """Zig file must not contain double semicolons (pass_to_pass)."""
    text = _read_zig()
    double_semicolons = text.count(";;")
    assert double_semicolons == 0, f"Found {double_semicolons} double semicolons"


# [static] pass_to_pass
def test_tsconfig_structure():
    """tsconfig.json must have valid structure with required fields (pass_to_pass)."""
    import json
    filepath = Path(REPO) / "tsconfig.json"
    assert filepath.exists(), "tsconfig.json is missing"
    with open(filepath) as f:
        config = json.load(f)
    assert "compilerOptions" in config, "tsconfig.json missing compilerOptions"
    assert "references" in config, "tsconfig.json missing references field"
    refs = config["references"]
    assert isinstance(refs, list), "references should be a list"
    assert len(refs) > 0, "references should not be empty"


# [static] pass_to_pass
def test_prettierrc_valid():
    """.prettierrc must be valid JSON if it exists (pass_to_pass)."""
    import json
    filepath = Path(REPO) / ".prettierrc"
    if filepath.exists():
        try:
            with open(filepath) as f:
                json.load(f)
        except json.JSONDecodeError as e:
            assert False, f".prettierrc is not valid JSON: {e}"


# [repo_tests] pass_to_pass
def test_zig_computeChunks_file_exists():
    """computeChunks.zig must exist (verified via subprocess) (pass_to_pass)."""
    r = subprocess.run(
        ["ls", "-la", f"{REPO}/src/bundler/linker_context/computeChunks.zig"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"computeChunks.zig not found:\n{r.stderr}"
    assert "computeChunks.zig" in r.stdout, "computeChunks.zig not in output"


# [repo_tests] pass_to_pass
def test_repo_find_critical_files():
    """Critical repo files must exist (verified via find command) (pass_to_pass)."""
    critical_files = ["meta.json", "build.zig", "package.json", "tsconfig.json"]
    for filename in critical_files:
        r = subprocess.run(
            ["find", REPO, "-maxdepth", "1", "-name", filename],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"find command failed for {filename}"
        assert filename in r.stdout, f"Critical file {filename} not found"


# [repo_tests] pass_to_pass
def test_python_syntax_valid():
    """Repo Python scripts must have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["find", f"{REPO}/scripts", "-name", "*.py", "-type", "f"],
        capture_output=True, text=True, timeout=30,
    )
    if r.stdout.strip():
        for pyfile in r.stdout.strip().split("\n"):
            r2 = subprocess.run(
                ["python3", "-m", "py_compile", pyfile],
                capture_output=True, text=True, timeout=30,
            )
            assert r2.returncode == 0, f"Python syntax error in {pyfile}: {r2.stderr}"


# [repo_tests] pass_to_pass — Prettier check on CI workflow files
def test_repo_prettier_workflow_files():
    """CI workflow files must pass Prettier formatting (pass_to_pass)."""
    workflow_files = [
        ".github/workflows/lint.yml",
        ".github/workflows/format.yml",
    ]
    existing = [f for f in workflow_files if (Path(REPO) / f).exists()]
    if existing:
        r = subprocess.run(
            ["npx", "prettier", "--check"] + existing,
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Prettier check failed for workflow files:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Prettier check on package files
def test_repo_prettier_packages():
    """Package json files must pass Prettier formatting (pass_to_pass)."""
    package_files = [
        "packages/bun-types/package.json",
    ]
    existing = [f for f in package_files if (Path(REPO) / f).exists()]
    if existing:
        r = subprocess.run(
            ["npx", "prettier", "--check"] + existing,
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert r.returncode == 0, f"Prettier check failed for packages:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Python syntax validation for repo scripts
def test_repo_python_syntax_misctools():
    """Python files in misctools must have valid syntax (pass_to_pass)."""
    py_files = [
        "misctools/gdb/zig_gdb_pretty_printers.py",
        "misctools/gdb/std_gdb_pretty_printers.py",
    ]
    for pyfile in py_files:
        fpath = Path(REPO) / pyfile
        if fpath.exists():
            r = subprocess.run(
                ["python3", "-m", "py_compile", str(fpath)],
                capture_output=True, text=True, timeout=30,
            )
            assert r.returncode == 0, f"Python syntax error in {pyfile}: {r.stderr}"


# [repo_tests] pass_to_pass — Python syntax validation for test scripts
def test_repo_python_syntax_tests():
    """Python files in test directory must have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["find", f"{REPO}/test", "-name", "*.py", "-type", "f"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode == 0 and r.stdout.strip():
        for pyfile in r.stdout.strip().split("\n")[:5]:
            r2 = subprocess.run(
                ["python3", "-m", "py_compile", pyfile],
                capture_output=True, text=True, timeout=30,
            )
            assert r2.returncode == 0, f"Python syntax error in {pyfile}: {r2.stderr}"


# [repo_tests] pass_to_pass — oxlint basic check on bundler directory
def test_repo_oxlint_bundler():
    """Bundler JavaScript files must pass basic oxlint check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "oxlint", f"{REPO}/src/js/bundler"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint check failed for bundler:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — All JSON files must be valid
def test_repo_all_json_valid():
    """All JSON config files must be valid (pass_to_pass)."""
    json_files = [
        "package.json",
        "tsconfig.json",
        "meta.json",
        ".prettierrc",
    ]
    for json_file in json_files:
        fpath = Path(REPO) / json_file
        if fpath.exists():
            r = subprocess.run(
                ["python3", "-c", f"import json; json.load(open('{fpath}')); print('VALID')"],
                capture_output=True, text=True, timeout=30,
            )
            assert r.returncode == 0, f"JSON validation failed for {json_file}: {r.stderr}"


# ---------------------------------------------------------------------------
# NEW P2P TESTS ADDED DURING ENRICHMENT
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Bun banned words check
def test_repo_banned_words():
    """Repo must not contain banned words/patterns (pass_to_pass).

    This runs the repo's banned words check which validates that:
    - No undefined behavior patterns like ' != undefined' or ' == undefined'
    - No prohibited std APIs like std.fs, std.debug.assert, std.log
    - No catch bun.outOfMemory() patterns (should use bun.handleOom)
    """
    r = subprocess.run(
        "curl -fsSL https://bun.sh/install | bash >/dev/null 2>&1 && "
        "export PATH=\"/root/.bun/bin:$PATH\" && "
        "cd /workspace/bun && "
        "bun install >/dev/null 2>&1 && "
        "bun run banned",
        capture_output=True, text=True, timeout=180, shell=True,
    )
    assert r.returncode == 0, f"Banned words check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Bun glob-sources script
def test_repo_glob_sources():
    """Glob sources script must run successfully (pass_to_pass).

    This script scans all source files and generates the Sources.json
    file used by the build system. It must complete without errors.
    """
    r = subprocess.run(
        "curl -fsSL https://bun.sh/install | bash >/dev/null 2>&1 && "
        "export PATH=\"/root/.bun/bin:$PATH\" && "
        "cd /workspace/bun && "
        "bun install >/dev/null 2>&1 && "
        "bun scripts/glob-sources.mjs",
        capture_output=True, text=True, timeout=120, shell=True,
    )
    assert r.returncode == 0, f"glob-sources failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Git repository clean state
def _disabled_test_repo_git_clean():
    """Git repository must be in a clean state (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    lines = r.stdout.strip().split("\n") if r.stdout.strip() else []
    modified = [l for l in lines if l and not l.startswith("?")]
    assert len(modified) == 0, f"Git repo has uncommitted changes:\n{r.stdout}"


# [repo_tests] pass_to_pass — TypeScript typecheck command runs
def test_repo_test_typecheck():
    """TypeScript typecheck command must run without crashing (pass_to_pass).

    This verifies the typecheck infrastructure is in place. The repo's
    test directory may have known type issues, but the command should run.
    """
    r = subprocess.run(
        "curl -fsSL https://bun.sh/install | bash >/dev/null 2>&1 && "
        "export PATH=\"/root/.bun/bin:$PATH\" && "
        "cd /workspace/bun && "
        "bun install >/dev/null 2>&1 && "
        "cd test && timeout 60 bun run typecheck 2>&1 | head -30",
        capture_output=True, text=True, timeout=120, shell=True,
    )
    # Command should run and produce output (may have type errors, but not crash)
    assert "tsc" in r.stdout or "error TS" in r.stdout or r.returncode in [0, 1, 2],         f"Typecheck command did not run properly:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Bun test harness check (internal tests)
def test_repo_bun_test_internal():
    """Bun internal tests must pass (pass_to_pass).

    Runs a quick sanity check using Bun's test runner on a small
    internal test file to verify the test infrastructure works.
    """
    r = subprocess.run(
        "curl -fsSL https://bun.sh/install | bash >/dev/null 2>&1 && "
        "export PATH=\"/root/.bun/bin:$PATH\" && "
        "cd /workspace/bun && "
        "bun install >/dev/null 2>&1 && "
        "bun test test/internal/ban-words.test.ts 2>&1 | tail -20",
        capture_output=True, text=True, timeout=180, shell=True,
    )
    assert r.returncode == 0, f"Bun internal test failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
    assert "fail" not in r.stdout.lower() or "0 fail" in r.stdout.lower(), \
        f"Tests had failures:\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass — Verify bundler test file exists and is valid TS
# [repo_tests] pass_to_pass — Verify bundler CSS test file exists
def test_repo_bundler_css_test_exists():
    """Bundler CSS test file must exist and have valid syntax (pass_to_pass).

    Verifies the CSS bundler test infrastructure is present.
    """
    css_test = Path(REPO) / "test/bundler/css/css-modules.test.ts"
    assert css_test.exists(), "Bundler CSS test file must exist"

    # Check file has content and imports
    content = css_test.read_text()
    assert "import" in content, "CSS test file should have imports"
    assert "test" in content.lower() or "describe" in content.lower() or "it" in content.lower(),         "CSS test file should contain test constructs"

