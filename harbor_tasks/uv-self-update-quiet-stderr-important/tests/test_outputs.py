"""
Task: uv-self-update-quiet-stderr-important
Repo: astral-sh/uv @ 262a50bb4c952cf2461d4073ae21081ed516f21c
PR:   astral-sh/uv#18645

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"
PRINTER = f"{REPO}/crates/uv/src/printer.rs"
SELF_UPDATE = f"{REPO}/crates/uv/src/commands/self_update.rs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_method_body(src: str, method_name: str, return_type: str) -> str | None:
    """Extract the body of a method `fn <name>(self) -> <return_type> { ... }`."""
    pattern = rf"fn\s+{re.escape(method_name)}\s*\(\s*self\s*\)\s*->\s*{re.escape(return_type)}\s*\{{"
    m = re.search(pattern, src)
    if not m:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[start + 1 : i]
    return None


def _parse_match_arms(body: str) -> dict[str, str]:
    """Parse match arms in a Rust method body, returning {variant: return_value}."""
    ALL_VARIANTS = ("Silent", "Quiet", "Default", "Verbose", "NoProgress")
    arms: dict[str, str] = {}
    wildcard_value: str | None = None

    for m in re.finditer(
        r"((?:(?:Self|Printer)\s*::\s*\w+\s*\|?\s*)+|_)\s*=>\s*([\w:]+)",
        body,
    ):
        lhs = m.group(1).strip()
        value = m.group(2).strip().split("::")[-1]
        if lhs == "_":
            wildcard_value = value
        else:
            for v in re.findall(r"(?:Self|Printer)\s*::\s*(\w+)", lhs):
                arms[v] = value

    if wildcard_value is not None:
        for v in ALL_VARIANTS:
            if v not in arms:
                arms[v] = wildcard_value

    return arms


def _find_new_stderr_method(src: str) -> tuple[str, str] | None:
    """Find a method on Printer returning Stderr that is NOT named 'stderr'."""
    for m in re.finditer(
        r"fn\s+(\w+)\s*\(\s*self\s*\)\s*->\s*Stderr\s*\{",
        src,
    ):
        name = m.group(1)
        if name == "stderr":
            continue
        body = _extract_method_body(src, name, "Stderr")
        if body is not None:
            return name, body
    return None


def _cargo_check(manifest_path: str | None = None) -> subprocess.CompletedProcess:
    """Run cargo check on the workspace or specific manifest."""
    cmd = ["cargo", "check"]
    if manifest_path:
        cmd.extend(["--manifest-path", manifest_path])
    else:
        cmd.extend(["--package", "uv"])
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_rust_syntax():
    """Modified Rust files must exist and contain expected structures."""
    for path in [PRINTER, SELF_UPDATE]:
        assert Path(path).exists(), f"{path} not found"
        content = Path(path).read_text()
        assert len(content) > 100, f"{path} is suspiciously small"

    printer_src = Path(PRINTER).read_text()
    assert "enum Printer" in printer_src, "Printer enum not found in printer.rs"
    assert "fn stderr" in printer_src, "stderr method not found in printer.rs"

    su_src = Path(SELF_UPDATE).read_text()
    assert "fn self_update" in su_src, "self_update function not found"


def test_compilation():
    """Modified crate compiles without errors."""
    r = _cargo_check()
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_new_stderr_important_exists():
    """Printer must have a new stderr_important method (the core fix)."""
    src = Path(PRINTER).read_text()
    result = _find_new_stderr_method(src)
    assert result is not None, "No new method found on Printer returning Stderr (besides stderr())"
    name, body = result
    assert name == "stderr_important", f"Expected method name 'stderr_important', got '{name}'"
    assert len(body.strip()) > 0, "stderr_important method body is empty"


def test_stderr_important_quiet_enabled():
    """stderr_important() returns Stderr::Enabled for Quiet (behavioral verification)."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr_important", "Stderr")
    assert body is not None, "stderr_important() method not found"
    arms = _parse_match_arms(body)
    assert "Quiet" in arms, "stderr_important has no match arm for Quiet"
    assert arms["Quiet"] == "Enabled", (
        f"stderr_important returns {arms['Quiet']} for Quiet, expected Enabled"
    )


def test_stderr_important_silent_disabled():
    """stderr_important() returns Stderr::Disabled for Silent (double-quiet suppresses all)."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr_important", "Stderr")
    assert body is not None, "stderr_important() method not found"
    arms = _parse_match_arms(body)
    assert "Silent" in arms, "stderr_important has no match arm for Silent"
    assert arms["Silent"] == "Disabled", (
        f"stderr_important returns {arms['Silent']} for Silent, expected Disabled"
    )


def test_stderr_important_non_silent_enabled():
    """stderr_important() returns Enabled for Default, Verbose, and NoProgress."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr_important", "Stderr")
    assert body is not None, "stderr_important() method not found"
    arms = _parse_match_arms(body)
    for variant in ("Default", "Verbose", "NoProgress"):
        assert variant in arms, f"stderr_important has no match arm for {variant}"
        assert arms[variant] == "Enabled", (
            f"stderr_important returns {arms[variant]} for {variant}, expected Enabled"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

def test_stderr_quiet_still_disabled():
    """Original stderr() must still return Disabled for Quiet (no regression)."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr", "Stderr")
    assert body is not None, "stderr() method not found on Printer"
    arms = _parse_match_arms(body)
    assert arms.get("Quiet") == "Disabled", (
        f"stderr() returns {arms.get('Quiet')} for Quiet, expected Disabled (regression!)"
    )
    assert arms.get("Silent") == "Disabled", (
        f"stderr() returns {arms.get('Silent')} for Silent, expected Disabled (regression!)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification
# ---------------------------------------------------------------------------

def test_repo_formatting():
    """Repo code passes Rust formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Formatting check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_clippy():
    """Repo code passes Clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--package", "uv", "--all-targets", "--all-features", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Clippy check failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_check_lib():
    """Repo uv library compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--package", "uv", "--lib"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check --lib failed:\n{r.stderr[-1000:]}"


def test_repo_clippy_workspace():
    """Full workspace passes Clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--workspace", "--all-targets", "--all-features", "--locked", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Workspace clippy failed:\n{r.stderr[-1000:]}"


def test_repo_cargo_check_locked():
    """Cargo.lock is up to date with Cargo.toml files (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--package", "uv", "--locked"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check --locked failed (Cargo.lock out of date):\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — wiring
# ---------------------------------------------------------------------------

def test_self_update_uses_stderr_important():
    """self_update.rs uses stderr_important() for important messages (>=3 call sites)."""
    su_src = Path(SELF_UPDATE).read_text()

    cleaned = re.sub(r"//[^\n]*", "", su_src)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'"(?:[^"\\]|\\.)*"', '""', cleaned)

    calls = re.findall(r"\.stderr_important\(\)", cleaned)
    assert len(calls) >= 3, (
        f"self_update.rs uses .stderr_important() only {len(calls)} times, expected >= 3"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_stderr_important_not_stub():
    """stderr_important has real branching logic, not a trivial stub."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr_important", "Stderr")
    assert body is not None, "stderr_important() method not found"
    has_branching = bool(re.search(r"\b(match|if)\b", body))
    has_both = "Enabled" in body and "Disabled" in body
    lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
    assert has_branching, "stderr_important has no branching logic (match/if)"
    assert has_both, "stderr_important doesn't have both Enabled and Disabled variants"
    assert len(lines) >= 2, f"stderr_important body is too short ({len(lines)} lines)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

def test_no_panic_unwrap_in_new_method():
    """New method must not use panic!, unreachable!, or .unwrap() (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr_important", "Stderr")
    assert body is not None, "Could not find stderr_important method body to check"
    assert not re.search(r"(panic!|unreachable!|\.unwrap\(\))", body), (
        "stderr_important uses panic!/unreachable!/unwrap() — violates CLAUDE.md:7"
    )


def test_no_unsafe_in_new_method():
    """New method must not use unsafe code (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr_important", "Stderr")
    assert body is not None, "Could not find stderr_important method body to check"
    assert not re.search(r"\bunsafe\b", body), (
        "stderr_important uses unsafe — violates CLAUDE.md:7"
    )


def test_no_allow_attribute_in_new_code():
    """New code must not use #[allow(...)] — prefer #[expect()] (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr_important", "Stderr")
    assert body is not None, "Could not find stderr_important method to check"
    pattern = r"((?:#\[[^\]]*\]\s*)*fn\s+stderr_important\(self\)\s*->\s*Stderr\s*\{)"
    m = re.search(pattern, src)
    method_header = m.group(1) if m else ""
    assert not re.search(r"#\[allow\(", method_header + body), (
        "stderr_important uses #[allow(...)] — prefer #[expect()] per CLAUDE.md:10"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config)
# ---------------------------------------------------------------------------

def test_no_local_imports_in_new_method():
    """New method must not use local 'use' imports — prefer top-level imports (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    body = _extract_method_body(src, "stderr_important", "Stderr")
    assert body is not None, "Could not find stderr_important method body to check"
    assert not re.search(r"\buse\s+", body), (
        "stderr_important contains a local 'use' statement — violates CLAUDE.md:16"
    )
