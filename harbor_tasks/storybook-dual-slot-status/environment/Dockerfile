FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone Storybook repository at base commit
ARG BASE_COMMIT=6abc5278709d3d598392e8cb50f740ae6dd2eb4e
RUN git clone --filter=blob:none https://github.com/storybookjs/storybook.git storybook && \
    cd storybook && \
    git checkout ${BASE_COMMIT}

# Install dependencies and compile
WORKDIR /workspace/storybook

# Install yarn dependencies
RUN yarn install --immutable

# Install Python dependencies for testing
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory to the code folder for tests
WORKDIR /workspace/storybook/code

# Default command
CMD ["bash"]
