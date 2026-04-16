FROM node:22-slim

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace

# Clone the repository at base commit
RUN git clone --filter=blob:none https://github.com/mantinedev/mantine.git /workspace/mantine \
    && cd /workspace/mantine \
    && git checkout 0fabf4e0b9e42d7bef766ed2a0baf7a29ca53694

# Install dependencies
WORKDIR /workspace/mantine
RUN yarn install --frozen-lockfile --network-timeout 600000

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

WORKDIR /workspace/mantine
