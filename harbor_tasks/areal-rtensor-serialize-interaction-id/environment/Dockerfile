FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir httpx

RUN mkdir -p /logs/verifier

WORKDIR /repos/AReaL

RUN git clone https://github.com/inclusionAI/AReaL.git . && \
    git checkout 3bf10c9c56eeae846b3de52dde8db42918f80690

# Install torch CPU-only and minimal deps for testing serialization
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir openai pydantic numpy aiohttp colorlog Pillow flask orjson pytest pytest-json-ctrf

# Neutralize __init__.py files that pull in GPU/cluster deps (torchdata,
# transformers, etc.) via transitive re-exports. Tests import specific
# submodules directly so these re-exports are not needed.
RUN for f in \
      areal/__init__.py \
      areal/infra/__init__.py \
      areal/infra/rpc/__init__.py \
      areal/experimental/openai/__init__.py \
      areal/experimental/openai/proxy/__init__.py; do \
    echo '' > "$f"; \
    done

ENV PYTHONPATH=/repos/AReaL
RUN git config user.email "test@test.com" && git config user.name "Test"

WORKDIR /repos/AReaL