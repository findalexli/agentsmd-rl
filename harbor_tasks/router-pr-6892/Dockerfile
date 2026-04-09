FROM node:22-slim

RUN apt-get update && apt-get install -y git python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout 870cf28066954b17e551c4e0f6627e382f0d6a57

WORKDIR /workspace/router

# Install pnpm and dependencies
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set up Python for pytest
ENV PYTHONPATH=/workspace/router:$PYTHONPATH
