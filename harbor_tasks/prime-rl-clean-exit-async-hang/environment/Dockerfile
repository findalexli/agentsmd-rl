FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at the base commit (BEFORE the fix)
RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin 27c35b1ce136c85c120b0486128316ae022b53a5 && \
    git checkout FETCH_HEAD

# Install uv (matches CI: astral-sh/setup-uv@v5)
RUN pip3 install --break-system-packages uv

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl