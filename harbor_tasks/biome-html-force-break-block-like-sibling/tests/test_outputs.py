"""Tests for biome HTML formatter PR #8833 (force-break + display:none handling)."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/biome")
WHITESPACE_DIR = REPO / "crates/biome_html_formatter/tests/specs/html/whitespace"
FIXTURES = Path("/tests/fixtures")

FIXTURE_FILES = [
    "force-break-nontext-and-non-sensitive-sibling.html",
    "force-break-nontext-and-non-sensitive-sibling.html.snap",
    "force-break-nontext-and-non-sensitive-sibling-2.html",
    "force-break-nontext-and-non-sensitive-sibling-2.html.snap",
    "no-break-display-none.html",
    "no-break-display-none.html.snap",
]


def _refresh_fixtures() -> None:
    """Re-copy test fixtures into the repo to defend against tampering."""
    for name in FIXTURE_FILES:
        src = FIXTURES / name
        dst = WHITESPACE_DIR / name
        if not src.exists():
            raise FileNotFoundError(f"fixture missing: {src}")
        shutil.copy(src, dst)


@pytest.fixture(scope="module")
def cargo_results() -> dict[str, str]:
    """Run the html_formatter spec_tests once and return a {test_name: status} map.

    Cargo's first invocation in a fresh container does ~55s of re-link work
    even when sources are unchanged (a docker layer fingerprint quirk); after
    that, repeated runs are sub-second. So we run cargo test exactly once
    here at module scope.
    """
    _refresh_fixtures()

    # libtest's text output: lines like "test foo::bar ... ok" or "... FAILED"
    proc = subprocess.run(
        [
            "cargo",
            "test",
            "-p",
            "biome_html_formatter",
            "--test",
            "spec_tests",
            "--no-fail-fast",
            "--",
            "--test-threads",
            "1",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    output = proc.stdout + proc.stderr
    status: dict[str, str] = {}
    pattern = re.compile(r"^test (\S+) \.\.\. (ok|FAILED|ignored)\s*$", re.MULTILINE)
    for match in pattern.finditer(output):
        name, result = match.group(1), match.group(2)
        # Ignore the per-test-binary "test result:" summary lines (they don't match).
        if "::" in name:
            status[name] = result
    if not status:
        pytest.fail(
            f"could not parse any test results from cargo output\n"
            f"stdout tail:\n{proc.stdout[-1500:]}\n"
            f"stderr tail:\n{proc.stderr[-1500:]}"
        )
    return status


# --- Fail-to-pass ---------------------------------------------------------


def test_force_break_block_like_sibling_with_text(cargo_results: dict[str, str]) -> None:
    """A visible block-like child (e.g. `<div>`) adjacent to text in a parent
    must force the parent onto multiple lines.

    Concretely: ``<div>a<div>b</div> c</div>`` should reformat to a
    four-line block; on the buggy base it stays on a single line and the
    snapshot test fails.
    """
    name = "formatter::html::html::whitespace::force_break_nontext_and_non_sensitive_sibling_html"
    if name not in cargo_results:
        pytest.fail(f"test {name} did not run; cargo_results keys: {sorted(cargo_results)[:10]} ...")
    assert cargo_results[name] == "ok", (
        f"{name} status={cargo_results[name]} (expected ok). "
        f"On the buggy base commit the formatter emits "
        f"'<div>a<div>b</div> c</div>' on a single line; it should break."
    )


def test_force_break_block_like_sibling_with_text_variant(cargo_results: dict[str, str]) -> None:
    """Second fail-to-pass: a different visible block-like element
    (``<article>``) adjacent to text must also force parent multiline.

    Input ``<div>before<article>middle</article>after</div>`` must
    reformat to a four-line block; on the buggy base it stays on a
    single line.
    """
    name = "formatter::html::html::whitespace::force_break_nontext_and_non_sensitive_sibling_2_html"
    if name not in cargo_results:
        pytest.fail(f"test {name} did not run; cargo_results keys: {sorted(cargo_results)[:10]} ...")
    assert cargo_results[name] == "ok", (
        f"{name} status={cargo_results[name]} (expected ok). "
        f"On the buggy base commit the formatter does not break "
        f"around a visible block-like <article> child; it should."
    )


# --- Pass-to-pass: regression guards on the same code-path ----------------


def test_no_break_around_display_none_element(cargo_results: dict[str, str]) -> None:
    """Whitespace-sensitive children adjacent to a ``display: none`` element
    (e.g. ``<meta>``) must NOT be split onto separate lines.

    Input ``<div>123<meta attr />456</div>`` should stay on one line; this
    is the regression case the new branch in element_list.rs guards.
    """
    name = "formatter::html::html::whitespace::no_break_display_none_html"
    assert cargo_results.get(name) == "ok", (
        f"{name} status={cargo_results.get(name)} (expected ok). "
        f"display:none elements must not introduce whitespace breaks."
    )


def test_existing_whitespace_preserve_newline(cargo_results: dict[str, str]) -> None:
    """Existing snapshot test for newline preservation must still pass."""
    name = "formatter::html::html::whitespace::preserve_newline_after_element_html"
    assert cargo_results.get(name) == "ok", f"{name} regressed: {cargo_results.get(name)}"


def test_existing_whitespace_preserve_space(cargo_results: dict[str, str]) -> None:
    """Existing snapshot test for space preservation must still pass."""
    name = "formatter::html::html::whitespace::preserve_space_after_element_html"
    assert cargo_results.get(name) == "ok", f"{name} regressed: {cargo_results.get(name)}"


def test_no_other_spec_test_regressions(cargo_results: dict[str, str]) -> None:
    """No spec_tests outside the two new whitespace tests should regress.

    The PR only changes formatter logic for text-adjacent block-like /
    display:none siblings; every other spec test is a regression guard.
    """
    new_test_ids = {
        "formatter::html::html::whitespace::force_break_nontext_and_non_sensitive_sibling_html",
        "formatter::html::html::whitespace::force_break_nontext_and_non_sensitive_sibling_2_html",
        "formatter::html::html::whitespace::no_break_display_none_html",
    }
    failures = [
        name
        for name, st in cargo_results.items()
        if st == "FAILED" and name not in new_test_ids
    ]
    assert not failures, f"unexpected spec_test regressions: {failures}"


# --- Pass-to-pass: repo CI tooling ---------------------------------------


def test_repo_cargo_fmt_check() -> None:
    """`cargo fmt --check` must pass on the whole workspace."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo fmt failed:\n{r.stdout}\n{r.stderr}"


def test_repo_cargo_clippy_html_formatter() -> None:
    """`cargo clippy` on biome_html_formatter must pass with --deny warnings."""
    r = subprocess.run(
        [
            "cargo",
            "clippy",
            "-p",
            "biome_html_formatter",
            "--all-targets",
            "--",
            "--deny",
            "warnings",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-2000:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build__biomejs_wasm_web_build_wasm_module_for_the_web():
    """fail_to_pass | CI job 'Build @biomejs/wasm-web' → step 'Build WASM module for the web'"""
    r = subprocess.run(
        ["bash", "-lc", 'just build-wasm-web'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build WASM module for the web' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build__biomejs_wasm_web_verify_wasm_artifact_exists():
    """fail_to_pass | CI job 'Build @biomejs/wasm-web' → step 'Verify WASM artifact exists'"""
    r = subprocess.run(
        ["bash", "-lc", 'test -f biome_wasm_bg.wasm && echo "Found wasm artifact biome_wasm_bg.wasm"'], cwd=os.path.join(REPO, 'packages/@biomejs/wasm-web'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify WASM artifact exists' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

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

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'Test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo test --workspace --features=js_plugin'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_project_run_clippy():
    """pass_to_pass | CI job 'Lint project' → step 'Run clippy'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run clippy' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_dependencies_detect_unused_dependencies_using_udeps():
    """pass_to_pass | CI job 'Check Dependencies' → step 'Detect unused dependencies using udeps'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo +nightly udeps --all-targets'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Detect unused dependencies using udeps' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")