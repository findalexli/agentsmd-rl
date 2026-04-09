FROM node:22-slim

# Install Python for test runner
RUN apt-get update && apt-get install -y python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Clone ant-design repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=aa0594058b3735533a59c83feb5c309e88b544bd
RUN git clone --filter=blob:none --depth=50 https://github.com/ant-design/ant-design.git /workspace/ant-design \
    && cd /workspace/ant-design \
    && git checkout ${BASE_COMMIT}

WORKDIR /workspace/ant-design

# Install dependencies
RUN npm install

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set up Python for tests
ENV PYTHONPATH=/workspace:/workspace/ant-design
