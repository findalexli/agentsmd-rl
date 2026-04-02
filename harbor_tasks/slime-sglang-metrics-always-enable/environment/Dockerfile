FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at base commit (before fix)
RUN git clone https://github.com/THUDM/slime.git /workspace/slime && \
    cd /workspace/slime && \
    git checkout a9614431b35e9c54b88a42f9d565ef81075172a1

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime

ENV PYTHONPATH="/workspace/slime:${PYTHONPATH:-}"