FROM node:22-slim

# Install Python for test harness and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Create workspace directory
WORKDIR /workspace

# Clone ant-design repository at base commit
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git ant-design \
    && cd ant-design \
    && git checkout df5547f2ade5fe0bd9906bb9a386e7865afa4835

# Install dependencies
WORKDIR /workspace/ant-design
RUN npm install --legacy-peer-deps

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/ant-design
