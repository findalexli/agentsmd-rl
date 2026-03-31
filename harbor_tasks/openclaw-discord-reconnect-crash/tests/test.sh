#!/usr/bin/env bash
set +e

TARGET="/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[gate]=0.00
WEIGHTS[behavioral]=0.55
WEIGHTS[regression]=0.20
WEIGHTS[antistub]=0.10
WEIGHTS[config_boundary]=0.10
WEIGHTS[style_rubric]=0.05

for key in gate behavioral regression antistub config_boundary style_rubric; do
    RESULTS[$key]=0
done

if [ ! -f "$TARGET" ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi

# ---------- GATE (0%): Code must compile ----------
python3 << 'PYEOF'
import subprocess, sys, os

target = "/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts"

# Create a minimal tsconfig for standalone compilation
os.chdir("/workspace/openclaw")

# Check TypeScript compilation - this is the gate
result = subprocess.run(
    ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2020",
     "--module", "ESNext", "--moduleResolution", "node", target],
    capture_output=True, text=True, timeout=60
)

if result.returncode != 0:
    print(f"GATE FAIL: TypeScript compilation failed")
    print(result.stderr[:500])
    sys.exit(1)

print("GATE PASS: TypeScript compiles")
PYEOF
GATE_PASS=$?
[ $GATE_PASS -eq 0 ] && RESULTS[gate]=1 && echo "TEST gate: PASS" || echo "TEST gate: FAIL"

# Gate failure = zero score
if [ $GATE_PASS -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- PRIMARY (55%): Behavioral - reconnect-exhausted not gated by lifecycleStopping ----------
python3 << 'PYEOF'
import ast, sys, re, textwrap

TARGET = "/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts"

def extract_file_functions(filepath):
    """Extract function definitions from TypeScript-like source using AST extraction patterns."""
    with open(filepath) as f:
        src = f.read()

    # For TS, we'll use regex to extract the handleGatewayEvent function
    # and analyze its control flow
    return src

def analyze_reconnect_handling(src):
    """
    Analyze the handleGatewayEvent function to ensure reconnect-exhausted
    is handled without requiring lifecycleStopping to be true.

    The bug was: if (lifecycleStopping && event.type === "reconnect-exhausted")
    The fix should just check: if (event.type === "reconnect-exhausted") or similar
    """
    # Find the handleGatewayEvent function
    func_match = re.search(
        r'const handleGatewayEvent = \(([^)]+)\)[^=]*=>\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}\s*;',
        src, re.DOTALL
    )

    if not func_match:
        # Try alternative patterns
        func_match = re.search(
            r'(?:function|const)\s+handleGatewayEvent\s*[=(]\s*\(?\s*event\s*:?[^)]*\)?[^=]*=>?\s*\{',
            src
        )

    if not func_match:
        print("BEHAVIORAL FAIL: handleGatewayEvent not found")
        sys.exit(1)

    # Extract the function body using brace matching
    start_idx = src.find('=> {', func_match.start())
    if start_idx < 0:
        start_idx = func_match.end() - 1

    brace_count = 0
    in_string = False
    string_char = None
    i = start_idx

    while i < len(src):
        c = src[i]
        if not in_string:
            if c in '"\'`':
                in_string = True
                string_char = c
            elif c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    break
        else:
            if c == string_char and src[i-1] != '\\':
                in_string = False
        i += 1

    func_body = src[start_idx:i+1]

    # Check for the BUGGY pattern: lifecycleStopping && ... reconnect-exhausted
    buggy_pattern = re.search(
        r'lifecycleStopping\s*&&[^&]*event\.type\s*===?\s*["\']reconnect-exhausted["\']',
        func_body
    )

    if buggy_pattern:
        print("BEHAVIORAL FAIL: reconnect-exhausted still gated by lifecycleStopping")
        sys.exit(1)

    # Verify the fix exists: standalone reconnect-exhausted check (not tied to lifecycleStopping)
    # The fix should have event.type === "reconnect-exhausted" without lifecycleStopping &&
    fix_pattern = re.search(
        r'event\.type\s*===?\s*["\']reconnect-exhausted["\']',
        func_body
    )

    if not fix_pattern:
        print("BEHAVIORAL FAIL: reconnect-exhausted check not found")
        sys.exit(1)

    # Verify it's handled (returns "stop")
    # Look for return "stop" after the reconnect-exhausted check
    exhausted_idx = fix_pattern.start()
    after_exhausted = func_body[exhausted_idx:exhausted_idx + 500]

    if 'return "stop"' not in after_exhausted and "return 'stop'" not in after_exhausted:
        print("BEHAVIORAL FAIL: reconnect-exhausted does not return 'stop'")
        sys.exit(1)

    # Check drainPendingGatewayErrors function too - it should also handle reconnect-exhausted
    # without requiring lifecycleStopping
    drain_match = re.search(
        r'const drainPendingGatewayErrors.*?=.*?\(\)[^=]*=>',
        src, re.DOTALL
    )

    if drain_match:
        # Find drainPendingGatewayErrors body
        drain_start = src.find('=> {', drain_match.start())
        if drain_start > 0:
            brace_count = 0
            i = drain_start
            while i < len(src):
                if src[i] == '{':
                    brace_count += 1
                elif src[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        break
                i += 1

            drain_body = src[drain_start:i+1]

            # The drain function should handle reconnect-exhausted without lifecycleStopping
            # OR with abortSignal as alternative (which the PR fix included)
            drain_fix = re.search(
                r'event\.type\s*===?\s*["\']reconnect-exhausted["\']',
                drain_body
            )

            if drain_fix:
                # Check if it's still gated ONLY by lifecycleStopping (buggy)
                # Fixed version allows: lifecycleStopping || abortSignal?.aborted
                buggy_drain = re.search(
                    r'event\.type\s*===?\s*["\']reconnect-exhausted["\'][^}]*&&[^}]*lifecycleStopping',
                    drain_body
                )
                if buggy_drain and 'abortSignal' not in drain_body:
                    print("BEHAVIORAL FAIL: drainPendingGatewayErrors still gates reconnect-exhausted")
                    sys.exit(1)

    print("BEHAVIORAL PASS: reconnect-exhausted handled without lifecycleStopping gate")
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- REGRESSION (20%): disallowed-intents and basic functionality preserved ----------
python3 << 'PYEOF'
import re, sys

TARGET = "/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts"

with open(TARGET) as f:
    src = f.read()

# Check disallowed-intents handling preserved
if "disallowed-intents" not in src:
    print("REGRESSION FAIL: disallowed-intents handling removed")
    sys.exit(1)

# Check that disallowed-intents still returns "stop"
disallowed_pattern = re.search(
    r'event\.type\s*===?\s*["\']disallowed-intents["\']',
    src
)

if disallowed_pattern:
    after = src[disallowed_pattern.start():disallowed_pattern.start() + 400]
    if 'return "stop"' not in after and "return 'stop'" not in after:
        print("REGRESSION FAIL: disallowed-intents doesn't return stop")
        sys.exit(1)

# Check main function exists and has proper structure
if "runDiscordGatewayLifecycle" not in src:
    print("REGRESSION FAIL: main function removed")
    sys.exit(1)

# Check for export keyword
if "export" not in src:
    print("REGRESSION FAIL: module not exported")
    sys.exit(1)

# Check lifecycleStopping flag is still defined (just not gating reconnect-exhausted)
if "lifecycleStopping" not in src:
    print("REGRESSION FAIL: lifecycleStopping flag removed (needed for other logic)")
    sys.exit(1)

print("REGRESSION PASS: Core functionality preserved")
PYEOF
[ $? -eq 0 ] && RESULTS[regression]=1 && echo "TEST regression: PASS" || echo "TEST regression: FAIL"

# ---------- ANTI-STUB (10%): Code has meaningful implementation ----------
python3 << 'PYEOF'
import re, sys

TARGET = "/workspace/openclaw/extensions/discord/src/monitor/provider.lifecycle.ts"

with open(TARGET) as f:
    src = f.read()
    lines = src.split('\n')

# Count non-trivial lines (not comments, not blank)
non_trivial = 0
for line in lines:
    stripped = line.strip()
    if stripped and not stripped.startswith('//') and not stripped.startswith('*') and not stripped.startswith('/*'):
        non_trivial += 1

# Must have substantial implementation
if non_trivial < 40:
    print(f"ANTI-STUB FAIL: Only {non_trivial} non-trivial lines")
    sys.exit(1)

# Check for actual function bodies with logic
try_catch_count = src.count('try') + src.count('catch')
if_count = len(re.findall(r'\bif\s*\(', src))
return_count = len(re.findall(r'return\s+', src))
async_count = len(re.findall(r'\basync\b', src))
await_count = len(re.findall(r'\bawait\b', src))

if if_count < 3:
    print("ANTI-STUB FAIL: Too few conditionals")
    sys.exit(1)

if return_count < 3:
    print("ANTI-STUB FAIL: Too few return statements")
    sys.exit(1)

if async_count < 1 or await_count < 3:
    print("ANTI-STUB FAIL: Missing async/await structure")
    sys.exit(1)

# Check function has complexity - multiple distinct operations
required_patterns = ['registerGateway', 'attachDiscordGatewayLogging', 'drainPendingGatewayErrors', 'handleGatewayEvent']
found = sum(1 for p in required_patterns if p in src)
if found < 3:
    print(f"ANTI-STUB FAIL: Only {found}/4 required function components found")
    sys.exit(1)

print("ANTI-STUB PASS: Code has meaningful implementation")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# ---------- Config-derived test (10%): "Extension code must import from plugin-sdk/*" ----------
# Source: extensions/CLAUDE.md line 16 @ 496a1a35bd7ac7a1719d39a3723a731e2d131e8b
python3 << 'PYEOF'
import os, re, sys

EXTENSIONS_DIR = "/workspace/openclaw/extensions"
VIOLATIONS = []

for root, dirs, files in os.walk(os.path.join(EXTENSIONS_DIR, "discord/src")):
    # Skip test files and type definitions
    files = [f for f in files if not f.endswith('.test.ts') and not f.endswith('.d.ts')]

    for file in files:
        if not file.endswith('.ts'):
            continue

        filepath = os.path.join(root, file)
        with open(filepath) as f:
            content = f.read()
            lines = content.split('\n')

        for i, line in enumerate(lines):
            # Check for imports from core internals
            if re.search(r'^import .* from [\'"]\.\./\.\./\.\./src/', line):
                VIOLATIONS.append(f"{filepath}:{i+1}: {line.strip()}")

if VIOLATIONS:
    print("CONFIG_BOUNDARY FAIL: Cross-boundary imports found:")
    for v in VIOLATIONS[:5]:
        print(f"  {v}")
    sys.exit(1)

print("CONFIG_BOUNDARY PASS: No cross-boundary imports")
PYEOF
[ $? -eq 0 ] && RESULTS[config_boundary]=1 && echo "TEST config_boundary: PASS" || echo "TEST config_boundary: FAIL"

# ---------- STYLE RUBRIC (5%): Placeholder for LLM judge ----------
RESULTS[style_rubric]=0
if [ -f "/tests/judge_hook.sh" ]; then
    source /tests/judge_hook.sh 2>/dev/null || true
    # If judge awards points, set style_rubric=1
fi

# Calculate total score
SCORE=$(python3 -c "
w = {'behavioral': ${WEIGHTS[behavioral]}, 'regression': ${WEIGHTS[regression]},
     'antistub': ${WEIGHTS[antistub]}, 'config_boundary': ${WEIGHTS[config_boundary]},
     'style_rubric': ${WEIGHTS[style_rubric]}}
r = {'behavioral': ${RESULTS[behavioral]}, 'regression': ${RESULTS[regression]},
     'antistub': ${RESULTS[antistub]}, 'config_boundary': ${RESULTS[config_boundary]},
     'style_rubric': ${RESULTS[style_rubric]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")

echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# Self-audit output
echo ""
echo "=== Self-Audit Summary ==="
echo "Behavioral: ${RESULTS[behavioral]} | Regression: ${RESULTS[regression]} | AntiStub: ${RESULTS[antistub]} | Config: ${RESULTS[config_boundary]}"
echo "Score: $SCORE"
