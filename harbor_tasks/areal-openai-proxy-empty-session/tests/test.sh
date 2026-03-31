#!/usr/bin/env bash
set +e

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="/workspace/AReaL"
TARGET="$REPO/areal/experimental/openai/proxy/workflow.py"

echo "=== Testing areal-openai-proxy-empty-session ==="

# GATE: Syntax check
if ! python3 -c "import ast; ast.parse(open('$TARGET').read())" 2>/dev/null; then
    echo "GATE FAILED: $TARGET has syntax errors"
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0}' > "/logs/verifier/reward.json"
    echo "0.0" > "/logs/verifier/reward.txt"
    exit 0
fi
echo "GATE PASSED: syntax valid"

# All checks in a single Python script
python3 - "$TARGET" "$TASK_DIR" << 'ENDPYTHON'
import ast, textwrap, asyncio, logging, sys, json
from unittest.mock import MagicMock

TARGET = sys.argv[1]
TASK_DIR = sys.argv[2]

source = open(TARGET).read()
tree = ast.parse(source)
results = {}

# Find arun_episode
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.AsyncFunctionDef) and node.name == "arun_episode":
        func_node = node
        break

if func_node is None:
    for name in ["BEHAV1","BEHAV2","BEHAV3","BEHAV4","REGR1","CONFIG1","CONFIG2"]:
        results[name] = False
else:
    all_lines = source.splitlines()
    method_lines = all_lines[func_node.lineno - 1 : func_node.end_lineno]

    # ---------------------------------------------------------------
    # Extract the interactions-handling tail of the online-mode branch.
    # This is the segment from empty-check/stats-recording to "return interactions".
    # We exec it with mock deps to test BEHAVIOR, not just structure.
    # ---------------------------------------------------------------
    tail_start = None
    tail_end = None
    for i, line in enumerate(method_lines):
        s = line.strip()
        lower_s = s.lower()
        if tail_start is None:
            if ("record stats" in lower_s
                or ("interactions" in s and s.startswith("if"))
                or "list(interactions" in s
                or ("empty" in lower_s and "interact" in lower_s)
                or ("no interactions" in lower_s)):
                tail_start = i
        if tail_start is not None and s.startswith("return interactions"):
            tail_end = i + 1
            # Look ahead for a 'return None' shortly after (handles positive-check pattern)
            for j in range(i + 1, min(i + 5, len(method_lines))):
                sj = method_lines[j].strip()
                if sj.startswith("return None") or sj == "return None":
                    tail_end = j + 1
                    break
                if sj and not sj.startswith("#") and not sj.startswith("logger"):
                    break
            break

    can_extract = tail_start is not None

    def run_tail_test(interactions_setup, func_name):
        """Extract the tail, wrap in async func with mocks, run it.
        Returns (return_value, log_records) or None on failure."""
        if not can_extract:
            return None
        end = tail_end if tail_end else len(method_lines)
        raw_tail = "\n".join(method_lines[tail_start:end])
        tail = textwrap.dedent(raw_tail)

        # Build: module-level log capture list + async test function
        code_lines = [
            "_log = []",
            f"async def {func_name}():",
            "    import logging as _lg",
            "    from unittest.mock import MagicMock as _M",
            "    class _H(_lg.Handler):",
            "        def emit(s, r): _log.append(r)",
            f"    logger = _lg.getLogger('{func_name}')",
            "    logger.handlers.clear()",
            "    logger.addHandler(_H())",
            "    logger.setLevel(_lg.DEBUG)",
            "    session_info = _M()",
            "    session_info.session_id = 'test-session'",
            "    workflow_context = _M()",
            "    workflow_context.stat_scope.return_value = 'scope'",
            "    stats_tracker = _M()",
            "    self = _M()",
            f"    {interactions_setup}",
        ]
        for tl in tail.splitlines():
            code_lines.append("    " + tl)

        code = "\n".join(code_lines)
        ns = {}
        try:
            exec(compile(code, f"<{func_name}>", "exec"), ns)
            ret = asyncio.run(ns[func_name]())
            return (ret, ns.get("_log", []))
        except IndexError:
            return ("INDEXERROR", ns.get("_log", []))
        except Exception as e:
            return (f"EXCEPTION:{type(e).__name__}", ns.get("_log", []))

    # ---------------------------------------------------------------
    # [pr_diff] (0.35): F2P — Empty interactions must return None.
    # Buggy code returns {} (empty dict). Fixed code returns None.
    # ---------------------------------------------------------------
    out1 = run_tail_test("interactions = {}", "_t_empty")
    if out1 is not None:
        ret, _ = out1
        results["BEHAV1"] = (ret is None)
        if not results["BEHAV1"]:
            print(f"  BEHAV1 debug: got {ret!r} instead of None")
    else:
        results["BEHAV1"] = False
        print("  BEHAV1 debug: could not extract tail")

    # ---------------------------------------------------------------
    # [pr_diff] (0.20): F2P — Warning must be logged for empty sessions.
    # ---------------------------------------------------------------
    out2 = run_tail_test("interactions = {}", "_t_warn")
    if out2 is not None:
        _, logs = out2
        results["BEHAV2"] = any(r.levelno >= logging.WARNING for r in logs)
        if not results["BEHAV2"]:
            levels = [r.levelname for r in logs]
            print(f"  BEHAV2 debug: log levels={levels}")
    else:
        results["BEHAV2"] = False

    # ---------------------------------------------------------------
    # [pr_diff] (0.15): P2P — Non-empty interactions must return dict.
    # ---------------------------------------------------------------
    out3 = run_tail_test(
        "interactions = {'s1': _M(reward=0.75), 's2': _M(reward=0.9)}",
        "_t_nonempty"
    )
    if out3 is not None:
        ret3, _ = out3
        results["BEHAV3"] = isinstance(ret3, dict) and len(ret3) >= 2
        if not results["BEHAV3"]:
            print(f"  BEHAV3 debug: got {ret3!r}")
    else:
        results["BEHAV3"] = False

    # ---------------------------------------------------------------
    # [pr_diff] (0.10): Buggy list(keys())[-1] pattern removed,
    # reward access still present (stats not deleted).
    # ---------------------------------------------------------------
    method_text = ast.get_source_segment(source, func_node) or ""
    # Only check the online-mode branch (before "Normal mode" comment)
    online_text = method_text.split("Normal mode")[0] if "Normal mode" in method_text else method_text
    has_buggy = "list(interactions.keys())[-1]" in online_text
    has_reward = ".reward" in online_text
    results["BEHAV4"] = (not has_buggy) and has_reward

    # ---------------------------------------------------------------
    # [pr_diff] (0.10): Anti-stub — method body must be substantive.
    # ---------------------------------------------------------------
    body = func_node.body
    skip = 0
    if (body and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)):
        skip = 1
    results["REGR1"] = len(body[skip:]) >= 5

    # ---------------------------------------------------------------
    # [agent_config] (0.05): No wildcard imports — AGENTS.md:25 @ 84eaef12
    # ---------------------------------------------------------------
    has_wildcard = False
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.names:
            if any(a.name == "*" for a in n.names):
                has_wildcard = True
    results["CONFIG1"] = not has_wildcard

    # ---------------------------------------------------------------
    # [agent_config] (0.05): No print() in arun_episode — AGENTS.md:84-86 @ 84eaef12
    # ---------------------------------------------------------------
    has_print = False
    for child in ast.walk(func_node):
        if (isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
            and child.func.id == "print"):
            has_print = True
    results["CONFIG2"] = not has_print

# ---------------------------------------------------------------
# Score
# ---------------------------------------------------------------
weights = {
    "BEHAV1": 0.35, "BEHAV2": 0.20, "BEHAV3": 0.15, "BEHAV4": 0.10,
    "REGR1": 0.10, "CONFIG1": 0.05, "CONFIG2": 0.05,
}

score = sum(weights[k] for k, v in results.items() if v)

for name in ["BEHAV1","BEHAV2","BEHAV3","BEHAV4","REGR1","CONFIG1","CONFIG2"]:
    passed = results.get(name, False)
    status = "PASSED" if passed else "FAILED"
    print(f"{name} {status} ({weights[name]:.2f})")

print(f"\n=== FINAL SCORE: {score:.2f} ===")

behavioral = sum(weights[k] for k in ["BEHAV1","BEHAV2","BEHAV3","BEHAV4"] if results.get(k))
regression = weights["REGR1"] if results.get("REGR1") else 0
config = sum(weights[k] for k in ["CONFIG1","CONFIG2"] if results.get(k))

with open(f"/logs/verifier/reward.json", "w") as f:
    json.dump({
        "reward": round(score, 2),
        "behavioral": round(behavioral, 2),
        "regression": round(regression, 2),
        "config": round(config, 2),
    }, f)
with open(f"/logs/verifier/reward.txt", "w") as f:
    f.write(f"{score:.2f}\n")
ENDPYTHON

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
