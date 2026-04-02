"""
Task: ruff-lsp-markdown-preview-warning
Repo: astral-sh/ruff @ a84a58fef88968e36c0b070f0ab9a4bff7a05389
PR:   #24150

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
BASE_COMMIT = "a84a58fef88968e36c0b070f0ab9a4bff7a05389"
FORMAT_RS = Path(REPO, "crates/ruff_server/src/format.rs")
FORMAT_REQ_RS = Path(REPO, "crates/ruff_server/src/server/api/requests/format.rs")
EXEC_CMD_RS = Path(REPO, "crates/ruff_server/src/server/api/requests/execute_command.rs")

# Snapshot file contents before any test injection modifies them
_FORMAT_RS_ORIGINAL = FORMAT_RS.read_text()
_FORMAT_REQ_ORIGINAL = FORMAT_REQ_RS.read_text()
_EXEC_CMD_ORIGINAL = EXEC_CMD_RS.read_text()

# All modified files for agent_config checks
_MODIFIED_FILES = {
    "format.rs": _FORMAT_RS_ORIGINAL,
    "format_req.rs": _FORMAT_REQ_ORIGINAL,
    "execute_command.rs": _EXEC_CMD_ORIGINAL,
}

# Rust test injected into the existing mod tests block in format.rs.
# Tests three scenarios: markdown-without-preview must be distinguishable from
# unchanged Python, unchanged Markdown (with preview), and formatted Python.
_INJECTED_TEST = r'''
    #[allow(unused_imports)]
    use ruff_python_ast::SourceType;

    #[test]
    fn __eval_behavioral_md_preview() {
        let settings = FormatterSettings::default();

        // Already-formatted Python -> "unchanged" result
        let py_doc = TextDocument::new("x = 1\n".to_string(), 0);
        let py_result = format(
            &py_doc,
            SourceType::Python(PySourceType::Python),
            &settings,
            Path::new("test.py"),
            FormatBackend::Internal,
        )
        .unwrap();

        // Markdown without preview -> must NOT equal "unchanged"
        let md_doc = TextDocument::new("# Hello\n".to_string(), 0);
        let md_result = format(
            &md_doc,
            SourceType::Markdown,
            &settings,
            Path::new("test.md"),
            FormatBackend::Internal,
        )
        .unwrap();

        let py_repr = format!("{:?}", py_result);
        let md_repr = format!("{:?}", md_result);
        assert_ne!(
            py_repr, md_repr,
            "Markdown without preview must be distinguishable from unchanged (both were '{}')",
            py_repr
        );
    }

    #[test]
    fn __eval_behavioral_md_preview_varied() {
        let settings = FormatterSettings::default();

        // Test with different markdown content to prevent hardcoding
        for content in &["# Title\n", "Hello world\n", "```python\nx=1\n```\n"] {
            let md_doc = TextDocument::new(content.to_string(), 0);
            let md_result = format(
                &md_doc,
                SourceType::Markdown,
                &settings,
                Path::new("test.md"),
                FormatBackend::Internal,
            )
            .unwrap();

            let repr = format!("{:?}", md_result);
            // Must not be Unchanged/None — should indicate preview-only
            assert!(
                !repr.contains("Unchanged") && repr != "None",
                "Markdown '{}' without preview should not be Unchanged, got: {}",
                content.trim(), repr
            );
        }
    }
'''


def _inject_behavioral_test():
    """Inject the behavioral Rust test into format.rs (idempotent)."""
    src = FORMAT_RS.read_text()
    if "__eval_behavioral_md_preview" in src:
        return
    lines = src.split("\n")
    last_brace = -1
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "}":
            last_brace = i
            break
    assert last_brace >= 0, "Cannot find mod tests closing brace in format.rs"
    lines.insert(last_brace, _INJECTED_TEST)
    FORMAT_RS.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ruff_server crate must compile without errors."""
    _inject_behavioral_test()
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_server"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_md_preview_distinguishable():
    """format() on markdown without preview must return a distinguishable result."""
    _inject_behavioral_test()
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_server", "--",
         "__eval_behavioral_md_preview", "--exact"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        "Behavioral test failed — markdown-without-preview result is "
        "indistinguishable from 'unchanged':\n"
        f"{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_md_preview_distinguishable_varied():
    """format() returns preview-only for varied markdown inputs (anti-hardcode)."""
    _inject_behavioral_test()
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_server", "--",
         "__eval_behavioral_md_preview_varied", "--exact"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        "Varied markdown test failed — preview-only not returned for all inputs:\n"
        f"{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_warning_in_format_handler():
    """Format request handler must send a user-visible warning for markdown preview.
    # AST-only because: Rust LSP handler requires full server context to invoke
    """
    # Check that the format request handler has a user-visible warning mechanism
    warning_patterns = [
        r"show_warning_message",
        r"show_message",
        r"ShowMessageParams",
        r"window/showMessage",
        r"MessageType::Warning",
    ]
    has_warning = any(re.search(p, _FORMAT_REQ_ORIGINAL) for p in warning_patterns)
    assert has_warning, (
        "No user-visible warning mechanism found in format request handler. "
        "Expected show_message, ShowMessageParams, or similar LSP notification."
    )
    # Warning message must mention "preview" so user knows what to enable
    assert re.search(r"(?i)preview", _FORMAT_REQ_ORIGINAL), (
        "Warning in format handler does not mention 'preview' — "
        "user won't know how to fix the issue."
    )


# [pr_diff] fail_to_pass
def test_format_result_enum_exists():
    """format.rs must define a result type that distinguishes preview-only from unchanged.
    # AST-only because: Rust enum definition is structural, not callable from Python
    """
    # The fix requires a new enum or modified return type in format.rs
    # that can represent "skipped because preview is off" distinctly from "unchanged"
    src = _FORMAT_RS_ORIGINAL
    # Check for an enum with a preview-related variant
    has_preview_variant = bool(re.search(
        r"enum\s+\w+.*\{[^}]*(?:Preview|preview)[^}]*\}",
        src, re.DOTALL
    ))
    # Or check for a struct/type that encodes preview state
    has_preview_type = bool(re.search(r"PreviewOnly|PreviewRequired|NeedsPreview", src))
    assert has_preview_variant or has_preview_type, (
        "No enum variant or type found in format.rs that distinguishes "
        "'preview required' from 'unchanged'. The format function must "
        "return a distinct result when markdown formatting is skipped."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_format_tests():
    """Existing format::tests in ruff_server must still pass."""
    _inject_behavioral_test()
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_server", "--",
         "format::tests", "--skip", "__eval_behavioral"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Existing format::tests failed:\n"
        f"{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ a84a58fe
def test_no_new_unwrap():
    """No new .unwrap() calls added to modified files."""
    for name, content in _MODIFIED_FILES.items():
        if name == "format.rs":
            base_path = "crates/ruff_server/src/format.rs"
        elif name == "format_req.rs":
            base_path = "crates/ruff_server/src/server/api/requests/format.rs"
        elif name == "execute_command.rs":
            base_path = "crates/ruff_server/src/server/api/requests/execute_command.rs"
        else:
            continue
        base_r = subprocess.run(
            ["git", "show", f"{BASE_COMMIT}:{base_path}"],
            cwd=REPO, capture_output=True,
        )
        base_count = base_r.stdout.decode().count(".unwrap()")
        curr_count = content.count(".unwrap()")
        assert curr_count <= base_count, (
            f"New .unwrap() calls in {name}: {base_count} → {curr_count}"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ a84a58fe
def test_no_inline_imports():
    """No 'use' imports inside function bodies in modified Rust files."""
    for name, content in _MODIFIED_FILES.items():
        in_fn = False
        depth = 0
        violations = []
        for lineno, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            if re.match(r"(pub(\(crate\))?\s+)?(fn|async fn) ", stripped):
                in_fn = True
                depth = 0
            if in_fn:
                depth += stripped.count("{") - stripped.count("}")
                if depth <= 0 and in_fn:
                    in_fn = False
                if in_fn and depth > 0 and stripped.startswith("use "):
                    violations.append(f"{name}:{lineno}: {stripped}")
        assert len(violations) == 0, (
            f"Inline import(s) in function bodies:\n" +
            "\n".join(violations)
        )


# [agent_config] pass_to_pass — AGENTS.md:81 @ a84a58fe
def test_prefer_expect_over_allow():
    """New #[allow(..)] attributes should use #[expect(..)] instead."""
    for name, content in _MODIFIED_FILES.items():
        if name == "format.rs":
            base_path = "crates/ruff_server/src/format.rs"
        elif name == "format_req.rs":
            base_path = "crates/ruff_server/src/server/api/requests/format.rs"
        elif name == "execute_command.rs":
            base_path = "crates/ruff_server/src/server/api/requests/execute_command.rs"
        else:
            continue
        base_r = subprocess.run(
            ["git", "show", f"{BASE_COMMIT}:{base_path}"],
            cwd=REPO, capture_output=True,
        )
        base_allows = len(re.findall(r"#\[allow\(", base_r.stdout.decode()))
        curr_allows = len(re.findall(r"#\[allow\(", content))
        assert curr_allows <= base_allows, (
            f"New #[allow(..)] in {name}: {base_allows} → {curr_allows}. "
            "Use #[expect(..)] instead per AGENTS.md:81."
        )
