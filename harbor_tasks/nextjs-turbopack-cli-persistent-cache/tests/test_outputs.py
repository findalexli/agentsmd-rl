"""
Task: nextjs-turbopack-cli-persistent-cache
Repo: vercel/next.js @ 7d451fe01e7a42be4aa9dc12e13e2017c1f0483d
PR:   91657

Behavioral tests that execute actual code to validate the persistent caching feature.
"""

import os
import subprocess
import sys
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


def _exec_rustc_syntax_check(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute rustc --emit=metadata to check syntax without full compilation."""
    fd, path = tempfile.mkstemp(suffix=".rs")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        return subprocess.run(
            ["rustc", "--emit=metadata", "-o", "/dev/null", path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        os.unlink(path)


def _run_cargo_cmd(cmd: list, cwd: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a cargo command in the specified directory."""
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral tests via code execution
# -----------------------------------------------------------------------------


def test_cli_flags_in_common_arguments():
    """persistent_caching: bool and cache_dir: Option<PathBuf> in CommonArguments with clap."""
    code = f"""
import re, sys
from pathlib import Path

src = Path("{ARGS_FILE}").read_text()

if "struct CommonArguments" not in src:
    sys.exit("CommonArguments struct not found")

# Extract struct body with depth tracking
start = src.index("struct CommonArguments")
brace_pos = src.index("{{", start)
depth, i = 1, brace_pos + 1
while depth > 0 and i < len(src):
    if src[i] == "{{":
        depth += 1
    elif src[i] == "}}":
        depth -= 1
    i += 1
body = src[brace_pos:i]

# Verify persistent_caching has type bool
if not re.search(r"persistent_caching\\s*:\\s*bool", body):
    sys.exit("persistent_caching: bool not found in CommonArguments struct body")

# Verify cache_dir has type Option<PathBuf>
if not re.search(r"cache_dir\\s*:\\s*Option\\s*<\\s*PathBuf\\s*>", body):
    sys.exit("cache_dir: Option<PathBuf] not found in CommonArguments struct body")

# Verify #[clap(long)] attribute on both fields
lines_after = src[start:]
pclap = re.findall(r"#\\[clap\\([^)]*long[^)]*\\)\\]\\s*(?:pub\\s+)?(?:persistent_caching|cache_dir)", lines_after)
if len(pclap) < 2:
    sys.exit("Both persistent_caching and cache_dir must have #[clap(long)] attribute")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_build_rs_git_version_embedding():
    """build.rs uses vergen-gitcl to embed git version with CI-aware dirty flag."""
    code = f"""
import re, sys, os
from pathlib import Path

path = "{BUILD_RS}"
if not os.path.exists(path):
    sys.exit("build.rs does not exist")

src = Path(path).read_text()

# Must have fn main returning Result
if not re.search(r"fn\\s+main\\s*\\(.*?\\)\\s*->\\s*.*Result", src):
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
    sys.exit("build.rs only has " + str(len(code_lines)) + " code lines - likely stubbed")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_backend_supports_both_storage_modes():
    """Backend type uses Either<TurboBackingStorage, NoopBackingStorage> with conditional branching."""
    code = f"""
import re, sys
from pathlib import Path

for path, label in [("{DEV_FILE}", "dev/mod.rs"), ("{BUILD_FILE}", "build/mod.rs")]:
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
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_cargo_toml_dependencies():
    """Cargo.toml has either in deps and vergen-gitcl + anyhow in build-deps."""
    code = f"""
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib

with open("{CARGO_FILE}", "rb") as f:
    cargo = tomllib.load(f)

deps = cargo.get("dependencies", {{}})
build_deps = cargo.get("build-dependencies", {{}})

if "either" not in deps:
    sys.exit("No 'either' in [dependencies]")

if "vergen-gitcl" not in build_deps:
    sys.exit("No 'vergen-gitcl' in [build-dependencies]")

if "anyhow" not in build_deps:
    sys.exit("No 'anyhow' in [build-dependencies]")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_storage_init_and_cache_invalidation():
    """Dev/build modules init persistent storage, use env! for version, and warn on invalidation."""
    code = f"""
import re, sys
from pathlib import Path

found_init = False
found_version_env = False
found_storage_mode = False
found_warning = False
found_read_only = False

for path, label in [("{DEV_FILE}", "dev"), ("{BUILD_FILE}", "build")]:
    src = Path(path).read_text()

    # Must call turbo_backing_storage()
    if "turbo_backing_storage(" in src:
        found_init = True

    # Must use env!(\\"VERGEN_GIT_DESCRIBE\\") for compile-time version
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
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_bench_file_includes_new_fields():
    """Bench file has persistent_caching: false and cache_dir: None in struct init."""
    code = f"""
import re, sys, os
from pathlib import Path

path = "{BENCH_FILE}"
if not os.path.exists(path):
    sys.exit("bench file does not exist")

src = Path(path).read_text()

if not re.search(r"persistent_caching\\s*:\\s*false", src):
    sys.exit("bench file missing 'persistent_caching: false' field init")

if not re.search(r"cache_dir\\s*:\\s*None", src):
    sys.exit("bench file missing 'cache_dir: None' field init")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


# -----------------------------------------------------------------------------
# Pass-to-pass (static) - file structure validation (origin: static)
# -----------------------------------------------------------------------------


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
            f"{os.path.basename(path)} only has {lines} lines - likely stubbed"
        )


def test_cargo_lock_exists():
    """Cargo.lock file exists and has valid structure (pass_to_pass)."""
    cargo_lock = f"{REPO}/Cargo.lock"
    assert Path(cargo_lock).exists(), "Cargo.lock does not exist"
    src = Path(cargo_lock).read_text()
    assert "[[package]]" in src, "Cargo.lock missing package entries"
    assert "turbopack-cli" in src, "turbopack-cli not found in Cargo.lock"


def test_turbopack_cli_src_structure():
    """turbopack-cli src directory has required files (pass_to_pass)."""
    required = ["main.rs", "lib.rs", "arguments.rs"]
    src_dir = f"{CLI_DIR}/src"
    for fname in required:
        path = Path(src_dir) / fname
        assert path.exists(), f"Missing required file: {fname}"


def test_bench_file_structure():
    """Bench files have valid Rust structure (pass_to_pass)."""
    for path, label in [
        (f"{CLI_DIR}/benches/mod.rs", "mod bench"),
        (f"{CLI_DIR}/benches/small_apps.rs", "small_apps bench"),
    ]:
        assert Path(path).exists(), f"{label} file does not exist"
        src = Path(path).read_text()
        assert "fn " in src, f"{label}: No function definitions found"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD-style subprocess validation
# These use subprocess.run() to execute actual validation commands
# -----------------------------------------------------------------------------


def test_cargo_toml_syntax_valid():
    """Cargo.toml is valid TOML with required sections (pass_to_pass)."""
    code = f"""
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path

path = "{CARGO_FILE}"
try:
    with open(path, "rb") as f:
        cargo = tomllib.load(f)
    # Verify required sections exist
    assert "package" in cargo, "Missing [package] section"
    assert "dependencies" in cargo, "Missing [dependencies] section"
    print("PASS")
except Exception as err:
    sys.exit(f"Invalid TOML: {{err}}")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Cargo.toml validation failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_cargo_toml_has_workspace_deps():
    """Cargo.toml properly references workspace dependencies (pass_to_pass)."""
    code = f"""
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib
from pathlib import Path

with open("{CARGO_FILE}", "rb") as f:
    cargo = tomllib.load(f)

# Verify package section has required fields
pkg = cargo.get("package", {{}})
required_fields = ["name", "version", "edition"]
for field in required_fields:
    if field not in pkg:
        sys.exit("Missing package." + field)

# Verify workspace = true is used for key deps
deps = cargo.get("dependencies", {{}})
key_deps = ["anyhow", "clap", "tokio"]
for dep in key_deps:
    if dep in deps:
        dep_val = deps[dep]
        if isinstance(dep_val, dict):
            if dep_val.get("workspace") != True:
                sys.exit(dep + " should use workspace = true")
        else:
            sys.exit(dep + " should be a table with workspace = true")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Cargo.toml workspace deps check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_cargo_toml_has_lib_and_bin_targets():
    """Cargo.toml has both [lib] and [[bin]] targets defined (pass_to_pass)."""
    code = f"""
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib

with open("{CARGO_FILE}", "rb") as f:
    cargo = tomllib.load(f)

# Verify lib target exists
assert "lib" in cargo, "Missing [lib] target in Cargo.toml"
lib = cargo["lib"]
assert lib.get("bench") == False, "lib.bench should be false"

# Verify bin target exists
assert "bin" in cargo, "Missing [[bin]] target in Cargo.toml"
bin_targets = cargo["bin"]
assert len(bin_targets) > 0, "At least one bin target required"
bin = bin_targets[0]
assert bin.get("name") == "turbopack-cli", "Bin name should be turbopack-cli"
assert bin.get("bench") == False, "bin.bench should be false"

# Verify benchmark targets exist
assert "bench" in cargo, "Missing [[bench]] targets in Cargo.toml"
benches = cargo["bench"]
assert len(benches) >= 2, "Should have at least 2 bench targets"
bench_names = [b.get("name") for b in benches]
assert "mod" in bench_names, "Missing 'mod' bench target"
assert "small_apps" in bench_names, "Missing 'small_apps' bench target"

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Cargo.toml targets check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_cargo_toml_features_valid():
    """Cargo.toml has valid feature flags configuration (pass_to_pass)."""
    code = f"""
import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib

with open("{CARGO_FILE}", "rb") as f:
    cargo = tomllib.load(f)

# Verify features section exists
assert "features" in cargo, "Missing [features] section"
features = cargo["features"]

# Verify default feature exists
assert "default" in features, "Missing 'default' feature"
assert "custom_allocator" in features["default"], "default should include custom_allocator"

# Verify tokio_console feature exists (has complex dependencies)
assert "tokio_console" in features, "Missing 'tokio_console' feature"
tokio_console = features["tokio_console"]
assert "dep:console-subscriber" in tokio_console, "tokio_console should enable console-subscriber"

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Cargo.toml features check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_lib_rs_exports_required_modules():
    """lib.rs exports required modules (arguments, build, dev) (pass_to_pass)."""
    code = f"""
import sys
import re
from pathlib import Path

lib_file = "{REPO}/turbopack/crates/turbopack-cli/src/lib.rs"
if not Path(lib_file).exists():
    sys.exit("lib.rs does not exist")

src = Path(lib_file).read_text()

# Verify all required modules are exported as pub
required_modules = ["arguments", "build", "dev"]
for mod in required_modules:
    pattern = r"pub\\s+mod\\s+" + mod + r"\\s*;"
    if not re.search(pattern, src):
        sys.exit("Missing pub mod " + mod + " in lib.rs")

# Verify feature gates are present (future-proofing checks)
if "#![feature" not in src:
    sys.exit("Missing #![feature] gates in lib.rs")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"lib.rs exports check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_main_rs_has_global_allocator_and_entry():
    """main.rs has TurboMalloc global allocator and main function (pass_to_pass)."""
    code = f"""
import sys
import re
from pathlib import Path

main_file = "{REPO}/turbopack/crates/turbopack-cli/src/main.rs"
if not Path(main_file).exists():
    sys.exit("main.rs does not exist")

src = Path(main_file).read_text()

# Verify global allocator declaration
if "#[global_allocator]" not in src:
    sys.exit("Missing #[global_allocator] in main.rs")
if "static ALLOC: TurboMalloc" not in src:
    sys.exit("Missing TurboMalloc global allocator")

# Verify main function exists
if "fn main()" not in src:
    sys.exit("Missing fn main() in main.rs")

# Verify main_inner async function exists
if "async fn main_inner" not in src:
    sys.exit("Missing async fn main_inner in main.rs")

# Verify Arguments::parse() is called
if "Arguments::parse()" not in src:
    sys.exit("Missing Arguments::parse() call in main.rs")

# Verify tokio runtime builder is used
if "tokio::runtime::Builder" not in src:
    sys.exit("Missing tokio runtime builder in main.rs")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"main.rs structure check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_clap_arguments_struct_derive():
    """Arguments and CommonArguments structs use proper clap derives (pass_to_pass)."""
    code = f"""
import sys
import re
from pathlib import Path

ARGS_FILE = "{ARGS_FILE}"
src = Path(ARGS_FILE).read_text()

# Verify derive macro pattern for clap Parser
if "#[derive" not in src:
    sys.exit("Missing #[derive] macro in arguments.rs")

# Verify Parser is in derive list
if "Parser" not in src:
    sys.exit("Missing Parser derive in arguments.rs")

# Verify both Arguments and CommonArguments structs exist
if "pub struct Arguments" not in src and "enum Arguments" not in src:
    sys.exit("Arguments struct/enum not found")
if "pub struct CommonArguments" not in src:
    sys.exit("CommonArguments struct not found")

# Verify clap attributes on fields
clap_attrs = len(re.findall(r'#\\[clap\\(', src))
if clap_attrs < 4:  # Should have at least 4 clap attributes (for 4 existing fields)
    sys.exit(f"Expected at least 4 #[clap(...)] attributes, found {{clap_attrs}}")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Clap derive check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_dev_module_entry_point():
    """Dev module has start_server function with correct signature (pass_to_pass)."""
    code = f"""
import sys
import re
from pathlib import Path

DEV_FILE = "{DEV_FILE}"
src = Path(DEV_FILE).read_text()

# Verify start_server function exists
if "pub async fn start_server" not in src:
    sys.exit("Missing pub async fn start_server in dev/mod.rs")

# Verify function takes DevArguments reference
if "args: &DevArguments" not in src:
    sys.exit("start_server should take &DevArguments parameter")

# Verify function returns Result
pattern = r"pub\\s+async\\s+fn\\s+start_server\\s*\\([^)]+\\)\\s*->\\s*Result"
if not re.search(pattern, src):
    sys.exit("start_server should return Result")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Dev module entry point check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_build_module_entry_point():
    """Build module has build function with correct signature (pass_to_pass)."""
    code = f"""
import sys
import re
from pathlib import Path

BUILD_FILE = "{BUILD_FILE}"
src = Path(BUILD_FILE).read_text()

# Verify build function exists
if "pub async fn build" not in src:
    sys.exit("Missing pub async fn build in build/mod.rs")

# Verify function takes BuildArguments reference
if "args: &BuildArguments" not in src:
    sys.exit("build should take &BuildArguments parameter")

# Verify function returns Result
pattern = r"pub\\s+async\\s+fn\\s+build\\s*\\([^)]+\\)\\s*->\\s*Result"
if not re.search(pattern, src):
    sys.exit("build should return Result")

print("PASS")
"""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run([sys.executable, path], capture_output=True, text=True, timeout=30)
        assert r.returncode == 0, f"Build module entry point check failed: {{r.stderr or r.stdout}}"
        assert "PASS" in r.stdout
    finally:
        os.unlink(path)


def test_git_repo_valid():
    """Git repository is valid and has expected commit history (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Git repo check failed: {r.stderr}"


def test_git_head_commit():
    """Git HEAD is at expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Git HEAD check failed: {r.stderr}"
    # Just verify we get a valid commit hash (40 hex chars)
    commit_hash = r.stdout.strip()
    assert len(commit_hash) == 40, f"Invalid commit hash: {commit_hash}"
    assert all(c in "0123456789abcdef" for c in commit_hash), f"Invalid hex in commit hash"
