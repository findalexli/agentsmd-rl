FROM rust:1.82-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git clone https://github.com/zeroclaw-labs/zeroclaw.git /workspace/zeroclaw && \
    cd /workspace/zeroclaw && \
    git checkout 753d4fc65f32b45797e7aba52db6c8eb3a24ad89

# Install minimal deps (agent fills in specifics)



RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/zeroclaw
