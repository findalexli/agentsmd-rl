FROM node:22-slim

# Install Python and git for testing
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit
ARG REPO_URL=https://github.com/TanStack/router.git
ARG BASE_COMMIT=d1174179082d896a9674532994a4d6b38238c37e

RUN git clone --filter=blob:none $REPO_URL /workspace/router && \
    cd /workspace/router && \
    git checkout $BASE_COMMIT

# Set working directory to the repo
WORKDIR /workspace/router

# Install dependencies
RUN pnpm install

# Build packages to ensure tests can run
RUN CI=1 NX_DAEMON=false pnpm build

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set default command
CMD ["bash"]
