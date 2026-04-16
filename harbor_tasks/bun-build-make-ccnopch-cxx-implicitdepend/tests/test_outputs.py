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


def _run_ts_test(ts_code: str, timeout: int = 60) -> dict:
    """Execute TypeScript code and return parsed JSON output.
    
    Tries multiple TypeScript runners (bun, deno, node/tsx).
    """
    import tempfile
    import os

    # Wrap user code with result extraction
    wrapped = ts_code + '\nconsole.log("RESULT:" + JSON.stringify(result));'

    # Write to temp file in the repo so imports work
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".ts", delete=False, dir=f"{REPO}/scripts/build"
    ) as f:
        f.write(wrapped)
        ts_path = f.name

    try:
        # Try bun first, then deno, then npx tsx
        runners = [
            ["bun", "run", ts_path],
            ["deno", "run", "--allow-all", ts_path],
            ["npx", "tsx", ts_path],
        ]

        for runner in runners:
            try:
                result = subprocess.run(
                    runner,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=REPO,
                )
                if result.returncode == 0:
                    # Extract RESULT: line
                    for line in result.stdout.strip().split("\n"):
                        if line.startswith("RESULT:"):
                            return json.loads(line[7:])
                    # If no RESULT line, try parsing whole output
                    try:
                        return json.loads(result.stdout.strip())
                    except:
                        pass
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

        raise RuntimeError(f"No TypeScript runner available")

    finally:
        try:
            os.unlink(ts_path)
        except:
            pass


def _get_compile_c_behavior() -> dict:
    """Execute compileC and return the build node configuration for cc calls."""
    ts_code = '''
import { Ninja } from "./ninja.ts";
import { emitBun } from "./bun.ts";
import { registerCompileRules } from "./compile.ts";

class RecordingNinja extends Ninja {
  buildNodes: any[] = [];
  constructor(opts: any) {
    super(opts);
  }
  build(node: any): void {
    this.buildNodes.push({
      rule: node.rule,
      inputs: node.inputs ?? [],
      implicitInputs: node.implicitInputs ?? [],
      orderOnlyInputs: node.orderOnlyInputs ?? [],
    });
    super.build(node);
  }
}

const cfg = {
  cwd: "/workspace/bun",
  buildDir: "/workspace/bun/build",
  mode: "cpp-only",
  os: "linux",
  arch: "x64",
  linux: true, darwin: false, windows: false,
  webkit: "local", staticLibatomic: false,
  cc: "clang", cxx: "clang++", ar: "llvm-ar",
  jsRuntime: "node", libPrefix: "lib", libSuffix: ".a",
};

const n = new RecordingNinja({ buildDir: cfg.buildDir });
registerCompileRules(n, cfg as any);

const sources = { cpp: [], c: ["/workspace/bun/src/test.c"], zig: [] };
emitBun(n, cfg as any, sources as any);

const ccNodes = n.buildNodes.filter((n: any) => n.rule === "cc");
const result = {
  ccCount: ccNodes.length,
  ccNodes: ccNodes.map((n: any) => ({
    implicitInputs: n.implicitInputs,
    orderOnlyInputs: n.orderOnlyInputs,
  })),
  hasImplicitDepOutputs: ccNodes.some((n: any) =>
    n.implicitInputs.some((i: string) => i.includes(".a"))
  ),
  hasOrderOnlyCodegen: ccNodes.some((n: any) =>
    n.orderOnlyInputs.some((i: string) => i.includes("codegen") || i.includes(".h"))
  ),
};
'''
    return _run_ts_test(ts_code)


def _get_nopch_cxx_behavior() -> dict:
    """Execute no-PCH cxx path and return build node configuration."""
    ts_code = '''
import { Ninja } from "./ninja.ts";
import { emitBun } from "./bun.ts";
import { registerCompileRules } from "./compile.ts";

class RecordingNinja extends Ninja {
  buildNodes: any[] = [];
  constructor(opts: any) {
    super(opts);
  }
  build(node: any): void {
    this.buildNodes.push({
      rule: node.rule,
      inputs: node.inputs ?? [],
      implicitInputs: node.implicitInputs ?? [],
      orderOnlyInputs: node.orderOnlyInputs ?? [],
      vars: node.vars ?? {},
    });
    super.build(node);
  }
}

const cfg = {
  cwd: "/workspace/bun",
  buildDir: "/workspace/bun/build",
  mode: "cpp-only",
  os: "win",
  arch: "x64",
  linux: false, darwin: false, windows: true,
  webkit: "local", staticLibatomic: false,
  cc: "clang-cl", cxx: "clang-cl", ar: "llvm-lib",
  jsRuntime: "node", libPrefix: "", libSuffix: ".lib",
};

const n = new RecordingNinja({ buildDir: cfg.buildDir });
registerCompileRules(n, cfg as any);

const sources = { cpp: ["/workspace/bun/src/test.cpp"], c: [], zig: [] };
emitBun(n, cfg as any, sources as any);

const cxxNodes = n.buildNodes.filter((n: any) =>
  n.rule === "cxx" && !n.vars?.pch_file
);

const result = {
  cxxCount: cxxNodes.length,
  cxxNodes: cxxNodes.map((n: any) => ({
    implicitInputs: n.implicitInputs,
    orderOnlyInputs: n.orderOnlyInputs,
  })),
  hasImplicitDepOutputs: cxxNodes.some((n: any) =>
    n.implicitInputs.some((i: string) => i.includes(".lib") || i.includes(".a"))
  ),
  hasOrderOnlyCodegen: cxxNodes.some((n: any) =>
    n.orderOnlyInputs.some((i: string) => i.includes("codegen") || i.includes(".h"))
  ),
};
'''
    return _run_ts_test(ts_code)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_cc_implicit_dep_outputs():
    """cc() calls in compileC pass depOutputs as implicitInputs, not orderOnlyInputs.

    This test executes the emitBun code path and verifies that C compilation
    nodes have library outputs (.a files) in their implicitInputs, triggering
    recompilation when dependencies are rebuilt.
    """
    result = _get_compile_c_behavior()

    assert result.get("ccCount", 0) > 0, "Must have at least one cc build node"
    assert result.get("hasImplicitDepOutputs") is True, (
        f"cc() calls must have library outputs (.a files) in implicitInputs. Result: {result}"
    )


def test_nopch_cxx_implicit_dep_outputs():
    """No-PCH cxx path passes depOutputs as implicitInputs.

    Verifies that when PCH is disabled (e.g., on Windows), cxx() calls
    receive library outputs as implicitInputs, triggering recompilation
    when dependencies are rebuilt.
    """
    result = _get_nopch_cxx_behavior()

    if result.get("cxxCount", 0) == 0:
        return  # No no-PCH nodes to test

    assert result.get("hasImplicitDepOutputs") is True, (
        f"No-PCH cxx() calls must have library outputs in implicitInputs. Result: {result}"
    )


def test_codegen_separated_from_dep_outputs():
    """depOutputs and codegen headers are in separate dependency lists.

    Verifies the build graph separates library outputs (implicit deps)
    from codegen headers (order-only deps).
    """
    c_result = _get_compile_c_behavior()

    assert c_result.get("hasImplicitDepOutputs") is True, (
        f"Must have library outputs as implicit deps. Result: {c_result}"
    )
    assert c_result.get("hasOrderOnlyCodegen") is True, (
        f"Must have codegen headers as order-only deps. Result: {c_result}"
    )

    try:
        cxx_result = _get_nopch_cxx_behavior()
        if cxx_result.get("cxxCount", 0) > 0:
            assert cxx_result.get("hasImplicitDepOutputs") is True, (
                f"No-PCH cxx must have library outputs as implicit deps. Result: {cxx_result}"
            )
            assert cxx_result.get("hasOrderOnlyCodegen") is True, (
                f"No-PCH cxx must have codegen headers as order-only deps. Result: {cxx_result}"
            )
    except Exception:
        pass


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

    # Check for unified implicit guidance
    has_implicit = bool(
        re.search(r"PCH.*cc.*cxx.*implicit", src, re.IGNORECASE) or
        re.search(r"PCH.*cc.*and.*no-PCH cxx.*implicit", src, re.IGNORECASE) or
        re.search(r"cc.*cxx.*need implicit dep", src, re.IGNORECASE)
    )

    # Check Gotchas section has all three
    gotchas_match = re.search(r"Gotchas([\s\S]*?)(?=^#{1,2} |\Z)", src, re.MULTILINE)
    gotchas_section = gotchas_match.group(1) if gotchas_match else ""
    has_unified = (
        bool(re.search(r"PCH", gotchas_section)) and
        bool(re.search(r"cc", gotchas_section)) and
        bool(re.search(r"cxx", gotchas_section)) and
        bool(re.search(r"implicit", gotchas_section))
    )

    updated = not has_old and has_implicit and has_unified
    assert updated, (
        f"CLAUDE.md must document implicit dep strategy for PCH, cc, and no-PCH cxx. "
        f"has_old={has_old}, has_implicit={has_implicit}, has_unified={has_unified}"
    )


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
