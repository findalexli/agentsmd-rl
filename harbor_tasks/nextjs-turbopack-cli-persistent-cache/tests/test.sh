#!/usr/bin/env bash
# Verifier for nextjs-turbopack-cli-persistent-cache
#
# All checks are structural (comment-stripped source inspection) because:
# - Rust code requiring the full turbopack workspace (~200 crates) to compile
# - No Rust toolchain in the Docker image
# - cargo check would exceed timeout even if Rust were installed
#
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

CLI_DIR="/workspace/next.js/turbopack/crates/turbopack-cli"
ARGS_FILE="$CLI_DIR/src/arguments.rs"
DEV_FILE="$CLI_DIR/src/dev/mod.rs"
BUILD_FILE="$CLI_DIR/src/build/mod.rs"
BUILD_RS="$CLI_DIR/build.rs"
CARGO_FILE="$CLI_DIR/Cargo.toml"
BENCH_FILE="$CLI_DIR/benches/small_apps.rs"

###############################################################################
# GATE: Source files exist
###############################################################################
for f in "$ARGS_FILE" "$DEV_FILE" "$BUILD_FILE" "$CARGO_FILE"; do
    if [ ! -f "$f" ]; then
        echo "GATE FAILED: $f missing"
        echo "0.0" > "$REWARD_FILE"
        exit 0
    fi
done
echo "GATE PASSED"

SCORE="0.0"

###############################################################################
# Shared Python helper — strips Rust line + block comments
###############################################################################
STRIP_COMMENTS='
import re
def strip_comments(src):
    """Remove Rust // and /* */ comments so keyword-in-comment tricks fail."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return "\n".join(
        line[:line.index("//")] if "//" in line else line
        for line in src.split("\n")
    )
'

###############################################################################
# TEST 1 [pr_diff] (0.25): persistent_caching + cache_dir as struct fields
# Strips comments, extracts CommonArguments struct body, checks field decls.
# Accepts #[clap(...)] or #[arg(...)] for CLI registration.
###############################################################################
echo ""
echo "TEST 1: [pr_diff] (0.25) CLI flags in CommonArguments"
python3 << PYEOF
import re, sys
$STRIP_COMMENTS

with open("$ARGS_FILE") as f:
    code = strip_comments(f.read())

# CommonArguments struct must exist in actual code
if "struct CommonArguments" not in code:
    print("FAIL: CommonArguments struct not found (after stripping comments)")
    sys.exit(1)

# Extract struct body via brace-depth tracking
start = code.index("struct CommonArguments")
brace_pos = code.index("{", start)
depth, i = 1, brace_pos + 1
while depth > 0 and i < len(code):
    if code[i] == "{": depth += 1
    elif code[i] == "}": depth -= 1
    i += 1
struct_body = code[brace_pos:i]

# Field declarations: <name> : <type> inside the struct
if not re.search(r"persistent_caching\s*:", struct_body):
    print("FAIL: persistent_caching not declared as a field in CommonArguments")
    sys.exit(1)

if not re.search(r"cache_dir\s*:", struct_body):
    print("FAIL: cache_dir not declared as a field in CommonArguments")
    sys.exit(1)

# Must have CLI arg registration — accepts both clap and arg derive macros
if not re.search(r"#\[(clap|arg)\s*\(", code):
    print("FAIL: No #[clap(...)] or #[arg(...)] attribute found")
    sys.exit(1)

print("PASS")
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.25)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 2 [pr_diff] (0.15): build.rs creates git version embedding
# Checks that build.rs exists, has fn main(), references vergen, and has
# enough real code lines to not be a stub.
###############################################################################
echo ""
echo "TEST 2: [pr_diff] (0.15) build.rs with git version embedding"
python3 << PYEOF
import re, sys, os
$STRIP_COMMENTS

path = "$BUILD_RS"
if not os.path.exists(path):
    print("FAIL: build.rs does not exist")
    sys.exit(1)

with open(path) as f:
    code = strip_comments(f.read())

# Must have a fn main (Cargo build script entry point)
if not re.search(r"fn\s+main\s*\(", code):
    print("FAIL: build.rs has no fn main()")
    sys.exit(1)

# Must reference vergen (any variant) for git version embedding
if "vergen" not in code.lower() and "gitcl" not in code.lower():
    print("FAIL: build.rs does not reference vergen/gitcl in code (comments stripped)")
    sys.exit(1)

# Must configure git describe (the version string source)
if "describe" not in code.lower():
    print("FAIL: build.rs does not configure git describe")
    sys.exit(1)

# Must have emit/build logic
if "emit" not in code.lower():
    print("FAIL: build.rs does not emit build instructions")
    sys.exit(1)

# Anti-stub: must have >=5 non-empty code lines
code_lines = [l for l in code.split("\n") if l.strip()]
if len(code_lines) < 5:
    print(f"FAIL: build.rs only has {len(code_lines)} code lines — likely stubbed")
    sys.exit(1)

print("PASS")
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 3 [pr_diff] (0.20): Backend type supports both storage modes
# Checks that the Backend type alias is NOT hardcoded to NoopBackingStorage
# alone, and that there is conditional logic tied to persistent_caching.
# Accepts Either<A,B>, custom enums, or trait objects as dispatch mechanism.
###############################################################################
echo ""
echo "TEST 3: [pr_diff] (0.20) Backend supports persistent + noop storage"
python3 << PYEOF
import re, sys
$STRIP_COMMENTS

errors = []
for path, label in [
    ("$DEV_FILE", "dev/mod.rs"),
    ("$BUILD_FILE", "build/mod.rs"),
]:
    with open(path) as f:
        code = strip_comments(f.read())

    # Must have a Backend type alias
    alias_match = re.search(r"type\s+Backend\s*=", code)
    if not alias_match:
        errors.append(f"{label}: No 'type Backend =' alias found in code")
        continue

    # Extract the type alias text up to the semicolon
    alias_start = alias_match.start()
    semi = code.index(";", alias_start)
    alias_text = code[alias_start:semi]

    # The alias must NOT be just NoopBackingStorage — it must include a
    # persistent storage type or a dispatch mechanism (Either, enum, dyn)
    has_noop_only = ("NoopBackingStorage" in alias_text and
                     not re.search(r"(TurboBackingStorage|Persistent|Either|enum|dyn\s)", alias_text))
    if has_noop_only:
        errors.append(f"{label}: Backend still hardcoded to NoopBackingStorage only")
        continue

    # Must reference the persistent_caching flag somewhere in the file
    if "persistent_caching" not in code:
        errors.append(f"{label}: Does not reference persistent_caching flag")
        continue

    # Must have conditional logic (if or match) to select storage mode
    has_conditional = bool(re.search(r"\b(if|match)\b", code))
    if not has_conditional:
        errors.append(f"{label}: No conditional (if/match) logic for storage selection")
        continue

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    sys.exit(1)

print("PASS")
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.20)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 4 [pr_diff] (0.10): Cargo.toml has required dependencies
# Uses Python tomllib for proper TOML parsing — checks type-dispatch crate
# in [dependencies] and vergen variant in [build-dependencies].
###############################################################################
echo ""
echo "TEST 4: [pr_diff] (0.10) Cargo.toml dependencies"
python3 << PYEOF
import sys
try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        # Fallback to raw text if no TOML parser
        tomllib = None

path = "$CARGO_FILE"

if tomllib:
    with open(path, "rb") as f:
        cargo = tomllib.load(f)

    deps = cargo.get("dependencies", {})
    build_deps = cargo.get("build-dependencies", {})

    # Type-dispatch crate (either, enum_dispatch, etc.) in runtime deps
    has_dispatch = any(k in deps for k in ["either", "enum_dispatch", "auto_enums"])
    if not has_dispatch:
        print("FAIL: No type-dispatch crate (either/enum_dispatch) in [dependencies]")
        sys.exit(1)

    # Git version embedding crate in build deps
    has_vergen = any("vergen" in k for k in build_deps)
    if not has_vergen:
        print("FAIL: No vergen variant in [build-dependencies]")
        sys.exit(1)
else:
    # Raw text fallback (less robust)
    with open(path) as f:
        raw = f.read()
    if "either" not in raw and "enum_dispatch" not in raw:
        print("FAIL: No type-dispatch crate in Cargo.toml")
        sys.exit(1)
    if "vergen" not in raw:
        print("FAIL: No vergen variant in Cargo.toml")
        sys.exit(1)

print("PASS")
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 5 [repo_tests] (0.10): Pass-to-pass — existing CLI args preserved
###############################################################################
echo ""
echo "TEST 5: [repo_tests] (0.10) Existing CLI args preserved"
python3 << PYEOF
import sys

with open("$ARGS_FILE") as f:
    src = f.read()

# These fields existed before the PR and must still be present
required = ["log_detail", "log_level", "full_stats", "worker_threads"]
missing = [f for f in required if f not in src]
if missing:
    print(f"FAIL: Existing fields removed: {missing}")
    sys.exit(1)

if "struct CommonArguments" not in src:
    print("FAIL: CommonArguments struct removed")
    sys.exit(1)

print("PASS")
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 6 [pr_diff] (0.10): Storage initialization + cache invalidation
# Checks that dev/build modules initialize persistent storage (not just
# reference the type) and include cache invalidation warning logic.
###############################################################################
echo ""
echo "TEST 6: [pr_diff] (0.10) Storage initialization + cache invalidation"
python3 << PYEOF
import re, sys
$STRIP_COMMENTS

found_storage_init = False
found_warning = False

for path in ["$DEV_FILE", "$BUILD_FILE"]:
    with open(path) as f:
        code = strip_comments(f.read())

    # Must create/initialize a persistent storage instance (function call or constructor)
    if re.search(r"(turbo_backing_storage|TurboBackingStorage\s*::\s*new|backing_storage\s*\()", code):
        found_storage_init = True

    # Cache invalidation warning (eprintln!, warn!, println! with invalidation message)
    if re.search(r'(eprintln|warn|println)\s*!?\s*\(.*invalidat', code, re.IGNORECASE | re.DOTALL):
        found_warning = True
    # Also accept: storing invalidation info and printing it
    if re.search(r'invalidat.*\bcache\b|\bcache\b.*invalidat', code, re.IGNORECASE):
        found_warning = True

if not found_storage_init:
    print("FAIL: No persistent storage initialization found in dev/build modules")
    sys.exit(1)

# Warning is expected but non-blocking (partial credit already via storage init)
if not found_warning:
    print("INFO: No cache invalidation warning found (non-critical)")

print("PASS")
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 7 [pr_diff] (0.05): Bench file includes new struct fields
###############################################################################
echo ""
echo "TEST 7: [pr_diff] (0.05) Bench file includes new fields"
python3 << PYEOF
import re, sys, os
$STRIP_COMMENTS

path = "$BENCH_FILE"
if not os.path.exists(path):
    print("FAIL: bench file does not exist")
    sys.exit(1)

with open(path) as f:
    code = strip_comments(f.read())

if not re.search(r"persistent_caching\s*:", code):
    print("FAIL: bench file missing persistent_caching field assignment")
    sys.exit(1)

if not re.search(r"cache_dir\s*:", code):
    print("FAIL: bench file missing cache_dir field assignment")
    sys.exit(1)

print("PASS")
PYEOF
if [ $? -eq 0 ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "  FAIL"
fi

###############################################################################
# TEST 8 [structural] (0.05): Anti-stub — key files have substantial content
###############################################################################
echo ""
echo "TEST 8: [structural] (0.05) Anti-stub check"
PASS8=true
for f in "$ARGS_FILE" "$DEV_FILE" "$BUILD_FILE"; do
    LINES=$(wc -l < "$f")
    if [ "$LINES" -lt 50 ]; then
        echo "  FAIL: $(basename $f) only has $LINES lines — likely stubbed"
        PASS8=false
    fi
done
if [ "$PASS8" = true ]; then
    echo "  PASS"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "  FAIL"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "========================================="
echo "TOTAL SCORE: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
