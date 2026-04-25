FROM node:22-slim

# Install Python for pytest and pnpm
RUN apt-get update && apt-get install -y python3 python3-pip curl git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable corepack for pnpm
RUN corepack enable && corepack prepare pnpm@10.6.2 --activate

ENV PATH="/root/.local/share/pnpm:$PATH"

# Clone the repo at base commit
ARG REPO=tanstack-router
ARG BASE_COMMIT=870cf28066954b17e551c4e0f6627e382f0d6a57
RUN git clone --filter=blob:none https://github.com/TanStack/router.git /workspace/router && \
    cd /workspace/router && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/router

# Install dependencies (needed for the script to work)
RUN pnpm install --frozen-lockfile || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
