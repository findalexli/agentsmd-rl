#!/usr/bin/env bash
set +e

REPO="/workspace/slime"
FILE="$REPO/slime/ray/rollout.py"
TOTAL=0
MAX=100

add() { TOTAL=$((TOTAL + $1)); }

# ──────────────────────────────────────────────────────────
# GATE (0.00): Syntax check — abort on failure
# ──────────────────────────────────────────────────────────
# [pr_diff] (0.00): File must be valid Python
python3 -c "
import ast, sys
try:
    ast.parse(open('$FILE').read())
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
print('GATE PASS: syntax OK')
" || { echo "0.0" > /logs/verifier/reward.txt; exit 0; }

# ──────────────────────────────────────────────────────────
# BEHAVIORAL FAIL-TO-PASS (0.40): Core closure bug
# Extract _make_group body, run it with mocked deps, verify
# router params come from function args not closure.
# ──────────────────────────────────────────────────────────

# [pr_diff] (0.40): _make_group uses its own params for router, not closure state
python3 << 'PYEOF'
import ast, sys, textwrap, types

source = open("/workspace/slime/slime/ray/rollout.py").read()
tree = ast.parse(source)

# ---- locate _make_group inside start_rollout_servers ----
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_make_group":
        func_node = node
        break

if func_node is None:
    print("FAIL: _make_group not found")
    sys.exit(1)

# ---- extract source lines ----
lines = source.splitlines(keepends=True)
func_lines = lines[func_node.lineno - 1 : func_node.end_lineno]
func_src = textwrap.dedent("".join(func_lines))

# ---- check the function accepts router connection info somehow ----
params = [a.arg for a in func_node.args.args]
# We accept any reasonable param name containing "router" or a **kwargs / generic config
has_router_params = (
    any("router" in p for p in params)
    or any(p in ("router_config", "router_info", "router_kwargs") for p in params)
    or func_node.args.kwarg is not None  # **kwargs
)
if not has_router_params:
    print(f"FAIL: _make_group params {params} — no way to receive router info")
    sys.exit(1)

# ---- build a mock environment and exec the function ----
# We'll provide two different sets of "closure" vs "param" router values.
# If the function uses closure values, we'll detect it via the ServerGroup mock.

captured_kwargs = {}

class MockServerGroup:
    def __init__(self, **kwargs):
        captured_kwargs.update(kwargs)

class MockBox:
    def __getattr__(self, name):
        if name == "hf_checkpoint":
            return "/fake/model"
        if name == "num_gpus_per_node":
            return 8
        if name == "offload_rollout":
            return False
        return MockBox()

class MockGroupCfg:
    num_gpus_per_engine = 1
    num_gpus = 2
    worker_type = "decode"
    overrides = {}

class MockLogger:
    def info(self, *a, **kw): pass
    def warning(self, *a, **kw): pass

# Closure variables — these are the WRONG values. If the function reads from
# closure, it will use these instead of the passed params.
CLOSURE_ROUTER_IP = "CLOSURE_STALE_IP"
CLOSURE_ROUTER_PORT = 99999

# The CORRECT values we pass as arguments
PARAM_ROUTER_IP = "10.0.0.42"
PARAM_ROUTER_PORT = 8080

# Namespace that simulates the enclosing scope
ns = {
    "__builtins__": __builtins__,
    "ServerGroup": MockServerGroup,
    "args": MockBox(),
    "pg": None,
    "logger": MockLogger(),
    # closure router vars — stale/wrong values
    "router_ip": CLOSURE_ROUTER_IP,
    "router_port": CLOSURE_ROUTER_PORT,
    # nonlocal state
    "engine_offset": 0,
    "gpu_offset": 0,
    "rollout_pg_offset": 0,
    "megatron_num_gpus": 0,
}

try:
    exec(func_src, ns)
except Exception as e:
    print(f"FAIL: could not exec _make_group: {e}")
    sys.exit(1)

make_group_fn = ns.get("_make_group")
if make_group_fn is None:
    print("FAIL: _make_group not defined after exec")
    sys.exit(1)

# ---- call it, passing the correct router values ----
import inspect
sig = inspect.signature(make_group_fn)
param_names = list(sig.parameters.keys())

# Build call kwargs adaptively — we don't mandate specific param names
call_kwargs = {}
call_args = [MockGroupCfg()]

# Try to pass router info via whatever params exist
for pname in param_names:
    if "router_ip" in pname or pname == "router_ip":
        call_kwargs[pname] = PARAM_ROUTER_IP
    elif "router_port" in pname or pname == "router_port":
        call_kwargs[pname] = PARAM_ROUTER_PORT
    elif pname == "router_config" or pname == "router_info":
        call_kwargs[pname] = {"ip": PARAM_ROUTER_IP, "port": PARAM_ROUTER_PORT}

# If function uses **kwargs, pass router info there
if func_node.args.kwarg:
    call_kwargs.setdefault("router_ip", PARAM_ROUTER_IP)
    call_kwargs.setdefault("router_port", PARAM_ROUTER_PORT)

try:
    make_group_fn(*call_args, **call_kwargs)
except Exception as e:
    print(f"FAIL: _make_group raised: {e}")
    sys.exit(1)

# ---- verify ServerGroup received the CORRECT router values, not closure ----
got_ip = captured_kwargs.get("router_ip", None)
got_port = captured_kwargs.get("router_port", None)

if got_ip == CLOSURE_ROUTER_IP or got_port == CLOSURE_ROUTER_PORT:
    print(f"FAIL: ServerGroup got closure values router_ip={got_ip} router_port={got_port}")
    print("The function still reads router info from closure, not from its parameters")
    sys.exit(1)

if got_ip == PARAM_ROUTER_IP and got_port == PARAM_ROUTER_PORT:
    print(f"PASS: ServerGroup received correct param values router_ip={got_ip} router_port={got_port}")
    sys.exit(0)

# Could be a config-dict approach — check if router info is embedded somewhere
all_vals = str(captured_kwargs)
if PARAM_ROUTER_IP in all_vals and str(PARAM_ROUTER_PORT) in all_vals:
    print("PASS: ServerGroup received correct router values (via config object)")
    sys.exit(0)

print(f"FAIL: ServerGroup kwargs don't contain expected router values. Got: {captured_kwargs}")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then add 40; fi

# ──────────────────────────────────────────────────────────
# BEHAVIORAL (0.25): All call sites pass router info
# Extract start_rollout_servers body, check that every
# _make_group(...) call includes router arguments.
# ──────────────────────────────────────────────────────────

# [pr_diff] (0.25): Every call site to _make_group passes router connection info
python3 << 'PYEOF'
import ast, sys

source = open("/workspace/slime/slime/ray/rollout.py").read()
tree = ast.parse(source)

class CallFinder(ast.NodeVisitor):
    def __init__(self):
        self.calls = []
        self.in_target = False

    def visit_FunctionDef(self, node):
        if node.name == "start_rollout_servers":
            self.in_target = True
            self.generic_visit(node)
            self.in_target = False
        elif self.in_target:
            self.generic_visit(node)

    def visit_Call(self, node):
        if self.in_target and isinstance(node.func, ast.Name) and node.func.id == "_make_group":
            self.calls.append(node)
        self.generic_visit(node)

finder = CallFinder()
finder.visit(tree)

if len(finder.calls) < 3:
    print(f"FAIL: expected at least 3 _make_group call sites, found {len(finder.calls)}")
    sys.exit(1)

# Each call must pass more than just group_cfg — i.e., must include router info somehow.
# Accept: extra positional args, keyword args containing "router", or a config-like arg.
for i, call in enumerate(finder.calls):
    n_pos = len(call.args)
    kw_names = [kw.arg for kw in call.keywords if kw.arg is not None]
    has_extra = (
        n_pos >= 2  # at least group_cfg + something else
        or any("router" in (k or "") for k in kw_names)
        or any(kw.arg is None for kw in call.keywords)  # **kwargs expansion
    )
    if not has_extra:
        print(f"FAIL: call site {i+1} passes only {n_pos} positional arg(s) and keywords {kw_names}")
        print("No router info being passed")
        sys.exit(1)

print(f"PASS: all {len(finder.calls)} call sites pass router info to _make_group")
PYEOF
if [ $? -eq 0 ]; then add 25; fi

# ──────────────────────────────────────────────────────────
# PASS-TO-PASS (0.15): Existing structure preserved
# ──────────────────────────────────────────────────────────

# [pr_diff] (0.10): start_rollout_servers still exists with expected signature
python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'start_rollout_servers':
        params = [a.arg for a in node.args.args]
        if 'args' in params and 'pg' in params:
            print('PASS: start_rollout_servers(args, pg) intact')
            sys.exit(0)
print('FAIL: start_rollout_servers not found or signature changed')
sys.exit(1)
" && add 10

# [pr_diff] (0.05): _make_group body constructs ServerGroup (anti-stub)
python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_make_group':
        # Must have substantial body (>5 statements) and reference ServerGroup
        stmts = [n for n in ast.walk(node) if isinstance(n, ast.stmt)]
        body_dump = ast.dump(node)
        if len(stmts) < 5:
            print(f'FAIL: _make_group body too small ({len(stmts)} stmts), likely stub')
            sys.exit(1)
        if 'ServerGroup' not in body_dump:
            print('FAIL: _make_group does not construct ServerGroup')
            sys.exit(1)
        print('PASS: _make_group has substantial body with ServerGroup')
        sys.exit(0)
print('FAIL: _make_group not found')
sys.exit(1)
" && add 5

# ──────────────────────────────────────────────────────────
# CONFIG-DERIVED (0.10): Module structure intact
# ──────────────────────────────────────────────────────────

# [agent_config] (0.05): Module organization — .claude/skills/add-rollout-function/SKILL.md
python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
funcs = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
if 'start_rollout_servers' in funcs and '_make_group' in funcs:
    print('PASS: module structure intact')
else:
    print(f'FAIL: expected functions missing. Found: {funcs[:10]}')
    sys.exit(1)
" && add 5

# [agent_config] (0.05): _make_group still uses nonlocal for offset tracking — .claude/skills/add-rollout-function/SKILL.md
python3 -c "
import ast, sys
source = open('$FILE').read()
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_make_group':
        for child in ast.walk(node):
            if isinstance(child, ast.Nonlocal):
                names = child.names
                if 'engine_offset' in names or 'gpu_offset' in names:
                    print('PASS: nonlocal offset tracking preserved')
                    sys.exit(0)
        print('FAIL: nonlocal offset declaration missing')
        sys.exit(1)
print('FAIL: _make_group not found')
sys.exit(1)
" && add 5

# ──────────────────────────────────────────────────────────
# Final score
# ──────────────────────────────────────────────────────────
REWARD=$(python3 -c "print(round($TOTAL / $MAX, 4))")
echo ""
echo "Total score: $REWARD (${TOTAL}/${MAX})"
echo "$REWARD" > /logs/verifier/reward.txt

python3 -c "
import json
json.dump({
    'reward': $TOTAL / $MAX,
    'behavioral': min($TOTAL, 65) / 100,
    'regression': min(max($TOTAL - 65, 0), 15) / 100,
    'config': min(max($TOTAL - 80, 0), 10) / 100,
    'structural': min(max($TOTAL - 90, 0), 10) / 100,
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
