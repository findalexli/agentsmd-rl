"""
Task: bun-dns-stale-cache-refcount
Repo: oven-sh/bun @ 7960fe985dfa3418b507777a5a61289defbdb9dc
PR:   #28271

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Zig cannot be compiled in this container (needs cmake + zig + JSC).
All checks are structural source analysis on dns.zig, honestly labeled.
"""

import re
from pathlib import Path

REPO = "/workspace/bun"
DNS_FILE = Path(f"{REPO}/src/bun.js/api/bun/dns.zig")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_zig_comments(src: str) -> str:
    """Remove // line comments from Zig source (preserves strings)."""
    lines = src.split("\n")
    out = []
    for line in lines:
        in_str = False
        i = 0
        clean = []
        while i < len(line):
            c = line[i]
            if c == '"' and (i == 0 or line[i - 1] != "\\"):
                in_str = not in_str
                clean.append(c)
            elif not in_str and c == "/" and i + 1 < len(line) and line[i + 1] == "/":
                break
            else:
                clean.append(c)
            i += 1
        out.append("".join(clean))
    return "\n".join(out)


def _extract_fn(src: str, fn_pattern: str, max_lines: int = 50,
                body_must_contain: str | None = None) -> str:
    """Extract a Zig function body by matching its signature pattern.

    Handles multi-line signatures where the opening '{' is on a later line
    (e.g., Zig functions with multiple parameters).
    """
    lines = src.split("\n")
    candidates = [i for i, line in enumerate(lines) if re.search(fn_pattern, line)]
    for start in candidates:
        body_lines = [lines[start]]
        brace_depth = lines[start].count("{") - lines[start].count("}")
        seen_open_brace = brace_depth > 0
        for j in range(start + 1, min(start + max_lines, len(lines))):
            line = lines[j]
            body_lines.append(line)
            brace_depth += line.count("{") - line.count("}")
            if not seen_open_brace and "{" in line:
                seen_open_brace = True
            if seen_open_brace and re.match(r"\s{0,12}(pub\s+)?fn\s+\w+", line) and j > start:
                body_lines.pop()
                break
            if seen_open_brace and brace_depth <= 0:
                break
        body = "\n".join(body_lines)
        if body_must_contain is None or body_must_contain in body:
            return body
    return ""


def _load_source():
    """Load dns.zig, strip comments, extract the three target functions."""
    raw = DNS_FILE.read_text()
    src = _strip_zig_comments(raw)
    isexpired = _extract_fn(src, r"pub\s+fn\s+isExpired")
    get_fn = _extract_fn(src, r"(pub\s+)?fn\s+get\s*\(", max_lines=60,
                         body_must_contain="isExpired")
    freeaddrinfo = _extract_fn(src, r"(pub\s+)?fn\s+freeaddrinfo", max_lines=40)
    return src, isexpired, get_fn, freeaddrinfo


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dns_file_exists():
    """dns.zig must exist and be non-empty."""
    assert DNS_FILE.exists(), f"{DNS_FILE} does not exist"
    assert DNS_FILE.stat().st_size > 0, f"{DNS_FILE} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral fixes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_isexpired_no_refcount_gate():
    """isExpired must not gate expiry on refcount > 0.

    The bug: `if (this.refcount > 0 or this.result == null)` blocks expiry
    for referenced entries. Fix: remove the refcount > 0 condition so TTL
    is checked regardless of active connections.
    """
    _, isexpired, _, _ = _load_source()
    assert isexpired.strip(), "isExpired function not found or empty"
    assert not re.search(r"refcount\s*>\s*0", isexpired), (
        "isExpired still gates on refcount > 0"
    )


# [pr_diff] fail_to_pass
def test_get_refcount_guard():
    """get() must guard deinit of expired entries on zero refcount.

    The bug: get() unconditionally deinits expired entries even when
    refcount > 0 (use-after-free). Fix: only deinit when refcount == 0.
    """
    _, _, get_fn, _ = _load_source()
    assert re.search(r"isExpired", get_fn), "get() no longer calls isExpired"
    zero_patterns = [
        r"refcount\s*==\s*0",
        r"refcount\s*<\s*1",
        r"refcount\s*<=\s*0",
        r"0\s*==\s*\w*refcount",
        r"refcount\s*==\s*@as\s*\(\s*\w+\s*,\s*0\s*\)",
    ]
    found = any(re.search(pat, get_fn) for pat in zero_patterns)
    assert found, "get() does not guard deinit on zero refcount"


# [pr_diff] fail_to_pass
def test_freeaddrinfo_conditional_valid():
    """freeaddrinfo must not unconditionally assign valid = (err == 0).

    The bug: `req.valid = err == 0` overwrites previously valid entries on
    success callback. Fix: only set valid = false on error.
    """
    _, _, _, freeaddrinfo = _load_source()
    assert freeaddrinfo.strip(), "freeaddrinfo function not found or empty"

    has_unconditional = bool(
        re.search(r"\.valid\s*=\s*err\s*==\s*0", freeaddrinfo)
    ) or bool(
        re.search(r"\.valid\s*=\s*\(\s*err\s*==\s*0\s*\)", freeaddrinfo)
    )
    assert not has_unconditional, (
        "freeaddrinfo still has unconditional valid = (err == 0)"
    )
    # Must still handle the error case
    handles_error = (
        bool(re.search(r"valid\s*=\s*false", freeaddrinfo))
        or bool(re.search(r"err\s*!=\s*0", freeaddrinfo))
        or bool(re.search(r"err\s*>\s*0", freeaddrinfo))
    )
    assert handles_error, "freeaddrinfo doesn't handle the error case at all"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_isexpired_result_null():
    """isExpired still checks result == null (pre-existing guard)."""
    _, isexpired, _, _ = _load_source()
    assert re.search(r"result\s*==\s*null", isexpired), (
        "isExpired no longer checks result == null"
    )


# [pr_diff] pass_to_pass
def test_get_calls_isexpired():
    """get() still calls isExpired for cache entries."""
    _, _, get_fn, _ = _load_source()
    assert re.search(r"isExpired", get_fn), "get() no longer calls isExpired"


# [pr_diff] pass_to_pass
def test_get_calls_deinit():
    """get() still calls deinit for expired unreferenced entries."""
    _, _, get_fn, _ = _load_source()
    assert re.search(r"deinit\s*\(", get_fn), "get() no longer calls deinit"


# [pr_diff] pass_to_pass
def test_isexpired_ttl_comparison():
    """isExpired still performs TTL comparison (not stubbed out)."""
    _, isexpired, _, _ = _load_source()
    assert re.search(r"getMaxDNSTimeToLiveSeconds|max_dns_ttl|dns_ttl", isexpired), (
        "isExpired no longer references TTL"
    )


# ---------------------------------------------------------------------------
# Structural — anti-stub (pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_isexpired_not_stub():
    """isExpired has a meaningful body (>= 4 non-blank code lines)."""
    _, isexpired, _, _ = _load_source()
    code_lines = [
        l for l in isexpired.split("\n")
        if l.strip() and l.strip() not in ("{", "}", "};")
    ]
    assert len(code_lines) >= 4, (
        f"isExpired has only {len(code_lines)} code lines — likely a stub"
    )


# [pr_diff] pass_to_pass
def test_freeaddrinfo_refcount_dec():
    """freeaddrinfo still decrements refcount."""
    _, _, _, freeaddrinfo = _load_source()
    assert re.search(
        r"refcount\s*-=\s*1|refcount\s*=\s*\w*refcount\s*-\s*1", freeaddrinfo
    ), "freeaddrinfo no longer decrements refcount"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — src/CLAUDE.md:14-16 @ 7960fe9
def test_no_std_apis():
    """Modified functions must not introduce std.* usage (use bun.* instead)."""
    _, isexpired, get_fn, freeaddrinfo = _load_source()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"std\.(mem|fs|posix|process)", body)
        assert not matches, f"{name} uses std.* APIs: {matches}"


# [agent_config] pass_to_pass — src/CLAUDE.md:11 @ 7960fe9
def test_no_inline_imports():
    """Modified functions must not use @import() inline."""
    _, isexpired, get_fn, freeaddrinfo = _load_source()
    for name, body in [("isExpired", isexpired), ("get", get_fn),
                       ("freeaddrinfo", freeaddrinfo)]:
        matches = re.findall(r"@import\s*\(", body)
        assert not matches, f"{name} has inline @import()"
