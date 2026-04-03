FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip unzip \
    && rm -rf /var/lib/apt/lists/*

# Pre-install pytest so test.sh doesn't need network at test time
RUN python3 -m pip install --break-system-packages pytest pytest-json-ctrf

# Install bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Install gh CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y gh && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/opencode && \
    cd /workspace/opencode && \
    git remote add origin https://github.com/anomalyco/opencode.git && \
    git fetch --depth=1 origin ee018d5c82a593907bae9011bc074766e670d593 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/opencode

# Install minimal deps needed for type checking / parsing
# (no full build needed - just bun install for TypeScript resolution)
RUN bun install --frozen-lockfile 2>/dev/null || bun install || true