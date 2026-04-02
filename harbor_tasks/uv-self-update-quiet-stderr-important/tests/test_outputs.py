"""
Task: uv-self-update-quiet-stderr-important
Repo: astral-sh/uv @ 262a50bb4c952cf2461d4073ae21081ed516f21c
PR:   astral-sh/uv#18645

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/repo"
PRINTER = f"{REPO}/crates/uv/src/printer.rs"
SELF_UPDATE = f"{REPO}/crates/uv/src/commands/self_update.rs"


# ---------------------------------------------------------------------------
# Helpers — extract Rust types and compile snippets
# ---------------------------------------------------------------------------

def _extract_balanced_block(src, start):
    """Extract balanced-brace block starting from first '{' at or after start."""
    brace_pos = src.index("{", start)
    depth = 0
    for i in range(brace_pos, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[brace_pos : i + 1]
    raise ValueError("Unbalanced braces")


def _extract_printer_components():
    """Extract Printer enum and all impl methods returning Stderr from printer.rs."""
    src = Path(PRINTER).read_text()

    # Extract Printer enum (enum has no nested braces, simple match is fine)
    enum_match = re.search(
        r'((?:#\[derive[^\]]*\]\s*)*pub(?:\(crate\))?\s+enum\s+Printer\s*\{[^}]+\})',
        src,
    )
    assert enum_match, "Could not find Printer enum in printer.rs"
    enum_def = enum_match.group(1)
    enum_def = enum_def.replace("pub(crate)", "pub")
    enum_def = re.sub(r"#\[derive[^\]]*\]", "", enum_def)
    enum_def = re.sub(r"\s*///[^\n]*", "", enum_def)

    # Extract all impl Printer methods returning Stderr using balanced brace matching
    methods = []
    for m in re.finditer(
        r"((?:\s*///[^\n]*\n)*\s*pub(?:\(crate\))?\s+fn\s+(\w+)\(self\)\s*->\s*Stderr\s*)\{",
        src,
    ):
        method_name = m.group(2)
        sig = m.group(1).strip()
        body = _extract_balanced_block(src, m.end() - 1)
        method_src = sig + " " + body
        method_src = method_src.replace("pub(crate)", "pub")
        method_src = re.sub(r"\s*///[^\n]*\n", "\n", method_src)
        methods.append((method_name, method_src))

    return enum_def, methods


def _find_new_important_method():
    """Find a new method on Printer (not stderr) that returns Stderr."""
    enum_def, methods = _extract_printer_components()
    non_stderr = [(n, s) for n, s in methods if n != "stderr"]
    assert non_stderr, "No new method found on Printer returning Stderr (besides stderr())"
    return enum_def, methods, non_stderr


def _compile_and_run_rust(code: str) -> subprocess.CompletedProcess:
    """Compile a Rust snippet and run it. Returns completed process."""
    with tempfile.NamedTemporaryFile(suffix=".rs", mode="w", delete=False) as f:
        f.write(code)
        rs_path = f.name
    bin_path = rs_path.replace(".rs", "")
    comp = subprocess.run(
        ["rustc", "--edition", "2021", "-o", bin_path, rs_path],
        capture_output=True,
        timeout=30,
    )
    assert comp.returncode == 0, f"Rust compilation failed:\n{comp.stderr.decode()}"
    return subprocess.run([bin_path], capture_output=True, timeout=10)


def _build_test_program(enum_def, methods, test_body):
    """Build a complete Rust program with Printer/Stderr and a main that runs test_body."""
    code = (
        "#[derive(Debug, Copy, Clone, PartialEq)]\nenum Stderr { Enabled, Disabled }\n\n"
        "#[derive(Debug, Copy, Clone, PartialEq)]\n"
        + enum_def
        + "\n\nimpl Printer {\n"
    )
    for _, msrc in methods:
        code += msrc + "\n"
    code += "}\n\nfn main() {\n" + test_body + "\n}\n"
    return code


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_rust_syntax():
    """Modified Rust files must exist and compile (extracted snippets)."""
    for path in [PRINTER, SELF_UPDATE]:
        assert Path(path).exists(), f"{path} not found"
        content = Path(path).read_text()
        assert len(content) > 100, f"{path} is suspiciously small"

    # Verify printer.rs retains Printer enum and stderr method
    printer_src = Path(PRINTER).read_text()
    assert "enum Printer" in printer_src, "Printer enum not found in printer.rs"
    assert "fn stderr" in printer_src, "stderr method not found in printer.rs"

    # Verify self_update.rs retains the self_update function
    su_src = Path(SELF_UPDATE).read_text()
    assert "fn self_update" in su_src, "self_update function not found"

    # Verify the extracted Printer enum and methods compile
    enum_def, methods = _extract_printer_components()
    code = _build_test_program(enum_def, methods, "    // no-op")
    _compile_and_run_rust(code)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_new_method_quiet_enabled():
    """New Printer method returns Stderr::Enabled for Quiet (the core fix)."""
    enum_def, methods, non_stderr = _find_new_important_method()
    for method_name, _ in non_stderr:
        body = f"""\
    if Printer::Quiet.{method_name}() == Stderr::Enabled {{
        std::process::exit(0);
    }} else {{
        std::process::exit(1);
    }}"""
        result = _compile_and_run_rust(_build_test_program(enum_def, methods, body))
        if result.returncode == 0:
            return
    assert False, "No new method returns Stderr::Enabled for Printer::Quiet"


# [pr_diff] fail_to_pass
def test_new_method_silent_disabled():
    """New method returns Stderr::Disabled for Silent (double-quiet suppresses all)."""
    enum_def, methods, non_stderr = _find_new_important_method()
    for method_name, _ in non_stderr:
        body = f"""\
    let ok = Printer::Quiet.{method_name}() == Stderr::Enabled
        && Printer::Silent.{method_name}() == Stderr::Disabled;
    std::process::exit(if ok {{ 0 }} else {{ 1 }});"""
        result = _compile_and_run_rust(_build_test_program(enum_def, methods, body))
        if result.returncode == 0:
            return
    assert False, "No new method satisfies Quiet→Enabled AND Silent→Disabled"


# [pr_diff] fail_to_pass
def test_new_method_all_non_silent_enabled():
    """New method returns Enabled for Default, Verbose, and NoProgress too."""
    enum_def, methods, non_stderr = _find_new_important_method()
    for method_name, _ in non_stderr:
        body = f"""\
    let ok = Printer::Quiet.{method_name}() == Stderr::Enabled
        && Printer::Silent.{method_name}() == Stderr::Disabled
        && Printer::Default.{method_name}() == Stderr::Enabled
        && Printer::Verbose.{method_name}() == Stderr::Enabled
        && Printer::NoProgress.{method_name}() == Stderr::Enabled;
    std::process::exit(if ok {{ 0 }} else {{ 1 }});"""
        result = _compile_and_run_rust(_build_test_program(enum_def, methods, body))
        if result.returncode == 0:
            return
    assert False, "No new method returns Enabled for all non-Silent variants"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_stderr_quiet_still_disabled():
    """Original stderr() must still return Disabled for Quiet (no regression)."""
    enum_def, methods = _extract_printer_components()
    stderr_methods = [n for n, _ in methods if n == "stderr"]
    assert stderr_methods, "stderr() method not found on Printer"
    body = """\
    let ok = Printer::Quiet.stderr() == Stderr::Disabled
        && Printer::Silent.stderr() == Stderr::Disabled;
    std::process::exit(if ok { 0 } else { 1 });"""
    result = _compile_and_run_rust(_build_test_program(enum_def, methods, body))
    assert result.returncode == 0, "stderr() should still return Disabled for Quiet and Silent"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — wiring
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_self_update_wiring():
    """self_update.rs uses the new method for important messages (≥3 call sites)."""
    src = Path(SELF_UPDATE).read_text()
    _, _, non_stderr = _find_new_important_method()

    # Strip comments and string literals to avoid false matches
    cleaned = re.sub(r"//[^\n]*", "", src)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r'"(?:[^"\\]|\\.)*"', '""', cleaned)

    for method_name, _ in non_stderr:
        calls = re.findall(rf"\.{re.escape(method_name)}\(\)", cleaned)
        if len(calls) >= 3:
            return

    assert False, "self_update.rs should use the new important-stderr method in ≥3 call sites"


# ---------------------------------------------------------------------------
# Fail-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] fail_to_pass
def test_new_method_not_stub():
    """New method has real branching logic, not a trivial stub."""
    src = Path(PRINTER).read_text()
    _, _, non_stderr = _find_new_important_method()

    for method_name, _ in non_stderr:
        pattern = rf"fn\s+{re.escape(method_name)}\(self\)\s*->\s*Stderr\s*\{{(.*?)\n\s*\}}"
        m = re.search(pattern, src, re.DOTALL)
        if not m:
            continue
        body = m.group(1)
        has_branching = bool(re.search(r"\b(match|if)\b", body))
        has_both_variants = "Enabled" in body and "Disabled" in body
        lines = [l.strip() for l in body.strip().splitlines() if l.strip()]
        if has_branching and has_both_variants and len(lines) >= 2:
            return

    assert False, "New method body is a stub — needs branching logic with Enabled and Disabled"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:7 @ 262a50bb
def test_no_panic_unwrap_in_new_method():
    """New method must not use panic!, unreachable!, or .unwrap() (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    _, _, non_stderr = _find_new_important_method()

    for method_name, _ in non_stderr:
        pattern = rf"fn\s+{re.escape(method_name)}\(self\)\s*->\s*Stderr\s*\{{(.*?)\n\s*\}}"
        m = re.search(pattern, src, re.DOTALL)
        if not m:
            continue
        body = m.group(1)
        assert not re.search(r"(panic!|unreachable!|\.unwrap\(\))", body), (
            f"Method {method_name} uses panic!/unreachable!/unwrap() — violates CLAUDE.md:7"
        )
        return

    assert False, "Could not find new method body to check"


# [agent_config] fail_to_pass — CLAUDE.md:7 @ 262a50bb
def test_no_unsafe_in_new_method():
    """New method must not use unsafe code (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    _, _, non_stderr = _find_new_important_method()

    for method_name, _ in non_stderr:
        pattern = rf"fn\s+{re.escape(method_name)}\(self\)\s*->\s*Stderr\s*\{{(.*?)\n\s*\}}"
        m = re.search(pattern, src, re.DOTALL)
        if not m:
            continue
        body = m.group(1)
        assert not re.search(r"\bunsafe\b", body), (
            f"Method {method_name} uses unsafe — violates CLAUDE.md:7"
        )
        return

    assert False, "Could not find new method body to check"


# [agent_config] fail_to_pass — CLAUDE.md:10 @ 262a50bb
def test_no_allow_attribute_in_new_code():
    """New code must not use #[allow(...)] — prefer #[expect()] (CLAUDE.md rule)."""
    src = Path(PRINTER).read_text()
    _, _, non_stderr = _find_new_important_method()

    for method_name, _ in non_stderr:
        # Find the method and any attributes above it
        pattern = rf"((?:#\[[^\]]*\]\s*)*fn\s+{re.escape(method_name)}\(self\)\s*->\s*Stderr\s*\{{.*?\n\s*\}})"
        m = re.search(pattern, src, re.DOTALL)
        if not m:
            continue
        method_block = m.group(1)
        assert not re.search(r"#\[allow\(", method_block), (
            f"Method {method_name} uses #[allow(...)] — prefer #[expect()] per CLAUDE.md:10"
        )
        return

    assert False, "Could not find new method to check"
