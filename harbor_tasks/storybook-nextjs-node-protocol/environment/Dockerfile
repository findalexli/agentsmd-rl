FROM node:22-slim

# Install Python (needed by pytest runner) and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Clone the storybook repo with blobless clone for faster checkout
# Using base commit: 370524faae96a30d27e36efcaa2fc39cd65fab29
RUN git clone --filter=blob:none --single-branch --branch next https://github.com/storybookjs/storybook.git /workspace/storybook \
    && cd /workspace/storybook \
    && git checkout 370524faae96a30d27e36efcaa2fc39cd65fab29

WORKDIR /workspace/storybook

# Install dependencies for the nextjs package (focused install for speed)
# We need to install at the root level for the monorepo to work
RUN yarn install --immutable || yarn install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
