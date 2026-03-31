#!/usr/bin/env bash
# Test: opencode-markdown-streaming-jank
# Verifies that markdown rendering jank during streaming is fixed.
set +e

REWARD=0
LOGS=/logs/verifier
mkdir -p "$LOGS"

cd /workspace/opencode

TIMELINE="packages/app/src/pages/session/message-timeline.tsx"
MARKDOWN="packages/ui/src/components/markdown.tsx"
MSGPART="packages/ui/src/components/message-part.tsx"

###############################################################
# [pr_diff] (0.25): CSS containment must be conditional on active/streaming state
# F2P: base has unconditional content-visibility: auto → FAIL
#       any fix makes it conditional or removes it → PASS
###############################################################
python3 << 'PYEOF'
import re, sys

with open("packages/app/src/pages/session/message-timeline.tsx") as f:
    src = f.read()

lines = src.splitlines()

# Find lines referencing content-visibility (camelCase or kebab-case)
cv_indices = [i for i, l in enumerate(lines)
              if "content-visibility" in l.lower() or "contentvisibility" in l.lower()]

if not cv_indices:
    # Removed entirely — valid fix (no containment = no jank)
    print("PASS: content-visibility removed entirely")
    sys.exit(0)

# Check that every occurrence is inside a conditional (ternary, if, &&, or references active/streaming)
conditional = re.compile(r'(\?\s*["\x27]auto["\x27]|active|streaming|undefined|&&|\bif\b)', re.I)

for idx in cv_indices:
    window = "\n".join(lines[max(0, idx - 3):idx + 4])
    if conditional.search(window):
        print("PASS: content-visibility is conditional on active/streaming state")
        sys.exit(0)

print("FAIL: content-visibility appears unconditional")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && REWARD=$((REWARD + 25))

###############################################################
# [pr_diff] (0.10): contain-intrinsic-size must also be conditional or removed
# F2P: base has it unconditional → FAIL
###############################################################
python3 << 'PYEOF'
import re, sys

with open("packages/app/src/pages/session/message-timeline.tsx") as f:
    src = f.read()

lines = src.splitlines()
cis_indices = [i for i, l in enumerate(lines)
               if "contain-intrinsic-size" in l.lower() or "containintrinsicsize" in l.lower()]

if not cis_indices:
    print("PASS: contain-intrinsic-size removed entirely")
    sys.exit(0)

conditional = re.compile(r'(\?\s*["\x27]auto|active|streaming|undefined|&&|\bif\b)', re.I)
for idx in cis_indices:
    window = "\n".join(lines[max(0, idx - 3):idx + 4])
    if conditional.search(window):
        print("PASS: contain-intrinsic-size is conditional")
        sys.exit(0)

print("FAIL: contain-intrinsic-size appears unconditional")
sys.exit(1)
PYEOF
[ $? -eq 0 ] && REWARD=$((REWARD + 10))

###############################################################
# [pr_diff] (0.25): Markdown component must have streaming awareness
# F2P: base markdown.tsx has no streaming param or fence handling → FAIL
#       any correct fix adds streaming awareness + incomplete fence logic → PASS
###############################################################
python3 << 'PYEOF'
import re, sys

with open("packages/ui/src/components/markdown.tsx") as f:
    src = f.read()

# Part A: Component accepts streaming-related information.
# Could be a prop named streaming/isStreaming/live, or accessed via context/store.
streaming_aware = bool(re.search(
    r'(streaming|isStreaming|live)\s*[\?:=]', src
))
# Also accept: reading streaming from a context or store
if not streaming_aware:
    streaming_aware = bool(re.search(
        r'(useContext|createMemo|createEffect).*streaming', src, re.I | re.S
    ))

# Part B: Logic that handles incomplete/unclosed code fences.
# ANY implementation must reference triple-backtick patterns in executable code
# (not just comments). Look for ``` in string literals or regex.
code_lines = [l for l in src.splitlines() if l.strip() and not l.strip().startswith("//")]
code_src = "\n".join(code_lines)

# Check for backtick fence handling in code (not comments)
fence_handling = bool(re.search(r'["\x27`/].*`{3}|```', code_src))
# Also accept named references to fence/incomplete concepts in code
if not fence_handling:
    fence_handling = bool(re.search(
        r'(incomplete|unclosed|openFence|codeFence|fenceOpen)', code_src
    ))

if streaming_aware and fence_handling:
    print("PASS: Markdown has streaming awareness and fence handling")
    sys.exit(0)
elif streaming_aware:
    # Streaming aware but no explicit fence handling — partial credit
    # Some fixes might handle this differently (e.g., debounce all re-renders)
    print("PARTIAL: streaming param but no fence handling detected")
    sys.exit(1)
else:
    print("FAIL: No streaming awareness in markdown.tsx")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && REWARD=$((REWARD + 25))

###############################################################
# [pr_diff] (0.15): message-part must compute and pass streaming state
# F2P: base message-part.tsx has no streaming logic → FAIL
###############################################################
python3 << 'PYEOF'
import re, sys

with open("packages/ui/src/components/message-part.tsx") as f:
    src = f.read()

# A correct fix must determine if a message is still streaming and convey that
# to the Markdown renderer. Check for:
# 1. Computing streaming state (checking completed time, role, active flag, etc.)
# 2. Passing it to <Markdown> or providing via context

# Streaming state computation — any of these patterns
computes_streaming = bool(re.search(
    r'(streaming|isStreaming|isActive|active)\s*[=:]', src
))
# Also accept checking message completion status
if not computes_streaming:
    computes_streaming = bool(re.search(
        r'(completed|\.time\.|finished|done)\b', src
    ))

# Passes to Markdown — as prop, context, or store
passes_streaming = bool(re.search(
    r'<Markdown[^>]*(streaming|active|live)', src, re.I
))
# Or via context/provider
if not passes_streaming:
    passes_streaming = bool(re.search(
        r'(Provider|Context|Store).*streaming', src, re.I | re.S
    ))

if computes_streaming and passes_streaming:
    print("PASS: streaming state computed and passed to Markdown")
    sys.exit(0)
elif computes_streaming:
    print("PARTIAL: streaming computed but not clearly passed to Markdown")
    sys.exit(1)
else:
    print("FAIL: No streaming state logic in message-part.tsx")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && REWARD=$((REWARD + 15))

###############################################################
# [repo_tests] (0.10): P2P — All target files must exist and be non-empty
###############################################################
P2P_OK=true
for f in "$MARKDOWN" "$MSGPART" "$TIMELINE"; do
    if [ ! -s "$f" ]; then
        echo "FAIL: $f missing or empty"
        P2P_OK=false
    fi
done
if $P2P_OK; then
    echo "PASS: All target files exist and non-empty"
    REWARD=$((REWARD + 10))
fi

###############################################################
# [pr_diff] (0.15): Anti-stub — markdown.tsx must have substantial new logic
# Rejects trivial stubs that just add a streaming prop with no real implementation
###############################################################
python3 << 'PYEOF'
import re, sys

with open("packages/ui/src/components/markdown.tsx") as f:
    src = f.read()

# Count non-empty, non-comment lines
lines = [l for l in src.splitlines()
         if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")]

# Base file has ~165 code lines. A real fix adds 40+ lines of streaming logic.
# Require at least 190 meaningful lines.
if len(lines) < 190:
    print(f"FAIL: Only {len(lines)} code lines — likely stub (need >=190)")
    sys.exit(1)

# Must have at least 3 of these implementation signals (in code, not comments):
code = "\n".join(lines)
signals = 0

# 1. Block/segment splitting or array construction
if re.search(r'(blocks|segments|parts|chunks)\s*[.(\[=]', code):
    signals += 1

# 2. Caching or memoization of parsed results
if re.search(r'(cache|memo|previous|latest|prior)\b', code, re.I):
    signals += 1

# 3. Code fence pattern matching (regex or string matching with backticks)
if re.search(r'(match|test|exec|search|indexOf|includes).*(`{3}|```)', code):
    signals += 1
# Also accept: a function/variable named for fence detection
if re.search(r'(incomplete|unclosed|openFence|fence)', code):
    signals += 1

# 4. Conditional rendering based on streaming/mode
if re.search(r'(streaming|mode\s*===?\s*["\x27]live|mode\s*===?\s*["\x27]full)', code):
    signals += 1

# 5. HTML joining or concatenation of separately parsed blocks
if re.search(r'(join|concat|\.html|innerHTML).*(?:block|part|segment)', code, re.I):
    signals += 1

if signals >= 3:
    print(f"PASS: Non-trivial implementation ({signals} signals, {len(lines)} lines)")
    sys.exit(0)
else:
    print(f"FAIL: Likely stub ({signals} signals, {len(lines)} lines)")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && REWARD=$((REWARD + 15))

###############################################################
# Final score
###############################################################
FINAL=$(echo "scale=2; $REWARD / 100" | bc)
# Ensure leading zero
case "$FINAL" in
    .*) FINAL="0$FINAL" ;;
esac

echo "$FINAL" > "$LOGS/reward.txt"

echo "Total reward: $FINAL (raw: $REWARD/100)"
