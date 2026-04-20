FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22.x and yarn
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g yarn \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo
RUN git clone --filter=blob:none --depth=1 https://github.com/mantinedev/mantine.git mantine

WORKDIR /workspace/mantine

# Checkout base commit
RUN git fetch --filter=blob:none origin 4e071c14d8febd7e583ef59a9f8eb9245c22a3ae && git checkout 4e071c14d8febd7e583ef59a9f8eb9245c22a3ae

# Install dependencies for the mcp-server package
RUN yarn install --frozen-lockfile

# Install dependencies needed for tests
RUN pip install --no-cache-dir pytest==8.3.4

# Create logs directory
RUN mkdir -p /logs/verifier

# Do NOT copy solution/ or tests/ - harness mounts them externally
