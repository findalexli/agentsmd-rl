FROM node:22-slim

RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace

# Clone ant-design at base commit (before fix)
RUN git clone --filter=blob:none https://github.com/ant-design/ant-design.git antd \
    && cd antd \
    && git checkout 501436e5f45e533679f797ee0ee58e2a391e566d

WORKDIR /workspace/antd

# Install dependencies
RUN npm install --legacy-peer-deps

# Set up Python virtual environment for pytest
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install pytest

WORKDIR /workspace/antd
