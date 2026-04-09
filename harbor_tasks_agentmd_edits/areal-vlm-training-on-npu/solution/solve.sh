#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotent: skip if already applied
if [ -f examples/vlm_npu/geometry3k_grpo.py ]; then
    echo "Patch already applied."
    exit 0
fi

mkdir -p examples/vlm_npu

cat > examples/vlm_npu/README.md << 'READMEEOF'
# Training VLMs with GRPO on NPU:
In this instruction, we will introduce how to train VLMs with GRPO on NPU.

### Hardware

The following hardware configuration has been extensively tested:

- **NPU**: 16x NPU per node
- **CPU**: 64 cores per node
- **Memory**: 1TB per node
- **Network**: RoCE 3.2 Tbps
- **Storage**:
  - 1TB local storage for single-node experiments
  - 10TB shared storage (NAS) for distributed experiments

### Key Contributions
-	Trained Qwen2.5VL-3B-instruct model upto 70 epochs with (4 cards+ 4 cards) train-infer configuration. Took around 19hr to finish full training.
- Trained model is tested with more than one benchmark using VLMEvalKit.


### System configuration:
-	Vllm==0.11.0 ; vllm-ascend==0.11.0rc0 ;
-	Torch==0.7.1+cpu ; torch_npu==2.7.1.dev20250724
-	Areal==0.4.1
-	CANN==8.1RC1 ; 910c npus (65 gigs X 16)

### Results:
We trained Qwen2.5-VL-3B for 70 epochs on Geometry3K and evaluated the checkpoints using VLMEvalKit on out of distribution tasks such as MathVision, MathVista, and LogicVista. The training was performed on both NPU and GPU and results are as follows:

| Method     | LogicVista | MathVision_mini | MathVista_mini | Avg.  |
|------------|------------|------------------|----------------|-------|
| Base Model | 31.0       | 18.3             | 52.3           | 33.8     |
| GRPO-GPU   | 35.4       | 20.9             | 55.9           | **37.4** |
| GRPO-NPU   | 35.3       | 20.5             | 54.7           | **36.8** |
READMEEOF

cat > examples/vlm_npu/geometry3k_grpo.py << 'PYEOF'
import os
import re
import sys

from mathruler.grader import extract_boxed_content, grade_answer

from areal.api.cli_args import GRPOConfig, load_expr_config
from areal.dataset import get_custom_dataset
from areal.experimental.trainer import PPOTrainer
from areal.utils.hf_utils import load_hf_processor_and_tokenizer
from areal.utils.stats_logger import StatsLogger
from areal.workflow.vision_rlvr import VisionRLVRWorkflow


def format_reward(predict_str: str) -> float:
    pattern = re.compile(r"<think>.*</think>.*\\boxed\{.*\}.*", re.DOTALL)
    match_result = re.fullmatch(pattern, predict_str)
    return 1.0 if match_result else 0.0


def acc_reward(predict_str: str, ground_truth: str) -> float:
    answer = extract_boxed_content(predict_str)
    return 1.0 if grade_answer(answer, ground_truth) else 0.0


def geometry3k_reward_fn(
    prompt, completions, prompt_ids, completion_ids, answer, **kwargs
):
    format_reward_val = format_reward(completions)
    acc_reward_val = acc_reward(completions, answer)
    format_score = 0.1
    score = (1.0 - format_score) * (acc_reward_val) + format_score * format_reward_val
    return score


def main(args):
    config, _ = load_expr_config(args, GRPOConfig)
    processor, tokenizer = load_hf_processor_and_tokenizer(config.tokenizer_path)

    train_dataset = get_custom_dataset(
        split="train",
        dataset_config=config.train_dataset,
        tokenizer=tokenizer,
        processor=processor,
    )

    valid_dataset = get_custom_dataset(
        split="test",
        dataset_config=config.valid_dataset,
        tokenizer=tokenizer,
        processor=processor,
    )

    with PPOTrainer(
        config,
        train_dataset=train_dataset,
        valid_dataset=valid_dataset,
    ) as trainer:
        workflow = VisionRLVRWorkflow(
            reward_fn=geometry3k_reward_fn,
            gconfig=config.gconfig,
            tokenizer=trainer.tokenizer,
            processor=trainer.processor,
            enable_thinking=False,
            dump_dir=os.path.join(
                StatsLogger.get_log_path(config.stats_logger), "generated"
            ),
        )
        eval_workflow = VisionRLVRWorkflow(
            reward_fn=geometry3k_reward_fn,
            gconfig=config.gconfig.new(temperature=0.6),
            tokenizer=trainer.tokenizer,
            processor=trainer.processor,
            enable_thinking=False,
            rollout_stat_scope="eval-rollout",
            dump_dir=os.path.join(
                StatsLogger.get_log_path(config.stats_logger), "generated-eval"
            ),
        )
        trainer.train(workflow, eval_workflow)


if __name__ == "__main__":
    main(sys.argv[1:])
PYEOF

cat > examples/vlm_npu/geometry3k_grpo.sh << 'SHEOF'
export USE_OPTIMIZED_MODEL=0
# Some models are optimized by vllm ascend. While in some case, e.g. rlhf training,
# the optimized model may not be suitable. In this case, set this value to 0 to disable the optimized model.

python -m areal.launcher.local \
    examples/vlm_npu/geometry3k_grpo.py --config examples/vlm_npu/geometry3k_grpo.yaml
SHEOF

cat > examples/vlm_npu/geometry3k_grpo.yaml << 'YAMLEOF'
experiment_name: geometry3k-grpo
trial_name: trial1

seed: 1
enable_offload: false
total_train_epochs: 3
tokenizer_path: ${actor.path}

cluster:
  n_nodes: 1
  n_gpus_per_node: 8
  fileroot: /tmp/areal/experiments
  name_resolve:
    type: nfs
    nfs_record_root: /tmp/areal/name_resolve

allocation_mode: vllm:d4p1t1+d4p1t1

rollout:
  experiment_name: ${experiment_name}
  trial_name: ${trial_name}
  max_concurrent_rollouts: 256
  queue_size: null
  consumer_batch_size: ${train_dataset.batch_size}
  max_head_offpolicyness: 4
  enable_rollout_tracing: false

gconfig:
  n_samples: 4
  min_new_tokens: 0
  max_new_tokens: 512
  greedy: false
  temperature: 1.0

actor:
  experiment_name: ${experiment_name}
  trial_name: ${trial_name}
  path: Qwen/Qwen2.5-VL-3B-Instruct
  init_from_scratch: false
  disable_dropout: true
  gradient_checkpointing: true
  dtype: bfloat16
  mb_spec:
    max_tokens_per_mb: 4096
  optimizer:
    type: adam
    lr: 2e-6
    weight_decay: 0.01
    beta1: 0.9
    beta2: 0.999
    eps: 1e-8
    lr_scheduler_type: constant
    gradient_clipping: 1.0
    warmup_steps_proportion: 0.001
  group_size: ${gconfig.n_samples}
  eps_clip: 0.4
  temperature: ${gconfig.temperature}
  reward_scaling: 10.0
  reward_bias: -0.5
  kl_ctl: 0.0
  ppo_n_minibatches: 1
  recompute_logprob: true
  use_decoupled_loss: true
  behav_imp_weight_cap: 5.0
  dynamic_sampling: false
  reward_norm:
    mean_level: group
    std_level: group
    group_size: ${gconfig.n_samples}
  adv_norm:
    mean_level: batch
    std_level: batch
  max_new_tokens: ${gconfig.max_new_tokens}

ref:
  experiment_name: ${experiment_name}
  trial_name: ${trial_name}
  path: ${actor.path}
  init_from_scratch: false
  disable_dropout: true
  dtype: ${actor.dtype}
  mb_spec:
    max_tokens_per_mb: 4096
  optimizer: null

# SGLang
sglang:
  model_path: ${actor.path}
  random_seed: ${seed}
  skip_tokenizer_init: true
  dtype: ${actor.dtype}
  max_running_requests: 64
  context_length: 32768
  mem_fraction_static: 0.8
  enable_multimodal: true

vllm:
  model: ${actor.path}
  seed: ${seed}
  skip_tokenizer_init: false
  dtype: ${actor.dtype}
  max_model_len: 32768
  gpu_memory_utilization: 0.9
  disable_sliding_window: false


# datasets
train_dataset:
  batch_size: 32
  pin_memory: true
  num_workers: 4
  path: hiyouga/geometry3k
  type: rl

valid_dataset:
  batch_size: 32
  pin_memory: true
  num_workers: 4
  path: hiyouga/geometry3k
  type: rl

# Utilities
saver:
  experiment_name: ${experiment_name}
  trial_name: ${trial_name}
  fileroot: ${cluster.fileroot}
  freq_epochs: 1
  freq_steps: null
  freq_secs: null

recover:
  mode: disabled
  experiment_name: ${experiment_name}
  trial_name: ${trial_name}
  fileroot: ${cluster.fileroot}
  freq_epochs: 1
  freq_steps: null
  freq_secs: 3600

evaluator:
  experiment_name: ${experiment_name}
  trial_name: ${trial_name}
  fileroot: ${cluster.fileroot}
  freq_epochs: 1
  freq_steps: null
  freq_secs: null

stats_logger:
  experiment_name: ${experiment_name}
  trial_name: ${trial_name}
  fileroot: ${cluster.fileroot}
  wandb:
    mode: disabled

launcher:
  inference_server_cpus_per_gpu: 4
  inference_server_mem_per_gpu: 32768
  trainer_cpus_per_gpu: 4
  trainer_mem_per_gpu: 32768
YAMLEOF

echo "Patch applied successfully."
