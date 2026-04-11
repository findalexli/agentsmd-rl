FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates python3 python3-pip build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Clone Next.js at the base commit (before the fix)
RUN git init /workspace/next.js \
    && cd /workspace/next.js \
    && git remote add origin https://github.com/vercel/next.js.git \
    && git fetch --depth=1 origin 8283b1260ba3eb187baf20727e739fbd8ba7bbf6 \
    && git checkout FETCH_HEAD \
    && git config user.name "Agent" \
    && git config user.email "agent@test.com"

# Install dependencies (needed for prettier check)
RUN cd /workspace/next.js && pnpm install --frozen-lockfile || pnpm install

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js
