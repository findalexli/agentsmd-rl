FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm and tsx for TypeScript execution
RUN npm install -g pnpm@10 tsx

# Clone payload (shallow)
WORKDIR /workspace
RUN git clone --filter=blob:none --no-checkout https://github.com/payloadcms/payload.git
WORKDIR /workspace/payload
RUN git checkout 727d74eff1476bcd8236f716282275e42f8786ad

# Install dependencies (without building anything)
RUN pnpm install --frozen-lockfile=false

WORKDIR /workspace
RUN mkdir -p /workspace/task_tests /logs/verifier /workspace/task
