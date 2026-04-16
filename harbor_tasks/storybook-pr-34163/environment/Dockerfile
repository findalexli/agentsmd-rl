FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /workspace

# Clone the storybook repository at the base commit
# Use --filter=blob:none for partial clone to save time/space
RUN git clone --filter=blob:none https://github.com/storybookjs/storybook.git

WORKDIR /workspace/storybook

# Checkout the base commit (parent of merge commit)
RUN git checkout 5f74cba8c083b6166bdd5d5394ab650fc8f29051

# Install dependencies (Storybook uses Yarn Berry)
RUN yarn install --immutable

# Pre-compile just the core package and dependencies for faster test runs
RUN yarn nx run-many -t compile --projects=storybook,@storybook/components

# Create logs directory for test outputs
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/storybook
