#!/usr/bin/env bash
set +e

SCORE=0
DNS_FILE="/workspace/bun/src/bun.js/api/bun/dns.zig"

echo "=== DNS Cache Stale Refcount Fix Tests ==="

# --- GATE: File exists and is non-empty ---
# [pr_diff] (GATE): dns.zig must exist and be non-empty
if [ ! -s "$DNS_FILE" ]; then
    echo "GATE FAIL: $DNS_FILE missing or empty"
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASS: dns.zig exists"

# =============================================================================
# All checks use Python to parse Zig source with comment stripping.
# Zig cannot be compiled in this container (needs cmake + zig + JSC build system),
# so all checks are STRUCTURAL source analysis, honestly labeled.
# =============================================================================

RESULT=$(python3 << 'PYEOF'
import re, sys, json

def strip_zig_comments(src):
    """Remove // line comments from Zig source (preserves string content)."""
    lines = src.split('\n')
    out = []
    for line in lines:
        # Simple approach: remove everything after // that's not inside a string
        # Good enough for pattern matching — not a full parser
        in_str = False
        i = 0
        clean = []
        while i < len(line):
            c = line[i]
            if c == '"' and (i == 0 or line[i-1] != '\\'):
                in_str = not in_str
                clean.append(c)
            elif not in_str and c == '/' and i + 1 < len(line) and line[i+1] == '/':
                break  # rest is comment
            else:
                clean.append(c)
            i += 1
        out.append(''.join(clean))
    return '\n'.join(out)

def extract_fn(src, fn_pattern, max_lines=50, body_must_contain=None):
    """Extract a Zig function body from 'pub fn name' or 'fn name' to next fn/closing.
    If body_must_contain is set, skip matches whose body doesn't contain that string."""
    lines = src.split('\n')
    candidates = [i for i, line in enumerate(lines) if re.search(fn_pattern, line)]
    for start in candidates:
        body_lines = [lines[start]]
        brace_depth = lines[start].count('{') - lines[start].count('}')
        for j in range(start + 1, min(start + max_lines, len(lines))):
            line = lines[j]
            body_lines.append(line)
            brace_depth += line.count('{') - line.count('}')
            if re.match(r'\s{0,12}(pub\s+)?fn\s+\w+', line) and j > start:
                body_lines.pop()
                break
            if brace_depth <= 0:
                break
        body = '\n'.join(body_lines)
        if body_must_contain is None or body_must_contain in body:
            return body
    return ""

with open("/workspace/bun/src/bun.js/api/bun/dns.zig") as f:
    raw_src = f.read()

# Strip comments for all pattern matching
src = strip_zig_comments(raw_src)

isexpired_body = extract_fn(src, r'pub\s+fn\s+isExpired')
# get() might be "fn get(" or "pub fn get(" — target the GlobalCache.get (contains isExpired)
get_body = extract_fn(src, r'(pub\s+)?fn\s+get\s*\(', max_lines=60, body_must_contain='isExpired')
freeaddrinfo_body = extract_fn(src, r'(pub\s+)?fn\s+freeaddrinfo', max_lines=40)

checks = {}
score = 0

# ============================================
# Structural: fail-to-pass pattern checks (0.55 total)
# These verify the buggy patterns are fixed in source.
# All operate on comment-stripped code.
# ============================================

# [pr_diff] (0.20): isExpired must not gate expiry on refcount > 0
# The bug: `if (this.refcount > 0 or this.result == null)` blocks expiry for referenced entries.
# Fix: remove the refcount > 0 condition so TTL is checked regardless.
# Accept: any version of isExpired that does NOT have refcount > 0 in the early-return guard.
c1_pass = True
if re.search(r'refcount\s*>\s*0', isexpired_body):
    c1_pass = False
if not isexpired_body.strip():
    c1_pass = False  # function was deleted/emptied
checks['isexpired_no_refcount_gate'] = c1_pass
if c1_pass:
    score += 20

# [pr_diff] (0.20): get() must guard deinit of expired entries on zero refcount
# The bug: get() unconditionally deinits expired entries even if refcount > 0 (use-after-free).
# Fix: wrap deinit in a refcount check.
# Accept: refcount == 0, refcount < 1, refcount <= 0, refcount == @as(usize, 0)
c2_pass = False
if re.search(r'isExpired', get_body):
    # Look for a refcount zero-check near deinit context
    # Accept various ways to express "refcount is zero"
    zero_patterns = [
        r'refcount\s*==\s*0',
        r'refcount\s*<\s*1',
        r'refcount\s*<=\s*0',
        r'0\s*==\s*\w*refcount',
        r'refcount\s*==\s*@as\s*\(\s*\w+\s*,\s*0\s*\)',
    ]
    for pat in zero_patterns:
        if re.search(pat, get_body):
            c2_pass = True
            break
checks['get_refcount_guard'] = c2_pass
if c2_pass:
    score += 20

# [pr_diff] (0.15): freeaddrinfo must not unconditionally set valid = (err == 0)
# The bug: `req.valid = err == 0` overwrites previously valid entries on success callback.
# Fix: only set valid = false on error, don't touch on success.
# Accept: any approach that doesn't have the unconditional assignment.
c3_pass = False
# Check the unconditional assignment is gone
has_unconditional = bool(re.search(r'\.valid\s*=\s*err\s*==\s*0', freeaddrinfo_body))
has_unconditional = has_unconditional or bool(re.search(r'\.valid\s*=\s*\(\s*err\s*==\s*0\s*\)', freeaddrinfo_body))
if not has_unconditional and freeaddrinfo_body.strip():
    # Verify the function still handles the error case somehow
    # Accept: sets valid=false on error, or checks err != 0
    handles_error = (
        bool(re.search(r'valid\s*=\s*false', freeaddrinfo_body)) or
        bool(re.search(r'err\s*!=\s*0', freeaddrinfo_body)) or
        bool(re.search(r'err\s*>\s*0', freeaddrinfo_body))
    )
    if handles_error:
        c3_pass = True
checks['freeaddrinfo_conditional_valid'] = c3_pass
if c3_pass:
    score += 15

# ============================================
# Structural: regression / pass-to-pass (0.20 total)
# Verify core logic wasn't deleted or stubbed out.
# ============================================

# [pr_diff] (0.05): isExpired still checks result == null (pre-existing guard)
c4_pass = bool(re.search(r'result\s*==\s*null', isexpired_body))
checks['isexpired_result_null'] = c4_pass
if c4_pass:
    score += 5

# [pr_diff] (0.05): get() still calls isExpired for cache entries
c5_pass = bool(re.search(r'isExpired', get_body))
checks['get_calls_isexpired'] = c5_pass
if c5_pass:
    score += 5

# [pr_diff] (0.05): get() still calls deinit for expired unreferenced entries
c6_pass = bool(re.search(r'deinit\s*\(', get_body))
checks['get_calls_deinit'] = c6_pass
if c6_pass:
    score += 5

# [pr_diff] (0.05): isExpired performs TTL comparison (not stubbed)
c7_pass = bool(re.search(r'getMaxDNSTimeToLiveSeconds|max_dns_ttl|dns_ttl', isexpired_body))
checks['isexpired_ttl'] = c7_pass
if c7_pass:
    score += 5

# ============================================
# Structural: anti-stub depth checks (0.10 total)
# Verify functions have real bodies, not stubs.
# ============================================

# [pr_diff] (0.05): isExpired has meaningful body (>= 4 non-blank lines of code)
isexpired_code_lines = [l for l in isexpired_body.split('\n') if l.strip() and l.strip() not in ('{', '}', '};')]
c8_pass = len(isexpired_code_lines) >= 4
checks['isexpired_not_stub'] = c8_pass
if c8_pass:
    score += 5

# [pr_diff] (0.05): freeaddrinfo still decrements refcount
c9_pass = bool(re.search(r'refcount\s*-=\s*1|refcount\s*=\s*\w*refcount\s*-\s*1', freeaddrinfo_body))
checks['freeaddrinfo_refcount_dec'] = c9_pass
if c9_pass:
    score += 5

# ============================================
# Config-derived checks (0.10 total)
# ============================================

# [agent_config] (0.05): "Always use bun.* APIs instead of std.*" — src/CLAUDE.md:12-13 @ 7960fe9
# Only check the modified functions, not the whole file
new_std = 0
for body in [isexpired_body, get_body, freeaddrinfo_body]:
    new_std += len(re.findall(r'std\.(mem|fs|posix|process)', body))
c10_pass = (new_std == 0)
checks['no_std_apis'] = c10_pass
if c10_pass:
    score += 5

# [agent_config] (0.05): "Never use @import() inline inside of functions" — src/CLAUDE.md:7 @ 7960fe9
inline_imports = 0
for body in [isexpired_body, get_body, freeaddrinfo_body]:
    inline_imports += len(re.findall(r'@import\s*\(', body))
c11_pass = (inline_imports == 0)
checks['no_inline_imports'] = c11_pass
if c11_pass:
    score += 5

# ============================================
# Output
# ============================================
reward = score / 100.0

# Component breakdown
fix_pts = min(score, 55) / 100.0
regr_pts = max(0, min(score - 55, 20)) / 100.0
anti_stub_pts = max(0, min(score - 75, 10)) / 100.0
config_pts = max(0, min(score - 85, 10)) / 100.0

result = {
    "reward": round(reward, 4),
    "behavioral": round(fix_pts, 4),
    "regression": round(regr_pts, 4),
    "structural": round(anti_stub_pts, 4),
    "config": round(config_pts, 4),
    "checks": {k: "PASS" if v else "FAIL" for k, v in checks.items()}
}

for name, passed in checks.items():
    status = "PASS" if passed else "FAIL"
    print(f"  {status}: {name}")

print(f"\nReward: {reward:.4f} ({score}/100)")
print(f"JSON:{json.dumps(result)}")
PYEOF
)

echo "$RESULT"

# Extract reward and JSON from Python output
REWARD=$(echo "$RESULT" | grep "^Reward:" | sed 's/Reward: //' | awk '{print $1}')
JSON_LINE=$(echo "$RESULT" | grep "^JSON:" | sed 's/^JSON://')

# Fallback
if [ -z "$REWARD" ]; then
    REWARD="0.0"
fi
if [ -z "$JSON_LINE" ]; then
    JSON_LINE="{\"reward\": 0.0}"
fi

mkdir -p /logs/verifier
echo "$REWARD" > /logs/verifier/reward.txt
echo "$JSON_LINE" > /logs/verifier/reward.json

echo ""
cat /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
