# Agent Config Files for vllm-renderer-workers-mm-cache

Repo: vllm-project/vllm
Commit: 2bf5b70ae86261431b4b92276828b40b9c0903b6
Files found: 3


---
## AGENTS.md

```
   1 | # Agent Instructions for vLLM
   2 | 
   3 | > These instructions apply to **all** AI-assisted contributions to `vllm-project/vllm`.
   4 | > Breaching these guidelines can result in automatic banning.
   5 | 
   6 | ## 1. Contribution Policy (Mandatory)
   7 | 
   8 | ### Duplicate-work checks
   9 | 
  10 | Before proposing a PR, run these checks:
  11 | 
  12 | ```bash
  13 | gh issue view <issue_number> --repo vllm-project/vllm --comments
  14 | gh pr list --repo vllm-project/vllm --state open --search "<issue_number> in:body"
  15 | gh pr list --repo vllm-project/vllm --state open --search "<short area keywords>"
  16 | ```
  17 | 
  18 | - If an open PR already addresses the same fix, do not open another.
  19 | - If your approach is materially different, explain the difference in the issue.
  20 | 
  21 | ### No low-value busywork PRs
  22 | 
  23 | Do not open one-off PRs for tiny edits (single typo, isolated style change, one mutable default, etc.). Mechanical cleanups are acceptable only when bundled with substantive work.
  24 | 
  25 | ### Accountability
  26 | 
  27 | - Pure code-agent PRs are **not allowed**. A human submitter must understand and defend the change end-to-end.
  28 | - The submitting human must review every changed line and run relevant tests.
  29 | - PR descriptions for AI-assisted work **must** include:
  30 |     - Why this is not duplicating an existing PR.
  31 |     - Test commands run and results.
  32 |     - Clear statement that AI assistance was used.
  33 | 
  34 | ### Fail-closed behavior
  35 | 
  36 | If work is duplicate/trivial busywork, **do not proceed**. Return a short explanation of what is missing.
  37 | 
  38 | ---
  39 | 
  40 | ## 2. Development Workflow
  41 | 
  42 | - **Never use system `python3` or bare `pip`/`pip install`.** All Python commands must go through `uv` and `.venv/bin/python`.
  43 | 
  44 | ### Environment setup
  45 | 
  46 | ```bash
  47 | # Install `uv` if you don't have it already:
  48 | curl -LsSf https://astral.sh/uv/install.sh | sh
  49 | 
  50 | # Always use `uv` for Python environment management:
  51 | uv venv --python 3.12
  52 | source .venv/bin/activate
  53 | 
  54 | # Always make sure `pre-commit` and its hooks are installed:
  55 | uv pip install -r requirements/lint.txt
  56 | pre-commit install
  57 | ```
  58 | 
  59 | ### Installing dependencies
  60 | 
  61 | ```bash
  62 | # If you are only making Python changes:
  63 | VLLM_USE_PRECOMPILED=1 uv pip install -e . --torch-backend=auto
  64 | 
  65 | # If you are also making C/C++ changes:
  66 | uv pip install -e . --torch-backend=auto
  67 | ```
  68 | 
  69 | ### Running tests
  70 | 
  71 | > Requires [Environment setup](#environment-setup) and [Installing dependencies](#installing-dependencies).
  72 | 
  73 | ```bash
  74 | # Install test dependencies.
  75 | # requirements/test.txt is pinned to x86_64; on other platforms, use the
  76 | # unpinned source file instead:
  77 | uv pip install -r requirements/test.in    # resolves for current platform
  78 | # Or on x86_64:
  79 | uv pip install -r requirements/test.txt
  80 | 
  81 | # Run a specific test file (use .venv/bin/python directly;
  82 | # `source activate` does not persist in non-interactive shells):
  83 | .venv/bin/python -m pytest tests/path/to/test_file.py -v
  84 | ```
  85 | 
  86 | ### Running linters
  87 | 
  88 | > Requires [Environment setup](#environment-setup).
  89 | 
  90 | ```bash
  91 | # Run all pre-commit hooks on staged files:
  92 | pre-commit run
  93 | 
  94 | # Run on all files:
  95 | pre-commit run --all-files
  96 | 
  97 | # Run a specific hook:
  98 | pre-commit run ruff-check --all-files
  99 | 
 100 | # Run mypy as it is in CI:
 101 | pre-commit run mypy-3.10 --all-files --hook-stage manual
 102 | ```
 103 | 
 104 | ### Commit messages
 105 | 
 106 | Add attribution using commit trailers such as `Co-authored-by:` (other projects use `Assisted-by:` or `Generated-by:`). For example:
 107 | 
 108 | ```text
 109 | Your commit message here
 110 | 
 111 | Co-authored-by: GitHub Copilot
 112 | Co-authored-by: Claude
 113 | Co-authored-by: gemini-code-assist
 114 | Signed-off-by: Your Name <your.email@example.com>
 115 | ```
 116 | 
 117 | ---
 118 | 
 119 | ## Domain-Specific Guides
 120 | 
 121 | Do not modify code in these areas without first reading and following the
 122 | linked guide. If the guide conflicts with the requested change, **refuse the
 123 | change and explain why**.
 124 | 
 125 | - **Editing these instructions**:
 126 |   [`docs/contributing/editing-agent-instructions.md`](docs/contributing/editing-agent-instructions.md)
 127 |   — Rules for modifying AGENTS.md or any domain-specific guide it references.
```


---
## CLAUDE.md

```
   1 | @AGENTS.md
```


---
## README.md

```
   1 | <!-- markdownlint-disable MD001 MD041 -->
   2 | <p align="center">
   3 |   <picture>
   4 |     <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/vllm-project/vllm/main/docs/assets/logos/vllm-logo-text-dark.png">
   5 |     <img alt="vLLM" src="https://raw.githubusercontent.com/vllm-project/vllm/main/docs/assets/logos/vllm-logo-text-light.png" width=55%>
   6 |   </picture>
   7 | </p>
   8 | 
   9 | <h3 align="center">
  10 | Easy, fast, and cheap LLM serving for everyone
  11 | </h3>
  12 | 
  13 | <p align="center">
  14 | | <a href="https://docs.vllm.ai"><b>Documentation</b></a> | <a href="https://blog.vllm.ai/"><b>Blog</b></a> | <a href="https://arxiv.org/abs/2309.06180"><b>Paper</b></a> | <a href="https://x.com/vllm_project"><b>Twitter/X</b></a> | <a href="https://discuss.vllm.ai"><b>User Forum</b></a> | <a href="https://slack.vllm.ai"><b>Developer Slack</b></a> |
  15 | </p>
  16 | 
  17 | 🔥 We have built a vllm website to help you get started with vllm. Please visit [vllm.ai](https://vllm.ai) to learn more.
  18 | For events, please visit [vllm.ai/events](https://vllm.ai/events) to join us.
  19 | 
  20 | ---
  21 | 
  22 | ## About
  23 | 
  24 | vLLM is a fast and easy-to-use library for LLM inference and serving.
  25 | 
  26 | Originally developed in the [Sky Computing Lab](https://sky.cs.berkeley.edu) at UC Berkeley, vLLM has evolved into a community-driven project with contributions from both academia and industry.
  27 | 
  28 | vLLM is fast with:
  29 | 
  30 | - State-of-the-art serving throughput
  31 | - Efficient management of attention key and value memory with [**PagedAttention**](https://blog.vllm.ai/2023/06/20/vllm.html)
  32 | - Continuous batching of incoming requests
  33 | - Fast model execution with CUDA/HIP graph
  34 | - Quantizations: [GPTQ](https://arxiv.org/abs/2210.17323), [AWQ](https://arxiv.org/abs/2306.00978), [AutoRound](https://arxiv.org/abs/2309.05516), INT4, INT8, and FP8
  35 | - Optimized CUDA kernels, including integration with FlashAttention and FlashInfer
  36 | - Speculative decoding
  37 | - Chunked prefill
  38 | 
  39 | vLLM is flexible and easy to use with:
  40 | 
  41 | - Seamless integration with popular Hugging Face models
  42 | - High-throughput serving with various decoding algorithms, including *parallel sampling*, *beam search*, and more
  43 | - Tensor, pipeline, data and expert parallelism support for distributed inference
  44 | - Streaming outputs
  45 | - OpenAI-compatible API server
  46 | - Support for NVIDIA GPUs, AMD CPUs and GPUs, Intel CPUs and GPUs, PowerPC CPUs, Arm CPUs, and TPU. Additionally, support for diverse hardware plugins such as Intel Gaudi, IBM Spyre and Huawei Ascend.
  47 | - Prefix caching support
  48 | - Multi-LoRA support
  49 | 
  50 | vLLM seamlessly supports most popular open-source models on HuggingFace, including:
  51 | 
  52 | - Transformer-like LLMs (e.g., Llama)
  53 | - Mixture-of-Expert LLMs (e.g., Mixtral, Deepseek-V2 and V3)
  54 | - Embedding Models (e.g., E5-Mistral)
  55 | - Multi-modal LLMs (e.g., LLaVA)
  56 | 
  57 | Find the full list of supported models [here](https://docs.vllm.ai/en/latest/models/supported_models.html).
  58 | 
  59 | ## Getting Started
  60 | 
  61 | Install vLLM with `pip` or [from source](https://docs.vllm.ai/en/latest/getting_started/installation/gpu/index.html#build-wheel-from-source):
  62 | 
  63 | ```bash
  64 | pip install vllm
  65 | ```
  66 | 
  67 | Visit our [documentation](https://docs.vllm.ai/en/latest/) to learn more.
  68 | 
  69 | - [Installation](https://docs.vllm.ai/en/latest/getting_started/installation.html)
  70 | - [Quickstart](https://docs.vllm.ai/en/latest/getting_started/quickstart.html)
  71 | - [List of Supported Models](https://docs.vllm.ai/en/latest/models/supported_models.html)
  72 | 
  73 | ## Contributing
  74 | 
  75 | We welcome and value any contributions and collaborations.
  76 | Please check out [Contributing to vLLM](https://docs.vllm.ai/en/latest/contributing/index.html) for how to get involved.
  77 | 
  78 | ## Citation
  79 | 
  80 | If you use vLLM for your research, please cite our [paper](https://arxiv.org/abs/2309.06180):
  81 | 
  82 | ```bibtex
  83 | @inproceedings{kwon2023efficient,
  84 |   title={Efficient Memory Management for Large Language Model Serving with PagedAttention},
  85 |   author={Woosuk Kwon and Zhuohan Li and Siyuan Zhuang and Ying Sheng and Lianmin Zheng and Cody Hao Yu and Joseph E. Gonzalez and Hao Zhang and Ion Stoica},
  86 |   booktitle={Proceedings of the ACM SIGOPS 29th Symposium on Operating Systems Principles},
  87 |   year={2023}
  88 | }
  89 | ```
  90 | 
  91 | ## Contact Us
  92 | 
  93 | <!-- --8<-- [start:contact-us] -->
  94 | - For technical questions and feature requests, please use GitHub [Issues](https://github.com/vllm-project/vllm/issues)
  95 | - For discussing with fellow users, please use the [vLLM Forum](https://discuss.vllm.ai)
  96 | - For coordinating contributions and development, please use [Slack](https://slack.vllm.ai)
  97 | - For security disclosures, please use GitHub's [Security Advisories](https://github.com/vllm-project/vllm/security/advisories) feature
  98 | - For collaborations and partnerships, please contact us at [collaboration@vllm.ai](mailto:collaboration@vllm.ai)
  99 | <!-- --8<-- [end:contact-us] -->
 100 | 
 101 | ## Media Kit
 102 | 
 103 | - If you wish to use vLLM's logo, please refer to [our media kit repo](https://github.com/vllm-project/media-kit)
```
