FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth=1 origin f3a86d51d9efbb5575a9d87839a81135a51d6233 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/slime

# Install minimal deps for testing (CPU-only torch, no GPU)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir aiohttp pillow

# Stub transformers module so processing_utils can be imported
# (only encode_image_for_rollout_engine is needed; it uses only PIL + base64)
RUN mkdir -p /workspace/stubs/transformers /logs/verifier && \
    printf 'class AutoProcessor:\n    @classmethod\n    def from_pretrained(cls, *a, **kw): pass\n' > /workspace/stubs/transformers/__init__.py && \
    printf 'AutoTokenizer = AutoProcessor\nPreTrainedTokenizerBase = object\nProcessorMixin = object\n' >> /workspace/stubs/transformers/__init__.py

ENV PYTHONPATH="/workspace/slime:/workspace/stubs"

RUN git config --global user.name "agent" && git config --global user.email "agent@test"