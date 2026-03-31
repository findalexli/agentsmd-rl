#!/usr/bin/env bash
set +e

APP_FILE="/workspace/AReaL/areal/experimental/inference_service/data_proxy/app.py"
SCORE=0

# =========================================================================
# GATE: Python syntax check — abort on failure
# =========================================================================
# [pr_diff] (0.00): File must be valid Python
if ! python3 -c "
import ast, sys
try:
    ast.parse(open('$APP_FILE').read())
except SyntaxError as e:
    print(f'GATE FAIL: {e}', file=sys.stderr)
    sys.exit(1)
"; then
    echo "GATE: syntax check FAILED — aborting"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE: syntax OK"

# =========================================================================
# Helper: extract batch handler, build mini FastAPI app, run httpx tests
# =========================================================================
# WHY AST extraction: app.py transitively imports torch, transformers,
# datasets, peft — cannot import in CPU-only container. We extract the
# handler function via AST, exec it in a namespace with mock deps, and
# test real HTTP behavior via httpx AsyncClient.

cat > /tmp/test_behavioral.py << 'PYEOF'
import ast, sys, textwrap, json, asyncio, logging, os

APP_FILE = os.environ.get("APP_FILE", "/workspace/AReaL/areal/experimental/inference_service/data_proxy/app.py")
source = open(APP_FILE).read()
tree = ast.parse(source)

# Find the POST /data/batch handler
handler_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if (dec.func.attr == 'post' and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                    and dec.args[0].value == '/data/batch'):
                    handler_node = node
                    break
        if handler_node:
            break

results = {
    "handler_found": False,
    "handler_executable": False,
    "valid_batch_200": False,
    "valid_batch_data": False,
    "missing_shard_error": False,
    "invalid_input_rejected": False,
}

if handler_node is None:
    print(json.dumps(results))
    sys.exit(0)

results["handler_found"] = True

# Extract function source (the def line through end_lineno)
lines = source.splitlines(keepends=True)
func_start = handler_node.lineno - 1  # 0-indexed; points to 'async def' line
func_end = handler_node.end_lineno     # 1-indexed inclusive
func_source = textwrap.dedent("".join(lines[func_start:func_end]))

import fastapi, httpx, orjson
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.responses import Response as RawResponse
from httpx import ASGITransport

app = fastapi.FastAPI()

# Mock rtensor_storage with known data
class MockStorage:
    def __init__(self):
        self.data = {
            "shard_a": [1, 2, 3],
            "shard_b": [4, 5, 6],
            "shard_c": {"key": "value"},
        }
    def fetch(self, sid):
        if sid in self.data:
            return self.data[sid]
        raise KeyError(sid)

ns = {
    # FastAPI / response types
    "Request": Request, "HTTPException": HTTPException,
    "JSONResponse": JSONResponse, "StreamingResponse": StreamingResponse,
    "RawResponse": RawResponse, "Response": fastapi.Response,
    # Application deps
    "rtensor_storage": MockStorage(),
    "serialize_value": lambda v: v,  # identity — the real one serializes tensors
    "orjson": orjson,
    "json": __import__("json"),
    "logger": logging.getLogger("test_batch"),
    "app": app,
    "__builtins__": __builtins__,
}

try:
    exec('@app.post("/data/batch")\n' + func_source, ns)
    results["handler_executable"] = True
except Exception as e:
    print(f"Could not exec handler: {e}", file=sys.stderr)
    print(json.dumps(results))
    sys.exit(0)

# Also register param routes AFTER batch (mimicking correct ordering)
@app.put("/data/{shard_id}")
async def store_shard(shard_id: str):
    return {"status": "ok"}

@app.get("/data/{shard_id}")
async def get_shard(shard_id: str):
    return {"status": "ok"}


async def run_tests():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # ---- Test 1: valid batch request ----
        try:
            resp = await client.post("/data/batch", json={"shard_ids": ["shard_a", "shard_b"]})
            results["valid_batch_200"] = (resp.status_code == 200)
            if resp.status_code == 200:
                try:
                    body = orjson.loads(resp.content)
                    # Must return a list of 2 shard payloads
                    results["valid_batch_data"] = (
                        isinstance(body, list) and len(body) == 2
                    )
                except Exception:
                    results["valid_batch_data"] = False
        except Exception as e:
            print(f"valid_batch error: {e}", file=sys.stderr)

        # ---- Test 2: missing shard → error status ----
        try:
            resp = await client.post("/data/batch", json={"shard_ids": ["nonexistent_xyz_123"]})
            # Accept 400, 404, or 422 — any non-200 error indicating missing shard
            results["missing_shard_error"] = resp.status_code in (400, 404, 422, 500)
            if resp.status_code == 200:
                results["missing_shard_error"] = False  # should not succeed
        except Exception as e:
            print(f"missing_shard error: {e}", file=sys.stderr)

        # ---- Test 3: invalid input (non-list shard_ids) → rejected ----
        try:
            resp = await client.post("/data/batch", json={"shard_ids": "not_a_list"})
            results["invalid_input_rejected"] = resp.status_code in (400, 422)
        except Exception as e:
            print(f"invalid_input error: {e}", file=sys.stderr)

asyncio.run(run_tests())
print(json.dumps(results))
PYEOF

# Run behavioral tests
BEHAVIORAL_JSON=$(APP_FILE="$APP_FILE" python3 /tmp/test_behavioral.py 2>/dev/null)
if [ $? -ne 0 ] || [ -z "$BEHAVIORAL_JSON" ]; then
    BEHAVIORAL_JSON='{"handler_found":false,"handler_executable":false,"valid_batch_200":false,"valid_batch_data":false,"missing_shard_error":false,"invalid_input_rejected":false}'
fi

# Parse results
handler_found=$(echo "$BEHAVIORAL_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('handler_found', False))")
handler_exec=$(echo "$BEHAVIORAL_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('handler_executable', False))")
valid_200=$(echo "$BEHAVIORAL_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('valid_batch_200', False))")
valid_data=$(echo "$BEHAVIORAL_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('valid_batch_data', False))")
missing_err=$(echo "$BEHAVIORAL_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('missing_shard_error', False))")
invalid_rej=$(echo "$BEHAVIORAL_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('invalid_input_rejected', False))")

# =========================================================================
# Fail-to-pass: POST /data/batch returns correct data (behavioral)
# =========================================================================
# [pr_diff] (0.35): POST /data/batch retrieves multiple shards and returns serialized data
if [ "$valid_200" = "True" ] && [ "$valid_data" = "True" ]; then
    echo "CHECK: Valid batch returns 200 + correct data — PASS (0.35)"
    SCORE=$(python3 -c "print($SCORE + 0.35)")
else
    echo "CHECK: Valid batch returns 200 + correct data — FAIL (found=$handler_found exec=$handler_exec 200=$valid_200 data=$valid_data)"
fi

# =========================================================================
# Fail-to-pass: Missing shard returns error (behavioral)
# =========================================================================
# [pr_diff] (0.15): POST /data/batch returns error status for nonexistent shards
# Gated on happy-path passing to prevent "always return 400" gaming
if [ "$valid_200" = "True" ] && [ "$valid_data" = "True" ] && [ "$missing_err" = "True" ]; then
    echo "CHECK: Missing shard returns error — PASS (0.15)"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "CHECK: Missing shard returns error — FAIL (gated on valid_batch)"
fi

# =========================================================================
# Fail-to-pass: Invalid input rejected (behavioral)
# =========================================================================
# [pr_diff] (0.10): POST /data/batch rejects non-list shard_ids with 400/422
# Gated on happy-path passing to prevent "always return 400" gaming
if [ "$valid_200" = "True" ] && [ "$valid_data" = "True" ] && [ "$invalid_rej" = "True" ]; then
    echo "CHECK: Invalid input rejected — PASS (0.10)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "CHECK: Invalid input rejected — FAIL (gated on valid_batch)"
fi

# =========================================================================
# Fail-to-pass: Route ordering — /data/batch before /data/{shard_id}
# =========================================================================
# [pr_diff] (0.15): /data/batch declared before /data/{shard_id} (FastAPI matches in order)
# WHY structural: route ordering is a declaration-order property, not runtime-testable
# in isolation (our mini app always has correct ordering). Must check source AST.
if python3 -c "
import ast, sys

source = open('$APP_FILE').read()
tree = ast.parse(source)

batch_line = None
param_line = None

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if dec.args and isinstance(dec.args[0], ast.Constant):
                    path = dec.args[0].value
                    method = dec.func.attr
                    if path == '/data/batch' and method == 'post':
                        batch_line = node.lineno
                    elif '{shard_id}' in str(path) and param_line is None:
                        param_line = node.lineno

if batch_line is None:
    print('FAIL: /data/batch not found', file=sys.stderr)
    sys.exit(1)
if param_line is not None and batch_line >= param_line:
    print(f'FAIL: /data/batch (L{batch_line}) must precede /data/{{shard_id}} (L{param_line})', file=sys.stderr)
    sys.exit(1)
print(f'Route ordering OK: batch at L{batch_line}, param at L{param_line}')
"; then
    echo "CHECK: Route ordering (batch before shard_id) — PASS (0.15)"
    SCORE=$(python3 -c "print($SCORE + 0.15)")
else
    echo "CHECK: Route ordering — FAIL"
fi

# =========================================================================
# Pass-to-pass: Existing routes still present (regression)
# =========================================================================
# [pr_diff] (0.10): Existing PUT/GET/DELETE data routes still registered
if python3 -c "
import ast, sys

source = open('$APP_FILE').read()
tree = ast.parse(source)

routes = set()
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                method = dec.func.attr
                if dec.args and isinstance(dec.args[0], ast.Constant):
                    routes.add((method, dec.args[0].value))

required = [
    ('put', '/data/{shard_id}'),
    ('get', '/data/{shard_id}'),
    ('delete', '/data/clear'),
]

for method, path in required:
    if (method, path) not in routes:
        print(f'FAIL: missing existing route {method.upper()} {path}', file=sys.stderr)
        sys.exit(1)
print('All existing data routes present')
"; then
    echo "CHECK: Existing routes preserved — PASS (0.10)"
    SCORE=$(python3 -c "print($SCORE + 0.10)")
else
    echo "CHECK: Existing routes — FAIL"
fi

# =========================================================================
# Config-derived: No wildcard imports
# =========================================================================
# [agent_config] (0.05): "No wildcard imports" — AGENTS.md:30 @ 0405b5c
if ! grep -qE '^\s*from\s+\S+\s+import\s+\*' "$APP_FILE"; then
    echo "CHECK: No wildcard imports — PASS (0.05)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "CHECK: No wildcard imports — FAIL"
fi

# =========================================================================
# Config-derived: No hardcoded endpoints
# =========================================================================
# [agent_config] (0.05): "No hardcoded secrets, paths, or endpoints" — AGENTS.md:31 @ 0405b5c
if ! grep -E "(localhost|127\.0\.0\.1|0\.0\.0\.0):[0-9]+" "$APP_FILE" 2>/dev/null | grep -v "^\s*#" | grep -q .; then
    echo "CHECK: No hardcoded endpoints — PASS (0.05)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "CHECK: No hardcoded endpoints — FAIL"
fi

# =========================================================================
# Config-derived: Handler has meaningful error responses
# =========================================================================
# [agent_config] (0.05): Error responses use structured JSON — follows existing patterns
# Accept any approach: JSONResponse, Response with JSON body, dict return, etc.
if python3 -c "
import ast, sys

source = open('$APP_FILE').read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                if (dec.func.attr == 'post' and dec.args
                    and isinstance(dec.args[0], ast.Constant)
                    and dec.args[0].value == '/data/batch'):
                    # Handler must have at least one status_code keyword in a call
                    # (JSONResponse, Response, HTTPException — any structured error)
                    has_status = False
                    for child in ast.walk(node):
                        if isinstance(child, ast.keyword) and child.arg == 'status_code':
                            has_status = True
                            break
                        if isinstance(child, ast.Raise):
                            has_status = True  # raising HTTPException is fine too
                            break
                    if has_status:
                        print('Handler uses structured error responses')
                        sys.exit(0)
                    print('FAIL: no status_code or raise in handler', file=sys.stderr)
                    sys.exit(1)
print('FAIL: handler not found', file=sys.stderr)
sys.exit(1)
"; then
    echo "CHECK: Structured error responses — PASS (0.05)"
    SCORE=$(python3 -c "print($SCORE + 0.05)")
else
    echo "CHECK: Structured error responses — FAIL"
fi

# =========================================================================
# Final score
# =========================================================================
SCORE=$(python3 -c "print(round($SCORE, 2))")
echo ""
echo "=== FINAL SCORE: $SCORE ==="
echo "$SCORE" > /logs/verifier/reward.txt

echo "{\"reward\": $SCORE}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
