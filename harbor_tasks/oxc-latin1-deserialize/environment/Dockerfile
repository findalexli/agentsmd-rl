FROM node:22-slim

# Install Python for pytest and required dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone the oxc repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/oxc-project/oxc.git

WORKDIR /workspace/oxc
RUN git checkout 55e1e9b1d22c30f8ec9bf937c66c4d5d428a6116

# Install pnpm (required by the project)
RUN npm install -g pnpm

# Install dependencies for napi/parser
WORKDIR /workspace/oxc/napi/parser
RUN pnpm install

# Set working directory back to repo root
WORKDIR /workspace/oxc
