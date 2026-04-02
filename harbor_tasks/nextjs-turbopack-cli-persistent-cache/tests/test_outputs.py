"""
Task: nextjs-turbopack-cli-persistent-cache
Repo: vercel/next.js @ 7d451fe01e7a42be4aa9dc12e13e2017c1f0483d
PR:   91657

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: All tests are structural (source inspection) because this is a Rust
project requiring the full turbopack workspace (~200 crates) to compile —
no Rust toolchain in the Docker image, cargo check would exceed timeout.
"""

import re
import os
from pathlib import Path

REPO = "/workspace/next.js"
CLI_DIR = f"{REPO}/turbopack/crates/turbopack-cli"
ARGS_FILE = f"{CLI_DIR}/src/arguments.rs"
DEV_FILE = f"{CLI_DIR}/src/dev/mod.rs"
BUILD_FILE = f"{CLI_DIR}/src/build/mod.rs"
BUILD_RS = f"{CLI_DIR}/build.rs"
CARGO_FILE = f"{CLI_DIR}/Cargo.toml"
BENCH_FILE = f"{CLI_DIR}/benches/small_apps.rs"


def strip_rust_comments(src: str) -> str:
    """Remove Rust // and /* */ comments so keyword-in-comment tricks fail."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return "\n".join(
        line[: line.index("//")] if "//" in line else line
        for line in src.split("\n")
    )


def extract_struct_body(code: str, struct_name: str) -> str:
    """Extract the body of a Rust struct (between braces) using depth tracking."""
    start = code.index(f"struct {struct_name}")
    brace_pos = code.index("{", start)
    depth, i = 1, brace_pos + 1
    while depth > 0 and i < len(code):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
        i += 1
    return code[brace_pos:i]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cli_flags_in_common_arguments():
    """persistent_caching and cache_dir declared as fields in CommonArguments."""
    code = strip_rust_comments(Path(ARGS_FILE).read_text())

    assert "struct CommonArguments" in code, (
        "CommonArguments struct not found (after stripping comments)"
    )

    body = extract_struct_body(code, "CommonArguments")

    assert re.search(r"persistent_caching\s*:", body), (
        "persistent_caching not declared as a field in CommonArguments"
    )
    assert re.search(r"cache_dir\s*:", body), (
        "cache_dir not declared as a field in CommonArguments"
    )
    # Must have CLI arg registration via clap or arg derive macro
    assert re.search(r"#\[(clap|arg)\s*\(", code), (
        "No #[clap(...)] or #[arg(...)] attribute found"
    )


# [pr_diff] fail_to_pass
def test_build_rs_git_version_embedding():
    """build.rs exists with vergen-based git version embedding."""
    assert os.path.exists(BUILD_RS), "build.rs does not exist"

    code = strip_rust_comments(Path(BUILD_RS).read_text())

    assert re.search(r"fn\s+main\s*\(", code), "build.rs has no fn main()"
    assert "vergen" in code.lower() or "gitcl" in code.lower(), (
        "build.rs does not reference vergen/gitcl in code"
    )
    assert "describe" in code.lower(), (
        "build.rs does not configure git describe"
    )
    assert "emit" in code.lower(), (
        "build.rs does not emit build instructions"
    )
    # Anti-stub: must have >=5 non-empty code lines
    code_lines = [l for l in code.split("\n") if l.strip()]
    assert len(code_lines) >= 5, (
        f"build.rs only has {len(code_lines)} code lines — likely stubbed"
    )


# [pr_diff] fail_to_pass
def test_backend_supports_both_storage_modes():
    """Backend type alias supports persistent+noop storage with conditional selection."""
    for path, label in [(DEV_FILE, "dev/mod.rs"), (BUILD_FILE, "build/mod.rs")]:
        code = strip_rust_comments(Path(path).read_text())

        alias_match = re.search(r"type\s+Backend\s*=", code)
        assert alias_match, f"{label}: No 'type Backend =' alias found"

        alias_start = alias_match.start()
        semi = code.index(";", alias_start)
        alias_text = code[alias_start:semi]

        # Must NOT be just NoopBackingStorage — needs dispatch mechanism
        has_noop_only = (
            "NoopBackingStorage" in alias_text
            and not re.search(
                r"(TurboBackingStorage|Persistent|Either|enum|dyn\s)", alias_text
            )
        )
        assert not has_noop_only, (
            f"{label}: Backend still hardcoded to NoopBackingStorage only"
        )

        assert "persistent_caching" in code, (
            f"{label}: Does not reference persistent_caching flag"
        )

        assert re.search(r"\b(if|match)\b", code), (
            f"{label}: No conditional (if/match) logic for storage selection"
        )


# [pr_diff] fail_to_pass
def test_cargo_toml_dependencies():
    """Cargo.toml has type-dispatch crate in deps and vergen in build-deps."""
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            tomllib = None

    if tomllib:
        with open(CARGO_FILE, "rb") as f:
            cargo = tomllib.load(f)

        deps = cargo.get("dependencies", {})
        build_deps = cargo.get("build-dependencies", {})

        assert any(k in deps for k in ["either", "enum_dispatch", "auto_enums"]), (
            "No type-dispatch crate (either/enum_dispatch) in [dependencies]"
        )
        assert any("vergen" in k for k in build_deps), (
            "No vergen variant in [build-dependencies]"
        )
    else:
        raw = Path(CARGO_FILE).read_text()
        assert "either" in raw or "enum_dispatch" in raw, (
            "No type-dispatch crate in Cargo.toml"
        )
        assert "vergen" in raw, "No vergen variant in Cargo.toml"


# [pr_diff] fail_to_pass
def test_storage_init_and_cache_invalidation():
    """Dev/build modules initialize persistent storage and warn on cache invalidation."""
    found_storage_init = False
    found_warning = False

    for path in [DEV_FILE, BUILD_FILE]:
        code = strip_rust_comments(Path(path).read_text())

        if re.search(
            r"(turbo_backing_storage|TurboBackingStorage\s*::\s*new|backing_storage\s*\()",
            code,
        ):
            found_storage_init = True

        if re.search(
            r"(eprintln|warn|println)\s*!?\s*\(.*invalidat",
            code,
            re.IGNORECASE | re.DOTALL,
        ):
            found_warning = True
        if re.search(
            r"invalidat.*\bcache\b|\bcache\b.*invalidat", code, re.IGNORECASE
        ):
            found_warning = True

    assert found_storage_init, (
        "No persistent storage initialization found in dev/build modules"
    )
    assert found_warning, (
        "No cache invalidation warning found in dev/build modules"
    )


# [pr_diff] fail_to_pass
def test_bench_file_includes_new_fields():
    """Bench file includes persistent_caching and cache_dir field assignments."""
    assert os.path.exists(BENCH_FILE), "bench file does not exist"

    code = strip_rust_comments(Path(BENCH_FILE).read_text())

    assert re.search(r"persistent_caching\s*:", code), (
        "bench file missing persistent_caching field assignment"
    )
    assert re.search(r"cache_dir\s*:", code), (
        "bench file missing cache_dir field assignment"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_cli_args_preserved():
    """Existing CLI args (log_detail, log_level, etc.) still present."""
    src = Path(ARGS_FILE).read_text()

    required = ["log_detail", "log_level", "full_stats", "worker_threads"]
    missing = [f for f in required if f not in src]
    assert not missing, f"Existing fields removed: {missing}"

    assert "struct CommonArguments" in src, "CommonArguments struct removed"


# [static] pass_to_pass
def test_key_files_not_stubbed():
    """Key source files have substantial content (>=50 lines each)."""
    for path in [ARGS_FILE, DEV_FILE, BUILD_FILE]:
        lines = len(Path(path).read_text().splitlines())
        assert lines >= 50, (
            f"{os.path.basename(path)} only has {lines} lines — likely stubbed"
        )
