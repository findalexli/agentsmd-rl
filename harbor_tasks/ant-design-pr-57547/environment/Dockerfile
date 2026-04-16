FROM node:22-slim

# Install Python (needed for pytest test harness), git, and other utilities
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for the test harness
RUN pip3 install pytest --break-system-packages

# Create log directory
RUN mkdir -p /logs/verifier

# Clone the repository at the base commit (before the fix)
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd
WORKDIR /workspace/antd
RUN git checkout aa0594058b3735533a59c83feb5c309e88b544bd

# Install dependencies
RUN npm install --legacy-peer-deps

# Set working directory
WORKDIR /workspace/antd
