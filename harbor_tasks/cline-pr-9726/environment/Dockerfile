FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl nodejs npm \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace/cline && \
    git clone --filter=blob:none https://github.com/cline/cline /workspace/cline

WORKDIR /workspace/cline

# Start at base commit (parent of merge) - tests will fail here
RUN git fetch --filter=blob:none origin f6d2b4d9acbf52d5fc5ad4e8f519a2d2d45e5dfb && \
    git checkout f6d2b4d9acbf52d5fc5ad4e8f519a2d2d45e5dfb

RUN npm install 2>&1 | tail -5

RUN mkdir -p /logs/verifier
