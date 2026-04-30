FROM node:22-slim

# Install Python and pytest
RUN apt-get update && apt-get install -y python3 python3-pip git \
    && pip install --break-system-packages pytest \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo
RUN git clone --filter=blob:none https://github.com/openai/openai-agents-js.git

WORKDIR /workspace/openai-agents-js

# Checkout base commit
RUN git checkout 4e6b3fbd3355709831a1bb64472b3c947b694690

# Install pnpm globally
RUN npm install -g pnpm@10

# Install dependencies
RUN pnpm install --frozen-lockfile

# Create logs directory
RUN mkdir -p /logs/verifier
