FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone https://github.com/openclaw/openclaw.git /workspace/openclaw && \
    cd /workspace/openclaw && \
    git checkout 29cb1e3c7edd54a3d060419ffa153eecbd19c133 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install pnpm and deps (needed for behavioral tests that call the code)
RUN corepack enable && corepack prepare pnpm@latest --activate

# Tests and rubric are volume-mounted at runtime