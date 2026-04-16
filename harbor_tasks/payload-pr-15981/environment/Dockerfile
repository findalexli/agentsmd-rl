FROM node:22-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm
RUN npm install -g pnpm@10.27.0

WORKDIR /workspace

# Clone the repository with blobless filter (skips downloading file content)
RUN git clone --filter=blob:none https://github.com/payloadcms/payload.git payload_repo && \
    cd payload_repo && \
    git checkout 944a889d

# Install dependencies
RUN cd /workspace/payload_repo && pnpm install --frozen-lockfile

# Install pytest
RUN pip3 install pytest --break-system-packages -q

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/payload_repo
