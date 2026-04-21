FROM python:3.12-slim

# Install Node.js, pnpm, and git
RUN apt-get update && apt-get install -y curl git && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g pnpm@9 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --depth=1 --filter=blob:none https://github.com/civitai/civitai.git civitai
WORKDIR /workspace/civitai
RUN git fetch --depth=1 origin 1ef47bec41ce9f6f4b0f7ee89921a0ca263ac7df && \
    git checkout 1ef47bec41ce9f6f4b0f7ee89921a0ca263ac7df

# Install dependencies (only what's needed for tests)
RUN pnpm install --frozen-lockfile

# Install pytest for test runner
RUN python3 -m pip install pytest==8.3.4 pytest-timeout==2.3.1

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]