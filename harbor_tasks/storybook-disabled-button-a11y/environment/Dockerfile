FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set up Python environment
RUN python3 -m pip install --break-system-packages pytest

# Create working directory
WORKDIR /workspace/storybook

# Clone the repository at base commit with minimal history
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/storybookjs/storybook.git /workspace/storybook \
    && git checkout 90d86a1213443055f5e1ce73c9e2d7a7ac5a8499

# Install dependencies
RUN yarn install --frozen-lockfile

# Compile the core package and dependencies
RUN yarn nx run-many -t compile --projects=storybook,@storybook/core

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
