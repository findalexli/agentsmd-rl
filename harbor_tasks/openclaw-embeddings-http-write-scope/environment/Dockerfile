FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
      git curl ca-certificates build-essential tmux python3 && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone https://github.com/openclaw/openclaw.git /workspace/openclaw && \
    cd /workspace/openclaw && \
    git checkout 85647949a484957ba6bac00e47653b0acd4a92d7 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/openclaw

# Install pnpm for potential agent use
RUN corepack enable && corepack prepare pnpm@latest --activate
