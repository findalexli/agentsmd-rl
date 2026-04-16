FROM node:22-slim

WORKDIR /workspace

# Install git and python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at base commit
RUN git clone --filter=blob:none --no-checkout https://github.com/continuedev/continue.git /workspace/continue \
    && cd /workspace/continue \
    && git checkout 173810bab405bb1c6e3740e90207ffdc17d1065b

WORKDIR /workspace/continue/extensions/cli

# Fetch package.json from the base commit
RUN curl -fsSL https://raw.githubusercontent.com/continuedev/continue/173810bab405bb1c6e3740e90207ffdc17d1065b/extensions/cli/package.json -o package.json

# Install tsx and vitest only — tsx runs .ts files directly without full project compilation
RUN npm install --legacy-peer-deps \
    tsx@^4.20.3 \
    vitest@^3.2.4 \
    @types/node@^10.0.3 \
    typescript@^5.8.3

# Install pytest runner
RUN pip3 install --break-system-packages pytest pytest-timeout

# Create log dir
RUN mkdir -p /logs/verifier
