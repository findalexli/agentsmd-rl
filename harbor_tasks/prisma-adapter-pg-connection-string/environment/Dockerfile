FROM python:3.12-slim

WORKDIR /workspace

# Install Node.js 22, pnpm, and git
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gnupg \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g pnpm@10.15.1 \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (parent of merge)
RUN git clone --filter=blob:none https://github.com/prisma/prisma.git
WORKDIR /workspace/prisma
RUN git checkout a98aff2ede1598a7718f07cde9204b435ae4b5b4

# Install deps and build packages needed by adapter-pg
RUN pnpm install --frozen-lockfile
# Build from root — turbo orchestrates deps in correct order
RUN pnpm build

# Create logs dir
RUN mkdir -p /logs/verifier

CMD ["bash"]