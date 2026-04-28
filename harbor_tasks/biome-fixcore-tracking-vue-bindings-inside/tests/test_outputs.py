"""
Task: biome-fixcore-tracking-vue-bindings-inside
Repo: biomejs/biome @ c047e86583434beb33ed4fb0b49e627d26a8afbd
PR:   9053

Fix Vue/Svelte directive variable tracking so variables used inside directive
attributes (e.g. @click="handler", bind:value={x}) are recognized as used.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests use cargo check to verify compilation of changed crates.
Documentation tests verify required content in skill/agent files.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/biome"


# ---------------------------------------------------------------------------
# Pass-to-pass tests
# ---------------------------------------------------------------------------


def test_markdown_table_formatting():
    """SKILL.md files must use proper markdown table formatting."""
    p = Path(REPO) / ".claude/skills/biome-developer/SKILL.md"
    if not p.exists():
        return  # File not required to exist at base commit
    content = p.read_text()
    proper = bool(re.search(r'\|\s+[-\w]+\s+\|', content))
    compact = bool(re.search(r'\|[-]{3,}\|', content))
    assert proper or not compact, \
        "SKILL.md should have properly formatted markdown tables (spaces around separators)"


def test_vue_svelte_test_specs_exist():
    """Vue and Svelte test spec files must exist in the HTML parser tests."""
    base = Path(REPO) / "crates/biome_html_parser/tests/html_specs"
    vue_ok = len(list((base / "ok/vue").glob("*.vue"))) if (base / "ok/vue").exists() else 0
    vue_err = len(list((base / "error/vue").glob("*.vue"))) if (base / "error/vue").exists() else 0
    sv_err = len(list((base / "error/svelte").glob("*.svelte"))) if (base / "error/svelte").exists() else 0
    assert vue_ok >= 3, f"Expected >= 3 Vue ok specs, got {vue_ok}"
    assert vue_err >= 3, f"Expected >= 3 Vue error specs, got {vue_err}"
    assert sv_err >= 5, f"Expected >= 5 Svelte error specs, got {sv_err}"


def test_lib_rs_module_declaration():
    """biome_html_syntax::lib.rs uses proper module declaration style."""
    content = Path(REPO, "crates/biome_html_syntax/src/lib.rs").read_text()
    inline = len(re.findall(r'^mod\s+\w+\s*;', content, re.MULTILINE))
    brace = len(re.findall(r'^mod\s+\w+\s*\{', content, re.MULTILINE))
    assert inline >= 1, "lib.rs should have inline module declarations"
    assert brace <= 2, f"Expected <= 2 brace modules, got {brace}"


# ---------------------------------------------------------------------------
# Fail-to-pass tests — behavioral verification via compilation + content
# ---------------------------------------------------------------------------


def test_new_module_registered():
    """biome_html_syntax::lib.rs must declare a module for directive extension."""
    content = Path(REPO, "crates/biome_html_syntax/src/lib.rs").read_text()
    mods = re.findall(r'^\s*(?:pub\s+)?mod\s+(\w+)\s*;', content, re.MULTILINE)
    assert "directive_ext" in mods, \
        f"lib.rs must declare mod directive_ext. Found: {mods}"


def test_directive_ext_compiles():
    """directive_ext.rs must exist and the biome_html_syntax crate must compile.

    Behavioral verification: cargo check exercises the Rust compiler on the
    new directive extension module, confirming it integrates correctly with
    the crate's existing AST types.
    """
    directive_ext = Path(REPO) / "crates/biome_html_syntax/src/directive_ext.rs"
    assert directive_ext.exists(), \
        "directive_ext.rs must exist in biome_html_syntax/src/"

    proc = subprocess.run(
        ["cargo", "check", "-p", "biome_html_syntax"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, \
        f"biome_html_syntax must compile with directive_ext module.\n{proc.stderr[-2000:]}"


def test_html_handler_compiles():
    """html.rs must handle Vue and Svelte directive types and compile.

    Behavioral verification: cargo check on biome_service confirms that the
    directive handling code type-checks correctly against the AST types and
    embedding infrastructure. Gate checks verify the instruction-required
    Vue and Svelte directive types are referenced in the handler.
    """
    html_rs = Path(REPO) / "crates/biome_service/src/file_handlers/html.rs"
    content = html_rs.read_text()

    # Gate: instruction requires handling Vue directive AST types
    has_vue = any(t in content for t in [
        "VueDirective", "VueVOnShorthandDirective",
        "VueVBindShorthandDirective", "VueVSlotShorthandDirective",
    ])
    assert has_vue, "html.rs must handle Vue directive types"

    # Gate: instruction requires handling Svelte directive AST types
    has_svelte = any(t in content for t in [
        "AnySvelteDirective", "SvelteBindDirective", "SvelteClassDirective",
    ])
    assert has_svelte, "html.rs must handle Svelte directive types"

    # Behavioral: compile the service crate to verify type correctness
    proc = subprocess.run(
        ["cargo", "check", "-p", "biome_service"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, \
        f"biome_service must compile with directive handling.\n{proc.stderr[-2000:]}"


def test_biome_developer_skill_created():
    """biome-developer/SKILL.md exists with valid frontmatter and required content."""
    path = Path(REPO) / ".claude/skills/biome-developer/SKILL.md"
    assert path.exists(), "biome-developer/SKILL.md must exist"

    content = path.read_text()
    lines = content.split("\n")

    # Check frontmatter
    assert len(lines) > 0 and lines[0].strip() == "---", \
        "SKILL.md must start with YAML frontmatter delimiter"
    fm_end = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            fm_end = i
            break
    assert fm_end > 0, "SKILL.md must have closing frontmatter delimiter"
    fm_text = "\n".join(lines[1:fm_end])
    assert "name:" in fm_text, "Frontmatter must include a name: field"

    # Check required content themes (instruction-specified topics)
    body = content.lower()
    assert any(t in body for t in [
        "inner_string", "text_trimmed", "string extract", "text extract"
    ]), "Must document string extraction methods"
    assert any(t in body for t in [
        "quick_test", "dbg!", "inspect", "ast"
    ]), "Must document AST inspection techniques"
    assert any(t in body for t in [
        "embedding", "embedded", "embeddingkind"
    ]), "Must cover embedded language handling"


def test_agents_md_updated():
    """AGENTS.md includes guidelines about evidence, legacy syntax, AST inspection."""
    content = Path(REPO, "AGENTS.md").read_text()
    lower = content.lower()

    has_evidence = bool(re.search(
        r'(?:widely used|common).*(?:without evidence|not proven|unverified)',
        lower
    ))
    has_legacy = any(t in lower for t in ["legacy", "deprecated", "old syntax"])
    has_ast = bool(re.search(
        r'(?:inspect|quick_test|ast.*structure|parse.*first)',
        lower
    ))
    has_skills = bool(re.search(r'(?:skills?\s*directory|\.claude/skills)', content))

    assert has_evidence, "Must warn against claiming patterns without evidence"
    assert has_legacy, "Must warn about legacy/deprecated syntax"
    assert has_ast, "Must recommend AST inspection"
    assert has_skills, "Must reference skills directory"


def test_testing_codegen_skill_updated():
    """testing-codegen SKILL.md documents parser quick testing."""
    content = Path(REPO, ".claude/skills/testing-codegen/SKILL.md").read_text()
    lower = content.lower()

    has_quick_test = bool(re.search(r'(?:quick.*test|parser.*test)', lower))
    has_qt_cmd = bool(re.search(r'(?:just\s+qt|quick_test)', content))
    has_html_parser = "biome_html_parser" in content

    assert has_quick_test, "Must document quick testing"
    assert has_qt_cmd, "Must reference quick test command"
    assert has_html_parser, "Must reference biome_html_parser"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_validate_rules_documentation_run_rules_check():
    """pass_to_pass | CI job 'Validate rules documentation' → step 'Run rules check'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo run -p rules_check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run rules check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_node_js_api_build_main_binary():
    """pass_to_pass | CI job 'Test Node.js API' → step 'Build main binary'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build -p biome_cli --release'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build main binary' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_node_js_api_build_typescript_code():
    """pass_to_pass | CI job 'Test Node.js API' → step 'Build TypeScript code'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @biomejs/backend-jsonrpc i && pnpm --filter @biomejs/backend-jsonrpc run build && pnpm --filter @biomejs/js-api run build:wasm-bundler-dev && pnpm --filter @biomejs/js-api run build:wasm-node-dev && pnpm --filter @biomejs/js-api run build:wasm-web-dev && pnpm --filter @biomejs/js-api i && pnpm --filter @biomejs/js-api run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build TypeScript code' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_node_js_api_run_js_tests():
    """pass_to_pass | CI job 'Test Node.js API' → step 'Run JS tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @biomejs/backend-jsonrpc run test:ci && pnpm --filter @biomejs/js-api run test:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run JS tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_project_run_clippy():
    """pass_to_pass | CI job 'Lint project' → step 'Run clippy'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run clippy' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'Test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo test --workspace --features=js_plugin'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_dependencies_detect_unused_dependencies_using_udeps():
    """pass_to_pass | CI job 'Check Dependencies' → step 'Detect unused dependencies using udeps'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo +nightly udeps --all-targets'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Detect unused dependencies using udeps' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build__biomejs_wasm_web_build_wasm_module_for_the_web():
    """pass_to_pass | CI job 'Build @biomejs/wasm-web' → step 'Build WASM module for the web'"""
    r = subprocess.run(
        ["bash", "-lc", 'just build-wasm-web'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build WASM module for the web' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")