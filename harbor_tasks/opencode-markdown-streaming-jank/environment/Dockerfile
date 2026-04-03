FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential python3 tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install bun (project uses bun as package manager)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin 311ba4179a3c112a7e0cbbeae152a971284a3632 && \
    git checkout FETCH_HEAD

RUN cd /workspace/opencode && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode