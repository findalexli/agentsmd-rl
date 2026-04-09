# Support running multiple experiments per node

## Problem

The current codebase only supports running a single RL experiment per node. The `tmux.sh` script hardcodes the session name as "rl", log files go to a flat `logs/` directory, and the code assumes GPUs are always numbered 0, 1, 2, etc. This makes it impossible to run multiple experiments in parallel on a single node (e.g., splitting 4 GPUs to run two 2-GPU experiments side by side).

## Requirements

You need to implement first-class support for parallelizing experiments within a node. When an experiment identifier (`--exp-id`) is specified:

1. **Separate connection points** - Each experiment needs unique:
   - Inference server port and orchestrator client port
   - Orchestrator rollout path and trainer data path  
   - Trainer weights path and orchestrator weight path
   - Log file directories
   - Torch rendezvous endpoint

2. **GPU visibility** - Respect `CUDA_VISIBLE_DEVICES` when selecting GPUs instead of assuming devices are numbered 0..N.

3. **Port allocation** - Automatically find and use a free port for torch rendezvous.

4. **Documentation** - Update `README.md` to document:
   - The new `--exp-id` flag and its purpose
   - How to run multiple experiments per node with examples
   - How to pass experiment names to `tmux.sh`
   - A new "Multiple Experiments per Node" section

## Files to Look At

- `src/prime_rl/rl.py` - Main RL entrypoint, needs `exp_id` field and auto-setup logic
- `src/prime_rl/orchestrator/config.py` - ClientConfig needs host/port split instead of base_url
- `src/prime_rl/orchestrator/client.py` - Must construct base_url from host:port
- `src/prime_rl/orchestrator/orchestrator.py` - Update logging to use host:port
- `src/prime_rl/eval/eval.py` - Update logging to use host:port
- `src/prime_rl/utils/utils.py` - Add `get_free_port()` and `get_cuda_visible_devices()` helpers
- `tmux.sh` - Support experiment name argument, use `$EXPERIMENT_NAME` in log paths
- `README.md` - Document the new parallel experiment feature

## Expected Behavior

After implementing:

```bash
# First experiment (uses GPUs 0,1)
./tmux.sh exp-1
uv run rl \
  --trainer @ configs/trainer/reverse_text.toml \
  --orchestrator @ configs/orchestrator/reverse_text.toml \
  --inference @ configs/inference/reverse_text.toml \
  --exp-id exp-1

# Second experiment (uses GPUs 2,3)  
./tmux.sh exp-2
CUDA_VISIBLE_DEVICES=2,3 uv run rl \
  --trainer @ configs/trainer/reverse_text.toml \
  --orchestrator @ configs/orchestrator/reverse_text.toml \
  --inference @ configs/inference/reverse_text.toml \
  --inference.server.port 8001 \
  --orchestrator.client.port 8001 \
  --exp-id exp-2
```

Log files should be written to `logs/exp-1/` and `logs/exp-2/` respectively.
