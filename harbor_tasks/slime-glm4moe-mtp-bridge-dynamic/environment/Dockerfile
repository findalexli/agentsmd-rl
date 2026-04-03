FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at base commit (before fix)
RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth=1 origin 57e76686346beeaaec4010ebefc56b9949686457 && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime

ENV PYTHONPATH="/workspace/slime:${PYTHONPATH:-}"