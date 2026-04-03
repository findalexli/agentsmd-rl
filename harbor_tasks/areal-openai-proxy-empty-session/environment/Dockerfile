FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/AReaL && \
    cd /workspace/AReaL && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin 84eaef1292b2a3184d4a565d4abb0758408be018 && \
    git checkout FETCH_HEAD

# Install minimal deps for testing (no torch/GPU needed — we test via AST + import)
RUN cd /workspace/AReaL && \
    pip install --no-cache-dir pyyaml aiohttp pytest pytest-json-ctrf

# Configure git
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH=/workspace/AReaL
RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL