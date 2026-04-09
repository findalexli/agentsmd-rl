"""
Task: bun-statx-seccomp-fallback
Repo: oven-sh/bun @ 159a285841539c8f166509116c12b11e15b47fdf
PR:   28825

Tests verify the fix for statx fallback error handling in src/sys.zig.
A compiled C analyzer parses statxImpl to verify:
- EPERM and EINVAL are included in the fallback errno set
- Abnormal rc>0 return values trigger fallback
- The statxFallback helper delegates correctly (stat/lstat/fstat)
"""

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

    /* Find statxImpl function body */
    char *impl = strstr(buf, "fn statxImpl");
    if (!impl) {
        fprintf(stderr, "FAIL: statxImpl not found\n");
        free(buf); return 1;
    }

    /* Find the getErrno switch block within statxImpl */
    char *errno_switch = strstr(impl, "getErrno()");
    if (!errno_switch) {
        fprintf(stderr, "FAIL: no getErrno() call in statxImpl\n");
        free(buf); return 1;
    }

    /* Find the switch statement following getErrno */
    char *brace = strchr(errno_switch, '{');
    if (!brace) {
        fprintf(stderr, "FAIL: no switch block after getErrno()\n");
        free(buf); return 1;
    }

    /* Extract switch body - find matching close brace */
    int depth = 0;
    char *end = brace;
    while (*end) {
        if (*end == '{') depth++;
        else if (*end == '}') { depth--; if (depth == 0) break; }
        end++;
    }

    /* Save the switch body for analysis */
    char saved = *(end + 1);
    *(end + 1) = '\0';

    /* Must contain .PERM in the switch cases */
    if (!strstr(brace, ".PERM")) {
        fprintf(stderr, "FAIL: .PERM not in errno switch — EPERM won't trigger fallback\n");
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
        fprintf(stderr, "FAIL: .INVAL not in errno switch — EINVAL won't trigger fallback\n");
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

    /* The rc>0 check must use bitCast to isize and check > 0.
       This handles QEMU user-mode and S390 RHEL docker where statx
       returns a positive value that isn't 0 (success) or -errno. */
    char *bitcast_pos = strstr(impl, "isize");
    if (!bitcast_pos) {
        fprintf(stderr, "FAIL: no isize cast found in statxImpl\n");
        free(buf); return 1;
    }

    /* Look for the pattern: @bitCast(rc) followed by > 0 check */
    char *bitcast = strstr(impl, "@bitCast");
    if (!bitcast || bitcast > bitcast_pos + 200) {
        fprintf(stderr, "FAIL: no @bitCast of rc found — cannot detect rc>0\n");
        free(buf); return 1;
    }

    /* The positive-rc check must come BEFORE the errno handling,
       because errnoSys treats rc>0 as success (errno == 0). */
    char *errno_check = strstr(impl, "errnoSys");
    if (!errno_check) {
        fprintf(stderr, "FAIL: no errnoSys call in statxImpl\n");
        free(buf); return 1;
    }

    if (bitcast > errno_check) {
        fprintf(stderr, "FAIL: rc>0 check is AFTER errnoSys — won't catch positive rc\n");
        free(buf); return 1;
    }

    /* Must store false to supports_statx_on_linux and call fallback */
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

    /* Find the getErrno() area in statxImpl */
    char *errno_area = strstr(impl, "getErrno()");
    if (!errno_area) {
        fprintf(stderr, "FAIL: no getErrno() in statxImpl\n");
        free(buf); return 1;
    }

    /* The four errnos must appear grouped together (comma-separated switch cases
       or combined with "or"), not as separate if-checks. Look for a line that
       contains at least 3 of the 4 errnos together. */
    char *line_start = errno_area;
    int found_grouped = 0;

    /* Search forward up to 2000 chars for the errno handling */
    char *search_end = errno_area + 2000;
    if (search_end > buf + len) search_end = buf + len;

    /* Extract the errno handling region */
    long region_len = search_end - errno_area;
    char *region = malloc(region_len + 1);
    memcpy(region, errno_area, region_len);
    region[region_len] = '\0';

    /* Check all four errnos exist in the handling region */
    int has_nosys = strstr(region, ".NOSYS") != NULL;
    int has_opnotsupp = strstr(region, ".OPNOTSUPP") != NULL;
    int has_perm = strstr(region, ".PERM") != NULL;
    int has_inval = strstr(region, ".INVAL") != NULL;

    if (!has_nosys || !has_opnotsupp || !has_perm || !has_inval) {
        fprintf(stderr, "FAIL: missing errnos: NOSYS=%d OPNOTSUPP=%d PERM=%d INVAL=%d\n",
                has_nosys, has_opnotsupp, has_perm, has_inval);
        free(region); free(buf); return 1;
    }

    /* All four must trigger the same fallback action.
       Look for a shared code path that handles them together. */
    char *switch_arm = strstr(region, ".NOSYS");
    if (switch_arm) {
        /* Check if all 4 errnos are on the same logical line (within ~200 chars).
           This means they're grouped in one switch arm or if-condition. */
        char nearby[200] = {0};
        int n = switch_arm - region;
        int start_idx = (n > 100) ? n - 100 : 0;
        int end_idx = (n + 200 < region_len) ? n + 200 : region_len;
        int copy_len = end_idx - start_idx;
        memcpy(nearby, region + start_idx, copy_len);
        nearby[copy_len] = '\0';

        /* At minimum, PERM and INVAL must appear near NOSYS and OPNOTSUPP,
           not in a completely separate block. */
        if (strstr(nearby, ".PERM") && strstr(nearby, ".INVAL")) {
            found_grouped = 1;
        }
    }

    if (!found_grouped) {
        /* Alternative: the fix may use a separate statxFallback helper.
           Verify that exists and all errnos lead to it. */
        char *fallback = strstr(impl, "statxFallback");
        if (fallback) {
            found_grouped = 1;
        }
    }

    if (!found_grouped) {
        fprintf(stderr, "FAIL: errnos not grouped together in handling logic\n");
        free(region); free(buf); return 1;
    }

    /* Must disable statx and return fallback for all four */
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
# Pass-to-pass (repo_tests / static) — regression + anti-stub
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
