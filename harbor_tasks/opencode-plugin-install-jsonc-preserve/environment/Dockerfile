FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install bun (project uses bun runtime)
RUN curl -fsSL https://bun.sh/install | bash
ENV BUN_INSTALL="/root/.bun"
ENV PATH="$BUN_INSTALL/bin:$PATH"

# Clone opencode at base commit (before fix)
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin afb6abff73bdc1577f7388d8273e2eba69849e08 && \
    git checkout FETCH_HEAD

# Configure git
RUN cd /workspace/opencode && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

# Install dependencies (needed for behavioral tests)
RUN cd /workspace/opencode && bun install --frozen-lockfile 2>/dev/null || \
    cd /workspace/opencode && bun install

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode