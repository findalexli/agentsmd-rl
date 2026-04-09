FROM python:3.12-slim

# Install Node.js and git
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone ant-design repo at base commit (shallow clone for efficiency)
RUN git clone --filter=blob:none --depth=50 https://github.com/ant-design/ant-design.git ant-design \
    && cd ant-design \
    && git fetch --depth=50 origin b73b49c02f70e54ffc67c6e7ec895ec8d62378f3 \
    && git checkout b73b49c02f70e54ffc67c6e7ec895ec8d62378f3

# Set working directory to the repo
WORKDIR /workspace/ant-design

# The repo uses npm; package.json defines all dependencies
# We'll install dependencies in solve.sh to match the task flow

# Create log directories
RUN mkdir -p /logs/verifier /logs/agent

# Copy test files
COPY tests/ /workspace/task/tests/

WORKDIR /workspace/ant-design
