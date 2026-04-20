FROM node:22.22.2-slim

# Install Python, pytest, and git for test runner
RUN apt-get update && apt-get install -y \
    python3 python3-pip git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install pytest and requests for test runner
RUN pip3 install --no-cache-dir --break-system-packages pytest==8.3.4 requests==2.32.3

WORKDIR /workspace

# Clone the repository (shallow clone for efficiency)
RUN git clone --filter=blob:none --depth=100 https://github.com/supabase/supabase.git

WORKDIR /workspace/supabase

# Checkout the base commit (parent of merge commit)
RUN git checkout ebf9bc495530156f091e458ef12d86acd7c6646b

# Install dependencies (monorepo uses pnpm workspaces)
RUN npm install -g pnpm@10.24.0
RUN pnpm install --frozen-lockfile

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]