FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Clone repo at base commit (before fix)
RUN git clone https://github.com/THUDM/slime.git /workspace/slime && \
    cd /workspace/slime && \
    git checkout f9f7b566cca476aeeb963b67a44d663da79e0484

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime

ENV PYTHONPATH="/workspace/slime:${PYTHONPATH:-}"