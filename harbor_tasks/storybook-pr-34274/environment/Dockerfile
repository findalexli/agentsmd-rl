FROM node:22-slim

WORKDIR /workspace

# Install python3 and pip for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest with pinned versions
RUN pip3 install --no-cache-dir --break-system-packages pytest==8.3.4 pytest-timeout==2.3.1

# Clone storybook repo (filter=blob:none for efficiency)
RUN git clone --filter=blob:none --depth=1 https://github.com/storybookjs/storybook.git storybook

WORKDIR /workspace/storybook

# Checkout base commit (parent of merge)
RUN git fetch --depth=1 origin db1ddc8e390e80df62a3cf2a92d0b92faab2c3f4 && \
    git checkout db1ddc8e390e80df62a3cf2a92d0b92faab2c3f4

# Install yarn berry
RUN corepack enable && corepack prepare yarn@stable --activate

# Install dependencies
RUN yarn install --immutable

# Compile the builder-vite package
RUN yarn nx compile builder-vite

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/storybook