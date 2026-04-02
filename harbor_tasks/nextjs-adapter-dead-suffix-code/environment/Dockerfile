FROM node:22-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git clone --filter=blob:none https://github.com/vercel/next.js.git /repo \
    && cd /repo \
    && git checkout 904501127c9ed2e0a7ffd51bd192537b7c398fb3

# Configure git
RUN cd /repo && git config user.name "test" && git config user.email "test@test.com"

# Install TypeScript globally for syntax checking in tests
RUN npm install -g typescript

RUN mkdir -p /logs/verifier

WORKDIR /repo