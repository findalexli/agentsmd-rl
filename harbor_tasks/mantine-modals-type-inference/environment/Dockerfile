FROM node:22-slim

# Install python3 for pytest runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Clone the repo at the base commit
WORKDIR /workspace
ARG BASE_COMMIT=44c661434baf4f0c46c5d4538ea53da03f060be9
RUN git clone --filter=blob:none https://github.com/mantinedev/mantine.git && \
    cd mantine && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/mantine
RUN yarn install --frozen-lockfile

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/mantine
