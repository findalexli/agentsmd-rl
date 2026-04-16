FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/shadcn-ui/ui.git
WORKDIR /workspace/ui
RUN git checkout 64c8cd99eee94cc3b76c063a8e62bc66fbede62f

# Install dependencies
RUN npm install -g pnpm
RUN pnpm install

# Create logs directory
RUN mkdir -p /logs/verifier
