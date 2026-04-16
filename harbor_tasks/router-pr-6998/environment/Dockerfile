FROM node:22-slim

# Install git, python3 (needed by pytest runner), and other essentials
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    patch \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /workspace

# Clone the repository at the base commit
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router \
    && cd router \
    && git checkout e71040784ac43a8ea259ea820c0d62ea80b8d7a3

WORKDIR /workspace/router

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build the packages (needed for tests)
RUN pnpm build:all

# Install pytest for the test runner
RUN python3 -m pip install pytest --break-system-packages

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/router
