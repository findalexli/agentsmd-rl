FROM node:22-slim

# Install Python for pytest runner
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit - fetch blobs for package files
ARG BASE_COMMIT=a120c05faf259ef45d23ab689bde5e9e5f7630fb
RUN git clone --filter=blob:none --no-checkout https://github.com/ant-design/ant-design.git ant-design && \
    cd ant-design && \
    git fetch --no-filter origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT} && \
    git fetch origin ${BASE_COMMIT} --depth=1

# Install dependencies (use npm install if package-lock.json missing)
RUN cd ant-design && \
    if [ -f package-lock.json ]; then npm ci --legacy-peer-deps; else npm install --legacy-peer-deps; fi

# Create logs directory
RUN mkdir -p /logs/verifier

# Copy test files (from parent directory context)
COPY ../tests/test_outputs.py /workspace/tests/
COPY ../tests/test.sh /workspace/tests/
RUN chmod +x /workspace/tests/test.sh

WORKDIR /workspace/ant-design
