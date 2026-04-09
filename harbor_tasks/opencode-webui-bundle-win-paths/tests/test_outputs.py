"""
Task: opencode-webui-bundle-win-paths
Repo: anomalyco/opencode @ b7a06e193952a66a8efa07feb4e105f44bf7ea8b
PR:   #19337

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import functools
import os
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/opencode"
TARGET = "packages/opencode/script/build.ts"
SCRIPT_DIR = f"{REPO}/packages/opencode/script"
DIST = f"{REPO}/packages/app/dist"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_function_body() -> str:
    """Read createEmbeddedWebUIBundle from build.ts and return its source."""
    source = Path(f"{REPO}/{TARGET}").read_text()
    start = source.find("const createEmbeddedWebUIBundle")
    assert start != -1, "createEmbeddedWebUIBundle not found in build.ts"
    depth = 0
    end = start
    started = False
    for i in range(start, len(source)):
        if source[i] == "{":
            depth += 1
            started = True
        if source[i] == "}":
            depth -= 1
            if started and depth == 0:
                end = i + 1
                break
    return source[start:end]


@functools.lru_cache(maxsize=1)
def _run_bundle_function() -> str:
    """Extract createEmbeddedWebUIBundle, skip bun build, run it, return output."""
    # Create test dist files
    os.makedirs(f"{DIST}/assets/sub", exist_ok=True)
    Path(f"{DIST}/index.html").write_text("<html></html>")
    Path(f"{DIST}/assets/style.css").write_text("body{margin:0}")
    Path(f"{DIST}/assets/sub/deep.js").write_text("console.log('test')")
    Path(f"{DIST}/assets/logo.png").write_text("PNG_DATA")

    source = Path(f"{REPO}/{TARGET}").read_text()

    # Extract `dir` variable from outer scope
    dir_def = f'const dir = {SCRIPT_DIR!r}'
    for line in source.split("\n"):
        m = re.match(r"^(export\s+)?(const|let|var)\s+dir\s*=\s*(.+)$", line)
        if m:
            dir_def = (
                re.sub(r"^export\s+", "", line)
                .replace("import.meta.dirname", repr(SCRIPT_DIR))
                .replace("import.meta.filename", repr(f"{SCRIPT_DIR}/build.ts"))
            )
            break

    func = _extract_function_body()

    # Patch: skip bun build, replace import.meta references
    func = re.sub(r"await\s+\$`[^`]*`", "void 0", func)
    func = func.replace("import.meta.dirname", repr(SCRIPT_DIR))
    func = func.replace("import.meta.filename", repr(f"{SCRIPT_DIR}/build.ts"))

    runner = "\n".join([
        'import path from "path"',
        f'const __filename = {repr(f"{SCRIPT_DIR}/build.ts")}',
        f'const __dirname = {repr(SCRIPT_DIR)}',
        dir_def,
        "const $ = ((s, ...v) => Promise.resolve('')) as any",
        func,
        "const __result = await createEmbeddedWebUIBundle()",
        "console.log(__result)",
    ])

    runner_path = "/tmp/run_bundle_func.ts"
    Path(runner_path).write_text(runner)

    r = subprocess.run(
        ["bun", "run", runner_path],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"bun run failed:\n{r.stderr}"
    assert r.stdout.strip(), "Function produced empty output"
    return r.stdout.strip()


def _parse_imports(output: str) -> list[str]:
    """Extract import specifiers from the generated module."""
    specs = []
    for line in output.split("\n"):
        line = line.strip()
        if line.startswith("import "):
            m = re.search(r'from\s+("([^"]+)"|\'([^\']+)\')', line)
            if m:
                specs.append(m.group(2) or m.group(3))
    return specs


def _parse_export_keys(output: str) -> list[str]:
    """Extract export mapping keys from the generated module."""
    return re.findall(r'^\s*"([^"]+)"\s*:\s*file_\d+', output, re.MULTILINE)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_import_specifiers_relative():
    """Import specifiers must be relative paths (./... or ../...), not absolute."""
    output = _run_bundle_function()
    specs = _parse_imports(output)
    assert len(specs) >= 2, f"Expected at least 2 imports, got {len(specs)}"
    for spec in specs:
        assert spec.startswith("./") or spec.startswith("../"), (
            f"Non-relative import specifier: {spec}"
        )


# [pr_diff] fail_to_pass
def test_export_keys_sorted():
    """Export keys must be sorted alphabetically for deterministic output."""
    output = _run_bundle_function()
    keys = _parse_export_keys(output)
    assert len(keys) >= 2, f"Expected at least 2 export keys, got {len(keys)}"
    assert keys == sorted(keys), f"Keys not sorted: {keys}"


# [pr_diff] fail_to_pass
def test_backslash_normalization():
    """Source code must handle backslash-to-forward-slash normalization for Windows."""
    # AST-only because: running on Linux, Bun.Glob never produces backslash paths
    func = _extract_function_body()
    patterns = [
        r'replaceAll\s*\(\s*["\']\\\\["\']',  # Matches replaceAll("\\", ...) - two backslashes in source
        r'\.replace\s*\(\s*/[^/]*\\\\[^/]*/[gim]*\s*,',  # Matches .replace(/.../, ...)
        r'split\s*\(\s*["\']\\\\["\']\s*\).*?join',  # Matches split("\\").join(...)
        r'path\.posix\.',
        r'(toForwardSlash|normalizePath|normalizeSlash)\s*\(',
        r'\.replaceAll\s*\(\s*path\.sep',
        r'\.replace\s*\(\s*path\.sep',
    ]
    assert any(re.search(p, func, re.DOTALL) for p in patterns), (
        "No backslash normalization found in createEmbeddedWebUIBundle"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_all_dist_files_present():
    """All scanned dist files must appear in the generated module output."""
    output = _run_bundle_function()
    expected = ["index.html", "assets/style.css", "assets/sub/deep.js", "assets/logo.png"]
    for f in expected:
        assert f in output, f"Missing file in output: {f}"


# [pr_diff] pass_to_pass
def test_valid_module_structure():
    """Generated module must have import statements, export default, and type: file."""
    output = _run_bundle_function()
    assert re.search(r"^import\s+\w+\s+from\s+", output, re.MULTILINE), "No import statements"
    assert "export default" in output, "No export default"
    assert 'type: "file"' in output or "type: 'file'" in output, "No type: file annotation"


# [static] pass_to_pass
def test_not_stub():
    """Function body must have >= 5 meaningful statements (not a stub)."""
    func = _extract_function_body()
    body_lines = [
        l.strip() for l in func.split("\n")[1:-1]
        if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")
    ]
    assert len(body_lines) >= 5, f"Function body too small ({len(body_lines)} lines), likely a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:70 @ b7a06e193952a66a8efa07feb4e105f44bf7ea8b
def test_const_only():
    """Function body must use const only, no let/var (AGENTS.md line 70)."""
    func = _extract_function_body()
    body = "\n".join(func.split("\n")[1:-1])
    assert not re.search(r"\blet\b", body), "Function uses 'let' — prefer const (AGENTS.md:70)"
    assert not re.search(r"\bvar\b", body), "Function uses 'var' — prefer const (AGENTS.md:70)"


# [agent_config] pass_to_pass — AGENTS.md:17 @ b7a06e193952a66a8efa07feb4e105f44bf7ea8b
def test_no_imperative_loops():
    """Function must use functional array methods, not for/while loops (AGENTS.md line 17)."""
    # AST-only because: TypeScript source, structural style rule
    func = _extract_function_body()
    assert not re.search(r"\b(for|while)\s*\(", func), (
        "Function uses imperative loops — prefer map/filter/flatMap (AGENTS.md:17)"
    )


# [agent_config] pass_to_pass — AGENTS.md:13 @ b7a06e193952a66a8efa07feb4e105f44bf7ea8b
def test_no_any_type():
    """Function must not use the 'any' type (AGENTS.md line 13)."""
    # AST-only because: TypeScript type annotation, structural rule
    func = _extract_function_body()
    # Match ": any", "as any", "<any>" but not words containing "any" like "anyOf"
    assert not re.search(r"(?::\s*any\b|as\s+any\b|<any>)", func), (
        "Function uses 'any' type — avoid it (AGENTS.md:13)"
    )


# [agent_config] pass_to_pass — AGENTS.md:12 @ b7a06e193952a66a8efa07feb4e105f44bf7ea8b
def test_no_try_catch():
    """Function must not use try/catch (AGENTS.md line 12)."""
    # AST-only because: TypeScript source, structural style rule
    func = _extract_function_body()
    assert not re.search(r"\btry\s*\{", func), (
        "Function uses try/catch — avoid where possible (AGENTS.md:12)"
    )


# [agent_config] pass_to_pass — AGENTS.md:84 @ b7a06e193952a66a8efa07feb4e105f44bf7ea8b
def test_no_else_statements():
    """Function must not use else — prefer early returns (AGENTS.md line 84)."""
    # AST-only because: TypeScript source, structural style rule
    func = _extract_function_body()
    assert not re.search(r"\belse\b", func), (
        "Function uses 'else' — prefer early returns (AGENTS.md:84)"
    )


# [agent_config] pass_to_pass — AGENTS.md:15 @ b7a06e193952a66a8efa07feb4e105f44bf7ea8b
def test_uses_bun_glob_api():
    """Function must use Bun.Glob for file scanning — prefer Bun APIs over native fs (AGENTS.md line 15)."""
    # AST-only because: TypeScript source, API usage style rule
    func = _extract_function_body()
    assert re.search(r"\bBun\.Glob\b", func), (
        "Function does not use Bun.Glob — prefer Bun APIs when possible (AGENTS.md:15)"
    )


# ---------------------------------------------------------------------------
# Repo CI-derived pass_to_pass (repo_tests) — CI/CD gates that must pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — validates TypeScript can be parsed/bundled
def test_repo_typescript_syntax_valid():
    """Repo's TypeScript files must have valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "build", "--target=bun", "--external=*", TARGET],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript syntax error in {TARGET}:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — validates bun lockfile integrity
def test_repo_bun_lockfile_valid():
    """Repo's bun.lock must be valid and dependencies resolvable (pass_to_pass)."""
    # Check bun.lock exists and is valid JSON
    lock_path = os.path.join(REPO, "bun.lock")
    assert os.path.exists(lock_path), "bun.lock not found"

    # Verify bun can parse the lockfile by querying it
    r = subprocess.run(
        ["bun", "pm", "ls"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    # Command may fail due to missing workspace deps, but should not crash
    # A crash would indicate an invalid lockfile
    assert "error:" not in r.stderr.lower() or "cannot find module" in r.stderr.lower() or r.returncode == 0, (
        f"bun.lock appears invalid or corrupted: {r.stderr[-300:]}"
    )
