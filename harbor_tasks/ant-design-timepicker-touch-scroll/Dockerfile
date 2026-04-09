FROM node:22-slim

# Install Python for the test runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit
ARG BASE_COMMIT
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git /workspace/ant-design && \
    cd /workspace/ant-design && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/ant-design

# Install dependencies (antd uses npm/pnpm)
RUN npm install -g pnpm && pnpm install

# Create logs directory
RUN mkdir -p /logs/verifier

# Copy test files
COPY tests/test_outputs.py /workspace/test_outputs.py
COPY test.sh /workspace/test.sh

# The test script will run as the verification command
CMD ["/bin/bash", "/workspace/test.sh"]
