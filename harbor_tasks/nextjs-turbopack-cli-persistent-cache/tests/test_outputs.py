"""
Task: nextjs-turbopack-cli-persistent-cache
Repo: vercel/next.js @ 7d451fe01e7a42be4aa9dc12e13e2017c1f0483d
PR:   91657

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Rust project — no compiler in Docker image. All f2p tests use subprocess.run()
to execute Python validation scripts that parse and verify the Rust source.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/next.js"
CLI_DIR = f"{REPO}/turbopack/crates/turbopack-cli"
ARGS_FILE = f"{CLI_DIR}/src/arguments.rs"
DEV_FILE = f"{CLI_DIR}/src/dev/mod.rs"
BUILD_FILE = f"{CLI_DIR}/src/build/mod.rs"
BUILD_RS = f"{CLI_DIR}/build.rs"
CARGO_FILE = f"{CLI_DIR}/Cargo.toml"
BENCH_FILE = f"{CLI_DIR}/benches/small_apps.rs"


def _run_check(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a Python validation script to a temp file and execute it."""
    fd, path = tempfile.mkstemp(suffix=".py", prefix="_eval_")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        return subprocess.run(
            ["python3", path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------


def test_cli_flags_in_common_arguments():
    """persistent_caching: bool and cache_dir: Option<PathBuf> in CommonArguments with clap."""
    r = _run_check(
        """
import re, sys
from pathlib import Path

src = Path("{ARGS}").read_text()

if "struct CommonArguments" not in src:
    sys.exit("CommonArguments struct not found")

# Extract struct body with depth tracking
start = src.index("struct CommonArguments")
brace_pos = src.index("{", start)
depth, i = 1, brace_pos + 1
while depth > 0 and i < len(src):
    if src[i] == "{":
        depth += 1
    elif src[i] == "}":
        depth -= 1
    i += 1
body = src[brace_pos:i]

# Verify persistent_caching has type bool
if not re.search(r"persistent_caching\\s*:\\s*bool", body):
    sys.exit("persistent_caching: bool not found in CommonArguments struct body")

# Verify cache_dir has type Option<PathBuf>
if not re.search(r"cache_dir\\s*:\\s*Option\\s*<\\s*PathBuf\\s*>", body):
    sys.exit("cache_dir: Option<PathBuf> not found in CommonArguments struct body")

# Verify #[clap(long)] attribute on both fields
lines_after = src[start:]
pclap = re.findall(r"#\\[clap\\([^)]*long[^)]*\\)\\]\\s*(?:pub\\s+)?(?:persistent_caching|cache_dir)", lines_after)
if len(pclap) < 2:
    sys.exit("Both persistent_caching and cache_dir must have #[clap(long)] attribute")

print("PASS")
""".format(ARGS=ARGS_FILE)
    )
    assert r.returncode == 0, f"Check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_build_rs_git_version_embedding():
    """build.rs uses vergen-gitcl to embed git version with CI-aware dirty flag."""
    r = _run_check(
        """
import re, sys, os
from pathlib import Path

path = "{BUILD_RS}"
if not os.path.exists(path):
    sys.exit("build.rs does not exist")

src = Path(path).read_text()

# Must have fn main returning Result
if not re.search(r"fn\\s+main\\s*\\(.*\\)\\s*->\\s*.*Result", src):
    sys.exit("build.rs has no fn main() -> Result")

# Must use vergen_gitcl crate
if "vergen_gitcl" not in src:
    sys.exit("build.rs does not reference vergen_gitcl")

# Must configure .describe() with tags, dirty, and match pattern
if not re.search(r"\\.describe\\s*\\(", src):
    sys.exit("build.rs does not configure .describe()")

# Must use .dirty() for untracked file handling
if not re.search(r"\\.dirty\\s*\\(", src):
    sys.exit("build.rs does not configure .dirty()")

# Must emit via Emitter
if "Emitter" not in src or ".emit()" not in src:
    sys.exit("build.rs does not emit via vergen Emitter")

# Must handle CI env var for dirty suffix suppression
if "rerun-if-env-changed=CI" not in src:
    sys.exit("build.rs missing cargo:rerun-if-env-changed=CI")

# Anti-stub: must have >= 10 non-empty, non-comment code lines
code_lines = [
    l for l in src.split("\\n")
    if l.strip() and not l.strip().startswith("//")
]
if len(code_lines) < 10:
    sys.exit("build.rs only has " + str(len(code_lines)) + " code lines — likely stubbed")

print("PASS")
""".format(BUILD_RS=BUILD_RS)
    )
    assert r.returncode == 0, f"Check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_backend_supports_both_storage_modes():
    """Backend type uses Either<TurboBackingStorage, NoopBackingStorage> with conditional branching."""
    r = _run_check(
        """
import re, sys
from pathlib import Path

for path, label in [("{DEV}", "dev/mod.rs"), ("{BUILD}", "build/mod.rs")]:
    src = Path(path).read_text()

    # Backend must use Either with both storage types
    if not re.search(
        r"type\\s+Backend\\s*=\\s*TurboTasksBackend\\s*<\\s*Either\\s*<",
        src,
    ):
        sys.exit(label + ": Backend type does not use Either<Turbo...>")

    if "TurboBackingStorage" not in src:
        sys.exit(label + ": TurboBackingStorage not referenced")
    if "NoopBackingStorage" not in src:
        sys.exit(label + ": NoopBackingStorage not referenced")

    # Must import Either
    if "use either::Either" not in src:
        sys.exit(label + ": Missing 'use either::Either' import")

    # Must branch on persistent_caching flag
    if "persistent_caching" not in src:
        sys.exit(label + ": persistent_caching flag not referenced")

    # Must use Either::Left for persistent and Either::Right for noop
    if "Either::Left" not in src:
        sys.exit(label + ": No Either::Left branch (persistent storage)")
    if "Either::Right" not in src:
        sys.exit(label + ": No Either::Right branch (noop storage)")

print("PASS")
""".format(DEV=DEV_FILE, BUILD=BUILD_FILE)
    )
    assert r.returncode == 0, f"Check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_cargo_toml_dependencies():
    """Cargo.toml has either in deps and vergen-gitcl + anyhow in build-deps."""
    r = _run_check(
        """
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

with open("{CARGO}", "rb") as f:
    cargo = tomllib.load(f)

deps = cargo.get("dependencies", {})
build_deps = cargo.get("build-dependencies", {})

if "either" not in deps:
    sys.exit("No 'either' in [dependencies]")

if "vergen-gitcl" not in build_deps:
    sys.exit("No 'vergen-gitcl' in [build-dependencies]")

if "anyhow" not in build_deps:
    sys.exit("No 'anyhow' in [build-dependencies]")

print("PASS")
""".format(CARGO=CARGO_FILE)
    )
    assert r.returncode == 0, f"Check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_storage_init_and_cache_invalidation():
    """Dev/build modules init persistent storage, use env! for version, and warn on invalidation."""
    r = _run_check(
        """
import re, sys
from pathlib import Path

found_init = False
found_version_env = False
found_storage_mode = False
found_warning = False
found_read_only = False

for path, label in [("{DEV}", "dev"), ("{BUILD}", "build")]:
    src = Path(path).read_text()

    # Must call turbo_backing_storage()
    if "turbo_backing_storage(" in src:
        found_init = True

    # Must use env!("VERGEN_GIT_DESCRIBE") for compile-time version
    if 'env!("VERGEN_GIT_DESCRIBE")' in src:
        found_version_env = True

    # Must construct GitVersionInfo
    if "GitVersionInfo" in src:
        found_version_env = True

    # Must select StorageMode based on conditions
    if "StorageMode::" in src:
        found_storage_mode = True

    # Must check TURBO_ENGINE_READ_ONLY env var
    if "TURBO_ENGINE_READ_ONLY" in src:
        found_read_only = True

    # Must print cache invalidation warning
    if re.search(r"cache was invalidated", src, re.IGNORECASE):
        found_warning = True

    # Must handle StartupCacheState
    if "StartupCacheState" in src:
        pass  # proper invalidation detection

if not found_init:
    sys.exit("No turbo_backing_storage() call found")
if not found_version_env:
    sys.exit("No env!(VERGEN_GIT_DESCRIBE) or GitVersionInfo found")
if not found_storage_mode:
    sys.exit("No StorageMode selection found")
if not found_warning:
    sys.exit("No cache invalidation warning found")
if not found_read_only:
    sys.exit("No TURBO_ENGINE_READ_ONLY env var check found")

print("PASS")
""".format(DEV=DEV_FILE, BUILD=BUILD_FILE)
    )
    assert r.returncode == 0, f"Check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


def test_bench_file_includes_new_fields():
    """Bench file has persistent_caching: false and cache_dir: None in struct init."""
    r = _run_check(
        """
import re, sys, os
from pathlib import Path

path = "{BENCH}"
if not os.path.exists(path):
    sys.exit("bench file does not exist")

src = Path(path).read_text()

if not re.search(r"persistent_caching\\s*:\\s*false", src):
    sys.exit("bench file missing 'persistent_caching: false' field init")

if not re.search(r"cache_dir\\s*:\\s*None", src):
    sys.exit("bench file missing 'cache_dir: None' field init")

print("PASS")
""".format(BENCH=BENCH_FILE)
    )
    assert r.returncode == 0, f"Check failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


def test_existing_cli_args_preserved():
    """Existing CLI args (log_detail, log_level, full_stats, worker_threads) still present."""
    src = Path(ARGS_FILE).read_text()

    required = ["log_detail", "log_level", "full_stats", "worker_threads"]
    missing = [f for f in required if f not in src]
    assert not missing, f"Existing fields removed: {missing}"
    assert "struct CommonArguments" in src, "CommonArguments struct removed"


def test_key_files_not_stubbed():
    """Key source files have substantial content (>=50 lines each)."""
    for path in [ARGS_FILE, DEV_FILE, BUILD_FILE]:
        lines = len(Path(path).read_text().splitlines())
        assert lines >= 50, (
            f"{os.path.basename(path)} only has {lines} lines — likely stubbed"
        )
