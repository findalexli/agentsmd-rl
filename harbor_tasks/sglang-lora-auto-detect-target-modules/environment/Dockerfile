FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before fix)
RUN git clone https://github.com/sgl-project/sglang.git /workspace/sglang \
    && cd /workspace/sglang \
    && git checkout 9b29131961bb6c167e6956dae60a6269232ca694 \
    && git config user.email "bench@test" \
    && git config user.name "Benchmark"

# Install minimal deps for the LoRA module (no torch/GPU)
# We only need enough to parse the Python and run AST/import checks
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir \
    peft transformers safetensors pydantic \
    && pip install --no-cache-dir --no-deps -e /workspace/sglang/python

ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH:-}"
RUN pip install --no-cache-dir pybase64

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang