FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone Next.js at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js \
    && cd /workspace/next.js \
    && git checkout e9df6ed9dc381cf99e54c91d984799ca51e2940f

# Configure git
RUN cd /workspace/next.js && \
    git config user.name "Agent" && \
    git config user.email "agent@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js