FROM node:20-slim

# Install Python and git (needed for pytest and repo checkout)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Enable corepack and install pnpm matching CI version
RUN corepack enable && corepack prepare pnpm@10.28.1 --activate

WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --depth=1 --filter=blob:none https://github.com/civitai/civitai.git civitai
WORKDIR /workspace/civitai
RUN git fetch --depth=1 origin 1ef47bec41ce9f6f4b0f7ee89921a0ca263ac7df && \
    git checkout 1ef47bec41ce9f6f4b0f7ee89921a0ca263ac7df

# Install dependencies
RUN pnpm install --frozen-lockfile

# Make pip usable (PEP 668 workaround for Docker)
RUN python3 -m pip install --no-cache-dir --break-system-packages pytest==8.3.4 pytest-timeout==2.3.1

# Create logs directory
RUN mkdir -p /logs/verifier

CMD ["bash"]
