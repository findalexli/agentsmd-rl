FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "bench@test" && \
    git config --global user.name "Bench"

# Clone slime at the base commit (before the fix)
RUN git init /workspace/slime && \
    cd /workspace/slime && \
    git remote add origin https://github.com/THUDM/slime.git && \
    git fetch --depth=1 origin 6f11313004dbe71f4194536335b891371eefd0e9 && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime

ENV PYTHONPATH="/workspace/slime:${PYTHONPATH:-}"