#!/usr/bin/env bash
set +e

TOTAL=0

log() { echo "[$1] $2 (weight=$3) => $4"; }

add() {
    local w=$1 p=$2
    if [ "$p" = "1" ]; then
        TOTAL=$(python3 -c "print(round($TOTAL + $w, 4))")
    fi
}

REPO=/workspace/transformers

# ============================================================
# GATE: Syntax check on changed files
# ============================================================
echo "=== GATE: Syntax check ==="
GATE_PASS=1
for f in \
    src/transformers/processing_utils.py \
    src/transformers/utils/chat_template_utils.py \
    src/transformers/models/smolvlm/processing_smolvlm.py \
    src/transformers/models/voxtral/processing_voxtral.py; do
    if ! python3 -c "import ast; ast.parse(open('$REPO/$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" = "0" ]; then
    mkdir -p /logs/verifier
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "gate": "FAIL"}' > /logs/verifier/reward.json
    echo "GATE FAILED — aborting"
    exit 0
fi
echo "GATE: PASS"

# ============================================================
# [pr_diff] (0.30): F2P — _get_template_variables extracts correct variables
# Fails on base: function doesn't exist (ImportError)
# ============================================================
echo ""
echo "=== F2P: _get_template_variables works correctly ==="
RESULT=$(cd "$REPO" && python3 -c "
from transformers.utils.chat_template_utils import _get_template_variables

# Test 1: Standard + custom variables
t1 = '{{ messages }}{{ bos_token }}{% if custom_var %}yes{% endif %}'
v1 = _get_template_variables(t1)
assert 'messages' in v1, f'messages not in {v1}'
assert 'bos_token' in v1, f'bos_token not in {v1}'
assert 'custom_var' in v1, f'custom_var not in {v1}'
assert isinstance(v1, frozenset), f'Expected frozenset, got {type(v1)}'

# Test 2: Loop variables are NOT undeclared
t2 = '''{% for msg in messages %}{{ msg['role'] }}: {{ msg['content'] }}{% endfor %}{% if add_generation_prompt %}assistant:{% endif %}'''
v2 = _get_template_variables(t2)
assert 'messages' in v2
assert 'add_generation_prompt' in v2
assert 'msg' not in v2, f'loop var msg should not be in undeclared vars: {v2}'

# Test 3: Empty/simple template
t3 = 'Hello world'
v3 = _get_template_variables(t3)
assert len(v3) == 0, f'Expected no variables in literal template, got {v3}'

# Test 4: Nested conditionals
t4 = '{% if a %}{% if b %}{{ c }}{% endif %}{% endif %}'
v4 = _get_template_variables(t4)
assert 'a' in v4 and 'b' in v4 and 'c' in v4, f'Missing vars in {v4}'

print('PASS')
" 2>&1) || true
if echo "$RESULT" | grep -q "PASS"; then
    # [pr_diff] (0.30): _get_template_variables extracts variables from Jinja2 templates
    log "pr_diff" "_get_template_variables extracts variables correctly" "0.30" "PASS"
    add 0.30 1
else
    log "pr_diff" "_get_template_variables extracts variables correctly" "0.30" "FAIL: $RESULT"
    add 0.30 0
fi

# ============================================================
# [pr_diff] (0.20): F2P — kwargs separation logic works
# Fails on base: function doesn't exist (ImportError)
# ============================================================
echo ""
echo "=== F2P: Template introspection separates template vs processor kwargs ==="
RESULT=$(cd "$REPO" && python3 -c "
from transformers.utils.chat_template_utils import _get_template_variables

# Realistic chat template
t = '''{% for msg in messages %}{{ msg['role'] }}: {{ msg['content'] }}
{% endfor %}{% if add_generation_prompt %}assistant: {% endif %}'''
variables = _get_template_variables(t)

# Template vars correctly identified
assert 'messages' in variables
assert 'add_generation_prompt' in variables

# Processor kwargs NOT in template variables
for k in ['padding', 'max_length', 'return_tensors', 'truncation']:
    assert k not in variables, f'{k} should not be a template variable'

# Simulate separation: items not in template vars are processor kwargs
all_kwargs = {
    'messages': [{'role': 'user', 'content': 'hi'}],
    'add_generation_prompt': True,
    'padding': 'max_length',
    'max_length': 50,
}
processor_kwargs = {k: v for k, v in all_kwargs.items() if k not in variables}
assert 'padding' in processor_kwargs
assert 'max_length' in processor_kwargs
assert 'messages' not in processor_kwargs
assert 'add_generation_prompt' not in processor_kwargs

# Custom var that IS in a different template should be correctly routed
t2 = '{% for msg in messages %}{{ msg.content }}{% endfor %}{% if custom_flag %}yes{% endif %}'
v2 = _get_template_variables(t2)
proc2 = {k: v for k, v in {'custom_flag': True, 'padding': 'max_length'}.items() if k not in v2}
assert 'custom_flag' not in proc2, 'custom_flag is a template var in t2'
assert 'padding' in proc2, 'padding is always a processor kwarg'

print('PASS')
" 2>&1) || true
if echo "$RESULT" | grep -q "PASS"; then
    # [pr_diff] (0.20): Template introspection correctly separates kwargs
    log "pr_diff" "kwargs separation via template introspection" "0.20" "PASS"
    add 0.20 1
else
    log "pr_diff" "kwargs separation via template introspection" "0.20" "FAIL: $RESULT"
    add 0.20 0
fi

# ============================================================
# [pr_diff] (0.15): F2P — apply_chat_template calls _get_template_variables
# Uses mock to verify actual integration (not just function existence)
# Fails on base: _get_template_variables not imported in processing_utils
# ============================================================
echo ""
echo "=== F2P: apply_chat_template integrates _get_template_variables ==="
RESULT=$(cd "$REPO" && python3 -c "
from unittest.mock import MagicMock, patch
import transformers.processing_utils as pu
from transformers.processing_utils import ProcessorMixin

# Verify _get_template_variables is imported in processing_utils
assert hasattr(pu, '_get_template_variables'), '_get_template_variables not available in processing_utils'

template = '{% for msg in messages %}{{ msg[\"content\"] }}{% endfor %}'
mock_self = MagicMock()
mock_self.chat_template = {'default': template}
mock_self.tokenizer.special_tokens_map = {}
mock_self.tokenizer.__class__.__name__ = 'TestTokenizer'

# Track whether _get_template_variables is called during apply_chat_template
original_fn = pu._get_template_variables
call_log = []
def tracking_wrapper(t):
    call_log.append(t)
    return original_fn(t)

with patch.object(pu, '_get_template_variables', side_effect=tracking_wrapper):
    try:
        result = ProcessorMixin.apply_chat_template(
            mock_self,
            [{'role': 'user', 'content': 'hello'}],
        )
    except Exception:
        pass  # May fail due to mock limitations; we only care about the call

assert len(call_log) > 0, 'apply_chat_template did NOT call _get_template_variables — function exists but is not wired up'
assert call_log[0] == template, f'Called with wrong template: {call_log[0]}'

print('PASS')
" 2>&1) || true
if echo "$RESULT" | grep -q "PASS"; then
    # [pr_diff] (0.15): apply_chat_template calls _get_template_variables for kwarg routing
    log "pr_diff" "apply_chat_template calls _get_template_variables" "0.15" "PASS"
    add 0.15 1
else
    log "pr_diff" "apply_chat_template calls _get_template_variables" "0.15" "FAIL: $RESULT"
    add 0.15 0
fi

# ============================================================
# [pr_diff] (0.10): F2P — _get_template_variables is cached
# Fails on base: function doesn't exist
# ============================================================
echo ""
echo "=== F2P: _get_template_variables is cached ==="
RESULT=$(cd "$REPO" && python3 -c "
from transformers.utils.chat_template_utils import _get_template_variables

# Cached functions (lru_cache / functools.cache) expose cache_info()
assert hasattr(_get_template_variables, 'cache_info'), 'No cache_info — function is not cached'

t = '{{ messages }}'
_get_template_variables(t)
_get_template_variables(t)
info = _get_template_variables.cache_info()
assert info.hits >= 1, f'Expected at least 1 cache hit, got {info.hits}'

print('PASS')
" 2>&1) || true
if echo "$RESULT" | grep -q "PASS"; then
    # [pr_diff] (0.10): _get_template_variables is cached for performance
    log "pr_diff" "_get_template_variables is cached" "0.10" "PASS"
    add 0.10 1
else
    log "pr_diff" "_get_template_variables is cached" "0.10" "FAIL: $RESULT"
    add 0.10 0
fi

# ============================================================
# [pr_diff] (0.10): P2P — render_jinja_template still works
# Should pass on both base and fixed code
# ============================================================
echo ""
echo "=== P2P: render_jinja_template still works ==="
RESULT=$(cd "$REPO" && python3 -c "
from transformers.utils.chat_template_utils import render_jinja_template

template = '{% for msg in messages %}{{ msg[\"role\"] }}: {{ msg[\"content\"] }}\n{% endfor %}'
conversations = [[{'role': 'user', 'content': 'Hello'}]]
prompt, indices = render_jinja_template(
    conversations=conversations,
    chat_template=template,
    add_generation_prompt=False,
)
assert 'user: Hello' in prompt[0], f'Unexpected prompt: {prompt}'

print('PASS')
" 2>&1) || true
if echo "$RESULT" | grep -q "PASS"; then
    # [pr_diff] (0.10): render_jinja_template backwards-compatible
    log "pr_diff" "render_jinja_template still works" "0.10" "PASS"
    add 0.10 1
else
    log "pr_diff" "render_jinja_template still works" "0.10" "FAIL: $RESULT"
    add 0.10 0
fi

# ============================================================
# [agent_config] (0.05): ruff lint — CLAUDE.md:2 @ 6a056a16
# "make style: runs formatters and linters (ruff)"
# ============================================================
echo ""
echo "=== Config: ruff lint check ==="
RUFF_PASS=1
for f in \
    src/transformers/processing_utils.py \
    src/transformers/utils/chat_template_utils.py \
    src/transformers/models/smolvlm/processing_smolvlm.py \
    src/transformers/models/voxtral/processing_voxtral.py; do
    if ! (cd "$REPO" && ruff check --select E,W "$f" 2>/dev/null); then
        RUFF_PASS=0
    fi
done
if [ "$RUFF_PASS" = "1" ]; then
    # [agent_config] (0.05): "make style: runs formatters and linters (ruff)" — CLAUDE.md:2 @ 6a056a16
    log "agent_config" "ruff lint passes on changed files" "0.05" "PASS"
    add 0.05 1
else
    log "agent_config" "ruff lint passes on changed files" "0.05" "FAIL"
    add 0.05 0
fi

# ============================================================
# [static] (0.10): Anti-stub — real implementation + AST wiring check
# ============================================================
echo ""
echo "=== Structural: Anti-stub checks ==="
RESULT=$(cd "$REPO" && python3 -c "
import ast, inspect
from transformers.utils.chat_template_utils import _get_template_variables

# Unwrap cache decorator to inspect real function body
fn = _get_template_variables
while hasattr(fn, '__wrapped__'):
    fn = fn.__wrapped__

source = inspect.getsource(fn)
tree = ast.parse(source)
func = tree.body[0]
body = func.body

# Skip docstring if present
if isinstance(body[0], ast.Expr) and isinstance(getattr(body[0].value, 'value', None), str):
    body = body[1:]
assert len(body) >= 2, f'Only {len(body)} statements — likely a stub'

# Verify processing_utils.py calls _get_template_variables inside apply_chat_template
with open('src/transformers/processing_utils.py') as f:
    pu_source = f.read()
pu_tree = ast.parse(pu_source)

found_call = False
for node in ast.walk(pu_tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'apply_chat_template':
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                callee = child.func
                if isinstance(callee, ast.Name) and callee.id == '_get_template_variables':
                    found_call = True
                elif isinstance(callee, ast.Attribute) and callee.attr == '_get_template_variables':
                    found_call = True
assert found_call, 'apply_chat_template body does not call _get_template_variables (AST check)'

print('PASS')
" 2>&1) || true
if echo "$RESULT" | grep -q "PASS"; then
    # [static] (0.10): Anti-stub — real implementation wired into apply_chat_template
    log "static" "Anti-stub: real implementation + AST wiring" "0.10" "PASS"
    add 0.10 1
else
    log "static" "Anti-stub: real implementation + AST wiring" "0.10" "FAIL: $RESULT"
    add 0.10 0
fi

# ============================================================
# Final score
# ============================================================
echo ""
echo "=== Final Score: $TOTAL ==="

mkdir -p /logs/verifier
echo "$TOTAL" > /logs/verifier/reward.txt

python3 -c "
import json
s = float('$TOTAL')
data = {
    'reward': s,
    'behavioral': min(s, 0.85),
    'regression': min(max(s - 0.85, 0), 0.10),
    'config': min(max(s - 0.95, 0), 0.05),
    'structural': min(max(s - 0.90, 0), 0.10),
}
print(json.dumps(data, indent=2))
with open('/logs/verifier/reward.json', 'w') as f:
    json.dump(data, f, indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
