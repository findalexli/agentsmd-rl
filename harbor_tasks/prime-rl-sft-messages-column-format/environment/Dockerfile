FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git init /workspace && \
    cd /workspace && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin 7e853195ea6c7ce0cdfd67f7f00e6fb755ad0e17 && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir pydantic pydantic-settings

RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Install CPU-only torch and minimal deps needed for SFT data module testing
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir transformers datasets torchdata jaxtyping \
    pydantic loguru beartype numpy pyarrow tomli rich \
    pytest pytest-json-ctrf pydantic-settings
RUN pip install --no-cache-dir "pydantic-config @ git+https://github.com/samsja/pydantic_config.git@main"

# Pre-download tokenizer for tests
RUN python3 -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('PrimeIntellect/Qwen3-0.6B')"

ENV PYTHONPATH="/workspace/src:${PYTHONPATH}"