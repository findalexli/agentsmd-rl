FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (with minimal history)
RUN git clone --filter=blob:none --depth=50 https://github.com/mantinedev/mantine.git mantine \
    && cd mantine \
    && git checkout 0c52227db887ce0b48fe59fa3422638b0448e1e1

# Install dependencies
WORKDIR /workspace/mantine
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/mantine
