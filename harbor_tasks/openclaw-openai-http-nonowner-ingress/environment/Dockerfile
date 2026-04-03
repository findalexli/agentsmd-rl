FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/openclaw && \
    cd /workspace/openclaw && \
    git remote add origin https://github.com/openclaw/openclaw.git && \
    git fetch --depth=1 origin c6f2db1506873e053bda30f99dea736a1b0e3ba2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install minimal deps for test scoring (just need to parse TS files)
# No full pnpm install — tests use grep/AST checks, not runtime execution
RUN corepack enable && corepack prepare pnpm@latest --activate

# Tests, rubric, and instruction are volume-mounted at runtime