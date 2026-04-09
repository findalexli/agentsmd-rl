FROM node:22-slim

# Install Python for pytest and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone superset repo at base commit
ARG REPO=superset
ARG BASE_COMMIT=4f695e1b4d23beb67473b39d2f0ab71df56378b3
WORKDIR /workspace

# Clone with shallow history for speed
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/superset.git && \
    cd superset && \
    git checkout ${BASE_COMMIT}

# Install frontend dependencies (needed for TypeScript checking)
WORKDIR /workspace/superset/superset-frontend
RUN npm ci --legacy-peer-deps --no-audit --no-fund || npm install --legacy-peer-deps --no-audit --no-fund

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
