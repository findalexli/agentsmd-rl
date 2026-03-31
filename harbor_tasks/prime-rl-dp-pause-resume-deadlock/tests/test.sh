#!/usr/bin/env bash
set +e

REPO="/workspace/prime-rl"
PATCHES="$REPO/src/prime_rl/inference/patches.py"

mkdir -p /logs/verifier
SCORE=0

echo "=== Gate: Syntax check ==="
# [pr_diff] (0.00): File must be valid Python syntax
if ! python3 -c "import ast; ast.parse(open('$PATCHES').read())"; then
    echo "GATE FAILED: patches.py has syntax errors"
    echo "0" > /logs/verifier/reward.txt
    exit 0
fi
echo "  PASS: syntax ok"

echo ""
echo "=== Behavioral: Mock-based DP pause/resume tests ==="

# [pr_diff] (0.30): Unpaused + old wave → sends notification with engines_running=True
# [pr_diff] (0.20): Paused + old wave → does NOT send notification (conditional on test 1)
# [pr_diff] (0.10): New wave (unpaused) → current_wave updated
# [pr_diff] (0.05): New wave (paused) → current_wave updated regardless of pause
# [pr_diff] (0.05): Patch targets DPEngineCoreProc explicitly (in __dict__)
BEHAVIORAL_SCORE=$(python3 << 'PYEOF'
import sys, types, importlib, enum, queue

# ---- Build mock vllm modules so patches.py can import them ----
class PauseState(enum.Enum):
    UNPAUSED = 0
    PAUSED = 1

sched_interface = types.ModuleType("vllm.v1.core.sched.interface")
sched_interface.PauseState = PauseState

class EngineCoreOutputs:
    def __init__(self, **kwargs):
        self.start_wave = kwargs.get("start_wave")
    def __repr__(self):
        return f"EngineCoreOutputs(start_wave={self.start_wave})"

engine_mod = types.ModuleType("vllm.v1.engine")
engine_mod.EngineCoreOutputs = EngineCoreOutputs

class Request:
    pass

request_mod = types.ModuleType("vllm.v1.request")
request_mod.Request = Request

class EngineCore:
    def __init__(self):
        self.has_coordinator = True
        self.current_wave = 1
        self.engines_running = False
        self.scheduler = types.SimpleNamespace(pause_state=PauseState.UNPAUSED)
        self.output_queue = queue.Queue()

    def add_request(self, request, request_wave=0):
        """Base implementation: no-op."""
        pass

class DPEngineCoreProc(EngineCore):
    pass

engine_core_mod = types.ModuleType("vllm.v1.engine.core")
engine_core_mod.EngineCore = EngineCore
engine_core_mod.DPEngineCoreProc = DPEngineCoreProc

for name, mod in [
    ("vllm", types.ModuleType("vllm")),
    ("vllm.v1", types.ModuleType("vllm.v1")),
    ("vllm.v1.core", types.ModuleType("vllm.v1.core")),
    ("vllm.v1.core.sched", types.ModuleType("vllm.v1.core.sched")),
    ("vllm.v1.core.sched.interface", sched_interface),
    ("vllm.v1.engine", engine_mod),
    ("vllm.v1.engine.core", engine_core_mod),
    ("vllm.v1.request", request_mod),
]:
    sys.modules[name] = mod

# ---- Import and apply the patch ----
sys.path.insert(0, "/workspace/prime-rl/src")
patches_mod = importlib.import_module("prime_rl.inference.patches")

if not hasattr(patches_mod, "monkey_patch_dp_engine_core_pause_resume_deadlock"):
    print("0.0")
    sys.exit(0)

patches_mod.monkey_patch_dp_engine_core_pause_resume_deadlock()

score = 0.0
test1_passed = False

# Test 1 (0.30): Unpaused + old wave → sends notification with engines_running=True
engine1 = DPEngineCoreProc()
engine1.has_coordinator = True
engine1.current_wave = 5
engine1.engines_running = False
engine1.scheduler = types.SimpleNamespace(pause_state=PauseState.UNPAUSED)
engine1.output_queue = queue.Queue()
engine1.add_request(Request(), request_wave=3)

if not engine1.output_queue.empty():
    item = engine1.output_queue.get()
    if isinstance(item, tuple) and item[0] == -1 and item[1].start_wave == 5:
        if engine1.engines_running:
            score += 0.30
            test1_passed = True
            print("  PASS (0.30): Unpaused old-wave sends notification with engines_running=True", file=sys.stderr)
        else:
            print("  FAIL: engines_running not set to True", file=sys.stderr)
    else:
        print(f"  FAIL: Wrong notification format: {item}", file=sys.stderr)
else:
    print("  FAIL: No notification sent when unpaused with old wave", file=sys.stderr)

# Test 2 (0.20): Paused + old wave → NO notification
# Only scores if Test 1 proved the code CAN send notifications (prevents no-op gaming)
engine2 = DPEngineCoreProc()
engine2.has_coordinator = True
engine2.current_wave = 5
engine2.engines_running = False
engine2.scheduler = types.SimpleNamespace(pause_state=PauseState.PAUSED)
engine2.output_queue = queue.Queue()
engine2.add_request(Request(), request_wave=3)

if test1_passed and engine2.output_queue.empty():
    score += 0.20
    print("  PASS (0.20): Paused old-wave does NOT send notification", file=sys.stderr)
elif not test1_passed:
    print("  SKIP (0.20): Test 2 requires Test 1 to pass first (proves code can send notifications)", file=sys.stderr)
else:
    print("  FAIL: Notification sent when paused (would cause deadlock)", file=sys.stderr)

# Test 3 (0.10): New wave (unpaused) → current_wave updated
engine3 = DPEngineCoreProc()
engine3.has_coordinator = True
engine3.current_wave = 5
engine3.engines_running = False
engine3.scheduler = types.SimpleNamespace(pause_state=PauseState.UNPAUSED)
engine3.output_queue = queue.Queue()
engine3.add_request(Request(), request_wave=7)

if engine3.current_wave == 7:
    score += 0.10
    print("  PASS (0.10): current_wave updated to request_wave when higher (unpaused)", file=sys.stderr)
else:
    print(f"  FAIL: current_wave={engine3.current_wave}, expected 7", file=sys.stderr)

# Test 4 (0.05): New wave (paused) → current_wave updated regardless of pause state
engine4 = DPEngineCoreProc()
engine4.has_coordinator = True
engine4.current_wave = 5
engine4.engines_running = False
engine4.scheduler = types.SimpleNamespace(pause_state=PauseState.PAUSED)
engine4.output_queue = queue.Queue()
engine4.add_request(Request(), request_wave=7)

if engine4.current_wave == 7:
    score += 0.05
    print("  PASS (0.05): current_wave updated when paused (regardless of pause state)", file=sys.stderr)
else:
    print(f"  FAIL: current_wave={engine4.current_wave}, expected 7 (paused)", file=sys.stderr)

# Test 5 (0.05): Patch targets DPEngineCoreProc explicitly (in its own __dict__)
if "add_request" in DPEngineCoreProc.__dict__:
    score += 0.05
    print("  PASS (0.05): DPEngineCoreProc explicitly patched (add_request in __dict__)", file=sys.stderr)
else:
    print("  FAIL: add_request not in DPEngineCoreProc.__dict__ (only inherited)", file=sys.stderr)

print(f"{score:.2f}")
PYEOF
)

echo "  Behavioral score: $BEHAVIORAL_SCORE"
SCORE=$(python3 -c "print(round($SCORE + ${BEHAVIORAL_SCORE:-0}, 4))")

echo ""
echo "=== Structural: Wired into transformers_v5_compat ==="
# [pr_diff] (0.10): The new patch function is called from transformers_v5_compat
WIRED_SCORE=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/prime-rl/src/prime_rl/inference/patches.py") as f:
    tree = ast.parse(f.read())

# Find transformers_v5_compat and check it calls the deadlock patch function
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "transformers_v5_compat":
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                name = child.func.id.lower()
                # Accept any reasonable name referencing the deadlock/pause/dp patch
                if ("deadlock" in name or "pause" in name or "dp_engine" in name or
                    ("patch" in name and any(k in name for k in ("dp", "wave", "engine", "add_request"))) or
                    ("fix" in name and any(k in name for k in ("dp", "wave", "engine", "deadlock"))) or
                    ("monkey" in name and any(k in name for k in ("dp", "engine", "pause")))):
                    print("0.10")
                    sys.exit(0)
        break

print("0.0")
PYEOF
)

echo "  Wired score: $WIRED_SCORE"
SCORE=$(python3 -c "print(round($SCORE + ${WIRED_SCORE:-0}, 4))")

echo ""
echo "=== Pass-to-pass: Existing patch functions still present ==="
# [pr_diff] (0.10): Existing monkey-patches not broken (transformers_v5_compat and _patch_qwen35_lora)
P2P_SCORE=$(python3 << 'PYEOF'
import ast

with open("/workspace/prime-rl/src/prime_rl/inference/patches.py") as f:
    tree = ast.parse(f.read())

func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
required = {"transformers_v5_compat", "_patch_qwen35_lora"}
if required.issubset(func_names):
    print("0.10")
else:
    missing = required - func_names
    print(f"  FAIL: Missing functions: {missing}", flush=True)
    print("0.0")
PYEOF
)

echo "  P2P score: $P2P_SCORE"
SCORE=$(python3 -c "print(round($SCORE + ${P2P_SCORE:-0}, 4))")

echo ""
echo "=== Structural: Anti-stub check ==="
# [pr_diff] (0.05): Patch function defines a replacement with meaningful logic (>=4 body stmts)
ANTI_STUB_SCORE=$(python3 << 'PYEOF'
import ast

with open("/workspace/prime-rl/src/prime_rl/inference/patches.py") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and ("pause" in node.name.lower() or
       "deadlock" in node.name.lower() or "dp_engine" in node.name.lower()):
        # Must contain a nested function (the replacement) with >=4 non-trivial body stmts
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef) and child is not node:
                real_stmts = [s for s in child.body
                    if not (isinstance(s, ast.Pass) or
                            (isinstance(s, ast.Expr) and isinstance(getattr(s, 'value', None), ast.Constant)))]
                if len(real_stmts) >= 4:
                    print("0.05")
                    exit()
        break

print("0.0")
PYEOF
)

echo "  Anti-stub score: $ANTI_STUB_SCORE"
SCORE=$(python3 -c "print(round($SCORE + ${ANTI_STUB_SCORE:-0}, 4))")

echo ""
echo "=== Config-derived: No unnecessary try/except ==="
# [agent_config] (0.05): "Avoid try/except blocks unless it's really necessary" — AGENTS.md:5 @ c2b99e69
CONFIG_SCORE=$(python3 << 'PYEOF'
import ast

with open("/workspace/prime-rl/src/prime_rl/inference/patches.py") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and ("pause" in node.name.lower() or
       "deadlock" in node.name.lower() or "dp_engine" in node.name.lower()):
        for child in ast.walk(node):
            if isinstance(child, (ast.Try, ast.ExceptHandler)):
                print("0.0")
                exit()
        print("0.05")
        exit()

print("0.0")
PYEOF
)

echo "  Config score: $CONFIG_SCORE"
SCORE=$(python3 -c "print(round($SCORE + ${CONFIG_SCORE:-0}, 4))")

echo ""
echo "=== Final Score ==="
echo "  Total: $SCORE"
echo "$SCORE" > /logs/verifier/reward.txt

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
