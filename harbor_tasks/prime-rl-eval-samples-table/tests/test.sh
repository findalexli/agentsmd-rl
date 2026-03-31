#!/usr/bin/env bash
set +e

BASE="/workspace/prime-rl/src/prime_rl"
MONITOR_BASE="$BASE/utils/monitor/base.py"
MONITOR_MULTI="$BASE/utils/monitor/multi.py"
MONITOR_WANDB="$BASE/utils/monitor/wandb.py"
MONITOR_PRIME="$BASE/utils/monitor/prime.py"
EVAL_UTILS="$BASE/orchestrator/eval_utils.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TOTAL=0

# ========== GATE: Syntax check ==========
python3 -c "
import ast
for f in ['$MONITOR_BASE','$MONITOR_MULTI','$MONITOR_WANDB','$MONITOR_PRIME','$EVAL_UTILS']:
    ast.parse(open(f).read())
" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi
echo "GATE PASS: all files parse"

# ========== F2P BEHAVIORAL: ABC enforcement — subclass without log_eval_samples cannot instantiate (0.25) ==========
# [pr_diff] (0.25): Monitor ABC must declare log_eval_samples as abstract; missing impl → TypeError
python3 << 'PYEOF'
import sys
from unittest.mock import MagicMock

sys.modules['verifiers'] = MagicMock()
sys.path.insert(0, '/workspace/prime-rl/src')

from prime_rl.utils.monitor.base import Monitor

# Subclass implementing every OTHER abstract method but NOT log_eval_samples
class IncompleteMonitor(Monitor):
    def log(self, metrics, step): pass
    def log_samples(self, rollouts, step): pass
    def log_final_samples(self): pass

try:
    IncompleteMonitor()
    print("FAIL: instantiated without log_eval_samples — not abstract")
    sys.exit(1)
except TypeError as e:
    if "log_eval_samples" in str(e):
        print("PASS: TypeError for missing log_eval_samples")
        sys.exit(0)
    print(f"FAIL: TypeError but not about log_eval_samples: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.25)")
    echo "TEST f2p_abc: PASS"
else
    echo "TEST f2p_abc: FAIL"
fi

# ========== F2P BEHAVIORAL: WandbMonitor.log_eval_samples processes rollouts into table (0.20) ==========
# [pr_diff] (0.20): WandbMonitor must iterate rollouts, add rows to table, call wandb.log
# AST extraction justified: wandb.py imports wandb, torch, and WandbWithExtrasConfig at module level
python3 << 'PYEOF'
import ast, sys, textwrap
from unittest.mock import MagicMock, patch

TARGET = "/workspace/prime-rl/src/prime_rl/utils/monitor/wandb.py"
with open(TARGET) as f:
    source = f.read()
tree = ast.parse(source)

# Extract WandbMonitor.log_eval_samples method source
func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "WandbMonitor":
        for n in node.body:
            if isinstance(n, ast.FunctionDef) and n.name == "log_eval_samples":
                lines = source.splitlines(keepends=True)
                func_src = "".join(lines[n.lineno - 1 : n.end_lineno])
                break
if func_src is None:
    print("FAIL: WandbMonitor.log_eval_samples not found")
    sys.exit(1)

# Set up mocks
wandb_mock = MagicMock()
table_mock = MagicMock()

class FakeConfig:
    class _Extras:
        samples = True
    log_extras = _Extras()

mock_self = MagicMock()
mock_self.is_master = True
mock_self.config = FakeConfig()
mock_self.eval_samples_table = table_mock

# Build callable class with the extracted method
wrapper_src = "class _W:\n" + textwrap.indent(textwrap.dedent(func_src), "    ")
ns = {"wandb": wandb_mock, "WandbWithExtrasConfig": FakeConfig, "__builtins__": __builtins__}
try:
    exec(wrapper_src, ns)
except Exception as e:
    print(f"FAIL: cannot compile method: {e}")
    sys.exit(1)

method = ns["_W"].__dict__["log_eval_samples"]

# Test rollouts (dicts, matching vf.RolloutOutput structure)
test_rollouts = [
    {"example_id": "ex1", "completion": "answer1", "reward": 0.8, "task": "math"},
    {"example_id": "ex2", "completion": "answer2", "reward": 0.5, "task": "code"},
]
try:
    method(mock_self, rollouts=test_rollouts, env_name="gsm8k", step=100)
except Exception as e:
    print(f"FAIL: method raised: {e}")
    sys.exit(1)

# Verify table rows were added
add_calls = table_mock.add_data.call_args_list
if len(add_calls) < 1:
    print(f"FAIL: table.add_data never called (got {len(add_calls)} calls)")
    sys.exit(1)

# Verify wandb.log was called
if not wandb_mock.log.called:
    print("FAIL: wandb.log not called")
    sys.exit(1)

print(f"PASS: {len(add_calls)} rows added to table, wandb.log called")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.20)")
    echo "TEST f2p_wandb_behavior: PASS"
else
    echo "TEST f2p_wandb_behavior: FAIL"
fi

# ========== F2P BEHAVIORAL: MultiMonitor.log_eval_samples delegates to sub-monitors (0.15) ==========
# [pr_diff] (0.15): MultiMonitor must forward log_eval_samples calls to each sub-monitor
python3 << 'PYEOF'
import sys
from unittest.mock import MagicMock

sys.modules['verifiers'] = MagicMock()
sys.path.insert(0, '/workspace/prime-rl/src')

try:
    from prime_rl.utils.monitor.multi import MultiMonitor
except Exception as e:
    print(f"FAIL: cannot import MultiMonitor: {e}")
    sys.exit(1)

mock1 = MagicMock()
mock2 = MagicMock()

# Bypass __init__ and wire up internals directly
mm = object.__new__(MultiMonitor)
mm.monitors = [mock1, mock2]
mm.logger = MagicMock()

test_rollouts = [{"example_id": "1", "completion": "hi", "reward": 1.0}]

try:
    mm.log_eval_samples(rollouts=test_rollouts, env_name="test_env", step=42)
except AttributeError:
    print("FAIL: MultiMonitor has no log_eval_samples (bug not fixed)")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected error: {e}")
    sys.exit(1)

if not mock1.log_eval_samples.called or not mock2.log_eval_samples.called:
    print("FAIL: not all sub-monitors received the call")
    sys.exit(1)

print("PASS: delegated to both sub-monitors")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.15)")
    echo "TEST f2p_multi: PASS"
else
    echo "TEST f2p_multi: FAIL"
fi

# ========== F2P STRUCTURAL: evaluate_env calls log_eval_samples (0.15) ==========
# [pr_diff] (0.15): evaluate_env must call monitor.log_eval_samples after logging metrics
# AST justified: async orchestrator function with heavy deps (verifiers, torch, etc.)
python3 << 'PYEOF'
import ast, sys
with open("/workspace/prime-rl/src/prime_rl/orchestrator/eval_utils.py") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "evaluate_env":
        for n in ast.walk(node):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "log_eval_samples":
                print("PASS: evaluate_env calls log_eval_samples")
                sys.exit(0)
        print("FAIL: evaluate_env does not call log_eval_samples")
        sys.exit(1)
print("FAIL: evaluate_env function not found")
sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.15)")
    echo "TEST eval_call: PASS"
else
    echo "TEST eval_call: FAIL"
fi

# ========== P2P BEHAVIORAL: Existing abstract methods still enforced (0.10) ==========
# [repo_tests] (0.10): log, log_samples, log_final_samples must remain abstract
python3 << 'PYEOF'
import sys
from unittest.mock import MagicMock

sys.modules['verifiers'] = MagicMock()
sys.path.insert(0, '/workspace/prime-rl/src')

from prime_rl.utils.monitor.base import Monitor

for missing in ['log', 'log_samples', 'log_final_samples']:
    methods = {
        'log': lambda self, metrics, step: None,
        'log_samples': lambda self, rollouts, step: None,
        'log_final_samples': lambda self: None,
        'log_eval_samples': lambda self, rollouts, env_name, step: None,
    }
    del methods[missing]
    Cls = type('T', (Monitor,), methods)
    try:
        Cls()
        print(f"FAIL: instantiated without {missing}")
        sys.exit(1)
    except TypeError:
        pass

print("PASS: all original abstract methods preserved")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.10)")
    echo "TEST p2p_abc: PASS"
else
    echo "TEST p2p_abc: FAIL"
fi

# ========== STRUCTURAL: Anti-stub for WandbMonitor (0.05) ==========
# [pr_diff] (0.05): WandbMonitor.log_eval_samples body must be non-trivial
python3 << 'PYEOF'
import ast, sys
with open("/workspace/prime-rl/src/prime_rl/utils/monitor/wandb.py") as f:
    tree = ast.parse(f.read())
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "WandbMonitor":
        for n in node.body:
            if isinstance(n, ast.FunctionDef) and n.name == "log_eval_samples":
                stmts = sum(1 for s in ast.walk(n)
                            if isinstance(s, (ast.Assign, ast.Return, ast.If, ast.For, ast.Call, ast.AugAssign)))
                if stmts < 5:
                    print(f"FAIL: only {stmts} meaningful statements (stub)")
                    sys.exit(1)
                print(f"PASS: {stmts} meaningful statements")
                sys.exit(0)
print("FAIL: method not found"); sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.05)")
    echo "TEST antistub: PASS"
else
    echo "TEST antistub: FAIL"
fi

# ========== CONFIG: No unnecessary comments (0.05) ==========
# [agent_config] (0.05): "Do not add unnecessary comments" — AGENTS.md:7 @ 714d0ea9
python3 << 'PYEOF'
import sys
files = [
    "/workspace/prime-rl/src/prime_rl/utils/monitor/base.py",
    "/workspace/prime-rl/src/prime_rl/utils/monitor/multi.py",
    "/workspace/prime-rl/src/prime_rl/utils/monitor/prime.py",
    "/workspace/prime-rl/src/prime_rl/utils/monitor/wandb.py",
]
total = 0
for fpath in files:
    with open(fpath) as f:
        lines = f.readlines()
    in_method = False
    indent_level = None
    for line in lines:
        stripped = line.strip()
        if "def log_eval_samples" in stripped:
            in_method = True
            indent_level = len(line) - len(line.lstrip())
            continue
        if in_method:
            cur_indent = len(line) - len(line.lstrip())
            if stripped and cur_indent <= indent_level:
                in_method = False
                continue
            if stripped.startswith("#"):
                total += 1
if total > 8:
    print(f"FAIL: {total} comment lines in log_eval_samples methods (excessive)")
    sys.exit(1)
print(f"PASS: {total} comment lines")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.05)")
    echo "TEST config_comments: PASS"
else
    echo "TEST config_comments: FAIL"
fi

# ========== CONFIG: No bare except clauses (0.05) ==========
# [agent_config] (0.05): "Avoid try/except blocks unless really necessary" — AGENTS.md:5 @ 714d0ea9
python3 << 'PYEOF'
import ast, sys
for fpath, cls_name in [
    ("/workspace/prime-rl/src/prime_rl/utils/monitor/wandb.py", "WandbMonitor"),
    ("/workspace/prime-rl/src/prime_rl/utils/monitor/prime.py", "PrimeMonitor"),
]:
    with open(fpath) as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == cls_name:
            for n in node.body:
                if isinstance(n, ast.FunctionDef) and n.name == "log_eval_samples":
                    try_count = sum(1 for s in ast.walk(n) if isinstance(s, ast.Try))
                    if try_count > 1:
                        print(f"FAIL: {cls_name} has {try_count} try/except (excessive)")
                        sys.exit(1)
print("PASS: no unnecessary try/except")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    TOTAL=$(python3 -c "print($TOTAL + 0.05)")
    echo "TEST config_try_except: PASS"
else
    echo "TEST config_try_except: FAIL"
fi

# ========== SCORE ==========
echo "TOTAL: $TOTAL"
echo "$TOTAL" > "$REWARD_FILE"

# Optional LLM rubric judge
source /tests/judge_hook.sh 2>/dev/null || true
