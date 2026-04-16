FROM node:22-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
# Base commit: 199f65679628d2575f0cba43354e3db4284901a5
RUN git clone --filter=blob:none https://github.com/storybookjs/storybook.git storybook \
    && cd storybook \
    && git checkout 199f65679628d2575f0cba43354e3db4284901a5

# Install dependencies and compile
WORKDIR /workspace/storybook
RUN yarn install --frozen-lockfile || yarn install

# Compile the core package and dependencies
RUN yarn nx run-many -t compile --projects=storybook,@storybook/core

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/storybook
