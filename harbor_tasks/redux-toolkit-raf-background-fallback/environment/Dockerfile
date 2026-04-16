FROM node:22-slim

# Install Python for pytest runner, git for cloning, and patch for applying fixes
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    patch \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/reduxjs/redux-toolkit.git

# The repo structure has packages/toolkit as the main package
WORKDIR /workspace/redux-toolkit
RUN git checkout 20a03774af8a9f1090796bb728254168702f3f60

# Install dependencies
RUN yarn install

# Build the toolkit package
RUN yarn workspace @reduxjs/toolkit run build

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Working directory for task
WORKDIR /workspace/redux-toolkit/packages/toolkit
