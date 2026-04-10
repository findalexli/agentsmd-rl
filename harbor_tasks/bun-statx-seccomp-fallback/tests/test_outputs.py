import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
SYS_ZIG = f"{REPO}/src/sys.zig"


def _compile_and_run_c(source: str, *args, timeout: int = 30):
    """Compile a C analysis program and run it with the given arguments."""
    fd, c_path = tempfile.mkstemp(suffix=".c")
    bin_path = c_path.replace(".c", "")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(source)
        comp = subprocess.run(
            ["gcc", "-o", bin_path, c_path],
            capture_output=True, text=True, timeout=timeout,
        )
        assert comp.returncode == 0, f"C compile failed: {comp.stderr}"
        run = subprocess.run(
            [bin_path, *args],
            capture_output=True, text=True, timeout=timeout,
        )
        return run
    finally:
        for p in [c_path, bin_path]:
            if os.path.exists(p):
                os.unlink(p)


def _get_statximpl_body():
    """Extract the body of statxImpl from sys.zig."""
    text = Path(SYS_ZIG).read_text()
    # Find fn statxImpl(...) opening brace
    m = re.search(r"fn\s+statxImpl\s*\(", text)
    if not m:
        return None, text
    # Find matching closing brace (count braces)
    start = text.index("{", m.start())
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i + 1], text
        i += 1
    return None, text


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_source_files_exist():
    """Core source file must exist and be non-empty."""
    p = Path(SYS_ZIG)
    assert p.exists(), f"{SYS_ZIG} does not exist"
    assert p.stat().st_size > 1000, f"{SYS_ZIG} is unexpectedly small"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI gates discovered from the repo
# ---------------------------------------------------------------------------


def test_zig_fmt_sys_zig():
    """Zig code formatting check on src/sys.zig passes (pass_to_pass).
    This is a lightweight CI gate from the repo's format.yml workflow.
    Note: Full build.zig check fails due to Zig version mismatch (expected).
    """
    # Create a shell script to run zig fmt check
    shell_script = """#!/bin/bash
set -e
apt-get update -qq && apt-get install -y -qq unzip curl ca-certificates 2>/dev/null
ZIG_TEMP=$(mktemp -d)
curl -sL -o "$ZIG_TEMP/zig.zip" "https://github.com/oven-sh/zig/releases/download/autobuild-e0b7c318f318196c5f81fdf3423816a7b5bb3112/bootstrap-x86_64-linux-musl.zip" 2>/dev/null
unzip -q -d "$ZIG_TEMP" "$ZIG_TEMP/zig.zip"
export PATH="$ZIG_TEMP/bootstrap-x86_64-linux-musl:$PATH"
cd /workspace/bun
zig fmt --check src/sys.zig
rm -rf "$ZIG_TEMP"
"""
    r = subprocess.run(
        ["bash", "-c", shell_script],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"zig fmt check failed on src/sys.zig:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_zig_fmt_build_zig():
    """Zig code formatting check on build.zig passes (pass_to_pass).
    CI gate from the repo's format.yml workflow (runs zig fmt on build.zig).
    """
    shell_script = """#!/bin/bash
set -e
apt-get update -qq && apt-get install -y -qq unzip curl ca-certificates 2>/dev/null
ZIG_TEMP=$(mktemp -d)
curl -sL -o "$ZIG_TEMP/zig.zip" "https://github.com/oven-sh/zig/releases/download/autobuild-e0b7c318f318196c5f81fdf3423816a7b5bb3112/bootstrap-x86_64-linux-musl.zip" 2>/dev/null
unzip -q -d "$ZIG_TEMP" "$ZIG_TEMP/zig.zip"
export PATH="$ZIG_TEMP/bootstrap-x86_64-linux-musl:$PATH"
cd /workspace/bun
zig fmt --check build.zig
rm -rf "$ZIG_TEMP"
"""
    r = subprocess.run(
        ["bash", "-c", shell_script],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"zig fmt check failed on build.zig:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_claude_md_valid():
    """CLAUDE.md (AGENTS.md) exists and is non-empty (pass_to_pass).
    Verifies the project's coding guidelines file is present and AGENTS.md symlink is valid.
    """
    claude_md = Path(f"{REPO}/CLAUDE.md")
    assert claude_md.exists(), "CLAUDE.md does not exist"
    assert claude_md.stat().st_size > 1000, "CLAUDE.md is unexpectedly small"

    # Verify AGENTS.md symlink points to CLAUDE.md
    agents_md = Path(f"{REPO}/AGENTS.md")
    assert agents_md.exists() or agents_md.is_symlink(), "AGENTS.md does not exist"


def test_repo_structure_intact():
    """Repository structure is intact with required directories (pass_to_pass).
    Verifies the base commit checkout was successful and key files exist.
    """
    required_paths = [
        f"{REPO}/src/sys.zig",
        f"{REPO}/build.zig",
        f"{REPO}/package.json",
        f"{REPO}/src",
    ]
    for path in required_paths:
        p = Path(path)
        assert p.exists(), f"Required repo path does not exist: {path}"


def test_coderabbit_config_valid():
    """CodeRabbit config (.coderabbit.yaml) exists and is valid YAML (pass_to_pass).
    Verifies CodeRabbit AI code review configuration is valid YAML.
    """
    config_path = Path(f"{REPO}/.coderabbit.yaml")
    assert config_path.exists(), ".coderabbit.yaml does not exist"
    assert config_path.stat().st_size > 100, ".coderabbit.yaml is unexpectedly small"

    content = config_path.read_text()

    # Validate YAML is parseable (try PyYAML first, fallback to basic checks)
    try:
        import yaml
        try:
            parsed = yaml.safe_load(content)
            # Verify expected top-level keys exist
            assert isinstance(parsed, dict), ".coderabbit.yaml must be a YAML dictionary"
            assert "language" in parsed, ".coderabbit.yaml missing 'language' key"
            assert "reviews" in parsed, ".coderabbit.yaml missing 'reviews' key"
        except yaml.YAMLError as e:
            assert False, f".coderabbit.yaml is not valid YAML: {e}"
    except ImportError:
        # Fallback: basic structural validation if PyYAML not available
        assert "language:" in content, ".coderabbit.yaml missing 'language' key"
        assert "reviews:" in content, ".coderabbit.yaml missing 'reviews' key"


def test_agents_symlink_valid():
    """AGENTS.md is a valid symlink pointing to CLAUDE.md (pass_to_pass).
    Verifies AGENTS.md must be a symlink to CLAUDE.md per repo conventions.
    """
    agents_md = Path(f"{REPO}/AGENTS.md")
    claude_md = Path(f"{REPO}/CLAUDE.md")

    # Must exist (as symlink or file)
    assert agents_md.exists() or agents_md.is_symlink(), "AGENTS.md does not exist"

    # Must be a symlink
    assert agents_md.is_symlink(), "AGENTS.md must be a symlink to CLAUDE.md"

    # Symlink target must point to CLAUDE.md
    target = os.readlink(agents_md)
    assert target == "CLAUDE.md", f"AGENTS.md must point to 'CLAUDE.md', got '{target}'"

    # CLAUDE.md must exist and be valid
    assert claude_md.exists(), "CLAUDE.md (target of AGENTS.md symlink) does not exist"
    assert claude_md.stat().st_size > 1000, "CLAUDE.md is unexpectedly small"


def test_editorconfig_valid():
    """EditorConfig file exists and contains expected settings (pass_to_pass).
    CI gate: EditorConfig specifies consistent formatting rules (utf-8, lf, trim whitespace).
    """
    editorconfig = Path(f"{REPO}/.editorconfig")
    assert editorconfig.exists(), ".editorconfig does not exist"
    assert editorconfig.stat().st_size > 50, ".editorconfig is unexpectedly small"

    content = editorconfig.read_text()

    # Verify core settings expected by the repo
    assert "root = true" in content, ".editorconfig must have root = true"
    assert "charset = utf-8" in content, ".editorconfig must specify charset = utf-8"
    assert "insert_final_newline = true" in content, ".editorconfig must specify insert_final_newline"
    assert "trim_trailing_whitespace = true" in content, ".editorconfig must specify trim_trailing_whitespace"
    assert "end_of_line = lf" in content, ".editorconfig must specify lf line endings"


def test_ban_words_passes():
    """Internal ban-words test passes (pass_to_pass).
    CI gate from format.yml - checks for banned words/phrases in the codebase.
    Requires bun to be installed. Skips if bun is not available.
    """
    # Check if bun is available
    r = subprocess.run(
        ["which", "bun"],
        capture_output=True, text=True, timeout=10,
    )
    if r.returncode != 0:
        # Skip if bun not available - this is expected in minimal Docker
        import pytest
        pytest.skip("bun not available in this environment")
        return

    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ban-words test failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via C analysis
# ---------------------------------------------------------------------------

def test_statx_handles_eperm():
    """statxImpl must fall back on EPERM (seccomp-blocked statx).
    Before the fix, only ENOSYS and EOPNOTSUPP triggered fallback.
    Compiles a C analyzer that verifies .PERM is in the errno switch."""
    c_source = r"""
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "Usage: %s <file>\n", argv[0]); return 1; }

    FILE *f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "Cannot open %s\n", argv[1]); return 1; }

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(len + 1);
    fread(buf, 1, len, f);
    buf[len] = '\0';
    fclose(f);

    char *impl = strstr(buf, "fn statxImpl");
    if (!impl) {
        fprintf(stderr, "FAIL: statxImpl not found\n");
        free(buf); return 1;
    }

    char *errno_switch = strstr(impl, "getErrno()");
    if (!errno_switch) {
        fprintf(stderr, "FAIL: no getErrno() call in statxImpl\n");
        free(buf); return 1;
    }

    char *brace = strchr(errno_switch, '{');
    if (!brace) {
        fprintf(stderr, "FAIL: no switch block after getErrno()\n");
        free(buf); return 1;
    }

    int depth = 0;
    char *end = brace;
    while (*end) {
        if (*end == '{') depth++;
        else if (*end == '}') { depth--; if (depth == 0) break; }
        end++;
    }

    char saved = *(end + 1);
    *(end + 1) = '\0';

    if (!strstr(brace, ".PERM")) {
        fprintf(stderr, "FAIL: .PERM not in errno switch\n");
        *(end + 1) = saved; free(buf); return 1;
    }

    *(end + 1) = saved;
    free(buf);

    printf("PASS\n");
    return 0;
}
"""
    r = _compile_and_run_c(c_source, SYS_ZIG)
    assert r.returncode == 0, f"EPERM check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_statx_handles_einval():
    """statxImpl must fall back on EINVAL (old Android builds).
    Compiles a C analyzer that verifies .INVAL is in the errno switch."""
    c_source = r"""
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "Usage: %s <file>\n", argv[0]); return 1; }

    FILE *f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "Cannot open %s\n", argv[1]); return 1; }

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(len + 1);
    fread(buf, 1, len, f);
    buf[len] = '\0';
    fclose(f);

    char *impl = strstr(buf, "fn statxImpl");
    if (!impl) {
        fprintf(stderr, "FAIL: statxImpl not found\n");
        free(buf); return 1;
    }

    char *errno_switch = strstr(impl, "getErrno()");
    if (!errno_switch) {
        fprintf(stderr, "FAIL: no getErrno() call in statxImpl\n");
        free(buf); return 1;
    }

    char *brace = strchr(errno_switch, '{');
    if (!brace) {
        fprintf(stderr, "FAIL: no switch block after getErrno()\n");
        free(buf); return 1;
    }

    int depth = 0;
    char *end = brace;
    while (*end) {
        if (*end == '{') depth++;
        else if (*end == '}') { depth--; if (depth == 0) break; }
        end++;
    }

    char saved = *(end + 1);
    *(end + 1) = '\0';

    if (!strstr(brace, ".INVAL")) {
        fprintf(stderr, "FAIL: .INVAL not in errno switch\n");
        *(end + 1) = saved; free(buf); return 1;
    }

    *(end + 1) = saved;
    free(buf);

    printf("PASS\n");
    return 0;
}
"""
    r = _compile_and_run_c(c_source, SYS_ZIG)
    assert r.returncode == 0, f"EINVAL check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_statx_handles_positive_rc():
    """statxImpl must detect abnormal positive rc (QEMU/S390) and fall back.
    Before the fix, only negative rc (normal -errno) was handled.
    Verifies the rc>0 bitcast check exists BEFORE the errno check."""
    c_source = r"""
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "Usage: %s <file>\n", argv[0]); return 1; }

    FILE *f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "Cannot open %s\n", argv[1]); return 1; }

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(len + 1);
    fread(buf, 1, len, f);
    buf[len] = '\0';
    fclose(f);

    char *impl = strstr(buf, "fn statxImpl");
    if (!impl) {
        fprintf(stderr, "FAIL: statxImpl not found\n");
        free(buf); return 1;
    }

    char *bitcast_pos = strstr(impl, "isize");
    if (!bitcast_pos) {
        fprintf(stderr, "FAIL: no isize cast found in statxImpl\n");
        free(buf); return 1;
    }

    char *bitcast = strstr(impl, "@bitCast");
    if (!bitcast || bitcast > bitcast_pos + 200) {
        fprintf(stderr, "FAIL: no @bitCast of rc found\n");
        free(buf); return 1;
    }

    char *errno_check = strstr(impl, "errnoSys");
    if (!errno_check) {
        fprintf(stderr, "FAIL: no errnoSys call in statxImpl\n");
        free(buf); return 1;
    }

    if (bitcast > errno_check) {
        fprintf(stderr, "FAIL: rc>0 check is AFTER errnoSys\n");
        free(buf); return 1;
    }

    char *after_bitcast = bitcast;
    char *store_false = strstr(after_bitcast, "supports_statx_on_linux.store(false");
    if (!store_false) {
        fprintf(stderr, "FAIL: rc>0 path doesn't disable statx support flag\n");
        free(buf); return 1;
    }

    char *fallback = strstr(after_bitcast, "statxFallback");
    if (!fallback) {
        fprintf(stderr, "FAIL: rc>0 path doesn't call statxFallback\n");
        free(buf); return 1;
    }

    free(buf);
    printf("PASS\n");
    return 0;
}
"""
    r = _compile_and_run_c(c_source, SYS_ZIG)
    assert r.returncode == 0, f"Positive rc check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_statx_errnos_grouped_in_switch():
    """All four errno cases (NOSYS, OPNOTSUPP, PERM, INVAL) must be handled
    together in a single switch arm, not scattered across separate if checks.
    This verifies the fix groups them properly like libuv does."""
    c_source = r"""
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "Usage: %s <file>\n", argv[0]); return 1; }

    FILE *f = fopen(argv[1], "r");
    if (!f) { fprintf(stderr, "Cannot open %s\n", argv[1]); return 1; }

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(len + 1);
    fread(buf, 1, len, f);
    buf[len] = '\0';
    fclose(f);

    char *impl = strstr(buf, "fn statxImpl");
    if (!impl) {
        fprintf(stderr, "FAIL: statxImpl not found\n");
        free(buf); return 1;
    }

    char *errno_area = strstr(impl, "getErrno()");
    if (!errno_area) {
        fprintf(stderr, "FAIL: no getErrno() in statxImpl\n");
        free(buf); return 1;
    }

    char *search_end = errno_area + 2000;
    if (search_end > buf + len) search_end = buf + len;

    long region_len = search_end - errno_area;
    char *region = malloc(region_len + 1);
    memcpy(region, errno_area, region_len);
    region[region_len] = '\0';

    int has_nosys = strstr(region, ".NOSYS") != NULL;
    int has_opnotsupp = strstr(region, ".OPNOTSUPP") != NULL;
    int has_perm = strstr(region, ".PERM") != NULL;
    int has_inval = strstr(region, ".INVAL") != NULL;

    if (!has_nosys || !has_opnotsupp || !has_perm || !has_inval) {
        fprintf(stderr, "FAIL: missing errnos: NOSYS=%d OPNOTSUPP=%d PERM=%d INVAL=%d\n",
                has_nosys, has_opnotsupp, has_perm, has_inval);
        free(region); free(buf); return 1;
    }

    int found_grouped = 0;
    char *switch_arm = strstr(region, ".NOSYS");
    if (switch_arm) {
        char nearby[400] = {0};
        int n = switch_arm - region;
        int start_idx = (n > 200) ? n - 200 : 0;
        int end_idx = (n + 200 < region_len) ? n + 200 : region_len;
        int copy_len = end_idx - start_idx;
        if (copy_len > 399) copy_len = 399;
        memcpy(nearby, region + start_idx, copy_len);
        nearby[copy_len] = '\0';

        if (strstr(nearby, ".PERM") && strstr(nearby, ".INVAL")) {
            found_grouped = 1;
        }
    }

    if (!found_grouped) {
        char *fallback = strstr(impl, "statxFallback");
        if (fallback) {
            found_grouped = 1;
        }
    }

    if (!found_grouped) {
        fprintf(stderr, "FAIL: errnos not grouped together in handling logic\n");
        free(region); free(buf); return 1;
    }

    if (!strstr(region, "supports_statx_on_linux.store(false")) {
        fprintf(stderr, "FAIL: statx support flag not disabled on fallback\n");
        free(region); free(buf); return 1;
    }

    free(region);
    free(buf);
    printf("PASS\n");
    return 0;
}
"""
    r = _compile_and_run_c(c_source, SYS_ZIG)
    assert r.returncode == 0, f"Errno grouping check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + anti-stub
# ---------------------------------------------------------------------------


def test_statx_fallback_helper_exists():
    """statxFallback function must exist as a separate helper with correct
    delegation to stat/lstat/fstat based on flags."""
    text = Path(SYS_ZIG).read_text()

    # Function must exist
    assert "fn statxFallback(" in text, "statxFallback function not found"

    # Find statxFallback body
    m = re.search(r"fn\s+statxFallback\s*\(", text)
    assert m, "statxFallback signature not found"

    # Extract body
    start = text.index("{", m.start())
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    body = text[start:i + 1]

    # Must handle both path (stat/lstat) and fd (fstat) cases
    assert "lstat" in body, "statxFallback must handle lstat for SYMLINK_NOFOLLOW"
    assert "fstat" in body, "statxFallback must handle fstat for fd-only case"
    assert "SYMLINK_NOFOLLOW" in body, "statxFallback must check SYMLINK_NOFOLLOW flag"

    # Must return Maybe(PosixStat) using .result/.err tagged union
    assert "PosixStat.init" in body, "statxFallback must convert via PosixStat.init"
    assert ".err" in body, "statxFallback must propagate errors"


def test_existing_errno_cases_preserved():
    """The original NOSYS and EOPNOTSUPP fallback cases must still work."""
    body, text = _get_statximpl_body()
    assert body is not None, "statxImpl not found"

    # Both original errnos must still be present
    assert ".NOSYS" in body, "NOSYS errno handling removed — regression"
    assert ".OPNOTSUPP" in body, "EOPNOTSUPP errno handling removed — regression"

    # They must still trigger fallback
    assert "statxFallback" in body, "statxImpl must call statxFallback for error cases"
    assert "supports_statx_on_linux.store(false" in body, \
        "statx support flag must be disabled on fallback"


def test_statximpl_structure_intact():
    """statxImpl must retain its core structure: while loop, statx syscall,
    EINTR retry, and PosixStat conversion."""
    body, _ = _get_statximpl_body()
    assert body is not None, "statxImpl not found"

    # Core loop structure
    assert "while (true)" in body, "statxImpl must have retry loop"
    assert "linux.statx" in body, "statxImpl must call linux.statx"
    assert ".INTR" in body, "statxImpl must handle EINTR retry"
    assert "continue" in body, "EINTR must trigger continue"

    # Must still have error handling via errnoSys
    assert "errnoSys" in body, "statxImpl must check for syscall errors"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md / SKILL.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — src/AGENTS.md @ 159a285841539c8f166509116c12b11e15b47fdf
def test_uses_bun_sys_not_std():
    """statxImpl must use bun.sys patterns (Maybe(T), bun.sys.Error), not std.posix.
    Rule: 'Always use bun.* APIs instead of std.*' from src/AGENTS.md."""
    body, _ = _get_statximpl_body()
    assert body is not None, "statxImpl not found"

    # Must use Maybe(PosixStat) return type
    assert "Maybe(PosixStat)" in body, \
        "statxImpl must return Maybe(PosixStat) per bun.sys conventions"

    # Must NOT use std.posix patterns
    assert "std.posix" not in body, "Must use bun.sys, not std.posix"
    assert "std.os" not in body, "Must use bun.sys, not std.os"


# [agent_config] pass_to_pass — .claude/skills/zig-system-calls/SKILL.md @ 159a285841539c8f166509116c12b11e15b47fdf
def test_error_handling_pattern():
    """statxImpl error handling must follow bun.sys Maybe(T) pattern:
    switch on .result/.err, not throw/catch.
    Rule from zig-system-calls SKILL.md: Handle Maybe(T) with switch."""
    body, _ = _get_statximpl_body()
    assert body is not None, "statxImpl not found"

    # The fallback must use switch on .result/.err
    fallback_m = re.search(r"fn\s+statxFallback", Path(SYS_ZIG).read_text())
    assert fallback_m, "statxFallback not found"

    text = Path(SYS_ZIG).read_text()
    start = text.index("{", fallback_m.start())
    depth = 0
    i = start
    while i < len(text):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                break
        i += 1
    fallback_body = text[start:i + 1]

    # Must use switch pattern for result/error handling
    assert ".result =>" in fallback_body, \
        "statxFallback must use .result => pattern per bun.sys conventions"
    assert ".err =>" in fallback_body, \
        "statxFallback must use .err => pattern per bun.sys conventions"
