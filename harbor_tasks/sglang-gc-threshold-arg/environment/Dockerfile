FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux bc \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
# Use blobless clone to avoid downloading full history (repo is very large)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin 4e905febd2f9e96b4c114530a2379b084ad791af && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

# Install minimal deps for testing (no torch/GPU needed)
# We only need the package to be importable for server_args and basic engine code
RUN pip install --no-cache-dir \
    dataclasses-json \
    pydantic \
    requests \
    packaging \
    fastapi \
    uvicorn \
    aiohttp \
    numpy \
    psutil \
    pytest \
    pytest-json-ctrf \
    && pip install --no-cache-dir -e "python/" 2>/dev/null || true

# Set PYTHONPATH so we can import sglang modules
ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH:-}"

# Configure git user
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"