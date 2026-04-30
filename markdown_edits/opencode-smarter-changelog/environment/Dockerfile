FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install bun (needed to run .ts scripts that use Bun-specific APIs)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout 057848deb847d59250e7db08ab2402f4a69bfcda && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
