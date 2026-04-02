FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash user
USER user
RUN mkdir -p /logs/verifier

WORKDIR /home/user

# Clone uv at the base commit (before the fix)
RUN git clone --no-checkout https://github.com/astral-sh/uv.git && \
    cd uv && \
    git checkout 8b1a15eae6aa51f25f7dfefd247d5592201b78a0 && \
    git config user.email "bench@test.com" && \
    git config user.name "Bench"

WORKDIR /home/user/uv