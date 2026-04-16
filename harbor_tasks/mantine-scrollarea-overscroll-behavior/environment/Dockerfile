FROM node:22-slim

# Install Python for pytest
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Clone repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/mantinedev/mantine.git

WORKDIR /workspace/mantine
# Checkout base commit (before the fix)
RUN git checkout 50526dd9df22b8d51f9890d92604a7b53ee85dc1

# Install dependencies
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
