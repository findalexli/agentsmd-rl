FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin b92c2128ddeb679c23954c2bf6825e4d6659d501 && \
    git checkout FETCH_HEAD

# Install minimal deps for testing (only pydantic needed for config classes)
RUN cd /workspace/prime-rl && pip install --no-cache-dir pydantic

# Configure git for applying patches
RUN cd /workspace/prime-rl && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

ENV PYTHONPATH=/workspace/prime-rl/src
RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl