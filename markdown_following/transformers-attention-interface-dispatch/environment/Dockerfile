FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU (needed to import transformers model modules)
RUN pip install --no-cache-dir \
    torch==2.6.0 \
    --index-url https://download.pytorch.org/whl/cpu

# Install transformers core dependencies (pinned)
RUN pip install --no-cache-dir \
    numpy==2.0.1 \
    packaging==24.2 \
    pyyaml==6.0.2 \
    regex==2024.11.6 \
    requests==2.32.3 \
    tokenizers==0.21.0 \
    safetensors==0.5.3 \
    filelock==3.17.0 \
    huggingface-hub==0.29.3 \
    tqdm==4.67.1

# Clone repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers \
    && cd /workspace/transformers \
    && git checkout a804c74a9fc0518c1fa992decdac485c17f87479

# Install transformers in editable mode
RUN pip install --no-cache-dir -e /workspace/transformers

# Install test tools
RUN pip install --no-cache-dir \
    pytest==8.3.4 \
    ruff==0.9.6

RUN mkdir -p /logs/verifier
