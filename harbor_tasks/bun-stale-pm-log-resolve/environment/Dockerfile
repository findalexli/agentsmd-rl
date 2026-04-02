FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update -o Acquire::AllowInsecureRepositories=true \
    && apt-get install -y --no-install-recommends -o APT::Get::AllowUnauthenticated=true \
    git curl ca-certificates build-essential unzip tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone bun at base commit (before fix)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun \
    && cd /workspace/bun \
    && git fetch --depth=1 origin 9ce5b052840cecea4aa1977aeb063c47d0137a22 \
    && git checkout 9ce5b052840cecea4aa1977aeb063c47d0137a22

# Configure git for applying patches
RUN cd /workspace/bun && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun