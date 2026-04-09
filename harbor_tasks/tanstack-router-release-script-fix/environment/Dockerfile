FROM node:22-slim

# Install Python for pytest and git for repository operations
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt-get/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for efficiency)
RUN git clone --filter=blob:none https://github.com/TanStack/router.git router && \
    cd router && \
    git checkout ab46b5ec42296c60dc46d97481f038b8df68ed84

# Install pnpm globally (required by the repo)
RUN npm install -g pnpm

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/router
