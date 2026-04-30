#!/bin/bash
set -euo pipefail

cd /workspace/areal

git apply -v <<'PATCH'
diff --git a/.claude/rules/code-style.md b/.claude/rules/code-style.md
index 70d733f0e5..a7e21cadd1 100644
--- a/.claude/rules/code-style.md
+++ b/.claude/rules/code-style.md
@@ -18,11 +18,26 @@ Rules beyond pre-commit (ruff format/lint).
   - Good: `getLogger("RLVRWorkflow")`, `getLogger("ArchonEngine")`,
     `getLogger("GSM8KReward")`
   - Avoid: `getLogger(__name__)` or dotted paths like `getLogger("areal.engine.fsdp")`
+- For per-rank loggers: `[{Component} Rank {N}]` (e.g., `[FSDPEngine Rank 0]`)
 - Log levels:
   - DEBUG: Detailed tracing (avoid in hot paths)
   - INFO: Milestones (training start, checkpoint saved)
   - WARNING: Recoverable issues
   - ERROR: Failures requiring attention
+- Register new loggers in `areal/utils/logging.py` (`LOGGER_COLORS_EXACT` or
+  `LOGGER_PATTERNS`)
+- Test colors: `python -m areal.utils.logging`
+
+**Color Scheme:**
+
+| Color      | Category                               | Examples                           |
+| ---------- | -------------------------------------- | ---------------------------------- |
+| blue       | Infrastructure (Schedulers, Launchers) | `LocalScheduler`, `RayLauncher`    |
+| white      | Orchestration (Controllers, RPC)       | `TrainController`, `SGLangWrapper` |
+| purple     | RL-specific (Workflows, Rewards)       | `RLVRWorkflow`, `GSM8KReward`      |
+| green      | Data/Metrics (Stats, Dataset)          | `StatsLogger`, `RLTrainer`         |
+| cyan       | Compute backends (Engines, Platforms)  | `FSDPEngine`, `CUDAPlatform`       |
+| yellow/red | Warning/Error levels (override)        | Any logger at WARNING+             |

 ## Performance Patterns

diff --git a/.dockerignore b/.dockerignore
index d8ac92183c..603ec565fc 100644
--- a/.dockerignore
+++ b/.dockerignore
@@ -5,7 +5,6 @@

 # Documentation (not needed in runtime image)
 docs/
-README.md
 CONTRIBUTING.md

 # Legacy codes
diff --git a/.github/workflows/build-docker-image.yml b/.github/workflows/build-docker-image.yml
index 87bbb0d495..d0580544cc 100644
--- a/.github/workflows/build-docker-image.yml
+++ b/.github/workflows/build-docker-image.yml
@@ -1,9 +1,6 @@
 name: Build and Test Docker Image

 on:
-  pull_request:
-    branches: [main]
-    types: [labeled]
   workflow_dispatch:

 concurrency:
@@ -13,23 +10,16 @@ concurrency:
 permissions:
   contents: read
   packages: write
-  pull-requests: write

 env:
   GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
   VALIDATOR_LABELS: gcp-docker-validator
   RUNNER_VERSION: '2.317.0'
   IMAGE_NAME: ghcr.io/inclusionai/areal-runtime
-  IMAGE_TAG: dev
+  IMAGE_TAG: test

 jobs:
   start-builder:
-    if: |
-      (github.event_name == 'pull_request' &&
-       github.head_ref == 'build-docker-image' &&
-       contains(github.event.pull_request.labels.*.name, 'new-image')) ||
-      (github.event_name == 'workflow_dispatch' &&
-       github.ref_name == 'build-docker-image')
     name: Start areal-docker-builder instance
     runs-on: ubuntu-latest
     outputs:
@@ -122,12 +112,6 @@ jobs:
             throw new Error(`Timed out waiting for builder runner ${instanceName} to come online.`);

   build-and-push-image:
-    if: |
-      (github.event_name == 'pull_request' &&
-       github.head_ref == 'build-docker-image' &&
-       contains(github.event.pull_request.labels.*.name, 'new-image')) ||
-      (github.event_name == 'workflow_dispatch' &&
-       github.ref_name == 'build-docker-image')
     needs:
       - start-builder
     name: Build and push Docker image
@@ -163,11 +147,71 @@ jobs:
           echo "Commit: ${{ github.sha }}"
           echo "Branch: ${{ github.head_ref || github.ref_name }}"

+  run-tests:
+    name: Run tests with test image
+    needs:
+      - build-and-push-image
+    uses: ./.github/workflows/test-areal.yml
+    with:
+      image_tag: test
+    secrets: inherit
+
+  promote-image:
+    name: Promote test image to dev
+    needs:
+      - run-tests
+    runs-on: ubuntu-latest
+    steps:
+      - name: Log in to GitHub Container Registry
+        uses: docker/login-action@v3
+        with:
+          registry: ghcr.io
+          username: inclusionai
+          password: ${{ secrets.GHCR_TOKEN }}
+
+      - name: Pull test image and push as dev
+        env:
+          IMAGE_NAME: ghcr.io/inclusionai/areal-runtime
+        run: |
+          docker pull $IMAGE_NAME:test
+          docker tag $IMAGE_NAME:test $IMAGE_NAME:dev
+          docker push $IMAGE_NAME:dev
+          echo "✅ Image promoted from :test to :dev"
+
+  cleanup-test-image:
+    name: Delete test image from registry
+    needs:
+      - build-and-push-image
+      - run-tests
+      - promote-image
+    if: always() && needs.build-and-push-image.result == 'success'
+    runs-on: ubuntu-latest
+    steps:
+      - name: Delete test image from GHCR
+        env:
+          GH_TOKEN: ${{ secrets.GHCR_TOKEN }}
+        run: |
+          # Get the package version ID for the test tag
+          PACKAGE_VERSION_ID=$(curl -s -H "Authorization: Bearer $GH_TOKEN" \
+            "https://api.github.com/orgs/inclusionai/packages/container/areal-runtime/versions" \
+            | jq -r '.[] | select(.metadata.container.tags[] == "test") | .id')
+
+          if [ -n "$PACKAGE_VERSION_ID" ] && [ "$PACKAGE_VERSION_ID" != "null" ]; then
+            curl -X DELETE -H "Authorization: Bearer $GH_TOKEN" \
+              "https://api.github.com/orgs/inclusionai/packages/container/areal-runtime/versions/$PACKAGE_VERSION_ID"
+            echo "✅ Deleted test image from registry"
+          else
+            echo "⚠️ Test image not found or already deleted"
+          fi
+
   stop-builder:
     name: Stop areal-docker-builder instance
     needs:
-      - build-and-push-image
       - start-builder
+      - build-and-push-image
+      - run-tests
+      - promote-image
+      - cleanup-test-image
     if: always() && needs.start-builder.outputs.was_running != 'true'
     runs-on: ubuntu-latest
     env:
diff --git a/.github/workflows/tag-release-image.yml b/.github/workflows/tag-release-image.yml
index f49536464a..97acc5cf36 100644
--- a/.github/workflows/tag-release-image.yml
+++ b/.github/workflows/tag-release-image.yml
@@ -159,6 +159,7 @@ jobs:
           tags: |
             ${{ env.IMAGE_NAME }}:${{ steps.get-version.outputs.release_tag }}
             ${{ env.IMAGE_NAME }}:latest
+            ${{ env.IMAGE_NAME }}:dev

       - name: Image details
         run: |
@@ -167,6 +168,7 @@ jobs:
           echo "Tags:"
           echo "  - ${{ steps.get-version.outputs.release_tag }}"
           echo "  - latest"
+          echo "  - dev"
           echo "Release: ${{ github.event.release.name || github.event.inputs.tag }}"
           echo "Commit: ${{ github.sha }}"

diff --git a/.github/workflows/test-areal.yml b/.github/workflows/test-areal.yml
index 7892765e1b..0a06142801 100644
--- a/.github/workflows/test-areal.yml
+++ b/.github/workflows/test-areal.yml
@@ -5,6 +5,13 @@ on:
     branches: [main]
     types: [labeled]
   workflow_dispatch:
+  workflow_call:
+    inputs:
+      image_tag:
+        description: 'Docker image tag to use for testing'
+        required: false
+        type: string
+        default: 'dev'

 concurrency:
   group: areal-unit-tests-${{ github.ref }}
@@ -15,11 +22,14 @@ env:
   RUNNER_LABELS: gcp-a2-highgpu-2g
   RUNNER_VERSION: '2.317.0'
   GCP_OS_IMAGE: areal-cicd-test-202602030
-  CONTAINER_IMAGE: ghcr.io/inclusionai/areal-runtime:dev
+  CONTAINER_IMAGE: ghcr.io/inclusionai/areal-runtime:${{ inputs.image_tag || 'dev' }}

 jobs:
   provision-runner:
-    if: contains(github.event.pull_request.labels.*.name, 'safe-to-test') || github.event_name == 'workflow_dispatch'
+    if: |
+      github.event_name == 'workflow_call' ||
+      contains(github.event.pull_request.labels.*.name, 'safe-to-test') ||
+      github.event_name == 'workflow_dispatch'
     name: Provision GCP runner with 2 A100 GPUs
     runs-on: ubuntu-latest
     outputs:
@@ -228,7 +238,10 @@ jobs:
             throw new Error(`Timed out waiting for runner ${instanceName} to come online.`);

   unit-tests:
-    if: contains(github.event.pull_request.labels.*.name, 'safe-to-test') || github.event_name == 'workflow_dispatch'
+    if: |
+      github.event_name == 'workflow_call' ||
+      contains(github.event.pull_request.labels.*.name, 'safe-to-test') ||
+      github.event_name == 'workflow_dispatch'
     needs:
       - provision-runner
     name: Run AReaL tests
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 4c4af0cff9..4740cf9070 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -85,6 +85,8 @@ helping with code reviews. This guide will help you get started.

 1. **Submit a Pull Request**

+We suggest applying our provided claude command `/create-pr` whenever possible.
+
 ## Ways to Contribute

 ### 🐛 Bug Reports
@@ -133,71 +135,11 @@ issue or open a draft PR to discuss with the core developers before making any c
 changes. Directly opening a PR that conflicts with our future [roadmap](ROADMAP.md) may
 waste your effort.

-When opening a PR:
-
-- Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md) and complete the checklist
-- Link to the related issue using `Fixes #123` or `Closes #456`
-- Describe what changed and why (you can use GitHub Copilot summarization)
-- Prefix "wip:" in the PR title or mark it as a draft if it's still work-in-progress
-- List the testing you performed
-- Let AI review first before requesting human reviewers
-
-### 📝 Logging Convention
-
-AReaL uses colored logging to help distinguish log messages from different components.
-When adding new loggers, please follow these conventions:
-
-**Logger Naming:**
-
-- Use **PascalCase** with no spaces or hyphens (e.g., `TrainController`, not
-  `train_controller` or `Train Controller`)
-- Use descriptive names that indicate the component type
-- Use category suffixes: `Scheduler`, `Launcher`, `Workflow`, `Controller`, `Engine`,
-  etc.
-- For per-rank loggers, use the format `[{Component} Rank {N}]` (e.g.,
-  `[FSDPEngine Rank 0]`)
-
-**Example:**
-
-```python
-import logging
-
-# Good - PascalCase, descriptive
-logger = logging.getLogger("TrainController")
-logger = logging.getLogger("RLVRWorkflow")
-logger = logging.getLogger("[FSDPEngine Rank 0]")
-
-# Bad - avoid these patterns
-logger = logging.getLogger(__name__)  # Not descriptive in logs
-logger = logging.getLogger("train controller")  # Has spaces
-logger = logging.getLogger("train_controller")  # Snake case
-```
-
-**Color Scheme by Category:**
-
-| Color           | Category                                    | Examples                                 |
-| --------------- | ------------------------------------------- | ---------------------------------------- |
-| blue            | Infrastructure (Schedulers, Launchers)      | `LocalScheduler`, `RayLauncher`          |
-| white           | Orchestration (Controllers, RPC, Inference) | `TrainController`, `SGLangWrapper`       |
-| light_purple    | RL-specific (Workflows, Rewards, OpenAI)    | `RLVRWorkflow`, `GSM8KReward`            |
-| light_green     | Data/Metrics (Stats, Dataset, Trainers)     | `StatsLogger`, `Dataset`, `RLTrainer`    |
-| light_cyan/cyan | Compute backends (Engines, Platforms)       | `FSDPEngine`, `CUDAPlatform`, `PPOActor` |
-| yellow/red      | Warning/Error levels (always override)      | Any logger at WARNING+ level             |
-
-When adding a new logger, register it in `areal/utils/logging.py` under
-`LOGGER_COLORS_EXACT` or `LOGGER_PATTERNS` to ensure consistent coloring.
-
-Test your logger colors with: `python -m areal.utils.logging`
-
 ## Tips for Using AI-Assisted Coding

-- [AGENTS.md](AGENTS.md) is a reference guide for AI coding agents working on AReaL.
-  Before letting AI make any changes, ensure it understands the codebase using
-  `AGENTS.md`.
-
-- You can use the plan mode of coding agents to generate a plan for refactoring or new
-  features. Submit it as a draft PR before making any actual code changes and discuss
-  with the core developers.
+See the full
+[AI-Assisted Development Guide](https://inclusionai.github.io/AReaL/reference/ai_assisted_dev.html)
+for detailed documentation.

 ## CI/CD

@@ -271,36 +213,49 @@ def test_some_multi_gpu_functionality():

 > **NOTE:** The image building CI workflow is experimental and subject to change.

-The image building CI runs on the `build-docker-image` branch. Only project members with
-write permissions can push to this branch and open a PR.
+The image building workflow can be triggered manually from any branch by users with
+write permissions to the repository.

 **Triggering the Workflow:**

-The workflow is triggered when:
+You can trigger the workflow from any branch using either method:
+
+1. **Via GitHub UI:**

-1. A PR from `build-docker-image` to `main` is opened **AND**
-1. The PR is tagged with `new-image`
+   - Go to **Actions** → **"Build and Test Docker Image"**
+   - Click **"Run workflow"** dropdown
+   - Select the branch you want to build from
+   - Click **"Run workflow"**
+
+1. **Via GitHub CLI:**
+
+   ```bash
+   # Build from main
+   gh workflow run build-docker-image.yml --ref main
+
+   # Build from a feature branch
+   gh workflow run build-docker-image.yml --ref feature/my-changes
+
+   # Build from current branch
+   gh workflow run build-docker-image.yml --ref $(git branch --show-current)
+   ```

-The workflow will wake up a pinned CPU GCP compute engine instance with 64 vCPUs and 512
-GB memory, run the build job with the code and Dockerfile from the current commit, and
-push the image as `ghcr.io/inclusionai/areal-runtime:dev`. Building the image from
-scratch takes approximately 1-2 hours.
+**Pipeline Stages:**

-**Testing with the New Image:**
+The workflow executes the following stages sequentially:

-After successfully building the image:
+1. **Build**: Builds the Docker image and pushes it with `:test` tag
+1. **Test**: Automatically runs the full test suite using the `:test` image
+1. **Promote**: If tests pass, promotes the image by retagging `:test` → `:dev`
+1. **Cleanup**: Always deletes the `:test` image from the registry (success or failure)

-1. Remove the `new-image` tag
-1. Add the `safe-to-test` tag to trigger CI tests using the same procedure described
-   above
+Building the image from scratch takes approximately 1-2 hours, plus additional time for
+running the test suite.

-Note that our test suite detects the branch name that triggers the workflow. When the
-branch name is `build-docker-image`, it will pull the dev image instead of the stable
-image for testing.
+**Normal PR Testing:**

-**Important:** If you add the `safe-to-test` tag without removing `new-image` first,
-both image building and testing workflows will run simultaneously, which is usually
-undesired.
+The PR-based test workflow (triggered by the `safe-to-test` label) remains unchanged and
+uses the `:dev` image. This allows testing PRs against the last known-good image.

 ______________________________________________________________________

diff --git a/ROADMAP.md b/ROADMAP.md
index d32a5df8c1..94bf632d4d 100644
--- a/ROADMAP.md
+++ b/ROADMAP.md
@@ -7,11 +7,11 @@ direction of the project.
 **Latest Release:** Check [releases](https://github.com/inclusionAI/AReaL/releases) for
 the most recent version.

-## 2025 Q4 Roadmap (due January 31, 2026)
+## 2026 Q1 Roadmap (due April 30, 2026)

-[GitHub Issue #542](https://github.com/inclusionAI/AReaL/issues/542).
+[GitHub Issue #907](https://github.com/inclusionAI/AReaL/issues/907).

-This roadmap tracks major planned enhancements through January 31, 2026. Items are
+This roadmap tracks major planned enhancements through April 30, 2026. Items are
 organized into two categories:

 - **On-going:** Features currently under active development by the core AReaL team
@@ -22,42 +22,101 @@ organized into two categories:

 **On-going**

-- [ ] Single-controller mode: https://github.com/inclusionAI/AReaL/issues/260
-- [ ] Detailed profiling for optimal performance across different scales
-- [ ] RL training with cross-node vLLM pipeline/context parallelism
+- [ ] ZBPP & ZBPP-V support for the Archon backend
+- [ ] FP8 training for Archon

 **Planned but not in progress**

+- [ ] Support for agentic training with large VLM MoE models (Archon backend)
+- [ ] Omni model RL support with FSDP/Archon backend
+- [ ] Decoupling agent service from the inference service
+- [ ] Online RL training with the proxy server
+- [ ] LoRA support for the Archon backend
+- [ ] Colocation mode with `awex` as the weight sync engine
 - [ ] Multi-LLM training (different agents with different parameters)
-- [ ] Data transfer optimization in single-controller mode
 - [ ] Auto-scaling inference engines in single-controller mode
 - [ ] Elastic weight update setup and acceleration
-- [ ] Low-precision RL training
+- [ ] RL training with cross-node vLLM pipeline/context parallelism

 ### Usability

+**On-going**
+
+- [ ] Flatten the import structure of areal modules
+
 **Planned but not in progress**

-- [ ] Wrap training scripts into trainers
-- [ ] Fully respect allocation mode in trainers/training scripts
+- [ ] Publishing PyPI packages
 - [ ] Support distributed training and debugging in Jupyter notebooks
-- [ ] Refactor FSDP/Megatron engine/controller APIs to finer granularity
-- [ ] Add CI pipeline to build Docker images upon release
 - [ ] Example of using a generative or critic-like reward model
+- [ ] Support directly constructing inference/training engines without config objects
+- [ ] Add router in rollout controller for simpler proxy server usage
+- [ ] Integrate `aenvironment` for environment handling

 ### Documentation

 **Planned but not in progress**

-- [ ] Tutorial on how to write efficient async rollout workflows
-- [ ] Benchmarking and profiling guide
-- [ ] Use case guides: offline inference, offline evaluation, multi-agent training
-- [ ] AReaL performance tuning guide
-  - [ ] Device allocation strategies for training and inference
-  - [ ] Parallelism strategy configuration for training and inference
+- [ ] Use case guides: multi-agent training
+- [ ] Guide for online proxy mode training

 ## Historical Roadmaps

+### 2025 Q4
+
+[GitHub Issue #542](https://github.com/inclusionAI/AReaL/issues/542).
+
+**Backends**
+
+Completed:
+
+- Single-controller mode
+- Detailed profiling for optimal performance across different scales
+- Low-precision RL training (Megatron FP8)
+- Data transfer optimization in single-controller mode
+- New PyTorch-native backend: Archon
+
+Carried over to Q1 2026:
+
+- Multi-LLM training (different agents with different parameters)
+- Auto-scaling inference engines in single-controller mode
+- Elastic weight update setup and acceleration
+- RL training with cross-node vLLM pipeline/context parallelism
+
+**Usability**
+
+Completed:
+
+- Add CI pipeline to build Docker images upon release
+- Wrap training scripts into trainers
+- Refactor FSDP/Megatron engine/controller APIs to finer granularity
+- Fully respect allocation mode in trainers/training scripts
+
+Carried over to Q1 2026:
+
+- Flatten the import structure of areal modules
+- Support distributed training and debugging in Jupyter notebooks
+- Example of using a generative or critic-like reward model
+
+Canceled:
+
+- Rename `RemoteSGLang/vLLMEngine` as `SGLang/vLLMEngine`
+
+**Documentation**
+
+Completed:
+
+- Tutorial on how to write efficient async rollout workflows
+- Benchmarking and profiling guide
+- Use case guides: offline inference, offline evaluation
+- AReaL performance tuning guide
+  - Device allocation strategies for training and inference
+  - Parallelism strategy configuration for training and inference
+
+Carried over to Q1 2026:
+
+- Use case guides: multi-agent training
+
 ### 2025 Q3

 [GitHub Issue #257](https://github.com/inclusionAI/AReaL/issues/257).
@@ -148,7 +207,7 @@ agentic AI systems** that is:

 ______________________________________________________________________

-**Last Updated:** 2025-11-06
+**Last Updated:** 2026-02-06

 **Questions about the roadmap?** Open a discussion in
 [GitHub Discussions](https://github.com/inclusionAI/AReaL/discussions) or ask in our
PATCH

# Idempotency check
grep -qF 'Register new loggers in' .claude/rules/code-style.md
