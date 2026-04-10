"""
Task: bun-build-make-ccnopch-cxx-implicitdepend
Repo: oven-sh/bun @ 485ec522a22b469b336aece8276b507a71665a87
PR:   28858

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cc_implicit_dep_outputs():
    """cc() calls in compileC pass depOutputs as implicitInputs, not orderOnlyInputs."""
    r = subprocess.run(
        ["python3", "-c", """
import re
src = open('/workspace/bun/scripts/build/bun.ts').read()

# Find the compileC lambda and the cc() call within it.
# On base: cc(n, cfg, src, { flags: cFlagsFull, orderOnlyInputs: depOrderOnly })
# On fix:  cc(n, cfg, src, { ..., implicitInputs: depOutputs, orderOnlyInputs: codegenOrderOnly })
m = re.search(r'const compileC.*?cc\\(n,.*?\\)', src, re.DOTALL)
assert m, "compileC function with cc() call not found in bun.ts"
cc_block = m.group()

# The cc() call must include implicitInputs referencing depOutputs
assert re.search(r'implicitInputs[:\\s]+depOutputs', cc_block), (
    "cc() must pass depOutputs as implicitInputs.\\n"
    f"Found in compileC: ...{cc_block[-200:]}"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_nopch_cxx_implicit_dep_outputs():
    """No-PCH cxx path in bun.ts sets opts.implicitInputs = depOutputs."""
    r = subprocess.run(
        ["python3", "-c", """
src = open('/workspace/bun/scripts/build/bun.ts').read()

# The no-PCH else branch must assign opts.implicitInputs = depOutputs.
# On base: only opts.orderOnlyInputs = depOrderOnly  (no implicitInputs)
# On fix:  opts.implicitInputs = depOutputs; opts.orderOnlyInputs = codegenOrderOnly
assert 'opts.implicitInputs = depOutputs' in src, (
    "No-PCH cxx path must set opts.implicitInputs = depOutputs"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_codegen_separated_from_dep_outputs():
    """depOutputs and codegen.cppAll are not combined into one order-only variable."""
    r = subprocess.run(
        ["python3", "-c", """
import re
src = open('/workspace/bun/scripts/build/bun.ts').read()

# On base: const depOrderOnly = [...depOutputs, ...codegen.cppAll]
# On fix:  const codegenOrderOnly = codegen.cppAll  (depOutputs NOT mixed in)
mixed = re.search(
    r'const\\s+\\w+\\s*=\\s*\\[.*?depOutputs.*?codegen\\.cppAll.*?\\]',
    src, re.DOTALL
)
assert not mixed, (
    "depOutputs must not be combined with codegen.cppAll in one array. "
    f"Found: {mixed.group()[:120] if mixed else ''}"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — CLAUDE.md documentation must match code
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — scripts/build/CLAUDE.md:229 @ 485ec522
def test_claude_md_dep_strategy_updated():
    """CLAUDE.md Gotchas documents cc and no-PCH cxx using implicit deps on depOutputs."""
    r = subprocess.run(
        ["python3", "-c", """
import re
src = open('/workspace/bun/scripts/build/CLAUDE.md').read()

# Base has: "cxx needs order-only dep on `depOutputs`"
# Fix has:  "PCH, cc, and no-PCH cxx need implicit dep on `depOutputs`"
old_guidance = re.search(r'cxx needs order-only dep on.*depOutputs', src)
assert not old_guidance, (
    "CLAUDE.md must NOT say 'cxx needs order-only dep on depOutputs' -- "
    "the fix changes cc/no-PCH cxx to use implicit deps"
)

# Verify the new guidance mentions cc needing implicit dep
assert re.search(r'cc.*need implicit dep', src), (
    "CLAUDE.md Gotchas must state that cc needs implicit dep on depOutputs"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compile_opts_has_both_input_types():
    """compile.ts CompileOpts interface retains both implicitInputs and orderOnlyInputs."""
    src = Path(f"{REPO}/scripts/build/compile.ts").read_text()
    assert "implicitInputs" in src, "CompileOpts must have implicitInputs field"
    assert "orderOnlyInputs" in src, "CompileOpts must have orderOnlyInputs field"


# [static] pass_to_pass
def test_bun_ts_pch_implicit_deps():
    """PCH still uses implicit deps on depOutputs (unchanged across base and fix)."""
    src = Path(f"{REPO}/scripts/build/bun.ts").read_text()
    assert "PCH" in src and "implicit dep" in src, \
        "bun.ts must reference PCH's implicit dep on depOutputs in comments"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's own CI/CD checks
# These ensure the fix doesn't break existing repo functionality
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — EditorConfig compliance check
def test_repo_editorconfig_compliance():
    """Build scripts comply with EditorConfig (pass_to_pass).

    Verifies that scripts/build/*.ts files follow basic EditorConfig rules:
    - UTF-8 encoding
    - LF line endings
    - No trailing whitespace
    - Final newline present
    """
    build_dir = Path(f"{REPO}/scripts/build")
    ts_files = list(build_dir.glob("*.ts"))

    issues = []
    for f in ts_files:
        content = f.read_bytes()

        # Check UTF-8 encoding
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError as e:
            issues.append(f"{f.name}: Not valid UTF-8 ({e})")
            continue

        # Check no trailing whitespace
        for i, line in enumerate(text.split('\n'), 1):
            if line.rstrip() != line:
                issues.append(f"{f.name}:{i}: Trailing whitespace")

        # Check final newline
        if text and not text.endswith('\n'):
            issues.append(f"{f.name}: Missing final newline")

        # Check no CR (Windows line endings)
        if '\r' in text:
            issues.append(f"{f.name}: Contains CR (Windows line endings)")

    if issues:
        assert False, "EditorConfig violations:\n" + "\n".join(issues[:20])


# [repo_tests] pass_to_pass — Build script import integrity
def test_repo_build_script_imports():
    """Build script imports reference existing files (pass_to_pass).

    Parses import statements in scripts/build/*.ts and verifies
    that relative imports point to files that exist.
    """
    import re

    build_dir = Path(f"{REPO}/scripts/build")
    ts_files = list(build_dir.glob("*.ts"))

    import_re = re.compile(r"import\s+.*?\s+from\s+['\"](\.[^'\"]+)['\"]|import\s+['\"](\.[^'\"]+)['\"]")

    missing = []
    for f in ts_files:
        text = f.read_text()
        for match in import_re.finditer(text):
            imp = match.group(1) or match.group(2)
            if imp:
                # Resolve relative to the file
                if imp.endswith('.ts'):
                    target = f.parent / imp
                else:
                    target = f.parent / (imp + '.ts')

                if not target.exists():
                    missing.append(f"{f.name}: import '{imp}' -> {target} not found")

    if missing:
        assert False, "Missing import targets:\n" + "\n".join(missing[:20])


# [repo_tests] pass_to_pass — JSON config files are valid
def test_repo_json_configs_valid():
    """JSON configuration files are syntactically valid (pass_to_pass)."""
    import json

    json_files = [
        f"{REPO}/tsconfig.json",
        f"{REPO}/tsconfig.base.json",
        f"{REPO}/.prettierrc",
        f"{REPO}/oxlint.json",
        f"{REPO}/scripts/build/tsconfig.json",
    ]

    errors = []
    for path_str in json_files:
        path = Path(path_str)
        if path.exists():
            try:
                json.loads(path.read_text())
            except json.JSONDecodeError as e:
                errors.append(f"{path.name}: {e}")

    if errors:
        assert False, "Invalid JSON files:\n" + "\n".join(errors)


# [repo_tests] pass_to_pass — Git repository integrity
def test_repo_git_integrity():
    """Git repository is in a valid state (pass_to_pass).

    Runs git fsck to verify the repository is not corrupted.
    """
    r = subprocess.run(
        ["git", "fsck", "--full", "--strict"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Git fsck failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — Shell script syntax check
def test_repo_shell_scripts_syntax():
    """Shell scripts have valid syntax (pass_to_pass).

    Uses bash -n to check syntax of shell scripts in .buildkite/.
    """
    shell_dir = Path(f"{REPO}/.buildkite")
    if not shell_dir.exists():
        return

    sh_files = list(shell_dir.rglob("*.sh"))
    errors = []

    for f in sh_files:
        r = subprocess.run(
            ["bash", "-n", str(f)],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            errors.append(f"{f.name}: {r.stderr.strip()}")

    if errors:
        assert False, "Shell syntax errors:\n" + "\n".join(errors[:10])


# [repo_tests] pass_to_pass — Build scripts exist and have content
def test_repo_build_scripts_exist():
    """Build scripts exist and are non-empty (pass_to_pass)."""
    bun_ts = Path(f"{REPO}/scripts/build/bun.ts")
    compile_ts = Path(f"{REPO}/scripts/build/compile.ts")
    claude_md = Path(f"{REPO}/scripts/build/CLAUDE.md")

    assert bun_ts.exists(), "bun.ts must exist"
    assert compile_ts.exists(), "compile.ts must exist"
    assert claude_md.exists(), "CLAUDE.md must exist"

    assert len(bun_ts.read_text()) > 1000, "bun.ts must have substantial content"
    assert len(compile_ts.read_text()) > 1000, "compile.ts must have substantial content"
    assert len(claude_md.read_text()) > 500, "CLAUDE.md must have substantial content"


# [repo_tests] pass_to_pass — CLAUDE.md documentation structure
def test_repo_claude_md_structure():
    """CLAUDE.md has expected sections (pass_to_pass)."""
    claude_md = Path(f"{REPO}/scripts/build/CLAUDE.md").read_text()

    # Check for key documentation concepts that should exist in any version
    assert "Ninja" in claude_md, "CLAUDE.md must reference Ninja"
    assert "implicit" in claude_md, "CLAUDE.md must document implicit inputs"
    assert "order-only" in claude_md, "CLAUDE.md must document order-only inputs"
    assert "PCH" in claude_md, "CLAUDE.md must document PCH"
    assert "depOutputs" in claude_md, "CLAUDE.md must reference depOutputs"


# [repo_tests] pass_to_pass — Build scripts have key functions
def test_repo_build_scripts_structure():
    """Build scripts have expected functions and interfaces (pass_to_pass)."""
    bun_ts = Path(f"{REPO}/scripts/build/bun.ts").read_text()
    compile_ts = Path(f"{REPO}/scripts/build/compile.ts").read_text()

    # bun.ts should have key functions
    assert "compileC" in bun_ts, "bun.ts must have compileC function"
    assert "function cc(" in compile_ts or "const cc" in compile_ts, "compile.ts must have cc function"
    assert "interface CompileOpts" in compile_ts, "compile.ts must have CompileOpts interface"

    # compile.ts should have key rules
    assert 'n.rule("cxx"' in compile_ts, "compile.ts must define cxx rule"
    assert 'n.rule("cc"' in compile_ts, "compile.ts must define cc rule"
    assert 'n.rule("pch"' in compile_ts, "compile.ts must define pch rule"
