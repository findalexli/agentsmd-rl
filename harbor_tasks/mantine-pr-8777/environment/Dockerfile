FROM python:3.12-slim

WORKDIR /workspace

# Install git, Node.js, npm, and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 24 (matches repo's .nvmrc) via nvm or direct binary
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g npm@latest \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace/mantine_repo

# Clone at base commit
RUN git clone --filter=blob:none --depth=1 https://github.com/mantinedev/mantine.git . \
    && git fetch --depth=1 origin 1cb55b4131525aa802b68020c66a345760a0d466 \
    && git checkout 1cb55b4131525aa802b68020c66a345760a0d466

# Install deps with yarn (faster, less issues with workspace protocol)
RUN corepack enable && corepack prepare yarn@stable --activate
RUN yarn install --immutable 2>&1 | tail -20

# Pin pytest for the test runner
RUN pip install --no-cache-dir pytest==8.3.4

# Create logs directory
RUN mkdir -p /logs/verifier
