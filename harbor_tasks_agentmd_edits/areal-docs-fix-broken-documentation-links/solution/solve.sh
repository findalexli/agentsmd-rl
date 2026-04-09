#!/usr/bin/env bash
set -euo pipefail

cd /workspace/AReaL

# Idempotent: skip if already applied
if grep -q 'inclusionai.github.io/AReaL/en/tutorial/quickstart.html' README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.github/ISSUE_TEMPLATE/config.yml b/.github/ISSUE_TEMPLATE/config.yml
index c8404f746..333eba2a4 100644
--- a/.github/ISSUE_TEMPLATE/config.yml
+++ b/.github/ISSUE_TEMPLATE/config.yml
@@ -7,13 +7,13 @@ contact_links:
     url: https://inclusionai.github.io/AReaL/
     about: Check our comprehensive documentation for guides and tutorials
   - name: 🚀 Quickstart Guide
-    url: https://inclusionai.github.io/AReaL/tutorial/quickstart.html
+    url: https://inclusionai.github.io/AReaL/en/tutorial/quickstart.html
     about: New to AReaL? Start here for installation and basic usage
   - name: 🐛 Debugging Guide
-    url: https://inclusionai.github.io/AReaL/best_practices/debugging.html
+    url: https://inclusionai.github.io/AReaL/en/best_practices/debugging.html
     about: Tips for debugging common issues
   - name: 💾 Handling OOM Issues
-    url: https://inclusionai.github.io/AReaL/best_practices/handling_oom.html
+    url: https://inclusionai.github.io/AReaL/en/best_practices/handling_oom.html
     about: Solutions for out-of-memory errors
   - name: 💬 WeChat Community
     url: https://github.com/inclusionAI/AReaL/blob/main/assets/wechat_qrcode.png
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index bafec785f..b15a30a58 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -24,7 +24,7 @@ helping with code reviews. This guide will help you get started.
 1. **Install Development Dependencies:**

    Check our
-   [installation guide](https://inclusionai.github.io/AReaL/tutorial/installation.html)
+   [installation guide](https://inclusionai.github.io/AReaL/en/tutorial/installation.html)
    for detailed setup instructions.

 1. **Set Up Code Formatting:**
@@ -138,7 +138,7 @@ waste your effort.
 ## Tips for Using AI-Assisted Coding

 See the full
-[AI-Assisted Development Guide](https://inclusionai.github.io/AReaL/reference/ai_assisted_dev.html)
+[AI-Assisted Development Guide](https://inclusionai.github.io/AReaL/en/reference/ai_assisted_dev.html)
 for detailed documentation.

 ## CI/CD
diff --git a/README.md b/README.md
index c75b355e6..9e7f04b00 100644
--- a/README.md
+++ b/README.md
@@ -3,7 +3,7 @@
 </h1>

 <p align="center">
-| <a href="https://arxiv.org/pdf/2505.24298"><b>Paper</b></a> | <a href="https://inclusionai.github.io/AReaL/"><b>Documentation</b></a> | <a href="https://deepwiki.com/inclusionAI/AReaL"><b>Ask DeepWiki</b></a> | <a href="https://huggingface.co/collections/inclusionAI/"><b>🤗 Models & Data</b></a> |
+| <a href="https://arxiv.org/pdf/2505.24298"><b>Paper</b></a> | <a href="https://inclusionai.github.io/AReaL/"><b>Documentation</b></a> | <a href="https://inclusionai.github.io/AReaL/zh/"><b>中文文档</b></a> | <a href="https://deepwiki.com/inclusionAI/AReaL"><b>Ask DeepWiki</b></a> | <a href="https://huggingface.co/collections/inclusionAI/"><b>🤗 Models & Data</b></a> |
 <a href="./assets/wechat_qrcode.png" target="_blank"><img src="./assets/wechat_icon.png" width="20" style="vertical-align: middle;"> <b>WeChat (微信) Group</b></a> |
 </p>

@@ -22,7 +22,7 @@ as much as you'd enjoy real milk tea. Cheers!
 **AReaL Highlights**

 - ⚡ **Flexibility**: Seamless customization for
-  [agentic RL](https://inclusionai.github.io/AReaL/tutorial/agentic_rl.html) and
+  [agentic RL](https://inclusionai.github.io/AReaL/en/tutorial/agentic_rl.html) and
   [online RL training](./examples/openclaw/) by simply replacing the `base_url`.
 - 📈 **Scalability**: **Stable** fully asynchronous RL training with **industry-leading
   speed**.
@@ -57,7 +57,7 @@ and the [announcement on X](https://x.com/guohao_li/status/2009678513574408636).
 @HwVanICI, we are excited to officially announce stable support for AReaL training on
 **Ascend NPU devices**! The code is actively maintained and continuously updated in the
 [`ascend` branch](https://github.com/inclusionAI/AReaL/tree/ascend). Check out
-[our documentation](https://inclusionai.github.io/AReaL/tutorial/installation_npu.html)
+[our documentation](https://inclusionai.github.io/AReaL/en/tutorial/installation_npu.html)
 to get started, and feel free to report any issues!

 **\[2025/08/30\]** Introducing ASearcher, a state-of-the-art search agent built with
@@ -70,8 +70,8 @@ features an **algorithm-first** API design that prioritizes ease of use and algo
 development, while natively supporting **fully asynchronous agentic RL**. With 80% fewer
 lines of code, AReaL-lite maintains 90% of AReaL's performance and core functionality.
 Check out [our AReaL-lite design documentation](/areal/README.md) and
-[the quickstart guide](https://inclusionai.github.io/AReaL/tutorial/quickstart.html) to
-begin your journey with **AReaL-lite**!
+[the quickstart guide](https://inclusionai.github.io/AReaL/en/tutorial/quickstart.html)
+to begin your journey with **AReaL-lite**!

 **\[2025/06/03\] (v0.3, boba²)** We release **boba²** (double-boba) for fully
 asynchronous RL training, which achieves **2.77× speedup while delivering comparable or
@@ -119,7 +119,7 @@ python3 examples/math/gsm8k_rl.py --config examples/math/gsm8k_grpo.yaml \
 ```

 For comprehensive setup instructions, see
-[our quickstart guide](https://inclusionai.github.io/AReaL/tutorial/quickstart.html).
+[our quickstart guide](https://inclusionai.github.io/AReaL/en/tutorial/quickstart.html).

 ## 📚 Examples

@@ -212,45 +212,45 @@ Check the [AI Coding Assistant Guide](docs/reference/ai_assisted_dev.md) and

 ### Tutorial

-- [Installation](https://inclusionai.github.io/AReaL/tutorial/installation.html)
-- [Quickstart](https://inclusionai.github.io/AReaL/tutorial/quickstart.html)
-- [Agentic RL](https://inclusionai.github.io/AReaL/tutorial/agentic_rl.html)
-- [Evaluation](https://inclusionai.github.io/AReaL/tutorial/eval.html)
-- [Large MoE with Megatron](https://inclusionai.github.io/AReaL/tutorial/megatron.html)
-- [Large MoE with PyTorch Archon](https://inclusionai.github.io/AReaL/tutorial/archon.html)
+- [Installation](docs/en/tutorial/installation.md)
+- [Quickstart](docs/en/tutorial/quickstart.md)
+- [Agentic RL](docs/en/tutorial/agentic_rl.md)
+- [Evaluation](docs/en/tutorial/eval.md)
+- [Large MoE with Megatron](docs/en/tutorial/megatron.md)
+- [Large MoE with PyTorch Archon](docs/en/tutorial/archon.md)

 ### Code Walkthrough

-- [Running GRPO on GSM8K dataset](https://inclusionai.github.io/AReaL/tutorial/gsm8k_grpo.html)
+- [Running GRPO on GSM8K dataset](docs/en/tutorial/gsm8k_grpo.md)

 ### Best Practices

-- [Improving Algorithm Performance](https://inclusionai.github.io/AReaL/best_practices/algo_perf.html)
-- [Agent Workflow Best Practices](https://inclusionai.github.io/AReaL/best_practices/workflow.html)
-- [Debugging](https://inclusionai.github.io/AReaL/best_practices/debugging.html)
-- [Handling OOM Issues](https://inclusionai.github.io/AReaL/best_practices/handling_oom.html)
-- [Performance Profiling](https://inclusionai.github.io/AReaL/best_practices/perf_profiling.html)
+- [Improving Algorithm Performance](docs/en/best_practices/algo_perf.md)
+- [Agent Workflow Best Practices](docs/en/best_practices/workflow.md)
+- [Debugging](docs/en/best_practices/debugging.md)
+- [Handling OOM Issues](docs/en/best_practices/handling_oom.md)
+- [Performance Profiling](docs/en/best_practices/perf_profiling.md)

 ### Customization

-- [Customize Dataset](https://inclusionai.github.io/AReaL/customization/dataset.html)
-- [Customize Agentic/RVLR Rollout Workflows](https://inclusionai.github.io/AReaL/customization/agent.html)
+- [Customize Dataset](docs/en/customization/dataset.md)
+- [Customize Agentic/RVLR Rollout Workflows](docs/en/customization/agent.md)

 ### Algorithms

-- [Asynchronous RL Explained](https://inclusionai.github.io/AReaL/algorithms/async.html)
-- [PPO, GRPO, and Related Algorithms](https://inclusionai.github.io/AReaL/algorithms/grpo_series.html)
-- [M2PO](https://inclusionai.github.io/AReaL/algorithms/m2po.html)
+- [Asynchronous RL Explained](docs/en/algorithms/async.md)
+- [PPO, GRPO, and Related Algorithms](docs/en/algorithms/grpo_series.md)
+- [M2PO](docs/en/algorithms/m2po.md)

 ### Reference

-- [CLI Configurations](https://inclusionai.github.io/AReaL/cli_reference.html)
-- [Checkpointing](https://inclusionai.github.io/AReaL/reference/checkpointing.html)
-- [Metrics Tracking](https://inclusionai.github.io/AReaL/reference/metrics_tracking.html)
-- [Allocation Mode](https://inclusionai.github.io/AReaL/reference/alloc_mode.html)
-- [Rollout Workflow](https://inclusionai.github.io/AReaL/reference/rollout_workflow.html)
-- [Agent Workflow](https://inclusionai.github.io/AReaL/reference/agent_workflow.html)
-- [AI-Assisted Development](https://inclusionai.github.io/AReaL/reference/ai_assisted_dev.html)
+- [CLI Configurations](docs/en/cli_reference.md)
+- [Checkpointing](docs/en/reference/checkpointing.md)
+- [Metrics Tracking](docs/en/reference/metrics_tracking.md)
+- [Allocation Mode](docs/en/reference/alloc_mode.md)
+- [Rollout Workflow](docs/en/reference/rollout_workflow.md)
+- [Agent Workflow](docs/en/reference/agent_workflow.md)
+- [AI-Assisted Development](docs/en/reference/ai_assisted_dev.md)

 ## 🤝 Contributing

diff --git a/areal/api/alloc_mode.py b/areal/api/alloc_mode.py
index 1598e9628..91602092b 100644
--- a/areal/api/alloc_mode.py
+++ b/areal/api/alloc_mode.py
@@ -1163,7 +1163,7 @@ def parse(self, expression: str):
             err_hint = """
 Hints:
 1. The parsing logic requires colons instead of dots to separate backends from dimensions, e.g., use "sglang:d4+fsdp:d4" instead of "sglang.d4+fsdp.d4".
-2. Check https://inclusionai.github.io/AReaL/tutorial/megatron.html for allowed syntax and examples with complex MoE models.
+2. Check https://inclusionai.github.io/AReaL/en/tutorial/megatron.html for allowed syntax and examples with complex MoE models.
 """
             raise ValueError(f"Parsing error: {e}\n{err_hint}")

diff --git a/blog/AReaL_v0_3.md b/blog/AReaL_v0_3.md
index e246a4c87..b989a2f56 100644
--- a/blog/AReaL_v0_3.md
+++ b/blog/AReaL_v0_3.md
@@ -291,6 +291,7 @@ either entirely correct or entirely incorrect.
     [14B-code](https://huggingface.co/inclusionAI/AReaL-boba-2-14B),
     [8B-code-open](https://huggingface.co/inclusionAI/AReaL-boba-2-8B-subset),
     [14B-code-open](https://huggingface.co/inclusionAI/AReaL-boba-2-14B-subset)
-  - [Evaluation Guide](https://inclusionai.github.io/AReaL/tutorial/eval.html)
+  - [Evaluation Guide](https://inclusionai.github.io/AReaL/en/tutorial/eval.html)
   - [Training configs](https://github.com/inclusionAI/AReaL/tree/main/examples/configs/v0.3-qwen3-code)
-    and [instructions](https://inclusionai.github.io/AReaL/references/reproduce.html)
+    and instructions (`reference/reproduce.html`, revert to a version before v0.5.1 to
+    see the reproduction guide)
diff --git a/docs/en/version_history.md b/docs/en/version_history.md
index 23846d76c..580a5dc36 100644
--- a/docs/en/version_history.md
+++ b/docs/en/version_history.md
@@ -6,7 +6,7 @@ development history, highlighting the key contributions of each version release.
 ## AReaL-lite (July 2025): Simplifying RL for Everyone

 *📖
-[Step-by-step Tutorial](https://inclusionai.github.io/AReaL/tutorial/gsm8k_grpo.html)*
+[Step-by-step Tutorial](https://inclusionai.github.io/AReaL/en/tutorial/gsm8k_grpo.html)*

 AReaL-lite represents a fundamental rethinking of how researchers interact with
 reinforcement learning systems. Born from the recognition that AReaL's system-first
diff --git a/docs/zh/version_history.md b/docs/zh/version_history.md
index affff147a..8d8b8529e 100644
--- a/docs/zh/version_history.md
+++ b/docs/zh/version_history.md
@@ -4,7 +4,7 @@

 ## AReaL-lite（2025年7月）：让 RL 触手可及

-*📖 [分步教程](https://inclusionai.github.io/AReaL/tutorial/gsm8k_grpo.html)*
+*📖 [分步教程](https://inclusionai.github.io/AReaL/zh/tutorial/gsm8k_grpo.html)*

 AReaL-lite 代表了对研究人员与强化学习系统交互方式的根本性重新思考。源于认识到 AReaL 的系统优先架构为 AI
 研究人员设置了障碍，这个轻量级版本将算法开发置于基础设施复杂性之上。
diff --git a/examples/countdown/README.md b/examples/countdown/README.md
index a8a4e095d..ef39757af 100644
--- a/examples/countdown/README.md
+++ b/examples/countdown/README.md
@@ -24,7 +24,7 @@ for this puzzle.
 Before you begin, ensure you have met the following requirements:

 - You have installed **AReaL**. Please follow the official
-  [AReaL installation guide](https://inclusionai.github.io/AReaL/tutorial/installation.html).
+  [AReaL installation guide](https://inclusionai.github.io/AReaL/en/tutorial/installation.html).
 - You have access to the `Qwen/Qwen2.5-3B-Instruct` model on the Hugging Face Hub (or
   have it downloaded locally).

diff --git a/examples/tau2/README.md b/examples/tau2/README.md
index 5d1092763..f7b68277e 100644
--- a/examples/tau2/README.md
+++ b/examples/tau2/README.md
@@ -25,7 +25,7 @@ with user's request by both using agent tools and guiding users using their tool
 ### Prerequisites

 Please make sure AReaL is setup and working following the
-[installation guide](https://inclusionai.github.io/AReaL/tutorial/installation.html).
+[installation guide](https://inclusionai.github.io/AReaL/en/tutorial/installation.html).

 1. Install the (forked) tau2-bench package:

diff --git a/pyproject.toml b/pyproject.toml
index 223625cdc..d03999685 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -166,7 +166,7 @@ all = [
 [project.urls]
 "Homepage" = "https://github.com/inclusionAI/AReaL"
 "Repository" = "https://github.com/inclusionAI/AReaL"
-"Documentation" = "https://inclusionai.github.io/AReaL/intro.html"
+"Documentation" = "https://inclusionai.github.io/AReaL/en/intro.html"
 "Bug Tracker" = "https://github.com/inclusionAI/AReaL/issues"

 [dependency-groups]

PATCH

echo "Patch applied successfully."
