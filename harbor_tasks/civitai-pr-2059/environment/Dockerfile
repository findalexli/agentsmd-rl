FROM python:3.12-slim

# Install Node.js 22, pnpm, and git
RUN apt-get update && apt-get install -y curl git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm@9.15.0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for running tests
RUN pip install --no-cache-dir pytest==8.3.4

WORKDIR /workspace

# Clone the repository at base commit
RUN git clone --filter=blob:none https://github.com/civitai/civitai.git \
    && cd civitai \
    && git checkout 91f7bf0cd37ff0418bcc7fd48cb02fa3202faa31

WORKDIR /workspace/civitai

# Install dependencies (production-like, minimal)
RUN pnpm install --frozen-lockfile --prod=false

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]