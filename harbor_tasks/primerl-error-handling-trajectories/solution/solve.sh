#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied
if grep -q 'has_error = state\["error"\] is not None' src/prime_rl/orchestrator/trajectories.py 2>/dev/null; then
    echo "Patch already applied."
    if ! git log --oneline -1 | grep -q "gold solution"; then
        git add -A
        git commit -m "Apply gold solution for error handling in trajectories" --no-verify || true
    fi
    exit 0
fi

# Create math_python config files
mkdir -p configs/math_python

cat > configs/math_python/README.md << 'MATHREADME'
# math-python

## Setup

CLone `verifiers`

```bash
cd ~ && curl -sSL https://raw.githubusercontent.com/PrimeIntellect-ai/verifiers/main/scripts/install.sh | bash && cd -
```

Install the environment as local packages

```bash
uv pip install -e ~/verifiers/environments/math_python
```

This will automatically install the environment, and a pinned verifiers commit (`71006c`) which includes necessary changes to the PythonEnv.

## Eval

Get a quick vibe-check of the model

```bash
vllm serve Qwen/Qwen3-4B-Instruct-2507 --enable-auto-tool-choice --tool-call-parser hermes --max-model-len 8192
```

```bash
uv run --no-sync vf-eval math-python -n 16 -r 1 -c -1 -v -m Qwen/Qwen3-4B-Instruct-2507 -b http://localhost:8000/v1 -a '{"dataset_name": "PrimeIntellect/Hendrycks-Math", "dataset_subset": "default"}' -t 512
```

## RL

Again, make sure to have installed the environment as local packages from verifiers

```bash
uv pip install -e ~/verifiers/environments/math_python
```

Then, run RL in debug mode (small batch size, limited turns, 2 GPUs, etc.)

```bash
uv run --no-sync rl @ configs/math_python/math_python.toml --log.level debug
```
MATHREADME

cat > configs/math_python/math_python.toml << 'MATHTOML'
max_steps = 300

[wandb]
project = "math-python-debug"
name = "math-python"

[model]
name = "Qwen/Qwen3-4B-Instruct-2507"

[orchestrator]
seq_len = 4096
batch_size = 512
rollouts_per_example = 16

[orchestrator.sampling]
max_tokens = 512

[[orchestrator.env]]
id = "math-python"

[trainer]

[inference]
api_server_count = 4

[inference.model]
enable_auto_tool_choice = true
tool_call_parser = "hermes"
max_model_len = 4096
MATHTOML

echo "Config files created."

# Update CHANGELOG.md
if ! grep -q "api_server_count=1" CHANGELOG.md; then
    sed -i '/Documenting changes which affect/a\n- Auto-set `api_server_count=1` on inference when LoRA is enabled, because vLLM does not support hotloading for multiple API servers (#1422, 2025-12-17)' CHANGELOG.md
fi

# Update pyproject.toml
sed -i 's/rev = "0dd0645"/rev = "ca75d04"/g' pyproject.toml

# Update uv.lock
sed -i 's/rev=0dd0645/rev=ca75d04/g' uv.lock
sed -i 's/0dd06450aed7f1a78a8eb7807b5b836575376c40/ca75d04002c8e8d4eb766720ecd19e91abc02f20/g' uv.lock

# Update trajectories.py - interleave_rollout
sed -i 's/def interleave_rollout(state: vf.State) -> list\[TrainingSample\]:/def interleave_rollout(state: vf.State) -> list[TrainingSample] | None:/' src/prime_rl/orchestrator/trajectories.py

# Add empty trajectory check and has_error to interleave_rollout
python3 << 'PYEOF'
import re

with open('src/prime_rl/orchestrator/trajectories.py', 'r') as f:
    content = f.read()

# Replace the beginning of interleave_rollout
old_code = '''    logger = get_logger()

    # Initialize the rollout with prompt and completion from first trajectory step
    trajectory = state["trajectory"]
    first_step = trajectory[0]'''

new_code = '''    logger = get_logger()

    trajectory = state["trajectory"]
    if len(trajectory) == 0:
        logger.warning(f"No trajectory steps for example {state['example_id']}. Skipping rollout.")
        return None

    has_error = state.get("error") is not None

    # Initialize the rollout with prompt and completion from first trajectory step
    first_step = trajectory[0]
    if has_error:
        completion_mask = [False] * len(first_step["tokens"]["completion_mask"])
    else:
        completion_mask = [bool(i) for i in first_step["tokens"]["completion_mask"]]'''

content = content.replace(old_code, new_code)

# Replace completion_mask line
content = content.replace(
    'completion_mask=[bool(i) for i in first_step["tokens"]["completion_mask"]],',
    'completion_mask=completion_mask,'
)

# Replace the mask extension in loop
old_extend = 'interleaved_rollout.completion_mask.extend([True] * len(completion_ids))'
new_extend = '''if has_error:
            interleaved_rollout.completion_mask.extend([False] * len(tokens["completion_mask"]))
        else:
            interleaved_rollout.completion_mask.extend([bool(i) for i in tokens["completion_mask"]])'''
content = content.replace(old_extend, new_extend)

with open('src/prime_rl/orchestrator/trajectories.py', 'w') as f:
    f.write(content)

print("Updated interleave_rollout")
PYEOF

# Update trajectories.py - branch_rollout  
python3 << 'PYEOF'
with open('src/prime_rl/orchestrator/trajectories.py', 'r') as f:
    content = f.read()

# Update return type
content = content.replace(
    'def branch_rollout(state: vf.State) -> list[TrainingSample]:',
    'def branch_rollout(state: vf.State) -> list[TrainingSample] | None:'
)

# Add empty trajectory check and has_error
old_code = '''def branch_rollout(state: vf.State) -> list[TrainingSample] | None:
    """Convert vf.State to *multiple* trainable rollouts using branching trajectories strategy."""
    rollouts = []'''

new_code = '''def branch_rollout(state: vf.State) -> list[TrainingSample] | None:
    """Convert vf.State to *multiple* trainable rollouts using branching trajectories strategy."""
    logger = get_logger()

    rollouts = []
    trajectory = state["trajectory"]
    if len(trajectory) == 0:
        logger.warning(f"No trajectory steps for example {state['example_id']}. Skipping rollout.")
        return None

    has_error = state.get("error") is not None'''

content = content.replace(old_code, new_code)

# Update loop code
old_loop = '''    for step in state["trajectory"]:
        assert "tokens" in step
        tokens = step["tokens"]
        rollout = TrainingSample(
            prompt_ids=deepcopy(tokens["prompt_ids"]),
            prompt_mask=[bool(i) for i in tokens["prompt_mask"]],
            completion_ids=deepcopy(tokens["completion_ids"]),
            completion_mask=[bool(i) for i in tokens["completion_mask"]],'''

new_loop = '''    for step in state["trajectory"]:
        assert "tokens" in step
        tokens = step["tokens"]
        if has_error:
            completion_mask = [False] * len(tokens["completion_mask"])
        else:
            completion_mask = [bool(i) for i in tokens["completion_mask"]]
        rollout = TrainingSample(
            prompt_ids=deepcopy(tokens["prompt_ids"]),
            prompt_mask=[bool(i) for i in tokens["prompt_mask"]],
            completion_ids=deepcopy(tokens["completion_ids"]),
            completion_mask=completion_mask,'''

content = content.replace(old_loop, new_loop)

with open('src/prime_rl/orchestrator/trajectories.py', 'w') as f:
    f.write(content)

print("Updated branch_rollout")
PYEOF

# Update orchestrator.py
python3 << 'PYEOF'
with open('src/prime_rl/orchestrator/orchestrator.py', 'r') as f:
    content = f.read()

# Remove get_is_truncated import
content = content.replace(
    'from prime_rl.utils.vf import generate_batch, get_completion_len, get_is_truncated, get_prompt_len, get_seq_len',
    'from prime_rl.utils.vf import generate_batch, get_completion_len, get_prompt_len, get_seq_len'
)

# Update train_example handling
content = content.replace(
    '''        for train_rollout, advantage in zip(train_rollouts, advantages):
            train_example = make_train_example(train_rollout)
            for te in train_example:
                te.advantage = advantage
            train_examples.extend(train_example)''',
    '''        for train_rollout, advantage in zip(train_rollouts, advantages):
            train_example = make_train_example(train_rollout)
            if train_example is not None:
                for te in train_example:
                    te.advantage = advantage
                train_examples.extend(train_example)'''
)

# Update results_df construction
content = content.replace(
    '''"is_truncated": [get_is_truncated(rollout) for rollout in train_rollouts],''',
    '''"is_truncated": [rollout["is_truncated"] for rollout in train_rollouts],
                "error": [
                    type(rollout["error"]).__name__ if rollout["error"] is not None else None
                    for rollout in train_rollouts
                ],'''
)

# Add error metrics
content = content.replace(
    '''"batch/effective_batch_size": effective_batch_size,
            # Env metrics''',
    '''"batch/effective_batch_size": effective_batch_size,
            # Error metrics
            "error/mean": (~results_df.error.isna()).mean(),
            **{
                f"error/{error}": error_rate
                for error, error_rate in results_df.error.dropna().value_counts(normalize=True).items()
            },
            # Env metrics'''
)

with open('src/prime_rl/orchestrator/orchestrator.py', 'w') as f:
    f.write(content)

print("Updated orchestrator.py")
PYEOF

# Update test fixtures
python3 << 'PYEOF'
with open('tests/unit/orchestrator/test_trajectories.py', 'r') as f:
    content = f.read()

# Add error=None to fixtures
content = content.replace(
    '''        extras={},
            )
        ],
    )''',
    '''        extras={},
            )
        ],
        error=None,
    )'''
)

# Add to third fixture
content = content.replace(
    '''metrics={"has_error": 0.0, "tool_calls": 1.0},
    )''',
    '''metrics={"has_error": 0.0, "tool_calls": 1.0},
        error=None,
    )'''
)

with open('tests/unit/orchestrator/test_trajectories.py', 'w') as f:
    f.write(content)

print("Updated test fixtures")
PYEOF

echo "All changes applied."

# Commit the changes so judge.py can detect them via git diff
git add -A
git commit -m "Apply gold solution for error handling in trajectories" --no-verify || true

