# Dockerfile for ant-design/ant-design#57440
# Task: Typography actions placement feature

FROM node:22-slim

# Install python3 for pytest runner and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone repository with partial clone for efficiency
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd

WORKDIR /workspace/antd

# Checkout base commit (before the fix)
RUN git checkout 73286005cfccfd94f3ce02280bd46ba557f70e94

# Install dependencies
RUN npm install --legacy-peer-deps

WORKDIR /workspace/antd
