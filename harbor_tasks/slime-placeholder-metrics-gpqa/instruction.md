# Placeholder worker crashes, missing metrics router, and GPQA letter range too narrow

Three related issues in the slime RL training framework:

## 1. GPQA reward function rejects valid answer letters (I, J)

In `slime/rollout/rm_hub/gpqa.py`, the default set of valid answer letters only covers A through H (8 options). Some GPQA evaluation datasets have questions with up to 10 answer choices. When a question's correct answer is the 9th or 10th option and the label is provided as an integer index (e.g., `8` or `9`), `compute_gpqa_reward` silently returns `0.0` even when the model's response is correct, because the index falls outside the valid letter list bounds.

## 2. `nodes_per_engine` crashes when placeholder server groups exist

In `slime/ray/rollout.py`, the `RolloutServer.nodes_per_engine` property computes a set of `nodes_per_engine` values across all server groups and raises `ValueError` if they're not homogeneous. However, placeholder server groups (which reserve GPU slots without launching engines) may have a different `nodes_per_engine` value than active groups. The property doesn't account for this, causing spurious crashes when placeholder groups are present.

Additionally, the `WorkerType` enum in `slime/router/router.py` is missing a variant for placeholder workers, even though the server group dataclass already supports `worker_type="placeholder"`.

## 3. W&B metrics tracking initialized before servers are available

In the `RolloutManager.__init__` method in `slime/ray/rollout.py`, the W&B tracking initialization (`init_tracking`) is called before rollout servers are launched. This means the SGLang router address is not yet available, so Prometheus metrics from the engine cannot be scraped and forwarded to W&B. The initialization should happen after servers are up so the router address can be passed in for metrics scraping.
