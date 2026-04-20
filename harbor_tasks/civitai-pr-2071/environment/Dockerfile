FROM python:3.12-slim

# Install git, Node.js and pnpm
RUN apt-get update && apt-get install -y curl git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm@9 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone repo at base commit (not the merge commit — we need to apply the fix)
RUN git clone --filter=blob:none --depth=1 https://github.com/civitai/civitai.git civitai_repo
WORKDIR /workspace/civitai_repo
RUN git fetch --depth=1 origin 47c3beedb50993e5f410e241e4940131bba9afb2
RUN git checkout 47c3beedb50993e5f410e241e4940131bba9afb2

# Install dependencies (for p2p tests: typecheck, lint)
RUN pnpm install --frozen-lockfile

# Install Python deps for test runner
RUN pip install --no-cache-dir pytest==8.3.4 requests==2.32.3

# Create logs dir
RUN mkdir -p /logs/verifier
