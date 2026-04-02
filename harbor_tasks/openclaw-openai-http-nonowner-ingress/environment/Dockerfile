FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone https://github.com/openclaw/openclaw.git /workspace/openclaw && \
    cd /workspace/openclaw && \
    git checkout c6f2db1506873e053bda30f99dea736a1b0e3ba2 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install minimal deps for test scoring (just need to parse TS files)
# No full pnpm install — tests use grep/AST checks, not runtime execution
RUN corepack enable && corepack prepare pnpm@latest --activate

# Tests, rubric, and instruction are volume-mounted at runtime