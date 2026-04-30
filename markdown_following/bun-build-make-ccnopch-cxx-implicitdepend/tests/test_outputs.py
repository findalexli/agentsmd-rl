"""
Task: bun-build-make-ccnopch-cxx-implicitdepend
Repo: oven-sh/bun @ 485ec522a22b469b336aece8276b507a71665a87
PR:   28858

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_cc_implicit_dep_outputs():
    """cc() calls in compileC pass depOutputs as implicitInputs, not orderOnlyInputs.

    Verifies that C compilation nodes have library outputs (depOutputs) as
    implicit dependencies, triggering recompilation when dep libraries are rebuilt.
    Uses subprocess to analyze the build script structure.
    """
    r = subprocess.run(
        ["python3", "-c", """
import re
from pathlib import Path

src = Path("/workspace/bun/scripts/build/bun.ts").read_text()

# Find the cc() call in the C compilation section (compileC function)
# Look for cc(n, cfg, ...) call with its options
cc_call_match = re.search(r'compileC.*?cc\\(n,\\s*cfg.*?\\}\\)?;', src, re.DOTALL)
assert cc_call_match, "Could not find cc() call in compileC"
cc_context = cc_call_match.group(0)

# The cc() call must have implicitInputs that references dep outputs
# (library files that serve as rebuild signals)
has_implicit_deps = bool(re.search(r'implicitInputs.*?dep', cc_context, re.DOTALL | re.IGNORECASE))
assert has_implicit_deps, (
    f"cc() call must use implicitInputs for dep outputs to trigger "
    f"recompilation when dependencies are rebuilt. Found: {cc_context}"
)

# Verify dep outputs are NOT in orderOnlyInputs for the cc call
# (codegen/headers may be order-only, but dep library outputs must not be)
order_only_match = re.search(r'orderOnlyInputs\\s*[:=]\\s*(\\S+)', cc_context)
if order_only_match:
    order_only_value = order_only_match.group(1)
    # Should reference codegen, not dep outputs
    assert 'depOutput' not in order_only_value and 'depOrderOnly' not in order_only_value, (
        f"cc() orderOnlyInputs must not contain dep outputs: {order_only_value}"
    )

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_nopch_cxx_implicit_dep_outputs():
    """No-PCH cxx path passes depOutputs as implicitInputs.

    Verifies that when PCH is disabled (e.g., on Windows), the cxx() compilation
    path uses implicit dependencies for dep outputs, not just order-only.
    """
    r = subprocess.run(
        ["python3", "-c", """
import re
from pathlib import Path

src = Path("/workspace/bun/scripts/build/bun.ts").read_text()

# Find the no-PCH else branch: the else block that sets up deps when PCH is disabled
# This is the code path for Windows where PCH is not used
else_match = re.search(
    r'\\}\\s*else\\s*\\{([^}]*?(?:orderOnlyInputs|implicitInputs)[^}]*)\\}',
    src
)
assert else_match, "Could not find no-PCH else branch in bun.ts"
else_body = else_match.group(1)

# The else branch must set implicitInputs for dep outputs
has_implicit = bool(re.search(r'implicitInputs', else_body))
assert has_implicit, (
    f"No-PCH else branch must set implicitInputs for dep outputs "
    f"to trigger recompilation. Found: {else_body}"
)

# implicitInputs must reference dep outputs (not just codegen)
implicit_match = re.search(r'implicitInputs\\s*=\\s*(\\S+)', else_body)
assert implicit_match, f"Could not find implicitInputs assignment in: {else_body}"
implicit_value = implicit_match.group(1)
assert 'dep' in implicit_value.lower() or 'Dep' in implicit_value or 'output' in implicit_value.lower(), (
    f"implicitInputs must reference dep outputs, got: {implicit_value}"
)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_codegen_separated_from_dep_outputs():
    """depOutputs and codegen headers are in separate dependency lists.

    Verifies the build graph separates library outputs (implicit deps)
    from codegen headers (order-only deps) — they must not be combined
    into a single variable used for one dependency type.
    """
    r = subprocess.run(
        ["python3", "-c", """
import re
from pathlib import Path

src = Path("/workspace/bun/scripts/build/bun.ts").read_text()

# Check that depOutputs and codegen.cppAll are NOT combined into a single
# array spread (e.g. [...depOutputs, ...codegen.cppAll] as one variable)
combined_pattern = re.search(
    r'\\[\\s*\\.\\.\\.depOutputs\\s*,\\s*\\.\\.\\.codegen\\.cppAll\\s*\\]',
    src
)
assert not combined_pattern, (
    "depOutputs and codegen.cppAll must NOT be combined into a single variable. "
    "They serve different dependency purposes: dep outputs are implicit deps "
    "(rebuild triggers) while codegen headers are order-only."
)

# Verify that codegen headers are used as order-only somewhere in compile section
compile_section = src[src.find('Step 6'):] if 'Step 6' in src else src
has_codegen_order_only = bool(re.search(r'orderOnlyInputs.*codegen', compile_section, re.DOTALL))
assert has_codegen_order_only, (
    "Codegen headers must be used as orderOnlyInputs in the compile section"
)

# Verify that dep outputs are used as implicit inputs somewhere in compile section
has_dep_implicit = bool(re.search(r'implicitInputs.*dep', compile_section, re.DOTALL | re.IGNORECASE))
assert has_dep_implicit, (
    "Dep outputs must be used as implicitInputs in the compile section"
)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# -----------------------------------------------------------------------------
# Fail-to-pass (agent_config) — CLAUDE.md documentation must match code
# -----------------------------------------------------------------------------

def test_claude_md_dep_strategy_updated():
    """CLAUDE.md Gotchas documents the corrected dependency strategy.

    Verifies CLAUDE.md reflects the fix:
    - Old incorrect text about "cxx needs order-only dep on depOutputs" is removed
    - New text documents that cc/PCH/no-PCH cxx all need implicit deps on depOutputs
    """
    src = Path(f"{REPO}/scripts/build/CLAUDE.md").read_text()

    # Check that old incorrect guidance is gone
    has_old = bool(re.search(r"cxx needs order-only dep on.*depOutputs", src, re.IGNORECASE))
    assert not has_old, (
        "CLAUDE.md still contains the old incorrect guidance "
        "'cxx needs order-only dep on depOutputs'"
    )

    # Check for unified implicit guidance mentioning PCH, cc, and cxx
    has_implicit = bool(
        re.search(r"PCH.*cc.*cxx.*implicit", src, re.IGNORECASE) or
        re.search(r"PCH.*cc.*and.*no-PCH cxx.*implicit", src, re.IGNORECASE) or
        re.search(r"cc.*cxx.*need implicit dep", src, re.IGNORECASE)
    )
    assert has_implicit, (
        "CLAUDE.md must contain unified guidance stating PCH, cc, and cxx "
        "all need implicit deps on depOutputs"
    )

    # Check Gotchas section specifically has all three mentioned with implicit
    gotchas_match = re.search(r"## Gotchas([\s\S]*?)(?=^#{1,2} |\Z)", src, re.MULTILINE)
    assert gotchas_match, "CLAUDE.md must have a ## Gotchas section"
    gotchas_section = gotchas_match.group(1)
    assert re.search(r"PCH", gotchas_section), "Gotchas must mention PCH"
    assert re.search(r"cc", gotchas_section), "Gotchas must mention cc"
    assert re.search(r"cxx", gotchas_section), "Gotchas must mention cxx"
    assert re.search(r"implicit", gotchas_section), "Gotchas must mention implicit deps"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# -----------------------------------------------------------------------------

def test_compile_opts_has_both_input_types():
    """compile.ts CompileOpts interface retains both implicitInputs and orderOnlyInputs."""
    compile_ts = Path(f"{REPO}/scripts/build/compile.ts").read_text()
    assert "implicitInputs" in compile_ts, "CompileOpts must have implicitInputs field"
    assert "orderOnlyInputs" in compile_ts, "CompileOpts must have orderOnlyInputs field"


def test_bun_ts_pch_implicit_deps():
    """PCH still uses implicit deps on depOutputs (unchanged across base and fix)."""
    bun_ts = Path(f"{REPO}/scripts/build/bun.ts").read_text()
    assert "PCH" in bun_ts, "bun.ts must reference PCH"
    assert (
        "implicit dep" in bun_ts or "IMPLICIT dep" in bun_ts or "implicit deps" in bun_ts
    ), "bun.ts must document PCH's implicit dep behavior"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo's own CI/CD checks
# -----------------------------------------------------------------------------

def test_repo_editorconfig_compliance():
    """Build scripts comply with EditorConfig (pass_to_pass)."""
    build_dir = Path(f"{REPO}/scripts/build")
    ts_files = list(build_dir.glob("*.ts"))

    issues = []
    for f in ts_files:
        content = f.read_bytes()
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as e:
            issues.append(f"{f.name}: Not valid UTF-8 ({e})")
            continue

        for i, line in enumerate(text.split("\n"), 1):
            if line.rstrip() != line:
                issues.append(f"{f.name}:{i}: Trailing whitespace")

        if text and not text.endswith("\n"):
            issues.append(f"{f.name}: Missing final newline")

        if "\r" in text:
            issues.append(f"{f.name}: Contains CR (Windows line endings)")

    if issues:
        assert False, "EditorConfig violations:\n" + "\n".join(issues[:20])


def test_repo_build_script_imports():
    """Build script imports reference existing files (pass_to_pass)."""
    build_dir = Path(f"{REPO}/scripts/build")
    ts_files = list(build_dir.glob("*.ts"))

    import_re = re.compile(r'import\s+.*?\s+from\s+[\'"](\.[^\'"]+)[\'"]|import\s+[\'"](\.[^\'"]+)[\'"]')

    missing = []
    for f in ts_files:
        text = f.read_text()
        for match in import_re.finditer(text):
            imp = match.group(1) or match.group(2)
            if imp:
                if imp.endswith(".ts") or imp.endswith(".mjs"):
                    target = f.parent / imp
                else:
                    target = f.parent / (imp + ".ts")

                if not target.exists():
                    missing.append(f"{f.name}: import '{imp}' -> {target} not found")

    if missing:
        assert False, "Missing import targets:\n" + "\n".join(missing[:20])


def _load_jsonc(content: str):
    """Parse JSONC (JSON with comments) by stripping comments."""
    lines = []
    for line in content.split("\n"):
        in_str = False
        escape = False
        result = []
        for char in line:
            if escape:
                result.append(char)
                escape = False
                continue
            if char == "\\":
                result.append(char)
                escape = True
                continue
            if char == '"' and not in_str:
                in_str = True
                result.append(char)
                continue
            if char == '"' and in_str:
                in_str = False
                result.append(char)
                continue
            if not in_str and char == "/" and len(result) > 0 and result[-1] == "/":
                result.pop()
                break
            result.append(char)
        lines.append("".join(result))
    content = "\n".join(lines)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    return json.loads(content)


def test_repo_json_configs_valid():
    """JSON configuration files are syntactically valid JSONC (pass_to_pass)."""
    files = [
        Path(f"{REPO}/tsconfig.json"),
        Path(f"{REPO}/tsconfig.base.json"),
        Path(f"{REPO}/.prettierrc"),
        Path(f"{REPO}/oxlint.json"),
        Path(f"{REPO}/scripts/build/tsconfig.json"),
    ]

    errors = []
    for f in files:
        try:
            content = f.read_text()
            _load_jsonc(content)
        except Exception as e:
            errors.append(f"{f.name}: {e}")

    if errors:
        assert False, "JSONC validation failed:\n" + "\n".join(errors)


def test_repo_git_integrity():
    """Git repository is in a valid state (pass_to_pass)."""
    r = subprocess.run(
        ["git", "fsck", "--full", "--strict"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git fsck failed:\n{r.stderr}"


def test_repo_shell_scripts_syntax():
    """Shell scripts have valid syntax (pass_to_pass)."""
    shell_dir = Path(f"{REPO}/.buildkite")
    if not shell_dir.exists():
        return

    sh_files = list(shell_dir.rglob("*.sh"))
    errors = []

    for f in sh_files:
        r = subprocess.run(
            ["bash", "-n", str(f)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            errors.append(f"{f.name}: {r.stderr.strip()}")

    if errors:
        assert False, "Shell syntax errors:\n" + "\n".join(errors[:10])


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


def test_repo_claude_md_structure():
    """CLAUDE.md has expected sections (pass_to_pass)."""
    claude_md = Path(f"{REPO}/scripts/build/CLAUDE.md").read_text()

    assert "Ninja" in claude_md, "CLAUDE.md must reference Ninja"
    assert "implicit" in claude_md, "CLAUDE.md must document implicit inputs"
    assert "order-only" in claude_md, "CLAUDE.md must document order-only inputs"
    assert "PCH" in claude_md, "CLAUDE.md must document PCH"
    assert "depOutputs" in claude_md, "CLAUDE.md must reference depOutputs"


def test_repo_build_scripts_structure():
    """Build scripts have expected functions and interfaces (pass_to_pass)."""
    bun_ts = Path(f"{REPO}/scripts/build/bun.ts").read_text()
    compile_ts = Path(f"{REPO}/scripts/build/compile.ts").read_text()

    assert "compileC" in bun_ts, "bun.ts must have compileC function"
    assert "function cc(" in compile_ts or "const cc" in compile_ts, "compile.ts must have cc function"
    assert "interface CompileOpts" in compile_ts, "compile.ts must have CompileOpts interface"
    assert 'n.rule("cxx"' in compile_ts, "compile.ts must define cxx rule"
    assert 'n.rule("cc"' in compile_ts, "compile.ts must define cc rule"
    assert 'n.rule("pch"' in compile_ts, "compile.ts must define pch rule"


def test_repo_tsconfig_valid_jsonc():
    """TypeScript config files are syntactically valid JSONC (pass_to_pass)."""
    files = [
        Path(f"{REPO}/tsconfig.json"),
        Path(f"{REPO}/tsconfig.base.json"),
        Path(f"{REPO}/scripts/build/tsconfig.json"),
    ]

    errors = []
    for f in files:
        try:
            content = f.read_text()
            no_comments = re.sub(r'//.*$', "", content, flags=re.MULTILINE)
            no_comments = re.sub(r'/\*.*?\*/', "", no_comments, flags=re.DOTALL)
            json.loads(no_comments)
        except Exception as e:
            errors.append(f"{f.name}: {e}")

    if errors:
        assert False, "JSONC validation failed:\n" + "\n".join(errors)
