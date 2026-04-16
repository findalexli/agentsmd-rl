FROM node:22-slim

# Install git and python3 (needed by pytest runner)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    python3 \
    python3-pip \
    patch \
    && rm -rf /var/lib/apt/lists/* \
    && pip3 install pytest --break-system-packages

# Clone ant-design at the base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd \
    && cd antd \
    && git checkout 853528ee93702fa919de71c996ce3a774b1c7ab6

WORKDIR /workspace/antd

# Install dependencies
RUN npm install --legacy-peer-deps

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for the task
WORKDIR /workspace/antd
