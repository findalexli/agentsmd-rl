FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential && \
    rm -rf /var/lib/apt/lists/*

# Clone transformers repo at base commit (pre-fix)
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout 57e84139542c8c297873f35fcd25f66ffcf132ae && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/transformers

# Install dependencies - torch from PyTorch index, everything else from PyPI
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir pytest pytest-timeout pytest-json-ctrf numpy filelock requests regex 'tokenizers>=0.21.0'

# Install transformers in editable mode (without the full testing extras)
RUN pip install --no-cache-dir -e .

ENV PYTHONPATH="/workspace/transformers"

# Verifier output directory
RUN mkdir -p /logs/verifier
