FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone Next.js at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /workspace/next.js \
    && cd /workspace/next.js \
    && git checkout b5cb015c5f94088cf0211613051fb696b67cddda

# Configure git
RUN cd /workspace/next.js && \
    git config user.name "Agent" && \
    git config user.email "agent@test.com"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js