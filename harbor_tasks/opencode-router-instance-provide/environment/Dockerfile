FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 unzip \
    && rm -rf /var/lib/apt/lists/*

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

RUN git clone https://github.com/anomalyco/opencode.git /workspace/opencode \
    && cd /workspace/opencode \
    && git checkout e5f0e813b6e2f9305fc27d432689f95a56beea51

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

# Install dependencies
RUN bun install --frozen-lockfile || bun install

# Configure git for patching
RUN git config user.email "test@test.com" && git config user.name "Test"

ENV PYTHONPATH=/workspace/opencode