#!/usr/bin/env bash
set +e

TOTAL=0
SCORE=0

log() { echo "$1"; }

# Python helper: strip C/C++ comments from source to prevent comment-injection gaming
STRIP_COMMENTS='
import re, sys
src = sys.stdin.read()
# Remove single-line comments
src = re.sub(r"//[^\n]*", "", src)
# Remove multi-line comments
src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
print(src)
'

strip_comments() {
    python3 -c "$STRIP_COMMENTS" < "$1"
}

cd /workspace/bun

ALGO_CPP="src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp"
ALGO_H="src/bun.js/bindings/webcore/JSAbortAlgorithm.h"
SIGNAL_CPP="src/bun.js/bindings/webcore/AbortSignal.cpp"
SIGNAL_H="src/bun.js/bindings/webcore/AbortSignal.h"
CUSTOM_CPP="src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp"

##############################################################################
# GATE: Core files must exist and be non-trivial
##############################################################################
# [pr_diff] (gate): All modified source files must exist
for f in "$ALGO_CPP" "$ALGO_H" "$SIGNAL_CPP" "$SIGNAL_H" "$CUSTOM_CPP"; do
    if [ ! -s "$f" ]; then
        log "GATE FAILED: $f missing or empty"
        echo "0.0" > /logs/verifier/reward.txt
        echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
        exit 0
    fi
done

##############################################################################
# CHECK 1 (0.25): Break the strong ref cycle — callback storage must not
# create a GC root. Any weak reference mechanism counts, not just
# JSCallbackDataWeak. Verified by: strong ref type is REMOVED from
# JSAbortAlgorithm code AND some non-strong ref type is used instead.
# WHY structural: C++ requires full Bun build system (Zig, JSC, CMake).
##############################################################################
# [pr_diff] (0.25): JSAbortAlgorithm must not use strong callback storage
TOTAL=$((TOTAL + 25))
RESULT=$(python3 << 'PYEOF'
import re

def strip(src):
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

cpp = strip(open("src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp").read())
header = strip(open("src/bun.js/bindings/webcore/JSAbortAlgorithm.h").read())

# The original bug: JSCallbackDataStrong creates a GC root.
# Fix: must NOT have JSCallbackDataStrong in the callback data member usage.
# We check both .cpp and .h stripped of comments.

# Strong ref must be gone from BOTH files (not just renamed in a string)
strong_in_cpp = bool(re.search(r'\bJSCallbackDataStrong\b', cpp))
strong_in_h = bool(re.search(r'\bJSCallbackDataStrong\b', header))

# Some weak/non-strong callback mechanism must be present.
# Accept any of: JSCallbackDataWeak, weak ref wrapper, weak pointer pattern
# This is intentionally broad to avoid narrowness.
weak_patterns = [
    r'\bJSCallbackDataWeak\b',
    r'\bWeakPtr\b',
    r'\bWeak<',
    r'\bweakCallback\b',
    r'\bJSWeakValue\b',
]
has_weak_cpp = any(re.search(p, cpp) for p in weak_patterns)
has_weak_h = any(re.search(p, header) for p in weak_patterns)

if not strong_in_cpp and not strong_in_h and (has_weak_cpp or has_weak_h):
    print("PASS")
else:
    reasons = []
    if strong_in_cpp: reasons.append("strong still in cpp")
    if strong_in_h: reasons.append("strong still in header")
    if not has_weak_cpp and not has_weak_h: reasons.append("no weak mechanism found")
    print("FAIL:" + ",".join(reasons))
PYEOF
)
if [ "$RESULT" = "PASS" ]; then
    SCORE=$((SCORE + 25))
    log "PASS [0.25]: Strong ref removed from JSAbortAlgorithm, weak mechanism present"
else
    log "FAIL [0.25]: $RESULT"
fi

##############################################################################
# CHECK 2 (0.15): GC must be able to trace weak callback to keep it alive.
# The JSAbortAlgorithm (or equivalent) must have a visitor/tracer method
# that delegates to the callback data's visitor. Accept any naming convention.
# WHY structural: GC visiting is a C++ compile-time concern.
##############################################################################
# [pr_diff] (0.15): JSAbortAlgorithm must have GC visitor for weak callback
TOTAL=$((TOTAL + 15))
RESULT=$(python3 << 'PYEOF'
import re

def strip(src):
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

cpp = strip(open("src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp").read())
header = strip(open("src/bun.js/bindings/webcore/JSAbortAlgorithm.h").read())

# Must have a method in cpp that:
# 1. Is a member of JSAbortAlgorithm (or related class)
# 2. Takes a visitor/slot parameter
# 3. Delegates to m_data's visitor method
# Accept: visitJSFunction, visit, trace, visitChildren, etc.

# Find methods in cpp that belong to JSAbortAlgorithm and involve visiting
visitor_method = re.search(
    r'JSAbortAlgorithm::\w*(?:visit|trace|mark)\w*\s*\([^)]*(?:Visitor|Slot)[^)]*\)\s*\{([^}]+)\}',
    cpp, re.IGNORECASE
)

# Also check header declares such a method
visitor_decl = re.search(
    r'(?:void|template)\s+.*(?:visit|trace|mark)\w*\s*\([^)]*(?:Visitor|Slot)',
    header, re.IGNORECASE
)

if visitor_method and visitor_decl:
    body = visitor_method.group(1)
    # Body must delegate to the data member's visitor (not be empty)
    delegates = bool(re.search(r'm_data\s*->\s*\w*(?:visit|trace|mark)', body, re.IGNORECASE))
    if delegates:
        print("PASS")
    else:
        print("FAIL:visitor method does not delegate to m_data")
else:
    reasons = []
    if not visitor_method: reasons.append("no visitor method in cpp")
    if not visitor_decl: reasons.append("no visitor declaration in header")
    print("FAIL:" + ",".join(reasons))
PYEOF
)
if [ "$RESULT" = "PASS" ]; then
    SCORE=$((SCORE + 15))
    log "PASS [0.15]: JSAbortAlgorithm has GC visitor that delegates to callback data"
else
    log "FAIL [0.15]: $RESULT"
fi

##############################################################################
# CHECK 3 (0.10): handleEvent must guard against collected weak callback.
# With weak refs, the callback can be GC'd. handleEvent must not blindly
# dereference. Accept: null check, optional check, validity check, etc.
# WHY structural: Runtime behavior of GC-collected refs is C++ domain.
##############################################################################
# [pr_diff] (0.10): handleEvent guards against collected callback
TOTAL=$((TOTAL + 10))
RESULT=$(python3 << 'PYEOF'
import re

def strip(src):
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

cpp = strip(open("src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp").read())

# Find handleEvent method body — match JSAbortAlgorithm::handleEvent
# Use a brace-counting approach for robustness
start = cpp.find("JSAbortAlgorithm::handleEvent")
if start == -1:
    print("FAIL:handleEvent method not found")
else:
    # Find opening brace
    brace_start = cpp.find("{", start)
    if brace_start == -1:
        print("FAIL:handleEvent has no body")
    else:
        depth = 0
        end = brace_start
        for i in range(brace_start, len(cpp)):
            if cpp[i] == "{": depth += 1
            elif cpp[i] == "}": depth -= 1
            if depth == 0:
                end = i
                break
        body = cpp[brace_start:end+1]

        # Must have some form of null/validity guard before using callback
        # Accept: !callback, callback == nullptr, !xxx.callback(),
        #         callback.has_value(), if (!...), guard patterns
        guards = [
            r'!\s*\w*callback',
            r'callback\w*\s*==\s*nullptr',
            r'nullptr\s*==\s*\w*callback',
            r'!\s*m_data',
            r'callback\w*\.has_value',
            r'if\s*\(\s*!',  # generic early-return guard
        ]
        has_guard = any(re.search(g, body, re.IGNORECASE) for g in guards)

        # Body must also be non-trivial (>3 lines of actual code)
        code_lines = [l.strip() for l in body.split("\n") if l.strip() and l.strip() != "{" and l.strip() != "}"]
        non_trivial = len(code_lines) >= 3

        if has_guard and non_trivial:
            print("PASS")
        elif not has_guard:
            print("FAIL:no null/validity guard in handleEvent")
        else:
            print("FAIL:handleEvent body is trivial (stub)")
PYEOF
)
if [ "$RESULT" = "PASS" ]; then
    SCORE=$((SCORE + 10))
    log "PASS [0.10]: handleEvent guards against collected callback"
else
    log "FAIL [0.10]: $RESULT"
fi

##############################################################################
# CHECK 4 (0.15): AbortSignal must store abort algorithms in a GC-visible
# container (separate from the type-erased m_algorithms lambdas).
# Accept any container type (Vector, HashMap, Deque, etc.) holding typed
# AbortAlgorithm refs. Must also have a GC visitor declared.
# WHY structural: C++ template/container choice, can't execute.
##############################################################################
# [pr_diff] (0.15): AbortSignal has typed abort algorithm storage with visitor
TOTAL=$((TOTAL + 15))
RESULT=$(python3 << 'PYEOF'
import re

def strip(src):
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

header = strip(open("src/bun.js/bindings/webcore/AbortSignal.h").read())
cpp = strip(open("src/bun.js/bindings/webcore/AbortSignal.cpp").read())

# Header must have a member that stores AbortAlgorithm in a typed container
# Accept: Vector, HashMap, Deque, std::vector, etc.
container_patterns = [
    r'(?:Vector|HashMap|Deque|std::vector|std::unordered_map|std::map|std::deque)\s*<[^>]*AbortAlgorithm',
    r'(?:Vector|HashMap|Deque|std::vector)\s*<[^>]*Ref\s*<\s*AbortAlgorithm',
]
has_typed_container = any(re.search(p, header) for p in container_patterns)

# Must also have a visitor/tracer method for these algorithms
# Accept any name: visitAbortAlgorithms, traceAlgorithms, visitCallbacks, etc.
visitor_patterns = [
    r'(?:visit|trace|mark)\w*(?:Abort|Algorithm|Callback)\w*\s*\(',
    r'template\s*<\s*typename\s+\w+\s*>\s*void\s+\w*(?:visit|trace)\w*',
]
has_visitor_decl = any(re.search(p, header, re.IGNORECASE) for p in visitor_patterns)

# CPP must have the visitor implementation
has_visitor_impl = any(re.search(p, cpp, re.IGNORECASE) for p in [
    r'AbortSignal::\w*(?:visit|trace)\w*(?:Abort|Algorithm|Callback)',
])

if has_typed_container and has_visitor_decl and has_visitor_impl:
    print("PASS")
else:
    reasons = []
    if not has_typed_container: reasons.append("no typed AbortAlgorithm container in header")
    if not has_visitor_decl: reasons.append("no visitor declaration in header")
    if not has_visitor_impl: reasons.append("no visitor implementation in cpp")
    print("FAIL:" + ",".join(reasons))
PYEOF
)
if [ "$RESULT" = "PASS" ]; then
    SCORE=$((SCORE + 15))
    log "PASS [0.15]: AbortSignal has typed abort algorithm storage with GC visitor"
else
    log "FAIL [0.15]: $RESULT"
fi

##############################################################################
# CHECK 5 (0.10): Thread safety — GC thread visits the algorithm container
# concurrently with main-thread mutations. Must have synchronization.
# Accept: Lock, Mutex, std::mutex, Atomic, lock_guard, Locker, etc.
# WHY structural: Concurrency correctness, C++ domain.
##############################################################################
# [pr_diff] (0.10): Abort algorithm storage is synchronized
TOTAL=$((TOTAL + 10))
RESULT=$(python3 << 'PYEOF'
import re

def strip(src):
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

header = strip(open("src/bun.js/bindings/webcore/AbortSignal.h").read())
cpp = strip(open("src/bun.js/bindings/webcore/AbortSignal.cpp").read())

# Header must declare a lock/mutex member
lock_member_patterns = [
    r'\b(?:Lock|Mutex|std::mutex|std::shared_mutex|RecursiveLock|SpinLock)\b\s+m_\w*',
    r'm_\w*(?:Lock|Mutex|lock|mutex)\b',
    r'WTF_GUARDED_BY_LOCK',
]
has_lock_member = any(re.search(p, header) for p in lock_member_patterns)

# CPP must use the lock in at least 2 places (add/remove + visit/run)
lock_usage_patterns = [
    r'\bLocker\b', r'\block_guard\b', r'\bunique_lock\b',
    r'\bscoped_lock\b', r'\.lock\(\)', r'\.acquire\(\)',
    r'\bLockHolder\b', r'\bAutoLocker\b',
]
lock_uses = 0
for p in lock_usage_patterns:
    lock_uses += len(re.findall(p, cpp))

if has_lock_member and lock_uses >= 2:
    print("PASS")
elif not has_lock_member:
    print("FAIL:no lock/mutex member in header")
else:
    print(f"FAIL:only {lock_uses} lock usage(s) in cpp, need >=2")
PYEOF
)
if [ "$RESULT" = "PASS" ]; then
    SCORE=$((SCORE + 10))
    log "PASS [0.10]: Abort algorithm storage is thread-safe"
else
    log "FAIL [0.10]: $RESULT"
fi

##############################################################################
# CHECK 6 (0.10): The GC visitor on JSAbortSignal must walk the abort
# algorithms so their weak callbacks stay alive. The visitor method
# (visitAdditionalChildren or similar) must call through to AbortSignal's
# algorithm visitor.
# WHY structural: GC integration, C++ domain.
##############################################################################
# [pr_diff] (0.10): JSAbortSignal GC visitor walks abort algorithms
TOTAL=$((TOTAL + 10))
RESULT=$(python3 << 'PYEOF'
import re

def strip(src):
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

custom = strip(open("src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp").read())

# Find the GC visitor method — accept various naming conventions
visitor_method = re.search(
    r'(?:visitAdditionalChildren|visitChildren|visitOutputConstraints|trace)\w*\s*\([^)]*(?:Visitor|Slot)[^)]*\)\s*\{',
    custom
)

if not visitor_method:
    print("FAIL:no GC visitor method found in JSAbortSignalCustom.cpp")
else:
    # Find matching closing brace
    start = visitor_method.end() - 1
    depth = 0
    end = start
    for i in range(start, len(custom)):
        if custom[i] == "{": depth += 1
        elif custom[i] == "}": depth -= 1
        if depth == 0:
            end = i
            break
    body = custom[start:end+1]

    # Must call through to the AbortSignal's algorithm visitor
    # Accept: visitAbortAlgorithms, traceAlgorithms, visitCallbacks, etc.
    calls_algo_visitor = bool(re.search(
        r'(?:visit|trace|mark)\w*(?:Abort|Algorithm|Callback)', body, re.IGNORECASE
    ))

    # Alternative: directly iterates over algorithms and visits them
    direct_iteration = bool(re.search(
        r'for\s*\(.*(?:abort|algorithm)', body, re.IGNORECASE
    ))

    if calls_algo_visitor or direct_iteration:
        print("PASS")
    else:
        print("FAIL:GC visitor does not walk abort algorithms")
PYEOF
)
if [ "$RESULT" = "PASS" ]; then
    SCORE=$((SCORE + 10))
    log "PASS [0.10]: JSAbortSignal GC visitor walks abort algorithms"
else
    log "FAIL [0.10]: $RESULT"
fi

##############################################################################
# CHECK 7 (0.10): addAbortAlgorithmToSignal must store AbortAlgorithm in the
# new typed container, NOT erase it into a type-erased lambda via the old
# addAlgorithm() path. The body must push/append/emplace into a member,
# not call addAlgorithm with a lambda wrapper.
# WHY structural: The type erasure is the root cause of the leak.
##############################################################################
# [pr_diff] (0.10): addAbortAlgorithmToSignal uses typed storage path
TOTAL=$((TOTAL + 10))
RESULT=$(python3 << 'PYEOF'
import re

def strip(src):
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

cpp = strip(open("src/bun.js/bindings/webcore/AbortSignal.cpp").read())

# Find addAbortAlgorithmToSignal function body
start = cpp.find("addAbortAlgorithmToSignal")
if start == -1:
    print("FAIL:addAbortAlgorithmToSignal not found")
else:
    brace = cpp.find("{", start)
    if brace == -1:
        print("FAIL:no body found")
    else:
        depth = 0
        end = brace
        for i in range(brace, len(cpp)):
            if cpp[i] == "{": depth += 1
            elif cpp[i] == "}": depth -= 1
            if depth == 0:
                end = i
                break
        body = cpp[brace:end+1]

        # Must NOT call the old addAlgorithm (which type-erases into a lambda)
        # But "addAbortAlgorithm" is OK (it's the new path)
        calls_old = bool(re.search(r'\baddAlgorithm\s*\(', body))
        # Filter out false positive from addAbortAlgorithm
        if calls_old:
            # Check it's not just addAbortAlgorithm
            old_calls = re.findall(r'\b(?<!Abort)addAlgorithm\s*\(', body)
            calls_old = len(old_calls) > 0

        # Must store into a member (append, push_back, emplace_back, emplace, insert, add)
        stores = bool(re.search(
            r'(?:append|push_back|emplace_back|emplace|insert|add)\s*\(', body
        ))

        # Body must be non-trivial
        code_lines = [l.strip() for l in body.split("\n")
                      if l.strip() and l.strip() not in ("{", "}")]
        non_trivial = len(code_lines) >= 3

        if not calls_old and stores and non_trivial:
            print("PASS")
        else:
            reasons = []
            if calls_old: reasons.append("still calls old addAlgorithm (type erasure)")
            if not stores: reasons.append("no container insertion found")
            if not non_trivial: reasons.append("body is trivial")
            print("FAIL:" + ",".join(reasons))
PYEOF
)
if [ "$RESULT" = "PASS" ]; then
    SCORE=$((SCORE + 10))
    log "PASS [0.10]: addAbortAlgorithmToSignal uses typed storage"
else
    log "FAIL [0.10]: $RESULT"
fi

##############################################################################
# CHECK 8 (0.05): Anti-stub — cross-file consistency. The weak ref type used
# in JSAbortAlgorithm must be referenced in the visitor, and the container
# in AbortSignal must be referenced in both add and visit paths.
# WHY structural: Ensures coherent fix, not isolated string injections.
##############################################################################
# [pr_diff] (0.05): Cross-file consistency of the fix
TOTAL=$((TOTAL + 5))
RESULT=$(python3 << 'PYEOF'
import re

def strip(src):
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return src

algo_cpp = strip(open("src/bun.js/bindings/webcore/JSAbortAlgorithm.cpp").read())
algo_h = strip(open("src/bun.js/bindings/webcore/JSAbortAlgorithm.h").read())
sig_cpp = strip(open("src/bun.js/bindings/webcore/AbortSignal.cpp").read())
sig_h = strip(open("src/bun.js/bindings/webcore/AbortSignal.h").read())
custom = strip(open("src/bun.js/bindings/webcore/JSAbortSignalCustom.cpp").read())

checks = []

# 1. JSAbortAlgorithm.cpp must define at least 2 methods (handleEvent + visitor)
method_defs = re.findall(r'JSAbortAlgorithm::\w+\s*\(', algo_cpp)
checks.append(("algo_cpp has >=2 method defs", len(method_defs) >= 2))

# 2. AbortSignal.h has >5 non-blank lines changed vs the original concept
#    (must have both container + lock + visitor decl — at least 3 new declarations)
new_decls = 0
if re.search(r'(?:Vector|HashMap|Deque|std::vector)<.*AbortAlgorithm', sig_h): new_decls += 1
if re.search(r'(?:Lock|Mutex|mutex)', sig_h): new_decls += 1
if re.search(r'(?:visit|trace)\w*\(', sig_h): new_decls += 1
checks.append(("sig_h has >=3 new concepts", new_decls >= 3))

# 3. AbortSignal.cpp must have the visitor impl + runAbortSteps or equivalent
has_visitor_impl = bool(re.search(r'AbortSignal::\w*(?:visit|trace)\w*', sig_cpp))
has_run_or_drain = bool(re.search(r'(?:runAbort|drainAbort|fireAbort|handleAbort)', sig_cpp))
checks.append(("sig_cpp has visitor + run/drain", has_visitor_impl and has_run_or_drain))

# 4. JSAbortSignalCustom.cpp references the algorithm visitor
has_algo_ref = bool(re.search(r'(?:abort|algorithm)', custom, re.IGNORECASE))
checks.append(("custom references algorithms", has_algo_ref))

passed = all(ok for _, ok in checks)
if passed:
    print("PASS")
else:
    failed = [name for name, ok in checks if not ok]
    print("FAIL:" + "; ".join(failed))
PYEOF
)
if [ "$RESULT" = "PASS" ]; then
    SCORE=$((SCORE + 5))
    log "PASS [0.05]: Cross-file consistency verified"
else
    log "FAIL [0.05]: $RESULT"
fi

##############################################################################
# Final score
##############################################################################

REWARD=$(python3 -c "print(round($SCORE / $TOTAL, 4) if $TOTAL > 0 else 0.0)")
echo ""
echo "Total: $SCORE / $TOTAL = $REWARD"
echo "$REWARD" > /logs/verifier/reward.txt

# Decompose into categories (all structural for this C++ task)
BEHAVIORAL=$(python3 -c "
# Checks 1-3 are the core fix (weak ref, visitor, null guard) = 0.50
score = $SCORE; total = $TOTAL
ratio = score/total if total > 0 else 0
# Core fix checks: 25+15+10 = 50 out of 100
core = min(ratio * 0.50, 0.50)
print(round(core, 4))
")
REGRESSION=$(python3 -c "
score = $SCORE; total = $TOTAL
ratio = score/total if total > 0 else 0
# Thread safety + storage path: 10+10 = 20 out of 100
reg = min(ratio * 0.20, 0.20)
print(round(reg, 4))
")
CONFIG=$(python3 -c "
score = $SCORE; total = $TOTAL
ratio = score/total if total > 0 else 0
# GC visitor integration: 10+10 = 20 out of 100
cfg = min(ratio * 0.20, 0.20)
print(round(cfg, 4))
")

echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": $REGRESSION, \"config\": $CONFIG, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
