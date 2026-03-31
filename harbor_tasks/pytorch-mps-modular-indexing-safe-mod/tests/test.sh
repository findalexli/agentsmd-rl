#!/usr/bin/env bash
set +e

REPO="/workspace/pytorch"
cd "$REPO"

REWARD=0

# ── Shared helper for extracting + calling printer methods ───────────
cat > /tmp/mps_helper.py << 'HELPEREOF'
import ast, sys, textwrap, sympy

def extract_method(filepath, method_name):
    """Extract a method from mps.py via AST and return it as a callable."""
    source = open(filepath).read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            lines = source.splitlines(keepends=True)
            func_src = textwrap.dedent(''.join(lines[node.lineno - 1 : node.end_lineno]))
            ns = {'__builtins__': __builtins__, 'sympy': sympy}
            for attr in dir(sympy):
                if not attr.startswith('_'):
                    ns[attr] = getattr(sympy, attr)
            exec(func_src, ns)
            return ns[method_name]
    return None

class FakePrinter:
    """Minimal printer mock — just converts sympy objects to str."""
    def doprint(self, x):
        return str(x)
    def _print(self, x):
        return str(x)
    def parenthesize(self, x, *a, **kw):
        return str(x)

class FakeExpr:
    """Mock for a ModularIndexing expression with (base, div, mod)."""
    def __init__(self, x, div, mod, is_integer=True):
        self.args = (x, div, mod)
        self.is_integer = is_integer

class FakeFloorDivExpr:
    """Mock for a FloorDiv expression with (base, div)."""
    def __init__(self, x, div, is_integer=True):
        self.args = (x, div)
        self.is_integer = is_integer
HELPEREOF

# ── GATE: Python syntax check ──────────────────────────────────────
# [pr_diff] (gate): mps.py must parse
python3 -c "import ast; ast.parse(open('torch/_inductor/codegen/mps.py').read())"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: mps.py syntax error"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi

# [pr_diff] (gate): utils.h must have balanced braces
python3 -c "
c = open('c10/metal/utils.h').read()
assert c.count('{') == c.count('}'), 'unbalanced braces'
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: utils.h brace imbalance"
    echo "0.0" > /logs/verifier/reward.txt
    exit 0
fi
echo "Gates passed."

# ── FAIL-TO-PASS (0.50): buggy pattern output differs from bare modulo ──
# [pr_diff] (0.50): Calling _print_ModularIndexing with div=65536 + non-power-of-2 mod
#   must NOT return bare "(x/div) % (mod)" — the Metal compiler bug workaround must activate
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from mps_helper import extract_method, FakePrinter, FakeExpr
import sympy

method = extract_method('torch/_inductor/codegen/mps.py', '_print_ModularIndexing')
if method is None:
    print('FAIL: _print_ModularIndexing not found')
    sys.exit(1)

printer = FakePrinter()

# Multiple buggy patterns: div=65536 (power-of-2), mod=non-power-of-2
buggy_cases = [
    (65536, 6, "SDPA with 6 heads"),
    (65536, 3, "non-p2 mod=3"),
    (65536, 5, "non-p2 mod=5"),
]

for div_val, mod_val, desc in buggy_cases:
    expr = FakeExpr(sympy.Symbol('idx'), sympy.Integer(div_val), sympy.Integer(mod_val))
    try:
        result = method(printer, expr)
    except Exception as e:
        print(f'FAIL: raised {type(e).__name__} for {desc}: {e}')
        sys.exit(1)

    if result is None or len(str(result).strip()) < 3:
        print(f'FAIL: trivial output for {desc}: {result}')
        sys.exit(1)

    result_str = str(result)

    # On the base commit, this returns "((idx) / (65536)) % (6)" etc.
    # A correct fix MUST return something different — any workaround is fine.
    clean = result_str.replace(' ', '')
    bare_pattern = f'((idx)/({div_val}))%({mod_val})'
    if clean == bare_pattern:
        print(f'FAIL: still bare modulo for {desc}: {result_str}')
        sys.exit(1)

    # Anti-stub: output must contain the mod value (not a trivial "pass" return)
    if str(mod_val) not in result_str:
        print(f'FAIL: output missing mod value {mod_val} for {desc}: {result_str}')
        sys.exit(1)

    # Anti-stub: output must reference the base variable
    if 'idx' not in result_str:
        print(f'FAIL: output missing base variable for {desc}: {result_str}')
        sys.exit(1)

print('PASS: all buggy patterns produce non-bare workaround output')
PYEOF
if [ $? -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.50)")
    echo "PASS [0.50]: buggy patterns produce workaround output"
else
    echo "FAIL [0.50]: buggy patterns still produce bare modulo"
fi

# ── FAIL-TO-PASS (0.20): workaround uses function call, not bare operator ──
# [pr_diff] (0.20): The buggy-pattern output must call a function (any name)
#   rather than using the bare % operator that triggers the Metal compiler bug
python3 << 'PYEOF'
import sys, re
sys.path.insert(0, '/tmp')
from mps_helper import extract_method, FakePrinter, FakeExpr
import sympy

method = extract_method('torch/_inductor/codegen/mps.py', '_print_ModularIndexing')
if method is None:
    sys.exit(1)

printer = FakePrinter()
expr = FakeExpr(sympy.Symbol('idx'), sympy.Integer(65536), sympy.Integer(6))
try:
    result = str(method(printer, expr))
except Exception as e:
    print(f'FAIL: raised {e}')
    sys.exit(1)

# The output should use a function call — any function name is fine
# (safe_mod, workaround_mod, metal_safe_modulo, etc.)
# A function call looks like: identifier(...args...)
has_func_call = bool(re.search(r'[a-zA-Z_][\w:]*\s*\([^)]*\)', result))

# Reject if it's ONLY using bare % with no function call
clean = result.replace(' ', '')
uses_bare_pct = bool(re.search(r'\)%\(', clean))

if uses_bare_pct and not has_func_call:
    print(f'FAIL: bare % operator without function call: {result}')
    sys.exit(1)

if not has_func_call:
    print(f'FAIL: no function call in output: {result}')
    sys.exit(1)

print(f'PASS: buggy pattern calls function: {result}')
PYEOF
if [ $? -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.20)")
    echo "PASS [0.20]: buggy output uses function call"
else
    echo "FAIL [0.20]: buggy output uses bare operator"
fi

# ── PASS-TO-PASS (0.10): non-buggy patterns still produce valid output ──
# [pr_diff] (0.10): div=1 or power-of-2 mod must still work — method must not crash
#   and must produce output containing the input values
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/tmp')
from mps_helper import extract_method, FakePrinter, FakeExpr, FakeFloorDivExpr
import sympy

method = extract_method('torch/_inductor/codegen/mps.py', '_print_ModularIndexing')
if method is None:
    sys.exit(1)

printer = FakePrinter()

# Non-buggy cases: div=1, or mod is power-of-2
cases = [
    (1, 8, "div=1, mod=8"),
    (65536, 8, "div=65536, mod=8 (power-of-2 mod)"),
    (256, 16, "div=256, mod=16"),
    (1, 32, "div=1, mod=32"),
]
for div_val, mod_val, desc in cases:
    expr = FakeExpr(sympy.Symbol('idx'), sympy.Integer(div_val), sympy.Integer(mod_val))
    try:
        result = str(method(printer, expr))
    except Exception as e:
        print(f'FAIL: {desc} raised {e}')
        sys.exit(1)
    if not result or len(result.strip()) < 3:
        print(f'FAIL: {desc} trivial output: {result}')
        sys.exit(1)
    if str(mod_val) not in result:
        print(f'FAIL: {desc} output missing mod value: {result}')
        sys.exit(1)

# Also verify _print_FloorDiv still works
fd_method = extract_method('torch/_inductor/codegen/mps.py', '_print_FloorDiv')
if fd_method is None:
    print('FAIL: _print_FloorDiv missing')
    sys.exit(1)
fd_expr = FakeFloorDivExpr(sympy.Symbol('idx'), sympy.Integer(4))
try:
    fd_result = str(fd_method(printer, fd_expr))
except Exception as e:
    print(f'FAIL: _print_FloorDiv raised {e}')
    sys.exit(1)
if 'idx' not in fd_result or ('floor_divide' not in fd_result and '/' not in fd_result):
    print(f'FAIL: _print_FloorDiv invalid output: {fd_result}')
    sys.exit(1)

print(f'PASS: non-buggy patterns and FloorDiv work correctly')
PYEOF
if [ $? -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.10)")
    echo "PASS [0.10]: non-buggy patterns + FloorDiv work"
else
    echo "FAIL [0.10]: non-buggy patterns or FloorDiv broken"
fi

# ── FAIL-TO-PASS structural (0.10): utils.h has new modulo-safety function ──
# [pr_diff] (0.10): A new function in c10/metal/utils.h that provides a safe modulo
# WHY structural: C++ Metal code cannot be compiled or executed in CPU-only Python Docker
python3 << 'PYEOF'
import sys, re

content = open('c10/metal/utils.h').read()

# Pre-existing functions at base commit — must NOT count as new
preexisting = {'floor_divide', 'fmod'}

# Find C++ function definitions
func_re = re.compile(
    r'(?:template\s*<[^>]*>\s*)?'
    r'(?:(?:inline|constexpr|static)\s+)*'
    r'[\w:]+\s+(\w+)\s*\([^)]*\)\s*\{',
    re.MULTILINE
)

new_funcs = []
for m in func_re.finditer(content):
    name = m.group(1)
    if name in preexisting:
        continue
    # Extract function body
    brace_start = content.index('{', m.end() - 1)
    depth, i = 0, brace_start
    while i < len(content):
        if content[i] == '{': depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0: break
        i += 1
    body = content[brace_start:i+1]
    new_funcs.append((name, body))

if not new_funcs:
    print('FAIL: no new functions added to utils.h')
    sys.exit(1)

# Accept any new function that:
#   (a) relates to modulo AND has an optimization barrier, OR
#   (b) has a name containing 'mod' or 'safe' AND body >=4 meaningful lines
found = False
for name, body in new_funcs:
    has_mod = '%' in body or 'mod' in name.lower() or 'remainder' in body.lower()
    has_barrier = ('volatile' in body or 'optnone' in body or
                   '__attribute__' in body or 'asm' in body or 'noinline' in body)
    meaningful = [l for l in body.split('\n') if l.strip() and not l.strip().startswith('//')]

    if has_mod and has_barrier:
        found = True
        print(f'Found: {name} (mod + optimization barrier)')
        break
    elif ('mod' in name.lower() or 'safe' in name.lower()) and len(meaningful) >= 4:
        found = True
        print(f'Found: {name} (name match + {len(meaningful)} meaningful lines)')
        break

if not found:
    names = [n for n, _ in new_funcs]
    print(f'FAIL: new functions {names} do not qualify as modulo-safety helpers')
    sys.exit(1)

print('PASS: utils.h has new modulo-safety function')
PYEOF
if [ $? -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.10)")
    echo "PASS [0.10]: utils.h has new modulo-safety function"
else
    echo "FAIL [0.10]: utils.h missing modulo-safety function"
fi

# ── PASS-TO-PASS (0.10): existing utils.h functions + anti-stub ──────
# [pr_diff] (0.10): floor_divide and fmod still present; files not gutted
python3 << 'PYEOF'
import sys, re

# Check existing functions preserved
content = open('c10/metal/utils.h').read()
for fn in ['floor_divide', 'fmod']:
    if not re.search(rf'\b{fn}\s*\(', content):
        print(f'FAIL: {fn} function missing from utils.h')
        sys.exit(1)

# Anti-stub: files have substantial content
mps_lines = open('torch/_inductor/codegen/mps.py').read().count('\n')
utils_lines = content.count('\n')
if mps_lines < 100:
    print(f'FAIL: mps.py only {mps_lines} lines — appears gutted')
    sys.exit(1)
if utils_lines < 50:
    print(f'FAIL: utils.h only {utils_lines} lines — appears gutted')
    sys.exit(1)

print('PASS: existing functions preserved, files intact')
PYEOF
if [ $? -eq 0 ]; then
    REWARD=$(python3 -c "print($REWARD + 0.10)")
    echo "PASS [0.10]: existing functions + anti-stub"
else
    echo "FAIL [0.10]: existing functions missing or files gutted"
fi

# ── Summary ──────────────────────────────────────────────────────────
echo ""
echo "Total reward: $REWARD / 1.0"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
r = $REWARD
json.dump({
    'reward': r,
    'behavioral': round(min(r, 0.80), 2),
    'regression': round(min(max(r - 0.80, 0), 0.10), 2),
    'structural': round(min(max(r - 0.90, 0), 0.10), 2)
}, open('/logs/verifier/reward.json', 'w'))
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
