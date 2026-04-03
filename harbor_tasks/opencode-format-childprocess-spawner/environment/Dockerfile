FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV BUN_INSTALL=/root/.bun
ENV PATH=$BUN_INSTALL/bin:$PATH

# Clone opencode at base commit (before fix)
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin c8909908f50afc3622d354cd8fd7a83dc3445706 && \
    git checkout FETCH_HEAD

# Install dependencies (at base commit — no new deps needed by fix)
RUN cd /workspace/opencode && bun install

# Configure git
RUN cd /workspace/opencode && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode