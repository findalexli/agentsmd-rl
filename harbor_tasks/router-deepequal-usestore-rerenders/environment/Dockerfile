FROM node:22-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit
ARG BASE_COMMIT=d5622bb413a2d1ac99c546c5336be949dfb351d9
RUN git clone --filter=blob:none https://github.com/TanStack/router.git && \
    cd router && \
    git checkout ${BASE_COMMIT}

# Install dependencies
WORKDIR /workspace/router
RUN pnpm install

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
